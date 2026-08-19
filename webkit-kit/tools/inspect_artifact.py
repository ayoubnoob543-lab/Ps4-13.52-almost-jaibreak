#!/usr/bin/env python3
"""Static inspector for WebKit/JSC ELF/SELF candidates.

Never loads or executes the inspected file. It only reads bytes, hashes them,
and uses the system `file`/`readelf` tools when available.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

PATTERNS = [
    rb"libSceNKWebKit", rb"libkernel_web", rb"libSceLibcInternal",
    rb"WebKit", rb"JavaScriptCore", rb"ORBIS", rb"13\.52",
    rb"SceShell", rb"build", rb"clang", rb"llvm", rb"webkit",
]


def run(cmd: list[str]) -> str | None:
    if not shutil.which(cmd[0]):
        return None
    try:
        return subprocess.run(cmd, text=True, capture_output=True, check=False).stdout
    except OSError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact", type=Path)
    ap.add_argument("--max-string-bytes", type=int, default=4_000_000)
    args = ap.parse_args()
    p = args.artifact.resolve()
    if not p.is_file():
        ap.error(f"not a regular file: {p}")
    data = p.read_bytes()
    sample = data[: args.max_string_bytes]
    strings = {}
    for pat in PATTERNS:
        key = pat.decode("ascii", errors="replace")
        strings[key] = [m.group(0).decode("utf-8", errors="replace") for m in re.finditer(rb"[ -~]{4,}", sample) if re.search(pat, m.group(0))][:50]
    result = {
        "path": str(p),
        "size": p.stat().st_size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "magic": data[:16].hex(),
        "file": run(["file", "-b", str(p)]),
        "readelf_header": run(["readelf", "-h", str(p)]),
        "readelf_program_headers": run(["readelf", "-l", str(p)]),
        "strings_matches": strings,
        "executed": False,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
