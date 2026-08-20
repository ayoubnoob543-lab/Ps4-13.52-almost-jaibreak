#!/usr/bin/env bash
set -u

# Runtime decision gate. It never builds WebKit/WPE and never touches an external build tree.
# WPE is authoritative when a MiniBrowser path is provided; GTK is only a clearly separate fallback.
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUT=${1:-"$(pwd)/wpe-runtime-matrix.json"}
MINIBROWSER=${WPE_MINIBROWSER:-}
WPE_JSON="$(dirname -- "$OUT")/wpe-smoke.json"
GTK_OUTPUT="$ROOT/homebrew/build/host/modern-webkitgtk-output.txt"

if [ -n "$MINIBROWSER" ]; then
  "$ROOT/tools/run_wpe_smoke.sh" --minibrowser "$MINIBROWSER" --output "$WPE_JSON" || true
fi

python3 - "$OUT" "$MINIBROWSER" "$WPE_JSON" "$GTK_OUTPUT" <<'PY'
import json, pathlib, sys, time
out, minibrowser, wpe_json, gtk_output = sys.argv[1:]
result = {
  "schema": 1,
  "policy": "WPE is authoritative; GTK is fallback only",
  "wpe": {"status": "NOT_RUN", "result_file": wpe_json},
  "gtk_fallback": {"status": "NOT_RUN", "result_file": gtk_output},
  "comparison": "NOT_RUN"
}
if minibrowser:
    result["wpe"]["requested"] = True
else:
    result["wpe"]["reason"] = "WPE_MINIBROWSER not set; no WPE result is inferred"
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

