# Investigación de portabilidad WebKit/WPE

**Proyecto:** `firmware-lab`  
**Rama:** `webkit-ps4-1352-kit`  
**Alcance:** exclusivamente WebKit OSS, WPE, libwpe, WPEBackend-fdo y validación host.  
**Fecha del informe:** 2026-08-19  
**Autor:** Manus AI

## Resumen ejecutivo

La evidencia de código confirma que **WPE WebKit 2.52.6 separa el motor WebKit de la presentación gráfica**, pero no convierte WebKit en una biblioteca independiente de todas las plataformas. El contrato público entre el motor y el backend está en libwpe 1.16.3; el backend de referencia WPEBackend-fdo 1.16.1 implementa esa interfaz usando un stack Freedesktop/EGL/Wayland/SHM/DMABUF. La arquitectura es adecuada para estudiar una futura plataforma no-GTK, pero un backend alternativo tendría que resolver por separado presentación, superficies EGL o un camino offscreen, IPC entre procesos, eventos de entrada, sincronización de frames, memoria gráfica y servicios del sistema.

El estado real no permite afirmar todavía un runtime WPE funcional en Linux: libwpe y WPEBackend-fdo fueron compilados, y WebKit 2.52.6 fue configurado con `PORT=WPE` y `ENABLE_MINIBROWSER=ON`, pero MiniBrowser no llegó a enlazarse antes de que los recursos del workspace terminaran los compiladores. El smoke test GTK es un baseline independiente y no se presenta como resultado WPE. Por tanto, la cobertura end-to-end WPE sigue siendo **0 % demostrada**, mientras que la cobertura de contratos estáticos y configuración host es alta.

La recomendación es mantener WPE 2.52.6 como base principal, no volver a WebKitGTK y ejecutar en paralelo una ruta JSCOnly de bajo coste. JSCOnly puede validar JavaScriptCore, LLInt y JIT sin WebCore ni renderer; no sustituye la prueba del navegador, pero reduce el riesgo y produce evidencia útil mientras se consigue un workspace con más memoria, tiempo y disco.

## 1. Estado reproducible y procedencia

| Componente | Versión | Procedencia documentada | SHA-256 documentado | Estado real |
|---|---:|---|---|---|
| WPE WebKit | 2.52.6 | Tarball oficial WPE | `b2bafef2751625b7fdf530f230ff0f542ff0eeba3590c3a989d931b2a55c858e` | CMake configurado; enlace pendiente |
| libwpe | 1.16.3 | Tarball oficial WPE | `c880fa8d607b2aa6eadde7d6d6302b1396ebc38368fe2332fa20e193c7ee1420` | Compilado en prefijo temporal |
| WPEBackend-fdo | 1.16.1 | Tarball oficial WPE | `544ae14012f8e7e426b8cb522eb0aaaac831ad7c35601d1cf31d37670e0ebb3b` | Compilado; 53/53 tareas |
| WebKit tag | `webkitgtk-2.52.6` | GitHub WebKit | commit `4fb33923db2f945803df49546f75867980365c08` | Consultado selectivamente |
| WPE headers auditados | libwpe 1.16.3 | GitHub oficial libwpe | Tag `1.16.3` | Inventario estático PASS |

Los árboles temporales de la build anterior (`/tmp/wpewebkit-2.52.6-src`, `/tmp/wpewebkit-2.52.6-build` y prefijos temporales) ya no están presentes en el workspace actual. Esto no invalida los resultados históricos documentados, pero significa que la build completa no puede reanudarse en esta sesión sin recuperar la fuente oficial y disponer de más espacio. Un intento posterior de descarga del tarball se descartó porque el archivo parcial resultó corrupto; no se usó como fuente ni se incorporó al repositorio.

La validación del repositorio actual quedó así:

