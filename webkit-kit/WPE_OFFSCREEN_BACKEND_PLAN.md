# Backend WPE mínimo/offscreen: plan verificable

## Estado actual

En este host no hay `MiniBrowser`, `libwpe`, `wpe-webkit-2.0` ni `WPEBackend-fdo` instalados mediante paquetes del sistema. Por esa razón no se ha declarado ningún runtime WPE PASS ni se ha iniciado otra compilación WPE/WebKit. La ruta funcional ejecutada en esta iteración es el fallback público WebKitGTK 2.52.3, etiquetado separadamente.

## Contrato público que debe cubrir un backend

| Área | Responsabilidad del engine/port | Responsabilidad del backend |
|---|---|---|
| Event loop | Programación de tareas y timers mediante GLib/WebKit | Integración del loop con display/window system si procede |
| Surface | WebCore/compositor produce contenido | Crear surface, elegir EGL/GL/software y presentar |
| Display | WebKit conoce el port | Conectar Wayland/X11/DRM/offscreen y gestionar lifecycle |
| Input | WebCore procesa eventos recibidos | Convertir teclado, puntero, touch y foco al contrato WPE |
| Presentación | Compositor prepara frames | Commit/swap, sincronización y resize |
| Render | WebCore/GraphicsContext y renderer | Contexto GL/EGL o ruta software y buffers |
| Filesystem/storage | WebCore/WebKit storage APIs | Directorios, permisos y persistencia del perfil |
| Network | WebKit network process/libsoup | Conectividad y política de sandbox/entorno |
| Fuentes | WebCore selecciona y mide fuentes | Fontconfig/Pango/fuentes disponibles en el sistema |

## Perfil offscreen mínimo

Un perfil offscreen legítimo debe comenzar con una surface de tamaño fijo y renderer software o EGL pbuffer, sin input físico. El harness debe inyectar o provocar sólo eventos DOM internos de los fixtures y debe separar esos resultados de la presentación gráfica real. Para declarar renderizado PASS se necesita una evidencia de frame, píxel o assertion del engine; que el proceso se mantenga vivo no es suficiente.

El runner `run_wpe_smoke.sh` no fabrica ese backend: verifica fixtures, inspecciona el runtime y ejecuta MiniBrowser sólo cuando el usuario proporciona un binario existente. `run_runtime_matrix.sh` mantiene WPE como resultado autoritativo y GTK como fallback explícito.

## Interfaces pendientes para una futura plataforma

Las partes que quedarían por implementar después de un runtime WPE host probado son surface/presentación, display lifecycle, input injection, sincronización de frames, renderer EGL/software, timers/event loop específicos, filesystem de perfil, fuentes, networking y sandboxing. La existencia de `libwpe` o de un backend FDO host no demuestra que una plataforma distinta implemente esas interfaces correctamente.

## Política de evidencia

`PASS` exige ejecución real y salida reproducible. `INSPECTED_ONLY` significa que ELF/dependencias fueron inspeccionados. `STARTED_ONLY` significa que el proceso arrancó sin assertions funcionales. `NOT_RUN` significa que falta MiniBrowser o el runtime. `BLOCKED` significa que una dependencia o backend impidió continuar. No se atribuyen resultados GTK al runtime WPE.

