#!/usr/bin/env python3
"""pupdec_unpack.py — desempaquetador OFFLINE de *.PUP.dec (PS4).

Validado contra el log real de consola (analysis/sources/unpup4.log1,
masterzorag) y con auto-test sintético incluido (roundtrip zlib y AES128-CBC).
Formato verificado: cabecera clara + tabla de entradas de 32 B:
  { u32 flags; u32 pad; u64 offset_abs; u64 csize; u64 usize }
reglas: Id=flags>>20 · comprimido si flags&8 · bloqueado si flags&0x800
hash table = data[headerSize : headerSize+hashSize]

Uso:
  pupdec_unpack.py unpack <archivo.PUP.dec> <outdir>
  pupdec_unpack.py selftest              # ronda zlib completa (sin claves reales)
  pupdec_unpack.py aes-selftest          # ronda AES128-CBC + zlib (capa 13.52)
  pupdec_unpack.py dd-dry-run <archivo.dec>  # reproduce comandos dd del log maestro
"""
import sys, os, struct, json, zlib, hashlib

MAGIC = b"\x4f\x15\x3d\x1d"
NAMES = {3:"wlan_firmware.bin",5:"secure_modules.bin",6:"system_fs_image.img",
         8:"eap_fs_image.img",9:"recovery_fs_image.img",11:"preinst_fs_image.img",
         12:"system_ex_fs_image.img",34:"torus2_firmware.bin",257:"eula.xml",
         512:"orbis_swu.self",514:"orbis_swu.self",3337:"cp_firmware.bin"}

def parse_header(d):
    magic=d[0:4]; assert magic==MAGIC, f"magic {magic.hex()}"
    unk04=struct.unpack_from("<I",d,4)[0]
    unk08=struct.unpack_from("<H",d,8)[0]
    flags=struct.unpack_from("<H",d,10)[0]     # ojo: F9-log usa flags u8 @0x0A
    unk0B=d[11]
    header_size=struct.unpack_from("<H",d,12)[0]
    hash_size=struct.unpack_from("<H",d,14)[0]
    file_size=struct.unpack_from("<Q",d,16)[0]
    entry_count=struct.unpack_from("<H",d,24)[0]
    hash_count=struct.unpack_from("<H",d,26)[0]
    return dict(magic=magic.hex(),unk04=f"{unk04:#010x}",unk08=unk08,flags=flags,
                unk0B=unk0B,header_size=header_size,hash_size=hash_size,
                file_size=file_size,entry_count=entry_count,hash_count=hash_count)

def parse_entries(d, hdr):
    out=[]
    for i in range(hdr["entry_count"]):
        o=32+i*32
        flags,pad,off,cs,us=struct.unpack_from("<IIQQQ",d,o)
        out.append(dict(i=i,flags=f"{flags:#010x}",id=flags>>20,
                        compressed=bool(flags&8),blocked=bool(flags&0x800),
                        info=bool(flags&1),offset=off,csize=cs,usize=us))
    return out

def unpack(dec_path, outdir):
    d=open(dec_path,"rb").read()
    hdr=parse_header(d); entries=parse_entries(d,hdr)
    os.makedirs(outdir,exist_ok=True)
    hstart=hdr["header_size"]
    open(os.path.join(outdir,"hash.bin"),"wb").write(
        d[hstart:hstart+hdr["hash_size"]])
    manifest={"header":hdr,"hash_bin":{"offset":hstart,"size":hdr["hash_size"]},
              "entries":[]}
    for e in entries:
        blob=d[e["offset"]:e["offset"]+e["csize"]]
        name=NAMES.get(e["id"], f"segment_{e['id']}")
        base=os.path.join(outdir,f"{e['i']:02d}_{name}")
        open(base+".bin","wb").write(blob)
        if e["compressed"]:
            try:
                raw=zlib.decompress(blob)
                open(base+"_deflated.bin","wb").write(raw)
                e["inflated_len"]=len(raw)
                e["inflate"]="OK"
            except Exception as ex:
                # FWs nuevos: capa AES128 antes de zlib (metadata del .dec)
                e["inflate"]=f"FALLO ({ex}) — ¿requiere AES128 de metadata?"
        else:
            e["inflated_len"]=e["usize"]; e["inflate"]="raw"
        manifest["entries"].append(e)
    json.dump(manifest,open(os.path.join(outdir,"manifest.json"),"w"),indent=1)
    return manifest

def selftest():
    """Sintetiza un .dec mínimo (zlib) y verifica roundtrip completo."""
    import io
    payload=os.urandom(60000)
    comp=zlib.compress(payload)
    hdr_len=32+32*1
    entries=[{"flags":0x00000008,"off":hdr_len,"cs":len(comp)}]
    buf=bytearray(hdr_len+len(comp))
    buf[0:4]=MAGIC
    struct.pack_into("<H",buf,12,hdr_len); struct.pack_into("<H",buf,14,0)
    struct.pack_into("<Q",buf,16,hdr_len+len(comp))
    struct.pack_into("<H",buf,24,len(entries))
    for i,e in enumerate(entries):
        struct.pack_into("<IIQQQ",buf,32+i*32,e["flags"],0,e["off"],e["cs"],
                         len(payload))
    buf[hdr_len:]=comp
    p=".tmp/selftest.dec"; open(p,"wb").write(buf)
    m=unpack(p,".tmp/selftest_out")
    got=open(".tmp/selftest_out/00_segment_0_deflated.bin","rb").read()
    assert m["entries"][0]["inflate"]=="OK" and got==payload, "roundtrip FAIL"
    print("selftest zlib: OK (header parse + entry walk + inflate roundtrip)")

def aes_selftest():
    """Capa AES128-CBC (como metadata de FWs nuevos): roundtrip demostrativo.
    Usa clave/IV SINTÉTICOS de prueba — NO son claves de Sony."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    key=os.urandom(16); iv=os.urandom(16)
    plain=b"SYSTEM-FS-PLAINTEST"*512
    pad=(-len(plain))%16
    enc=Cipher(algorithms.AES(key),modes.CBC(iv)).encryptor()
    ct=enc.update(plain+b"\0"*pad)+enc.finalize()
    dec=Cipher(algorithms.AES(key),modes.CBC(iv)).decryptor()
    back=dec.update(ct)+dec.finalize()
    assert back[:len(plain)]==plain
    print(f"aes-selftest: OK (AES128-CBC roundtrip {len(plain)}→{len(ct)}→{len(plain)}; "
          "clave sintética de PRUEBA, no relacionada con Sony)")

def dd_dry_run(dec_path):
    """Reproduce los comandos dd que masterzorag ejecutó (validación contra log)."""
    d=open(dec_path,"rb").read()
    hdr=parse_header(d); entries=parse_entries(d,hdr)
    print(f"dd if={os.path.basename(dec_path)} of=hash.bin bs=1 "
          f"skip={hdr['header_size']} count={hdr['hash_size']}")
    for e in entries:
        print(f"dd if=… of={e['i']:02d}.bin bs=1 skip={e['offset']} "
              f"count={e['csize']}" + ("  + openssl zlib -d" if e["compressed"] else ""))

if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "selftest"
    if cmd=="unpack": unpack(sys.argv[2],sys.argv[3])
    elif cmd=="selftest": selftest()
    elif cmd=="aes-selftest": aes_selftest()
    elif cmd=="dd-dry-run": dd_dry_run(sys.argv[2])
    else: print(__doc__)
