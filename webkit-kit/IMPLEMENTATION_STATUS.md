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
