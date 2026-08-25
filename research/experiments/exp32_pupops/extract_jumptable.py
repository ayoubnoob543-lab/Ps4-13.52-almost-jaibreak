#!/usr/bin/env python3
"""Extrae la jump table del d_ioctl de pup_update0 y desensambla cada case."""
import struct
from capstone import *

d = open("/data/data/com.termux/files/home/fl_verify/deep/kernel1102/11.02/kernel.bin", "rb").read()
T0 = 0xffffffff835b4000
md = Cs(CS_ARCH_X86, CS_MODE_64)

# jump table base: lea rcx,[rip+0x4b367d] @0xbeac34 (len 7) => base = next + disp
JT_INSN = 0xffffffff83beac34
JT_NEXT = JT_INSN + 7
JT_BASE = JT_NEXT + 0x4B367D
print(f"jump table @ {JT_BASE:#x} (file {JT_BASE-T0+0:x})" if JT_BASE >= T0 else f"jump table va {JT_BASE:#x}")

NAMES = {0xC0184401: "DECRYPT_HDR", 0xC0184402: "VERIFY_SEG_ADD",
         0xC0184403: "VERIFY_SEG", 0xC0184404: "DECRYPT_SEG"}

def dis(va, maxi=70, stop_ret=True):
    fo = va - T0
    out = []
    n = 0
    for ins in md.disasm(d[fo:fo + 600], va):
        line = f"    {ins.address:#x}: {ins.mnemonic} {ins.op_str}"
        out.append(line)
        n += 1
        if stop_ret and ins.mnemonic == "ret" and n > 4:
            break
        if n >= maxi:
            out.append("    …")
            break
    return out

print("\n== jump table entries ==")
case_tgts = []
for i in range(4):
    rel = struct.unpack_from("<i", d, JT_BASE - T0 + i * 4)[0]
    tgt = JT_BASE + rel
    case_tgts.append(tgt)
    num = 0xC0184401 + i
    print(f"  caso {NAMES.get(num, hex(num))}: target {tgt:#x}")
    open(f"/data/data/com.termux/files/home/firmware-lab/research/results/orbis1102_ioctl_{num:08X}.asm", "w").write(
        "\n".join(dis(tgt, 80)))

print("\n== otros opcodes nuevos ==")
for tgt, nm in [(0xffffffff83bead9c, "OP_0x20004407"),
                (0xffffffff83beadac, "OP_0x2000440C")]:
    print(f"\n-- {nm} case @{tgt:#x} --")
    print("\n".join(dis(tgt, 30)))
open("/data/data/com.termux/files/home/firmware-lab/research/results/orbis1102_op_new.asm", "w").write(
    "\n".join(dis(0xffffffff83bead9c, 25)) + "\n" +
    "\n".join(dis(0xffffffff83beadac, 25)))
