# WPE WebKit host: estado de build

## Versiones fijadas

| Componente | Versión | Fuente | SHA-256 | Estado |
|---|---:|---|---|---|
| WPE WebKit | 2.52.6 | https://wpewebkit.org/releases/wpewebkit-2.52.6.tar.xz | `b2bafef2751625b7fdf530f230ff0f542ff0eeba3590c3a989d931b2a55c858e` | fuente descargada/configurada |
| libwpe | 1.16.3 | https://wpewebkit.org/releases/libwpe-1.16.3.tar.xz | `c880fa8d607b2aa6eadde7d6d6302b1396ebc38368fe2332fa20e193c7ee1420` | compilado en prefijo temporal |
| WPEBackend-fdo | 1.16.1 | https://wpewebkit.org/releases/wpebackend-fdo-1.16.1.tar.xz | `544ae14012f8e7e426b8cb522eb0aaaac831ad7c35601d1cf31d37670e0ebb3b` | compilado |

## Dependencias públicas instaladas o utilizadas

La configuración utilizó CMake, Ninja, Meson, GCC, Wayland, Wayland protocols, EGL, Epoxy, GLib/GObject, Soup 3, ICU, HarfBuzz, JPEG, JPEG XL, AVIF, PNG, SQLite, WebP, ATK, Freetype, LibXslt, libsystemd, libseccomp, libdrm, GBM, `unifdef` y otras bibliotecas públicas de Ubuntu 24.04.

No se usó GTK en la configuración WPE. Tampoco se usaron SDKs Sony, módulos SPRX, JSCBRIDGE, offsets, exploits, payloads o ABI privada.

## Resultados reproducibles

`libwpe` 1.16.3 se configuró y compiló correctamente en `/tmp/libwpe-1.16.3-build`. `WPEBackend-fdo` 1.16.1 se configuró con Meson y compiló correctamente con 53/53 tareas; produjo `libWPEBackend-fdo-1.0.so.1.10.2`.

WPE WebKit 2.52.6 se configuró correctamente con CMake y Ninja mediante:

```sh
cmake -S wpewebkit-2.52.6 -B build -G Ninja \
  -DPORT=WPE -DCMAKE_BUILD_TYPE=Release \
  -DWPE_INCLUDE_DIR=/tmp/wpe-prefix/include/wpe-1.0 \
  -DWPE_LIBRARY=/tmp/wpe-prefix/lib/libwpe-1.0.so.1.9.6 \
  -DWPEBackendFDO_INCLUDE_DIR=/path/to/wpebackend-fdo/include \
  -DWPEBackendFDO_LIBRARY=/tmp/wpebackend-fdo-build/libWPEBackend-fdo-1.0.so.1.10.2 \
  -DENABLE_MINIBROWSER=ON -DUSE_LIBBACKTRACE=OFF -DUSE_GSTREAMER=OFF \
  -DENABLE_INTROSPECTION=OFF -DENABLE_WEBDRIVER=OFF \
  -DENABLE_GAMEPAD=OFF -DENABLE_SPEECH_SYNTHESIS=OFF
```

La configuración terminó con `Configuring done` y `Generating done`. Se generó el target público `MiniBrowser`.

## Bloqueo actual

La compilación de `MiniBrowser` fue iniciada realmente con `ninja -C build MiniBrowser -j2`. El build alcanzó la generación de headers WTF y llegó a 1.296 de 9.222 tareas antes de ser interrumpido por el límite operativo de la sesión. No se generó todavía el ejecutable ni las bibliotecas finales de WebKit.

El build directory ocupaba aproximadamente 68 MB en ese punto; la fuente extraída ocupaba aproximadamente 482 MB y el espacio libre era aproximadamente 2,5 GB. Por tanto, el bloqueo actual es de tiempo/recursos del workspace, no un error de CMake ni una incompatibilidad de WPE/libwpe.

## Estado de la prueba HTML

No se afirma todavía un smoke test HTML WPE funcional. El navegador WebKitGTK existente sí valida los tres fixtures, pero no se reutiliza como resultado WPE. La prueba WPE queda `PENDING_ENGINE_BUILD` hasta que `MiniBrowser` y sus bibliotecas completen el enlace.

## Backend futuro

WPE desacopla el engine de GTK, pero `WPEBackend-fdo` sigue siendo un backend Linux público basado en Wayland/EGL/DMABUF/SHM. Un backend OpenOrbis futuro tendría que proporcionar implementaciones públicas equivalentes de view backend, renderer host, frame scheduling, surface/presentation, input, timers/event loop, memoria, filesystem, networking/TLS, fuentes y sincronización. Nada de esto demuestra compatibilidad con PS4 13.52.

## Veredicto

