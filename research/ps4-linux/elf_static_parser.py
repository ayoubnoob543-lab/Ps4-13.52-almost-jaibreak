#!/usr/bin/env python3
import struct, sys
from pathlib import Path

def parse(path):
    b = Path(path).read_bytes()
    if b[:4] != b'\x7fELF' or b[4] != 2 or b[5] != 1:
        print(f'{path}: not ELF64 little-endian')
        return
    e = struct.unpack_from('<16sHHIQQQIHHHHHH', b, 0)
    _, typ, mach, ver, entry, phoff, shoff, flags, ehsize, phentsize, phnum, shentsize, shnum, shstrndx = e
    print(f'{path}: size={len(b)} type={typ} machine={mach} entry=0x{entry:x} sections={shnum} shoff=0x{shoff:x}')
    sections=[]
    for i in range(shnum):
        off=shoff+i*shentsize
        sh=struct.unpack_from('<IIQQQQIIQQ', b, off)
        sections.append(sh)
    shstr=sections[shstrndx]
    names=b[shstr[4]:shstr[4]+shstr[5]]
    def sname(idx):
        end=names.find(b'\0',idx)
        return names[idx:end].decode('ascii','replace')
    for i,sh in enumerate(sections):
        print(f'  section[{i}] {sname(sh[0])} type={sh[1]} off=0x{sh[4]:x} size=0x{sh[5]:x} entsize=0x{sh[9]:x}')
    for i,sh in enumerate(sections):
        if sh[1] not in (2,11) or sh[9] == 0:
            continue
        link=sh[6]
        if link >= len(sections): continue
        strsh=sections[link]
        strtab=b[strsh[4]:strsh[4]+strsh[5]]
        print(f'  symbols from {sname(sh[0])}:')
        n=sh[5]//sh[9]
        for j in range(n):
            so=sh[4]+j*sh[9]
            st_name, info, other, st_shndx, st_value, st_size=struct.unpack_from('<IBBHQQ',b,so)
            end=strtab.find(b'\0',st_name)
            name=strtab[st_name:end].decode('ascii','replace') if st_name < len(strtab) else ''
            if name and any(k in name.lower() for k in ('kernel','kmem','syscall','kexec','firmware','payload','offset','main')):
                print(f'    {name} value=0x{st_value:x} size=0x{st_size:x} bind={info>>4} type={info&15}')

for p in sys.argv[1:]: parse(p)
