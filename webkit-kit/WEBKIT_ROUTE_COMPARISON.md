# Comparación de rutas OSS para un WebKit/JSC funcional

## Alcance y criterio

Este análisis busca una ruta que produzca un motor funcional sin depender de `JSCBRIDGE`, SDK retail, módulos Sony, offsets, ABI privados ni payloads. Se separan tres objetivos que no son equivalentes: ejecutar JavaScript, ejecutar WebCore/DOM y disponer de un navegador WebKit completo con backend gráfico, red, almacenamiento y event loop.

La evidencia local incluye el corpus `PS4OSSCode` fijado en `d636699770323d7968a2c37955aa513bda5f8a37`, el árbol materializado de `WebKit-601-1300`, un build GTK histórico configurado con CMake y una instalación pública `JavaScriptCoreGTK 4.1` versión `2.52.3`. El host tiene `cc/gcc`, CMake, Ninja, Ruby, Perl, Python y `pkg-config`; no tiene `clang/clang++`, Meson ni un checkout OpenOrbis local. El espacio libre observado fue aproximadamente 3,3 GB.

## Opciones comparadas

| Ruta | JavaScript | WebCore/DOM | WebKit completo | JIT | Build host | Adaptación posterior a Orbis | Bloqueos actuales |
|---|---|---|---|---|---|---|---|
| PS4OSS WebKit-601-1300 GTK | Sí en teoría | Sí en teoría | Sí en teoría | Sí, pero condicionado por el port | CMake configura; compilación JSC se detiene | Baja-media | `bridge/Memory.h`, headers JSCBRIDGE, `JscBridge_vm`, `SceJitBridge` |
| PS4OSS WebKit-616-1250/1300 GTK | Sí en teoría | Sí en teoría | Sí en teoría | Dependiente de revisión/port | No se obtuvo una configuración completa reproducible | Baja-media | No se ha demostrado que elimine el contrato Manx/JSCBRIDGE; dependencias históricas y port incompleto |
| WebKitGTK OSS moderno | Sí | Sí | Sí | Integrado por upstream | Baja para Orbis; alta para host Linux | GTK/GLib/Cairo/Wayland/X11 y numerosos servicios host |
| WPE WebKit OSS moderno | Sí | Sí | Sí | Integrado por upstream | Media; requiere WebKit, libwpe, backend y Cog opcional | La mejor separación arquitectónica para un backend nuevo | Backend target, GL/EGL o software rendering, GLib/GStreamer/ICU y toolchain target |
| JavaScriptCore GTK instalado | Sí | No es un navegador | No | Sí según paquete | **Confirmado: smoke real host** | No es port target; sólo referencia de engine/API | No entrega WebCore/WebKit2 ni PS4 ABI |
| QuickJS | Sí | No | No | No equiparable al JIT JSC | Alta; pocas fuentes C, MIT | Alta para una app JS pequeña | No DOM, WebCore, WebKit2 ni compatibilidad web completa |
| Duktape | Sí parcial | No | No | No equivalente | Muy alta; C portable, MIT | Alta para recursos limitados | ES5/E5.1 principalmente, sin DOM/WebCore/WebKit2 |
| OpenOrbis directo con WebKit | Depende del motor | Depende | No demostrado | Depende del engine | Toolchain público, pero no presente localmente | Es la ruta target necesaria | Faltan sysroot target, port de WebKit, ABI pública suficiente, backend y dependencias |

## Evidencia de compilabilidad

### WebKit-601-1300

La configuración GTK histórica terminó correctamente después de instalar dependencias públicas y corregir una inclusión estándar de CMake que el módulo antiguo presuponía. CMake generó targets reales de `JavaScriptCore`, `WTF`, `WebCore` y WebKit.

La compilación real de JSC se detuvo en la primera dependencia específica del corpus:

```text
fatal error: bridge/Memory.h: No such file or directory
```

