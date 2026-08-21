#!/usr/bin/env python3
"""Find equal byte runs in the protected header of PS4 PUP entries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PAIRS = {
    'UPDATE1': {'a': (1024, 4832), 'b': (1024, 4832)},
    'UPDATE2': {'a': (326027776, 1248), 'b': (326028288, 1248)},
}


def read(path: Path, offset: int, size: int) -> bytes:
    with path.open('rb') as f:
        f.seek(offset)
        return f.read(size)


def runs(a: bytes, b: bytes, start: int = 16) -> list[dict[str, int]]:
    result = []
    i = start
    while i < min(len(a), len(b)):
        if a[i] != b[i]:
            i += 1
            continue
        begin = i
        while i < min(len(a), len(b)) and a[i] == b[i]:
            i += 1
        result.append({'offset': begin, 'length': i - begin})
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('image_a', type=Path)
    ap.add_argument('image_b', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    result = {'decryption_performed': False, 'execution_performed': False, 'entries': {}}
    for name, pair in PAIRS.items():
        aoff, size = pair['a']; boff, _ = pair['b']
        a = read(args.image_a, aoff, size)
        b = read(args.image_b, boff, size)
        result['entries'][name] = {
            'header_size': size,
            'equal_byte_count': sum(x == y for x, y in zip(a[16:], b[16:])),
            'equal_runs': runs(a, b),
        }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
