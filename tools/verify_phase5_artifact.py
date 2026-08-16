#!/usr/bin/env python3
"""Verify the recorded Phase 5 HEN 13.52 artifact evidence.

This script is static-only. It never executes the supplied artifact; it reads
bytes, verifies hashes, reconstructs the 89 uint32_t fields from offsets/1352.c,
and checks the recorded selector displacement when the published HEN asset is
available locally.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import struct
import sys
from pathlib import Path

EXPECTED_ASSET_SIZE = 499_776
EXPECTED_ASSET_SHA256 = "568d57e7c6bfff1b96fc20a4e00b9ca744aa58b135a56eeb5c66c1175acfac3e"
EXPECTED_TABLE_SHA256 = "d032dbd790eaa29cd8ec7571ee04636f82bbbb50a9b2ce0d24dfa003ace0030f"
EXPECTED_TABLE_OFFSET = 0x105E0
EXPECTED_TABLE_END = 0x10743
EXPECTED_SELECTOR_OFFSET = 0xC549
EXPECTED_SELECTOR_VERSION = 0x548
EXPECTED_SELECTOR_TABLE = 0x105E0


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_fields(source: Path) -> list[tuple[str, int]]:
    text = source.read_text(encoding="utf-8")
    pairs = re.findall(r"\.([A-Za-z0-9_]+)\s*=\s*(0x[0-9A-Fa-f]+)", text)
    if len(pairs) != 89:
        raise ValueError(f"expected 89 offset fields, found {len(pairs)} in {source}")
    return [(name, int(value, 16)) for name, value in pairs]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset", type=Path, help="published HEN 181 asset; no execution is performed")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("kpayload/source/offsets/1352.c"),
        help="offset source containing offsets_1352",
    )
    args = parser.parse_args()

    fields = load_fields(args.source)
    table = b"".join(struct.pack("<I", value & 0xFFFFFFFF) for _, value in fields)
    assert len(table) == 356
    assert sha256(table) == EXPECTED_TABLE_SHA256
    print(f"PASS fields={len(fields)} serialized_size={len(table)} table_sha256={sha256(table)}")
    print(f"PASS expected_table_range={EXPECTED_TABLE_OFFSET:#x}-{EXPECTED_TABLE_END:#x}")

    if args.asset is None:
        print("SKIP asset verification: provide --asset with the published HEN 181 file")
        return 0

    data = args.asset.read_bytes()
    actual_hash = sha256(data)
    if len(data) != EXPECTED_ASSET_SIZE or actual_hash != EXPECTED_ASSET_SHA256:
        print(
            f"FAIL asset size={len(data)} sha256={actual_hash}; "
            f"expected size={EXPECTED_ASSET_SIZE} sha256={EXPECTED_ASSET_SHA256}",
            file=sys.stderr,
        )
        return 1
    print(f"PASS asset_size={len(data)} asset_sha256={actual_hash}")

    if data[EXPECTED_TABLE_OFFSET : EXPECTED_TABLE_OFFSET + len(table)] != table:
        print("FAIL serialized offsets_1352 table does not match at 0x105e0", file=sys.stderr)
        return 1
    print(f"PASS exact_table_match offset={EXPECTED_TABLE_OFFSET:#x} end={EXPECTED_TABLE_END:#x}")

    # At 0xc552 the instruction is lea rax,[rip+0x4087]; the next instruction
    # begins at 0xc559, so its RIP-relative target is 0xc559 + 0x4087 = 0x105e0.
    selector = data[0xC549 : 0xC559]
    if b"\x66\x81\xff\x48\x05" not in selector:
        print("FAIL 1352 selector compare was not found at the recorded location", file=sys.stderr)
        return 1
    displacement = struct.unpack_from("<i", data, 0xC555)[0]
    target = 0xC559 + displacement
    if target != EXPECTED_SELECTOR_TABLE:
        print(f"FAIL selector target={target:#x}; expected {EXPECTED_SELECTOR_TABLE:#x}", file=sys.stderr)
        return 1
    print(f"PASS selector version={EXPECTED_SELECTOR_VERSION:#x} rip_target={target:#x}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
