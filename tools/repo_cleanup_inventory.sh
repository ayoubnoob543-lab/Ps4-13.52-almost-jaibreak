#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
out="repo-cleanup-inventory.txt"
{
  echo '=== CURRENT STATE ==='
  git status --short --branch
  echo
  echo '=== LOCAL BRANCHES ==='
  git branch -vv
  echo
  echo '=== REMOTE BRANCHES ==='
  git for-each-ref --format='%(refname:short) %(objectname:short) %(subject)' refs/remotes/origin/
  echo
  echo '=== README FILES ==='
  git ls-files | grep -Ei '(^|/)readme[^/]*\\.md$' | sort
  echo
  echo '=== STATUS/REPORT FILES ==='
  git ls-files | grep -Ei '(status|audit|report|progress|remaining|gap|artifact|research).*(\\.md|\\.json|\\.txt)$' | sort
  echo
  echo '=== MARKETING/PERCENTAGE CLAIMS ==='
  grep -RInE --exclude-dir=.git --exclude='*.bin' --exclude='*.iso' --exclude='*.jar' --exclude='*.zip' '(100[[:space:]]*%|15[[:space:]]*%|0[[:space:]]*%|progress|progreso|complete|completo|final|definitivo|verified|confirmed)' . | head -2000 || true
  echo
  echo '=== TOP-LEVEL FILES ==='
  find . -maxdepth 1 -mindepth 1 -printf '%f\\t%s bytes\\n' | sort
  echo
  echo '=== LARGE TRACKED FILES ==='
  git ls-files -z | while IFS= read -r -d '' f; do [ -f "$f" ] && stat -c '%s %n' "$f"; done | sort -nr | head -100
} > "$out"
cat "$out"
