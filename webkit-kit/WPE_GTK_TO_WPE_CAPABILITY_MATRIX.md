# Matriz WebKitGTK → WPE

**Regla de evidencia:** `PASS` sólo significa probado realmente en WPE con el binario y backend correspondientes. Los resultados WebKitGTK son baseline separado y no se transfieren automáticamente a WPE.

| Capacidad | Capa principalmente responsable | GTK/WebKitGTK específico | WPE/backend específico | Estado WPE actual | Evidencia requerida para PASS |
|---|---|---|---|---|---|
| DOM | WebCore | No es requisito conceptual | No es requisito conceptual | NOT_TESTED | Aserciones DOM en page1/page2/page3 ejecutadas por MiniBrowser |
| JavaScript | JavaScriptCore + bindings WebCore | Integración GLib/GTK sólo en APIs de aplicación | Integración WPE/GLib y proceso | NOT_TESTED | Resultado explícito de scripts de fixtures |
| CSS | WebCore | No | No, salvo presentación/compositor | NOT_TESTED | Aserciones de estilos computados |
| Flexbox/Grid | WebCore/layout | No | No | NOT_TESTED | Aserciones de layout/estilo en fixture |
| Eventos DOM | WebCore/EventHandler | Adaptación de input GTK en WebKitGTK | Eventos de input entregados por backend WPE | NOT_TESTED | Evento click/custom y estado observado |
| Formularios | WebCore | Widget/input method GTK puede influir en interacción | Input/foco del backend WPE | NOT_TESTED | Validación y submit observados |
| SVG/imágenes | WebCore/ImageDecoder/graphics | Cairo/GTK puede intervenir en superficie | Cairo/GL/EGL/compositor según backend | NOT_TESTED | Decodificación y dimensiones/estado de carga |
| Canvas | WebCore + aceleración opcional | Contexto y superficie GTK | EGL/GL/surface WPE y renderer | NOT_TESTED | Píxel/estado canvas o assertion explícita |
| localStorage | WebCore storage + WebKit process | Directorios/configuración de usuario GTK | Filesystem/configuración del port WPE | PARTIAL: storage host auxiliar PASS; WebCore localStorage WPE NOT_TESTED | Escritura, navegación y lectura posterior |
| Navegación | WebKit/WebCore network process | APIs WebKitGTK y señales GTK | APIs WPE/WebKit y event loop | NOT_TESTED | page1→page2→page3 y códigos de proceso |
| Historial | WebKit/WebCore page/session | API de navegación GTK | API WPE equivalente/event loop | NOT_TESTED | `history`/back-forward assertion |
| Event loop | GLib/WebKit process model | Integración GTK main context | Integración GLib + backend WPE | PARTIAL: loop host auxiliar PASS; WPE NOT_TESTED | Diagnóstico de runtime y ejecución real WPE |
| Ventana/surface | Backend | GDK/GTK window, display, events | libwpe + WPEBackend-fdo | PARTIAL: surface RGBA software auxiliar PASS; WPE BLOCKED | MiniBrowser arranca con backend real |
| Presentación | WebCore/compositor + backend | GTK/GDK surface | EGL/Wayland/X11/DRM según backend | PARTIAL: frame callback/checksum auxiliar PASS; WPE NOT_TESTED | startup y render surface observables |
| Input | WebCore event plumbing | GTK/GDK input | WPE backend input injection | PARTIAL: cola/input callback auxiliar PASS; WPE NOT_TESTED | evento fixture producido por backend |
| Red | WebKit network process/libsoup | Integración WebKitGTK | Igual WebKit/libsoup, configuración WPE | NOT_TESTED | Sólo probar si harness define red controlada |
| Fuentes | WebCore/Pango/Fontconfig | GTK/Pango integration | Dependencias Linux del port/backend | NOT_TESTED | Render/medición en runtime |

## Lectura arquitectónica

El abandono de GTK elimina la ventana y el adaptador de eventos GTK, pero no elimina WebCore, JavaScriptCore, WebKit multiproceso, almacenamiento, networking ni los decodificadores. WPE proporciona el contrato de port y el backend proporciona superficie, display, input, EGL/GL y presentación. En una futura plataforma no-GTK se tendría que sustituir o implementar el backend y las partes de plataforma permitidas por el port; no se puede inferir compatibilidad con PS4 13.52 a partir de este host.

## Estado documentado

`WPE WebKit 2.52.6` está configurado en host y `libwpe 1.16.3`/`WPEBackend-fdo 1.16.1` están documentados como PASS de build independiente. `MiniBrowser`, el smoke WPE y la comparación automática GTK→WPE siguen `BLOCKED`/`NOT_TESTED` mientras no exista un ejecutable WPE enlazado.