| Prueba | Resultado |
|---|---|
| Auditor estático `audit_wpe_interfaces.py` | PASS |
| `python3 -m py_compile` | PASS |
| Smoke seguro C host | PASS |
| Smoke JavaScriptCore-GTK | NOT_RUN/FAIL CONTROLADO: falta `javascriptcoregtk-4.1.pc` |
| Smoke WebKitGTK moderno | NOT_RUN: falta `webkit2gtk-4.1.pc` en esta sesión |
| `git diff --check` | PASS |
| Build completo WPE/MiniBrowser | BLOCKED_BY_WORKSPACE_RESOURCES |

## 2. Arquitectura confirmada

La documentación oficial define WPE como un port de WebKit para sistemas embebidos que no depende de un toolkit de interfaz como GTK. El motor prepara la representación compuesta de la página y libwpe proporciona el punto común con el backend; el backend recibe esa representación y la presenta en la aplicación [1]. La misma documentación indica que la entrada se entrega mediante libwpe porque WPE no proporciona un widget de toolkit [1].

El modelo 2.52.6 sigue siendo el modelo legacy de libwpe. La fuente `Source/WebKit/PlatformWPE.cmake` configura tres procesos auxiliares con nombres `WPEWebProcess`, `WPENetworkProcess` y `WPEGPUProcess`, además de la biblioteca `WPEWebKit-${WPE_API_VERSION}`. También agrega entry points Unix para cada proceso y genera headers forwarding de WPE y de la API GLib. La arquitectura, por tanto, es multiproceso y el backend no puede tratarse como una simple función de dibujo dentro del mismo proceso.

El artículo técnico de Igalia describe que el backend se carga mediante el símbolo `_wpe_loader_interface`, devuelve implementaciones para renderer host y targets EGL, y comparte descriptores para conectar el proceso de aplicación con cada WebProcess. El artículo es explícito en que este modelo queda obsoleto a partir de WPE/WebKit 2.54, cuando aparece WPE Platform; para la versión fijada 2.52.6 el contrato legacy de libwpe es el aplicable [3].

### Cadena de componentes

```text
Aplicación embebedora
        |
        | crea/configura view backend, inyecta input y recibe callbacks
        v
libwpe 1.16.3
        |
        | loader + renderer-host + EGL target/offscreen target + view backend
        v
WPEWebKit 2.52.6
        |
        +--> WebProcess: WebCore, layout, DOM, CSS, JS bindings, compositor
        +--> NetworkProcess: Soup/GLib, sockets, TLS, cookies, cache, storage de red
        +--> GPUProcess: ruta opcional/experimental de GPU/WebGL
        |
        v
WPEBackend-fdo 1.16.1 o backend alternativo
        |
        +--> EGL/GLES, Wayland/GBM/SHM/DMABUF, IPC y presentación host
        +--> traducción de teclado/puntero/touch y política fullscreen
        v
Renderer/presentación física o offscreen
```

Esta cadena muestra qué puede mantenerse al migrar de host y qué no. WebCore, JavaScriptCore, serialización, procesos y gran parte de la lógica de navegador pertenecen al motor. Display nativo, ventana, superficie, sincronización con la pantalla, input físico, transporte entre procesos y política de presentación pertenecen al integrador/backend.

## 3. Inventario exacto de interfaces libwpe 1.16.3

El inventario se generó con `webkit-kit/tools/audit_wpe_interfaces.py` y su salida reproducible `webkit-kit/wpe-interface-audit.json`. El script sólo analiza texto; no carga bibliotecas, no compila, no ejecuta WebKit y no inventa símbolos.

| Header | Contrato observado | Interfaz pública | Funciones detectadas | Clasificación |
|---|---|---|---:|---|
| `loader.h` | Carga dinámica del backend | `wpe_loader_interface` | 2 | PUBLIC |
| `renderer-host.h` | Host y clientes de IPC | `wpe_renderer_host_interface` | 1 función pública visible | PUBLIC |
| `renderer-backend-egl.h` | Display, EGL, target, offscreen y frame completion | 3 interfaces EGL | 18 | PUBLIC |
| `view-backend.h` | Creación, fd de renderer host, tamaño, actividad, input, fullscreen y pointer lock | `wpe_view_backend_interface` | 31 | PUBLIC |
| `input.h` | Estructuras y enums de teclado, puntero, axis y touch | tipos de datos | 2 nombres funcionales | PUBLIC |

