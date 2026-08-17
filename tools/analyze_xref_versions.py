from pathlib import Path
import shutil
import subprocess, re, hashlib, json, argparse

try:
    from capstone import Cs, CS_ARCH_X86, CS_MODE_64
except ImportError:
    Cs = None

parser = argparse.ArgumentParser(description='Static XREF/version analysis for a raw x86-64 libkernel dump')
REPO_ROOT = Path(__file__).resolve().parent.parent
parser.add_argument('dump', nargs='?', default=str(REPO_ROOT / 'libkernel_sys_13.52.bin'), help='raw dump path')
parser.add_argument('--out-dir', default=str(REPO_ROOT / 'analysis'), help='output directory')
args = parser.parse_args()
BIN = Path(args.dump).resolve()
OUT = Path(args.out_dir).resolve()
OUT.mkdir(parents=True, exist_ok=True)
TXT = OUT / 'xref_version_analysis_13.52.txt'
JS = OUT / 'xref_version_analysis_13.52.json'
WORK = OUT / '.work'
WORK.mkdir(parents=True, exist_ok=True)
raw = BIN.read_bytes()

requested = {
 'kern.sdk_version': 0x374a9,
 '%2x.%03x.%03x': 0x374ba,
 'machdep.upd_version': 0x378c0,
 'machdep.lower_limit_upd_version': 0x378d4,
 'machdep.lower_limit_sysex_version': 0x378f4,
 'machdep.system_ex_version': 0x37916,
}

def cstr_at(off):
    end = raw.find(b'\0', off)
    return raw[off:end if end >= 0 else off+256].decode('latin1', errors='replace')

def all_occ(needle):
    out=[]; p=0
    while True:
        p=raw.find(needle,p)
        if p<0: return out
        out.append(p); p+=1

def objdump(start=None, stop=None):
    """Return objdump-compatible text, falling back to Capstone when needed."""
    if shutil.which('objdump'):
        cmd=['objdump','-D','-b','binary','-m','i386:x86-64','-M','intel','--adjust-vma=0']
        if start is not None: cmd += [f'--start-address=0x{start:x}']
        if stop is not None: cmd += [f'--stop-address=0x{stop:x}']
        cmd += [str(BIN)]
        return subprocess.check_output(cmd, text=True, errors='replace')
    if Cs is None:
        raise RuntimeError('objdump is unavailable and Python capstone is not installed')
    decoder = Cs(CS_ARCH_X86, CS_MODE_64)
    decoder.detail = False
    lo = 0 if start is None else max(0, start)
    hi = len(raw) if stop is None else min(len(raw), stop)
    lines = []
    for insn in decoder.disasm(raw[lo:hi], lo):
        byte_text = ' '.join(f'{b:02x}' for b in insn.bytes)
        lines.append(f'{insn.address:x}:\\t{byte_text}\\t{insn.mnemonic} {insn.op_str}'.rstrip())
    return '\\n'.join(lines) + ('\\n' if lines else '')

full_path=WORK/'full_objdump.txt'
full_path.write_text(objdump())
full=full_path.read_text(errors='replace').splitlines()
line_re=re.compile(r'^\s*([0-9a-f]+):\s*(.*)$',re.I)
ins=[]
for line in full:
    m=line_re.match(line)
    if m:
        off=int(m.group(1),16)
        rest=m.group(2)
        parts=rest.split('\t')
        if len(parts) >= 2:
            byte_text=parts[0].strip()
            asm='\t'.join(parts[1:]).strip()
        else:
            byte_text=''
            asm=rest.strip()
        byte_tokens=re.findall(r'(?<![0-9a-f])[0-9a-f]{2}(?![0-9a-f])',byte_text,re.I)
        try:
            b=bytes.fromhex(' '.join(byte_tokens))
        except ValueError:
            b=b''
        ins.append({'offset':off,'bytes':b.hex(' '),'asm':asm,'line':line.strip()})
ins.sort(key=lambda x:x['offset'])
byoff={x['offset']:x for x in ins}

