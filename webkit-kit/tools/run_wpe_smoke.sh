#!/usr/bin/env bash
set -u

# Safe WPE smoke harness. It never builds, cleans, or edits a build directory.
# Functional PASS requires explicit output assertions supplied by the MiniBrowser wrapper.

usage() {
  printf 'Usage: %s --minibrowser PATH [--fixture-dir DIR] [--output FILE] [--webdriver-driver PATH --webdriver-browser PATH]\n' "$0"
  printf 'Environment: WPE_SMOKE_TIMEOUT (default 15), WPE_MINIBROWSER_ARGS (optional)\n'
}

MINIBROWSER=""
FIXTURE_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../homebrew/fixtures" && pwd)"
OUTPUT=""
WEBDRIVER_DRIVER=""
WEBDRIVER_BROWSER=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --minibrowser) MINIBROWSER=${2-}; shift 2 ;;
    --fixture-dir) FIXTURE_DIR=${2-}; shift 2 ;;
    --output) OUTPUT=${2-}; shift 2 ;;
    --webdriver-driver) WEBDRIVER_DRIVER=${2-}; shift 2 ;;
    --webdriver-browser) WEBDRIVER_BROWSER=${2-}; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$OUTPUT" ]; then
  OUTPUT="$(pwd)/wpe-smoke-$(date -u +%Y%m%dT%H%M%SZ).json"
fi
mkdir -p "$(dirname -- "$OUTPUT")"
MANIFEST="$FIXTURE_DIR/fixture-manifest.json"
TIMEOUT_SECS="${WPE_SMOKE_TIMEOUT:-15}"

if [ -n "$WEBDRIVER_DRIVER" ] || [ -n "$WEBDRIVER_BROWSER" ]; then
  if [ -z "$WEBDRIVER_DRIVER" ] || [ -z "$WEBDRIVER_BROWSER" ]; then
    printf '{"status":"BLOCKED","reason":"both --webdriver-driver and --webdriver-browser are required"}\\n' > "$OUTPUT"
    cat "$OUTPUT"
    exit 2
  fi
  python3 "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/run_wpe_webdriver_smoke.py" --driver "$WEBDRIVER_DRIVER" --browser "$WEBDRIVER_BROWSER" --fixtures "$FIXTURE_DIR" --output "$OUTPUT"
  exit $?
fi

python3 - "$MINIBROWSER" "$FIXTURE_DIR" "$MANIFEST" "$OUTPUT" "$TIMEOUT_SECS" <<'PY'
import hashlib, json, os, pathlib, shutil, subprocess, sys, time

binary, fixture_dir, manifest_path, output_path, timeout_s = sys.argv[1:]
result = {
    "schema": 1,
    "engine": "WPE WebKit 2.52.6",
    "backend": "WPEBackend-fdo 1.16.1",
    "status": "NOT_RUN",
    "reason": None,
    "fixture_validation": [],
    "sequence": [],
    "capabilities": {},
    "runtime": {"binary": binary, "ldd": [], "wpe_env": {}, "display": None},
    "process_runs": []
}

def finish():
    pathlib.Path(output_path).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

try:
    manifest = json.loads(pathlib.Path(manifest_path).read_text(encoding="utf-8"))
except Exception as exc:
    result["status"] = "BLOCKED"
    result["reason"] = f"invalid fixture manifest: {exc}"
    finish(); raise SystemExit(1)

for fixture in manifest["fixtures"]:
    path = pathlib.Path(fixture_dir) / fixture["file"]
    item = {"id": fixture["id"], "file": str(path), "exists": path.is_file(), "sha256": None, "expected_sha256": fixture["sha256"], "status": "PASS"}
    if path.is_file():
        item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        if item["sha256"] != item["expected_sha256"]:
            item["status"] = "FAIL"
    else:
        item["status"] = "FAIL"
    result["fixture_validation"].append(item)

if any(x["status"] != "PASS" for x in result["fixture_validation"]):
    result["status"] = "BLOCKED"
    result["reason"] = "fixture hash or presence validation failed"
    finish(); raise SystemExit(1)

if not binary:
    result["reason"] = "MiniBrowser path was not supplied; WPE smoke is intentionally NOT_RUN"
    finish(); raise SystemExit(0)

resolved = shutil.which(binary) if os.path.basename(binary) == binary else binary
if not resolved or not pathlib.Path(resolved).is_file() or not os.access(resolved, os.X_OK):
    result["reason"] = "MiniBrowser does not exist or is not executable; WPE smoke is NOT_RUN"
    finish(); raise SystemExit(0)

result["runtime"]["binary"] = str(pathlib.Path(resolved).resolve())
try:
    result["runtime"]["ldd"] = subprocess.run(["ldd", resolved], text=True, capture_output=True, check=False, timeout=5).stdout.splitlines()
except Exception as exc:
    result["runtime"]["ldd_error"] = str(exc)
for key in ("WAYLAND_DISPLAY", "DISPLAY", "WPE_BACKEND", "WPE_RENDERER", "LIBGL_ALWAYS_SOFTWARE"):
    if key in os.environ:
        result["runtime"]["wpe_env"][key] = os.environ[key]
result["runtime"]["display"] = os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY")

extra = os.environ.get("WPE_MINIBROWSER_ARGS", "").split()
for fixture in manifest["fixtures"]:
    url = (pathlib.Path(fixture_dir) / fixture["file"]).resolve().as_uri()
    cmd = [resolved, *extra, url]
    started = time.time()
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=float(timeout_s), check=False)
        run = {"id": fixture["id"], "url": url, "returncode": proc.returncode, "elapsed_s": round(time.time()-started, 3), "stdout_tail": proc.stdout[-4000:], "stderr_tail": proc.stderr[-4000:]}
        result["process_runs"].append(run)
        result["sequence"].append(fixture["id"])
    except subprocess.TimeoutExpired as exc:
        result["process_runs"].append({"id": fixture["id"], "url": url, "status": "TIMEOUT", "stdout_tail": (exc.stdout or "")[-4000:], "stderr_tail": (exc.stderr or "")[-4000:]})
        result["status"] = "BLOCKED"
        result["reason"] = "MiniBrowser started but timed out; no functional assertion was inferred"
        finish(); raise SystemExit(1)

result["status"] = "STARTED_ONLY"
result["reason"] = "MiniBrowser was invoked for all fixtures; capability PASS requires explicit assertions in stdout or a dedicated automation wrapper"
finish()
PY
