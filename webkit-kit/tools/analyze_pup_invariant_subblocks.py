#!/usr/bin/env python3
"""Characterize the invariant 0xf0-byte region in 0x50-byte subblocks."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

BASES = {
    "UPDATE1": (1024 + 0x6F0, 0xF0),
    "UPDATE2": (326027776 + 0x1B0, 0xF0),
}


def entropy(data: bytes) -> float:
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts if c)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    blob = args.image.read_bytes()
    result = {"decryption_performed": False, "execution_performed": False, "entries": {}}
    for name, (offset, size) in BASES.items():
        region = blob[offset:offset + size]
        if len(region) != size:
            raise SystemExit(f"short region for {name}")
        parts = []
        for index in range(3):
            part = region[index * 0x50:(index + 1) * 0x50]
            fields = [part[:0x10], part[0x10:0x20], part[0x20:0x40], part[0x40:0x50]]
            parts.append({
                "index": index,
                "sha256": hashlib.sha256(part).hexdigest(),
                "entropy": entropy(part),
                "unique_bytes": len(set(part)),
                "field_sha256": [hashlib.sha256(x).hexdigest() for x in fields],
                "field_entropy": [entropy(x) for x in fields],
                "hex_prefix": part[:16].hex(),
            })
        result["entries"][name] = {"offset": offset, "size": size, "sha256": hashlib.sha256(region).hexdigest(), "parts": parts}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