```text
LIBWPE_BUILD = PASS
WPEBACKEND_FDO_BUILD = PASS
WPEWEBKIT_CMAKE = PASS
WPEWEBKIT_MINIBROWSER_BUILD = INTERRUPTED_BY_RESOURCE_LIMIT
WPE_HTML_SMOKE = NOT_RUN
SONY_RETAIL_COMPATIBILITY = NOT_CLAIMED
```

No se incorporan al repositorio los tarballs, árboles temporales ni binarios generados; se conservan sólo URLs, hashes, opciones y resultados reproducibles.

## Reanudación posterior del build

Se reanudó el mismo directorio `/tmp/wpewebkit-2.52.6-build` sin limpiar objetos ni fuentes. La configuración permaneció `PORT=WPE`, `ENABLE_MINIBROWSER=ON`, `USE_GSTREAMER=OFF` y `Release`.

Los intentos realizados fueron:

```text
ninja -C /tmp/wpewebkit-2.52.6-build MiniBrowser -j2
ninja -C /tmp/wpewebkit-2.52.6-build MiniBrowser -j4
ninja -C /tmp/wpewebkit-2.52.6-build MiniBrowser -j1
```

El build reutilizó los headers y objetos existentes y progresó desde aproximadamente 1.296/9.222 tareas hasta la compilación de unidades de JavaScriptCore. Con `-j4` y `-j2`, los compiladores fueron terminados por la presión de memoria/límite operativo; no apareció un error semántico de C++ del proyecto. En el intento serial, 10 unidades pesadas avanzaron en aproximadamente cinco minutos, por lo que completar las 6.000+ tareas restantes no es viable dentro de este workspace temporal.

El último log `/tmp/wpewebkit-background.log` contiene una terminación externa de `cc1plus` durante `UnifiedSource-f0a787a9-2.cpp`; los mensajes de assembler truncado son consecuencia de esa terminación y no constituyen un diagnóstico válido del código fuente. No existe `MiniBrowser` enlazado ni biblioteca final WPE WebKit.

El workspace conserva aproximadamente 2,6 GB libres, 3,8 GB de RAM total y 2 GB de swap. No se eliminaron fuentes, hashes ni resultados necesarios. Los artefactos del build siguen siendo regenerables y temporales.

## Estado actualizado de smoke/comparación

No se ejecutó ningún smoke WPE porque no existe un ejecutable WPE WebKit enlazado. Los resultados de WebKitGTK permanecen exclusivamente como baseline independiente documentado en `WEBKITGTK_CAPABILITY_MATRIX.md`; no se presentan como resultados WPE.

| Capacidad | WebKitGTK baseline | WPE 2.52.6 en este workspace | Comparación automática |
|---|---|---|---|
| DOM | PASS | NOT_TESTED | NOT_TESTED |
| Flexbox/Grid | PASS | NOT_TESTED | NOT_TESTED |
| CSS | PASS | NOT_TESTED | NOT_TESTED |
| JavaScript | PASS | NOT_TESTED | NOT_TESTED |
| Eventos | PASS | NOT_TESTED | NOT_TESTED |
| Formularios | PASS | NOT_TESTED | NOT_TESTED |
| SVG/imágenes | PASS | NOT_TESTED | NOT_TESTED |
| Canvas | PASS | NOT_TESTED | NOT_TESTED |
| localStorage | PASS | NOT_TESTED | NOT_TESTED |
| Navegación page1→page2→page3 | PASS | NOT_TESTED | NOT_TESTED |

```text
WPEWEBKIT_CMAKE = PASS
WPE_MINIBROWSER_BUILD = BLOCKED_BY_WORKSPACE_RESOURCES
WPE_HTML_SMOKE = NOT_TESTED
WPE_VS_GTK_COMPARISON = NOT_TESTED
```


## Tooling de integración y pruebas host: 2026-08-20

La build principal `/tmp/wpewebkit-2.52.6-build` fue únicamente auditada en esta fase y no se modificó. El target generado sigue siendo `MiniBrowser`, con `PORT=WPE`, `ENABLE_MINIBROWSER=ON`, `ENABLE_UNIFIED_BUILDS=OFF`, `ENABLE_JIT=OFF`, `ENABLE_WEBASSEMBLY=OFF`, `USE_GSTREAMER=OFF` y `Release`. No existen todavía `bin/MiniBrowser` ni `libWPEWebKit-2.0.so` finales.

Se mejoraron tres herramientas públicas del kit. `probe_host_platform.py` descubre el prefijo WPE, añade sus rutas `pkg-config`, localiza `libwpe` y `WPEBackend-fdo`, valida filesystem, storage host, TLS, fuentes y un servidor/cliente loopback opcional. `diagnose_wpe_minibrowser.py` localiza automáticamente `MiniBrowser` en rutas conocidas, inspecciona `file`, arquitectura ELF, `ldd`, símbolos dinámicos, `DT_NEEDED`, bibliotecas del bundle, prefijo WPE y un arranque acotado opcional. `run_wpe_smoke.sh` conserva la validación SHA-256 de los tres fixtures, prepara `LD_LIBRARY_PATH`, registra backend/display, detecta dependencias dinámicas faltantes y no infiere capacidades funcionales a partir de un simple arranque.

