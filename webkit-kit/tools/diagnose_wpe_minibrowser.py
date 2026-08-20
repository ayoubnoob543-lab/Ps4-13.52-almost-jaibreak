#!/usr/bin/env python3
"""Read-only diagnostic for an existing WPE MiniBrowser executable.

This tool never builds, cleans, patches, or launches a browser unless --launch is
explicitly provided. A successful ELF/ldd inspection is not a runtime PASS.
"""
from __future__ import annotations
import argparse, json, os, pathlib, shutil, subprocess, sys, time


def run(cmd: list[str], timeout: float = 10) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, check=False)
        return {"command": cmd, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as exc:
        return {"command": cmd, "error": str(exc)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("binary", nargs="?", help="path or PATH name of MiniBrowser")
    ap.add_argument("--output", help="JSON output path")
    ap.add_argument("--launch", action="store_true", help="perform a bounded startup probe")
    ap.add_argument("--url", default="about:blank")
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--bundle-root", help="official extracted bundle root; inspect bin/ executables and README")
    ns = ap.parse_args()
    result = {
        "schema": 1,
        "tool": "diagnose_wpe_minibrowser.py",
        "status": "NOT_RUN",
        "reason": None,
        "binary": ns.binary,
        "elf": {},
        "dependencies": {},
        "symbols": {},
        "wpe_environment": {},
        "startup": None,
        "bundle": {},
    }
    if not ns.binary:
        result["reason"] = "no MiniBrowser path supplied"
    else:
        resolved = shutil.which(ns.binary) if os.path.basename(ns.binary) == ns.binary else ns.binary
        path = pathlib.Path(resolved) if resolved else pathlib.Path(ns.binary)
        result["binary"] = str(path.resolve())
        if not path.is_file() or not os.access(path, os.X_OK):
            result["reason"] = "MiniBrowser is absent or not executable"
        else:
            result["elf"] = run(["file", "-L", str(path)])
            result["dependencies"] = run(["ldd", str(path)])
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
            result["wpe_environment"]["backend_fdo_library"] = shutil.which("WPEBackend-fdo") or None
            result["wpe_environment"]["pkg_config_wpe"] = run(["pkg-config", "--modversion", "wpe-webkit-2.0"])
            result["wpe_environment"]["pkg_config_libwpe"] = run(["pkg-config", "--modversion", "wpe-1.0"])
            if ns.launch:
                started = time.time()
                try:
                    p = subprocess.run([str(path), ns.url], text=True, capture_output=True, timeout=ns.timeout, check=False)
                    result["startup"] = {"returncode": p.returncode, "elapsed_s": round(time.time()-started, 3), "stdout_tail": p.stdout[-4000:], "stderr_tail": p.stderr[-4000:]}
                    result["status"] = "STARTED_ONLY"
                    result["reason"] = "bounded startup probe completed; this is not a functional HTML capability PASS"
                except subprocess.TimeoutExpired as exc:
                    result["startup"] = {"status": "TIMEOUT", "stdout_tail": (exc.stdout or "")[-4000:], "stderr_tail": (exc.stderr or "")[-4000:]}
                    result["status"] = "BLOCKED"
                    result["reason"] = "startup probe timed out"
            else:
                result["status"] = "INSPECTED_ONLY"
                result["reason"] = "ELF, ldd, symbols and environment inspected; runtime not launched"
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if ns.output:
        pathlib.Path(ns.output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] in {"NOT_RUN", "INSPECTED_ONLY", "STARTED_ONLY"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
