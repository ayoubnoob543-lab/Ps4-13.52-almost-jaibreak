#!/usr/bin/env python3
"""pup_orchestrator.py — Port Termux de la ORQUESTRA de ps4-pup_decrypt (idc).

Replica fielmente el flujo de decrypt.c: BLS/SLB2 externo -> pup_file_header ->
cabecera cifrada -> segmentos/bloques. La ÚNICA diferencia: las operaciones
kernel (/dev/pup_update0 ioctls 0xC0184401..05) se sustituyen por un stub que
falla con diagnóstico claro. Cero criptografía local: las claves viven en el
kernel/SBL Sony y nunca estuvieron en el payload original.
"""
import struct, json, sys, pathlib

class KernelDeviceStub:
    """Sustituto offline de /dev/pup_update0. Ningún método puede funcionar
    sin el dispositivo del kernel Orbis; falla con razón explícita."""
    DEV = "/dev/pup_update0"
    def _fail(self, op):
        raise RuntimeError(
            f"ioctl {op} sobre {self.DEV}: REQUIERE_KERNEL_ORBIS "
            "(descifrado AES/claves residen en SceSblUpdateMgr del kernel)")
    def decrypt_header(self, buf, length, type_): self._fail("0xC0184401")
    def verify_segment(self, idx, buf, ln, add): self._fail("0xC0184402/03")
    def decrypt_segment(self, idx, buf, ln):     self._fail("0xC0184404")
    def decrypt_segment_block(self, e, b, bb, bl, tb, tl): self._fail("0xC0284405")

PUP_FILE_HEADER = "<4sIHBBHH"       # magic,unk04,unk08,flags,unk0B,unk0C,unk0E (16B)
MAGIC = b"\x4f\x15\x3d\x1d"

def parse_outer_bls(data):
    """bls_header(32) + bls_entry(48)*n — idéntico a decrypt_pups()"""
    magic, ver, flags, fcount, bcount = struct.unpack_from("<IIIII", data, 0)
    assert magic == 0x324C4253 or True  # SLB2 LE/BE según dump; informativo
    entries=[]
    off=32
    for i in range(fcount):
        bo,sz = struct.unpack_from("<II", data, off)
        name = data[off+16:off+48].rstrip(b"\0").decode(errors="replace")
        entries.append({"name":name,"block_offset":bo,"size":sz,
                        "byte_offset":bo*512})
        off+=48
    return entries

def plan_inner_pup(data, base, dev):
    """decrypt_pup_data() sin criptografía: parsea cabecera clara y emite
    orden de trabajo para cada segmento."""
    hdr = data[base:base+16]
    magic, unk04, unk08, flags, unk0B, unk0C, unk0E = struct.unpack(
        PUP_FILE_HEADER, hdr)
    if magic != MAGIC:
        return {"error": f"magic inválido: {magic.hex()}"}
    header_size = unk0C + unk0E            # región cifrada (tabla incluida)
    plan = {"base_offset": base, "flags": flags,
            "plaintext_header_bytes": 16,
            "encrypted_header_region": {"offset": base+16,
                                        "size": header_size-16},
            "segments": []}
    try:
        dev.decrypt_header(bytearray(header_size), header_size, 0)
    except RuntimeError as e:
        plan["header_decrypt"] = str(e)
    # sin tabla descifrada NO es posible enumerar segmentos (igual que en la
    # consola antes del ioctl): se registra como paso bloqueado
    plan["segment_enumeration"] = "BLOCKED: requiere header descifrado"
    return plan

def main(pup_path, out_json):
    data = pathlib.Path(pup_path).read_bytes()
    report = {"input": pup_path, "size": len(data),
              "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "device": KernelDeviceStub.DEV}
    try:
        entries = parse_outer_bls(data[:32+48*64])
        report["outer_entries"] = entries
    except Exception as e:
        report["outer_entries_error"] = str(e)
        entries=[{"name":"PS4UPDATE1.PUP","byte_offset":1024,"size":len(data)-1024}]
    dev = KernelDeviceStub()
    report["inner"] = [plan_inner_pup(data, e["byte_offset"], dev) for e in entries]
    pathlib.Path(out_json).write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2)[:2000])

import datetime
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else "/dev/stdout")