Resultados independientes reproducibles del bloque:

| Componente | Estado | Alcance demostrado |
|---|---|---|
| Adaptador software surface/renderer | PASS | Superficie RGBA, resize, checksum y exportación PPM; no es renderer WPE completo |
| Presentación offscreen | PASS | Callback de frame y exportación software PPM |
| Event loop host | PASS | Cola FIFO y despacho de tareas |
| Input host | PASS | Cola y callback de eventos sintéticos; input WPE real sigue backend-dependiente |
| Filesystem/storage host | PASS | Escritura/lectura temporal y almacenamiento host con rechazo de claves inseguras |
| Fuentes | AVAILABLE | `fc-list` presente; no demuestra carga de fuentes por WebCore |
| TLS | PASS | Inicialización del contexto TLS host/OpenSSL; no demuestra networking WebCore |
| Networking | PASS | Solo servidor/cliente loopback con `--network`; red externa no se ejecuta |
| libwpe/WPEBackend-fdo | PASS | Bibliotecas públicas localizadas en `/tmp/wpe-prefix` |
| MiniBrowser automático | NOT_RUN | No existe candidato enlazado |
| Smoke page1→page2→page3 | NOT_RUN | Se validan fixtures, pero no se invoca ningún WPE runtime |
| Regresión host existente | BLOCKED | El harness `basic_capabilities.js` no está materializado en el sparse checkout |

El resultado `offscreen-core: PASS` se limita al adaptador host software del kit y no se presenta como ejecución de WebKit/WPE. El resultado de WebKitGTK continúa separado como baseline; ninguna capacidad DOM/CSS/JavaScript/eventos/formularios/SVG/Canvas/localStorage/navegación se marca como PASS para WPE hasta disponer de un MiniBrowser enlazado.

El camino de integración queda preparado como: `MiniBrowser` localizado → inspección ELF/ABI/dependencias → prefijo `libwpe`/`WPEBackend-fdo` y entorno → backend/display → arranque acotado → fixtures page1/page2/page3 → assertions funcionales y comparación independiente contra GTK. Si falla cualquier etapa previa, el estado se registra como `BLOCKED` o `NOT_RUN`, nunca como PASS implícito.


## Fase de validación preparada: assertions y runner headless

Se añadió un contrato explícito en `homebrew/fixtures/wpe-expected-assertions.json`. El contrato exige, por etapa, DOM, CSS, Flexbox, Grid, JavaScript, eventos, formularios, SVG, imágenes, Canvas, localStorage, historial y navegación. El resultado funcional debe ser emitido por el proceso en una línea `WPE_SMOKE_ASSERTIONS=<json>`; sin esa línea el runner clasifica el proceso como `BLOCKED`, aunque haya arrancado.

`tools/run_wpe_headless.py` ejecuta una sola sesión comenzando en `page1.html`, configura `WPE_BACKEND=fdo`, `WPE_RENDERER=software` y `LIBGL_ALWAYS_SOFTWARE=1` cuando se solicita `--headless`, registra arquitectura, SHA-256 del binario, `ldd`, librerías del prefijo, entorno, tiempos y salidas. No usa Xvfb y no afirma que software offscreen sea equivalente a una ejecución WPE funcional.

`tools/compare_wpe_smoke.py` compara exclusivamente assertions explícitas con el contrato esperado. `tools/render_wpe_report.py` genera el informe Markdown a partir de los JSON del runner y comparador. `tools/test_wpe_validation.py` cubre ausencia de MiniBrowser, comparación sin assertions y coincidencia exacta del contrato; sus casos son pruebas del tooling, no resultados WebKit.

Estado ejecutado en este workspace:

```text
FIXTURE_HASH_VALIDATION = PASS
VALIDATION_UNIT_TESTS = PASS (3 tests)
WPE_MINIBROWSER_DISCOVERY = NOT_RUN (no binary found)
WPE_HEADLESS_RUNTIME = NOT_RUN
WPE_ASSERTION_COMPARISON = NOT_RUN (no actual assertions)
WPE_HTML_SMOKE = NOT_RUN
```

La ausencia de MiniBrowser no se transforma en `BLOCKED` de fixture ni en PASS implícito. Cuando aparezca el binario, el flujo reproducible será `run_wpe_headless.py` → `compare_wpe_smoke.py` → `render_wpe_report.py`, y solo un JSON con todas las assertions coincidentes podrá producir `PASS` funcional.
