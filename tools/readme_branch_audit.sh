#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
out="readme-branches.txt"
{
  echo '=== REMOTE BRANCHES AND README PATHS ==='
  for ref in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin/ | grep -v '/HEAD$'); do
    echo "--- $ref ---"
    git ls-tree -r --name-only "$ref" | grep -Ei '(^|/)(readme|readme[^/]*)\.(md|txt)$' || true
    for p in $(git ls-tree -r --name-only "$ref" | grep -Ei '(^|/)(readme|readme[^/]*)\.(md|txt)$' || true); do
      echo "### $p"
      git show "$ref:$p" 2>/dev/null | sha256sum | sed "s#  -#  $ref:$p#"
      git show "$ref:$p" 2>/dev/null | grep -nEi '(100[[:space:]]*%|15[[:space:]]*%|0[[:space:]]*%|13\.02|13\.52|progreso|progress|verified|confirmed|completo|complete)' | head -80 || true
    done
  done
  echo
  echo '=== DOCUMENTATION COUNTS BY REMOTE BRANCH ==='
  for ref in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin/ | grep -v '/HEAD$'); do
    printf '%s tracked=' "$ref"
    git ls-tree -r --name-only "$ref" | wc -l
    printf '%s md=' "$ref"
    git ls-tree -r --name-only "$ref" | grep -Ei '\.(md|txt)$' | wc -l
  done
} > "$out"
cat "$out"