La cabecera no existe en el checkout, en los objetos Git ni en las variantes OSS públicas comparadas. El árbol también exige `JSCBridge.h`, `JSCBridge_comp.h`, `JSCBridge_vm.h`, `VTableMap.h`, `VirtualMethodCall.h`, allocators y las bibliotecas `JscBridge_vm`/`SceJitBridge`. No se creó ningún sustituto.

Por tanto, 601-1300 es una referencia histórica útil para arquitectura y diferencias, pero no es una base compilable completa con el corpus público disponible.

### JavaScriptCore GTK host

El prototipo existente compila con la API C pública de JavaScriptCore GTK 4.1 y ejecuta un smoke real que verifica `Array.prototype.map`, `Uint32Array` y `JSON.parse`. Su salida validada es:

```json
{"engine":"JavaScriptCore-GTK-host","passed":true,"value":"true"}
```

Esto prueba ejecución real de JSC host, no WebCore ni WebKit PS4.

### GTK y WPE

La documentación oficial de WebKitGTK mantiene un script público de dependencias para `apt-get`, `dnf`, `pacman` y Homebrew [1]. WPE documenta una arquitectura separada en WebKit, `libwpe`, `WPEBackend-fdo` y Cog, además de recetas OpenEmbedded/Yocto para cross-compilación [2]. Esta separación evita que el engine dependa de una interfaz propietaria equivalente a JSCBRIDGE, aunque un backend Orbis nuevo seguiría siendo necesario.

### Alternativas independientes

QuickJS es MIT, pequeño y embebible, con unas pocas fuentes C y sin dependencias externas para un programa sencillo [3]. Es una buena ruta para una aplicación PS4 de scripting, pero no implementa DOM, WebCore ni WebKit2.

Duktape es MIT, portable y compacto, integrable añadiendo `duktape.c`, `duktape.h` y `duk_config.h` [4]. Su compatibilidad principal es ES5/E5.1 con partes de ES2015/2016; no es una alternativa de navegador WebKit.

## Compatibilidad C++/ABI y JIT

El código histórico 601-1300 mezcla interfaces C++ de JSC con el contrato externo JSCBRIDGE para allocator compartido, vtables, VM y memoria ejecutable/split-process. Esto significa que no basta con hacer que `Memory.h` compile: se necesitarían layouts, símbolos, reglas de ownership, llamadas virtuales, límites de memoria ejecutable y el proveedor de link completo.

WebKitGTK y WPE modernos compilan con una ABI de host Linux documentada por sus headers públicos y GLib/GObject. Esa ABI no es transferible a Orbis automáticamente. QuickJS y Duktape reducen mucho el riesgo porque su API principal es C y no exigen una ABI C++ grande, pero sacrifican WebCore y compatibilidad web.

El JIT en JSC es una dependencia adicional para un target no POSIX estándar: requiere allocator ejecutable, permisos de memoria, señales/excepciones, threads, atomics y garantías de coherencia de caché. En un port público a OpenOrbis sólo podría afirmarse tras disponer del toolchain/sysroot real, APIs públicas equivalentes y pruebas target; no se deben rellenar estos huecos con funciones Sony.

## Gráficos, filesystem, threads y networking

WebKitGTK resuelve estas áreas mediante GLib, Cairo, GTK, GDK, libsoup, SQLite, ICU, fontconfig, freetype, libjpeg/png/webp y, según configuración, OpenGL/EGL/GStreamer. Es la ruta más directa para un navegador funcional en Linux host.

WPE mueve la interfaz visual al backend: `libwpe` define la abstracción y un backend proporciona superficies, input, buffers y presentación. Esto es más apropiado que GTK para una futura plataforma embebida, pero no elimina la necesidad de implementar un backend público de Orbis ni de disponer de una pila gráfica pública compatible.

