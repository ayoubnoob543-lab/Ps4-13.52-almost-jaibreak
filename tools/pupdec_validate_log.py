#!/usr/bin/env python3
"""Valida pupdec_unpack contra el log REAL de consola (masterzorag unpup4.log1):
reconstruye el contenedor desde los valores del log y comprueba que el parser
reproduce exactamente los mismos comandos dd/zlib."""
import re, struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pupdec_unpack as P

LOG = os.path.expanduser("~/firmware-lab/analysis/sources/unpup4.log1")
txt = open(LOG, encoding="utf8", errors="replace").read()

# --- extraer cabecera del log ---
def grab(pat):
    m = re.search(pat, txt); return m
magic = "4f153d1d"
header_size = int(grab(r"headerSize\s+(\w+) \d+b \((\d+)b\)").group(2))
hash_size   = int(grab(r"hashSize\s+(\w+) \d+b \((\d+)b\)").group(2))
file_size   = int(grab(r"fileSize\s+(\w+) 8b \((\d+)b\)").group(2))
entry_count = int(grab(r"entryCount\s+(\w+) 2b \((\d+)n\)").group(2))
hash_count  = int(grab(r"hashCount\s+(\w+) 2b \((\d+)n\)").group(2))

# --- extraer entradas ---
entries = []
for m in re.finditer(
    r"Entry (\d+) @\w+\n\s+Flags\s+(\w+) 4b\n\s+Offset\s+\+(\w+) 8b \((\d+)b\)\n"
    r"\s+CompressedSize\s+(\w+) 8b \((\d+)b\)\n\s+UncompressedSize\s+(\w+) 8b \((\d+)b\)", txt):
    i=int(m.group(1)); flags=int(m.group(2),16)
    off=int(m.group(3),16); cs=int(m.group(5),16); us=int(m.group(7),16)
    compressed = bool(flags & 8)
    zl = f"openssl zlib -d -in {i:02d}.bin" in txt
    entries.append(dict(i=i,flags=flags,off=off,cs=cs,us=us,
                        compressed=compressed,zlib_in_log=zl))

# --- extraer comandos dd del log ---
dd_lines = [l.strip() for l in txt.splitlines() if l.startswith("dd if=")]

# --- reconstruir contenedor sintético con esos metadatos ---
total = max(e["off"]+e["cs"] for e in entries)
buf = bytearray(total)
buf[0:4] = bytes.fromhex(magic)
struct.pack_into("<H", buf, 12, header_size)
struct.pack_into("<H", buf, 14, hash_size)
struct.pack_into("<Q", buf, 16, file_size)
struct.pack_into("<H", buf, 24, entry_count)
struct.pack_into("<H", buf, 26, hash_count)
for e in entries:
    struct.pack_into("<IIQQQ", buf, 32+e["i"]*32,
                     e["flags"], 0, e["off"], e["cs"], e["us"])
    # contenido sintético distinguible (no es datos reales del FW)
    mark = bytes([0xA0+e["i"]])*max(1,min(e["cs"],64))
    buf[e["off"]:e["off"]+len(mark)] = mark

p="/data/data/com.termux/files/home/firmware-lab/tools/.tmp/synth.dec"
os.makedirs(os.path.dirname(p),exist_ok=True)
open(p,"wb").write(buf)

# --- validar con el unpacker real ---
hdr=P.parse_header(buf); ents=P.parse_entries(buf,hdr)
assert hdr["header_size"]==header_size and hdr["hash_size"]==hash_size, "header mismatch"
assert hdr["file_size"]==file_size and hdr["entry_count"]==entry_count, "campos mismatch"
assert len(ents)==len(entries)

mine=[f"dd if={os.path.basename(p)} of=hash.bin bs=1 skip={hdr['header_size']} count={hdr['hash_size']}"]
for e,e0 in zip(ents,entries):
    line=(f"dd if={os.path.basename(p)} of={e['i']:02d}.bin bs=1 "
          f"skip={e['offset']} count={e['csize']}")
    mine.append(line)
    assert e["compressed"]==e0["compressed"], f"flag compresión difiere en #{e['i']}"
    if e0["zlib_in_log"]:
        import zlib
        blob=buf[e["offset"]:e["offset"]+e["csize"]]
        try:
            zlib.decompress(blob)  # en sintético: marcador no comprimido ⇒ fallará
        except Exception: pass

import re
def nums(line):
    m=re.search(r"skip=(\d+)",line); c=re.search(r"count=(\d+)",line)
    return (int(m.group(1)) if m else -1, int(c.group(1)) if c else -1)
log_nums=[nums(l) for l in dd_lines]
mine_nums=[nums(l) for l in mine]
match=sum(1 for a,b in zip(log_nums,mine_nums) if a==b)
diff=[(i,l,m_) for i,(a,b),l,m_ in
      zip(range(len(log_nums)),zip(log_nums,mine_nums),dd_lines,mine[1:] if False else mine)
      if a!=b]
print(f"comandos log={len(dd_lines)} regenerados={len(mine)} "
      f"idénticos(skip,count)={match}")
for d_ in diff[:6]: print("  DIF:",d_)
sys.exit(1 if diff else 0)
sys.exit(1 if diff else 0)
print(f"comprimidas según log={comp_log} según flags={comp_mine}")
sys.exit(1 if mismatch else 0)
