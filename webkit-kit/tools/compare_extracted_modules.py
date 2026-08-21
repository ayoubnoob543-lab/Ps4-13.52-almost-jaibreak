#!/usr/bin/env python3
"""Static comparison of two user-supplied PS4 module extractions.

This tool reads bytes only. It never loads an ELF/SELF/SPRX as executable,
never invokes code from an input file, and never decrypts or patches inputs.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

TERMS = [
    'libSceNKWebKit', 'libkernel_web', 'JavaScriptCore', 'WebKit',
    'CSSFontFace', 'CSSFontFaceSet', 'FontFaceSet', 'MarkedVector',
    'SerializedScriptValue', 'CloneSerializer', 'CloneDeserializer',
    'DFGStoreBarrierInsertionPhase', 'StoreBarrierInsertionPhase',
    'Phi', 'Upsilon', 'm_featureSettings', 'm_propertiesOrCSSConnection',
]


def digest(path: Path) -> dict:
    md5 = hashlib.md5(); sha = hashlib.sha256(); size = 0
    with path.open('rb') as f:
        while chunk := f.read(1024 * 1024):
            size += len(chunk); md5.update(chunk); sha.update(chunk)
    return {'path': str(path), 'size': size, 'md5': md5.hexdigest(), 'sha256': sha.hexdigest()}


def header_info(path: Path) -> dict:
    with path.open('rb') as f: data = f.read(4096)
    info = {'magic_ascii': data[:16].hex(), 'format': 'unknown'}
    if data[:4] == b'SLB2': info['format'] = 'SLB2'
    elif data[:4] == b'\x7fELF':
        info['format'] = 'ELF'
        info['elf_class'] = {1: 'ELF32', 2: 'ELF64'}.get(data[4], str(data[4]))
        info['elf_data'] = {1: 'little', 2: 'big'}.get(data[5], str(data[5]))
        if data[4] == 2 and data[5] == 1 and len(data) >= 20:
            info['e_machine'] = struct.unpack_from('<H', data, 18)[0]
    elif data[:4] == b'PKG\x00' or data[:4] == b'\x7fPKG': info['format'] = 'PKG-like signature'
    elif data[:4] == b'SCE\x00': info['format'] = 'SCE-like'
    return info


def strings_hits(path: Path) -> dict:
    data = path.read_bytes()
    out = {}
    for term in TERMS:
        hits = []
        start = 0
        raw = term.encode()
        while True:
            pos = data.find(raw, start)
            if pos < 0: break
            hits.append(pos); start = pos + 1
        if hits: out[term] = hits[:100]
    return out


def diff_summary(a: Path, b: Path, limit=128) -> dict:
    first=[]; changed=0; offset=0
    with a.open('rb') as fa, b.open('rb') as fb:
        while True:
            ca=fa.read(1024*1024); cb=fb.read(1024*1024)
            if not ca and not cb: break
            n=min(len(ca),len(cb))
            changed += sum(x != y for x,y in zip(ca[:n], cb[:n]))
            if len(first) < limit:
                for i,(x,y) in enumerate(zip(ca[:n],cb[:n])):
                    if x != y:
                        first.append({'offset':offset+i,'a':x,'b':y})
                        if len(first) >= limit: break
            offset += n
            if len(ca) != len(cb): break
    return {'overlap_bytes_compared': offset, 'changed_bytes_in_overlap': changed, 'first_differences': first}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--fw50', type=Path, required=True)
    ap.add_argument('--fw52', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args=ap.parse_args()
    for p in (args.fw50,args.fw52):
        if not p.is_file(): raise SystemExit(f'not a regular file: {p}')
    result={
        'tool': 'compare_extracted_modules.py',
        'inputs': {'13.50': digest(args.fw50), '13.52': digest(args.fw52)},
        'headers': {'13.50': header_info(args.fw50), '13.52': header_info(args.fw52)},
        'strings': {'13.50': strings_hits(args.fw50), '13.52': strings_hits(args.fw52)},
        'byte_diff': diff_summary(args.fw50,args.fw52),
        'execution_performed': False,
        'decryption_performed': False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__': main()
