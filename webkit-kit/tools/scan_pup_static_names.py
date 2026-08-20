#!/usr/bin/env python3
"""Scan raw PUP entry bytes for literal module names; no decryption or execution."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

TARGETS = (
    b"libSceNKWebKit.sprx",
    b"libkernel_web.sprx",
    b"libSceLibcInternal.sprx",
    b"eboot.bin",
    b"WebProcess",
    b"JSCell",
    b"MarkedVector",
    b"CloneSerializer",
)


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while block := fh.read(chunk_size):
            digest.update(block)
    return digest.hexdigest()


def scan_range(fh, start: int, size: int, chunk_size: int = 1024 * 1024) -> dict:
    hits = {target.decode("ascii"): [] for target in TARGETS}
    fh.seek(start)
    overlap = max(map(len, TARGETS)) - 1
    previous = b""
    consumed = 0
    while consumed < size:
        block = fh.read(min(chunk_size, size - consumed))
        if not block:
            raise ValueError("unexpected EOF in PUP entry")
        data = previous + block
        base = start + consumed - len(previous)
        for target in TARGETS:
            needle = target
            pos = data.find(needle)
            while pos >= 0:
                absolute = base + pos
                if absolute >= start and absolute < start + size:
                    hits[target.decode("ascii")].append(absolute)
                pos = data.find(needle, pos + 1)
        previous = data[-overlap:]
        consumed += len(block)
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pup", type=Path)
    ap.add_argument("--entries-json", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    metadata = json.loads(args.entries_json.read_text(encoding="utf-8"))
    result = {
        "schema": "ps4-1352-pup-static-name-scan-v1",
        "pup": str(args.pup.resolve()),
        "pup_size": args.pup.stat().st_size,
        "pup_sha256": file_sha256(args.pup),
        "decryption_performed": False,
        "execution_performed": False,
        "entries": [],
    }
    with args.pup.open("rb") as fh:
        for entry in metadata["entries"]:
            hits = scan_range(fh, entry["offset"], entry["size"])
            result["entries"].append({"name": entry["name"], "offset": entry["offset"], "size": entry["size"], "literal_hits": hits})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
