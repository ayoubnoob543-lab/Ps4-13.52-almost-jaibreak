#!/usr/bin/env python3
"""Read-only diagnostic for an existing WPE MiniBrowser executable.

This tool never builds, cleans, patches, or launches a browser unless --launch
is explicitly provided. ELF/ldd inspection is not a runtime PASS.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import time


SEARCH_ROOTS = [
    pathlib.Path("/tmp/wpewebkit-2.52.6-build/bin"),
    pathlib.Path("/tmp/wpe-bundle/bin"),
    pathlib.Path("/home/ubuntu/wpe-bundle/bin"),
]


def run(cmd: list[str], env: dict[str, str] | None = None, timeout: float = 10) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, check=False, env=env)
        return {"command": cmd, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as exc:
        return {"command": cmd, "error": str(exc)}


def locate_binary(requested: str | None) -> pathlib.Path | None:
    if requested:
        resolved = shutil.which(requested) if os.path.basename(requested) == requested else requested
        path = pathlib.Path(resolved) if resolved else pathlib.Path(requested)
        return path if path.is_file() else None
    for root in SEARCH_ROOTS:
        candidate = root / "MiniBrowser"
        if candidate.is_file():
            return candidate
    for path in map(pathlib.Path, os.environ.get("PATH", "").split(os.pathsep)):
        candidate = path / "MiniBrowser"
        if candidate.is_file():
            return candidate
    return None


def prefix_dirs(requested: str | None, binary: pathlib.Path | None) -> list[pathlib.Path]:
    values = [requested, os.environ.get("WPE_PREFIX"), "/tmp/wpe-prefix"]
    if binary:
        values.extend([str(binary.parent.parent), str(binary.parent.parent / "lib")])
    result = []
    for value in values:
        if value:
            path = pathlib.Path(value)
            if path not in result:
                result.append(path)
    return result


def find_libraries(prefixes: list[pathlib.Path]) -> dict[str, list[str]]:
    patterns = {"libwpe": "libwpe-1.0.so*", "wpebackend_fdo": "libWPEBackend-fdo-1.0.so*", "webkit": "libWPEWebKit-2.0.so*"}
    result = {key: [] for key in patterns}
    for prefix in prefixes:
        roots = [prefix / "lib", prefix / "lib" / "x86_64-linux-gnu"]
        for root in roots:
            for key, pattern in patterns.items():
                result[key].extend(str(p) for p in root.glob(pattern))
    return {key: sorted(set(value)) for key, value in result.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("binary", nargs="?", help="path or PATH name of MiniBrowser; omitted means auto-locate")
    ap.add_argument("--prefix", help="bundle/WPE prefix used for library and pkg-config discovery")
    ap.add_argument("--output", help="JSON output path")
    ap.add_argument("--launch", action="store_true", help="perform a bounded startup probe")
    ap.add_argument("--url", default="about:blank")
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--bundle-root", help="official extracted bundle root; inspect bin/ executables and README")
    ns = ap.parse_args()
    result = {
        "schema": 2,
        "tool": "diagnose_wpe_minibrowser.py",
        "status": "NOT_RUN",
        "reason": None,
        "binary": ns.binary,
        "elf": {},
        "architecture": {},
        "dependencies": {},
        "symbols": {},
        "wpe_environment": {},
        "bundle_libraries": {},
        "startup": None,
        "bundle": {},
    }
    path = locate_binary(ns.binary)
    prefixes = prefix_dirs(ns.prefix, path)
    env = os.environ.copy()
    pkg_paths = []
    for prefix in prefixes:
        for candidate in (prefix / "lib" / "pkgconfig", prefix / "lib" / "x86_64-linux-gnu" / "pkgconfig"):
            if candidate.is_dir():
                pkg_paths.append(str(candidate))
    if pkg_paths:
        env["PKG_CONFIG_PATH"] = ":".join(dict.fromkeys(pkg_paths + [env.get("PKG_CONFIG_PATH", "")]))
    result["wpe_environment"]["pkg_config_path"] = env.get("PKG_CONFIG_PATH", "")
    result["bundle_libraries"] = find_libraries(prefixes)
    if not path:
        result["reason"] = "MiniBrowser not supplied and no candidate was found; WPE runtime is NOT_RUN"
    else:
        path = path.resolve()
        result["binary"] = str(path)
        result["elf"] = run(["file", "-L", str(path)])
        result["architecture"] = run(["readelf", "-h", str(path)])
        if not os.access(path, os.X_OK):
            result["reason"] = "MiniBrowser exists but is not executable"
            result["status"] = "BLOCKED"
        else:
            result["dependencies"] = run(["ldd", str(path)], env=env)
            if ns.bundle_root:
                bundle = pathlib.Path(ns.bundle_root).resolve()
                result["bundle"]["root"] = str(bundle)
                readme = bundle / "README.txt"
                if readme.is_file(): result["bundle"]["readme"] = readme.read_text(encoding="utf-8", errors="replace")
                for name in ("MiniBrowser", "WPEWebDriver"):
                    candidate = bundle / "bin" / name
                    if candidate.is_file():
                        result["bundle"].setdefault("executables", {})[name] = {"path": str(candidate), "file": run(["file", "-L", str(candidate)]), "sha256": run(["sha256sum", str(candidate)])}
                        result["bundle"]["executables"][name]["needed"] = run(["readelf", "--dynamic", "--wide", str(candidate)])
                loader = bundle / "lib" / "ld-linux-x86-64.so.2"
                result["bundle"]["loader"] = {"path": str(loader), "exists": loader.is_file()}
            result["symbols"]["dynamic"] = run(["readelf", "--dyn-syms", "--wide", str(path)])
            result["symbols"]["needed"] = run(["readelf", "--dynamic", "--wide", str(path)])
            for key in ("WPE_BACKEND", "WPE_RENDERER", "WAYLAND_DISPLAY", "DISPLAY", "LIBGL_ALWAYS_SOFTWARE", "XDG_RUNTIME_DIR"):
                if key in os.environ:
                    result["wpe_environment"][key] = os.environ[key]
            result["wpe_environment"]["backend_fdo_libraries"] = result["bundle_libraries"]["wpebackend_fdo"]
            result["wpe_environment"]["pkg_config_wpe"] = run(["pkg-config", "--modversion", "wpe-webkit-2.0"], env=env)
            result["wpe_environment"]["pkg_config_libwpe"] = run(["pkg-config", "--modversion", "wpe-1.0"], env=env)
            if ns.launch:
                started = time.time()
                try:
                    p = subprocess.run([str(path), ns.url], text=True, capture_output=True, timeout=ns.timeout, check=False, env=env)
                    result["startup"] = {"returncode": p.returncode, "elapsed_s": round(time.time() - started, 3), "stdout_tail": p.stdout[-4000:], "stderr_tail": p.stderr[-4000:]}
                    result["status"] = "STARTED_ONLY" if p.returncode == 0 else "BLOCKED"
                    result["reason"] = "bounded startup probe completed; this is not a functional HTML capability PASS" if p.returncode == 0 else "MiniBrowser exited non-zero during startup probe"
                except subprocess.TimeoutExpired as exc:
                    result["startup"] = {"status": "TIMEOUT", "stdout_tail": (exc.stdout or "")[-4000:], "stderr_tail": (exc.stderr or "")[-4000:]}
                    result["status"] = "BLOCKED"
                    result["reason"] = "startup probe timed out"
            else:
                result["status"] = "INSPECTED_ONLY"
                result["reason"] = "ELF, architecture, ldd, symbols, bundle and environment inspected; runtime not launched"
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if ns.output:
        pathlib.Path(ns.output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] in {"NOT_RUN", "INSPECTED_ONLY", "STARTED_ONLY"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
