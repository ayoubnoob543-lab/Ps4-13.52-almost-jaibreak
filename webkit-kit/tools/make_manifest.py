#!/usr/bin/env python3
"""Create a deterministic SHA-256 manifest for a directory."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

EXCLUDED = {"SHA256SUMS", "MANIFEST.tsv"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("directory", type=Path)
    args = ap.parse_args()
    root = args.directory.resolve()
    if not root.is_dir():
        ap.error(f"not a directory: {root}")
    for p in sorted(x for x in root.rglob("*") if x.is_file() and x.name not in EXCLUDED):
        print(f"{digest(p)}  {p.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
