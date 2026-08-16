#!/bin/bash
set -euo pipefail

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "error: required command not found: $1" >&2
    exit 1
  }
}

# Only update/install if running as root AND on Ubuntu
# This is for the CI
# On your system you shouldn't be running as root and should already have these installed
if [ "$(id -u)" -eq 0 ] && grep -qi ubuntu /etc/os-release; then
  apt-get update
  apt-get install -y --no-install-recommends ca-certificates curl unzip xxd
fi

require_command curl
require_command unzip
require_command xxd

pushd kpayload > /dev/null
make
popd > /dev/null

mkdir -p tmp
pushd tmp > /dev/null

# known bundled plugins
PRX_FILES=(
  plugin_bootloader.prx
  plugin_loader.prx
  plugin_mono.prx
  plugin_server.prx
  plugin_shellcore.prx
)

SKIP_DOWNLOAD=false
if [ -f plugins.zip ]; then
  SKIP_DOWNLOAD=true
else
  SKIP_DOWNLOAD=true
  for prx in "${PRX_FILES[@]}"; do
    if [ ! -f "$prx" ]; then
      SKIP_DOWNLOAD=false
      break
    fi
  done
fi

if [ "$SKIP_DOWNLOAD" = false ]; then
  f="plugins.zip"
  rm -f "$f"
  curl --fail --location --retry 3 --retry-delay 2 \
    --output "$f" \
    "https://github.com/Scene-Collective/ps4-hen-plugins/releases/latest/download/$f"
  unzip -q "$f"
fi

for prx in "${PRX_FILES[@]}"; do
  if [ ! -f "$prx" ]; then
    echo "error: required plugin missing after download: $prx" >&2
    exit 1
  fi
done

# need to use translation units to force rebuilds
# including as headers doesn't do it
shopt -s nullglob
prx_files=( *.prx )
if [ "${#prx_files[@]}" -eq 0 ]; then
  echo "error: no PRX files found in $PWD" >&2
  exit 1
fi
for file in "${prx_files[@]}"; do
  echo "${file}"
  xxd -i "$file" | sed 's/^unsigned /static const unsigned /' > "../installer/source/${file}.inc.c"
done

popd > /dev/null

xxd -i "hen.ini" | sed 's/^unsigned /static const unsigned /' > "installer/source/hen.ini.inc.c"

pushd installer > /dev/null
make
popd > /dev/null

rm -f hen.bin
cp installer/installer.bin hen.bin
