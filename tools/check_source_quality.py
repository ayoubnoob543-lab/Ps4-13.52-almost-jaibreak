#!/usr/bin/env python3
"""Static quality checks for the repository's non-operational research helpers."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []


def require(path: Path, pattern: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if not re.search(pattern, text, re.MULTILINE):
        errors.append(f"{path.relative_to(ROOT)}: missing {label}")


def forbid(path: Path, pattern: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if re.search(pattern, text, re.MULTILINE):
        errors.append(f"{path.relative_to(ROOT)}: forbidden {label}")


build = ROOT / "build.sh"
subprocess.run(["bash", "-n", str(build)], check=True)
require(build, r"PRX_FILES=\(\s*", "PRX_FILES array")
require(build, r'for prx in "\$\{PRX_FILES\[@\]\}"', "array-safe plugin iteration")
require(build, r"curl --fail", "curl failure checking")
require(build, r"unzip -q", "quiet unzip invocation")

js = ROOT / "jordy_stage2.js"
subprocess.run(["node", "--check", str(js)], check=True)
require(js, r"function toAddress\(value\)", "BigInt address conversion helper")
require(js, r"return lo \| \(hi << 32n\)", "BigInt read64")
require(js, r"INCOMPLETE: execution pivot", "explicit incomplete execution marker")
forbid(js, r"return 0;\s*//\s*placeholder", "numeric placeholder return")
forbid(js, r"Math\.floor\(addr / 0x100000000\)", "Number-based 64-bit address split")

java = ROOT / "src/org/bdj/SuidScanner.java"
require(java, r"nread > DENTS_BUF_SIZE", "getdents upper bound")
require(java, r"reclen < DIRENT_HEADER_SIZE", "getdents record-length lower bound")
require(java, r"namlen > nameCapacity", "getdents name bound")
require(java, r"STAT_LAYOUT = .*unverified", "stat layout qualification")
require(java, r"written != data\.length\(\)", "write return validation")
require(java, r"stat failed", "stat error reporting")

canonical = ROOT / "kpayload/source/offsets/1304.c"
legacy = ROOT / "1304.c"
require(legacy, r"Compatibility wrapper", "legacy wrapper marker")
require(legacy, r"kpayload/source/offsets/1304\.c", "canonical 1304 source reference")
require(canonical, r"PLACEHOLDER / UNVERIFIED", "1304 placeholder qualification")
require(canonical, r"0xDEADC0DE", "placeholder value preservation")

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)

print("source_quality=PASS")
print("shell=PASS")
print("javascript=PASS")
print("java_static=PASS")
print("offset_source_integrity=PASS")
