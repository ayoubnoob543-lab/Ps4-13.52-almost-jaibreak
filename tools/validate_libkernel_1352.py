#!/usr/bin/env python3
"""Static validation for the PS4 13.52 libkernel_sys anchor.

This script hashes files, reconstructs the three chunks, checks byte equality,
and inspects bytes at published offsets. It never executes analyzed artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_u64(blob: bytes, off: int) -> int:
    return struct.unpack_from("<Q", blob, off)[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--manifest", type=Path, default=Path(__file__).with_name("libkernel_1352_manifest.json"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text())
    root = args.root
    result = {"root": str(root), "artifact": {}, "chunks": [], "offsets": {}, "reconstruction": {}}

    artifact = root / manifest["artifact"]["path"]
    data = artifact.read_bytes()
    result["artifact"] = {
        "path": str(artifact),
        "exists": artifact.is_file(),
        "size": len(data),
        "size_expected": manifest["artifact"]["size"],
        "sha256": sha256(artifact),
        "sha256_expected": manifest["artifact"]["sha256"],
        "sha256_match": sha256(artifact) == manifest["artifact"]["sha256"],
    }

    chunks = []
    for entry in manifest["chunks"]:
        path = root / entry["path"]
        chunk = path.read_bytes()
        digest = sha256(path)
        item = {
            "path": str(path),
            "exists": path.is_file(),
            "size": len(chunk),
            "size_expected": entry["size"],
            "sha256": digest,
            "sha256_expected": entry["sha256"],
            "sha256_match": digest == entry["sha256"],
            "offset": entry["offset"],
        }
        result["chunks"].append(item)
        chunks.append(chunk)

    combined = b"".join(chunks)
    result["reconstruction"] = {
        "size": len(combined),
        "size_matches_artifact": len(combined) == len(data),
        "sha256": hashlib.sha256(combined).hexdigest(),
        "sha256_matches_artifact": combined == data,
        "last_byte_offset": hex(len(combined) - 1),
    }

    for name, entry in manifest["symbols"].items():
        off = int(entry["offset"], 16)
        window = data[off:off + 16]
        result["offsets"][name] = {
            "offset": entry["offset"],
            "category": entry["category"],
            "bytes": window.hex(),
            "syscall": entry.get("syscall"),
            "in_bounds": off < len(data),
        }
        if name == "jitshm_create" and len(window) >= 7:
            result["offsets"][name]["mov_rax_imm"] = hex(struct.unpack_from("<I", window, 3)[0]) if window[:3] == b"H\xc7\xc0" else None
        if name == "jitshm_alias" and len(window) >= 7:
            result["offsets"][name]["mov_rax_imm"] = hex(struct.unpack_from("<I", window, 3)[0]) if window[:3] == b"H\xc7\xc0" else None

    for name, entry in manifest["kernel_offsets"].items():
        off = int(entry["offset"], 16)
        result["offsets"][name] = {
            "offset": entry["offset"],
            "category": entry["category"],
            "reason": entry["reason"],
            "present_in_libkernel_blob": off < len(data),
            "warning": "This is a kernel offset candidate; libkernel bytes cannot validate it."
        }

    print(json.dumps(result, indent=2, sort_keys=True) if args.json else format_text(result))
    return 0


def format_text(result: dict) -> str:
    a = result["artifact"]
    r = result["reconstruction"]
    lines = [
        f"artifact={a['path']}",
        f"size={a['size']} expected={a['size_expected']}",
        f"sha256={a['sha256']} match={a['sha256_match']}",
        f"reconstruction_size={r['size']} match={r['sha256_matches_artifact']}",
        f"reconstruction_last_byte={r['last_byte_offset']}",
    ]
    for name, item in result["offsets"].items():
        lines.append(f"{name} {item['offset']} {item['category']} bytes={item.get('bytes', '')}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
