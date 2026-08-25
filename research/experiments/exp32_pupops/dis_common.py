#!/usr/bin/env python3
"""Desensambla el camino común 0xbead8f (implementación compartida de los 4 casos)."""
import struct
from capstone import *

d = open("/data/data/com.termux/files/home/fl_verify/deep/kernel1102/11.02/kernel.bin", "rb").read()
T0 = 0xffffffff835b4000
md = Cs(CS_ARCH_X86, CS_MODE_64)

va = 0xffffffff83bead8f
fo = va - T0
txt = []
n = 0
for ins in md.disasm(d[fo:fo + 1200], va):
    line = f"  {ins.address:#x}: {ins.mnemonic} {ins.op_str}"
    if ins.mnemonic == "call":
        try:
            tgt = int(ins.op_str, 16)
            line += f"   [→ {tgt:#x}]"
        except ValueError:
            pass
    txt.append(line)
    n += 1
    if ins.mnemonic == "ret" and n > 20:
        break
    if n > 200:
        txt.append("  …")
        break

out = "\n".join(txt)
open("/data/data/com.termux/files/home/firmware-lab/research/results/orbis1102_ioctl_common_path.asm", "w").write(out + "\n")
print(out)
