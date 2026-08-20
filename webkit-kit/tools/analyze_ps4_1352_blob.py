#!/usr/bin/env python3
"""Static-only analysis for PS4 firmware blobs; never loads or executes them."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for byte in data:
        counts[byte] += 1
    total = len(data)
    return -sum((count / total) * math.log2(count / total) for count in counts if count)


def magic_offsets(data: bytes, magic: bytes) -> list[int]:
    offsets: list[int] = []
    start = 0
    while True:
        index = data.find(magic, start)
        if index < 0:
            return offsets
        offsets.append(index)
        start = index + 1


def printable_strings(data: bytes, minimum: int = 6) -> list[str]:
    result: list[str] = []
    current = bytearray()
    for byte in data + b"\0":
        if 32 <= byte < 127:
            current.append(byte)
        elif len(current) >= minimum:
            result.append(current.decode("ascii", errors="replace"))
            current.clear()
        else:
            current.clear()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    records = []
    for path in args.files:
        data = path.read_bytes()
        records.append({
            "path": str(path.resolve()),
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "classification": "DIRECT_BYTES",
            "format_observation": "raw data; no ELF magic at offset 0" if not data.startswith(b"\x7fELF") else "ELF magic at offset 0; do not execute",
            "first_32_hex": data[:32].hex(),
            "entropy_bits_per_byte": round(entropy(data), 6),
            "magic_offsets": {
                "ELF": magic_offsets(data, b"\x7fELF"),
                "SELF": magic_offsets(data, b"SCE\x00"),
                "PKZIP": magic_offsets(data, b"PK\x03\x04"),
            },
            "strings": printable_strings(data)[:200],
            "static_only": True,
        })
    report = {"schema": "ps4-1352-static-blob-analysis-v1", "records": records}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
