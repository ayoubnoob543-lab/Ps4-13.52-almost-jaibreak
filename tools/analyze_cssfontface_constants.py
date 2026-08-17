#!/usr/bin/env python3
"""Statically inventory CSSFontFace constants from ntfargo/CSSFontFace-Exploit.

This parser deliberately treats the JavaScript file as text. It never imports or
executes the exploit. It extracts firmware-keyed fields and classifies them for
migration work; no value is promoted to PS4 13.52 without target bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

MAJOR_RE = re.compile(r"^\s{2}(\d+)\s*:\s*\{")
MINOR_RE = re.compile(r"^\s{4}(0x[0-9a-fA-F]+|\d+)\s*:\s*\{")
FIELD_RE = re.compile(r"^\s{6}([A-Za-z_$][A-Za-z0-9_$]*)\s*:\s*([^,]+),?")

CSS_FIELDS = {
    "wk_CSSFontFace_sizeof",
    "wk_CSSFontFace_m_families",
    "wk_CSSFontFace_m_featureSettings_m_buffer",
    "wk_CSSFontFace_m_featureSettings_m_size",
    "wk_CSSFontFace_m_featureSettings_m_capacity",
    "wk_CSSFontFace_m_propertiesOrCSSConnection",
    "wk_CSSFontFace_m_clients",
    "wk_CSSFontFace_m_wrapper",
    "wk_CSSFontFace_m_status",
    "wk_CSSFontFace_m_thread",
    "wk_CSSFontFace_m_function",
    "wk_CSSFontFace_vtable",
}


def parse_number(raw: str) -> Any:
    value = raw.strip()
    if value.startswith(("0x", "0X")):
        try:
            return int(value, 16)
        except ValueError:
            return value
    try:
        return int(value, 10)
    except ValueError:
        return value.strip('"\'')


def classify(name: str, major: int, minor: int) -> str:
    if name == "wk_CSSFontFace_m_propertiesOrCSSConnection":
        return "UNVERIFIED"  # absent from the public table; target layout unknown
    if name in CSS_FIELDS or name.startswith("wk_ArrayBuffer_"):
        return "FIRMWARE_DEPENDENT"
    if name.startswith("wk_") or name in {"k__error", "c_strerror", "KPATCH", "SYSENT_661", "EVF_OFFSET", "KL_LOCK", "JMP_RSI_GADGET"}:
        return "FIRMWARE_DEPENDENT"
    return "UNVERIFIED"


def parse(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    records: list[dict[str, Any]] = []
    major: int | None = None
    minor: int | None = None
    for line_no, line in enumerate(text.splitlines(), 1):
        m = MAJOR_RE.match(line)
        if m:
            major = int(m.group(1))
            minor = None
            continue
        m = MINOR_RE.match(line)
        if m and major is not None:
            token = m.group(1)
            minor = int(token, 16) if token.lower().startswith("0x") else int(token)
            continue
        m = FIELD_RE.match(line)
        if m and major is not None and minor is not None:
            name, raw_value = m.groups()
            records.append({
                "firmware": f"{major}.{minor:02x}" if minor > 9 else f"{major}.{minor}",
                "major": major,
                "minor": minor,
                "field": name,
                "value": parse_number(raw_value),
                "classification": classify(name, major, minor),
                "line": line_no,
            })
    firmware = sorted({(r["major"], r["minor"]) for r in records})
    css_records = [r for r in records if r["field"].startswith("wk_CSSFontFace_")]
    return {
        "source": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size": len(raw),
        "record_count": len(records),
        "firmware_keys": [
            {"major": major, "minor": minor, "label": f"{major}.{minor:02x}" if minor > 9 else f"{major}.{minor}"}
            for major, minor in firmware
        ],
        "cssfontface_records": css_records,
        "field_presence": {
            field: sorted({f"{r['major']}.{r['minor']:02x}" if r['minor'] > 9 else f"{r['major']}.{r['minor']}" for r in records if r["field"] == field})
            for field in sorted({r["field"] for r in css_records})
        },
        "target_13_52": {
            "status": "ABSENT",
            "detail": "ABSENT_FROM_PUBLIC_TABLE",
            "rule": "No historical constant is promoted to 13.52 without same-build WebKit bytes.",
            "required": [
                "libSceNKWebKit.sprx or equivalent WebKit image",
                ".text and PT_SCE_RELRO boundaries",
                "vtable bytes/XREFs for CSSFontFace",
                "field-layout validation for m_featureSettings and m_propertiesOrCSSConnection",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("constants", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = parse(args.constants)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
