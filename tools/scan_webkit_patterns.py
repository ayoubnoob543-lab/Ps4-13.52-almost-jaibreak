#!/usr/bin/env python3
"""Static WebKit pattern scanner.

The scanner accepts a raw/ELF/SELF byte image and a JSON pattern config. It
never executes the image. Patterns use hex bytes plus an optional mask, so
firmware-dependent values can remain unset until a real 13.52 image exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def parse_hex(value: str) -> bytes:
    value = "".join(value.split())
    return bytes.fromhex(value) if value else b""


def find_masked(blob: bytes, pattern: bytes, mask: bytes) -> list[int]:
    if not pattern or len(pattern) != len(mask) or len(pattern) > len(blob):
        return []
    out = []
    end = len(blob) - len(pattern) + 1
    for off in range(end):
        window = blob[off:off + len(pattern)]
        if all((b & m) == (p & m) for b, p, m in zip(window, pattern, mask)):
            out.append(off)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", type=Path, required=True)
    ap.add_argument("--config", type=Path, default=Path(__file__).with_name("webkit_1352_migration.json"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    image = args.image.read_bytes()
    cfg = json.loads(args.config.read_text())
    result = {
        "image": str(args.image),
        "size": len(image),
        "sha256": hashlib.sha256(image).hexdigest(),
        "target_firmware": cfg.get("target_firmware"),
        "patterns": {},
        "warning": "No runtime base, loader, GOT/PLT or semantic function identity is inferred from a match."
    }
    for name, entry in cfg.get("patterns", {}).items():
        pattern = parse_hex(entry.get("bytes", ""))
        mask_text = entry.get("mask", "")
        mask = parse_hex(mask_text) if mask_text else b"\xff" * len(pattern)
        hits = find_masked(image, pattern, mask) if pattern else []
        result["patterns"][name] = {
            "status": "DIRECT_BYTES" if hits else entry.get("status", "REQUIRES_REANALYSIS"),
            "hits": [hex(x) for x in hits],
            "pattern_length": len(pattern),
            "semantic_identity": "REQUIRES_REANALYSIS" if hits else "ABSENT",
            "note": "Byte match only; confirm XREFs, module headers and same-build provenance before assigning a symbol."
        }
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else text_result(result))
    return 0


def text_result(result: dict) -> str:
    lines = [f"image={result['image']}", f"size={result['size']}", f"sha256={result['sha256']}"]
    for name, item in result["patterns"].items():
        lines.append(f"{name}: {item['status']} hits={','.join(item['hits']) or '-'}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
