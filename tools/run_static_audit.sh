#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() {
  printf 'Static audit error: %s\n' "$*" >&2
  exit 2
}
require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "required command is missing: $1"
}
require_file() {
  [[ -r "$ROOT/$1" ]] || fail "required readable file is missing: $ROOT/$1"
}

require_command python3
# objdump is optional: current validators operate on raw bytes and Python parsers.
require_command sha256sum
require_file libkernel_sys_13.52.bin
for chunk in lk_dump1.bin lk_dump2.bin lk_dump3.bin; do require_file "$chunk"; done
require_file tools/verify_offsets.py
require_file tools/analyze_xref_versions.py
require_file tools/audit_psfree_porting.py

mkdir -p "$ROOT/analysis"
python3 "$ROOT/tools/verify_offsets.py" --repo "$ROOT" --json > "$ROOT/analysis/verify_offsets.json"
python3 "$ROOT/tools/analyze_xref_versions.py" "$ROOT/libkernel_sys_13.52.bin" --out-dir "$ROOT/analysis"
if [[ -n "${PSFREE_ROOT:-}" && -d "$PSFREE_ROOT" ]]; then
  python3 "$ROOT/tools/audit_psfree_porting.py" --psfree "$PSFREE_ROOT" --out "$ROOT/analysis/psfree_porting.json" >/dev/null
else
  printf '%s\n' '{"target_firmware":"13.52","status":"ABSENT","reason":"PSFREE_ROOT not provided; no external source was executed"}' > "$ROOT/analysis/psfree_porting.json"
fi
python3 -m unittest discover -s "$ROOT/tests" -v
(cd "$ROOT" && sha256sum ./*.bin) > "$ROOT/analysis/hash_inventory.txt"
(cd "$ROOT" && cat lk_dump1.bin lk_dump2.bin lk_dump3.bin | sha256sum) > "$ROOT/analysis/concatenation_sha256.txt"
printf 'Static audit complete. Outputs are under %s/analysis.\n' "$ROOT"
