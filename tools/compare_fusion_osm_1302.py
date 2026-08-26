from pathlib import Path
import re

fusion = Path('research/webkit-1302/upstream/fusion-1302/Offsets-1302.h').read_text()
osm = Path('research/webkit-1302/upstream/osm-kernel-sdk/firmware-1302.yaml').read_text()

f = dict(re.findall(r'addrs->([A-Za-z0-9_]+).*?kernelBase\s*\+\s*(0x[0-9A-Fa-f]+)', fusion))
o = dict(re.findall(r'- name:\s*([A-Za-z0-9_]+)\s*\n\s*offset:\s*(0x[0-9A-Fa-f]+)', osm))
common = sorted(set(f) & set(o))
identical = [k for k in common if f[k].lower() == o[k].lower()]
different = [(k, f[k], o[k]) for k in common if f[k].lower() != o[k].lower()]
print(f'Fusion assignments: {len(f)}')
print(f'OSM YAML assignments: {len(o)}')
print(f'Common names: {len(common)}')
print(f'Identical common offsets: {len(identical)}')
print(f'Different common offsets: {len(different)}')
for k, a, b in different:
    print(f'DIFF\t{k}\tFusion={a}\tOSM={b}')
print('TARGETS')
for k in ['patch_mount', 'M_MOUNT', 'getnewvnode', 'vn_fullpath', 'kern_open', 'malloc', 'free', 'kmem_alloc', 'kmem_free']:
    print(f'{k}\tFusion={f.get(k)}\tOSM={o.get(k)}')
print('OSM-only names')
for k in sorted(set(o)-set(f)):
    print(f'{k}\t{o[k]}')
print('Fusion-only names')
for k in sorted(set(f)-set(o)):
    print(f'{k}\t{f[k]}')
