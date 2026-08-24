#!/usr/bin/env bash
set -e
CC=${CC:-clang}
sed 's|/mnt_usb0/PS4UPDATE.PUP|'"$PWD"'/mnt_usb0/PS4UPDATE.PUP|g' decrypt.c > decrypt_host.c
# el host usa host_compat.h (log a stderr) en vez de defines.h/sceNetSend
sed -i '/#include "defines.h"/d; /#define DEBUG_SOCKET/d' decrypt_host.c
$CC -O1 -g -std=gnu11 -Wall -D_GNU_SOURCE -I. -include host_compat.h \
    host_main.c shim_ioctl.c decrypt_host.c pup.c pupup.c \
    -o pup_decrypt_mock
echo "build OK"
