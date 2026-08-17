#!/usr/bin/env python3
"""Static WebKit pattern and container scanner.

The scanner accepts raw, ELF64 little-endian or SELF-like images and a JSON
pattern config. It never executes, decrypts or relocates an image. Reported
addresses are file/declared virtual metadata only; a byte match never receives
semantic function, vtable, import or gadget identity automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

ELF_MAGIC = b"\x7fELF"
SELF_MAGIC = b"SELF"
PT_LOAD = 1
PT_NOTE = 4
PT_SCE_RELRO = 0x61000010
PT_GNU_RELRO = 0x6474E550
PT_SCE_NOTE = 0x61000001
MAX_PROGRAM_HEADERS = 4096
MAX_SECTION_HEADERS = 4096
ELF64_HEADER_SIZE = 64
ELF64_PROGRAM_HEADER_SIZE = 56
ELF64_SECTION_HEADER_SIZE = 64


def parse_hex(value: str) -> bytes:
    value = "".join(value.split())
    if not value:
        return b""
    if len(value) % 2:
        raise ValueError("hex pattern has odd length")
    return bytes.fromhex(value)


def find_masked(blob: bytes, pattern: bytes, mask: bytes) -> list[int]:
    if not pattern or len(pattern) != len(mask) or len(pattern) > len(blob):
        return []
    out: list[int] = []
    end = len(blob) - len(pattern) + 1
    for off in range(end):
        window = blob[off : off + len(pattern)]
        if all((b & m) == (p & m) for b, p, m in zip(window, pattern, mask)):
            out.append(off)
    return out


def valid_range(offset: int, size: int, length: int) -> bool:
    return 0 <= offset <= length and 0 <= size <= length - offset


def align4(value: int) -> int:
    return (value + 3) & ~3


def parse_note_build_id(blob: bytes, offset: int, size: int) -> str | None:
    if not valid_range(offset, size, len(blob)):
        return None
    end = offset + size
    cursor = offset
    while cursor + 12 <= end:
        namesz, descsz, note_type = struct.unpack_from("<III", blob, cursor)
        cursor += 12
        name_end = cursor + namesz
        if name_end > end:
            return None
        name = blob[cursor:name_end].rstrip(b"\x00")
        cursor = offset + align4(name_end - offset)
        desc_end = cursor + descsz
        if desc_end > end:
            return None
        desc = blob[cursor:desc_end]
        cursor = offset + align4(desc_end - offset)
        if note_type == 3 and name == b"GNU":
            return desc.hex()
    return None


def parse_container(blob: bytes) -> dict[str, Any]:
    if blob[:4] == ELF_MAGIC:
        if len(blob) < ELF64_HEADER_SIZE:
            return {"format": "ELF_TRUNCATED", "detected": False, "segments": [], "sections": [], "error": "short ELF64 header"}
        if blob[4] != 2 or blob[5] != 1:
            return {"format": "ELF_UNSUPPORTED", "detected": False, "segments": [], "sections": [], "error": "requires ELF64 little-endian"}

        e_phoff = struct.unpack_from("<Q", blob, 32)[0]
        e_shoff = struct.unpack_from("<Q", blob, 40)[0]
        e_phentsize = struct.unpack_from("<H", blob, 54)[0]
        e_phnum = struct.unpack_from("<H", blob, 56)[0]
        e_shentsize = struct.unpack_from("<H", blob, 58)[0]
        e_shnum = struct.unpack_from("<H", blob, 60)[0]
        e_shstrndx = struct.unpack_from("<H", blob, 62)[0]
        errors: list[str] = []
        if e_phnum > MAX_PROGRAM_HEADERS:
            errors.append("program header count exceeds safety limit")
        if e_phnum and e_phentsize < ELF64_PROGRAM_HEADER_SIZE:
            errors.append("program header entry is shorter than ELF64 minimum")
        if e_phnum and e_phentsize >= ELF64_PROGRAM_HEADER_SIZE and not valid_range(e_phoff, e_phentsize * e_phnum, len(blob)):
            errors.append("program header table outside file bounds")
        if e_shnum > MAX_SECTION_HEADERS:
            errors.append("section header count exceeds safety limit")
        if e_shnum and e_shentsize < ELF64_SECTION_HEADER_SIZE:
            errors.append("section header entry is shorter than ELF64 minimum")
        if e_shnum and e_shentsize >= ELF64_SECTION_HEADER_SIZE and not valid_range(e_shoff, e_shentsize * e_shnum, len(blob)):
            errors.append("section header table outside file bounds")

        segments: list[dict[str, Any]] = []
        if not errors or not any("program header" in error for error in errors):
            for index in range(min(e_phnum, MAX_PROGRAM_HEADERS)):
                off = e_phoff + index * e_phentsize
                if not valid_range(off, ELF64_PROGRAM_HEADER_SIZE, len(blob)):
                    errors.append(f"program header {index} outside file bounds")
                    break
                p_type, p_flags = struct.unpack_from("<II", blob, off)
                p_offset, p_vaddr, _, p_filesz, p_memsz, p_align = struct.unpack_from("<QQQQQQ", blob, off + 8)
                valid = valid_range(p_offset, p_filesz, len(blob))
                if not valid:
                    errors.append(f"segment {index} file range outside bounds")
                kind = "PT_SCE_RELRO" if p_type == PT_SCE_RELRO else ("PT_GNU_RELRO" if p_type == PT_GNU_RELRO else ("PT_LOAD" if p_type == PT_LOAD else f"0x{p_type:x}"))
                file_end = p_offset + p_filesz if valid else None
                segment: dict[str, Any] = {
                    "index": index,
                    "type": kind,
                    "p_type": hex(p_type),
                    "flags": hex(p_flags),
                    "file_offset": hex(p_offset),
                    "file_end": hex(file_end) if file_end is not None else None,
                    "file_size": p_filesz,
                    "vaddr": hex(p_vaddr),
                    "mem_size": p_memsz,
                    "align": hex(p_align),
                    "valid_file_range": valid,
                }
                if p_type in (PT_SCE_RELRO, PT_GNU_RELRO):
                    segment["role"] = "PT_SCE_RELRO"
                elif p_type == PT_LOAD and (p_flags & 0x1):
                    segment["role"] = ".text_candidate" if (p_flags & 0x4) else "executable_load"
                elif p_type == PT_NOTE:
                    segment["role"] = "PT_NOTE"
                elif p_type == PT_SCE_NOTE:
                    segment["role"] = "PT_SCE_NOTE"
                segments.append(segment)

        sections: dict[str, dict[str, Any]] = {}
        text_section: dict[str, Any] | None = None
        build_id: str | None = None
        if not any("section header" in error for error in errors) and e_shoff and e_shentsize >= ELF64_SECTION_HEADER_SIZE and e_shnum and e_shstrndx < e_shnum:
            shstr_header = e_shoff + e_shstrndx * e_shentsize
            if valid_range(shstr_header, ELF64_SECTION_HEADER_SIZE, len(blob)):
                _, _, _, _, shstr_off, shstr_size, _, _, _, _ = struct.unpack_from("<IIQQQQIIQQ", blob, shstr_header)
                if valid_range(shstr_off, shstr_size, len(blob)):
                    names = blob[shstr_off : shstr_off + shstr_size]
                    for index in range(min(e_shnum, MAX_SECTION_HEADERS)):
                        section_off = e_shoff + index * e_shentsize
                        if not valid_range(section_off, ELF64_SECTION_HEADER_SIZE, len(blob)):
                            errors.append(f"section header {index} outside file bounds")
                            break
                        name_off, sh_type, sh_flags, sh_addr, file_off, file_size, _, _, _, _ = struct.unpack_from("<IIQQQQIIQQ", blob, section_off)
                        if name_off >= len(names):
                            name = ""
                        else:
                            end = names.find(b"\x00", name_off)
                            name = names[name_off : end if end >= 0 else len(names)].decode("utf-8", errors="replace")
                        valid = valid_range(file_off, file_size, len(blob))
                        sections[name] = {
                            "index": index,
                            "type": hex(sh_type),
                            "flags": hex(sh_flags),
                            "file_offset": hex(file_off),
                            "file_size": file_size,
                            "vaddr": hex(sh_addr),
                            "valid_file_range": valid,
                        }
                    text_section = sections.get(".text")
                    if text_section and not text_section.get("valid_file_range", False):
                        errors.append(".text section outside file bounds")
                    for name, section in sections.items():
                        if name == ".note.gnu.build-id" and section.get("valid_file_range"):
                            build_id = parse_note_build_id(blob, int(section["file_offset"], 16), int(section["file_size"]))

        for segment in segments:
            if build_id is None and segment.get("role") in ("PT_NOTE", "PT_SCE_NOTE") and segment.get("valid_file_range"):
                build_id = parse_note_build_id(blob, int(segment["file_offset"], 16), int(segment["file_size"]))

        return {
            "format": "ELF64_LE" if not errors else "ELF64_LE_WITH_ERRORS",
            "detected": True,
            "class": 2,
            "endianness": "little",
            "program_header_offset": e_phoff,
            "program_header_count": e_phnum,
            "section_header_offset": e_shoff,
            "section_header_count": e_shnum,
            "sections": sections,
            "text_section": text_section,
            "build_id": build_id,
            "relro_present_heuristic": any(segment.get("role") == "PT_SCE_RELRO" and segment.get("valid_file_range") for segment in segments),
            "segments": segments,
            "errors": errors,
        }
    if blob[:4] == SELF_MAGIC:
        return {"format": "SELF", "detected": True, "segments": [], "sections": [], "build_id": None, "note": "SELF container recognized only by magic; no decryption, mapping or offsets inferred."}
    return {"format": "RAW", "detected": False, "segments": [], "sections": [], "build_id": None, "note": "No ELF/SELF header detected."}


def hit_segment(hit: int, length: int, segments: list[dict[str, Any]]) -> list[str]:
    end = hit + length
    roles: list[str] = []
    for segment in segments:
        if not segment.get("valid_file_range") or segment.get("file_end") is None:
            continue
        start = int(segment["file_offset"], 16)
        stop = int(segment["file_end"], 16)
        if start <= hit and end <= stop:
            roles.append(segment.get("role", segment["type"]))
    return roles


def pattern_result(image: bytes, entry: dict[str, Any], segments: list[dict[str, Any]]) -> dict[str, Any]:
    pattern_text = entry.get("bytes", "")
    mask_text = entry.get("mask", "")
    errors: list[str] = []
    try:
        pattern = parse_hex(pattern_text)
    except ValueError as exc:
        pattern = b""
        errors.append(str(exc))
    try:
        mask = parse_hex(mask_text) if mask_text else b"\xff" * len(pattern)
    except ValueError as exc:
        mask = b""
        errors.append(str(exc))
    if pattern and mask and len(pattern) != len(mask):
        errors.append("mask length does not match pattern length")
    if not pattern_text:
        errors.append("empty pattern")
    hits = find_masked(image, pattern, mask) if not errors else []
    status = "DIRECT_BYTES" if hits else entry.get("status", "REQUIRES_REANALYSIS")
    if errors and not hits:
        status = "UNVERIFIED" if "empty pattern" not in errors else entry.get("status", "REQUIRES_REANALYSIS")
    return {
        "status": status,
        "hits": [hex(x) for x in hits],
        "segment_roles": [hit_segment(x, len(pattern), segments) for x in hits],
        "pattern_length": len(pattern),
        "mask_length": len(mask),
        "validation_errors": errors,
        "semantic_identity": "REQUIRES_REANALYSIS" if hits else "ABSENT",
        "note": "Byte match only; confirm XREFs, module headers and same-build provenance before assigning a symbol.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", type=Path, required=True)
    ap.add_argument("--config", type=Path, default=Path(__file__).with_name("webkit_1352_migration.json"))
    ap.add_argument("--target-firmware", help="Override the config firmware label for historical artifacts; does not prove provenance")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    image = args.image.read_bytes()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    container = parse_container(image)
    result = {
        "image": str(args.image),
        "size": len(image),
        "sha256": hashlib.sha256(image).hexdigest(),
        "target_firmware": args.target_firmware or cfg.get("target_firmware"),
        "container": container,
        "elf": container,
        "patterns": {},
        "warning": "No runtime base, loader, GOT/PLT or semantic function identity is inferred from a match.",
    }
    for name, entry in cfg.get("patterns", {}).items():
        result["patterns"][name] = pattern_result(image, entry, container.get("segments", []))
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else text_result(result))
    return 0


def text_result(result: dict[str, Any]) -> str:
    lines = [
        f"image={result['image']}",
        f"format={result['container']['format']}",
        f"size={result['size']}",
        f"sha256={result['sha256']}",
    ]
    for name, item in result["patterns"].items():
        lines.append(f"{name}: {item['status']} hits={','.join(item['hits']) or '-'}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
