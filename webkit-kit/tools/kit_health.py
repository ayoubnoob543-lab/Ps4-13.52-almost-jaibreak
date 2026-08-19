#!/usr/bin/env python3
"""Conservative static health check for the WebKit kit."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

SECRET = re.compile(r"(?i)(private[_-]?key|api[_-]?key|password\s*=\s*[^$\{])")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).parents[1])
    args = parser.parse_args()
    findings = []
    for path in args.root.rglob("*"):
        if path.name == "kit_health.py":
            continue
        if not path.is_file() or path.suffix.lower() not in {".py", ".json", ".js", ".md", ".sh"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if SECRET.search(text):
            findings.append({"file": str(path), "kind": "possible_secret_marker"})
        if "GADGET_GENERATION=ENABLED" in text or '"absolute_offsets": "ENABLED"' in text:
            findings.append({"file": str(path), "kind": "unsafe_policy_marker"})
    result = {
        "schema": "webkit-kit-health/v1",
        "findings": findings,
        "status": "PASS" if not findings else "REVIEW_REQUIRED",
        "scope": "static_only",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not findings else 2


if __name__ == "__main__":
    raise SystemExit(main())
