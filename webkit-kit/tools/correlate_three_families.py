#!/usr/bin/env python3
"""Static source correlator for the frozen WebKit/JSC families.

This tool reads source text only. It never compiles, imports, executes, decrypts,
or assigns PS4 13.52 provenance. A result is a structural correlation, not a
vulnerability confirmation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "three_family_signatures.json"
SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".h", ".hpp", ".inc", ".m", ".mm", ".java"}


def files_for(root: Path, include_docs: bool = False) -> list[Path]:
    if root.is_file():
        return [root]
    suffixes = SOURCE_SUFFIXES | ({".txt", ".json"} if include_docs else set())
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix in suffixes)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def evidence(text: str, markers: list[str]) -> list[str]:
    return [marker for marker in markers if marker and marker.lower() in text.lower()]


def function_hits(text: str, functions: list[str]) -> list[str]:
    hits: list[str] = []
    for name in functions:
        short = name.split("::")[-1]
        if re.search(rf"\b{re.escape(short)}\s*\(", text) or name.lower() in text.lower():
            hits.append(name)
    return hits


def classify_family(family: dict[str, Any], text: str, paths: list[str]) -> dict[str, Any]:
    strings = evidence(text, family.get("strings", []))
    pre = evidence(text, family.get("pre_fix_markers", []))
    post = evidence(text, family.get("post_fix_markers", []))
    funcs = function_hits(text, family.get("functions", []) + family.get("functions_or_symbols", []))
    family_id = family["id"]

    if family_id == "jscell_tox_type_validation":
        family_match = len(funcs) >= 3 and len(strings) >= 2
        vulnerable = len(pre) >= 2 and not post
        fixed = len(post) >= 3 and len(funcs) >= 2
    elif family_id == "markedvector_gc_containers":
        family_match = (len(strings) >= 3 and ("CloneDeserializer" in text or "SerializedScriptValue" in text))
        vulnerable = len(pre) >= 2 and "Vector" in text and "MarkedVector" not in text
        fixed = len(post) >= 3 and ("markLists" in text or "Heap::markListSet" in text)
    elif family_id == "clone_object_pool_alignment":
        family_match = ("CloneSerializer" in text and "CloneDeserializer" in text and len(strings) >= 3)
        vulnerable = "m_gcBuffer" in text and "m_objectPool" in text and "m_keepAliveBuffer" not in text
        fixed = "m_objectPool" in text and "m_keepAliveBuffer" in text and len(post) >= 3
    else:
        family_match = bool(strings or funcs)
        vulnerable = bool(pre) and not post
        fixed = bool(post) and not pre

    if family_match:
        match = "MATCH"
    elif strings or funcs:
        match = "PARTIAL MATCH"
    else:
        match = "NO MATCH"

    state = "VULNERABLE_LIKE" if vulnerable else "FIXED_LIKE" if fixed else "UNVERIFIED"
    return {
        "id": family_id,
        "component": family.get("component"),
        "reference_commit": family.get("reference_commit"),
        "bugzilla": family.get("bugzilla"),
        "match": match,
        "vulnerability_state": state,
        "status_13_52": "UNVERIFIED",
        "matched_files": paths,
        "functions": funcs,
        "strings": strings,
        "pre_fix_markers": pre,
        "post_fix_markers": post,
        "note": "Structural source correlation only; provenance and retail 13.52 status are not inferred.",
    }


def analyze(root: Path, config_path: Path, include_docs: bool = False) -> dict[str, Any]:
    files = files_for(root, include_docs=include_docs)
    contents = [(path, read_text(path)) for path in files]
    joined = "\n".join(text for _, text in contents)
    paths = [str(path) for path, _ in contents]
    config = json.loads(config_path.read_text(encoding="utf-8"))
    results = [classify_family(family, joined, paths) for family in config.get("families", [])]
    return {
        "input": str(root),
        "input_sha256": hashlib.sha256(joined.encode("utf-8")).hexdigest(),
        "file_count": len(files),
        "config": str(config_path),
        "target_firmware": config.get("target_firmware"),
        "provenance": "UNVERIFIED unless supplied separately by an authorized manifest",
        "families": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--include-docs", action="store_true", help="Include .txt/.json files; disabled by default to avoid documentation false positives")
    args = parser.parse_args()
    result = analyze(args.root, args.config, include_docs=args.include_docs)
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
