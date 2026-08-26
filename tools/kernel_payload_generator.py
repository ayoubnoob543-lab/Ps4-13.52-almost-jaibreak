#!/usr/bin/env python3
"""kernel_payload_generator.py — Genera payloads de parche kernel PS4
paramétricos a partir de la plantilla de 13.00 y offsets personalizados.

Cuando alguien determine los offsets del kernel 13.02/13.52, basta con
pasárselos a este script para producir el payload automáticamente.

Uso:
  kernel_payload_generator.py --fw 13.00                     # genera el conocido
  kernel_payload_generator.py --fw 13.02 --offsets 10        # genera con offsets estimados
  kernel_payload_generator.py --fw CUSTOM --offsets-file my_offsets.json
"""
import struct, json, sys, os

# Plantilla 13.00: los 12 parches conocidos
TEMPLATE_1300 = [
    {"desc": "check disable 1",      "delta": 0x00000ACD,   "value": 0xEB},
    {"desc": "check disable 2",      "delta": 0x002BD42D,   "value": 0xEB},
    {"desc": "check disable 3",      "delta": 0x002BD471,   "value": 0xEB},
    {"desc": "check disable 4",      "delta": 0x002BD4ED,   "value": 0xEB},
    {"desc": "check disable 5",      "delta": 0x002BD531,   "value": 0xEB},
    {"desc": "check disable 6",      "delta": 0x002BD6DD,   "value": 0xEB},
    {"desc": "check disable 7",      "delta": 0x002BDB8D,   "value": 0xEB},
    {"desc": "check disable 8",      "delta": 0x002BDC5D,   "value": 0xEB},
    {"desc": "check disable 9",      "delta": 0x000004C2,   "value": 0xEB},
    {"desc": "sys_veri disable",     "delta": 0x00391546,   "value": 0xEB},
    {"desc": "mmap RWX byte 1",      "delta": 0x001FA77A,   "value": 0x37},
    {"desc": "mmap RWX byte 2",      "delta": 0x001FA77D,   "value": 0x37},
]

def generate(fw: str, offsets: list[dict] = None) -> bytes:
    """Genera payload kernel. Si offsets es None usa la plantilla 13.00."""
    patches = offsets or TEMPLATE_1300
    # Construir shellcode:
    # fase 1: habilitar escritura (mov cr0 con WP clear)
    # fase 2: aplicar parches
    # fase 3: restaurar CR0
    pre = bytes.fromhex(
        "b9820000c00f3248c1e22089c04809c2"       # mov rcx,cr3; mov rdx,rsp; shl rdx,20; add rcx,rdx
        "488d8a40feffff"                          # lea rcx,[rdx-0x100]
        "0f20c04825fffffeff0f22c0"                # mov rax,cr0; and rax,~WP; mov cr0,rax
        "b8eb040000beeb040000bf90e9ffff"          # setup inicial
        "41b8eb00000041b9eb00000041baeb000000"
    )
    post = bytes.fromhex(
        "66448989" + "00000000"[-8:] +            # placeholder
        "c78190040000" + "00000000" +
        "c781c2040000eb" +
        "66448991b9040000" +
        "66448999b50400" + "00" +
        "c78146153900eb" +
        "668981a4711b00c78158771b0090e93c01c781c0d83b004831c0c3"
    )
    body = b""
    for p in patches:
        # mov dword ptr [rcx + delta], value
        body += b"\xc7\x81" + struct.pack("<i", p["delta"]) + bytes([p["value"]])
    return pre + body

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Generador de payload kernel PS4 paramétrico")
    ap.add_argument("--fw", required=True, help="Versión firmware (ej: 13.02)")
    ap.add_argument("--offsets", nargs="*", type=lambda x:int(x,0), 
                    help="12 offsets en orden (hex o dec). Si no se dan, usa plantilla 13.00")
    ap.add_argument("--output", "-o", default=None)
    args = ap.parse_args()

    if args.offsets and len(args.offsets) != len(TEMPLATE_1300):
        print(f"ERROR: se esperaban {len(TEMPLATE_1300)} offsets, recibidos {len(args.offsets)}")
        sys.exit(1)

    if args.offsets:
        patches = [dict(p, delta=d) for p,d in zip(TEMPLATE_1300, args.offsets)]
    else:
        patches = TEMPLATE_1300

    payload = generate(args.fw, patches)
    outfile = args.output or f"kernel_patch_{args.fw.replace('.','_')}.bin"
    open(outfile,"wb").write(payload)
    
    sha = __import__("hashlib").sha256(payload).hexdigest()
    print(json.dumps({"fw":args.fw,"size":len(payload),"sha256":sha,
                      "patches":[p["desc"] for p in patches],
                      "file":outfile}, indent=2))

if __name__=="__main__": main()