### Loader

`wpe_loader_interface` exige que la biblioteca backend exporte `_wpe_loader_interface` y que su callback `load_object(const char*)` devuelva los objetos de interfaz solicitados. El integrador debe controlar la selección de la biblioteca backend y comprobar el nombre cargado mediante `wpe_loader_init()` y `wpe_loader_get_loaded_implementation_library_name()`.

### Renderer host

El renderer host gestiona los clientes asociados a los procesos WebProcess y sus endpoints. No es el renderer físico. La existencia de este contrato implica que una plataforma alternativa debe garantizar descriptores o un transporte equivalente para que el proceso de renderizado y la aplicación compartan los eventos de frame y los recursos gráficos.

### Renderer EGL y targets

`wpe_renderer_backend_egl_interface` proporciona `create`, `destroy`, `get_native_display` y `get_platform`. El target EGL proporciona `create`, `destroy`, `initialize`, `get_native_window`, `resize`, `frame_will_render`, `frame_rendered` y `deinitialize`. Existe además un target offscreen con `create`, `destroy`, `initialize` y `get_native_window`. El cliente del target recibe `frame_complete`, y el backend debe llamar a `wpe_renderer_backend_egl_target_dispatch_frame_complete()` cuando el consumidor haya terminado con el frame.

Esto no significa que un backend pueda devolver una ventana ficticia. WebCore crea el contexto EGL, obtiene el display nativo y crea una superficie; en el camino offscreen de 2.52.6 `GLContext::createWPEContext()` crea un target offscreen, obtiene su native window, crea un `EGLContext` y crea la superficie con `eglCreateWindowSurface`. Un backend no-EGL necesitaría una ruta de plataforma distinta en WebCore; no bastaría con cambiar un puntero en libwpe.

### View backend e input

`wpe_view_backend_interface` exige `create`, `destroy`, `initialize` y `get_renderer_host_fd`. El objeto view registra clientes de backend, input y fullscreen. El backend/application debe producir callbacks para `set_size`, `frame_displayed`, `activity_state_changed`, `set_device_scale_factor` y `target_refresh_rate_changed`. También debe convertir sus eventos a `wpe_input_keyboard_event`, `wpe_input_pointer_event`, `wpe_input_axis_event` y `wpe_input_touch_event`.

El contrato incluye fullscreen DOM y pointer lock. La API limita el factor de escala a 0.05–5.0 y modela visibilidad, foco y pertenencia a ventana como bits de estado. Estas reglas son públicas y comprobables en host; la política física de fullscreen o pointer lock depende de la plataforma y queda fuera del engine.

## 4. Interfaces no gráficas: WebCore, red, almacenamiento y sistema

El CMake WPE no enlaza sólo libwpe. `Source/WebCore/PlatformWPE.cmake` incluye Cairo o Skia, Gcrypt, GStreamer, decodificadores de imágenes, Soup, TextureMapper y fuentes WPE/GLib. El mismo archivo añade `GLib::Module`, ICU, FreeType/OpenType, Tasn1 y, según flags, GBM, LibDRM, OpenXR, Hyphen, UPower y GStreamer. Por ello la futura plataforma no-GTK aún necesita un contrato de sistema amplio aunque no necesite GTK.

La red y el almacenamiento de sesión están en las capas WebKit/WebCore y en el NetworkProcess; no son responsabilidades primarias del renderer backend. En la configuración WPE 2.52.6 las rutas Soup/GLib cubren conexiones, TLS, cookies, cachés, proxy, WebSocket y datos de sesión. Un target alternativo puede conservar estas capas si proporciona POSIX, hilos, relojes, sockets, resolución DNS, filesystem y TLS públicos. Si el target no ofrece esos servicios, habría que portar las capas de red y almacenamiento correspondientes, no añadir funciones al backend gráfico.

