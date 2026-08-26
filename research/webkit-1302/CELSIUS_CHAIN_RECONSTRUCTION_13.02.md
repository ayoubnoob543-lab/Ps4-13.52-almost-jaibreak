# Reconstrucción documental de Celsius para PS4 FW 13.02

**Fecha:** 2026-08-27  
**Alcance:** análisis estático y documental de artefactos públicos. No se ejecutaron payloads ni corrupción de memoria en hardware.  
**Baseline de trabajo:** Celsius se acepta como baseline verificado para esta fase, conforme a la solicitud. El objetivo aquí es reconstruir qué piezas públicas permiten cubrir cada etapa y qué dependencias siguen faltando para 13.02.

## Cadena objetivo

> **WebKit/BD-J → userland → Celsius → `ffs_mountfs` → corrupción controlada → kernel R/W**

La evidencia pública permite construir modelos parciales de cada extremo, pero no una integración única 13.02. La separación más importante es entre el **entrypoint y la ejecución nativa en userland**, que sí tienen material público, y la **transición específica de Celsius hacia una primitive kernel R/W**, que no aparece como implementación completa.

## Matriz de piezas

| Pieza | Evidencia encontrada | Fuente y procedencia | Firmware | Qué permite hacer | Qué falta |
|---|---|---|---|---|---|
| Entrada WebKit/Vue | Código histórico de Vue After Free/CSSFontFace y referencias públicas a Vue para PS4 | `ntfargo/CSSFontFace-Exploit`, `Feyzee61/cssfontface_lapse`, referencias de escena; linaje histórico | Hasta generaciones antiguas; Vue se anuncia para rangos posteriores | Obtener ejecución userland en cadenas históricas y servir de modelo de bootstrap | Adaptación y prueba integrada con el runtime 13.02 concreto |
| Entrada BD-J | API Java nativa, resolución de símbolos, invocación nativa, carga remota de JAR | [`ps3120/BD-JB-1250`][1], código `src/org/bdj/api/API.java` y loaders | BD-J histórico; documentación pública afirma rangos recientes | Ejecutar llamadas nativas desde el entorno BD-J y cargar componentes | Primitive WebKit/Jordy específica para 13.02 y conexión con Celsius |
| Resolución `dlsym` | `API.dlsym` y helpers de resolución en Java; implementaciones históricas en Luac0re | BD-JB-1250; Luac0re `func.lua` | Históricos/PS5 según implementación | Resolver funciones de libc/libkernel cuando se dispone de handle y runtime | Bases, handles y ABI exactos del stage 13.02 |
| ROP/fcall userland | `__Ux86_64_setcontext`, `call_rop`, pivots y fcall en BD-J histórico/Luac0re/Cryptogenic | BD-JB-1250; Luac0re; PoC Cryptogenic | Históricos y plataformas distintas | Modelo para invocar funciones y cargar shellcode | Gadgets, pivot y cadena adaptados a WebKit/BD-J 13.02 |
| Primitive `m_vector`/Jordy | `jordy_stage2.js` usa `targetAddress` y helpers de lectura/escritura; bootstrap no incluido | `adri22235/ps4-suid-scanner`, commits `96a7948` y `1089382` | Reclama 13.04; sin prueba independiente | Describe la interfaz que stage 2 espera recibir | Implementación pública completa de la primitive, bases y `targetAddress` |
| Acceso a disco/USB | Documentación declara USB 3.0 y HDD ≥250 GB; BD-JB tiene loaders y acceso a archivos | GameGaz; BD-JB-1250; scanner `SuidScanner.java` | Claim hasta 13.04 | Proporciona el medio donde residiría o desde donde se serviría una imagen | Código que entregue el dispositivo/imagen al subsistema UFS de forma controlada |
| Imagen UFS/FFS | Documentación de Celsius exige imagen UFS con superbloque manipulado; `makefs/ffs.c` permite construir estructuras FFS genéricas | `v2.0/cve_analysis.md`; `third_party/makefs/ffs.c` | FreeBSD/artefactos históricos, no Orbis | Modelo de layout y generación de imágenes FFS | Imagen Celsius original, campos exactos, dispositivo/offset y validación contra Orbis |
| Ruta `mount` | Fusion/OSM publican `patch_mount`, `M_MOUNT`, `getnewvnode`, `vn_fullpath`, `kern_open`; kpayload publica otros parches PFS/Shell | Fusion `Offsets-1302.h`, OSM YAML, kpayload 13.02/13.04 | 13.02/13.04 según tablas | Ofrece candidatos para llamadas/patches VFS genéricos | Bytes objetivo, call site, prototipo y prueba de que `patch_mount` conduce a FFS |
| `ffs_mountfs` | Código histórico FreeBSD 9.1 con aritmética sobre `fs_cssize`, `fs_ncg`, `fs_contigsumsize`; claims del scanner | `freebsd-9.1-ffs_vfsops.c`; GameGaz; scanner | FreeBSD 9.1; claim PS4 ≤13.04 | Explica la hipótesis del overflow y los campos relevantes | Bytes/pseudocódigo Orbis 13.02 y comparación 13.50 |
| Condición de overflow | Claims describen suma/multiplicación de tamaños y loop posterior sobre `fs_ncg` | `cve_analysis.md` del scanner; copia FreeBSD | Claim 13.04; código FreeBSD 9.1 | Da una plantilla de análisis estático del flujo vulnerable | Confirmar tipos, validaciones y orden de operaciones en Orbis |
| Corrupción controlada | No se encontró PoC pública completa; documentación menciona heap grooming y conversión posterior | Scanner README/CVE analysis; comentarios de `jordy_stage2.js` | Claim 13.04 | Sólo define el objetivo conceptual | Primitive de corrupción, objetos afectados, grooming y control de datos |
| Kernel R/W posterior | Lapse/Poops y BD-J contienen puentes históricos `kread`/`kwrite`, `ucred`, `rootvnode`, `sysent` y carga de payload | `BD-JB-1250/payloads/lapse`, `payloads/poops`; `Feyzee61/cssfontface_lapse` | Históricos hasta 13.00/11.02 según cadena | Proporciona el modelo de post-exploit y parcheo | Adaptación 13.02 y conexión desde la corrupción Celsius |
| Offsets de kernel | Fusion/OSM/SLOPOS y SDK publican tablas; varias entradas 13.02/13.04 coinciden | ArabPixel/Fusion, OSM, SLOPOS, kpayload/SDK | 13.02/13.04 | Permiten resolver símbolos si ya existe kernel base/RW | Distinguir offsets funcionales de derivados y probarlos en hardware |
| Prueba completa | No se encontró log, vídeo técnico detallado con trazas, dump o PoC pública integrada | Búsquedas GitHub/web, ConsoleMods, fuentes secundarias | 13.02 | Ninguna ruta completa reproducible | Artefacto de integración o evidencia de hardware |

