from pathlib import Path
import zlib, hashlib
src = Path('/home/ubuntu/firmware-lab/research/webkit-1302/upstream/osm-provenance/binary-assets/fusion14.bin')
out = Path('/home/ubuntu/firmware-lab/research/webkit-1302/upstream/osm-provenance/binary-assets/fusion14-embedded.elf')
data = src.read_bytes()
for i in range(len(data)-2):
    if data[i] == 0x78 and data[i+1] in (0x01, 0x5e, 0x9c, 0xda):
        try:
            obj = zlib.decompress(data[i:])
        except Exception:
            continue
        if obj.startswith(b'\x7fELF'):
            out.write_bytes(obj)
            print('source_sha256', hashlib.sha256(data).hexdigest())
            print('source_offset', hex(i))
            print('embedded_size', len(obj))
            print('embedded_sha256', hashlib.sha256(obj).hexdigest())
            print('output', out)
            break
else:
    raise SystemExit('no embedded ELF found')
