#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CI_MODE=0
if [[ "${1:-}" == "--ci" ]]; then
  CI_MODE=1
elif [[ $# -ne 0 ]]; then
  printf 'Usage: %s [--ci]\n' "$0" >&2
  exit 2
fi

failures=0
log_file="${ROOT}/analysis/ci_environment.txt"
mkdir -p "${ROOT}/analysis"
: > "$log_file"

log() {
  printf '%s\n' "$*" | tee -a "$log_file"
}
fail() {
  log "ERROR: $*"
  failures=$((failures + 1))
}
require_command() {
  local command_name="$1"
  if command -v "$command_name" >/dev/null 2>&1; then
    log "PASS: command $command_name -> $(command -v "$command_name")"
  else
    fail "required command is missing: $command_name"
  fi
}

log "PS4 research environment preflight"
log "root=$ROOT"
log "ci_mode=$CI_MODE"

for command_name in bash git python3 node make gcc objdump xxd curl unzip sha256sum; do
  require_command "$command_name"
done

if command -v python3 >/dev/null 2>&1; then log "python_version=$(python3 --version 2>&1)"; fi
if command -v node >/dev/null 2>&1; then log "node_version=$(node --version)"; fi
if command -v gcc >/dev/null 2>&1; then log "gcc_version=$(gcc --version | head -1)"; fi
if command -v objdump >/dev/null 2>&1; then log "objdump_version=$(objdump --version | head -1)"; fi
if command -v make >/dev/null 2>&1; then log "make_version=$(make --version | head -1)"; fi

# Disassembler backend for tools/analyze_xref_versions.py
if python3 -c 'import capstone' >/dev/null 2>&1; then
  log "PASS: python capstone available (disassembler fallback)"
else
  log "WARN: python capstone not installed; x86-64 disassembly relies on objdump/llvm-objdump"
fi

# x86_64 payload build mode (mirrors kpayload/Makefile and installer/Makefile probes)
probe='int main(void){return 0;}'
cc_bin="$(command -v gcc || command -v clang || true)"
if [[ -z "$cc_bin" ]]; then
  fail "required command is missing: gcc|clang"
elif printf '%s' "$probe" | "$cc_bin" -m64 -march=btver2 -mabi=sysv -mcmodel=small -x c -fsyntax-only - >/dev/null 2>&1; then
  log "PASS: x86_64 payload build mode=native ($(basename "$cc_bin"))"
elif printf '%s' "$probe" | "$cc_bin" --target=x86_64-unknown-freebsd13.0 -fuse-ld=lld -m64 -march=btver2 -mabi=sysv -mcmodel=small -x c -fsyntax-only - >/dev/null 2>&1; then
  log "PASS: x86_64 payload build mode=cross-clang target=x86_64-unknown-freebsd13.0"
  for helper in ld.lld llvm-objcopy llvm-ar; do
    require_command "$helper"
  done
else
  fail "no x86_64-capable compiler found for BTVER2 payload build"
fi

required_files=(
  "libkernel_sys_13.52.bin"
  "lk_dump1.bin"
  "lk_dump2.bin"
  "lk_dump3.bin"
  "tools/verify_offsets.py"
  "tools/analyze_xref_versions.py"
  "tools/run_static_audit.sh"
)
for relative_path in "${required_files[@]}"; do
  if [[ -r "${ROOT}/${relative_path}" ]]; then
    log "PASS: readable artifact $relative_path"
  else
    fail "required readable artifact is missing: $relative_path"
  fi
done

sdk_path="${ROOT}/third_party/ps4-payload-sdk"
expected_sdk="46efae910f3705e0171edea5b94e572d01bc00e8"
if [[ -d "$sdk_path/.git" || -f "$sdk_path/.git" ]]; then
  sdk_head="$(git -C "$sdk_path" rev-parse HEAD 2>/dev/null || true)"
  if [[ "$sdk_head" == "$expected_sdk" ]]; then
    log "PASS: SDK submodule HEAD=$sdk_head"
  else
    fail "SDK submodule is not at expected commit: expected=$expected_sdk actual=${sdk_head:-unavailable}"
  fi
else
  fail "SDK submodule is not initialized: $sdk_path"
fi

henloader_path="${ROOT}/third_party/henloader_lp"
if [[ -d "$henloader_path/.git" || -f "$henloader_path/.git" ]]; then
  log "PASS: henloader_lp submodule initialized at $(git -C "$henloader_path" rev-parse --short HEAD 2>/dev/null || echo unknown)"
else
  log "WARN: henloader_lp submodule not initialized (run: git submodule update --init)"
fi

if [[ -f "${ROOT}/libkernel_sys_13.52.bin" ]]; then
  size="$(wc -c < "${ROOT}/libkernel_sys_13.52.bin")"
  if [[ "$size" == 479232 ]]; then log "PASS: combined dump size=$size"; else fail "combined dump size is $size, expected 479232"; fi
fi
for chunk in lk_dump1.bin lk_dump2.bin lk_dump3.bin; do
  if [[ -f "${ROOT}/${chunk}" ]]; then
    size="$(wc -c < "${ROOT}/${chunk}")"
    if [[ "$size" == 159744 ]]; then log "PASS: $chunk size=$size"; else fail "$chunk size is $size, expected 159744"; fi
  fi
done

if (( failures > 0 )); then
  log "ENV_PREFLIGHT_FAILED failures=$failures"
  exit 1
fi
log "ENV_PREFLIGHT_PASS"
