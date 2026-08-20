#!/usr/bin/env python3
"""Render WPE headless runner and comparison JSON into a concise Markdown report."""
from __future__ import annotations

import argparse
import json
import pathlib


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runner_json")
    parser.add_argument("comparison_json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    runner = json.loads(pathlib.Path(args.runner_json).read_text(encoding="utf-8"))
    comparison = json.loads(pathlib.Path(args.comparison_json).read_text(encoding="utf-8"))
    runtime_value = runner.get("runtime")
    runtime = runtime_value if isinstance(runtime_value, dict) else {"description": runtime_value} if runtime_value else {}
    architecture = runtime.get("architecture") or {}
    process = runner.get("process") or {}
    lines = [
        "# WPE WebKit 2.52.6 headless smoke report",
        "",
        "> This report records only explicit runner output. A host/offscreen PASS is not a WPE/WebCore PASS.",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Runner status | **{runner.get('status', 'UNKNOWN')}** |",
        f"| Comparison status | **{comparison.get('status', 'UNKNOWN')}** |",
        f"| Reason | {runner.get('reason') or comparison.get('reason') or ''} |",
        f"| Runtime | `{runtime.get('description', runtime.get('binary', 'NOT_RUN'))}` |",
        f"| Binary SHA-256 | `{runtime.get('binary_sha256', 'NOT_RUN')}` |",
        f"| Architecture probe | `{architecture.get('stdout', '').strip() or 'NOT_RUN'}` |",
        f"| Process elapsed | `{process.get('elapsed_s', 'NOT_RUN')}` seconds |",
        "",
        "## Fixture validation",
        "",
        "| Fixture | SHA-256 | Status |",
        "|---|---|---|",
    ]
    for fixture in runner.get("fixtures", runner.get("fixture_validation", [])):
        lines.append(f"| {fixture['id']} | `{fixture.get('sha256')}` | **{fixture.get('status')}** |")
    lines += ["", "## Capability comparison", "", "| Capability | Status | Stages |", "|---|---|---|"]
    for capability, value in sorted(comparison.get("capabilities", {}).items()):
        lines.append(f"| {capability} | **{value.get('status')}** | {', '.join(value.get('stages', []))} |")
    if not comparison.get("capabilities"):
        lines.append("| all capabilities | **NOT_RUN/BLOCKED** | no explicit assertions received |")
    lines += ["", "## Runtime evidence", "", "```json", json.dumps({"runtime": runtime, "process": process}, indent=2, sort_keys=True), "```", ""]
    pathlib.Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(str(pathlib.Path(args.output).resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
