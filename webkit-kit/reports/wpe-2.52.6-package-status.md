# Paquete oficial WPE WebKit 2.52.6 x86_64

## Estado actual

```text
WPE_2526_PACKAGE = BLOCKED_PACKAGE_NOT_PRESENT
WPE_2526_SHA256 = NOT_VERIFIED
WPE_2526_MINIBROWSER = NOT_RUN
WPE_2526_HTML_SMOKE = NOT_RUN
```

El SHA-256 solicitado es:

```text
99f09e0a1e62069d1715ee9840d18202b07c4fcdbe5c6ba79b178cb93cf59faf
```

El paquete no existe en el sandbox actual. Se revisaron únicamente las ubicaciones acotadas `/home/ubuntu/Downloads`, `/home/ubuntu/upload`, `/home/ubuntu/wpe-bundles`, `/home/ubuntu/.cache/wpe`, `/tmp/wpe-bundles` y `/tmp/wpe-builds`; no apareció un archivo candidato ni un `MiniBrowser`/`WPEWebDriver` extraído.

También se comprobaron los índices oficiales públicos de bundles WPE. Sus valores actuales son `stable → MiniBrowser_wpe_2.52.3.tar.xz`, `beta → MiniBrowser_wpe_2.53.1.tar.xz` y `nightly → MiniBrowser_wpe_319501@main.tar.xz`. Ninguno corresponde al paquete 2.52.6 ni al SHA solicitado. No se descargó un artefacto distinto, no se usó el tarball de fuentes y no se reconstruyó WebKit.

## Requisitos de ejecución

| Componente | Estado | Evidencia |
|---|---|---|
| `bubblewrap` | **PASS** | `/usr/bin/bwrap`, versión 0.9.0 |
| User namespaces | **PASS** | `unshare -Ur true` devolvió código 0 |
| `user.max_user_namespaces` | **AVAILABLE** | 15740 |
| glibc | **AVAILABLE** | Ubuntu GLIBC 2.39-0ubuntu8.8 |
| Paquete WPE 2.52.6 | **BLOCKED** | No está montado ni presente localmente |
| Build fuente `/tmp/wpewebkit-2.52.6-build` | **PRESERVED** | Existe, sin `bin/MiniBrowser`, no modificada |

El bloqueo actual no es bubblewrap ni user namespaces: es la ausencia del archivo oficial cuyo SHA se pueda verificar. Cuando esté disponible, deberá conservarse fuera de Git, preferiblemente en:

```text
/home/ubuntu/wpe-bundles/wpewebkit-2.52.6/
```

La primera operación será:

```sh
sha256sum /home/ubuntu/wpe-bundles/wpewebkit-2.52.6/<bundle> \
  | grep 99f09e0a1e62069d1715ee9840d18202b07c4fcdbe5c6ba79b178cb93cf59faf
```

Solo tras esa coincidencia se extraerán `MiniBrowser`, `WPEWebDriver`, `libWPEWebKit-2.0.so` y sus recursos, y se ejecutarán los diagnósticos y el smoke existentes. Hasta entonces, `WPE_2526_MINIBROWSER` y `WPE_2526_HTML_SMOKE` permanecen `NOT_RUN`.
