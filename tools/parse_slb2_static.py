#!/usr/bin/env python3
"""Conservative static parser for the outer PS4 SLB2/PUP container."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

HEADER_SIZE = 0x20
ENTRY_SIZE = 0x30
SECTOR_SIZE = 0x200
MAGIC = b"SLB2"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def parse(path: Path) -> dict:
    size = path.stat().st_size
    if size < HEADER_SIZE:
        raise ValueError("file shorter than SLB2 header")
    with path.open("rb") as fh:
        header = fh.read(HEADER_SIZE)
        if header[:4] != MAGIC:
            raise ValueError("missing SLB2 magic")
        version, flags, entry_count, size_in_sectors = struct.unpack_from("<IIII", header, 4)
        table_end = HEADER_SIZE + entry_count * ENTRY_SIZE
        if entry_count == 0 or entry_count > 1024 or table_end > size:
            raise ValueError("invalid SLB2 entry table bounds")
        entries = []
        for index in range(entry_count):
            raw = fh.read(ENTRY_SIZE)
            if len(raw) != ENTRY_SIZE:
                raise ValueError("truncated SLB2 entry")
            start_sector, file_size = struct.unpack_from("<II", raw, 0)
            name = raw[0x10:0x30].split(b"\0", 1)[0].decode("ascii", "replace")
            start = start_sector * SECTOR_SIZE
            end = start + file_size
            entries.append({
                "index": index,
                "name": name,
                "start_sector": start_sector,
                "offset": start,
                "size": file_size,
                "end_exclusive": end,
                "within_container": end <= size,
                "sha256": None,
                "classification": "VERIFIED_METADATA" if end <= size else "REQUIRES_REANALYSIS",
            })
        for entry in entries:
            if entry["within_container"]:
                fh.seek(entry["offset"])
                h = hashlib.sha256()
                remaining = entry["size"]
                while remaining:
                    block = fh.read(min(1024 * 1024, remaining))
                    if not block:
                        raise ValueError("unexpected EOF while hashing entry")
                    h.update(block)
                    remaining -= len(block)
                entry["sha256"] = h.hexdigest()
    return {
        "path": str(path),
        "size": size,
        "sha256": sha256(path),
        "format": "SLB2 outer PUP container",
        "magic": "SLB2",
        "version": version,
        "flags": flags,
        "entry_count": entry_count,
        "size_in_sectors": size_in_sectors,
        "declared_container_bytes": size_in_sectors * SECTOR_SIZE,
        "container_size_matches_declared_sectors": size_in_sectors * SECTOR_SIZE == size,
        "decryption_performed": False,
        "entries": entries,
        "classification": "VERIFIED_METADATA",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("--json", type=Path, required=True)
    args = ap.parse_args()
    result = parse(args.image)
    args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
