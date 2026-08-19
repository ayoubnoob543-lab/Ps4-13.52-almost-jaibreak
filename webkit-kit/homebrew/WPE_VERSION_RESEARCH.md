# WPE host research

Official WPE page: https://wpewebkit.org/about/get-wpe.html

The official page identifies the required components as WebKit, libwpe, WPEBackend-fdo and Cog. It recommends the WebKit source build command `Tools/Scripts/build-webkit --wpe` or a production CMake build with `-DPORT=WPE -GNinja`. It lists stable releases: WPE WebKit 2.52.6, WPEBackend-fdo 1.16.1, libwpe 1.16.3 and Cog 0.18.5.

libwpe release 1.16.3 is tied to commit `e0814ca7d4f87594a46732ebd309494872d2520e` and has official tarball SHA-256 `c880fa8d607b2aa6eadde7d6d6302b1396ebc38368fe2332fa20e193c7ee1420`. The official release page states it is a bug-fix release in the stable 1.16 series.

WPEBackend-fdo is public BSD-2-Clause. The official repository is https://github.com/Igalia/WPEBackend-fdo. Its public tree contains Meson build files, headers, source and a BSD-2-Clause COPYING file.

The WPEWebKit public repository is https://github.com/WebPlatformForEmbedded/WPEWebKit. Its README documents the WPE build commands `cmake -DPORT=WPE -DCMAKE_BUILD_TYPE=RelWithDebInfo -GNinja` and `Tools/Scripts/build-webkit --wpe --debug`.

Local host status on 2026-08-19: no `wpewebkit`, `wpe-1.0`, `wpebackend-fdo` or `libwpe-1.0` pkg-config module is installed; Ubuntu apt repositories configured in this environment expose no candidate for the WPE packages queried. Approximately 3.2 GB disk space remains. Therefore a full WPE WebKit source build is not currently viable without obtaining the large dependency graph and likely more build space. No proprietary or target-specific substitute is used.

Local source attempt:
- Official WPE WebKit 2.52.6 tarball downloaded from https://wpewebkit.org/releases/wpewebkit-2.52.6.tar.xz.
- SHA-256: b2bafef2751625b7fdf530f230ff0f542ff0eeba3590c3a989d931b2a55c858e.
- Compressed size: 65,541,800 bytes; extracted source size: approximately 482 MB.
- Official libwpe 1.16.3 tarball downloaded from https://wpewebkit.org/releases/libwpe-1.16.3.tar.xz.
- SHA-256: c880fa8d607b2aa6eadde7d6d6302b1396ebc38368fe2332fa20e193c7ee1420.
- libwpe 1.16.3 configured and compiled successfully in an isolated `/tmp` build using CMake/Ninja, with EGL and xkbcommon found.
- WPE WebKit 2.52.6 CMake reached actual WPE configuration after installing public `libtasn1-6-dev`, `libjxl-dev` and `libavif-dev`. It found the locally built WPE 1.16.3, GLib, HarfBuzz, ICU, JPEG, Epoxy, LibGcrypt, Soup3, Tasn1, XkbCommon, XML, Zlib, PNG, SQLite, WebP, ATK/ATKBridge, JPEGXL, Hyphen, Freetype and LibXslt.
- Current CMake blocker: `libsystemd or libelogind are needed for ENABLE_JOURNALD_LOG`; Journald headers/library are absent. No proprietary component is involved.
- Full WPE WebKit build has not yet started. Remaining disk after source extraction and public dependencies is approximately 2.6 GB, so a complete compile may still exceed available workspace even if configuration is completed.
