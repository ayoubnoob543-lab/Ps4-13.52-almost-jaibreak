#!/usr/bin/env python3
"""Cross-source static evidence inventory for the PS4 13.52 migration.

The tool reads source files and manifests as text. It does not import, build, or
execute any external exploit, payload, JavaScript, TypeScript, ELF, or binary.
Historical values are never promoted to CONFIRMED_1352 unless the local anchor
hash matches the repository manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ALLOWED = {
    "CONFIRMED_1352",
    "DIRECT_BYTES",
    "STRUCTURAL",
    "PORTABLE",
    "REQUIRES_REANALYSIS",
    "UNVERIFIED",
    "ABSENT",
}


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(path: Path) -> str | None:
    if not (path / ".git").exists():
        return None
    try:
        return subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def contains(text: str, *terms: str) -> bool:
    return all(term.lower() in text.lower() for term in terms)


def scan_psfree(path: Path) -> dict[str, Any]:
    files = [path / "module/memtools.mjs", path / "module/offset.mjs", path / "config.mjs", path / "psfree.mjs", path / "send.mjs"]
    text = "\n".join(read_text(p) for p in files)
    findings = [
        {"name": "module_boundary_scan", "status": "PORTABLE", "evidence": "find_base() scans page boundaries for module text/data."} if "export function find_base" in text else {"name": "module_boundary_scan", "status": "ABSENT"},
        {"name": "import_resolution", "status": "PORTABLE", "evidence": "resolve_import() decodes FF 25 RIP-relative import stubs."} if "export function resolve_import" in text else {"name": "import_resolution", "status": "ABSENT"},
        {"name": "libkernel_web_syscall_scan", "status": "PORTABLE", "evidence": "searches rdlo and mov eax,syscall; mov r10,rcx; syscall pattern."} if contains(text, "libkernel_web", "rdlo", "syscall_num") else {"name": "libkernel_web_syscall_scan", "status": "ABSENT"},
        {"name": "historical_webkit_layouts", "status": "REQUIRES_REANALYSIS", "evidence": "offset.mjs contains historical JSC/WebCore layouts, not 13.52 values."} if "js_cell" in text and "jsta_impl" in text else {"name": "historical_webkit_layouts", "status": "ABSENT"},
    ]
    return {"source": "PSFree", "path": str(path), "commit": git_head(path), "firmware_context": "9.00/default historical", "findings": findings}


def scan_css(path: Path) -> dict[str, Any]:
    readme = read_text(path / "README.md")
    constants = read_text(path / "public/src/ps4/constants.js")
    fields = sorted(set(re.findall(r"wk_CSSFontFace_[A-Za-z0-9_]+", constants)))
    firmware_keys = sorted(set(re.findall(r"^\s{2}(\d+):\s*\{", constants, re.MULTILINE)))
    return {
        "source": "CSSFontFace-Exploit",
        "path": str(path),
        "commit": git_head(path),
        "scope_claim": "6.00-13.52" if "6.00-13.52" in readme else None,
        "implementation_claim": "6.00-11.02" if "6.00-11.02" in readme else None,
        "firmware_major_keys": [int(x) for x in firmware_keys],
        "fields": fields,
        "findings": [
            {"name": "uaf_methodology", "status": "PORTABLE", "evidence": "object lifetime coordination and fake-object organization are methodological."},
            {"name": "historical_layout_constants", "status": "STRUCTURAL", "evidence": "constants.js contains firmware-keyed CSSFontFace fields through 11.02."},
            {"name": "m_featureSettings_13_52", "status": "REQUIRES_REANALYSIS", "evidence": "README states newer WebKit introduced m_propertiesOrCSSConnection and invalidated the public primitive."},
            {"name": "webkit_13_52_artifact", "status": "ABSENT", "evidence": "no target WebKit image is present in the repository."},
        ],
    }


def scan_vue(path: Path) -> dict[str, Any]:
    files = list((path / "src/download0").glob("*.ts")) + [path / "README.md", path / "src/download0/config.json"]
    text = "\n".join(read_text(p) for p in files)
    versions = sorted(set(re.findall(r"\b(?:12\.50|12\.52|13\.00|13\.02|13\.04|13\.52)\b", text)))
    has_userland = "src/download0/userland.ts" in {str(p.relative_to(path)) for p in files if p.exists()}
    has_kernel = "src/download0/kernel.ts" in {str(p.relative_to(path)) for p in files if p.exists()}
    return {
        "source": "Vue-After-Free",
        "path": str(path),
        "commit": git_head(path),
        "versions_mentioned": versions,
        "findings": [
            {"name": "userland_layer", "status": "PORTABLE", "evidence": "userland.ts discovers JSC/libc/libkernel bases conceptually."} if has_userland else {"name": "userland_layer", "status": "ABSENT"},
            {"name": "kernel_layer", "status": "STRUCTURAL", "evidence": "kernel.ts separates sysent[661], kernel offsets and patch verification."} if has_kernel else {"name": "kernel_layer", "status": "ABSENT"},
            {"name": "13_52_support", "status": "UNVERIFIED", "evidence": "source is not a same-build 13.52 WebKit/kernel artifact."},
        ],
    }


def scan_loader(path: Path) -> dict[str, Any]:
    magic = read_text(path / "linux/magic.h")
    start = magic.find("#elif defined PS4_13_52")
    block = magic[start:] if start >= 0 else ""
    block = block.split("#endif", 1)[0]
    defines = dict(re.findall(r"#define\s+(kern_off_[A-Za-z0-9_]+)\s+(0x[0-9A-Fa-f]+)", block))
    fw_table = read_text(path / "linux/fw_offsets.h")
    has_table = "{ 1352," in fw_table
    findings = [
        {"name": "13_52_offset_block", "status": "STRUCTURAL", "evidence": "tagged PS4_13_52 block in linux/magic.h; source-level claim, no same-build kernel bytes."} if defines else {"name": "13_52_offset_block", "status": "ABSENT"},
        {"name": "13_52_firmware_dispatch", "status": "STRUCTURAL", "evidence": "fw_offsets.h contains normalized firmware 1352 entry."} if has_table else {"name": "13_52_firmware_dispatch", "status": "ABSENT"},
        {"name": "kernel_bytes", "status": "ABSENT", "evidence": "repository source/loader tables do not include a retail kernel image."},
    ]
    return {"source": "ps4-linux-loader", "path": str(path), "commit": git_head(path), "firmware": "13.52", "offsets": defines, "findings": findings}


def scan_anchor(root: Path) -> dict[str, Any]:
    manifest_path = root / "tools/libkernel_1352_manifest.json"
    manifest = json.loads(read_text(manifest_path)) if manifest_path.is_file() else {}
    artifact = root / manifest.get("artifact", {}).get("path", "")
    actual = sha256(artifact)
    expected = manifest.get("artifact", {}).get("sha256")
    status = "CONFIRMED_1352" if actual and actual == expected else "UNVERIFIED"
    chunks = []
    for item in manifest.get("chunks", []):
        p = root / item["path"]
        chunks.append({"path": item["path"], "size": p.stat().st_size if p.is_file() else None, "sha256": sha256(p), "expected": item.get("sha256")})
    return {"source": "firmware-lab", "artifact": str(artifact), "sha256": actual, "expected_sha256": expected, "status": status, "chunks": chunks, "findings": [{"name": "libkernel_sys_anchor", "status": status, "evidence": "manifest hash and local artifact match." if status == "CONFIRMED_1352" else "manifest/artifact mismatch or absent."}]}


def validate(node: Any) -> None:
    if isinstance(node, dict):
        if "status" in node and node["status"] not in ALLOWED:
            raise ValueError(f"invalid status: {node['status']}")
        for value in node.values():
            validate(value)
    elif isinstance(node, list):
        for value in node:
            validate(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab", type=Path, required=True)
    parser.add_argument("--psfree", type=Path, required=True)
    parser.add_argument("--cssfontface", type=Path, required=True)
    parser.add_argument("--vue", type=Path, required=True)
    parser.add_argument("--loader", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = {
        "target_firmware": "13.52",
        "rule": "Historical offsets never become CONFIRMED_1352 without same-build bytes.",
        "anchor": scan_anchor(args.lab),
        "sources": [scan_psfree(args.psfree), scan_css(args.cssfontface), scan_vue(args.vue), scan_loader(args.loader)],
    }
    validate(report)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
