#!/usr/bin/env python3
"""Run the WPE page1->page2->page3 smoke without assuming a GUI.

The runner never builds or edits a WPE build. A functional result requires the
MiniBrowser (or its wrapper) to emit one line of the form:
WPE_SMOKE_ASSERTIONS={"page1": {...}, "page2": {...}, "page3": {...}}
Without that explicit protocol the result is BLOCKED, never PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shlex
import shutil
import subprocess
import time


ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "homebrew" / "fixtures"
DEFAULT_SEARCH = [pathlib.Path("/tmp/wpewebkit-2.52.6-build/bin/MiniBrowser"), pathlib.Path("/tmp/wpe-bundle/bin/MiniBrowser"), pathlib.Path("/home/ubuntu/wpe-bundle/bin/MiniBrowser")]


def run(cmd: list[str], env: dict[str, str] | None = None, timeout: float = 10) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, check=False, env=env)
        return {"command": cmd, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as exc:
        return {"command": cmd, "error": str(exc)}


def locate(requested: str | None) -> pathlib.Path | None:
    if requested:
        path = pathlib.Path(shutil.which(requested) or requested)
        return path if path.is_file() else None
    for candidate in DEFAULT_SEARCH:
        if candidate.is_file():
            return candidate
    return next((pathlib.Path(directory) / "MiniBrowser" for directory in os.environ.get("PATH", "").split(os.pathsep) if (pathlib.Path(directory) / "MiniBrowser").is_file()), None)


def libs(prefix: pathlib.Path) -> dict[str, list[str]]:
    result = {"libWPEWebKit": [], "libwpe": [], "WPEBackend-fdo": []}
    for root in (prefix / "lib", prefix / "lib" / "x86_64-linux-gnu"):
        for key, pattern in (("libWPEWebKit", "libWPEWebKit-2.0.so*"), ("libwpe", "libwpe-1.0.so*"), ("WPEBackend-fdo", "libWPEBackend-fdo-1.0.so*")):
            result[key].extend(str(path) for path in root.glob(pattern))
    return {key: sorted(set(value)) for key, value in result.items()}


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_assertions(text: str) -> tuple[dict | None, str | None]:
    prefix = "WPE_SMOKE_ASSERTIONS="
    for line in text.splitlines():
        if line.startswith(prefix):
            raw = line[len(prefix):]
            try:
                value = json.loads(raw)
                return value, None
            except json.JSONDecodeError as exc:
                return None, f"invalid WPE_SMOKE_ASSERTIONS JSON: {exc}"
    return None, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minibrowser")
    parser.add_argument("--prefix", default=os.environ.get("WPE_PREFIX", "/tmp/wpe-prefix"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--extra-args", default=os.environ.get("WPE_MINIBROWSER_ARGS", ""))
    args = parser.parse_args()
    manifest = json.loads((FIXTURES / "fixture-manifest.json").read_text(encoding="utf-8"))
    expected = json.loads((FIXTURES / "wpe-expected-assertions.json").read_text(encoding="utf-8"))
    result = {
        "schema": 2,
        "engine": manifest["engine"],
        "backend": manifest["backend"],
        "status": "NOT_RUN",
        "reason": None,
        "headless_requested": args.headless,
        "sequence_expected": manifest["expected_sequence"],
        "fixtures": [],
        "expected": expected,
        "actual_assertions": None,
        "comparison": None,
        "runtime": {"prefix": str(pathlib.Path(args.prefix).resolve()), "binary": None, "architecture": None, "binary_sha256": None, "libraries": libs(pathlib.Path(args.prefix)), "ldd": [], "environment": {}},
        "process": None,
    }
    for item in manifest["fixtures"]:
        path = FIXTURES / item["file"]
        actual = sha256(path) if path.is_file() else None
        result["fixtures"].append({"id": item["id"], "path": str(path), "expected_sha256": item["sha256"], "sha256": actual, "status": "PASS" if actual == item["sha256"] else "FAIL"})
    if any(item["status"] != "PASS" for item in result["fixtures"]):
        result["status"] = "BLOCKED"
        result["reason"] = "fixture validation failed"
    else:
        binary = locate(args.minibrowser)
        if not binary:
            result["reason"] = "MiniBrowser not found; WPE smoke is NOT_RUN"
        else:
            binary = binary.resolve()
            result["runtime"]["binary"] = str(binary)
            result["runtime"]["binary_sha256"] = sha256(binary)
            result["runtime"]["architecture"] = run(["file", "-L", str(binary)])
            env = os.environ.copy()
            prefix = pathlib.Path(args.prefix)
            lib_dirs = [str(prefix / "lib"), str(prefix / "lib" / "x86_64-linux-gnu")]
            env["LD_LIBRARY_PATH"] = ":".join(dict.fromkeys([path for path in lib_dirs if pathlib.Path(path).is_dir()] + [env.get("LD_LIBRARY_PATH", "")]))
            if args.headless:
                env.setdefault("WPE_BACKEND", "fdo")
                env.setdefault("WPE_RENDERER", "software")
                env.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
            for key in ("WPE_BACKEND", "WPE_RENDERER", "LIBGL_ALWAYS_SOFTWARE", "WAYLAND_DISPLAY", "DISPLAY", "XDG_RUNTIME_DIR"):
                if key in env:
                    result["runtime"]["environment"][key] = env[key]
            result["runtime"]["ldd"] = run(["ldd", str(binary)], env=env)
            ldd_text = result["runtime"]["ldd"].get("stdout", "")
            missing = [line.strip() for line in ldd_text.splitlines() if "not found" in line]
            if missing:
                result["status"] = "BLOCKED"
                result["reason"] = "unresolved dynamic dependencies"
                result["runtime"]["missing_dependencies"] = missing
            else:
                command = [str(binary), *shlex.split(args.extra_args), (FIXTURES / "page1.html").resolve().as_uri()]
                started = time.monotonic()
                try:
                    process = subprocess.run(command, text=True, capture_output=True, timeout=args.timeout, check=False, env=env)
                    result["process"] = {"command": command, "returncode": process.returncode, "elapsed_s": round(time.monotonic() - started, 3), "stdout_tail": process.stdout[-12000:], "stderr_tail": process.stderr[-12000:]}
                    assertions, parse_error = extract_assertions(process.stdout + "\n" + process.stderr)
                    if parse_error:
                        result["status"] = "FAIL"
                        result["reason"] = parse_error
                    elif assertions is None:
                        result["status"] = "BLOCKED"
                        result["reason"] = "process completed without explicit WPE_SMOKE_ASSERTIONS protocol"
                    elif process.returncode != 0:
                        result["status"] = "FAIL"
                        result["reason"] = f"MiniBrowser returned {process.returncode}"
                    else:
                        result["actual_assertions"] = assertions
                        result["status"] = "PASS"
                        result["reason"] = "explicit assertions protocol received; compare_wpe_smoke.py must validate it"
                except subprocess.TimeoutExpired as exc:
                    result["status"] = "BLOCKED"
                    result["reason"] = "MiniBrowser timed out"
                    result["process"] = {"status": "TIMEOUT", "stdout_tail": (exc.stdout or "")[-12000:], "stderr_tail": (exc.stderr or "")[-12000:]}
    pathlib.Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in {"PASS", "NOT_RUN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
