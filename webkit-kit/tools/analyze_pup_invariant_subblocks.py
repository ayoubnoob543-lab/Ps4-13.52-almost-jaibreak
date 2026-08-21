#!/usr/bin/env python3
"""Characterize candidate 0xf0-byte regions after documented inner headers."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

HEADERS = {
    "UPDATE1": bytes.fromhex("4f153d1d0001011204000000f006f00b"),
    "UPDATE2": bytes.fromhex("4f153d1d0001011204000000b0013003"),
}
RELATIVE_METADATA_OFFSETS = {"UPDATE1": 0x6F0, "UPDATE2": 0x1B0}


def entropy(data: bytes) -> float:
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts if c)


def find_unique(data: bytes, needle: bytes, name: str) -> int:
    hits = []
    start = 0
    while True:
        pos = data.find(needle, start)
        if pos < 0:
            break
        hits.append(pos)
        start = pos + 1
    if len(hits) != 1:
        raise SystemExit(f"expected one {name} inner header, found {len(hits)}: {hits[:10]}")
    return hits[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    blob = args.image.read_bytes()
    result = {"decryption_performed": False, "execution_performed": False, "entries": {}}
    for name, header in HEADERS.items():
        header_offset = find_unique(blob, header, name)
        offset = header_offset + RELATIVE_METADATA_OFFSETS[name]
        size = 0xF0
        region = blob[offset:offset + size]
        if len(region) != size:
            raise SystemExit(f"short candidate region for {name}")
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
        result["entries"][name] = {
            "header_offset": header_offset,
            "relative_region_offset": RELATIVE_METADATA_OFFSETS[name],
            "offset": offset,
            "size": size,
            "sha256": hashlib.sha256(region).hexdigest(),
            "parts": parts,
        }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
