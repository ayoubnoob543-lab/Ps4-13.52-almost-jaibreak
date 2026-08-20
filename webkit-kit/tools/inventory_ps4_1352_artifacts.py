#!/usr/bin/env python3
"""Inventory PS4 13.52 artifacts without loading or executing them.

The inventory is deliberately negative-safe: missing retail modules remain
MISSING/UNVERIFIED, while a present file is only DIRECT_BYTES after hashing.
No ELF/SELF/SPRX parser or dynamic loader is invoked here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

EXPECTED = {
    "libSceNKWebKit.sprx": "retail WebKit module",
    "libkernel_web.sprx": "browser kernel module",
    "libSceLibcInternal.sprx": "browser libc module",
    "eboot.bin": "browser executable candidate",
}
PATTERNS = {"*.sprx", "*.self", "*.nxdp", "*.orbsdmp", "*.dmp", "*orbisstate*"}
KNOWN_STRUCTURAL = {
    "Sony PS4 WebKit OSS source 13.00 family": "STRUCTURAL",
    "PS4 retail WebKit 13.52 identity": "UNVERIFIED",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", action="append", default=[], help="directory to scan; repeatable")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    roots = [Path(p).resolve() for p in (args.root or ["/home/ubuntu/wpe-private-repo", "/home/ubuntu/Downloads", "/tmp"])]
    found: list[dict[str, object]] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for base, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__"}]
            for name in files:
                path = Path(base) / name
                if path in seen:
                    continue
                if name in EXPECTED or any(path.match(pattern) for pattern in PATTERNS):
                    seen.add(path)
                    item = {
                        "path": str(path),
                        "basename": name,
                        "size": path.stat().st_size,
                        "sha256": sha256(path),
                        "classification": "DIRECT_BYTES",
                        "role": EXPECTED.get(name, "unclassified candidate"),
                    }
                    found.append(item)
    expected = []
    for name, role in EXPECTED.items():
        matches = [item for item in found if item["basename"] == name]
        expected.append({
            "artifact": name,
            "role": role,
            "status": "DIRECT_BYTES" if matches else "MISSING/UNVERIFIED",
            "matches": matches,
        })
    known_kernel = Path("/home/ubuntu/wpe-private-repo/webkit-kit/libkernel_sys_13.52.bin")
    if known_kernel.exists():
        found.append({
            "path": str(known_kernel),
            "basename": known_kernel.name,
            "size": known_kernel.stat().st_size,
            "sha256": sha256(known_kernel),
            "classification": "DIRECT_BYTES",
            "role": "syscall/kernel dump; not a WebKit retail module",
        })
    report = {
        "schema": "ps4-1352-artifact-inventory-v1",
        "scope": "static filenames and SHA-256 only; no loading/execution",
        "roots": [str(root) for root in roots],
        "expected": expected,
        "found": found,
        "structural_context": KNOWN_STRUCTURAL,
        "conclusion": "No retail WebKit 13.52 module is present in scanned roots" if not any(item["status"] == "DIRECT_BYTES" for item in expected) else "At least one named retail candidate is present and hashed",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
