#!/usr/bin/env python3
"""Desensambla los 4 cases del d_ioctl de pup_update0 (kernel Orbis 11.02)."""
import struct
from capstone import *

d = open("/data/data/com.termux/files/home/fl_verify/deep/kernel1102/11.02/kernel.bin", "rb").read()
T0 = 0xffffffff835b4000
md = Cs(CS_ARCH_X86, CS_MODE_64)

CASES = {
    "DECRYPT_HDR(01)":     0xffffffff83beac44,
    "VERIFY_SEG_ADD(02)":  0xffffffff83beadf7,
    "VERIFY_SEG(03)":      0xffffffff83beaed4,
    "DECRYPT_SEG(04)":     0xffffffff83beb00f,
}

out_all = []
for name, va in CASES.items():
    fo = va - T0
    txt = [f"\n===== CASE {name} @ {va:#x} ====="]
    n = 0
    for ins in md.disasm(d[fo:fo + 900], va):
        line = f"  {ins.address:#x}: {ins.mnemonic} {ins.op_str}"
        # anotar calls con destino
        if ins.mnemonic == "call":
            try:
                tgt = int(ins.op_str, 16)
                line += f"   [call → {tgt:#x}]"
            except ValueError:
                pass
        txt.append(line)
        n += 1
        if ins.mnemonic == "ret" and n > 8:
            break
        if n > 120:
            txt.append("  …")
            break
    out_all.append("\n".join(txt))
    print(f"{name}: {n} instrucciones")

open("/data/data/com.termux/files/home/firmware-lab/research/results/orbis1102_ioctl_cases.asm", "w").write(
    "\n".join(out_all) + "\n")
print("guardado orbis1102_ioctl_cases.asm")
