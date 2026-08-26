#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
commit="79910d5"
branches=(main bdj-disc-hello-world ps4-13.52-build pup-byte-manifest-1350-1352 webkit-ps4-1352-kit)

git fetch origin --prune
for branch in "${branches[@]}"; do
  echo "=== syncing $branch ==="
  git checkout -B "$branch" "origin/$branch"
  if git cherry-pick "$commit"; then
    echo "cherry-pick succeeded for $branch"
  else
    echo "cherry-pick conflict for $branch; applying audited cleanup snapshot"
    git cherry-pick --abort
    while IFS= read -r path; do
      [ -n "$path" ] || continue
      mkdir -p "$(dirname "$path")"
      git show "$commit:$path" > "$path"
    done < <(git diff-tree --no-commit-id --name-only -r "$commit")
    git add -A
    git commit -m "cleanup: synchronize truthful repository documentation and fixes"
  fi
  git push origin "$branch"
  git status --short --branch
  git log -1 --oneline --decorate
 done

git checkout research/webkit-disk-1302
echo '=== final branches ==='
git ls-remote --heads origin main bdj-disc-hello-world ps4-13.52-build pup-byte-manifest-1350-1352 webkit-ps4-1352-kit research/webkit-disk-1302
