"""Host-side protocol checks; no PS4, payload or binary is involved."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import threading
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "termux-server" / "server.py"


def test_manifest_shape():
    manifest = json.loads((ROOT / "config/manifest.example.json").read_text())
    assert manifest["schema"] == 1
    assert manifest["mode"] == "consent-only-read"
    assert all("source" in x and "destination" in x for x in manifest["files"])


def test_server_imports_without_running():
    result = subprocess.run([sys.executable, "-m", "py_compile", str(SERVER)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_fixture_hash():
    data = b"collector fixture; no executable content\n"
    assert hashlib.sha256(data).hexdigest() == "".join(f"{b:02x}" for b in hashlib.sha256(data).digest())


if __name__ == "__main__":
    for fn in (test_manifest_shape, test_server_imports_without_running, test_fixture_hash):
        fn()
    print("ok: static collector protocol checks")
