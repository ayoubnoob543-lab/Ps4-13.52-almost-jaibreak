#!/usr/bin/env python3
"""Static integrity and offset sanity checks for the supplied libkernel dump.

This script reads bytes only. It does not execute the dump, payloads, exploits or
hardware-dependent code. Offsets are file-relative from the beginning of the
combined blob and the declared values are intentionally unchanged.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

EXPECTED_SHA256 = "ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c"
EXPECTED_COMBINED_SIZE = 0x75000
EXPECTED_CHUNK_SIZE = 0x27000
CHUNKS = [("lk_dump1.bin", 0x00000), ("lk_dump2.bin", 0x27000), ("lk_dump3.bin", 0x4E000)]
OFFSETS = {
    "usleep_anchor": 0x013B20, "open": 0x0148D0, "close": 0x014900,
    "read": 0x014870, "write": 0x0148A0, "notify": 0x019320,
    "socket": 0x0045F0, "connect": 0x00C990, "connect_alt": 0x00C970,
    "stat": 0x015310, "pread": 0x015460, "pwrite": 0x015490,
    "lseek": 0x0154F0, "unlink": 0x014930, "jitshm_create_stub": 0x00510,
    "jitshm_alias_stub": 0x00530, "dispatch_candidate": 0x114E0,
    "error_helper": 0x001BB0,
}
PROLOGUES = (bytes.fromhex("55 48 89"), bytes.fromhex("55 41 57"), bytes.fromhex("55 41 56"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


def read_required(path: Path, label: str) -> bytes:
    if not path.exists():
        fail(f"missing required {label}: {path}")
    if not path.is_file():
        fail(f"required {label} is not a regular file: {path}")
    try:
        data = path.read_bytes()
    except OSError as exc:
        fail(f"cannot read {label} {path}: {exc}")
    if not data:
        fail(f"required {label} is empty: {path}")
    return data


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="repository directory")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()
    root = Path(args.repo).resolve()
    errors = []
    try:
        combined_path = root / "libkernel_sys_13.52.bin"
        combined = read_required(combined_path, "combined dump")
        if len(combined) != EXPECTED_COMBINED_SIZE:
            fail(f"combined dump size {len(combined)} != expected {EXPECTED_COMBINED_SIZE}")

        chunks = []
        concat = bytearray()
        for name, base in CHUNKS:
            data = read_required(root / name, f"dump chunk {name}")
            if len(data) != EXPECTED_CHUNK_SIZE:
                fail(f"{name} size {len(data)} != expected {EXPECTED_CHUNK_SIZE}")
            if base + len(data) > len(combined):
                fail(f"chunk range exceeds combined dump: {name} base={hex(base)}")
            chunks.append({"file": name, "base": hex(base), "size": len(data), "sha256": sha256(data)})
            concat.extend(data)

        combined_hash = sha256(combined)
        concat_hash = sha256(concat)
        if combined_hash != EXPECTED_SHA256:
            fail(f"combined dump SHA-256 mismatch: got {combined_hash}, expected {EXPECTED_SHA256}")
        if bytes(concat) != combined:
            fail("chunk concatenation does not match the combined dump byte-for-byte")

        offsets = {}
        for name, off in OFFSETS.items():
            if off < 0 or off + 8 > len(combined):
                fail(f"offset window out of range: {name}={hex(off)}")
            data = combined[off:off + 8]
            offsets[name] = {
                "offset": hex(off),
                "bytes": data.hex(),
                "prologue_like": data[:3] in PROLOGUES,
            }

        result = {
            "combined": {
                "file": combined_path.name,
                "size": len(combined),
                "sha256": combined_hash,
                "expected_sha256": EXPECTED_SHA256,
                "sha256_match": True,
            },
            "concatenation": {
                "size": len(concat),
                "sha256": concat_hash,
                "matches_combined": True,
            },
            "chunks": chunks,
            "offsets": offsets,
            "static_only": True,
            "note": "A prologue match is only a structural sanity check; it does not prove a symbol identity or firmware version.",
        }
    except RuntimeError as exc:
        errors.append(str(exc))
        result = {"static_only": True, "errors": errors}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result)
        return 2

    print(json.dumps(result, indent=2) if args.json else result)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(json.dumps({"static_only": True, "errors": [str(exc)]}) if "--json" in sys.argv else f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
