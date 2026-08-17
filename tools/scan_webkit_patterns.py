#!/usr/bin/env python3
"""Static WebKit pattern and container scanner.

The scanner accepts raw, ELF64 or SELF-like images and a JSON pattern config.
It never executes an image. ELF parsing is deliberately minimal and reports
file offsets/segment metadata only; no runtime base or semantic symbol is
inferred from a byte match.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

PT_LOAD = 1
PT_SCE_RELRO = 0x61000010


def parse_hex(value: str) -> bytes:
    value = "".join(value.split())
    return bytes.fromhex(value) if value else b""


def find_masked(blob: bytes, pattern: bytes, mask: bytes) -> list[int]:
    if not pattern or len(pattern) != len(mask) or len(pattern) > len(blob):
        return []
    out: list[int] = []
    end = len(blob) - len(pattern) + 1
    for off in range(end):
        window = blob[off:off + len(pattern)]
        if all((b & m) == (p & m) for b, p, m in zip(window, pattern, mask)):
            out.append(off)
    return out


def parse_container(blob: bytes) -> dict:
    if blob[:4] == b"\x7fELF":
        if len(blob) < 64 or blob[4] != 2 or blob[5] != 1:
            return {"format": "ELF_UNSUPPORTED", "segments": []}
        e_phoff = struct.unpack_from("<Q", blob, 32)[0]
        e_shoff = struct.unpack_from("<Q", blob, 40)[0]
        e_phentsize = struct.unpack_from("<H", blob, 54)[0]
        e_phnum = struct.unpack_from("<H", blob, 56)[0]
        e_shentsize = struct.unpack_from("<H", blob, 58)[0]
        e_shnum = struct.unpack_from("<H", blob, 60)[0]
        e_shstrndx = struct.unpack_from("<H", blob, 62)[0]
        segments: list[dict] = []
        for index in range(e_phnum):
            off = e_phoff + index * e_phentsize
            if off + 56 > len(blob) or e_phentsize < 56:
                break
            p_type, p_flags = struct.unpack_from("<II", blob, off)
            p_offset, p_vaddr, _, p_filesz, p_memsz, p_align = struct.unpack_from("<QQQQQQ", blob, off + 8)
            if p_offset > len(blob):
                continue
            file_end = min(len(blob), p_offset + p_filesz)
            kind = "PT_SCE_RELRO" if p_type == PT_SCE_RELRO else ("PT_LOAD" if p_type == PT_LOAD else f"0x{p_type:x}")
            segment = {
                "index": index,
                "type": kind,
                "p_type": hex(p_type),
                "flags": hex(p_flags),
                "file_offset": hex(p_offset),
                "file_end": hex(file_end),
                "file_size": p_filesz,
                "vaddr": hex(p_vaddr),
                "mem_size": p_memsz,
                "align": hex(p_align),
            }
            if p_type == PT_SCE_RELRO:
                segment["role"] = "PT_SCE_RELRO"
            elif p_type == PT_LOAD and (p_flags & 0x5) == 0x5:
                segment["role"] = ".text_candidate"
            segments.append(segment)
        sections: dict[str, dict] = {}
        text_section = None
        if e_shoff and e_shentsize >= 64 and e_shnum and e_shstrndx < e_shnum:
            shstr_header = e_shoff + e_shstrndx * e_shentsize
            if shstr_header + 64 <= len(blob):
                _, _, _, _, shstr_off, shstr_size, _, _, _, _ = struct.unpack_from("<IIQQQQIIQQ", blob, shstr_header)
                if shstr_off + shstr_size <= len(blob):
                    names = blob[shstr_off:shstr_off + shstr_size]
                    for index in range(min(e_shnum, 4096)):
                        section_off = e_shoff + index * e_shentsize
                        if section_off + 64 > len(blob):
                            break
                        name_off, sh_type, sh_flags, sh_addr, file_off, file_size, _, _, _, _ = struct.unpack_from("<IIQQQQIIQQ", blob, section_off)
                        if name_off >= len(names):
                            name = ""
                        else:
                            end = names.find(b"\x00", name_off)
                            name = names[name_off:end if end >= 0 else len(names)].decode("utf-8", errors="replace")
                        sections[name] = {"index": index, "type": hex(sh_type), "flags": hex(sh_flags), "file_offset": hex(file_off), "file_size": file_size, "vaddr": hex(sh_addr)}
                    text_section = sections.get(".text")
        return {
            "format": "ELF64_LE",
            "class": 2,
            "endianness": "little",
            "program_header_offset": e_phoff,
            "program_header_count": e_phnum,
            "section_header_offset": e_shoff,
            "section_header_count": e_shnum,
            "sections": sections,
            "text_section": text_section,
            "segments": segments,
        }
    if blob[:4] == b"SELF":
        return {"format": "SELF", "segments": [], "note": "SELF container not decrypted or mapped; no offsets inferred."}
    return {"format": "RAW", "segments": [], "note": "No ELF/SELF header detected."}


def hit_segment(hit: int, length: int, segments: list[dict]) -> list[str]:
    end = hit + length
    roles: list[str] = []
    for segment in segments:
        start = int(segment["file_offset"], 16)
        stop = int(segment["file_end"], 16)
        if start <= hit and end <= stop:
            roles.append(segment.get("role", segment["type"]))
    return roles


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", type=Path, required=True)
    ap.add_argument("--config", type=Path, default=Path(__file__).with_name("webkit_1352_migration.json"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    image = args.image.read_bytes()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    container = parse_container(image)
    result = {
        "image": str(args.image),
        "size": len(image),
        "sha256": hashlib.sha256(image).hexdigest(),
        "target_firmware": cfg.get("target_firmware"),
        "container": container,
        "patterns": {},
        "warning": "No runtime base, loader, GOT/PLT or semantic function identity is inferred from a match.",
    }
    for name, entry in cfg.get("patterns", {}).items():
        pattern = parse_hex(entry.get("bytes", ""))
        mask_text = entry.get("mask", "")
        mask = parse_hex(mask_text) if mask_text else b"\xff" * len(pattern)
        hits = find_masked(image, pattern, mask) if pattern else []
        result["patterns"][name] = {
            "status": "DIRECT_BYTES" if hits else entry.get("status", "REQUIRES_REANALYSIS"),
            "hits": [hex(x) for x in hits],
            "segment_roles": [hit_segment(x, len(pattern), container.get("segments", [])) for x in hits],
            "pattern_length": len(pattern),
            "semantic_identity": "REQUIRES_REANALYSIS" if hits else "ABSENT",
            "note": "Byte match only; confirm XREFs, module headers and same-build provenance before assigning a symbol.",
        }
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else text_result(result))
    return 0


def text_result(result: dict) -> str:
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
