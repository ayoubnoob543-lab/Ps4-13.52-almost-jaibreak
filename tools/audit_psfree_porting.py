#!/usr/bin/env python3
"""Static PSFree porting audit.

This tool reads PSFree source text only. It never imports or executes JavaScript.
It reports which mechanisms are portable and which values are historical
firmware-dependent data that must be rebuilt for PS4 13.52.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PORTABLE = "PORTABLE"
FIRMWARE_DEPENDENT = "FIRMWARE_DEPENDENT"
OBSOLETE = "OBSOLETE"
REQUIRES_REANALYSIS = "REQUIRES_REANALYSIS"
UNVERIFIED = "UNVERIFIED"
ABSENT = "ABSENT"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def source_line(text: str, needle: str) -> int | None:
    for index, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return index
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--psfree", type=Path, required=True)
    parser.add_argument("--target", default="13.52")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    root = args.psfree
    offsets = read(root / "module/offset.mjs")
    memtools = read(root / "module/memtools.mjs")
    send = read(root / "send.mjs")
    chain = read(root / "module/chain.mjs")
    rop = read(root / "rop/900.mjs")

    structures = [
        ("JSC::JSObject.m_cell", "js_cell", "0x0", FIRMWARE_DEPENDENT),
        ("JSC::JSObject.m_butterfly", "js_butterfly", "0x8", FIRMWARE_DEPENDENT),
        ("JSC::JSObject.inline_properties", "js_inline_prop", "0x10", FIRMWARE_DEPENDENT),
        ("JSC::JSArrayBufferView.m_vector", "view_m_vector", "0x10", REQUIRES_REANALYSIS),
        ("JSC::JSArrayBufferView.m_length", "view_m_length", "0x18", REQUIRES_REANALYSIS),
        ("JSC::JSArrayBufferView.m_mode", "view_m_mode", "0x1c", REQUIRES_REANALYSIS),
        ("WTF::StringImpl.m_length", "strimpl_strlen", "0x4", REQUIRES_REANALYSIS),
        ("WTF::StringImpl.m_data", "strimpl_m_data", "0x8", REQUIRES_REANALYSIS),
        ("WTF::StringImpl.inline_data", "strimpl_inline_str", "0x14", REQUIRES_REANALYSIS),
        ("WebCore::JSHTMLTextAreaElement.m_wrapped", "jsta_impl", "0x18", REQUIRES_REANALYSIS),
    ]
    structure_report = []
    for name, symbol, historical, status in structures:
        present = symbol in offsets
        structure_report.append({
            "name": name,
            "historical_offset": historical if present else None,
            "source": "module/offset.mjs",
            "source_line": source_line(offsets, symbol),
            "status": status if present else ABSENT,
            "target": args.target,
        })

    portable = [
        ("page_boundary_base_scan", "find_base", "module/memtools.mjs"),
        ("rip_relative_import_resolution", "resolve_import", "module/memtools.mjs"),
        ("module_dump_boundaries", "get_boundaries", "send.mjs"),
        ("system_v_amd64_argument_contract", "System V ABI", "send.mjs"),
        ("gadget_name_lookup", "get_gadget", "module/chain.mjs"),
    ]
    portable_report = []
    for name, needle, source in portable:
        text = {"module/memtools.mjs": memtools, "send.mjs": send, "module/chain.mjs": chain}[source]
        portable_report.append({
            "name": name,
            "status": PORTABLE if needle in text else ABSENT,
            "source": source,
            "source_line": source_line(text, needle),
            "target": args.target,
        })

    historical = []
    for name, pattern, source in [
        ("WebKit __stack_chk_fail import", r"const offset = 0x8d8", "send.mjs"),
        ("WebKit strlen import", r"const offset = 0x918", "send.mjs"),
        ("ExecState argument offset", r"argumentOffset is 0x30", "send.mjs"),
        ("textarea scrollLeft vtable entry", r"0x1b8", "rop/900.mjs"),
    ]:
        text = send if source == "send.mjs" else rop
        match = re.search(pattern, text)
        historical.append({
            "name": name,
            "value": match.group(0) if match else None,
            "status": OBSOLETE if match else ABSENT,
            "source": source,
            "source_line": source_line(text, match.group(0)) if match else None,
            "target": args.target,
        })

    support_text = "\n".join([send, chain, rop])
    supports_1352 = bool(re.search(r"13\.52|0xd?52", support_text))
    load_900 = "0x800 <= value <= 0x900" in chain or "rop/900.mjs" in chain
    report = {
        "tool": "audit_psfree_porting.py",
        "analysis_mode": "static text parsing; JavaScript not executed",
        "source": str(root),
        "target_firmware": args.target,
        "source_support": {
            "explicit_target_13_52": supports_1352,
            "public_13_52_support": UNVERIFIED if supports_1352 else ABSENT,
            "loader_range_detected": "8.00-9.00 historical loader" if load_900 else None,
            "8_50_8_52_webkit_table": UNVERIFIED,
        },
        "structures": structure_report,
        "portable_mechanisms": portable_report,
        "historical_absolute_values": historical,
        "limits": [
            "No 13.52 WebKit image was analyzed by this source-only audit.",
            "Historical offsets are not ported or converted by delta.",
            "No JOP/ROP chain or runtime payload is generated.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
