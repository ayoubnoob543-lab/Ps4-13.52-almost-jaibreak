#!/usr/bin/env python3
"""Static probe for the historical PS4OSSCode WebKit build.

This tool does not compile or execute source from the corpus. It reports the
source commit, expected build files, public ports, host tools, and explicit
missing prerequisites. It never treats a PS4/Orbis port as a host build.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


TOOLS = ["cmake", "ninja", "bison", "flex", "gperf", "perl", "python", "ruby"]
REQUIRED_FILES = [
    "CMakeLists.txt",
    "Source/CMakeLists.txt",
    "Source/JavaScriptCore/CMakeLists.txt",
    "Source/WTF/CMakeLists.txt",
    "Source/cmake/OptionsGTK.cmake",
    "Source/cmake/OptionsManx.cmake",
]
SOURCE_PREFIX = "WebKit-601-1300/WebKit-601-1300/"


def git_head(source: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def git_has_path(source: Path, relative: str) -> bool:
    try:
        subprocess.check_call(
            ["git", "-C", str(source), "cat-file", "-e", f"HEAD:{SOURCE_PREFIX}{relative}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", default=os.environ.get("OSS_SOURCE_DIR", ""))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    source = Path(args.source_dir).expanduser() if args.source_dir else None
    source_exists = bool(source and source.is_dir())
    result = {
        "schema": "historical-oss-build-probe/v1",
        "source_dir": str(source) if source else None,
        "source_exists": source_exists,
        "git_head": git_head(source) if source_exists else None,
        "required_files": {},
        "git_required_files": {},
        "tools": {},
        "ports": ["Efl", "GTK", "AppleWin", "WinCairo", "Mac", "Manx"],
        "host_port_available": False,
        "ps4_orbis_port_present": False,
        "blockers": [],
    }
    if source_exists:
        result["required_files"] = {
            item: (source / SOURCE_PREFIX / item).is_file() for item in REQUIRED_FILES
        }
        result["git_required_files"] = {
            item: git_has_path(source, item) for item in REQUIRED_FILES
        }
        result["ps4_orbis_port_present"] = result["git_required_files"].get(
            "Source/cmake/OptionsManx.cmake", False
        )
    else:
        result["blockers"].append("OSS_SOURCE_DIR_NOT_AVAILABLE")

    for tool in TOOLS:
        result["tools"][tool] = shutil.which(tool)

    for tool in TOOLS:
        if not result["tools"][tool]:
            result["blockers"].append(f"MISSING_TOOL_{tool.upper()}")

    if not result["git_required_files"].get("Source/cmake/OptionsGTK.cmake", False):
        result["blockers"].append("GTK_PORT_FILES_MISSING_FROM_GIT")
    elif not result["required_files"].get("Source/cmake/OptionsGTK.cmake", False):
        result["blockers"].append("GTK_PORT_REQUIRES_ARCHIVE_CHECKOUT")

    if not result["git_required_files"].get("Source/cmake/OptionsManx.cmake", False):
        result["blockers"].append("MANX_PORT_FILES_MISSING_FROM_GIT")
    elif not result["required_files"].get("Source/cmake/OptionsManx.cmake", False):
        result["blockers"].append("MANX_PORT_REQUIRES_ARCHIVE_CHECKOUT")

    if result["ps4_orbis_port_present"]:
        result["blockers"].extend([
            "MANX_PORT_REQUIRES_ORBIS_FLAG",
            "MANX_PORT_REQUIRES_PUBLIC_ORBIS_HEADERS_AND_LIBS",
            "MANX_PORT_REQUIRES_PLATFORM_GRAPHICS_DEPENDENCIES",
        ])

    result["host_port_available"] = bool(
        source_exists
        and all(result["required_files"].values())
        and all(result["tools"].get(tool) for tool in TOOLS)
    )
    result["status"] = "HOST_PORT_CANDIDATE" if result["host_port_available"] else "HOST_BUILD_BLOCKED"

    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
