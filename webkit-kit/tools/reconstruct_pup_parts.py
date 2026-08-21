#!/usr/bin/env python3
"""Reconstruct local PUP files from private parts and verify SHA-256."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('manifest', type=Path)
    ap.add_argument('parts_dir', type=Path)
    ap.add_argument('--firmware', choices=['13.50', '13.52'], required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    prefix = f'PS4SYS_{args.firmware.replace(".", "")}'
    parts = sorted(args.parts_dir.glob(prefix + '.part-*'))
    if not parts:
        raise SystemExit(f'no parts found for {args.firmware}')
    expected = manifest['files'][0 if args.firmware == '13.50' else 1]

    h = hashlib.sha256()
    total = 0
    with args.output.open('wb') as out:
        for part in parts:
            data = part.read_bytes()
            out.write(data)
            h.update(data)
            total += len(data)
    digest = h.hexdigest()
    if total != expected['size'] or digest != expected['sha256']:
        raise SystemExit(f'verification failed: size={total} hash={digest}')
    print(json.dumps({'firmware': args.firmware, 'parts': len(parts), 'size': total, 'sha256': digest, 'output': str(args.output.resolve())}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
