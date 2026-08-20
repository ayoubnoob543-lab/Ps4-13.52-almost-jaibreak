# Evidencia pública WPE WebKit 2.52.6

## Fuentes oficiales

- Release oficial: https://wpewebkit.org/release/wpewebkit-2.52.6.html
- Índice oficial de releases: https://wpewebkit.org/release/
- Descarga de fuente 2.52.6: https://wpewebkit.org/releases/wpewebkit-2.52.6.tar.xz
- Índice oficial de bundles MiniBrowser: https://wpewebkit.org/built-products/x86_64/release/beta/MiniBrowser/
- Guía pública MiniBrowser/WPT: https://web-platform-tests.org/running-tests/wpewebkit_minibrowser.html
- Paquete Arch x86_64: https://archlinux.org/packages/extra/x86_64/wpewebkit/
- Lista de archivos Arch: https://archlinux.org/packages/extra/x86_64/wpewebkit/files/
- Base de datos Arch consultada: https://geo.mirror.pkgbuild.com/extra/os/x86_64/extra.db
- Paquete descargado: https://geo.mirror.pkgbuild.com/extra/os/x86_64/wpewebkit-2.52.6-1-x86_64.pkg.tar.zst
- Bootstrap Arch: https://geo.mirror.pkgbuild.com/iso/latest/archlinux-bootstrap-x86_64.tar.zst
- Checksums bootstrap: https://geo.mirror.pkgbuild.com/iso/latest/sha256sums.txt

## Datos confirmados

La release oficial WPE WebKit 2.52.6 fue publicada el 19 de agosto de 2026. Su tarball fuente tiene SHA-256 `b2bafef2751625b7fdf530f230ff0f542ff0eeba3590c3a989d931b2a55c858e`.

El índice oficial de bundles MiniBrowser no contiene ningún `MiniBrowser_wpe_2.52.6.tar.xz`; contiene 2.53.1 y versiones anteriores 2.51.x/2.49.x. Por tanto, el bundle universal no ofrece 2.52.6.

Arch Linux sí publica `wpewebkit 2.52.6-1` para x86_64. La base `extra.db` registra:

- archivo: `wpewebkit-2.52.6-1-x86_64.pkg.tar.zst`
- versión: `2.52.6-1`
- arquitectura: `x86_64`
- tamaño comprimido registrado: `38898907`
- tamaño instalado registrado: `143866290`
- SHA-256 oficial de la base: `99f09e0a1e62069d1715ee9840d18202b07c4fcdbe5c6ba79b178cb93cf59faf`
- packager: Jan Alexander Steffens (heftig) <heftig@archlinux.org>
- build timestamp de la base: `1787095948`

El archivo descargado tiene exactamente SHA-256 `99f09e0a1e62069d1715ee9840d18202b07c4fcdbe5c6ba79b178cb93cf59faf`; la verificación contra la base Arch es PASS y `zstd -t` también es PASS.

La lista de archivos del paquete confirma que incluye:

- `/usr/lib/wpe-webkit-2.0/MiniBrowser`
- `/usr/bin/WPEWebDriver`
- `/usr/lib/libWPEWebKit-2.0.so.1.9.10`
- `/usr/lib/wpe-webkit-2.0/WPEWebProcess`
- `/usr/lib/wpe-webkit-2.0/WPENetworkProcess`
- `/usr/lib/wpe-webkit-2.0/WPEGPUProcess`
- WPEPlatform, incluida la API headless

El paquete es ELF x86-64. Build IDs observados:

- MiniBrowser: `55f35b0dcddb3ed1733fb5e28f5d4ebe6b652aba`
- WPEWebDriver: `3fb7e9b322fde2d7dc4626cf634faeead30c28a2`
- libWPEWebKit: `40d28b84c551f2f8d6aa3b3272a63d599d84c1c0`

## Compatibilidad de ejecución

El host Ubuntu tiene glibc 2.39. El paquete Arch 2.52.6 exige, entre otras, `GLIBC_2.42`, `GLIBC_2.43` y `GLIBC_2.44`; por ello no es ejecutable directamente en el host Ubuntu.

Se descargó y verificó el bootstrap oficial Arch x86_64. El checksum oficial del bootstrap fue PASS mediante `sha256sums.txt`; el userspace informa glibc 2.44. Dentro de ese chroot se instalaron las dependencias públicas de Arch, incluyendo `wpewebkit`, `wpebackend-fdo`, `libwpe`, Wayland, Mesa, libinput, bubblewrap, fuentes y dependencias multimedia.

La primera comprobación real del MiniBrowser 2.52.6 dentro del chroot fue PASS para `--help`, confirmando las opciones `--headless` y `--automation`. El WPEWebDriver inició y su endpoint `/status` respondió `{"ready":true,"message":"No sessions"}`.

El intento de sesión y el MiniBrowser directo fallaron en la fase de creación de procesos hijos por:

```text
bwrap: Failed to make / slave: Invalid argument
Connection: failed to receive credentials: Expecting to read a single byte for receiving credentials but read zero bytes
```

Las pruebas directas de bubblewrap muestran:

- operación básica: `Failed to make / slave: Invalid argument`
- `--unshare-all`: `No permissions to create a new namespace`

Esto es un bloqueo del entorno chroot/kernel para bubblewrap, no evidencia de que falte el engine 2.52.6. La variable `WEBKIT_DISABLE_SANDBOX=1` no evitó que el runtime intentase usar bubblewrap en esta configuración.

## Estado de ejecución

```text
WPE_2526_SOURCE_RELEASE = AVAILABLE
WPE_2526_ARCH_BINARY_PACKAGE = VERIFIED
WPE_2526_MINIBROWSER_BINARY = PRESENT
WPE_2526_HELP_PROBE = PASS
WPE_2526_WEBDRIVER_STATUS = PASS
WPE_2526_HTML_SMOKE = BLOCKED_BY_BWRAP_NAMESPACE
WPE_2526_DIRECT_HEADLESS = BLOCKED_BY_BWRAP_NAMESPACE
WPE_2526_HOST_UBUNTU_DIRECT = BLOCKED_BY_GLIBC
WPE_2531_RESULT = INDEPENDENT_REFERENCE_ONLY
```

El paquete y el chroot se conservan fuera de Git en `/home/ubuntu/wpe-artifacts-2526/`. No se modificaron archivos versionados del repositorio ni se ejecutó CMake/Ninja.
