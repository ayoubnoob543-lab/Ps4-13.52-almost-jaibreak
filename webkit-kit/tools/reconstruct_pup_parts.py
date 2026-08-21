#!/usr/bin/env python3
"""Reconstruct local PUP files from private parts and verify SHA-256."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("parts_dir", type=Path)
    ap.add_argument("--firmware", choices=["13.50", "13.52"], required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    prefix = f"PS4SYS_{args.firmware.replace('.', '')}"
    expected = [
        item for item in manifest["files"]
        if Path(item["path"]).name.startswith(prefix + ".part-")
    ]
    expected.sort(key=lambda item: Path(item["path"]).name)
    parts = sorted(args.parts_dir.glob(prefix + ".part-*"))
    if len(parts) != len(expected):
        raise SystemExit(f"part count mismatch: found={len(parts)} expected={len(expected)}")

    h = hashlib.sha256()
    total = 0
    with args.output.open("wb") as out:
        for index, (part, block) in enumerate(zip(parts, expected)):
            data = part.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            if len(data) != block["size"] or digest != block["sha256"]:
                raise SystemExit(
                    f"part {index} verification failed: size={len(data)} hash={digest}"
                )
            out.write(data)
            h.update(data)
            total += len(data)

    image_manifest = json.loads(
        Path(args.manifest).with_name("PUP_BYTE_MANIFEST_1350_1352.json").read_text(
            encoding="utf-8"
        )
    )
    image = image_manifest["files"][0 if args.firmware == "13.50" else 1]
    digest = h.hexdigest()
    if total != image["size"] or digest != image["sha256"]:
        raise SystemExit(f"image verification failed: size={total} hash={digest}")
    print(json.dumps({
        "firmware": args.firmware,
        "parts": len(parts),
        "size": total,
        "sha256": digest,
        "output": str(args.output.resolve()),
        "per_part_verification": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
