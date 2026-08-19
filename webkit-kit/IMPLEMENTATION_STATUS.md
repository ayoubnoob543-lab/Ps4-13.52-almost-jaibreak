# Estado de implementación del kit WebKit/JSC

## Componentes añadidos

`tools/run_host_regression.py` ejecuta el harness ECMAScript seguro con Node. Su resultado es exclusivamente `HOST_ECMASCRIPT_SMOKE`; no demuestra que el motor sea WebKit de PS4 ni carga módulos retail.

`tools/structural_signatures.py` genera hashes del archivo, metadata ELF básica, hashes de cadenas imprimibles y ventanas de bytes. Es una firma estructural de baja dependencia. No desensambla, no resuelve offsets, no genera gadgets y deja `semantic_identity=UNVERIFIED`.

`tools/compare_signatures.py` compara dos salidas mediante similitud Jaccard de tokens/ventanas. Un resultado sólo puede clasificarse como `CANDIDATE_STRUCTURAL_ONLY`.

`tools/make_triple_manifest.py` crea un manifest de `libSceNKWebKit.sprx`, `libkernel_web.sprx` y `libSceLibcInternal.sprx`. Los archivos ausentes quedan `MISSING`; `common_build_id` permanece `MISSING` hasta que exista evidencia coherente.

`tools/kit_health.py` busca marcadores de secretos y políticas inseguras. No ejecuta JavaScript PS4, payloads ni binarios.

## Uso

```bash
python3 webkit-kit/tools/run_host_regression.py
python3 webkit-kit/tools/structural_signatures.py archivo-a -o a.signatures.json
python3 webkit-kit/tools/structural_signatures.py archivo-b -o b.signatures.json
python3 webkit-kit/tools/compare_signatures.py a.signatures.json b.signatures.json
python3 webkit-kit/tools/make_triple_manifest.py /ruta/al/conjunto -o triple-manifest.json
python3 webkit-kit/tools/kit_health.py
```

## Estado actual

El host dispone de Node, por lo que el smoke test ECMAScript puede ejecutarse. No hay Clang/LLD, CMake, Ninja, Docker ni SDK/ABI retail detectados en el entorno auditado. El repositorio no contiene los tres módulos WebKit 13.52; por ello no puede generar firmas target, Build ID común, GOT/imports reales, vtables retail ni offsets confirmados.

OpenOrbis permanece como una ruta separada para una aplicación homebrew legítima cuando el usuario aporte el toolchain. Este kit no incluye loader de jailbreak, exploit, payload, escape de sandbox ni redistribución de módulos propietarios.

## Criterios de promoción

Una coincidencia estructural no se promueve a `CONFIRMED` sin bytes target, SHA-256, formato/segmentos, Build ID o metadata equivalente y procedencia coherente. Los offsets absolutos permanecen deshabilitados por diseño.

## Prototipo `homebrew/`

El prototipo seguro de `homebrew/` está implementado como una frontera C portable con adaptación host. No incorpora WebKit retail, módulos `.sprx`, SDK Sony, offsets, gadgets, ROP/JOP, exploits ni payloads.

| Componente | Estado | Evidencia |
|---|---|---|
| Contrato C portable del runtime | AVAILABLE | `homebrew/include/orbis_webkit_stub.h` |
| Adaptador host seguro | AVAILABLE | `homebrew/src/orbis_webkit_stub.c` |
| Smoke executable host | AVAILABLE | `homebrew/src/homebrew_smoke.c` y build local |
| Makefile reproducible host | AVAILABLE | `homebrew/Makefile` |
| Fuente OSS WebKit/JSC de referencia | AVAILABLE | Corpus fijado en `PS4OSSCode.HEAD` |
| OpenOrbis toolchain instalado en sandbox | MISSING | No se detectaron `clang`, `ld.lld`, CMake ni Ninja |
| OpenOrbis sysroot/headers target | MISSING | No presentes en el entorno |
| ABI y runtime Orbis autorizados | UNKNOWN | No demostrables desde OSS |
| Backend gráfico/compositor PS4 | MISSING | No se implementa ni se inventa |
| Event loop, sandbox, filesystem y allocator target | MISSING | Requieren contrato target legítimo |
| `libSceNKWebKit.sprx` 13.52 | MISSING | Bytes verificables no disponibles |
| `libkernel_web.sprx` 13.52 | MISSING | Bytes verificables no disponibles |
| `libSceLibcInternal.sprx` 13.52 | MISSING | Bytes verificables no disponibles |
| Compatibilidad real con firmware 13.52 | UNKNOWN | No hay build ni prueba en hardware |