## Qué puede reutilizarse entre 13.00 y 13.02

La reutilización más sólida es conceptual y de infraestructura: el modelo de offsets relativos a la base del kernel, los helpers de lectura/escritura de los payloads históricos, la arquitectura BD-J para resolver/invocar funciones nativas y el conocimiento de los campos UFS relevantes. Las tablas muestran además valores coincidentes entre 13.02 y 13.04 para varias entradas generales, aunque esa coincidencia es una propiedad de las tablas y no demuestra identidad de bytes ni supervivencia de Celsius.

No se puede trasladar automáticamente la primitive Lapse/Poops a Celsius. Lapse usa una ruta de corrupción y objetos distintos, con layouts y offsets específicos. Del mismo modo, `jordy_stage2.js` no puede completarse simplemente copiando `func.lua` o `rop.lua` de Luac0re: esas implementaciones dependen de runtimes, gadgets, tablas y plataformas diferentes.

## Relación de `patch_mount` con la cadena

`patch_mount = 0x001512A7` aparece como una etiqueta de Fusion/OSM junto a símbolos VFS y de memoria. La búsqueda de código fuente, commits y coincidencias exactas no encontró bytes objetivo, nombre de función, call site ni referencia cruzada hacia `ffs_mountfs`. En `kpayload`, las entradas de montaje encontradas corresponden a PFS/Shell, no a FFS.

La interpretación más prudente es que `patch_mount` puede ser útil para una etapa de preparación del montaje, pero su relación con Celsius es todavía una hipótesis. La pieza que permitiría resolverlo sería un pequeño bloque de bytes o pseudocódigo alrededor de `0x1512A7`, con la función que se parchea y sus llamadas a VFS/FFS.

## Requisitos concretos para cerrar la reconstrucción

