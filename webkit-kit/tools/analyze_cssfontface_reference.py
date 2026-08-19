#!/usr/bin/env python3
"""Static inventory for CSSFontFace-Exploit.

The analyzer reads source and patch metadata only. It never imports JavaScript,
starts the server, resolves gadgets, or emits exploit parameters.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SOURCE_EXT = {".js", ".html", ".css", ".py", ".md", ".jsm"}
MARKERS = re.compile(r"13\.52|13\.5|11\.02|11\.00|10\.50|9\.60|offset|gadget|kernel|patch|libkernel|payload|rop|jop|syscall|CSSFontFace|WebKit", re.I)

def category(path: Path, text: str) -> str:
    name = path.as_posix().lower()
    if "/patches/" in name or path.suffix == ".bin":
        return "HISTORICAL_BINARY_PATCH_METADATA_ONLY"
    if any(x in text.lower() for x in ("rop", "jop", "payload", "arbitrary write", "syscall")):
        return "EXPLOIT_CHAIN_REFERENCE_ONLY"
    if any(x in text.lower() for x in ("cssfontface", "webkit", "webcore")):
        return "WEBKIT_RESEARCH_REFERENCE"
    return "GENERIC_SUPPORTING_CODE"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.root.resolve()
    files = []
    for p in sorted(x for x in root.rglob("*") if x.is_file()):
        data = p.read_bytes()
        text = data.decode("utf-8", errors="replace") if p.suffix in SOURCE_EXT else ""
        matches = []
        if text:
            for no, line in enumerate(text.splitlines(), 1):
                if MARKERS.search(line):
                    matches.append({"line": no, "text": line.strip()[:500]})
        files.append({
            "path": p.relative_to(root).as_posix(),
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "category": category(p, text),
            "marker_count": len(matches),
            "markers": matches,
            "13_52_status": "MISSING_UNVERIFIED",
        })
    result = {
        "repository": "ntfargo/CSSFontFace-Exploit",
        "audited_head": "221baa6e7349b96a6fd299808a25a4178e47741c",
        "scope": "static inventory only",
        "executed_code": False,
        "13_52_compatibility": "NOT_ESTABLISHED",
        "files": files,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"files": len(files), "output": str(args.output), "executed_code": False}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
