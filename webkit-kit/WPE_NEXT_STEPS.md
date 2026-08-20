# Ruta posterior a MiniBrowser WPE

Este documento define una secuencia de validación y no afirma que ninguna etapa futura esté completada.

## Etapa 1: smoke host controlado

Ejecutar `webkit-kit/tools/diagnose_wpe_minibrowser.py /ruta/a/MiniBrowser` para inspeccionar ELF, arquitectura, `ldd`, símbolos dinámicos y disponibilidad de `pkg-config`. Después ejecutar `webkit-kit/tools/run_wpe_smoke.sh --minibrowser /ruta/a/MiniBrowser --output resultado.json`. El harness verifica hashes de page1/page2/page3 y registra cada invocación. Si no existe MiniBrowser, el resultado correcto es `NOT_RUN`; si el proceso arranca pero no entrega aserciones funcionales, el resultado es `STARTED_ONLY`.

## Etapa 2: backend WPE real

Repetir el diagnóstico con el entorno de display y backend que realmente se utilice, por ejemplo Wayland/X11 o el backend FDO disponible. Registrar `WPE_BACKEND`, `WPE_RENDERER`, `DISPLAY`, `WAYLAND_DISPLAY`, `XDG_RUNTIME_DIR`, versiones de `libwpe` y `WPEBackend-fdo`, y las líneas de `ldd`. Un proceso que abre una ventana no demuestra por sí solo DOM, layout, JavaScript o almacenamiento; esos resultados deben provenir de aserciones explícitas del harness.

## Etapa 3: validación funcional

Para declarar `PASS`, el ejecutable debe producir resultados observables para DOM, CSS/Flexbox/Grid, JavaScript, eventos, formularios, SVG/imágenes, Canvas, localStorage, navegación page1→page2→page3 e historial. La matriz `WPE_GTK_TO_WPE_CAPABILITY_MATRIX.md` define la evidencia mínima de cada capacidad. Los resultados GTK permanecen como baseline independiente.

## Etapa 4: identificación de interfaces de plataforma

Sólo después de demostrar el runtime host se debe inventariar qué contrato del backend se necesitaría para otra plataforma: surface/presentación, display/EGL o renderer, input, event loop, timers, filesystem, fuentes, networking, almacenamiento y sincronización. Cada interfaz debe clasificarse por código público WPE/WebKit y no por suposiciones sobre APIs Sony. Ninguna conclusión de host demuestra compatibilidad con firmware PS4 13.52.

## Política de artefactos

Guardar junto a cada ejecución el JSON del harness, `sha256sum` de fixtures y ejecutable, salida de diagnóstico, versión de fuentes y dependencias. No añadir árboles de build, objetos, bibliotecas generadas ni workspaces temporales al repositorio. No ejecutar clean ni modificar el workspace de compilación externo.

