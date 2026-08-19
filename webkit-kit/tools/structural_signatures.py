#!/usr/bin/env python3
"""Generate conservative, offset-blind structural signatures.

This tool records hashes, basic ELF metadata, printable-token hashes and
fixed byte-window hashes. It intentionally does not disassemble, emit runtime
addresses, generate gadgets, or create ROP/JOP data.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

PRINTABLE = re.compile(rb"[ -~]{6,}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def elf_metadata(data: bytes) -> dict:
    if len(data) < 20 or data[:4] != b"\x7fELF":
        return {"format": "UNKNOWN_OR_RAW"}
    endian = data[5]
    machine = None
    if endian == 1:
        machine = struct.unpack_from("<H", data, 18)[0]
    elif endian == 2:
        machine = struct.unpack_from(">H", data, 18)[0]
    return {
        "format": "ELF",
        "class": {1: "ELF32", 2: "ELF64"}.get(data[4], "UNKNOWN"),
        "endianness": {1: "LE", 2: "BE"}.get(endian, "UNKNOWN"),
        "machine": machine,
    }


def signature_tokens(data: bytes, window: int = 64) -> list[str]:
    values: list[str] = []
    for match in PRINTABLE.finditer(data):
        values.append("str:" + hashlib.sha256(match.group().lower()).hexdigest()[:24])
        if len(values) >= 256:
            break
    for start in range(0, max(0, len(data) - window + 1), window):
        values.append("win:" + hashlib.sha256(data[start : start + window]).hexdigest()[:24])
        if len(values) >= 512:
            break
    return values


def analyze(path: Path) -> dict:
    data = path.read_bytes()
    return {
        "path": str(path),
        "size": len(data),
        "sha256": sha256(path),
        "format": elf_metadata(data),
        "signature": {"token_and_window_hashes": signature_tokens(data)},
        "evidence": "DIRECT_BYTES" if data else "EMPTY",
        "semantic_identity": "UNVERIFIED",
        "absolute_offsets": "DISABLED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    document = {
        "schema": "webkit-structural-signatures/v1",
        "policy": {
            "gadget_generation": "DISABLED",
            "absolute_offsets": "DISABLED",
            "semantic_promotion": "REQUIRES_BUILD_ID_AND_PROVENANCE",
        },
        "artifacts": [analyze(path) for path in args.artifacts if path.is_file()],
    }
    text = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
