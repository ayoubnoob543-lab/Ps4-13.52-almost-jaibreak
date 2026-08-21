#!/usr/bin/env python3
"""Read-only signature scanner for PS4 PUP bytes; never extracts or executes data."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SIGNATURES = {
    "SLB2": b"SLB2",
    "SCEUF": b"SCEUF",
    "SELF_magic": b"\x7fSELF",
    "PKG_magic": b"\x7fPKG",
    "PKG_ascii": b"PKG",
    "SCE": b"SCE",
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
    b"ps2-emu-compiler",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def scan(path: Path) -> dict:
    hits = {name: [] for name in SIGNATURES}
    literal_hits = {needle.decode("ascii"): [] for needle in LITERALS}
    overlap = max(map(len, (*SIGNATURES.values(), *LITERALS))) - 1
    previous = b""
    consumed = 0
    with path.open("rb") as fh:
        while block := fh.read(1024 * 1024):
            data = previous + block
            base = consumed - len(previous)
            for name, needle in SIGNATURES.items():
                start = data.find(needle)
                while start >= 0:
                    hits[name].append(base + start)
                    start = data.find(needle, start + 1)
            for needle in LITERALS:
                key = needle.decode("ascii")
                start = data.find(needle)
                while start >= 0:
                    literal_hits[key].append(base + start)
                    start = data.find(needle, start + 1)
            previous = data[-overlap:]
            consumed += len(block)
    return {
        "path": str(path.resolve()),
        "size": path.stat().st_size,
        "sha256": sha256(path),
        "decryption_performed": False,
        "execution_performed": False,
        "signature_hits": hits,
        "literal_hits": literal_hits,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("pup", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = scan(args.pup)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
