#!/usr/bin/env python3
"""Static classifier for a PSFree reference tree.

This tool inventories source text only. It deliberately does not import, run,
assemble, resolve, or emit exploit/ROP/JOP payload data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

HEX = re.compile(r"0x[0-9a-fA-F]+")
TARGET = re.compile(r"(?:9\.60|960|offset|gadget|rop|jop|payload|syscall|libkernel|webkit)", re.I)

def classify(text: str, path: str) -> list[dict[str, object]]:
    rows = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if not TARGET.search(line):
            continue
        literals = HEX.findall(line)
        if any(x in line.lower() for x in ("payload", "rop", "jop", "gadget")):
            category = "EXPLOIT_CHAIN_REFERENCE_ONLY"
        elif "offset" in line.lower() or literals:
            category = "TARGET_SPECIFIC_DATA_CANDIDATE"
        else:
            category = "GENERIC_OR_STRUCTURAL"
        rows.append({
            "path": path,
            "line": line_no,
            "category": category,
            "hex_literals": literals,
            "text": line.strip(),
            "13_52_status": "MISSING_UNVERIFIED",
        })
    return rows

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("reference_root", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.reference_root.resolve()
    files = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix in {".mjs", ".js", ".html"})
    result = {
        "reference": "zacke0815/ps4-9.04_webkitJB",
        "reference_commit": "e9046aa49b44584ef1a8bbdbc63e8a77d0709e1d",
        "scope": "static text classification only",
        "executed_code": False,
        "13_52_compatibility_claim": "NOT_ESTABLISHED",
        "files": [],
    }
    for p in files:
        data = p.read_bytes()
        text = data.decode("utf-8", errors="replace")
        result["files"].append({
            "path": str(p.relative_to(root)),
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "matches": classify(text, str(p.relative_to(root))),
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"files": len(files), "output": str(args.output), "executed_code": False}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
