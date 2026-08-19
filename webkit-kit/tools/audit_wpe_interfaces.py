#!/usr/bin/env python3
"""Static inventory of the public libwpe contract and WebKit WPE references.

This tool does not compile, load shared libraries, execute WebKit, or infer a
platform ABI. It only scans source/header text supplied by the caller.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

HEADER_NAMES = {
    "loader.h",
    "renderer-host.h",
    "renderer-backend-egl.h",
    "view-backend.h",
    "input.h",
}


def files_under(root: Path, suffixes: Iterable[str] = ()) -> list[Path]:
    if not root.exists():
        return []
    suffixes = tuple(suffixes)
    files = [p for p in root.rglob("*") if p.is_file()]
    if suffixes:
        files = [p for p in files if p.suffix in suffixes]
    return sorted(files)


def public_headers(include_root: Path) -> dict:
    result = {"root": str(include_root), "status": "MISSING", "headers": []}
    header_dir = include_root / "wpe"
    if not header_dir.exists():
        header_dir = include_root
    found = []
    for path in sorted(header_dir.rglob("*.h")) if header_dir.exists() else []:
        if path.name not in HEADER_NAMES:
            continue
        text = path.read_text(errors="replace")
        functions = sorted(set(re.findall(r"\bwpe_[a-zA-Z0-9_]+\s*\(", text)))
        functions = [f.split("(")[0] for f in functions]
        interfaces = sorted(set(re.findall(r"struct\s+(wpe_[a-zA-Z0-9_]+_interface)", text)))
        structs = sorted(set(re.findall(r"struct\s+(wpe_[a-zA-Z0-9_]+)", text)))
        found.append({
            "path": str(path),
            "functions": functions,
            "interfaces": interfaces,
            "structs": structs,
        })
    result["headers"] = found
    result["status"] = "PUBLIC" if found else "MISSING"
    return result


def webkit_scan(source_root: Path) -> dict:
    result = {
        "root": str(source_root),
        "status": "MISSING",
        "files_scanned": 0,
        "wpe_files": [],
        "platform_markers": {},
        "cmake_libraries": [],
        "process_outputs": [],
    }
    files = files_under(source_root, (".cmake", ".cpp", ".h", ".txt"))
    result["files_scanned"] = len(files)
    if not files:
        return result
    marker_re = re.compile(r"(?:PLATFORM\(WPE\)|WTF_PLATFORM_WPE|USE\(WPE_RENDERER\)|\bwpe_[A-Za-z0-9_]+|PlatformWPE|WPEPlatform)")
    for path in files:
        text = path.read_text(errors="replace")
        lines = [i + 1 for i, line in enumerate(text.splitlines()) if marker_re.search(line)]
        if lines:
            result["wpe_files"].append({"path": str(path), "marker_lines": lines[:100], "marker_count": len(lines)})
        if path.name == "PlatformWPE.cmake" or path.name == "PlatformWPE.cmake.in":
            libs = re.findall(r"(?:WebCore_LIBRARIES|WebKit_LIBRARIES|WebCore_PRIVATE_LIBRARIES).*", text)
            result["cmake_libraries"].extend(libs)
        if path.name == "PlatformWPE.cmake":
            result["process_outputs"].extend(re.findall(r"set\(([^ ]+_OUTPUT_NAME)\s+([^\)]+)\)", text))
    result["wpe_files"].sort(key=lambda item: item["path"])
    result["status"] = "AVAILABLE"
    return result


def classify(headers: dict, webkit: dict) -> list[dict]:
    rows = [
        ("libwpe public C API", "PUBLIC" if headers["status"] == "PUBLIC" else "MISSING", "headers/loader, renderer and input contracts"),
        ("WebKit WPE port source", "AVAILABLE" if webkit["status"] == "AVAILABLE" else "MISSING", "PlatformWPE and WPE marker scan"),
        ("WPEBackend-fdo implementation", "HOST_ONLY", "reference Linux/Freedesktop backend; not a target backend"),
        ("target renderer/display implementation", "MISSING", "must provide native display/window or an offscreen path"),
        ("target input translation", "MISSING", "must translate platform events to wpe_input_* structures"),
        ("target process IPC/FD transport", "MISSING", "backend/application integration owns transport details"),
        ("WebCore/JSC portable engine", "PORTABLE", "portable source, still requires a complete platform/build contract"),
        ("PS4/Orbis ABI or SDK", "UNKNOWN", "not inspected or supplied; deliberately out of scope"),
    ]
    return [{"component": c, "status": s, "evidence": e} for c, s, e in rows]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--libwpe-include", type=Path, required=True)
    parser.add_argument("--webkit-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    headers = public_headers(args.libwpe_include)
    webkit = webkit_scan(args.webkit_source)
    report = {
        "schema": "webkit-kit/wpe-interface-audit-v1",
        "mode": "static-only",
        "libwpe": headers,
        "webkit": webkit,
        "classification": classify(headers, webkit),
        "not_claimed": ["PS4 compatibility", "retail ABI", "functional target backend", "hardware rendering"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "libwpe": headers["status"], "webkit": webkit["status"], "classes": len(report["classification"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
