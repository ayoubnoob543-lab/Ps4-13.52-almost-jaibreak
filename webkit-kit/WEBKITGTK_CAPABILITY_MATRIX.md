# Matriz WebKitGTK 2.52.3 y migración conceptual a WPE

## Resultado ejecutado

El target `modern-webkit-smoke` carga tres páginas HTML locales con WebKitGTK 4.1 versión `2.52.3-0ubuntu0.24.04.1`, ejecutado bajo Xvfb. La cadena no es un stub: el documento se procesa por WebKit/WebCore, JavaScript se ejecuta en JavaScriptCore y la vista se gestiona mediante GTK/GLib.

La ejecución reproducible es:

```sh
make -C webkit-kit/homebrew clean all
cat webkit-kit/homebrew/build/host/modern-webkitgtk-output.txt
```

La salida observada fue:

```text
stage=1 result={"dom":true,"event":true,"text":"clicked","flex":true,"grid":true,"animation":true,"form":true,"svg":true,"image":true,"canvas":true,"storage":true}
stage=2 result={"page":true,"storage":true,"dom":"page2-ok","js":true,"event":true}
stage=3 result={"page":true,"history":true,"dom":true,"js":true}
```

## Capacidades validadas

| Capacidad | Evidencia | Capa principal | Estado |
|---|---|---|---|
| DOM complejo | Dos `article` dentro de `section`, consultas y mutación | WebCore | `VALIDATED` |
| Flexbox | `getComputedStyle(...).display == flex` | WebCore/layout | `VALIDATED` |
| CSS Grid | `getComputedStyle(...).display == grid` | WebCore/layout | `VALIDATED` |
| CSS animation | `animationName == pulse` | WebCore/style/timing | `VALIDATED` |
| JavaScript | JSON, funciones, propiedades y scripts inline | JavaScriptCore | `VALIDATED` |
| Eventos | `click()` y evento `custom` | WebCore DOM/events + JSC | `VALIDATED` |
| Formularios | `required`, `minlength`, `checkValidity()` | WebCore/forms | `VALIDATED` |
| SVG | Elemento SVG y `rect` | WebCore/SVG | `VALIDATED` |
| Imagen | Imagen SVG mediante data URI y `complete` | WebCore/loader/image decoder | `VALIDATED` |
| Canvas | `getContext('2d')`, `fillRect`, `toDataURL` | WebCore/canvas + graphics backend | `VALIDATED` |
| localStorage | Escritura en page1 y lectura en page2 | WebCore/storage + WebsiteDataStore | `VALIDATED` |
| Navegación | `file://` page1→page2→page3 | WebKitWebView + WebCore loader | `VALIDATED` |
| History | Objeto `history` presente en page3 | WebCore navigation/history | `VALIDATED` |

La prueba evita red y TLS; por ello la navegación validada es local. No se afirma que networking, cookies remotas, Service Workers, WebSockets, audio, video o aceleración GPU funcionen en este entorno.

## Qué depende de GTK y qué se mantiene en el engine

WebCore mantiene parsing HTML/XML, DOM, CSS, layout, SVG, canvas, formularios, eventos, navegación interna, storage y decodificación integrada. JavaScriptCore mantiene parser, bytecode, VM, GC, built-ins, JIT cuando está habilitado y la API de ejecución.

WebKitGTK aporta el objeto `WebKitWebView`, integración con GTK3/GDK, ciclo de vida del widget, señales GObject, selección de backend gráfico GTK/Cairo/EGL, integración con GLib, políticas de red mediante libsoup, configuración de `WebKitWebsiteDataManager`, impresión, permisos y bridges GObject. Algunas funciones pertenecen a WebKit/WebKit2 y no a GTK, aunque la aplicación GTK las expone mediante señales y objetos.

El `file://` smoke no ejercita necesariamente todas las integraciones de GTK. Xvfb proporciona un display virtual y el entorno mostró advertencias de DRI3; el fallback de renderizado fue suficiente para completar la prueba de DOM/CSS/Canvas.

