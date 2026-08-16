#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/analysis"
python3 "$ROOT/tools/verify_offsets.py" --repo "$ROOT" --json > "$ROOT/analysis/verify_offsets.json"
python3 "$ROOT/tools/analyze_xref_versions.py" "$ROOT/libkernel_sys_13.52.bin" --out-dir "$ROOT/analysis"
(cd "$ROOT" && sha256sum ./*.bin) > "$ROOT/analysis/hash_inventory.txt"
(cd "$ROOT" && cat lk_dump1.bin lk_dump2.bin lk_dump3.bin | sha256sum) > "$ROOT/analysis/concatenation_sha256.txt"
printf 'Static audit complete. Outputs are under %s/analysis.\n' "$ROOT"
