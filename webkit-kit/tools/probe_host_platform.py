#!/usr/bin/env python3
"""Read-only host capability probe; it never builds or starts WPE."""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import socket
import ssl
import subprocess
import tempfile


def pkg(name: str, env: dict[str, str]):
    try:
        p = subprocess.run(["pkg-config", "--modversion", name], text=True, capture_output=True, check=False, env=env)
        return {"status": "AVAILABLE" if p.returncode == 0 else "MISSING", "version": p.stdout.strip(), "stderr": p.stderr.strip()}
    except Exception as exc:
        return {"status": "UNKNOWN", "error": str(exc)}


def prefix_candidates(requested: str | None) -> list[pathlib.Path]:
    candidates = []
    for value in (requested, os.environ.get("WPE_PREFIX"), "/tmp/wpe-prefix"):
        if value and pathlib.Path(value) not in candidates:
            candidates.append(pathlib.Path(value))
    return candidates


def library_inventory(prefixes: list[pathlib.Path]) -> dict:
    result = {"libwpe": [], "wpebackend_fdo": []}
    for prefix in prefixes:
        for directory in (prefix / "lib", prefix / "lib" / "x86_64-linux-gnu"):
            if not directory.is_dir():
                continue
            result["libwpe"].extend(str(p) for p in sorted(directory.glob("libwpe-1.0.so*")))
            result["wpebackend_fdo"].extend(str(p) for p in sorted(directory.glob("libWPEBackend-fdo-1.0.so*")))
    for key in result:
        result[key] = sorted(set(result[key]))
    return result


def loopback_probe() -> dict:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        server.settimeout(1)
        port = server.getsockname()[1]
        client = socket.create_connection(("127.0.0.1", port), timeout=1)
        peer, _ = server.accept()
        client.sendall(b"wpe-host-loopback")
        data = peer.recv(64)
        client.close()
        peer.close()
        return {"status": "PASS" if data == b"wpe-host-loopback" else "FAIL", "scope": "loopback", "port": port}
    except OSError as exc:
        return {"status": "BLOCKED", "scope": "loopback", "detail": str(exc)}
    finally:
        server.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--network", action="store_true", help="probe loopback only; no external network")
    ap.add_argument("--wpe-prefix", help="WPE prefix containing lib/pkgconfig and libraries")
    ap.add_argument("--output")
    ns = ap.parse_args()

    prefixes = prefix_candidates(ns.wpe_prefix)
    pkg_paths = []
    for prefix in prefixes:
        for path in (prefix / "lib" / "pkgconfig", prefix / "lib" / "x86_64-linux-gnu" / "pkgconfig"):
            if path.is_dir():
                pkg_paths.append(str(path))
    env = os.environ.copy()
    if pkg_paths:
        env["PKG_CONFIG_PATH"] = ":".join(dict.fromkeys(pkg_paths + [env.get("PKG_CONFIG_PATH", "")]))

    result = {
        "schema": 2,
        "scope": "host-only",
        "wpe_runtime": "NOT_RUN",
        "wpe_prefix_candidates": [str(p) for p in prefixes],
        "pkg_config_path": env.get("PKG_CONFIG_PATH", ""),
        "capabilities": {},
    }
    with tempfile.TemporaryDirectory(prefix="wpe-host-probe-") as d:
        p = pathlib.Path(d) / "storage"
        p.write_text("probe", encoding="utf-8")
        result["capabilities"]["filesystem"] = {"status": "PASS" if p.read_text(encoding="utf-8") == "probe" else "FAIL", "tempdir": d}
    result["capabilities"]["storage"] = {"status": "PASS", "note": "filesystem-backed host probe; not WebCore localStorage"}
    try:
        context = ssl.create_default_context()
        result["capabilities"]["tls"] = {"status": "PASS", "openssl": ssl.OPENSSL_VERSION, "default_context": bool(context), "scope": "host-library-init-only"}
    except Exception as exc:
        result["capabilities"]["tls"] = {"status": "BLOCKED", "detail": str(exc)}
    result["capabilities"]["fonts"] = {"status": "AVAILABLE" if shutil.which("fc-list") else "MISSING", "tool": shutil.which("fc-list")}
    result["capabilities"]["networking"] = loopback_probe() if ns.network else {"status": "NOT_RUN", "note": "external network intentionally disabled; use --network for loopback only"}
    result["capabilities"]["input"] = {"status": "AVAILABLE", "note": "WPE input injection remains backend-dependent; host queue is tested by offscreen-core"}
    result["capabilities"]["pkg_config"] = {name: pkg(name, env) for name in ("glib-2.0", "cairo", "fontconfig", "libsoup-3.0", "wpe-1.0", "wpe-webkit-2.0")}
    result["capabilities"]["wpe_libraries"] = library_inventory(prefixes)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if ns.output:
        pathlib.Path(ns.output).write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
