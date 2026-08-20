#!/usr/bin/env python3
"""Conservative structural evidence extractor for ELF/SELF-like artifacts.

This tool never executes an artifact, disassembles code, emits gadgets, or
promotes a structural match to firmware identity. It records reproducible
container metadata useful when a legally obtained PS4 module becomes available.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any

PRINTABLE = re.compile(rb"[ -~]{6,}")
PT_LOAD = 1
PT_DYNAMIC = 2
PT_NOTE = 4
PT_SCE_RELRO = 0x61000010
DT_NULL = 0
DT_NEEDED = 1
DT_SONAME = 14
DT_STRTAB = 5
DT_STRSZ = 10
DT_SYMTAB = 6
DT_SYMENT = 11
DT_HASH = 4
DT_GNU_HASH = 0x6FFFFEF5


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cstring(data: bytes, offset: int) -> str:
    if offset < 0 or offset >= len(data):
        return ""
    end = data.find(b"\0", offset)
    if end < 0:
        end = len(data)
    return data[offset:end].decode("utf-8", "replace")


def file_offset_for_vaddr(phdrs: list[dict[str, int]], address: int) -> int | None:
    for ph in phdrs:
        start = ph["vaddr"]
        end = start + ph["memsz"]
        if ph["type"] in (PT_LOAD, PT_DYNAMIC) and start <= address < end:
            delta = address - start
            if delta < ph["filesz"]:
                return ph["offset"] + delta
    return None


def parse_elf(data: bytes) -> dict[str, Any]:
    if len(data) < 64 or data[:4] != b"\x7fELF":
        return {"format": "UNKNOWN_OR_RAW"}
    ei_class, ei_data = data[4], data[5]
    if ei_class != 2 or ei_data not in (1, 2):
        return {"format": "ELF", "class": {1: "ELF32", 2: "ELF64"}.get(ei_class, "UNKNOWN"), "endianness": {1: "LE", 2: "BE"}.get(ei_data, "UNKNOWN"), "parse_status": "LIMITED"}
    endian = "<" if ei_data == 1 else ">"
    unpack = lambda fmt, off: struct.unpack_from(endian + fmt, data, off)
    e_type, e_machine = unpack("HH", 16)
    e_entry, e_phoff, e_shoff = unpack("QQQ", 24)
    e_phentsize, e_phnum = unpack("HH", 54)
    phdrs: list[dict[str, int]] = []
    for index in range(e_phnum):
        off = e_phoff + index * e_phentsize
        if off + 56 > len(data):
            break
        p_type, p_flags, p_offset, p_vaddr, _p_paddr, p_filesz, p_memsz, p_align = unpack("IIQQQQQQ", off)
        phdrs.append({"index": index, "type": p_type, "flags": p_flags, "offset": p_offset, "vaddr": p_vaddr, "filesz": p_filesz, "memsz": p_memsz, "align": p_align})
    loads = [p for p in phdrs if p["type"] == PT_LOAD]
    notes: list[dict[str, Any]] = []
    build_ids: list[str] = []
    for ph in phdrs:
        if ph["type"] != PT_NOTE or ph["offset"] + ph["filesz"] > len(data):
            continue
        pos, end = ph["offset"], ph["offset"] + ph["filesz"]
        while pos + 12 <= end:
            namesz, descsz, n_type = unpack("III", pos)
            pos += 12
            name_end = pos + ((namesz + 3) & ~3)
            desc_start = name_end
            desc_end = desc_start + ((descsz + 3) & ~3)
            if desc_end > end:
                break
            name = data[pos:pos + namesz].rstrip(b"\0").decode("ascii", "replace")
            desc = data[desc_start:desc_start + descsz]
            item = {"name": name, "type": n_type, "desc_size": descsz}
            if name == "GNU" and n_type == 3:
                item["build_id"] = desc.hex()
                build_ids.append(desc.hex())
            notes.append(item)
            pos = desc_end
    dynamic = {"needed": [], "soname": None, "status": "NOT_FOUND"}
    dyn = next((p for p in phdrs if p["type"] == PT_DYNAMIC), None)
    if dyn and dyn["offset"] + dyn["filesz"] <= len(data):
        entries: list[tuple[int, int]] = []
        for pos in range(dyn["offset"], dyn["offset"] + dyn["filesz"], 16):
            tag, value = unpack("QQ", pos)
            entries.append((tag, value))
            if tag == DT_NULL:
                break
        strtab = next((v for t, v in entries if t == DT_STRTAB), None)
        if strtab is not None:
            str_off = file_offset_for_vaddr(phdrs, strtab)
            if str_off is not None:
                dynamic["status"] = "PARSED"
                for tag, value in entries:
                    if tag == DT_NEEDED:
                        dynamic["needed"].append(cstring(data, str_off + value))
                    elif tag == DT_SONAME:
                        dynamic["soname"] = cstring(data, str_off + value)
    return {
        "format": "ELF64",
        "class": "ELF64",
        "endianness": "LE" if ei_data == 1 else "BE",
        "type": e_type,
        "machine": e_machine,
        "entry": e_entry,
        "program_header_count": e_phnum,
        "program_headers": phdrs,
        "pt_load": loads,
        "pt_sce_relro": [p for p in phdrs if p["type"] == PT_SCE_RELRO],
        "notes": notes,
        "build_ids": build_ids,
        "dynamic": dynamic,
        "parse_status": "PARSED",
    }


def signature_tokens(data: bytes, window: int = 64) -> list[str]:
    values: list[str] = []
    for match in PRINTABLE.finditer(data):
        values.append("str:" + hashlib.sha256(match.group().lower()).hexdigest()[:24])
        if len(values) >= 512:
            break
    for start in range(0, max(0, len(data) - window + 1), window):
        values.append("win:" + hashlib.sha256(data[start : start + window]).hexdigest()[:24])
        if len(values) >= 2048:
            break
    return values


def analyze(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    elf = parse_elf(data)
    sce_magic = []
    for marker in (b"SCE\0", b"SELF", b"ORBI"):
        positions = [m.start() for m in re.finditer(re.escape(marker), data[:4096])]
        if positions:
            sce_magic.append({"marker": marker.decode("ascii", "replace"), "offsets": positions[:16]})
    return {
        "path": str(path),
        "size": len(data),
        "sha256": sha256(path),
        "format": elf,
        "sce_markers_first_4k": sce_magic,
        "strings": {"count_capped": min(len(PRINTABLE.findall(data)), 512), "sha256_tokens": signature_tokens(data)},
        "evidence": "DIRECT_BYTES" if data else "EMPTY",
        "semantic_identity": "UNVERIFIED",
        "absolute_offsets": "DISABLED",
        "execution": "PROHIBITED_BY_TOOL_POLICY",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract conservative ELF/SELF structural evidence without executing artifacts.")
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    document = {
        "schema": "webkit-structural-signatures/v2",
        "policy": {"execution": "DISABLED", "gadget_generation": "DISABLED", "absolute_offsets": "DISABLED", "semantic_promotion": "REQUIRES_BUILD_ID_AND_PROVENANCE"},
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


__all__ = ["analyze", "parse_elf", "signature_tokens"]
