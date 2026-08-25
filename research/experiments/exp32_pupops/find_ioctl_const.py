#!/usr/bin/env python3
"""Busca el inmediato 0xC0184401 (y familia) en el texto del kernel 11.02
y desensambla alrededor de cada hit para identificar el handler d_ioctl."""
import struct
from capstone import *

d = open("/data/data/com.termux/files/home/fl_verify/deep/kernel1102/11.02/kernel.bin", "rb").read()
T0, T_SZ = 0xffffffff835b4000, 0xcfe6d8
md = Cs(CS_ARCH_X86, CS_MODE_64)

targets = {0xC0184401: "DECRYPT_HDR", 0xC0184402: "VERIFY_SEG_ADD",
           0xC0184403: "VERIFY_SEG", 0xC0184404: "DECRYPT_SEG",
           0xC0284405: "DECRYPT_SEG_BLK"}

# buscar los 4 bytes LE del número en toda la primera LOAD (texto)
need = {}
for v, nm in targets.items():
    b = struct.pack("<I", v)
    i = 0
    hits = []
    while True:
        i = d.find(b, i, T_SZ)
        if i < 0:
            break
        hits.append(i)
        i += 1
    need[v] = (nm, hits)

all_hits = sorted({h for _, (nm, hs) in need.items() for h in hs})
print("hits por opcode:", {nm: len(hs) for v, (nm, hs) in need.items()})

def dis_at(va, n=45):
    fo = va - T0
    out = []
    cnt = 0
    for ins in md.disasm(d[fo:fo + 400], va):
        line = f"      {ins.address:#x}: {ins.mnemonic} {ins.op_str}"
        for v, nm in targets.items():
            if f"{v:#x}" in ins.op_str or str(v) in ins.op_str:
                line += f"   <<<< {nm}"
        out.append(line)
        cnt += 1
        if ins.mnemonic == "ret" and cnt > 6:
            break
        if cnt >= n:
            break
    return out

# agrupar hits cercanos (misma función probable)
groups = []
for h in all_hits:
    if groups and h - groups[-1][-1][0] < 0x200:
        groups[-1].append(h)
    else:
        groups.append([h])
print(f"grupos de hits: {len(groups)}")
for g in groups[:6]:
    start = g[0]
    va = T0 + start
    print(f"\n===== grupo @{va:#x} ({len(g)} hits: {[hex(x) for x in g]}) =====")
    # retroceder al prólogo más cercano: buscar 55 48 89 e5 hacia atrás hasta 0x200
    back = max(0, start - 0x200)
    pro = d.rfind(b"\x55\x48\x89\xe5", back, start)
    base_va = T0 + pro if pro >= 0 else va - 32
    for l in dis_at(base_va):
        print(l)