El smoke host sólo demuestra la coherencia del adaptador. No se promueve a `PS4_HOMEbrew_BUILD_PASS` ni a `WEBKIT_RETAIL_1352_CONFIRMED`.

## Navegador mínimo portable

Se añadió una aplicación mínima en `homebrew/` con entry point, arena de memoria, comprobación de filesystem sobre el directorio configurado, event loop host, hilo de timer y salida de capacidades. Esta aplicación no incorpora todavía JSC/WebCore/WebKit ejecutable: el puente `oss_webkit_bridge` sólo expone si existe una ruta `WEBKIT_SOURCE_DIR` y mantiene el estado `oss-source-not-configured` o `oss-source-configured-port-adapter-required`.

| Área | Estado actual | Motivo |
|---|---|---|
| Entry point portable | AVAILABLE | `src/minimal_browser_main.c` compila y ejecuta en host. |
| Memoria | AVAILABLE | Arena host controlada, sin memoria ejecutable ni APIs privilegiadas. |
| Filesystem básico | AVAILABLE | `stat()` sobre el root configurado; no hay acceso fuera del proceso. |
| Event loop | AVAILABLE | Bucle mínimo determinista. |
| Threads/timers | AVAILABLE | Hilo POSIX de timer con `pthread`, unido antes de salir. |
| Salida básica | AVAILABLE | Salida textual determinista del estado. |
| JSC OSS integrado | MISSING | No existe build system/sysroot/dependencias configuradas para compilarlo aquí. |
| WebCore OSS integrado | MISSING | Requiere generar headers, port layer y dependencias de WebKit. |
| WebKit UI/platform layer | MISSING | Requiere backend de plataforma y contrato target. |
| Backend gráfico host | UNKNOWN | No añadido; el prototipo declara `graphics=stub`. |
| Backend gráfico PS4 público suficiente | UNKNOWN | No demostrable con las APIs presentes. |
| Toolchain OpenOrbis | MISSING | No se detectan `clang`, `ld.lld`, CMake, Ninja ni instalación OpenOrbis. |
| Sysroot/headers OpenOrbis | MISSING | No presentes en el entorno. |
| Ejecución PS4 real | UNKNOWN | No hay dispositivo ni método de desarrollo conectado. |

El resultado de esta fase es `MINIMAL_HOST_BROWSER_AVAILABLE`; la transición a `PS4_HOMEBREW_BROWSER` permanece bloqueada por toolchain/sysroot/ABI y backend de plataforma.

## JavaScriptCore host real

Se instaló legalmente desde los repositorios Ubuntu la dependencia pública `libjavascriptcoregtk-4.1-dev` versión `2.52.3-0ubuntu0.24.04.1`, junto con su runtime y herramienta host. El `minimal-browser` ahora enlaza mediante `pkg-config javascriptcoregtk-4.1` y ejecuta una expresión JavaScript real con la API C pública de JavaScriptCore.

| Componente | Estado | Evidencia |
|---|---|---|
| JavaScriptCore host API pública | AVAILABLE | `jsc_context_new/evaluate`, `jsc_value_to_boolean/string`; smoke devuelve `passed=true`. |
| Smoke JavaScript dentro de minimal-browser | AVAILABLE | `homebrew/build/host/minimal-browser-output.txt` y `tests/test_homebrew_jsc.py`. |
| Corpus OSS PS4 WebKit/JSC | AVAILABLE | `/home/ubuntu/ps4-lab-1352/analysis/webkit_oss_sources_2026-08-19/PS4OSSCode`, commit `d636699770323d7968a2c37955aa513bda5f8a37`. |
| Build directo del árbol PS4OSSCode | UNKNOWN/MISSING | El corpus localizado no expone un build host listo para este prototipo; requiere adaptación y dependencias adicionales. |
| WebCore/WebKit OSS ejecutable integrado | MISSING | No se ha compilado ni conectado el port layer completo. |
| JSC de la misma revisión histórica PS4 | UNKNOWN | JavaScriptCore GTK host no demuestra equivalencia con WebKit 601/616 PS4. |
| OpenOrbis target build | MISSING | Siguen ausentes toolchain, sysroot, headers y ABI target. |
| PS4/retail 13.52 | MISSING/UNKNOWN | No se añadieron módulos Sony, SDK retail ni afirmaciones de compatibilidad. |

