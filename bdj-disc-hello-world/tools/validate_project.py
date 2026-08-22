#!/usr/bin/env python3
"""Static validation only for the benign BD-J Hello World project.

This script checks paths and source text. It never loads, executes, or imports
BD-J classes and it never treats missing platform stubs as available.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
required = [
    ROOT / "README.md",
    ROOT / "src/org/homebrew/MyXlet.java",
]
for path in required:
    if not path.is_file():
        raise SystemExit(f"MISSING {path.relative_to(ROOT)}")

source = (ROOT / "src/org/homebrew/MyXlet.java").read_text(encoding="utf-8")
for forbidden in ("Runtime.getRuntime", "System.load", "ProcessBuilder", "java.net", "Unsafe"):
    if forbidden in source:
        raise SystemExit(f"FORBIDDEN_REFERENCE {forbidden}")

platform_candidates = [
    ROOT / "lib/bdj.jar",
    ROOT / "lib/classes.zip",
    ROOT / "platform/bdj.jar",
]
result = {
    "project": "bdj-disc-hello-world",
    "mode": "static-only",
    "required_files": [str(p.relative_to(ROOT)) for p in required],
    "platform_stub_candidates": [
        {"path": str(p.relative_to(ROOT)), "present": p.is_file()}
        for p in platform_candidates
    ],
    "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
    "iso_generated": (ROOT / "build/bdj-hello-world.iso").is_file(),
    "iso_sha256": (hashlib.sha256((ROOT / "build/bdj-hello-world.iso").read_bytes()).hexdigest()
                    if (ROOT / "build/bdj-hello-world.iso").is_file() else None),
    "hardware_tested": False,
}
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs/validation.json").write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(result, indent=2, sort_keys=True))
