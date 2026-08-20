#!/usr/bin/env bash
set -u

# Safe WPE smoke harness. It never builds, cleans, or edits a build directory.
# Functional PASS requires explicit output assertions supplied by a MiniBrowser wrapper.

usage() {
  printf 'Usage: %s [--minibrowser PATH] [--fixture-dir DIR] [--prefix DIR] [--output FILE]\n' "$0"
  printf 'Environment: WPE_SMOKE_TIMEOUT (default 15), WPE_MINIBROWSER_ARGS (optional)\n'
}

MINIBROWSER=""
FIXTURE_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../homebrew/fixtures" && pwd)"
PREFIX="${WPE_PREFIX:-/tmp/wpe-prefix}"
OUTPUT=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --minibrowser) MINIBROWSER=${2-}; shift 2 ;;
    --fixture-dir) FIXTURE_DIR=${2-}; shift 2 ;;
    --prefix) PREFIX=${2-}; shift 2 ;;
    --output) OUTPUT=${2-}; shift 2 ;;
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

python3 - "$MINIBROWSER" "$FIXTURE_DIR" "$MANIFEST" "$OUTPUT" "$TIMEOUT_SECS" "$PREFIX" <<'PY'
import hashlib, json, os, pathlib, shlex, shutil, subprocess, sys, time

binary, fixture_dir, manifest_path, output_path, timeout_s, prefix = sys.argv[1:]
result = {
    "schema": 2,
    "engine": "WPE WebKit 2.52.6",
    "backend": "WPEBackend-fdo 1.16.1",
    "status": "NOT_RUN",
    "reason": None,
    "fixture_validation": [],
    "sequence": [],
    "capabilities": {},
    "runtime": {"binary": binary, "ldd": [], "wpe_env": {}, "display": None, "preflight": {}},
    "process_runs": []
}

def finish():
    pathlib.Path(output_path).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

def files(prefix, patterns):
    roots = [pathlib.Path(prefix) / "lib", pathlib.Path(prefix) / "lib" / "x86_64-linux-gnu"]
    return sorted({str(p) for root in roots for pattern in patterns for p in root.glob(pattern)})

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

resolved = str(pathlib.Path(resolved).resolve())
result["runtime"]["binary"] = resolved
prefix_libs = files(prefix, ["libwpe-1.0.so*", "libWPEBackend-fdo-1.0.so*"])
result["runtime"]["preflight"]["prefix"] = str(pathlib.Path(prefix).resolve())
result["runtime"]["preflight"]["libwpe"] = [p for p in prefix_libs if "libwpe-1.0" in p]
result["runtime"]["preflight"]["wpebackend_fdo"] = [p for p in prefix_libs if "libWPEBackend-fdo-1.0" in p]
env = os.environ.copy()
lib_dirs = [str(pathlib.Path(prefix) / "lib"), str(pathlib.Path(prefix) / "lib" / "x86_64-linux-gnu")]
env["LD_LIBRARY_PATH"] = ":".join(dict.fromkeys([p for p in lib_dirs if pathlib.Path(p).is_dir()] + [env.get("LD_LIBRARY_PATH", "")]))
for key in ("WAYLAND_DISPLAY", "DISPLAY", "WPE_BACKEND", "WPE_RENDERER", "LIBGL_ALWAYS_SOFTWARE"):
    if key in env:
        result["runtime"]["wpe_env"][key] = env[key]
result["runtime"]["display"] = env.get("WAYLAND_DISPLAY") or env.get("DISPLAY")
result["runtime"]["preflight"]["display_status"] = "AVAILABLE" if result["runtime"]["display"] else "NOT_SET"
try:
    ldd = subprocess.run(["ldd", resolved], text=True, capture_output=True, timeout=5, check=False, env=env)
    result["runtime"]["ldd"] = ldd.stdout.splitlines()
    missing = [line.strip() for line in ldd.stdout.splitlines() if "not found" in line]
    result["runtime"]["preflight"]["missing_dependencies"] = missing
except Exception as exc:
    result["runtime"]["ldd_error"] = str(exc)
    result["runtime"]["preflight"]["missing_dependencies"] = [str(exc)]
if result["runtime"]["preflight"]["missing_dependencies"]:
    result["status"] = "BLOCKED"
    result["reason"] = "MiniBrowser has unresolved dynamic dependencies"
    finish(); raise SystemExit(1)

extra = shlex.split(os.environ.get("WPE_MINIBROWSER_ARGS", ""))
for fixture in manifest["fixtures"]:
    url = (pathlib.Path(fixture_dir) / fixture["file"]).resolve().as_uri()
    cmd = [resolved, *extra, url]
    started = time.time()
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=float(timeout_s), check=False, env=env)
        run = {"id": fixture["id"], "url": url, "returncode": proc.returncode, "elapsed_s": round(time.time()-started, 3), "stdout_tail": proc.stdout[-4000:], "stderr_tail": proc.stderr[-4000:]}
        result["process_runs"].append(run)
        result["sequence"].append(fixture["id"])
        if proc.returncode != 0:
            result["status"] = "BLOCKED"
            result["reason"] = f"MiniBrowser returned {proc.returncode} for {fixture['id']}"
            finish(); raise SystemExit(1)
    except subprocess.TimeoutExpired as exc:
        result["process_runs"].append({"id": fixture["id"], "url": url, "status": "TIMEOUT", "stdout_tail": (exc.stdout or "")[-4000:], "stderr_tail": (exc.stderr or "")[-4000:]})
        result["status"] = "BLOCKED"
        result["reason"] = "MiniBrowser started but timed out; no functional assertion was inferred"
        finish(); raise SystemExit(1)

result["status"] = "STARTED_ONLY"
result["reason"] = "MiniBrowser was invoked for all fixtures; capability PASS requires explicit assertions in stdout or a dedicated automation wrapper"
finish()
PY