El estado de esta fase es `HOST_JSC_SMOKE_AVAILABLE`; no es `WEBKIT_OSS_PS4_BUILD_AVAILABLE` ni `WEBKIT_RETAIL_1352_CONFIRMED`.

## Build OSS histórico PS4OSSCode

La familia más adecuada quedó identificada como `WebKit-601-1300/WebKit-601-1300`, commit `d636699770323d7968a2c37955aa513bda5f8a37`. Sus archivos de CMake/JSC/WTF/WebCore/WebKit están confirmados en los objetos Git, pero no están checkoutados físicamente en el corpus agregado.

| Elemento | Estado | Resultado |
|---|---|---|
| Fuente histórica JSC/WTF/WebCore/WebKit | AVAILABLE | Confirmada en objetos Git del corpus. |
| CMake y port GTK históricos | AVAILABLE | Confirmados en Git; requieren archive de trabajo. |
| Port Manx/Orbis | AVAILABLE como fuente | Requiere `ORBIS`, headers/libs públicos y plataforma gráfica. |
| CMake/Ninja/Gperf/Bison/Flex/Perl/Python/Ruby | AVAILABLE | Herramientas presentes tras instalación/reparación pública. |
| Configuración GTK host | BLOCKED | Falta metadata/development set, comenzando por Cairo; también faltan varios paquetes GTK/GLib. |
| Compilación JSC histórica real | BLOCKED | La configuración no alcanzó generación de build por dependencias. |
| Integración WebCore/WebKit histórica en minimal-browser | MISSING | No existe biblioteca histórica compilada. |
| Build Manx/Orbis | BLOCKED | No hay sysroot/headers/libs target públicos configurados. |
| SDK retail, módulos Sony y ABI 13.52 | MISSING | Deliberadamente no usados ni inventados. |

El nuevo `tools/probe_historical_oss_build.py` y `homebrew/historical-oss-build-probe.json` dejan reproducible la diferencia entre contenido Git disponible y checkout/build disponible. El resultado de esta fase es `HISTORICAL_OSS_SOURCE_CONFIRMED` y `HOST_BUILD_BLOCKED_BY_DEPENDENCIES`; no se promociona a build WebKit compilada.

## Build operativo WebKit-601-1300

| Componente | Estado | Evidencia actualizada |
|---|---|---|
| Árbol build-relevante 601-1300 materializado | AVAILABLE | `Source/`, CMake, `Tools/Scripts` y `WebKitLibraries`; 18.231 archivos, ~314 MB. |
| Configuración CMake GTK | AVAILABLE/PASS | Configuración completa con dependencias públicas; `cmake_rc=0`. |
| JavaScriptCore histórico | BLOCKED | Ninja falla por `bridge/Memory.h`, ausente en Git y checkout. |
| WTF histórico | BLOCKED | Comparte la dependencia de cabecera ausente durante compilación. |
| WebCore histórico | BLOCKED | Depende de JSC/WTF no compilados. |
| WebKit/WebKit2 histórico | BLOCKED | No se llegó a enlazado por bloqueo de JSC. |
| Port Manx/Orbis | BLOCKED | CMake en Linux termina con `Unknown OS 'Linux'`; no se fuerza `ORBIS`. |
| `orbis-clang`/`orbis-clang++` | MISSING | Requeridos por `Source/cmake/ORBIS.cmake`. |
| `SCE_ORBIS_SDK_DIR`/sysroot | MISSING | No está presente en el entorno. |
| `manx/System.h`, `SceOrbisCompat_stub_weak` | MISSING | Requeridos por `FindLibmanx.cmake`. |
| `precompiled_shaders.h`, `ScePrecompiledShaders_stub_weak` | MISSING | Requeridos por `FindPrecompiledShaders.cmake`. |
| `ScePigletv2VSH_stub_weak`, `ScePosix_stub_weak` | MISSING | Referenciados por `OptionsManx.cmake`. |
| `LIBJSCBRIDGE_INCLUDE_DIRS` | UNKNOWN/MISSING | Referenciado por `PlatformManx.cmake`; proveedor no localizado. |
| SDK retail, `.sprx`, ABI 13.52 | MISSING | Deliberadamente no utilizados ni inventados. |