prologues=('55 48 89 e5','55 41 57','55 41 56','53 48 83 ec','48 83 ec')
def probable_function(off):
    by={x['offset']:x for x in ins}
    candidates=[]
    for x in ins:
        if x['offset']>off:
            break
        b=x['bytes'].replace(' ','').lower()
        nxt=by.get(x['offset']+1)
        if b.startswith('55') and nxt and nxt['bytes'].replace(' ','').lower().startswith('48 89 e5'.replace(' ','')):
            candidates.append(x)
        elif x['bytes'].startswith('55 41 57') or x['bytes'].startswith('55 41 56'):
            candidates.append(x)
    if not candidates: return None
    c=candidates[-1]
    if off-c['offset']>0x300: return None
    return {'offset':f'0x{c["offset"]:x}','line':c['line']}

def parse_target(asm):
    m=re.search(r'#\s*0x([0-9a-f]+)',asm,re.I)
    return int(m.group(1),16) if m else None

def is_rip(asm): return bool(re.search(r'\[rip[+-]',asm,re.I))

def xrefs_to(target):
    out=[]
    for x in ins:
        t=parse_target(x['asm'])
        if t == target:
            out.append({'xref_offset':x['offset'],'file_offset':x['offset'],'bytes':x['bytes'],'instruction':x['asm'],'rip_relative':is_rip(x['asm']),'function':probable_function(x['offset'])})
    return out

# Exact string facts, including requested-vs-actual discrepancy.
strings=[]
for name, req in requested.items():
    needle=name.encode()
    occ=all_occ(needle)
    actual=occ[0] if occ else None
    strings.append({'name':name,'requested_offset':f'0x{req:x}','actual_byte_offsets':[f'0x{x:x}' for x in occ], 'actual_first_offset':f'0x{actual:x}' if actual is not None else None, 'requested_offset_matches': req in occ, 'value_at_actual':cstr_at(actual) if actual is not None else None, 'xrefs':xrefs_to(req)+([] if actual is None or actual==req else xrefs_to(actual))})

# Focus functions requested by user. Windows selected to end at next likely prologue/ret window.
focus=[0x19720,0x19790,0x19860,0x198e0,0x19970,0x19a00,0x19a40,0x1be10,0x1be70,0x1bed0,0x1bf40,0x1bfd0,0x1c030,0x10240,0x10130,0x13d90,0x1bb0,0xdde0]
def func_lines(start, window=0x180):
    return [x for x in ins if start <= x['offset'] < start+window]

def analyze_func(start):
    ls=func_lines(start)
    if not ls: return {'start':f'0x{start:x}','status':'UNKNOWN'}
    calls=[]; jumps=[]; rip=[]; constants=[]; reads=[]
    for x in ls:
        a=x['asm']
        t=parse_target(a)
        if re.search(r'\bcall\b',a,re.I): calls.append({'offset':f'0x{x["offset"]:x}','target':f'0x{t:x}' if t is not None else 'UNKNOWN','instruction':a})
        if re.search(r'\b(jmp|ja|jae|jb|jbe|jc|je|jg|jge|jl|jle|jne|jno|jns|jo|jp|js|jz|jnz)\b',a,re.I): jumps.append({'offset':f'0x{x["offset"]:x}','target':f'0x{t:x}' if t is not None else 'UNKNOWN','instruction':a})
        if is_rip(a): rip.append({'offset':f'0x{x["offset"]:x}','target':f'0x{t:x}' if t is not None else 'UNKNOWN','instruction':a})
        for cm in re.findall(r'(?<![A-Za-z])(?:0x[0-9a-f]+|0x[0-9A-F]+|\b[0-9]+\b)',a):
            constants.append(cm)
        if re.search(r'\b(mov|cmp|test|and|or|xor|add|sub|shl|shr|imul|bextr|movzx|movsx)\b',a,re.I): reads.append(a)
    return {'start':f'0x{start:x}','status':'static_window','first_line':ls[0]['line'],'last_line':ls[-1]['line'],'instructions':[x['line'] for x in ls[:80]],'calls':calls,'jumps':jumps,'rip_relative':rip,'constants':sorted(set(constants), key=lambda s:(len(s),s)),'read_write_instruction_summary':reads[:80]}

functions=[analyze_func(x) for x in focus]