El event loop tampoco es una función de libwpe. WTF/WebKit usa las implementaciones de plataforma de RunLoop y WorkQueue; en la ruta WPE/GLib se integran con el entorno GLib. Un sistema alternativo debe proporcionar primitivas equivalentes de hilos, mutexes, condición, timers, file descriptors o un adaptador de loop, pero no debe confundirse el loop del embedder con el loop interno de WebProcess y NetworkProcess.

## 5. Clasificación de dependencias

| Componente | Estado | Justificación verificable |
|---|---|---|
| Código WebCore/JSC común | PORTABLE | Está en `Source/WebCore` y `Source/JavaScriptCore`; no depende de GTK por diseño, aunque requiere contratos de plataforma. |
| API pública libwpe 1.16.3 | PUBLIC/AVAILABLE | Headers auditados y biblioteca compilada previamente. |
| WPEBackend-fdo | HOST_ONLY | Implementación pública de referencia para Freedesktop; usa tecnologías Linux host. |
| EGL/GLES nativo | HOST_ONLY en el estado actual | `GLContextLibWPE.cpp` llama a EGL y necesita display/surface/native window. |
| Wayland/GBM/DMABUF/SHM | HOST_ONLY | Aparecen en WPEBackend-fdo y en las rutas gráficas opcionales de WebCore. |
| Renderer alternativo | MISSING | No existe una implementación target en el repositorio y no se deben inventar stubs. |
| Presentación física | MISSING | No hay hardware target ni contrato público target validado. |
| Input target | MISSING | Sólo existe el contrato libwpe; falta el traductor de eventos físicos. |
| IPC/FD transport target | MISSING | El backend fdo lo resuelve en Linux; no existe adaptador alternativo validado. |
| Event loop target | UNKNOWN | La ruta host usa GLib/POSIX; no existe prueba target. |
| POSIX threads/timers/memory | AVAILABLE en Linux | Son parte del entorno host y de las dependencias de build. |
| Soup/GLib networking | HOST_ONLY/PUBLIC | Fuente pública y validable en Linux; no es GTK, pero sí depende del stack GLib/Soup. |
| ICU/HarfBuzz/FreeType | PUBLIC/AVAILABLE en host | Dependencias OSS configuradas históricamente; sus equivalentes target siguen sin validarse. |
| JSC LLInt | PORTABLE | Documentación oficial describe offlineasm y backend C/x86/ARM. |
| JSC Baseline/DFG/FTL | PORTABLE por fuente, PLATFORM_REQUIRED para ejecución | Requieren arquitectura, allocator, memoria ejecutable y ABI de llamadas coherentes. |
| JIT target | MISSING para plataforma alternativa | No hay compilador/sysroot/ABI target legal incorporado. |
| GTK | NOT_REQUIRED por diseño WPE | WPE se configura con `WTF_PLATFORM_GTK=0`; el smoke GTK es sólo comparación. |
| Sony SDK/SPRX/ABI retail | EXCLUDED | Prohibido por alcance y no necesario para la demostración OSS host. |

## 6. JavaScriptCore, WebCore y el JIT

La documentación oficial de WebKit identifica JavaScriptCore como una máquina virtual optimizante con lexer, parser, LLInt, Baseline JIT, DFG y FTL [4]. El CMake de JavaScriptCore 2.52.6 incluye los directorios de parser, runtime, interpreter, JIT, LLInt, DFG, FTL, WebAssembly, bmalloc y offlineasm. La configuración muestra que, cuando `ENABLE_JIT` está desactivado y `ENABLE_C_LOOP` está activado, se selecciona un backend C para offlineasm; esto permite una ruta de validación que reduce la dependencia de código máquina generado, aunque no elimina todas las dependencias de JSC.

La parte portable es el parser, bytecode, GC, runtime, builtins, inspector y la semántica del lenguaje. La parte dependiente de plataforma comprende atomics, reserva y protección de memoria, señales/excepciones, threads, ABI de llamadas, código ejecutable y coherencia de caches de instrucciones. Con JIT activado, además, el target necesita una arquitectura soportada por MacroAssembler/offlineasm y permisos de memoria ejecutable. La existencia de `ENABLE_JIT` no demuestra que un target nuevo pueda ejecutar JIT: sólo el build y una prueba real de generación/ejecución lo demostrarían.