QuickJS y Duktape dejan filesystem, threads, timers, networking, TLS y gráficos a la aplicación. Eso hace viable una aplicación homebrew mínima, pero no produce un navegador hasta que se escriban DOM, fetch, layout, CSS, parsing HTML, compositing y almacenamiento.

## OpenOrbis

OpenOrbis es una base legal y pública para compilar homebrew PS4 y aporta toolchain, headers, stubs de biblioteca, herramientas ELF/empaquetado y headers EGL/GLES públicos [5]. No aporta WebKit/JSC, WebCore, WebKit2, un backend WPE, el contrato JSCBRIDGE de 601-1300 ni una garantía de ABI para un port histórico.

La ruta Manx del árbol 601-1300 requiere un target `ORBIS`, compiladores `orbis-clang`/`orbis-clang++`, sysroot, `manx/System.h`, stubs Sce específicos, shaders precompilados, EGL target, `LIBJSCBRIDGE_INCLUDE_DIRS`, `JscBridge_vm` y `SceJitBridge`. Estos requisitos están clasificados como `MISSING` o `UNKNOWN`; no se sustituyeron.

## Recomendación única

La ruta técnicamente más viable es:

> **Usar WebKitGTK moderno como referencia funcional host y evolucionar la integración hacia WPE WebKit para el futuro port, manteniendo QuickJS como plan B de scripting si el objetivo PS4 se reduce a una aplicación JavaScript.**

El primer paso operativo debe ser estabilizar un build reproducible de WebKitGTK/WPE moderno en un workspace separado, con fuentes y dependencias fijadas. El segundo debe ser construir una aplicación WPE mínima en host usando un backend público existente. El tercero debe ser definir una interfaz de backend abstracta y comprobar qué partes podrían implementarse con OpenOrbis público. Sólo después de disponer de un sysroot/toolchain OpenOrbis reproducible tendría sentido iniciar un port target.

No recomiendo invertir más en 601-1300 como base compilable hasta recuperar una fuente legítima del proveedor JSCBRIDGE. No recomiendo QuickJS o Duktape como sustitutos de WebKit: son rutas válidas para scripting, no para compatibilidad web.

## Esfuerzo estimado y bloqueos

| Etapa | Resultado | Esfuerzo relativo | Bloqueo principal |
|---|---|---:|---|
| JSC GTK host existente | Engine JS real | Bajo | Ya resuelto en el prototipo |
| WebKitGTK moderno host | Navegador completo Linux | Medio-alto | Árbol/dependencias grandes y espacio |
| WPE host con backend existente | Navegador modular Linux | Alto | WebKit + libwpe + backend + runtime |
| Backend WPE para OpenOrbis | Primer target PS4 público | Muy alto | sysroot, ABI, gráficos, input, filesystem, networking |
| WebKit-601-1300 público | Build histórica exacta | Bloqueado | Proveedor JSCBRIDGE ausente |
| QuickJS en OpenOrbis | App JS ligera | Medio | toolchain y bindings de aplicación |
| Duktape en OpenOrbis | App JS mínima | Bajo-medio | toolchain y bindings de aplicación |

Los porcentajes no se presentan como cobertura falsa: el navegador completo PS4 no está demostrado. La parte funcional demostrada hoy es JSC host; la ruta WebKit histórica está configurada pero bloqueada; la ruta OpenOrbis está disponible como toolchain público conceptual, no como build local verificada.

## Referencias

[1]: https://github.com/WebKit/webkit/blob/main/Tools/gtk/install-dependencies "WebKitGTK official dependency installer"
[2]: https://wpewebkit.org/about/get-wpe.html "WPE WebKit — Get WPE"
[3]: https://bellard.org/quickjs/ "QuickJS official site and license"
[4]: https://duktape.org/ "Duktape official site and integration guide"
[5]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain "OpenOrbis PS4 Toolchain"
[6]: https://github.com/FreeBSDKernel9-0/PS4OSSCode "PS4OSSCode public corpus"
