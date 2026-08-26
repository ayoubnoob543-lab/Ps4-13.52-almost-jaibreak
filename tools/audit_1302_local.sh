#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
out="1302-local-inventory.txt"
{
  echo '=== GIT STATE ==='
  git status --short --branch
  git log -1 --oneline --decorate
  echo
  echo '=== PATHS WITH 1302 ==='
  git ls-files | grep -Ei '(^|[^0-9])13[._-]?02([^0-9]|$)|1302' | sort || true
  echo
  echo '=== TEXT OCCURRENCES ==='
  grep -RInE --exclude-dir=.git --exclude='*.bin' --exclude='*.iso' --exclude='*.jar' --exclude='*.zip' '(13\.02|13_02|1302|13-02)' . | head -2000 || true
  echo
  echo '=== OFFSET DEFINITIONS ==='
  grep -RInE --include='*.h' --include='*.c' --include='*.json' --include='*.md' '(SYSENT|sysent|prison0|pmap|mmap|RWX|kernel_map|rootvnode|allproc)' kpayload installer analysis docs research webkit-kit 2>/dev/null | grep -Ei '1302|13\.02|13_02|13-02' | head -1200 || true
  echo
  echo '=== RELEVANT FILE SIZES/HASHES ==='
  while IFS= read -r f; do [ -f "$f" ] && { stat -c '%s %n' "$f"; sha256sum "$f"; }; done < <(git ls-files | grep -Ei '1302|13[._-]?02' || true)
} > "$out"
cat "$out"