Para reconstruir estáticamente la etapa FFS se necesita un kernel Orbis 13.02 o 13.04, o un disassembly suficientemente completo, que permita mapear `ffs_mountfs` y verificar el flujo de campos del superbloque. Para reconstruir la etapa de explotación se necesita además la imagen UFS original o sus parámetros, el mecanismo que hace llegar esa imagen al mount, el bootstrap WebKit/BD-J que proporciona control, y la conversión de la corrupción en lectura/escritura kernel.

La evidencia del tag `v2.0` muestra que el proyecto tiene un puente histórico post-exploit útil como referencia: sus payloads Lapse/Poops realizan `kread`/`kwrite`, recorren `allproc`, modifican `ucred`/`rootvnode` y parchean `sysent[661]`. Pero la tabla no contiene 13.02/13.04 para esa cadena y no debe presentarse como adaptación de Celsius.

## Conclusión práctica

> **Con lo encontrado, podemos construir:** la infraestructura BD-J de llamadas nativas; un modelo de bootstrap WebKit/Jordy; una plantilla de resolución `dlsym`/ROP; el modelo de campos y aritmética FFS; la tabla de candidatos VFS/offsets 13.02; y un modelo histórico de kernel R/W posterior basado en Lapse/Poops.

> **Sólo faltan, para una reconstrucción funcional 13.02:** el bootstrap Jordy/WebKit completo con bases y pivot; el artefacto Orbis que identifique `ffs_mountfs` y permita asociar o descartar `patch_mount`; la imagen/parametrización UFS de Celsius; y una primitive de corrupción controlable que conecte el overflow con el puente kernel R/W.

Por tanto, el trabajo público permite construir una **arquitectura de reconstrucción y una lista precisa de interfaces**, pero no una cadena 13.02 ejecutable o verificable de extremo a extremo. La pieza única más informativa sigue siendo un disassembly/dump legítimo de Orbis 13.02/13.04 con `ffs_mountfs`; la pieza única más decisiva para cerrar la ruta completa sería un PoC o log de hardware que muestre la transición desde el montaje hasta una lectura/escritura kernel.

## Referencias

[1]: https://github.com/ps3120/BD-JB-1250 — BD-JB-1250, API y payloads BD-J.
[2]: https://github.com/adri22235/ps4-suid-scanner — scanner, documentación Celsius y stage 2.
[3]: https://gamegaz.com/2026071945823/ — resumen secundario de Celsius, requisitos y atribución.
[4]: https://github.com/freebsd/freebsd-src/blob/release/9.1.0/sys/ufs/ffs/ffs_vfsops.c — referencia histórica de FFS.
[5]: https://github.com/AetherPS/Fusion — tabla Fusion/offsets y `patch_mount`.
[6]: https://github.com/OSM-Made/PS4-Kernel-SDK — tabla YAML derivada de offsets.
[7]: https://consolemods.org/wiki/PS4:Exploit_Chart — estado público de exploits por firmware.
[8]: https://github.com/Scene-Collective/ps4-kernel-dumper — dumper histórico para PS4.
[9]: https://github.com/obhq/kernel-dumper — dumper/documentación histórica con soporte declarado 11.00.

## Nueva pieza parcial: `libufs` del SDK

La auditoría del SDK público `ps4-payload-dev/sdk` añadió una pieza útil para la reconstrucción de la imagen: `libufs` contiene rutinas userland como `ufs_disk_fillout`, `ufs_disk_fillout_blank` y `sbread` para abrir dispositivos o imágenes y leer estructuras de superbloque. El release v0.4 también anuncia `nmount` y el release v0.8 una implementación inicial de `libufs`.

Esta pieza permite estudiar o generar metadatos FFS fuera de la consola, pero no implementa el kernel `ffs_mountfs`, no aporta la imagen Celsius original, no define cómo llegar al dispositivo USB/HDD de Orbis y no convierte ninguna corrupción en kernel R/W. Se clasifica como **VERIFIED** para la herramienta userland FreeBSD, **SOURCE_ONLY** para su posible utilidad en la imagen Celsius y **NOT PROVIDED** para la transición kernel.

## Auditoría focalizada de las cuatro piezas faltantes

### Bootstrap WebKit/Jordy

La búsqueda dirigida encontró una referencia secundaria a una liberación WebKit para 13.00 que usa “Jordy's AI WebKit”, pero no una copia pública completa del bootstrap que suministre simultáneamente `targetAddress`, `m_vector`, bases WebKit/libkernel, pivot y gadgets. La URL presumida `Scene-Collective/psfree` no resolvió en GitHub y no se trató como fuente. Estado: **parcialmente identificado como interfaz/claim, no conseguido como bootstrap completo**.