El informe operativo está en `homebrew/OSS_601_BUILD_RESULTS.md`.

## Investigación `bridge/Memory.h`

| Elemento | Estado | Resultado |
|---|---|---|
| `bridge/Memory.h` en PS4OSS 601-1300 | MISSING | Referenciado por 9 archivos, pero no existe en checkout ni objetos Git. |
| `JSCBRIDGE_MAKE_SHARED_DATA_ALLOCATED` | MISSING | Usado por 25 archivos; no hay definición pública en el corpus. |
| `JSCBRIDGE_INSTANCE` / `PoolAllocator16K` | MISSING | Contrato de memoria/JIT externo no recuperado. |
| Dependencia estándar WebKit upstream | NOT_FOUND | Tags Safari-601 y árbol Chromium WebKit no contienen `Memory.h`. |
| Fuente compatible recuperada | NOT_FOUND | No se integró código inventado ni una fuente incompatible. |
| Build JSC histórico | BLOCKED | Falla exactamente en `bridge/Memory.h`. |

Informe: `homebrew/BRIDGE_MEMORY_FORENSICS.md`.

## Contrato JSCBRIDGE

| Área | Estado | Evidencia |
|---|---|---|
| Call sites JSCBRIDGE en 601-1300 | `CONFIRMED` | Macros, allocators, ClassInfo y split-process JIT referenciados por el código. |
| Headers `bridge/*` | `MISSING` | `JSCBridge*.h`, `Memory.h`, `VTableMap.h`, `VirtualMethodCall.h` y `unique_ptr_*` ausentes. |
| `LIBJSCBRIDGE_INCLUDE_DIRS` | `MISSING` | Requerido por PlatformManx de JSC, WebCore y WebKit2; proveedor no presente. |
| `JscBridge_vm` / `SceJitBridge` | `MISSING` | Sólo nombres de link en CMake; no hay bibliotecas OSS recuperadas. |
| PoolAllocator16K/32K | `MISSING` | Call sites visibles; implementación y contrato de ownership ausentes. |
| vtable/class-info bridge | `MISSING` | `classInfoRegisterInstance`, `VTableMap` y virtual-call fixup sin provider. |
| Fuente alternativa legítima compatible | `NOT_FOUND` | No apareció en variantes PS4OSS, upstream WebKit ni búsquedas públicas. |

Informe: `homebrew/JSCBRIDGE_CONTRACT.md`.

## Investigación pública del origen JSCBRIDGE

| Candidato | Estado | Motivo |
|---|---|---|
| JSON `libSceJitBridge.sprx` de pset4/orbisLibGen | `FOUND_METADATA_ONLY` | Inventario de módulos; no contiene implementación, headers ni biblioteca enlazable. |
| CTurt `allocateJIT` | `FOUND_WRAPPER_ONLY` | Wrapper de exports JIT propietarios; no implementa JSCBridgeVM/Comp ni allocators WebKit. |
| PS4OSSCode forks/commits | `NOT_FOUND` | Sin provider JSCBRIDGE adicional. |
| GitHub code/commit/repository searches | `NOT_FOUND` | Sin fuente OSS coincidente para macros, headers o PoolAllocator16K. |
| Upstream WebKit/Safari-601 | `UNRELATED` | Bridge estándar de WebCore; no JSCBRIDGE. |
| Fuente compatible integrable | `NOT_FOUND` | No se incorporó código ni stub. |

Informe: `homebrew/JSCBRIDGE_PUBLIC_ORIGIN_RESEARCH.md`.

## Comparación de rutas OSS sin JSCBRIDGE

