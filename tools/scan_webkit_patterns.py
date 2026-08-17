#!/usr/bin/env python3
"""Static WebKit pattern scanner.

The scanner accepts a raw/ELF/SELF byte image and a JSON pattern config. It
never executes the image. Patterns use hex bytes plus an optional mask, so
firmware-dependent values can remain unset until a real 13.52 image exists.

This version adds conservative ELF/SELF parsing to report .text section,
program headers and a heuristic RELRO presence (PT_GNU_RELRO). It does not
infer runtime bases or invent offsets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import List, Dict, Any


def parse_hex(value: str) -> bytes:
    value = "".join(value.split())
    return bytes.fromhex(value) if value else b""


def find_masked(blob: bytes, pattern: bytes, mask: bytes) -> list[int]:
    if not pattern or len(pattern) != len(mask) or len(pattern) > len(blob):
        return []
    out: List[int] = []
    end = len(blob) - len(pattern) + 1
    for off in range(end):
        window = blob[off:off + len(pattern)]
        if all((b & m) == (p & m) for b, p, m in zip(window, pattern, mask)):
            out.append(off)
    return out


PT_GNU_RELRO = 0x6474e550  # common GNU RELRO program header type; heuristic only


def parse_elf_headers(blob: bytes) -> Dict[str, Any]:
    """Conservative ELF64 header parser. Returns ELF metadata or empty dict.

    This parser assumes little-endian ELF64 (platform-target). It performs
    bounds checks and will return minimal info if parsing fails. It does not
    attempt to interpret SELF-specific headers beyond standard ELF.
    """
    out: Dict[str, Any] = {"detected": False}
    if len(blob) < 16 or blob[:4] != b"\x7fELF":
        return out
    # e_ident[4] = EI_CLASS: 1=32bit,2=64bit; e_ident[5]=EI_DATA:1=little,2=big
    ei_class = blob[4]
    ei_data = blob[5]
    if ei_class != 2 or ei_data != 1:
        # Not ELF64 little-endian; report presence but don't parse further
        out.update({"detected": True, "class": f"ELF{ei_class}", "bitness": 32 if ei_class == 1 else None})
        return out
    # Parse ELF64 header (starting at offset 16)
    try:
        (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff,
         e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from("<HHIQQIHHHHHH", blob, 16)
    except Exception:
        out.update({"detected": True})
        return out
    out.update({
        "detected": True,
        "class": "ELF64",
        "bitness": 64,
        "e_phoff": e_phoff,
        "e_phentsize": e_phentsize,
        "e_phnum": e_phnum,
        "e_shoff": e_shoff,
        "e_shentsize": e_shentsize,
        "e_shnum": e_shnum,
        "e_shstrndx": e_shstrndx,
        "program_headers": [],
        "sections": {},
    })
    # Parse program headers (conservative bounds checks)
    phdrs: List[Dict[str, Any]] = []
    try:
        for i in range(min(e_phnum, 1024)):
            phoff = e_phoff + i * e_phentsize
            if phoff + e_phentsize > len(blob):
                break
            # ELF64 Program Header: p_type(4), p_flags(4), p_offset(8), p_vaddr(8), p_paddr(8), p_filesz(8), p_memsz(8), p_align(8)
            p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from("<IIQQQQQQ", blob, phoff)
            phdrs.append({
                "p_type": hex(p_type),
                "p_flags": hex(p_flags),
                "p_offset": hex(p_offset),
                "p_vaddr": hex(p_vaddr),
                "p_filesz": p_filesz,
                "p_memsz": p_memsz,
                "p_align": p_align,
            })
    except Exception:
        # best-effort: keep what we have
        pass
    out["program_headers"] = phdrs
    # Heuristic RELRO detection: check for PT_GNU_RELRO among p_type values
    relro_present = any(int(ph.get("p_type", "0"), 16) == PT_GNU_RELRO for ph in phdrs)
    out["relro_present_heuristic"] = relro_present
    # Parse section headers to find .text (requires shstrtab)
    try:
        if e_shoff and e_shnum and e_shentsize and e_shstrndx < e_shnum:
            # get shstrtab header to read string table
            shstr_off = e_shoff + e_shstrndx * e_shentsize
            if shstr_off + e_shentsize <= len(blob):
                sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link, sh_info, sh_addralign, sh_entsize = struct.unpack_from("<IIQQQQIIQQ", blob, shstr_off)
                if sh_offset + sh_size <= len(blob):
                    shstr = blob[sh_offset:sh_offset + sh_size]
                    sections = {}
                    for i in range(min(e_shnum, 4096)):
                        shoff = e_shoff + i * e_shentsize
                        if shoff + e_shentsize > len(blob):
                            break
                        sh_name_off, sh_type_i, sh_flags_i, sh_addr_i, sh_offset_i, sh_size_i, sh_link_i, sh_info_i, sh_addralign_i, sh_entsize_i = struct.unpack_from("<IIQQQQIIQQ", blob, shoff)
                        # read name from shstr
                        name = ""
                        if sh_name_off < len(shstr):
                            end = shstr.find(b"\x00", sh_name_off)
                            if end != -1:
                                name = shstr[sh_name_off:end].decode("utf-8", errors="replace")
                        sections[name] = {"offset": sh_offset_i, "size": sh_size_i, "type": sh_type_i, "flags": hex(sh_flags_i)}
                    out["sections"] = sections
                    if ".text" in sections:
                        out["text_section"] = sections[".text"]
    except Exception:
        pass
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", type=Path, required=True)
    ap.add_argument("--config", type=Path, default=Path(__file__).with_name("webkit_1352_migration.json"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    image = args.image.read_bytes()
    cfg = json.loads(args.config.read_text())
    result: Dict[str, Any] = {
        "image": str(args.image),
        "size": len(image),
        "sha256": hashlib.sha256(image).hexdigest(),
        "target_firmware": cfg.get("target_firmware"),
        "patterns": {},
        "warning": "No runtime base, loader, GOT/PLT or semantic function identity is inferred from a match.",
    }

    # ELF/SELF conservative parsing
    elf_meta = parse_elf_headers(image)
    result["elf"] = elf_meta

    for name, entry in cfg.get("patterns", {}).items():
        pattern = parse_hex(entry.get("bytes", ""))
        mask_text = entry.get("mask", "")
        mask = parse_hex(mask_text) if mask_text else b"\xff" * len(pattern)
        hits = find_masked(image, pattern, mask) if pattern else []
        result["patterns"][name] = {
            "status": "DIRECT_BYTES" if hits else entry.get("status", "REQUIRES_REANALYSIS"),
            "hits": [hex(x) for x in hits],
            "pattern_length": len(pattern),
            "semantic_identity": "REQUIRES_REANALYSIS" if hits else "ABSENT",
            "note": "Byte match only; confirm XREFs, module headers and same-build provenance before assigning a symbol.",
        }
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else text_result(result))
    return 0


def text_result(result: Dict[str, Any]) -> str:
    lines = [f"image={result['image']}", f"size={result['size']}", f"sha256={result['sha256']}"]
    elf = result.get("elf", {})
    lines.append(f"elf_detected={elf.get('detected', False)}")
    if elf.get("detected"):
        lines.append(f"elf_class={elf.get('class')}")
        if "text_section" in elf:
            ts = elf["text_section"]
            lines.append(f"text_offset={hex(ts['offset'])} text_size={ts['size']}")
        lines.append(f"relro_heuristic={elf.get('relro_present_heuristic', False)}")
    for name, item in result["patterns"].items():
        lines.append(f"{name}: {item['status']} hits={','.join(item['hits']) or '-'}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
