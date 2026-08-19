#!/usr/bin/env bash
set -euo pipefail

# This script only fetches public OSS sources. It does not fetch Sony SDKs,
# retail binaries, exploits, payloads, or run anything on a PS4.
ROOT="$(cd "$(dirname "$0")" && pwd)"
CACHE="${WEBKIT_KIT_CACHE:-$ROOT/cache}"
mkdir -p "$CACHE"

need() { command -v "$1" >/dev/null 2>&1 || { echo "missing command: $1" >&2; exit 2; }; }
need git
need curl
need sha256sum

fetch_zip() {
  local name="$1" url="$2"
  local out="$CACHE/$name.zip"
  if [[ ! -s "$out" ]]; then
    curl --fail --location --retry 3 --output "$out" "$url"
  fi
  sha256sum "$out" | tee "$out.sha256"
  echo "Downloaded public source archive: $out"
  echo "Inspect/extract manually after reviewing its license and hash."
}

if [[ "${1:-}" == "--official-webkit-1300" ]]; then
  fetch_zip "WebKit-601-1300" "https://www.playstation.com/content/dam/global_pdc/en-us/external-resources/oss/ps4/webkit/WebKit-601-1300.zip"
  fetch_zip "WebKit-616-1300" "https://www.playstation.com/content/dam/global_pdc/en-us/external-resources/oss/ps4/webkit/WebKit-616-1300.zip"
  exit 0
fi

if [[ "${1:-}" == "--openorbis" ]]; then
  target="$CACHE/OpenOrbis-PS4-Toolchain"
  if [[ ! -d "$target/.git" ]]; then
    git clone --filter=blob:none --no-checkout https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain.git "$target"
  fi
  git -C "$target" fetch --depth=1 origin master
  git -C "$target" checkout --detach 0a1aaf9dd4a92695538bdeb09fb056d06dd11725
  git -C "$target" rev-parse HEAD | tee "$target.COMMIT"
  exit 0
fi

cat >&2 <<'EOF'
Usage:
  bootstrap_sources.sh --official-webkit-1300
  bootstrap_sources.sh --openorbis

The official source archives are 13.00-13.04 structural bases, not a verified
13.52 WebKit. No proprietary SDK, retail binary, exploit or PS4 payload is fetched.
EOF
exit 2