La ruta JSCOnly está documentada en la documentación histórica pública de WebKit mediante `Tools/Scripts/build-jsc --jsc-only` y `run-javascriptcore-tests --jsc-only --release --no-build --no-fail-fast` [5]. Es la mejor prueba de bajo coste para la siguiente fase, porque separa JSC de WebCore, WebKit2, rendering, EGL, input y procesos de red. Su resultado esperado sería `jsc` host y tests ECMAScript; no sería evidencia de DOM, CSS, layout o presentación.

## 7. Comparación con WebKit-601-1300/Manx

El inventario histórico ya presente en `webkit-kit/homebrew/jscbridge-contract-inventory.txt` muestra que el port Manx/Orbis de WebKit-601-1300 enlazaba `PlatformManx.cmake`, definía `ORBIS` y requería `LIBJSCBRIDGE_INCLUDE_DIRS`. El mismo inventario identifica referencias a `JSCBRIDGE_MAKE_SHARED_DATA_ALLOCATED`, `JSCBRIDGE_INSTANCE()` y headers externos como `Memory.h`, `VTableMap.h` y `VirtualMethodCall.h`.

La diferencia arquitectónica principal es que el modelo Manx dependía de un puente externo específico del port para allocator, memoria compartida y llamadas internas, mientras que WPE 2.52.6 usa la separación pública WebKit/libwpe/backend y las APIs GLib/WPE generadas por CMake. Abandonar JSCBRIDGE elimina el bloqueo histórico de procedencia de headers y ABI privados del bridge. No elimina la necesidad de portar el sistema: WPE todavía requiere red, threads, memoria, filesystem, fuentes, EGL o una ruta gráfica equivalente, procesos e IPC.

| Área | WebKit-601-1300/Manx | WPE 2.52.6 |
|---|---|---|
| Puente JSC externo | Requerido por `PlatformManx.cmake` y macros JSCBRIDGE | No aparece en el contrato WPE auditado |
| API de embedding | Manx/Orbis y GLib parcial del árbol histórico | API WPE/libwpe pública y API GLib WPE |
| Renderizado | Acoplado a las interfaces del port Manx/Orbis | Delegado a libwpe + backend |
| Dependencias gráficas | ABI/port histórico no recuperado | EGL/renderer host/target u offscreen |
| Multiproceso | Presente pero dependiente del port histórico | WPEWebProcess, NetworkProcess y GPUProcess configurados públicamente |
| Reproducibilidad host | Bloqueada por JSCBRIDGE faltante | CMake/libwpe/backend host demostrados; enlace completo pendiente |
| Compatibilidad PS4 retail | No demostrada | No demostrada |

## 8. Alternativas evaluadas

### WPE 2.52.6 completo

Es la ruta recomendada para el navegador moderno porque mantiene WebCore, JSC, procesos y una arquitectura de backend pública. El coste es alto: el árbol y las unidades unificadas son grandes, y el enlace completo requiere más recursos que los disponibles actualmente. La configuración ya demostró que GTK no es necesario para configurar el port.

### WPE 2.48 o una serie anterior

La serie 2.48 es pública y anterior. Sus notas describen una API WPE Platform en preview, GPU process experimental, cambios de renderizado y un requisito mínimo de ICU 70.1 [6]. No hay evidencia de que sea una solución ligera: sigue siendo un WebKit completo, conserva WebCore y las dependencias de plataforma, y puede introducir una API WPE Platform distinta. Bajar de versión sólo por memoria sacrificaría correcciones y no resuelve el contrato de presentación.

### WPE Platform API

La API WPE Platform es la dirección moderna posterior al modelo legacy y aparece como preview en 2.48 [6]. Para la build fijada 2.52.6 debe tratarse como una ruta alternativa que requiere seleccionar explícitamente sus flags y estudiar su contrato de versión. No conviene mezclar interfaces WPE Platform de otra serie con libwpe 1.16.3 sin una prueba de compilación y runtime.

### JSCOnly

