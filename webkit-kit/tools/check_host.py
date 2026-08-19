#!/usr/bin/env python3
"""Report host-side prerequisites without installing or executing PS4 artifacts."""
from __future__ import annotations

import json
import platform
import shutil
import subprocess

COMMANDS = ["python3", "clang", "ld.lld", "cmake", "ninja", "file", "readelf", "sha256sum"]

def version(command: str) -> str | None:
    path = shutil.which(command)
    if not path:
        return None
    try:
        p = subprocess.run([path, "--version"], text=True, capture_output=True, check=False)
        return (p.stdout or p.stderr).splitlines()[0] if (p.stdout or p.stderr) else path
    except OSError:
        return path

def main() -> int:
    print(json.dumps({
        "host": platform.platform(),
        "python": platform.python_version(),
        "commands": {c: version(c) for c in COMMANDS},
        "ps4_sdk_present": False,
        "retail_webkit_13_52_present": False,
        "kernel6_bytes_present": False,
        "executed_ps4_artifacts": False,
        "note": "Host prerequisites only; PS4 artifacts are not loaded or executed.",
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
