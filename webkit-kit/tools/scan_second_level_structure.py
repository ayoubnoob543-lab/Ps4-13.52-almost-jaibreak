#!/usr/bin/env python3
"""Read-only structural scan for PS4SYS/SLB2 inner entries.

This tool does not decrypt, extract, execute, or assign module provenance.
It records container metadata, known inner-entry headers, conservative magic
hits, and literal WebKit markers. Hits inside high-entropy data are only
candidates and must not be treated as valid module headers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

INNER_HEADER = bytes.fromhex("4f153d1d00010112")
MAGICS = {
    "SLB2": b"SLB2",
    "SELF": b"\x7fSELF",
    "ELF": b"\x7fELF",
    "PKG": b"\x7fPKG",
    "PKG_ASCII": b"PKG",
    "SCEUF": b"SCEUF",
}
LITERALS = [
    b"libSceNKWebKit",
    b"libkernel_web",
    b"JavaScriptCore",
    b"WebKit",
    b"CSSFontFace",
    b"MarkedVector",
    b"CloneDeserializer",
    b"CloneSerializer",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_all(path: Path, needle: bytes) -> list[int]:
    hits: list[int] = []
    overlap = len(needle) - 1
    previous = b""
    consumed = 0
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            data = previous + block
            base = consumed - len(previous)
            start = data.find(needle)
            while start >= 0:
                hits.append(base + start)
                start = data.find(needle, start + 1)
            previous = data[-overlap:] if overlap else b""
            consumed += len(block)
    return hits


def scan(path: Path) -> dict[str, object]:
    return {
        "path": str(path.resolve()),
        "size": path.stat().st_size,
        "sha256": sha256(path),
        "decryption_performed": False,
        "execution_performed": False,
        "inner_header": INNER_HEADER.hex(),
        "inner_header_hits": find_all(path, INNER_HEADER),
        "magic_hits": {name: find_all(path, value) for name, value in MAGICS.items()},
        "literal_hits": {value.decode("ascii"): find_all(path, value) for value in LITERALS},
        "interpretation": "Candidate offsets only; no hit is a validated module header without format validation.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {"images": [scan(path) for path in args.images]}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
