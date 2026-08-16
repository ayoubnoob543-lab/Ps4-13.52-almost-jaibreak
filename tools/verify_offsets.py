#!/usr/bin/env python3
"""Static integrity and offset sanity checks for the supplied libkernel dump.

This script reads bytes only. It does not execute the dump, payloads, exploits or
hardware-dependent code. Offsets are file-relative from the beginning of the
combined blob.
"""
from pathlib import Path
import argparse, hashlib, json

EXPECTED_SHA256 = "ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c"
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

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="repository directory")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()
    root = Path(args.repo).resolve()
    combined_path = root / "libkernel_sys_13.52.bin"
    combined = combined_path.read_bytes()
    chunks = []
    concat = bytearray()
    for name, base in CHUNKS:
        p = root / name
        d = p.read_bytes()
        chunks.append({"file": name, "base": hex(base), "size": len(d), "sha256": sha256(d)})
        concat.extend(d)
    offsets = {}
    for name, off in OFFSETS.items():
        b = combined[off:off+8]
        offsets[name] = {"offset": hex(off), "bytes": b.hex(), "prologue_like": b[:3] in PROLOGUES}
    result = {
        "combined": {"file": combined_path.name, "size": len(combined), "sha256": sha256(combined), "expected_sha256": EXPECTED_SHA256, "sha256_match": sha256(combined) == EXPECTED_SHA256},
        "concatenation": {"size": len(concat), "sha256": sha256(concat), "matches_combined": bytes(concat) == combined},
        "chunks": chunks, "offsets": offsets,
        "static_only": True,
        "note": "A prologue match is only a structural sanity check; it does not prove a symbol identity or firmware version."
    }
    print(json.dumps(result, indent=2) if args.json else result)

if __name__ == "__main__":
    main()
