#!/usr/bin/env python3
"""Generate a verifiable manifest for local PS4 PUP files.

The output contains file metadata and SHA-256 hashes for fixed-size blocks.
It never copies, embeds, uploads, decrypts, or executes firmware bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_BLOCK_SIZE = 4 * 1024 * 1024


def sha256_blocks(path: Path, block_size: int) -> tuple[str, list[dict[str, object]]]:
    whole = hashlib.sha256()
    blocks: list[dict[str, object]] = []
    index = 0
    offset = 0
    with path.open('rb') as stream:
        while data := stream.read(block_size):
            whole.update(data)
            blocks.append({
                'index': index,
                'offset': offset,
                'size': len(data),
                'sha256': hashlib.sha256(data).hexdigest(),
            })
            index += 1
            offset += len(data)
    return whole.hexdigest(), blocks


def manifest(path: Path, block_size: int) -> dict[str, object]:
    digest, blocks = sha256_blocks(path, block_size)
    return {
        'path': str(path.resolve()),
        'size': path.stat().st_size,
        'sha256': digest,
        'block_size': block_size,
        'block_count': len(blocks),
        'bytes_embedded': False,
        'decryption_performed': False,
        'execution_performed': False,
        'blocks': blocks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--block-size', type=int, default=DEFAULT_BLOCK_SIZE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = {
        'format': 'local-file-sha256-block-manifest-v1',
        'block_size': args.block_size,
        'files': [manifest(path, args.block_size) for path in args.files],
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
