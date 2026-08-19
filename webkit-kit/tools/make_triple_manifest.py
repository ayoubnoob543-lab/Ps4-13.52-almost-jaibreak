#!/usr/bin/env python3
"""Create a conservative manifest for the three WebKit-related modules."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

NAMES = ["libSceNKWebKit.sprx", "libkernel_web.sprx", "libSceLibcInternal.sprx"]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    modules = []
    for name in NAMES:
        path = args.directory / name
        modules.append(
            {
                "name": name,
                "path": str(path) if path.exists() else None,
                "size": path.stat().st_size if path.exists() else None,
                "sha256": digest(path) if path.is_file() else None,
                "status": "PRESENT_UNVERIFIED" if path.is_file() else "MISSING",
            }
        )
    document = {
        "schema": "webkit-triple-module-manifest/v1",
        "firmware": "13.52",
        "modules": modules,
        "common_build_id": "MISSING",
        "provenance": "REQUIRES_AUTHORIZED_OR_USER_SUPPLIED_SOURCE",
        "promotion_rule": "all three bytes plus coherent manifest/build identity required",
        "absolute_offsets": "DISABLED",
    }
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
