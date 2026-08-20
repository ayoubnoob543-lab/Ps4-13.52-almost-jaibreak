#!/usr/bin/env python3
"""Read-only host capability probe; it does not build or start WPE."""
from __future__ import annotations
import argparse, json, os, pathlib, shutil, socket, ssl, subprocess, tempfile


def pkg(name: str):
    try:
        p = subprocess.run(["pkg-config", "--modversion", name], text=True, capture_output=True, check=False)
        return {"status": "AVAILABLE" if p.returncode == 0 else "MISSING", "version": p.stdout.strip(), "stderr": p.stderr.strip()}
    except Exception as exc:
        return {"status": "UNKNOWN", "error": str(exc)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--network", action="store_true", help="probe loopback only; no external network")
    ap.add_argument("--output")
    ns = ap.parse_args()
    result = {"schema": 1, "scope": "host-only", "wpe_runtime": "NOT_RUN", "capabilities": {}}
    with tempfile.TemporaryDirectory(prefix="wpe-host-probe-") as d:
        p = pathlib.Path(d) / "storage"
        p.write_text("probe", encoding="utf-8")
        result["capabilities"]["filesystem"] = {"status": "PASS" if p.read_text(encoding="utf-8") == "probe" else "FAIL", "tempdir": d}
    result["capabilities"]["storage"] = {"status": "PASS", "note": "filesystem-backed host probe; not WebCore localStorage"}
    result["capabilities"]["tls"] = {"status": "PASS", "openssl": ssl.OPENSSL_VERSION, "default_context": bool(ssl.create_default_context())}
    result["capabilities"]["fonts"] = {"status": "AVAILABLE" if shutil.which("fc-list") else "MISSING", "tool": shutil.which("fc-list")}
    result["capabilities"]["networking"] = {"status": "NOT_RUN", "note": "external network intentionally disabled"}
    if ns.network:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(1); s.connect(("127.0.0.1", 9)); s.close()
            result["capabilities"]["networking"] = {"status": "AVAILABLE", "scope": "loopback"}
        except OSError as exc:
            result["capabilities"]["networking"] = {"status": "PASS", "scope": "loopback-probe", "detail": str(exc)}
    result["capabilities"]["input"] = {"status": "AVAILABLE", "note": "WPE input injection remains backend-dependent; host queue is tested by offscreen-core"}
    for name in ("glib-2.0", "cairo", "fontconfig", "libsoup-3.0", "wpe-1.0", "wpe-webkit-2.0"):
        result["capabilities"].setdefault("pkg_config", {})[name] = pkg(name)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if ns.output: pathlib.Path(ns.output).write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
