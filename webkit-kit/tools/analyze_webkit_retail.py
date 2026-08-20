#!/usr/bin/env python3
"""Static, non-executing correlation pipeline for an authorized WebKit artifact.

The tool accepts a local file, extracts conservative ELF/SELF metadata, dynamic
symbols, relevant strings and byte-level xref candidates, then correlates the
result with three_family_signatures.json. It never decrypts, executes,
disassembles, emits gadgets, or promotes a result to CONFIRMED_13.52.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
KIT_DIR = TOOLS_DIR.parent
DEFAULT_SIGNATURES = KIT_DIR / "three_family_signatures.json"
PRINTABLE = re.compile(rb"[ -~]{6,}")
ELF_MAGIC = b"\x7fELF"
PT_LOAD = 1
PT_DYNAMIC = 2
PT_NOTE = 4
SHT_DYNSYM = 11
SHT_STRTAB = 3
DT_NULL = 0
DT_NEEDED = 1
DT_SONAME = 14
DT_STRTAB = 5
DT_STRSZ = 10
DT_SYMTAB = 6
DT_SYMENT = 11
DT_HASH = 4
DT_GNU_HASH = 0x6FFFFEF5


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cstring(data: bytes, offset: int) -> str:
    if offset < 0 or offset >= len(data):
        return ""
    end = data.find(b"\0", offset)
    return data[offset:end if end >= 0 else len(data)].decode("utf-8", "replace")


def parse_elf_header(data: bytes, base: int = 0) -> dict[str, Any]:
    if len(data) - base < 64 or data[base:base + 4] != ELF_MAGIC:
        return {"format": "UNKNOWN_OR_RAW", "offset": base}
    ei_class, ei_data = data[base + 4], data[base + 5]
    if ei_class not in (1, 2) or ei_data not in (1, 2):
        return {"format": "ELF", "class": ei_class, "endianness": ei_data, "parse_status": "LIMITED", "offset": base}
    endian = "<" if ei_data == 1 else ">"
    u16 = lambda off: struct.unpack_from(endian + "H", data, base + off)[0]
    u32 = lambda off: struct.unpack_from(endian + "I", data, base + off)[0]
    if ei_class == 2:
        e_type, machine = u16(16), u16(18)
        entry, phoff, shoff = struct.unpack_from(endian + "QQQ", data, base + 24)
        phentsize, phnum, shentsize, shnum, shstrndx = u16(54), u16(56), u16(58), u16(60), u16(62)
    else:
        e_type, machine = u16(16), u16(18)
        entry, phoff, shoff = struct.unpack_from(endian + "III", data, base + 24)
        phentsize, phnum, shentsize, shnum, shstrndx = u16(42), u16(44), u16(46), u16(48), u16(50)
    return {"format": "ELF64" if ei_class == 2 else "ELF32", "class": ei_class, "endianness": "LE" if ei_data == 1 else "BE", "endian": endian, "type": e_type, "machine": machine, "entry": entry, "phoff": phoff, "phentsize": phentsize, "phnum": phnum, "shoff": shoff, "shentsize": shentsize, "shnum": shnum, "shstrndx": shstrndx, "offset": base}


def parse_program_headers(data: bytes, hdr: dict[str, Any]) -> list[dict[str, int]]:
    if hdr.get("format") not in ("ELF64", "ELF32"):
        return []
    base, endian, cls = hdr["offset"], hdr["endian"], hdr["class"]
    out: list[dict[str, int]] = []
    for index in range(hdr["phnum"]):
        off = base + hdr["phoff"] + index * hdr["phentsize"]
        try:
            if cls == 2:
                p_type, flags, p_offset, vaddr, _paddr, filesz, memsz, align = struct.unpack_from(endian + "IIQQQQQQ", data, off)
            else:
                p_type, p_offset, vaddr, _paddr, filesz, memsz, flags, align = struct.unpack_from(endian + "IIIIIIII", data, off)
        except struct.error:
            break
        out.append({"index": index, "type": p_type, "flags": flags, "offset": p_offset + base, "vaddr": vaddr, "filesz": filesz, "memsz": memsz, "align": align})
    return out


def vaddr_to_file(phdrs: list[dict[str, int]], address: int) -> int | None:
    for ph in phdrs:
        if ph["type"] in (PT_LOAD, PT_DYNAMIC) and ph["vaddr"] <= address < ph["vaddr"] + ph["memsz"]:
            delta = address - ph["vaddr"]
            if delta < ph["filesz"]:
                return ph["offset"] + delta
    return None


def parse_notes(data: bytes, phdrs: list[dict[str, int]], endian: str) -> tuple[list[dict[str, Any]], list[str]]:
    notes, build_ids = [], []
    for ph in phdrs:
        if ph["type"] != PT_NOTE or ph["offset"] + ph["filesz"] > len(data):
            continue
        pos, end = ph["offset"], ph["offset"] + ph["filesz"]
        while pos + 12 <= end:
            try:
                namesz, descsz, n_type = struct.unpack_from(endian + "III", data, pos)
            except struct.error:
                break
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
    return notes, build_ids


def parse_dynamic(data: bytes, hdr: dict[str, Any], phdrs: list[dict[str, int]]) -> tuple[dict[str, Any], dict[int, int]]:
    dyn = next((p for p in phdrs if p["type"] == PT_DYNAMIC), None)
    if not dyn:
        return {"status": "NOT_FOUND", "needed": [], "soname": None}, {}
    endian, cls = hdr["endian"], hdr["class"]
    step, fmt = (16, "QQ") if cls == 2 else (8, "II")
    entries: list[tuple[int, int]] = []
    for off in range(dyn["offset"], min(len(data), dyn["offset"] + dyn["filesz"]), step):
        try:
            tag, value = struct.unpack_from(endian + fmt, data, off)
        except struct.error:
            break
        entries.append((tag, value))
        if tag == DT_NULL:
            break
    values = {tag: value for tag, value in entries if tag not in (DT_NEEDED,)}
    str_off = vaddr_to_file(phdrs, values.get(DT_STRTAB, -1))
    result: dict[str, Any] = {"status": "PARSED" if str_off is not None else "LIMITED", "needed": [], "soname": None, "entries": len(entries)}
    if str_off is not None:
        for tag, value in entries:
            if tag == DT_NEEDED:
                result["needed"].append(cstring(data, str_off + value))
            elif tag == DT_SONAME:
                result["soname"] = cstring(data, str_off + value)
    return result, values


def parse_dynamic_symbols(data: bytes, hdr: dict[str, Any], phdrs: list[dict[str, int]], dynamic_values: dict[int, int]) -> dict[str, Any]:
    sym_addr, str_addr = dynamic_values.get(DT_SYMTAB), dynamic_values.get(DT_STRTAB)
    if sym_addr is None or str_addr is None:
        return {"status": "NOT_FOUND", "imports": [], "exports": [], "count": 0}
    sym_off, str_off = vaddr_to_file(phdrs, sym_addr), vaddr_to_file(phdrs, str_addr)
    if sym_off is None or str_off is None:
        return {"status": "LIMITED", "imports": [], "exports": [], "count": 0}
    endian, cls = hdr["endian"], hdr["class"]
    ent = int(dynamic_values.get(DT_SYMENT, 24 if cls == 2 else 16))
    count = 0
    if DT_HASH in dynamic_values:
        ho = vaddr_to_file(phdrs, dynamic_values[DT_HASH])
        if ho is not None and ho + 8 <= len(data):
            _nbucket, count = struct.unpack_from(endian + "II", data, ho)
            count = struct.unpack_from(endian + "I", data, ho + 4)[0]
    if not count:
        # Conservative fallback: stop at the first invalid/out-of-file symbol.
        count = min(200000, max(0, (len(data) - sym_off) // ent))
    imports, exports = [], []
    for index in range(count):
        off = sym_off + index * ent
        try:
            if cls == 2:
                st_name, info, _other, shndx, value, size = struct.unpack_from(endian + "IBBHQQ", data, off)
            else:
                st_name, value, size, info, _other, shndx = struct.unpack_from(endian + "IIIBBH", data, off)
        except struct.error:
            break
        name = cstring(data, str_off + st_name)
        if not name:
            continue
        item = {"index": index, "name": name, "value": value, "size": size, "binding": info >> 4, "type": info & 0xF, "section_index": shndx}
        (imports if shndx == 0 else exports).append(item)
    return {"status": "PARSED", "imports": imports[:4096], "exports": exports[:4096], "count": len(imports) + len(exports)}


def relevant_strings(data: bytes, families: list[dict[str, Any]]) -> list[dict[str, Any]]:
    needles = sorted({s for fam in families for s in fam.get("strings", [])})
    out = []
    for needle in needles:
        raw = needle.encode()
        positions = [m.start() for m in re.finditer(re.escape(raw), data)]
        if positions:
            out.append({"needle": needle, "offsets": positions[:64], "count": len(positions)})
    return out


def xref_candidates(data: bytes, phdrs: list[dict[str, int]], string_hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    targets: dict[int, str] = {}
    for hit in string_hits:
        for off in hit["offsets"]:
            targets[off] = hit["needle"]
            for ph in phdrs:
                if ph["offset"] <= off < ph["offset"] + ph["filesz"]:
                    targets[ph["vaddr"] + off - ph["offset"]] = hit["needle"]
    if not targets:
        return []
    values = set(targets)
    result = []
    # A candidate xref is only an aligned little/big-endian 32/64-bit value
    # equal to a string file offset or mapped virtual address. It is not a
    # disassembly or semantic reference.
    for width in (4, 8):
        for endian in ("little", "big"):
            for off in range(0, len(data) - width + 1, 4):
                value = int.from_bytes(data[off:off + width], endian)
                if value in values:
                    result.append({"offset": off, "width": width, "endianness": endian, "points_to": targets[value]})
                    if len(result) >= 2048:
                        return result
    return result


def load_families(path: Path) -> list[dict[str, Any]]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc.get("families", [])


def correlate(families: list[dict[str, Any]], data: bytes, dynsym: dict[str, Any], string_hits: list[dict[str, Any]], xrefs: list[dict[str, Any]], parsed_elf: bool) -> list[dict[str, Any]]:
    text = data.decode("latin1", "ignore")
    names = "\n".join([x["name"] for x in dynsym.get("imports", []) + dynsym.get("exports", [])])
    searchable = text + "\n" + names
    hits_by_name = {x["needle"]: x["count"] for x in string_hits}
    out = []
    for fam in families:
        all_markers = list(dict.fromkeys(fam.get("strings", []) + fam.get("functions", []) + fam.get("functions_or_symbols", [])))
        pre = fam.get("pre_fix_markers", [])
        post = fam.get("post_fix_markers", [])
        present = [m for m in all_markers if m in searchable]
        pre_present = [m for m in pre if m in searchable]
        post_present = [m for m in post if m in searchable]
        xref_count = sum(1 for x in xrefs if x["points_to"] in present)
        evidence_classes = sum(bool(v) for v in (present, pre_present, post_present, xref_count))
        if pre_present and len(pre_present) >= 2 and evidence_classes >= 2:
            classification = "VULNERABLE_LIKE"
        elif post_present and len(post_present) >= 2 and evidence_classes >= 2:
            classification = "FIXED_LIKE"
        elif len(present) >= 3 and evidence_classes >= 2:
            classification = "MATCH"
        elif present:
            classification = "PARTIAL MATCH"
        elif parsed_elf and dynsym.get("status") == "PARSED":
            classification = "NO MATCH"
        else:
            classification = "UNVERIFIED"
        out.append({"id": fam["id"], "classification": classification, "present_markers": present, "pre_fix_markers_present": pre_present, "post_fix_markers_present": post_present, "string_hit_counts": {k: hits_by_name[k] for k in present if k in hits_by_name}, "xref_count": xref_count, "evidence_policy": "CONFIRMED_13.52_DISABLED"})
    return out


def analyze(path: Path, signatures_path: Path = DEFAULT_SIGNATURES) -> dict[str, Any]:
    data = path.read_bytes()
    families = load_families(signatures_path)
    elf_offset = data.find(ELF_MAGIC)
    hdr = parse_elf_header(data, elf_offset if elf_offset >= 0 else 0)
    phdrs = parse_program_headers(data, hdr)
    notes, build_ids = parse_notes(data, phdrs, hdr.get("endian", "<")) if hdr.get("format") in ("ELF32", "ELF64") else ([], [])
    dynamic, dynamic_values = parse_dynamic(data, hdr, phdrs) if phdrs else ({"status": "NOT_FOUND", "needed": [], "soname": None}, {})
    dynsym = parse_dynamic_symbols(data, hdr, phdrs, dynamic_values) if phdrs else {"status": "NOT_FOUND", "imports": [], "exports": [], "count": 0}
    hits = relevant_strings(data, families)
    xrefs = xref_candidates(data, phdrs, hits)
    elf_valid = hdr.get("format") in ("ELF32", "ELF64") and elf_offset == 0
    return {
        "schema": "webkit-retail-static-evidence/v1",
        "path": str(path),
        "size": len(data),
        "sha256": sha256(data),
        "container": {"format": "ELF" if elf_valid else ("SELF_OR_EMBEDDED_ELF" if elf_offset >= 0 else "UNKNOWN_OR_RAW"), "elf_offset": elf_offset if elf_offset >= 0 else None, "elf_header": hdr, "program_headers": phdrs, "pt_load": [x for x in phdrs if x["type"] == PT_LOAD], "notes": notes, "build_ids": build_ids, "dynamic": dynamic, "dynamic_symbols": dynsym},
        "relevant_strings": hits,
        "xref_candidates": xrefs,
        "family_correlations": correlate(families, data, dynsym, hits, xrefs, elf_valid),
        "evidence": "DIRECT_BYTES" if data else "EMPTY",
        "semantic_identity": "UNVERIFIED",
        "target_promotion": "CONFIRMED_13.52_DISABLED",
        "execution": "PROHIBITED",
        "decryption": "NOT_ATTEMPTED",
        "gadget_generation": "DISABLED"
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze an authorized local ELF/SELF-like artifact without execution or decryption.")
    parser.add_argument("artifact", type=Path)
    parser.add_argument("-s", "--signatures", type=Path, default=DEFAULT_SIGNATURES)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.artifact.is_file():
        parser.error(f"artifact not found: {args.artifact}")
    if not args.signatures.is_file():
        parser.error(f"signature manifest not found: {args.signatures}")
    args.output.write_text(json.dumps(analyze(args.artifact, args.signatures), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