Es la mejor ruta auxiliar. Reduce el objetivo a JavaScriptCore y sus tests, y permite evaluar JIT, LLInt, allocator y memoria sin compilar WebCore, WebKit, Soup o EGL. Es útil para construir evidencia de host y diseñar un eventual port de runtime, pero no valida HTML/CSS, DOM, navegación ni composición.

### WebKitGTK

No es una alternativa arquitectónica al objetivo. GTK sirve como baseline funcional porque el engine comparte WebCore/JSC, pero añade un frontend distinto y no demuestra que el contrato WPE ni un backend no-GTK funcionen. Los resultados GTK quedan separados y no deben reutilizarse como WPE.

## 9. Qué puede probarse completamente en Linux

| Capacidad | Host WPE estático/configuración | Runtime WPE actual | Próxima prueba host |
|---|---:|---:|---|
| Selección `PORT=WPE` | PASS | — | Mantener configuración |
| Compilación libwpe | PASS | — | Repetir sólo si se pierde el prefijo |
| Compilación WPEBackend-fdo | PASS | — | Reusar 53/53 resultado |
| Contrato loader/renderer/view/input | PASS | — | Auditor JSON |
| DOM/CSS/JS en WPE MiniBrowser | CONFIGURED | NOT_TESTED | Completar enlace |
| Frame lifecycle y presentación WPE | STATIC_ONLY | NOT_TESTED | Ejecutar MiniBrowser con backend fdo |
| Input WPE | STATIC_ONLY | NOT_TESTED | Harness de eventos después del enlace |
| Soup/TLS/storage | SOURCE_AVAILABLE | NOT_TESTED en WPE | Fixture con filesystem/cookies |
| JSC LLInt/JIT | SOURCE_AVAILABLE | NOT_TESTED en esta sesión | `build-jsc --jsc-only` |
| Backend no-GTK | CONTRATO DOCUMENTADO | MISSING | Sólo después de runtime fdo |
| Target PS4/OpenOrbis | MISSING | NOT_TESTED | Requiere toolchain/sysroot públicos y contrato gráfico |

El porcentaje debe definirse por cadena, no como una cifra única engañosa. Para los ocho bloques principales —fuente/configuración, libwpe, backend host, engine enlazado, MiniBrowser, smoke HTML, input/presentación y target alternativo— hay tres bloques demostrados o parcialmente demostrados y cinco no demostrados. Esto da aproximadamente **38 % de infraestructura host preparada**, pero **0 % de runtime WPE end-to-end validado en esta sesión** y **0 % de compatibilidad PS4 demostrada**.

## 10. Diagnóstico creado

Se añadieron:

| Archivo | Propósito |
|---|---|
| `webkit-kit/tools/audit_wpe_interfaces.py` | Analiza headers libwpe y fuentes WebKit WPE sin ejecutar código. |
| `webkit-kit/wpe-interface-audit.json` | Resultado JSON de la auditoría con 5 headers públicos, 7 archivos fuente WPE detectados y 8 clasificaciones. |
| `webkit-kit/WPE_PORTABILITY_RESEARCH.md` | Este informe de arquitectura y recomendaciones. |

Uso reproducible:

```bash
cd /home/ubuntu/firmware-lab
python3 -m py_compile webkit-kit/tools/audit_wpe_interfaces.py
python3 webkit-kit/tools/audit_wpe_interfaces.py \
  --libwpe-include /tmp/wpe-header-audit \
  --webkit-source /tmp/wpe-source-audit \
  --output webkit-kit/wpe-interface-audit.json
```

El auditor sólo clasifica lo que encuentra. Si se le entrega un árbol WebKit completo, amplía el inventario; si se le entrega un include inexistente, marca libwpe como `MISSING`. No genera headers ni stubs.

## 11. Recomendación concreta

