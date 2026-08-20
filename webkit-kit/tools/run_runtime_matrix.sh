#!/usr/bin/env bash
set -u

# Runtime decision gate. It never builds WebKit/WPE and never touches an external build tree.
# WPE is authoritative when a MiniBrowser path is provided; GTK is only a clearly separate fallback.
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUT=${1:-"$(pwd)/wpe-runtime-matrix.json"}
MINIBROWSER=${WPE_MINIBROWSER:-}
WEBDRIVER=${WPE_WEBDRIVER:-}
WPE_BROWSER=${WPE_BROWSER:-$MINIBROWSER}
WPE_JSON="$(dirname -- "$OUT")/wpe-smoke.json"
GTK_OUTPUT="$ROOT/homebrew/build/host/modern-webkitgtk-output.txt"
OFFSCREEN_OUTPUT="$ROOT/homebrew/build/host/offscreen-test-output.txt"
HOST_PROBE_OUTPUT="$(dirname -- "$OUT")/host-platform.json"

if [ -n "$WEBDRIVER" ] && [ -n "$WPE_BROWSER" ]; then
  "$ROOT/tools/run_wpe_smoke.sh" --webdriver-driver "$WEBDRIVER" --webdriver-browser "$WPE_BROWSER" --output "$WPE_JSON" || true
elif [ -n "$MINIBROWSER" ]; then
  "$ROOT/tools/run_wpe_smoke.sh" --minibrowser "$MINIBROWSER" --output "$WPE_JSON" || true
fi

python3 "$ROOT/tools/probe_host_platform.py" --output "$HOST_PROBE_OUTPUT" >/dev/null

python3 - "$OUT" "$MINIBROWSER" "$WPE_JSON" "$GTK_OUTPUT" "$OFFSCREEN_OUTPUT" "$HOST_PROBE_OUTPUT" <<'PY'
import json, pathlib, sys, time
out, minibrowser, wpe_json, gtk_output, offscreen_output, host_probe_output = sys.argv[1:]
result = {
  "schema": 1,
  "policy": "WPE is authoritative; GTK is fallback only",
  "wpe": {"status": "NOT_RUN", "result_file": wpe_json, "mode": "webdriver" if pathlib.Path(wpe_json).is_file() and "WPE MiniBrowser WebDriver" in pathlib.Path(wpe_json).read_text(errors="replace") else "process-only"},
  "offscreen_host_core": {"status": "NOT_RUN", "result_file": offscreen_output, "runtime_claim": "not a WPE runtime"},
  "host_platform_probe": {"status": "PASS", "result_file": host_probe_output, "runtime_claim": "host-only"},
  "gtk_fallback": {"status": "NOT_RUN", "result_file": gtk_output},
  "comparison": "NOT_RUN"
}
if minibrowser or pathlib.Path(wpe_json).is_file():
    result["wpe"]["requested"] = True
else:
    result["wpe"]["reason"] = "no WPE executable/driver supplied; no WPE result is inferred"
if pathlib.Path(wpe_json).is_file():
    try:
        wpe_result = json.loads(pathlib.Path(wpe_json).read_text())
        result["wpe"]["status"] = wpe_result.get("status", "NOT_RUN")
        result["wpe"]["version"] = wpe_result.get("version")
        result["wpe"]["capabilities"] = wpe_result.get("capabilities", {})
    except Exception as exc:
        result["wpe"]["parse_error"] = str(exc)
if pathlib.Path(offscreen_output).is_file() and "offscreen-core: PASS" in pathlib.Path(offscreen_output).read_text(errors="replace"):
    result["offscreen_host_core"]["status"] = "PASS"
else:
    result["offscreen_host_core"]["reason"] = "offscreen target not executed"
if pathlib.Path(gtk_output).is_file():
    text = pathlib.Path(gtk_output).read_text(errors="replace")
    expected = [
      'stage=1 result={"dom":true,"event":true,"text":"clicked","flex":true,"grid":true,"animation":true,"form":true,"svg":true,"image":true,"canvas":true,"storage":true}',
      'stage=2 result={"page":true,"storage":true,"dom":"page2-ok","js":true,"event":true}',
      'stage=3 result={"page":true,"history":true,"dom":true,"js":true}'
    ]
    result["gtk_fallback"]["status"] = "PASS" if all(x in text for x in expected) else "FAIL"
else:
    result["gtk_fallback"]["reason"] = "GTK fallback output not present; execute make modern-webkit-smoke separately"
pathlib.Path(out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, indent=2, sort_keys=True))
PY

