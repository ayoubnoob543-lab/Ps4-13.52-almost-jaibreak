#!/usr/bin/env python3
"""Compare structural-signature JSON files without resolving addresses."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def jaccard(left: list[str], right: list[str]) -> float:
    a, b = set(left), set(right)
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b) if a | b else 0.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    left = json.loads(args.left.read_text(encoding="utf-8"))
    right = json.loads(args.right.read_text(encoding="utf-8"))
    left_artifact = left.get("artifacts", [{}])[0]
    right_artifact = right.get("artifacts", [{}])[0]
    left_sig = left_artifact.get("signature", {}).get("token_and_window_hashes", [])
    right_sig = right_artifact.get("signature", {}).get("token_and_window_hashes", [])
    result = {
        "schema": "webkit-structural-comparison/v1",
        "left": {"path": left_artifact.get("path"), "sha256": left_artifact.get("sha256")},
        "right": {"path": right_artifact.get("path"), "sha256": right_artifact.get("sha256")},
        "similarity": {"token_window_jaccard": round(jaccard(left_sig, right_sig), 6)},
        "status": "CANDIDATE_STRUCTURAL_ONLY",
        "absolute_offsets": "DISABLED",
        "semantic_identity": "UNVERIFIED",
        "limitations": [
            "byte windows are not disassembly",
            "no target Build ID",
            "no function boundaries",
            "no import resolution",
            "no gadget generation",
        ],
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
