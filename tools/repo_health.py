#!/usr/bin/env python3
"""Conservative repository health check for static PS4/WebKit research."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

SECRET = re.compile(r"BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}")


def git(cmd: list[str]) -> str:
    return subprocess.check_output(["git", *cmd], text=True).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    files = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]
    findings: list[dict[str, object]] = []
    for p in files:
        if p.stat().st_size > 100 * 1024 * 1024:
            findings.append({"type": "large_file", "path": str(p.relative_to(root)), "size": p.stat().st_size})
        if p.suffix in {".json"}:
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except Exception as exc:
                findings.append({"type": "invalid_json", "path": str(p.relative_to(root)), "error": str(exc)})
        if p.suffix in {".py", ".js", ".mjs", ".sh", ".md", ".json", ".ts", ".tsx"}:
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if SECRET.search(text):
                findings.append({"type": "secret_pattern", "path": str(p.relative_to(root))})
    result = {
        "branch": git(["branch", "--show-current"]),
        "head": git(["rev-parse", "HEAD"]),
        "tracked_files": len(git(["ls-files"]).splitlines()),
        "working_tree_clean": not bool(git(["status", "--porcelain"])),
        "findings": findings,
        "policy": "static_only_no_exploit_execution",
    }
    output = json.dumps(result, indent=2) + "\n"
    if args.json:
        print(output, end="")
    else:
        print(f"branch={result['branch']} head={result['head']} tracked={result['tracked_files']}")
        print(f"working_tree_clean={result['working_tree_clean']} findings={len(findings)}")
        for finding in findings:
            print(finding)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
