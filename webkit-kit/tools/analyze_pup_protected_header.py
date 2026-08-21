#!/usr/bin/env python3
"""Inspect only the visible PUP fragment header and protected header extent."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

ENTRY_OFFSETS = {
    '13.50': {'PS4UPDATE1.PUP': (1024, 326026471), 'PS4UPDATE2.PUP': (326027776, 177266167)},
    '13.52': {'PS4UPDATE1.PUP': (1024, 326026951), 'PS4UPDATE2.PUP': (326028288, 177282367)},
}


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts if c)


def parse_header(data: bytes) -> dict[str, object]:
    if len(data) < 16:
        raise ValueError('short header')
    magic, unknown_04, unknown_08, flags, unknown_0b, unknown_0c, unknown_0e = struct.unpack('<IIHBBHH', data[:16])
    protected_extent = unknown_0c + unknown_0e
    return {
        'magic_hex': f'{magic:08x}',
        'unknown_04_hex': f'{unknown_04:08x}',
        'unknown_08': unknown_08,
        'flags': flags,
        'unknown_0b': unknown_0b,
        'header_size_field': unknown_0c,
        'metadata_size_field': unknown_0e,
        'protected_header_extent': protected_extent,
        'visible_header_size': 16,
        'protected_header_bytes_after_visible': max(0, protected_extent - 16),
        'raw_hex': data[:16].hex(),
    }


def read_entry(path: Path, offset: int, size: int) -> dict[str, object]:
    with path.open('rb') as f:
        f.seek(offset)
        protected = f.read(0x2000)
    parsed = parse_header(protected)
    extent = int(parsed['protected_header_extent'])
    protected_data = protected[:extent]
    return {
        **parsed,
        'entry_offset': offset,
        'entry_size': size,
        'entry_end': offset + size,
        'protected_header_sha256': hashlib.sha256(protected_data).hexdigest(),
        'protected_header_entropy': entropy(protected_data[16:]),
        'protected_header_sample_hex': protected_data[16:64].hex(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('image_1350', type=Path)
    ap.add_argument('image_1352', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    result: dict[str, object] = {'decryption_performed': False, 'execution_performed': False, 'entries': {}}
    for fw, path in [('13.50', args.image_1350), ('13.52', args.image_1352)]:
        result['entries'][fw] = {}
        for name, (offset, size) in ENTRY_OFFSETS[fw].items():
            result['entries'][fw][name] = read_entry(path, offset, size)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