| Ruta | Estado real |
|---|---|
| JSC host mediante JavaScriptCoreGTK 4.1 | `AVAILABLE/VALIDATED` |
| WebKit-601-1300 GTK | `CONFIGURED/BLOCKED` por `bridge/Memory.h` y proveedor JSCBRIDGE ausente |
| WebKit-616 PS4OSS | `AVAILABLE_AS_SOURCE/UNVALIDATED_BUILD` |
| WebKitGTK moderno | `PUBLIC_ROUTE/NOT_BUILT_IN_THIS_PHASE` |
| WPE WebKit | `PUBLIC_ROUTE/NOT_BUILT_IN_THIS_PHASE`; backend target pendiente |
| QuickJS | `PUBLIC_ALTERNATIVE/NOT_INTEGRATED`; no WebCore |
| Duktape | `PUBLIC_ALTERNATIVE/NOT_INTEGRATED`; compatibilidad web limitada |
| OpenOrbis | `PUBLIC_TOOLCHAIN/NOT_PRESENT_LOCALLY`; no WebKit port disponible |
| Navegador WebKit PS4 real | `UNKNOWN/MISSING` |

Recomendación única: usar WebKitGTK/WPE moderno como ruta OSS funcional y modular de host, y reservar QuickJS para una aplicación JS reducida. No tratar 601-1300 como compilable hasta recuperar legítimamente el proveedor JSCBRIDGE.

Informe: `WEBKIT_ROUTE_COMPARISON.md`.

## Prototipo WebKitGTK moderno

| Componente | Estado |
|---|---|
| WebKitGTK 4.1 runtime/development 2.52.3 | `AVAILABLE/INSTALLED` |
| Navegador mínimo compilado localmente | `AVAILABLE/VALIDATED` |
| DOM real | `VALIDATED` |
| CSS/layout computado | `VALIDATED` |
| JavaScriptCore integrado en WebKitGTK | `VALIDATED` |
| Evento DOM `click` | `VALIDATED` |
| Navegación local `file://` | `VALIDATED` |
| WebKitGTK engine compilado desde fuentes en este entorno | `BLOCKED` por source package/espacio |
| WPE backend | `NOT_INTEGRATED` |
| OpenOrbis backend WebKit | `MISSING/UNKNOWN` |
| PS4/Orbis/13.52 compatibility | `UNKNOWN` |

Detalle: `WEBKITGTK_MODERN_PROTOTYPE.md`.

## Matriz WebKitGTK ampliada y WPE

El smoke moderno valida DOM complejo, flexbox, CSS Grid, animación CSS, JavaScript, eventos, formularios, SVG, imagen data URI, canvas 2D, localStorage y navegación `file://` de tres páginas. Resultado: `VALIDATED` en host con WebKitGTK 2.52.3.

La evaluación WPE usa headers públicos de libwpe commit `445a0b5579aba7eca619973ca476bb5291a85cf5`. Las interfaces públicas de view backend, renderer host/EGL, input, loader, pasteboard y gamepad están documentadas, pero `libwpe-1.0-dev` no está disponible en los repositorios configurados y no se compiló WPE.

El baseline recomendado es WebKitGTK moderno para host y una futura arquitectura inspirada en WPE para separar WebKit/WebCore/JSC de ventana, input y compositor. OpenOrbis/Orbis sigue `MISSING/UNKNOWN` para un backend WebKit; PS4 13.52 no se afirma compatible.

## WPE WebKit moderno — build host

| Componente | Estado | Evidencia |
|---|---|---|
| libwpe 1.16.3 | `AVAILABLE/BUILD_PASS` | Tarball oficial fijado por SHA-256; compilado en prefijo temporal. |
| WPEBackend-fdo 1.16.1 | `AVAILABLE/BUILD_PASS` | Tarball oficial fijado por SHA-256; Meson completó 53/53 tareas. |
| WPE WebKit 2.52.6 | `SOURCE_AVAILABLE/CMAKE_PASS` | Configuración WPE sin GTK completó `Configuring done` y `Generating done`. |
| WPE MiniBrowser target | `GENERATED/BUILD_PENDING` | Target generado con `ENABLE_MINIBROWSER=ON`; el build fue interrumpido por límite operativo durante la generación de headers. |
| WPE HTML smoke | `NOT_RUN` | No se generó todavía el ejecutable WebKit/WPE. |
| OpenOrbis/Orbis WPE backend | `UNKNOWN/MISSING` | Requiere contratos públicos de superficie, presentación, input, timers, memoria, filesystem, red y sincronización. |
| Sony/retail/JSCBRIDGE | `MISSING/NOT_USED` | No utilizados ni incorporados. |