### Artefacto Orbis y `patch_mount`

No apareció un binario, disassembly, pseudocódigo o hash de Orbis 13.02/13.04 que identifique `ffs_mountfs`. `patch_mount = 0x001512A7` sigue siendo una etiqueta de tabla Fusion/OSM sin call site ni bytes. Estado: **no conseguido**. El artefacto decisivo sería un kernel/`libkernel` legítimo o un recorte de disassembly con referencias cruzadas a esa dirección.

### Imagen UFS/FFS

El SDK público aporta `libufs` userland y headers FreeBSD; sus rutinas permiten leer dispositivos/imágenes, superbloques y grupos de cilindros. Eso permite construir un laboratorio offline de estructuras FFS, pero no se encontró la imagen Celsius, sus campos exactos ni una parametrización publicada. Estado: **herramienta parcial conseguida; imagen Celsius no conseguida**.

### Primitive Celsius→kernel R/W

El SDK expone `kernel_copyin`/`kernel_copyout` y el árbol BD-JB contiene un puente histórico `kread`/`kwrite`, recorrido de `allproc`, modificación de `ucred`/`rootvnode` y parche de `sysent`. Ambos son consumidores o puentes de cadenas distintas: no incluyen la primitive inicial que convertiría el overflow de Celsius en R/W, y no existe una adaptación pública 13.02. Estado: **modelo histórico conseguido; primitive Celsius no conseguida**.

## Estado de cierre de la búsqueda focalizada

| Pieza | ¿Conseguida? | Artefacto concreto que podría cerrarla | Siguiente objetivo de búsqueda |
|---|---|---|---|
| Bootstrap WebKit/Jordy completo | **No**. Sólo se confirmó la interfaz esperada (`targetAddress`, `m_vector`, bases y helpers) y una referencia secundaria a Jordy para 13.00 | Una copia histórica del árbol WebKit/Jordy o de `jordy_stage2.js` con inicialización, bases, pivot y gadgets | Historiales, mirrors y releases del proyecto que publicó la referencia 13.00; no asumir que `Scene-Collective/psfree` es ese proyecto porque la URL no resolvió |
| Orbis `ffs_mountfs` / `patch_mount` | **No**. `patch_mount` sigue siendo un nombre de tabla sin bytes ni xref | Dump o disassembly legítimo de Orbis 13.02/13.04 con el bloque de montaje y una referencia al offset `0x1512A7` | Artefactos de análisis estático de kernels 13.02/13.04, proyectos IDA/Ghidra o capturas con símbolos/call graph |
| Imagen/parametrización UFS | **Parcial**. `libufs`, headers y rutinas de superbloque permiten modelar FFS offline | La imagen original de Celsius, un hash o una receta pública de campos del superbloque y dispositivo usado | Mirar artefactos asociados a la ISO/USB de Celsius y commits del scanner, no generar ni probar imágenes contra hardware |
| Primitive Celsius→kernel R/W | **No**. Sólo existe el modelo histórico Lapse/Poops y APIs consumidoras del SDK | Código o log técnico que muestre objeto afectado, corrupción controlada y posterior `kread`/`kwrite` en la misma cadena | Buscar una derivación de Celsius que cite estructuras de kernel y una secuencia de R/W; separar siempre los puentes Lapse/Poops por ser otra primitive |

La única pieza nueva parcialmente conseguida en esta fase es la **infraestructura userland de imagen FFS**: `libufs` permite leer/escribir estructuras UFS y el SDK aporta headers coherentes con FreeBSD. No equivale a la imagen de Celsius ni al trigger Orbis. La rama también conserva un modelo histórico de kernel R/W, pero no se clasifica como integración Celsius.

En términos prácticos, la reconstrucción pública actual puede llegar hasta un **diseño estático de interfaces y dependencias**, no hasta una cadena ejecutable 13.02. Los dos artefactos de mayor valor informativo son, en orden, un disassembly legítimo de `ffs_mountfs` Orbis 13.02/13.04 y una copia del bootstrap Jordy que entregue control de datos/llamadas; el artefacto que cerraría funcionalmente la cadena sería un PoC o log de hardware que conecte ambos con la primitive R/W. Esta conclusión no requiere volver a investigar la existencia de Celsius.