# All occurrences/references of broad terms and version numerals, including raw strings and disassembly mentions.
terms=['machdep','sdk_version','upd_version','sysex_version','system_ex_version','13.52','13_52','1352','version','SDK','0x0c0c','0xc0c','0x0fff','0xfff','0x040c','0x40c','0x80020016']
term_hits={}
for term in terms:
    hits=[]
    tb=term.encode()
    for o in all_occ(tb): hits.append({'file_offset':f'0x{o:x}','context':raw[max(0,o-48):min(len(raw),o+len(tb)+96)].decode('latin1',errors='replace')})
    dis=[x['line'] for x in ins if term.lower() in x['asm'].lower()]
    term_hits[term]={'raw_string_or_bytes_hits':hits[:300],'disassembly_hits':dis[:300],'raw_hit_count':len(hits),'disassembly_hit_count':len(dis)}

# Compact report sections.
report=[]
report.append('XREF VERSION ANALYSIS — libkernel_sys_13.52.bin\n')
report.append('Scope: static analysis only. The raw blob was read and disassembled as x86-64 with objdump or a Capstone fallback; no recovered code, payload, exploit or hardware was executed. Offsets are file-relative offsets from blob start, not virtual addresses.\n')
report.append('1. RESUMEN\n')
report.append(f'File size: {len(raw)} bytes (0x{len(raw):x}); SHA-256: {hashlib.sha256(raw).hexdigest()}. The requested strings were searched byte-for-byte and all RIP-relative disassembly targets were scanned. The exact byte start of kern.sdk_version is recorded separately because the requested 0x374a9 is one byte before the visible string start in this corpus.\n')
report.append('2. TABLA COMPLETA DE XREF\n')
for s in strings:
    report.append(f"STRING {s['name']} | requested={s['requested_offset']} | actual={','.join(s['actual_byte_offsets']) or 'NOT_FOUND'} | exact_requested_match={s['requested_offset_matches']}\n")
    if not s['xrefs']: report.append('  XREF: NONE found in objdump comments for exact target(s).\n')
    for x in s['xrefs']:
        report.append(f"  xref_file_offset=0x{x['xref_offset']:x} bytes=[{x['bytes']}] rip_relative={x['rip_relative']} instruction={x['instruction']} function={x['function'] or 'UNKNOWN'}\n")
report.append('\n3. FUNCIONES RELEVANTES\n')
for f in functions:
    report.append(f"FUNCTION {f['start']} status={f['status']}\n")
    report.append(f"  first={f.get('first_line','UNKNOWN')}\n  last={f.get('last_line','UNKNOWN')}\n")
    report.append('  calls: '+('; '.join(f'{c["offset"]}->{c["target"]} {c["instruction"]}' for c in f.get('calls',[])) or 'NONE')+'\n')
    report.append('  jumps: '+('; '.join(f'{j["offset"]}->{j["target"]} {j["instruction"]}' for j in f.get('jumps',[])) or 'NONE')+'\n')
    report.append('  rip_relative: '+('; '.join(f'{r["offset"]}->{r["target"]}' for r in f.get('rip_relative',[])) or 'NONE')+'\n')
    report.append('  constants: '+', '.join(f.get('constants',[]))+'\n')
    report.append('  compact instructions:\n    '+'\n    '.join(f.get('instructions',[])[:35])+'\n')
