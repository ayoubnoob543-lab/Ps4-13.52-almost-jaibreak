#!/usr/bin/env python3
"""Run the safe ECMAScript smoke harness through Node.

Host-only check: it does not emulate Orbis, load PS4 modules, access the
network, or execute exploit/payload code.
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--harness",
        type=Path,
        default=Path(__file__).parents[1] / "harness" / "basic_capabilities.js",
    )
    args = ap.parse_args()
    node = shutil.which("node")
    result = {
        "kind": "HOST_ECMASCRIPT_SMOKE",
        "harness": str(args.harness),
        "status": "BLOCKED",
        "scope": "host_only_not_ps4_webkit",
    }
    if not args.harness.is_file():
        result["reason"] = "harness_missing"
    elif not node:
        result["reason"] = "node_unavailable"
    else:
        proc = subprocess.run(
            [node, str(args.harness)],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        result.update(
            {
                "exit_code": proc.returncode,
                "stdout": proc.stdout[-4000:],
                "stderr": proc.stderr[-4000:],
                "status": "PASS" if proc.returncode == 0 else "FAIL",
            }
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in {"PASS", "BLOCKED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())


def _unused_for_type_checking() -> None:
    """Keep this module intentionally free of artifact execution helpers."""
    return None
