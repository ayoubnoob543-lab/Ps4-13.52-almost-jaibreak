#!/usr/bin/env python3
"""Static candidate scanner for PS4 kernel structures.

This is deliberately conservative: it reports byte-pattern candidates only.
It never derives an address by firmware delta and never labels a candidate as
confirmed without a target-kernel hash and corroborating references.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_PATTERNS = {
    "sysent": [],
    "pmap_protect": [],
    "allproc": [],
    "rootvnode": [],
    "kernel_map": [],
}


def masked_hits(blob: bytes, pattern: bytes, mask: bytes) -> list[int]:
    if not pattern or len(pattern) != len(mask):
        return []
    return [
        off for off in range(0, len(blob) - len(pattern) + 1)
        if all((b & m) == (p & m) for b, p, m in zip(blob[off:off + len(pattern)], pattern, mask))
    ]


def parse(value: str) -> bytes:
    return bytes.fromhex("".join(value.split())) if value else b""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", type=Path, required=True)
    ap.add_argument("--patterns", type=Path)
    ap.add_argument("--firmware", default="unknown")
    args = ap.parse_args()

    blob = args.kernel.read_bytes()
    cfg = json.loads(args.patterns.read_text()) if args.patterns else {"patterns": DEFAULT_PATTERNS}
    result = {
        "kernel": str(args.kernel),
        "firmware_label": args.firmware,
        "size": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "candidates": {},
        "classification": "UNVERIFIED",
        "rule": "Candidates require same-build bytes, function boundaries, XREFs and structure validation."
    }
    for name, specs in cfg.get("patterns", {}).items():
        hits = []
        for spec in specs:
            p = parse(spec.get("bytes", ""))
            m = parse(spec.get("mask", "")) if spec.get("mask") else b"\xff" * len(p)
            hits.extend(hex(x) for x in masked_hits(blob, p, m))
        result["candidates"][name] = sorted(set(hits))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
