#!/usr/bin/env python3
"""Real WPE MiniBrowser smoke test through the public WebDriver protocol."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.error
import urllib.request


def request(base: str, method: str, path: str, payload=None, timeout=30):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(base + path, data=data, method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode())


def call(base, sid, method, path, payload=None, timeout=30):
    obj = request(base, method, f"/session/{sid}{path}", payload, timeout)
    value = obj.get("value")
    if isinstance(value, dict) and value.get("error"):
        raise RuntimeError(value)
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--driver", required=True)
    ap.add_argument("--browser", required=True)
    ap.add_argument("--fixtures", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--port", type=int, default=9515)
    ns = ap.parse_args()
    fixtures = Path(ns.fixtures).resolve()
    result = {"schema": 1, "runtime": "WPE MiniBrowser WebDriver", "status": "BLOCKED", "version": None, "stages": [], "capabilities": {}, "fixture_validation": []}
    manifest_path = fixtures / "fixture-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest["fixtures"]:
            path = fixtures / item["file"]
            digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
            result["fixture_validation"].append({"id": item["id"], "file": str(path), "sha256": digest, "expected_sha256": item["sha256"], "status": "PASS" if digest == item["sha256"] else "FAIL"})
        if any(item["status"] != "PASS" for item in result["fixture_validation"]):
            result["error"] = "fixture manifest/hash validation failed"
            Path(ns.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
            print(json.dumps(result, indent=2, sort_keys=True))
            raise SystemExit(1)
    except Exception as exc:
        result["error"] = f"fixture validation error: {exc!r}"
        Path(ns.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        raise SystemExit(1)
    env = os.environ.copy()
    env["PATH"] = str(Path(ns.driver).resolve().parent) + os.pathsep + env.get("PATH", "")
    proc = subprocess.Popen([ns.driver, f"--port={ns.port}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    base = f"http://127.0.0.1:{ns.port}"
    sid = None
    try:
        for _ in range(60):
            try:
                if request(base, "GET", "/status", timeout=1).get("value", {}).get("ready"):
                    break
            except Exception:
                time.sleep(0.25)
        caps = {"capabilities": {"firstMatch": [{}], "alwaysMatch": {"browserName": "MiniBrowser", "pageLoadStrategy": "normal", "wpe:browserOptions": {"binary": str(Path(ns.browser).resolve()), "args": ["--automation", "--headless"]}}}}
        session = request(base, "POST", "/session", caps, timeout=45).get("value", {})
        sid = session.get("sessionId")
        if not sid:
            raise RuntimeError(session)
        result["status"] = "PASS_SESSION"
        result["version"] = session.get("capabilities", {}).get("browserVersion")
        p1 = (fixtures / "page1.html").as_uri(); p2 = (fixtures / "page2.html").as_uri(); p3 = (fixtures / "page3.html").as_uri()
        call(base, sid, "POST", "/url", {"url": p1})
        stage1 = call(base, sid, "POST", "/execute/sync", {"script": """
            const b = document.getElementById('action'); b.click();
            const input = document.getElementById('name'); input.value = 'ok';
            const c = document.getElementById('canvas'); const ctx = c.getContext('2d'); ctx.fillStyle = 'rgb(1,2,3)'; ctx.fillRect(0,0,1,1);
            return {dom: document.querySelectorAll('#content article').length === 2,
              flex: getComputedStyle(document.getElementById('flex')).display === 'flex',
              grid: getComputedStyle(document.getElementById('grid')).display === 'grid',
              js: b.dataset.clicked === 'yes' && document.getElementById('box').textContent === 'clicked',
              event: b.dataset.clicked === 'yes', form: input.checkValidity(),
              svg: document.querySelector('#vector rect').getAttribute('fill') === 'red',
              image: document.getElementById('image').complete,
              canvas: !!ctx && ctx.getImageData(0,0,1,1).data[0] === 1,
              storage: (localStorage.setItem('wpeSmoke','page1'), localStorage.getItem('wpeSmoke') === 'page1')};
        """, "args": []})
        result["stages"].append({"page": "page1", "result": stage1})
        if not all(stage1.values()): raise RuntimeError({"stage": "page1", "result": stage1})
        call(base, sid, "POST", "/url", {"url": p2})
        stage2 = call(base, sid, "POST", "/execute/sync", {"script": """
            const n = document.getElementById('nav'); n.dispatchEvent(new Event('custom')); return {
              page: window.page2Ready === true, dom: document.getElementById('destination').textContent === 'page2-ok',
              event: n.dataset.seen === 'yes', storage: localStorage.getItem('wpeSmoke') === 'page1', js: true};
        """, "args": []})
        result["stages"].append({"page": "page2", "result": stage2})
        if not all(stage2.values()): raise RuntimeError({"stage": "page2", "result": stage2})
        call(base, sid, "POST", "/url", {"url": p3})
        stage3 = call(base, sid, "POST", "/execute/sync", {"script": "return {page: window.page3Ready === true, dom: document.getElementById('final').textContent === 'final-page', history: history.length >= 2, js: document.body.dataset.final === 'yes'};", "args": []})
        result["stages"].append({"page": "page3", "result": stage3})
        if not all(stage3.values()): raise RuntimeError({"stage": "page3", "result": stage3})
        result["capabilities"] = {k: "PASS" for k in ("DOM", "CSS", "Flexbox", "Grid", "JavaScript", "events", "forms", "SVG", "images", "Canvas", "localStorage", "navigation", "history")}
        result["status"] = "PASS"
    except Exception as exc:
        result["status"] = "FAIL" if sid else "BLOCKED"
        result["error"] = repr(exc)
    finally:
        if sid:
            try: call(base, sid, "DELETE", "", timeout=10)
            except Exception: pass
        try: proc.terminate(); proc.wait(timeout=5)
        except Exception: proc.kill()
    Path(ns.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__": main()
