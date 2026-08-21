#!/usr/bin/env python3
"""Compare visible PS4 PUP/SLB2 metadata without decrypting payloads."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

SLB2_HEADER = 0x20
ENTRY_SIZE = 0x30
SECTOR = 0x200
INNER_HEADER_LEN = 16


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def parse(path: Path) -> dict:
    with path.open('rb') as f:
        header = f.read(SLB2_HEADER)
        magic = header[:4].decode('ascii', 'replace')
        version, flags, count, sectors = struct.unpack_from('<IIII', header, 4)
        entries = []
        table_rows = []
        for idx in range(count):
            raw = f.read(ENTRY_SIZE)
            start_sector, size = struct.unpack_from('<II', raw, 0)
            name = raw[0x10:0x30].split(b'\0', 1)[0].decode('ascii', 'replace')
            table_rows.append((idx, name, start_sector, size))
        for idx, name, start_sector, size in table_rows:
            offset = start_sector * SECTOR
            f.seek(offset)
            inner = f.read(INNER_HEADER_LEN)
            entries.append({
                'index': idx,
                'name': name,
                'start_sector': start_sector,
                'offset': offset,
                'size': size,
                'end_exclusive': offset + size,
                'inner_header_hex': inner.hex(),
                'inner_header_fields_u32le': list(struct.unpack('<4I', inner)) if len(inner) == 16 else None,
                'inner_header_common_prefix_8': inner[:8].hex(),
            })
    return {
        'path': str(path.resolve()),
        'size': path.stat().st_size,
        'sha256': sha256(path),
        'slb2_header_hex': header.hex(),
        'slb2_header_fields_u32le': list(struct.unpack_from('<8I', header)),
        'magic': magic,
        'entry_count': count,
        'declared_bytes': sectors * SECTOR,
        'declared_matches_file': sectors * SECTOR == path.stat().st_size,
        'entries': entries,
    }


def compare(a: dict, b: dict) -> dict:
    fields = ['size', 'entry_count', 'declared_bytes', 'declared_matches_file', 'magic']
    top = {field: {'a': a[field], 'b': b[field], 'equal': a[field] == b[field]} for field in fields}
    header_diff = [i for i, (x, y) in enumerate(zip(bytes.fromhex(a['slb2_header_hex']), bytes.fromhex(b['slb2_header_hex']))) if x != y]
    entries = []
    for ea, eb in zip(a['entries'], b['entries']):
        entries.append({
            'name_a': ea['name'], 'name_b': eb['name'],
            'offset_a': ea['offset'], 'offset_b': eb['offset'], 'offset_delta': eb['offset'] - ea['offset'],
            'size_a': ea['size'], 'size_b': eb['size'], 'size_delta': eb['size'] - ea['size'],
            'start_sector_a': ea['start_sector'], 'start_sector_b': eb['start_sector'],
            'inner_header_a': ea['inner_header_hex'], 'inner_header_b': eb['inner_header_hex'],
            'inner_header_diff_offsets': [i for i, (x, y) in enumerate(zip(bytes.fromhex(ea['inner_header_hex']), bytes.fromhex(eb['inner_header_hex']))) if x != y],
            'inner_prefix_equal': ea['inner_header_common_prefix_8'] == eb['inner_header_common_prefix_8'],
        })
    return {'top_level': top, 'slb2_header_diff_offsets': header_diff, 'entries': entries}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('image_a', type=Path)
    ap.add_argument('image_b', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    a, b = parse(args.image_a), parse(args.image_b)
    result = {'image_a': a, 'image_b': b, 'comparison': compare(a, b), 'decryption_performed': False, 'execution_performed': False}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
