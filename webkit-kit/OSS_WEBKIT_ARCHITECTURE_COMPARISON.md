# Comparación OSS WebKit para PS4 y aplicabilidad a 13.52

## Alcance y procedencia

Se analizó el corpus público `FreeBSDKernel9-0/PS4OSSCode` fijado en el commit `d636699770323d7968a2c37955aa513bda5f8a37`. El inventario local y sus métricas están en `/home/ubuntu/ps4-lab-1352/analysis/webkit_oss_sources_2026-08-19/`; el hash del informe de métricas acompaña a ese material.

También se conservaron las URLs y hashes del lockfile del repositorio. La fuente oficial `WebKit-601-1300.zip` está registrada con SHA-256 `dc2a7584695474c9b878dcfdc16b2358bda61041053220b146320d6cfed3f02b`. La descarga completa del ZIP oficial es grande y la copia local temporal quedó incompleta; por eso el análisis reproducible principal usa el corpus Git fijado, no un archivo parcial.

> El corpus OSS aporta código fuente y estructura de WebKit, pero no demuestra la existencia de módulos retail 13.52 ni de las adaptaciones privadas de Sony.

## Arquitectura identificada

Las versiones OSS comparten una separación por capas:

| Capa | Componentes observables | Reutilización probable |
|---|---|---|
| WTF | tipos básicos, concurrencia, strings, allocators y utilidades | Alta como referencia de diseño; depende de compilador y plataforma. |
| JavaScriptCore | parser, bytecode, VM, GC, runtime, API C y JIT | Alta para harness host; el JIT, allocator y políticas de memoria dependen del target. |
| WebCore | DOM, CSS, loaders, fonts, layout, eventos y bindings | Alta como fuente de comportamiento; baja para ABI binario retail. |
| WebKit/WebKit2 | procesos, páginas, UI process, IPC y port/platform | Estructural; la integración PS4 requiere interfaces privadas. |
| Platform | filesystem, networking, graphics, threads, timers y user-agent | Sólo parcialmente reutilizable; aquí se concentran diferencias de Sony/Orbis. |
| Build system | CMake/Makefiles, feature flags, port options y generación de headers | Reutilizable como receta conceptual; no sustituye sysroot ni SDK retail. |

## Comparación pública de versiones

El corpus contiene raíces `WebKit-601-1250`, `WebKit-601-1300`, `WebKit-616-1250`, `WebKit-616-1300`, además de series `webkit-1000` a `webkit-1200-2`. Las métricas se obtuvieron de los paths Git sin ejecutar código:

| Versión | Paths totales | Paths `Source` contabilizados | Observación |
|---|---:|---:|---|
| WebKit-601-1250 | 8.579 | 0 por layout distinto del corpus | Entrada OSS de referencia, árbol empaquetado/organizado de otra forma. |
| WebKit-601-1300 | 183.721 | 11.857 | Árbol fuente más completo; contiene rutas CSSFontFace y FrameLoader. |
| WebKit-616-1250 | 28.860 | 0 por layout distinto | Referencia posterior con organización distinta. |
| WebKit-616-1300 | 30.268 | 0 por layout distinto | Referencia posterior; no equivale a retail 13.52. |
| webkit-1150-2 | 23.614 | 0 por layout distinto | Referencia de generación posterior. |
| webkit-1200-2 | 24.016 | 0 por layout distinto | Referencia de generación posterior. |

El cambio de organización del corpus impide interpretar el número bruto de paths como tamaño de código comparable. Lo que sí es sólido es que existen varias generaciones públicas y que `WebKit-601-1300` contiene las fuentes completas relevantes para estudiar `CSSFontFace`, `FrameLoader`, JSC y WebCore.

Las diferencias que deben medirse con cuidado son: cambios de API entre WebKit 601/616, incorporación o retirada de features, reorganización del build system, cambios de JIT/GC y cambios en `platform`. LTO, compilador, flags, backports y parches privados pueden cambiar el binario aunque el código fuente parezca equivalente.

## Cruce con PSFree y CSSFontFace

El repositorio ya conserva inventarios de 31 archivos PSFree y 67 archivos de `CSSFontFace-Exploit`, junto con manifiestos SHA-256. Su utilidad es comparativa:

| Material | Se puede reutilizar | No se puede afirmar |
|---|---|---|
| PSFree histórico | nombres de funciones, conceptos de leak/RW, organización de análisis y relación WebKit/libkernel | offsets 9.60/anteriores, gadgets, ROP/JOP o compatibilidad 13.52 |
| CSSFontFace histórico | nombres de clases, flujo de `setStatus`/`pump`, fixtures y evolución de una clase WebCore | que el bug exista sin cambios en 13.52, ni offsets/GOT/vtables retail |
| WebKit OSS 601/616 | implementaciones fuente, headers públicos, layout tests y puntos de integración | `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx` retail |
| `libkernel_sys_13.52.bin` | análisis de sus propios bytes y metadata | sustituir el runtime WebKit, el SDK o la ABI retail |

El cruce correcto es por nombres y estructura: localizar clases/métodos en OSS, registrar firmas no operativas y marcar cualquier correspondencia con PS4 como `STRUCTURAL`. No se promueve un valor a `CONFIRMED` sin bytes target y procedencia de build.

## Partes genéricas frente a Orbis/Sony

Son genéricas o casi genéricas el parsing HTML/CSS, DOM, gran parte de JSC, algoritmos de layout, APIs C públicas de JSC, tests de regresión y muchas utilidades WTF. Son específicas o altamente dependientes de plataforma la creación de procesos, IPC, sandbox, filesystem, red, gráficos, event loop, allocator, JIT policy, formato SELF/SPRX, imports SCE, `libkernel_web`, `libSceLibcInternal`, user-agent retail, flags de build y empaquetado.

La existencia de una ruta `platform/playstation` o un user-agent de PlayStation en una fuente pública sólo prueba una integración de referencia. No prueba que el ABI, las bibliotecas internas o la configuración de 13.52 sean iguales.

## Interfaces que necesita la base homebrew

La base homebrew necesita, como mínimo, un toolchain OpenOrbis fijado, headers y stubs, sysroot autorizado, entry point de aplicación, allocator y runtime C compatibles, acceso a filesystem y logging, y un método legítimo de empaquetado/ejecución. Para un harness host se pueden sustituir esas interfaces por POSIX/Linux y usar Node o un JSC/WebKit host; eso no prueba Orbis.

El repositorio mantiene estas dos metas separadas:

| Perfil | Requisitos | Estado |
|---|---|---|
| `host-smoke` | Node y harness ECMAScript | Disponible y validado. |
| `ps4-homebrew` | OpenOrbis, sysroot, headers/stubs y método legítimo de ejecución | Documentado, toolchain no instalado en el sandbox. |
| `retail-compatible-13.52` | Fuente/patches 13.52, SDK/ABI retail, módulos internos y empaquetado | Bloqueado; no debe etiquetarse como build existente. |

## Qué puede reutilizarse para 13.52

Puede reutilizarse la organización del árbol, el análisis de WebCore/JSC, la comparación de APIs y clases, los layout tests, la metodología de firmas estructurales, los manifests y el harness host. También puede utilizarse la fuente 601/616 para estudiar qué interfaces necesitaría una futura adaptación, siempre que cada diferencia de plataforma se documente.

No pueden reutilizarse directamente los offsets de PSFree, los gadgets de CSSFontFace, los offsets de WebKit 9.60/11.02, las vtables históricas, los imports asumidos ni las tablas de kernel. Tampoco puede afirmarse que una build OSS para host o homebrew sea `libSceNKWebKit.sprx` retail.

## Desconocido o ausente para 13.52

Siguen ausentes los bytes verificables de `libSceNKWebKit.sprx`, `libkernel_web.sprx` y `libSceLibcInternal.sprx` 13.52; un manifest común o Build ID; imports/GOT reales; vtables y estructuras verificadas; patches privados de Sony; sysroot/ABI retail; flags exactas; toolchain usado por el navegador retail; y una prueba en hardware real.

El resultado de este trabajo es, por tanto, `OSS_STRUCTURAL_BASE_AVAILABLE`, no `WEBKIT_RETAIL_1352_CONFIRMED`.

## Referencias

[1]: https://github.com/FreeBSDKernel9-0/PS4OSSCode "FreeBSDKernel9-0/PS4OSSCode"
[2]: https://www.playstation.com/en-us/oss/ps4/webkit/ "Sony PlayStation 4 Open Source WebKit"
[3]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain "OpenOrbis PS4 Toolchain"
[4]: https://github.com/zacke0815/ps4-9.04_webkitJB "PSFree/WebKit reference repository"
[5]: https://github.com/ntfargo/CSSFontFace-Exploit "CSSFontFace exploit reference repository"