Detalle operativo: `homebrew/WPE_HOST_BUILD_STATUS.md`.


## Reanudación WPE WebKit 2.52.6

Se reanudó el build existente de `/tmp/wpewebkit-2.52.6-build` sin cambiar de arquitectura ni limpiar fuentes u objetos. `libwpe` 1.16.3, `WPEBackend-fdo` 1.16.1 y la configuración CMake del port WPE siguen validados. `MiniBrowser` no llegó a enlazarse: la compilación de JavaScriptCore fue terminada por el límite de recursos/tiempo del workspace durante unidades unificadas C++ pesadas; no se observó un error semántico reproducible del código WPE.

| Área | Estado actualizado | Evidencia |
|---|---|---|
| WPE WebKit CMake | AVAILABLE/PASS | `WPE_HOST_BUILD_STATUS.md`, configuración `PORT=WPE` |
| MiniBrowser WPE enlazado | BLOCKED | No existe ejecutable final en el build directory |
| Smoke HTML WPE | NOT_TESTED | No se ejecutó sin ejecutable WPE |
| DOM/CSS/JS/eventos en WPE | NOT_TESTED | No se atribuyen resultados GTK a WPE |
| Baseline WebKitGTK | PASS independiente | `WEBKITGTK_CAPABILITY_MATRIX.md` |
| Comparación automática WPE vs GTK | NOT_TESTED | Requiere MiniBrowser WPE funcional |
| Compatibilidad PS4 13.52 | UNKNOWN | No se usan SDK, módulos ni ABI propietarios |

El resultado de esta reanudación es `WPE_CMAKE_PASS_MINIBROWSER_BUILD_BLOCKED_BY_WORKSPACE_RESOURCES`, no `WPE_RUNTIME_PASS`.


## Investigación profunda de portabilidad WebKit/WPE

Se añadió `WPE_PORTABILITY_RESEARCH.md`, un informe técnico exclusivamente WebKit/WPE que separa engine, WebCore/JSC, libwpe, backend, renderer, input, event loop, red, almacenamiento y presentación. La evidencia fuente usada incluye el tag público WebKit `webkitgtk-2.52.6` (commit `4fb33923db2f945803df49546f75867980365c08`), los headers públicos libwpe 1.16.3 y el WPEBackend-fdo 1.16.1 versionado.

Se añadió `tools/audit_wpe_interfaces.py` y su salida `wpe-interface-audit.json`. La auditoría estática detecta los cinco headers públicos de libwpe (`loader`, `renderer-host`, `renderer-backend-egl`, `view-backend` e `input`), las interfaces loader/host/EGL/view, 53 funciones o contratos relevantes y siete archivos fuente WPE selectivos. El script no ejecuta código, no compila y no genera stubs.

| Área | Estado actualizado |
|---|---|
| Separación WebKit/libwpe/backend | `CONFIRMED_BY_SOURCE_AND_PUBLIC_DOCS` |
| Contrato loader/renderer/view/input | `PUBLIC/AVAILABLE` |
| WPEBackend-fdo como backend Linux | `HOST_ONLY/BUILD_PASS` |
| WPE WebKit CMake 2.52.6 | `SOURCE_AVAILABLE/CONFIGURED` |
| MiniBrowser WPE enlazado | `BLOCKED_BY_WORKSPACE_RESOURCES` |
| Smoke WPE DOM/CSS/JS/rendering | `NOT_TESTED` |
| WebCore/JSC común | `PORTABLE_WITH_PLATFORM_CONTRACT` |
| JSCOnly host route | `PUBLIC_ROUTE/RECOMMENDED_NEXT_TEST` |
| Backend alternativo no-GTK | `MISSING` |
| OpenOrbis/Orbis backend WebKit | `MISSING/UNKNOWN` |
| PS4/retail 13.52 compatibility | `UNKNOWN/NOT_CLAIMED` |

La cobertura se expresa por cadena: la infraestructura host de fuente/configuración/libwpe/backend alcanza aproximadamente 38% de los ocho bloques de una cadena completa; el runtime WPE end-to-end sigue en 0% validado en esta sesión. WebKitGTK permanece únicamente como baseline independiente.
