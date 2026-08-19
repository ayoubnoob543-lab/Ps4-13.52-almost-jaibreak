# Prototipo WebKitGTK moderno

## Versión y procedencia

El prototipo usa el paquete público de Ubuntu 24.04:

```text
libwebkit2gtk-4.1-0      2.52.3-0ubuntu0.24.04.1
libwebkit2gtk-4.1-dev    2.52.3-0ubuntu0.24.04.1
webkit2gtk-driver        2.52.3-0ubuntu0.24.04.1
```

La versión se fija mediante el paquete de distribución y `pkg-config webkit2gtk-4.1`. En esta máquina no fue viable compilar el engine WebKitGTK completo desde fuentes: no hay repositorios `deb-src` habilitados para obtener el source package, quedan aproximadamente 3,1 GB libres y el build completo de WebKit exige bastante más espacio temporal que el disponible. Por tanto, el engine usado aquí es una build pública de distribución, no una compilación local de WebKit desde sus fuentes.

El programa navegador sí se compila localmente contra los headers y bibliotecas públicas instaladas. No se mezcla con el árbol histórico 601-1300 ni con JSCBRIDGE.

## Arquitectura validada

| Capa | Componente | Estado |
|---|---|---|
| Aplicación | `modern_webkitgtk_smoke.c` | Compilada localmente |
| API navegador | WebKitGTK 4.1 / `WebKitWebView` | Disponible y ejecutada |
| Engine | WebKit moderno | Proporcionado por el paquete público 2.52.3 |
| DOM/layout/CSS | WebCore interno del engine | Validado por evaluación DOM y estilo calculado |
| JavaScript | JavaScriptCore integrado en WebKitGTK | Validado mediante `evaluate_javascript` |
| Widgets/event loop | GTK3 + GLib | Ejecutado bajo Xvfb |
| Networking | No requerido en esta prueba; navegación local `file://` | No se afirma red |
| Render backend | Cairo/GTK y EGL del paquete | Inicializado bajo Xvfb; DRI3 no disponible, se usa fallback |
| Target PS4/Orbis | Ninguno | `MISSING/UNKNOWN` |

## Prueba funcional real

El fixture `page1.html` contiene un elemento DOM, CSS con dimensiones explícitas y un botón con handler JavaScript. El navegador carga el documento, dispara `click()` en el botón y evalúa:

```text
body.dataset.domReady
button.dataset.clicked
box.textContent
getComputedStyle(box).width
getComputedStyle(box).height
```

La salida validada es:

```text
stage=1 result=yes|yes|clicked|120px|40px
```

Después se navega a `page2.html` mediante `webkit_web_view_load_uri`. La segunda página establece una variable JavaScript y el navegador verifica URL, DOM y estado JS:

```text
stage=2 result={"url":true,"dom":"navigation-ok","js":true}
```

Esto demuestra en host Linux la cadena **carga HTML → parsing DOM → CSS/layout computado → ejecución JavaScript → evento click → navegación → nuevo DOM/JS**. No es un test de PS4 ni del WebKit histórico 601.

La ejecución reproducible es:

```sh
make -C webkit-kit/homebrew clean all
cat webkit-kit/homebrew/build/host/modern-webkitgtk-output.txt
```

La prueba necesita `xvfb-run` porque el entorno no tiene una sesión gráfica interactiva. Las advertencias de DRI3 sólo indican que no hay GPU acelerada disponible en Xvfb; no impiden la evaluación DOM/CSS/JS.

## Por qué no es todavía un port OpenOrbis

Para sustituir GTK en una futura plataforma pública habría que conservar la separación entre WebKit/WebCore/JSC y la capa de plataforma. Habría que proporcionar, como mínimo, event loop y fuentes de eventos, threads/timers, allocator y memoria ejecutable si se habilita JIT, filesystem, URL loading/networking/TLS, cookies/cache/storage, fonts, imágenes, audio opcional, surfaces/buffers, composición/presentación, input y telemetría/error logging.

WPE ofrece una abstracción más adecuada para esa separación mediante `libwpe` y un backend. Sin embargo, portar WebKitGTK o WPE a OpenOrbis requeriría un toolchain/sysroot público verificable, una ABI target compatible, un backend gráfico/input, primitivas de memoria y threads, y un plan para todas las dependencias GLib/ICU/libsoup/Cairo/GStreamer. OpenOrbis no demuestra por sí mismo que esas interfaces existan para WebKit.

No se han asumido compatibilidad con PS4 13.52, módulos Sony, `.sprx`, SDK retail, offsets, exploits, payloads, ROP/JOP ni ABI privada.

## Limitación de compilación del engine

El resultado de esta fase es una **build local del navegador contra un engine WebKitGTK 2.52.3 precompilado por Ubuntu**, no una compilación local del engine completo. La compilación desde fuentes queda como trabajo separado y está bloqueada aquí por la combinación de source package no disponible vía `deb-src`, espacio insuficiente para un build grande y ausencia de una receta de build fijada dentro del repositorio.
