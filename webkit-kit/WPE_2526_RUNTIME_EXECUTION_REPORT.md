# Ejecución real de WPE WebKit 2.52.6

## Resultado

El MiniBrowser WPE WebKit **2.52.6 real** se ejecutó correctamente en x86_64 dentro de un bubblewrap host con namespaces PID y red, reutilizando el userspace Arch/glibc 2.44 y el paquete binario previamente verificado. No se recompiló WebKit, no se modificó el paquete `.pkg.tar.zst` y no se tocó `/tmp/wpewebkit-2.52.6-build`.

| Estado | Resultado |
|---|---|
| Artefacto WPE 2.52.6 | **PASS** |
| Loader/glibc/ELF | **PASS** |
| WPEWebDriver `/status` | **PASS** |
| Sesión WebDriver | **PASS**, `browserVersion=2.52.6` |
| MiniBrowser headless | **PASS** |
| page1→page2→page3 | **PASS** |
| Smoke DOM/CSS/JS | **PASS** |
| Navegación e historial | **PASS** |
| GTK/WPE 2.53.1 mezclado | **NO** |

## Identidad del runtime

- Paquete Arch: `wpewebkit-2.52.6-1-x86_64.pkg.tar.zst`
- SHA-256 del paquete: `99f09e0a1e62069d1715ee9840d18202b07c4fcdbe5c6ba79b178cb93cf59faf`
- MiniBrowser SHA-256: `a2c569e96a4e00a61b849eba6f4c592c43a4071767cc63d39effada41eca1d37`
- MiniBrowser Build ID: `55f35b0dcddb3ed1733fb5e28f5d4ebe6b652aba`
- WPEWebDriver Build ID: `3fb7e9b322fde2d7dc4626cf634faeead30c28a2`
- `libWPEWebKit-2.0.so.1.9.10` Build ID: `40d28b84c551f2f8d6aa3b3272a63d599d84c1c0`
- Userspace: Arch Linux bootstrap x86_64, glibc 2.44

## Entorno de ejecución

El Ubuntu host no puede ejecutar directamente el paquete por la versión de glibc. El chroot aislado puede iniciar MiniBrowser, pero su bubblewrap interno no puede crear los namespaces/mounts requeridos en el sandbox. La solución mínima fue envolver el userspace completo con el `bwrap` del host, que sí permite namespaces PID/network, y mantener la red compartida para el endpoint WebDriver y el servidor HTTP local:

```sh
sudo setsid bwrap \
  --unshare-pid --die-with-parent \
  --ro-bind /home/ubuntu/wpe-artifacts-2526/arch/rootfs / \
  --ro-bind /home/ubuntu/firmware-lab-bundle/webkit-kit/homebrew/fixtures /tmp/fixtures \
  --tmpfs /tmp --dir /tmp/cache \
  --dev /dev --proc /proc \
  --setenv HOME /tmp \
  --setenv XDG_RUNTIME_DIR /tmp \
  --setenv XDG_CACHE_HOME /tmp/cache \
  --setenv MESA_SHADER_CACHE_DIR /tmp/cache/mesa \
  --setenv WPE_BACKEND fdo \
  --setenv WPE_RENDERER software \
  --setenv LIBGL_ALWAYS_SOFTWARE 1 \
  --chdir / -- /usr/bin/WPEWebDriver --port=9515 --host=all
```

Las fixtures se sirvieron mediante HTTP local en `127.0.0.1:8765` para que WebKit recibiese `Content-Type: text/html`; con `file://`, el entorno aislado las interpretaba como texto plano. El servidor sólo sirvió las tres fixtures versionadas y no implicó tráfico externo.

## Evidencia WebDriver

`GET /status` devolvió `{"ready":true,"message":"No sessions"}`. La sesión creó:

```json
{
  "browserName": "MiniBrowser",
  "browserVersion": "2.52.6",
  "platformName": "linux",
  "pageLoadStrategy": "normal"
}
```

Las tres navegaciones devolvieron `{"value":null}`. Las assertions fueron ejecutadas dentro del engine mediante `POST /execute/sync`.

### page1

```json
{"dom":true,"flex":true,"grid":true,"js":true,"event":true,"forms":true,"svg":true,"images":true,"Canvas":true,"localStorage":true}
```

### page2

```json
{"page":true,"dom":true,"event":true,"storage":true,"js":true}
```

### page3

```json
{"page":true,"dom":true,"history":true,"js":true}
```

Resultado por capacidad:

| Capacidad | Estado |
|---|---|
| DOM | **PASS** |
| CSS | **PASS** |
| Flexbox | **PASS** |
| Grid | **PASS** |
| JavaScript | **PASS** |
| Eventos | **PASS** |
| Formularios | **PASS** |
| SVG | **PASS** |
| Imágenes | **PASS** |
| Canvas/pixel readback | **PASS** |
| localStorage | **PASS** |
| Navegación | **PASS** |
| Historial | **PASS** |

## Diagnóstico del bloqueo original

El bloqueo original no era una incompatibilidad de WebKit. Bubblewrap interno fallaba con `Failed to make / slave: Invalid argument` porque el sandbox no permitía la combinación de mount/user/PID/network namespaces solicitada por WPE. Las pruebas mostraron que el host sí puede ejecutar una instancia exterior de bubblewrap con namespaces suficientes; por eso la solución fue un entorno exterior compatible, no un shim que falsificase el aislamiento.

## Artefactos fuera de Git

Los binarios, chroot, logs y JSON completos se conservaron fuera del repositorio en `/home/ubuntu/wpe-artifacts-2526/`. El JSON final de la ejecución manual se identificó mediante el resultado de WebDriver; no se añadió ningún binario grande al repositorio. La evidencia de fixtures conserva los SHA-256 del manifiesto versionado.

## Estado final

```text
WPE_2526_ARTIFACT       = PASS
WPE_2526_ELF_LOADER     = PASS
WPE_2526_WEBDRIVER      = PASS
WPE_2526_MINIBROWSER    = PASS
WPE_2526_HTML_SMOKE     = PASS
WPE_2526_CAPABILITIES   = PASS
WPE_2531_REFERENCE      = SEPARATE
```