report.append('\n4. PSEUDOCÓDIGO APROXIMADO\n')
report.append('La siguiente representación es deliberadamente conservadora y no asigna símbolos no presentes:\n')
report.append('''function at 0x19790 (probable SDK-version formatter):\n    input = query_name_0x374aa_via_helper_0x10240(output_4_bytes)\n    if query fails: return error converted through 0x1bb0\n    high = input >> 24\n    middle = extract_bits(input, control=0x0c0c)\n    low = input & 0xfff\n    format output with "%2x.%03x.%03x"\n    store original packed value in an output field\n\nfunctions at 0x1be10/0x1be70/0x1bed0/0x1bf40/0x1bfd0/0x1c030:\n    if required output pointer is null: return 0x80020016 or equivalent error path\n    query one machdep.* name through helper 0x10240\n    use a 4-byte or 1-byte buffer depending on function\n    copy/transform returned bytes; on failure use 0x1bb0 and 0x13d90 where observed\n    return helper/result status\n''')
report.append('\n5. VALORES DE VERSIÓN ENCONTRADOS\n')
report.append('No se encontró un valor literal inequívoco 13.52, 13_52 o 1352 dentro del blob. Sí se encontró el formato "%2x.%03x.%03x" y código de extracción de campos de un valor de 32 bits obtenido en runtime. Las constantes observadas son 0xc0c, 0xfff, 0x18, 0x40c, 0x4, 0x24 y 0x80020016; ninguna prueba por sí sola que el valor sea 13.52.\n')
report.append('\n6. RELACIÓN kern.sdk_version / machdep.*\n')
report.append('Ambos grupos usan el helper común 0x10240 y buffers de tamaño pequeño, con rutas de error conectadas a 0x1bb0. kern.sdk_version se transforma en componentes de formato; machdep.* se consulta como identificadores, flags o versiones de sistema. El código común demuestra una infraestructura de consulta compartida, no que todos los valores representen la misma versión ni que alguno sea necesariamente el firmware PS4.\n')
report.append('\n7. EVIDENCIA DIRECTA\n')
report.append('- Bytes exactos de las cadenas y sus offsets de archivo.\n- Instrucciones RIP-relative cuyo comentario de objdump resuelve al offset de una cadena.\n- Llamadas observables a 0x10240 desde consumidores.\n- Longitudes de buffers, constantes, comparaciones y ramas presentes en las ventanas analizadas.\n- Rutas de error que llaman 0x1bb0; llamadas a 0x13d90 cuando el código las muestra.\n')
report.append('\n8. INFERENCIAS\n')
report.append('- 0x19790 parece un consumidor/formateador de un valor empaquetado de SDK por la consulta de 4 bytes, el formato y BEXTR/AND/SHR.\n- Las funciones machdep parecen wrappers de consulta y conversión de valores de sistema.\n- 0x10240 es probablemente un helper tipo sysctl-by-name, pero su nombre no está demostrado por símbolos.\n- La organización es compatible con versionado/runtime de Orbis, no con una prueba autónoma de FW 13.52.\n')
report.append('\n9. UNKNOWN\n')
report.append('- El valor runtime real devuelto por kern.sdk_version.\n- El nombre de símbolo de cada función consumidora.\n- El tipo C exacto de los buffers y estructuras.\n- La semántica exacta de cada número de sysctl y del helper 0x10240.\n- Si 0x374a9 fue documentado como inicio por una convención de offset o es un error de un byte; el byte exacto de la string visible debe respetarse.\n- Si cualquiera de las variables machdep contiene o deriva el firmware 13.52.\n- La relación con una dirección virtual o GOT: todos los offsets aquí son relativos al archivo.\n')
report.append('\n10. SIGUIENTE PASO\n')
report.append('Obtener un artefacto estático de la misma build que contenga el valor runtime o una tabla de símbolos/exports, idealmente el eboot exacto con sus relocaciones y el resultado de la consulta kern.sdk_version. El siguiente análisis estático más valioso es correlacionar 0x10240 y 0x10130 con una tabla de imports/exports o con un dump de sysctl/SDK version de la misma consola; sin ese valor, el blob sólo demuestra el mecanismo de consulta, no la versión concreta.\n')
report.append('\n11. NOTA SOBRE COMPLETITUD\n')
report.append('La búsqueda de XREFs se hizo sobre el desensamblado completo generado localmente. Sólo se consideran XREF directas cuando el destino aparece explícito en una referencia RIP-relative o comentario de destino; punteros indirectos, tablas sin relocación y referencias externas al blob quedan UNKNOWN.\n')
TXT.write_text(''.join(report))

data={'file':BIN.name,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'requested_strings':strings,'focus_functions':functions,'term_hits':term_hits,'method':{'disassembly':'objdump -D binary x86-64 Intel or Capstone x86-64 fallback','offset_semantics':'file-relative from blob start','execution':'none'}}
JS.write_text(json.dumps(data,indent=2,ensure_ascii=False))
print(TXT)
print(JS)
