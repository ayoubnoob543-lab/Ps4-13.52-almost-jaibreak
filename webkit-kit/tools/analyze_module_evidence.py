#!/usr/bin/env python3
"""Build a conservative evidence report for one future WebKit module.

The report is structural only: it does not execute files, disassemble them,
resolve absolute addresses, or claim that OSS/WPE matches PS4 retail.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from structural_signatures import analyze


def jaccard(left: list[str], right: list[str]) -> float:
    a, b = set(left), set(right)
    return round(len(a & b) / len(a | b), 6) if a or b else 0.0


def compare(target: dict[str, Any], reference: dict[str, Any]) -> dict[str, Any]:
    t_fmt, r_fmt = target["format"], reference["format"]
    t_tokens = target["strings"]["sha256_tokens"]
    r_tokens = reference["strings"]["sha256_tokens"]
    return {
        "reference_path": reference["path"],
        "reference_sha256": reference["sha256"],
        "format_same": t_fmt.get("format") == r_fmt.get("format"),
        "class_same": t_fmt.get("class") == r_fmt.get("class"),
        "machine_same": t_fmt.get("machine") == r_fmt.get("machine"),
        "pt_load_count": {"target": len(t_fmt.get("pt_load", [])), "reference": len(r_fmt.get("pt_load", []))},
        "token_jaccard": jaccard(t_tokens, r_tokens),
        "classification": "CANDIDATE_STRUCTURAL_ONLY",
        "semantic_equivalence": "UNVERIFIED",
        "absolute_offsets": "DISABLED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a static evidence report for one ELF/SELF-like module.")
    parser.add_argument("target", type=Path)
    parser.add_argument("--reference", action="append", type=Path, default=[])
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.target.is_file():
        raise SystemExit(f"target not found: {args.target}")
    target = analyze(args.target)
    refs = [analyze(path) for path in args.reference if path.is_file()]
    document = {
        "schema": "ps4-webkit-module-evidence/v1",
        "target": target,
        "references": refs,
        "comparisons": [compare(target, ref) for ref in refs],
        "policy": {
            "execution": "PROHIBITED",
            "payloads_and_exploits": "PROHIBITED",
            "absolute_offsets": "DISABLED",
            "promotion_to_confirmed": "REQUIRES_PROVENANCE_HASH_AND_BUILD_ID_OR_EQUIVALENT",
            "wpe_or_oss_equivalence": "NEVER_INFERRED",
        },
        "next_required_evidence": [
            "firmware/source provenance",
            "SHA-256 recorded at acquisition",
            "SELF/ELF container identity",
            "common-build metadata if comparing a module set",
        ],
    }
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
