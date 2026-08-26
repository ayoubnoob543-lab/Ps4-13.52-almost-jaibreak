#!/usr/bin/env python3
from pathlib import Path
import struct, zlib, hashlib

p = Path('/home/ubuntu/firmware-lab/research/webkit-1302/upstream/osm-provenance/binary-assets/fusion14.bin')
data = p.read_bytes()
print('file_size', len(data))
print('sha256', hashlib.sha256(data).hexdigest())
# Search for zlib streams and custom resource-looking headers without executing payload.
for i in range(len(data)-2):
    if data[i] == 0x78 and data[i+1] in (0x01,0x5e,0x9c,0xda):
        try:
            obj = zlib.decompress(data[i:])
        except Exception:
            continue
        print('zlib_stream', hex(i), 'compressed_available', len(data)-i, 'decompressed_size', len(obj), 'decompressed_sha256', hashlib.sha256(obj).hexdigest(), 'prefix', obj[:16].hex())
        if len(obj) >= 4 and obj[:4] == b'\x7fELF':
            print('classification', 'decompressed output begins ELF')
        break
# Print printable strings around Kernel.elf and resource markers, with offsets.
for needle in (b'Kernel.elf', b'Installing Kernel ELF', b'Failed to decompress Kernel.elf', b'ELFBase'):
    start = 0
    while True:
        j = data.find(needle, start)
        if j < 0: break
        print('string', needle.decode(errors='replace'), hex(j))
        start = j + 1