El siguiente paso debe ser **conseguir un workspace de build con al menos 10–15 GiB libres y más memoria efectiva, recuperar el tarball oficial fijado, configurar un segundo build WPE 2.52.6 `MinSizeRel` con `USE_GSTREAMER=OFF`, `ENABLE_INTROSPECTION=OFF`, `ENABLE_WEBDRIVER=OFF`, `ENABLE_GAMEPAD=OFF`, `ENABLE_SPEECH_SYNTHESIS=OFF`, `CMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF` y Ninja `-j1`**. El build anterior no mostró un error de código: terminó por presión de recursos durante unidades C++ pesadas.

En paralelo, ejecutar `Tools/Scripts/build-jsc --jsc-only` y los tests JSCOnly de la revisión correspondiente. Este experimento tiene alto valor porque puede completarse antes que MiniBrowser y separa el riesgo JIT/runtime del riesgo WebCore/backend. No debe presentarse como navegador funcional.

Una vez enlazado MiniBrowser con WPEBackend-fdo, hay que ejecutar el conjunto existente de tres fixtures y generar una matriz WPE independiente con `PASS`, `FAIL` y `NOT_TESTED`. Sólo después de esa prueba tiene sentido diseñar un backend alternativo. El backend futuro debe comenzar con un target offscreen o SHM verificable en host, no con una implementación gráfica target hipotética.

## Conclusión

WPE 2.52.6 es actualmente la ruta OSS más coherente para demostrar un WebKit moderno sin GTK. La investigación confirma una separación real entre engine y backend, y elimina el bloqueo de procedencia de JSCBRIDGE que afectaba a WebKit-601-1300/Manx. Sin embargo, WPE no elimina los requisitos de sistema: sigue necesitando procesos, IPC, GLib/Soup, ICU, fuentes, memoria, red, y una ruta de presentación EGL/offscreen.

El proyecto está en un estado **STATICALLY_VALIDATED / RUNTIME_WPE_PENDING**. La infraestructura y los contratos públicos están demostrados; el enlace MiniBrowser y el smoke WPE todavía no. No existe base técnica para afirmar compatibilidad con PS4 13.52 ni para introducir SDK, módulos, ABI u offsets propietarios.

## Referencias

[1]: https://wpewebkit.org/about/architecture.html "WPE Architecture — WPE WebKit"

[2]: https://wpewebkit.org/about/get-wpe.html "Get WPE — releases and components"

[3]: https://blogs.igalia.com/llepage/the-process-of-creating-a-new-wpe-backend/ "The process of creating a new WPE backend — Igalia"

[4]: https://docs.webkit.org/Deep%20Dive/JSC/JavaScriptCore.html "JavaScriptCore — WebKit Documentation"

[5]: https://trac.webkit.org/wiki/JSCOnly "JSCOnly — archived WebKit documentation"

[6]: https://wpewebkit.org/blog/2025-04-11-wpewebkit-2.48.html "WPE WebKit 2.48 highlights"

[7]: https://github.com/WebKit/WebKit/tree/webkitgtk-2.52.6 "WebKit source tag webkitgtk-2.52.6"

[8]: https://github.com/WebPlatformForEmbedded/libwpe/tree/1.16.3 "libwpe source tag 1.16.3"

[9]: https://github.com/Igalia/WPEBackend-fdo/tree/1.16.1 "WPEBackend-fdo source tag 1.16.1"


## Registro de validación final de esta investigación

La auditoría nueva pasó `py_compile`, produjo `libwpe=PUBLIC` y `webkit=AVAILABLE`, y `tools/run_host_regression.py` pasó con `HOST_ECMASCRIPT_SMOKE`. `tools/kit_health.py` pasó sin hallazgos y `git diff --check` pasó. La suite `make -C webkit-kit/homebrew all` llegó al smoke seguro, pero terminó con código 127 al ejecutar `minimal-browser` porque el loader no encontró `libjavascriptcoregtk-4.1.so.0` en el entorno de ejecución actual. Esto es un bloqueo del runtime del host, no un resultado WPE; no se atribuye a WebKit ni se presenta como PASS. El smoke WebKitGTK moderno tampoco se ejecutó en esta sesión porque `webkit2gtk-4.1.pc` no está disponible. El archivo generado `homebrew/build/host/minimal-browser-output.txt` se restauró para no incluir cambios de ejecución en el commit.
