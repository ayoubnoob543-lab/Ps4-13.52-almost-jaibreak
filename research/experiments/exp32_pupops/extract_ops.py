#!/usr/bin/env python3
"""Extrae la tabla de operaciones del device pup_update0 y desensambla handlers."""
import struct, sys
from capstone import *

d = open("/data/data/com.termux/files/home/fl_verify/deep/kernel1102/11.02/kernel.bin", "rb").read()
T0, T1 = 0xffffffff835b4000, 0xffffffff842b2cd8
md = Cs(CS_ARCH_X86, CS_MODE_64)

OPS_FILE = 0x2044810   # r14 -> 0xffffffff85df8810 (mapeo lineal hipótesis)

def disasm(va, n=40, stop_ret=True):
    fo = va - T0
    if not (0 <= fo < len(d)):
        return [f"    (fuera de archivo: {va:#x})"]
    out = []
    for ins in md.disasm(d[fo:fo + 300], va):
        out.append(f"      {ins.address:#x}: {ins.mnemonic} {ins.op_str}")
        n += 1
        if stop_ret and ins.mnemonic == "ret" and n > 3:
            break
        if n >= n:
            break
    return out

print(f"== ops struct @file {OPS_FILE:#x} ==")
slots = []
for k in range(24):
    o = OPS_FILE + k * 8
    v = struct.unpack_from("<Q", d, o)[0]
    intxt = T0 <= v < T1
    print(f"  +{k*8:#04x}: {v:#018x} {'TEXT' if intxt else ''}")
    if intxt:
        slots.append((k, v))

for k, v in slots[:8]:
    print(f"\n== handler candidato slot+{k*8:#x} @ {v:#x} ==")
    for l in disasm(v):
        if "0xc01844" in l.lower() or "0xc028" in l.lower():
            l += "   <<<< IOCTL CONST!"
        print(l)
