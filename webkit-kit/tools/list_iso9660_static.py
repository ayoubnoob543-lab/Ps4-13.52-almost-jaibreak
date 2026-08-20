#!/usr/bin/env python3
"""List ISO9660 directory metadata without mounting or extracting files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SECTOR = 2048


def record(data: bytes, offset: int) -> tuple[dict, int] | None:
    length = data[offset]
    if length == 0:
        return None
    raw = data[offset : offset + length]
    if len(raw) < 34:
        return None
    extent = int.from_bytes(raw[2:6], "little")
    size = int.from_bytes(raw[10:14], "little")
    flags = raw[25]
    name_len = raw[32]
    name = raw[33 : 33 + name_len].decode("ascii", "replace")
    if name in {"\x00", "\x01"}:
        name = "." if name == "\x00" else ".."
    return {"offset": offset, "extent_sector": extent, "size": size, "directory": bool(flags & 2), "name": name}, offset + length


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    data = args.image.read_bytes()
    pvd = data[16 * SECTOR : 17 * SECTOR]
    if pvd[1:6] != b"CD001":
        raise SystemExit("no ISO9660 primary volume descriptor")
    root, _ = record(pvd, 156)  # type: ignore[arg-type]
    entries: list[dict] = []
    visited: set[int] = set()

    def walk(extent: int, size: int, prefix: str) -> None:
        if extent in visited:
            return
        visited.add(extent)
        start = extent * SECTOR
        end = min(start + size, len(data))
        pos = start
        while pos < end:
            if data[pos] == 0:
                pos = ((pos // SECTOR) + 1) * SECTOR
                continue
            parsed = record(data, pos)
            if parsed is None:
                break
            item, pos = parsed
            if item["name"] in {".", ".."}:
                continue
            path = f"{prefix}/{item['name']}"
            out = {k: item[k] for k in ("name", "extent_sector", "size", "directory")}
            out["path"] = path
            out["classification"] = "VERIFIED_METADATA"
            entries.append(out)
            if item["directory"]:
                walk(item["extent_sector"], item["size"], path)

    walk(root["extent_sector"], root["size"], "")
    result = {
        "schema": "iso9660-static-list-v1",
        "path": str(args.image.resolve()),
        "size": len(data),
        "volume_id": pvd[40:72].decode("ascii", "replace").strip(),
        "root": root,
        "mount_or_extraction_performed": False,
        "entries": entries,
        "classification": "VERIFIED_METADATA",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