## WPE como alternativa de plataforma

WPE separa el engine WebKit de la integración de ventana y compositor. En el commit público inspeccionado de libwpe `445a0b5579aba7eca619973ca476bb5291a85cf5`, las interfaces relevantes son públicas y están en `view-backend.h`, `renderer-host.h`, `renderer-backend-egl.h`, `input.h`, `loader.h`, `pasteboard.h` y `process.h`.

| Interfaz libwpe pública | Responsabilidad de backend |
|---|---|
| `wpe_view_backend_*` | Crear/destruir vista, tamaño, escala, cliente, dispatch de teclado/puntero/touch/axis y pointer lock |
| `wpe_renderer_host_*` | Crear host de renderer y clientes |
| `wpe_renderer_backend_egl_*` | Display/plataforma EGL, targets, ventana nativa, resize, frame lifecycle y `frame_complete` |
| `wpe_input_*` | Estructuras de teclado, puntero, touch, axis y conversiones key/unicode |
| `wpe_loader_*` | Cargar la implementación de backend por nombre |
| `wpe_pasteboard_*` | Portapapeles público |
| `wpe_gamepad_*` | Gamepad opcional |
| `wpe_process_*` | Hooks de proceso separados |

En esta máquina no existe un paquete `libwpe-1.0-dev` en los repositorios configurados y no se compiló WPE. Los headers públicos se inspeccionaron desde el repositorio oficial y se conservaron sus nombres y commit en `wpe-interface-findings.txt`.

## Requisitos de un backend OpenOrbis futuro

Un backend para una plataforma distinta tendría que proporcionar una superficie o target de presentación, lifecycle de frames, sincronización, input, escala y resize. También necesitaría integrar event loop, timers y threads con las primitivas públicas disponibles; filesystem y WebsiteDataStore; carga de URLs, certificados y networking; fuentes y text shaping; decodificación de imágenes; memoria compartida y, si se habilita JIT, memoria ejecutable con las garantías de permisos y coherencia requeridas por JSC.

En la ruta EGL tendría que existir una forma pública de obtener display/window o una ruta offscreen. Si el target no ofrece EGL/GLES compatible, sería necesario otro backend de compositor o software rendering, pero no se puede afirmar su existencia sin documentación y headers del target. Input y clipboard tendrían que mapearse a las estructuras públicas de libwpe. Audio, video, gamepad y aceleración no son requisitos mínimos del smoke, pero forman parte del navegador completo.

OpenOrbis no proporciona por sí solo WebKit, WebCore, JSC, libwpe, un backend WPE, una ABI C++ de WebKit ni una garantía de memoria/JIT para este caso. La compatibilidad con PS4 13.52 permanece `UNKNOWN`; no se usaron SDK Sony, módulos `.sprx`, offsets, exploits, payloads, ROP/JOP ni ABI privada.

## Comparación y recomendación

WebKitGTK fue la ruta con mayor evidencia ejecutable: se compiló un navegador mínimo y se validaron once capacidades reales. WPE ofrece una separación arquitectónica mejor para una plataforma embebida, pero en este entorno no está instalado y no se demostró aún una aplicación WPE host.

La recomendación es mantener **WebKitGTK moderno como baseline funcional host** y modelar la futura portabilidad sobre una capa conceptual WPE, sin iniciar todavía una implementación OpenOrbis. Primero habría que obtener un toolchain/sysroot público reproducible y demostrar un backend gráfico/input mínimo; después se podría evaluar WPE. WebKit-601/JSCBRIDGE debe permanecer fuera de la ruta principal porque su proveedor no es recuperable desde el OSS consultado.

## Dependencias y bloqueos

El paquete WebKitGTK 2.52.3 y sus headers están disponibles. `xvfb` y `webkit2gtk-driver` están instalados. `libwpe-1.0-dev` no está disponible en los repositorios configurados. La compilación local del engine WebKit completo desde fuentes sigue separada: el prototipo enlaza contra el engine de distribución y no reclama haber reconstruido el engine desde cero.
