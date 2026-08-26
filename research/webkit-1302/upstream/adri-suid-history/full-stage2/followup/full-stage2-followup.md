# Seguimiento: piezas faltantes alrededor de `1089382`

**Ámbito:** sólo análisis documental y estático. No se ejecutaron archivos JavaScript, Lua, shellcode, exploits ni payloads.

## Resumen

La investigación confirma que `jordy_stage2.js` forma parte de una cadena documental mayor, pero no se ha localizado una versión completa de esa cadena para PS4 13.02/13.04. Las piezas externas encontradas se dividen en tres familias. La primera es el propio historial del scanner, que aporta gadgets WebKit y claims de kernel/FFS sin los artefactos de origen. La segunda son plantillas zecoxao/Luac0re para PS5, que describen o implementan parcialmente fcall, dlsym, JIT y ROP con dependencias específicas. La tercera es un PoC histórico de Cryptogenic para PS4 antiguo que sí implementa bases de módulos y ROP, pero utiliza otra explotación, otro API y otros offsets.

| Pieza | Contenido real | ¿Completa el stage 2 PS4 13.04? | Clasificación |
|---|---|---:|---|
| `1089382/jordy_stage2.js` | Helpers R/W, gadgets, skeleton de resolución y comentarios Celsius. | No. | **VERIFIED / INCOMPLETE** |
| `702fcc3/webkit_gadgets_1304.js` | 16 gadgets y claims de una SPRX 13.04 ausente. | No. | **VERIFIED / SOURCE_ONLY** |
| zecoxao `p2jb`/`poops` | Driver PS5 con offsets cero y TODOs. | No. | **VERIFIED / INVALID para completar** |
| Luac0re `func.lua`/`rop.lua` | `dlsym`, `func_wrap` y `call_rop` reales dentro de runtime Lua. | No directamente. | **VERIFIED en PS5/runtime Luac0re; SOURCE_ONLY para Jordy** |
| Cryptogenic PS4 4.0x PoC | Base WebKit/libkernel, import map y ROP ejecutables para firmware antiguo. | No. | **VERIFIED para su objetivo histórico; INVALID como compatibilidad 13.04** |
| Forks del scanner | Copias idénticas o sin stage 2. | No. | **DERIVED / NO INDEPENDIENTE** |

## Linaje del scanner

El historial remoto público sólo expone `main → 1089382` y `v2.0 → 3fd35a4`; no existen ramas o tags públicos adicionales. La secuencia relevante es `702fcc3 → 96a7948 → 1089382`. El commit 702fcc3 añadió los gadgets WebKit 13.04; el commit 96a7948 añadió un skeleton explícitamente titulado “Jordy r/w → ROP → Celsius for 13.04”; y 1089382 reemplazó ese skeleton por el archivo de 302 líneas titulado “full stage 2”.

La búsqueda de todo el árbol no encuentra un archivo auxiliar que defina `targetAddress`, `stage2_init`, la base WebKit, la base libkernel, la llamada a `mount` o el pivot. En el propio archivo, `targetAddress` se declara como dependencia suministrada por Jordy, pero no se proporciona el bootstrap Jordy.

## Piezas reutilizadas

### Gadgets WebKit 13.04

Los valores de `G` en `jordy_stage2.js` coinciden con los valores de `webkit_gadgets_1304.js` del commit 702fcc3. Esto demuestra reutilización directa de la tabla de gadgets. El archivo adyacente afirma que la fuente fue `1304_libSceNKWebKit.sprx.decrypted (68 MB) from zecoxao` y que los gadgets se obtuvieron mediante búsqueda de patrones. El SPRX no está incluido en el repositorio, no tiene hash público en este proyecto y no se aporta disassembly alrededor de cada gadget.

La misma tabla incluye comentarios que afirman que los kernels 13.00 y 13.04 tendrían tamaño 20.080.104 bytes, que la cadena `ffs_mountfs` aparecería en `0x7d021f` en ambos y que “Celsius [is] NOT patched”. Esas afirmaciones son texto de commit/archivo, no resultados reproducibles: faltan ambos kernels, hashes, diff, bytes circundantes, referencia cruzada y límites de función. Clasificación: **SOURCE_ONLY** para la comparación y **UNVERIFIED** para Celsius.

### Plantillas zecoxao

Las páginas `userland_only`, `p2jb` y `poops` de `zecoxao/zecoxao.github.io` comparten un driver Luac0re → WebKit. Incluyen funciones con nombres similares a las piezas que faltan —`make_fcall`, `resolve_dlsym`, `alloc_rwx_and_write`, `create_sockets` y `driver_entry`—, pero los offsets de firmware son cero y las funciones lanzan errores TODO o dependen de valores no suministrados. `SHELLCODE_HEX` se espera desde una concatenación de build y no aparece como artefacto completo en la página.

La similitud demuestra una fuente conceptual o una plantilla relacionada, pero no una implementación escondida del stage 2 PS4. La tabla de zecoxao incluye firmware PS5 12.02–12.70 y userland 13.00–13.60, no valores verificables de PS4 13.02/13.04.

### Luac0re `func.lua` y `rop.lua`

`func.lua` sí implementa `func_wrap`, `dlsym` e `init_dlsym`. En su rama PS4 calcula una dirección candidata a `sceKernelDlsym` desde `LIBC_OFFSETS.sceKernelGetModuleInfoFromAddr - 0x3A0`, verifica una firma de 18 bytes y, si no coincide, busca esa firma. Después envuelve la función en `call_rop`. Esta lógica no contiene una tabla explícita 13.02/13.04 y depende del runtime Lua, las tablas de libkernel y helpers como `read_buffer` y `find_pattern`.

`rop.lua` implementa `call_rop` con una cadena concreta que guarda argumentos, preserva RBP, calcula RSP, prepara pivots, usa `POP_RSP_RET` y llama a `call_rop_internal`. Es una pieza real de ROP dentro de Luac0re, pero utiliza símbolos globales y gadgets de ese runtime (`LUA_PIVOT_SCRATCH`, `STRING_BASE`, `LUA_STATE`, `write64_unstable`, `read64_unstable`). No puede trasladarse a `jordy_stage2.js` por coincidencia nominal.

### PoC histórico de Cryptogenic

El [PoC PS4 4.0x de Cryptogenic][1] implementa un modelo histórico de resolución de bases: deriva WebKit mediante una fuga de `parseFloat`, calcula libkernel leyendo el puntero importado de `__stack_chk_fail` y restando `0xd000`, selecciona mapas por firmware y realiza un pivot ROP con `pop rsp`. También implementa `p.call` y `p.syscall`.

Este PoC es la mejor fuente pública encontrada para explicar cómo podrían completarse conceptualmente `findWebkitBase`, `findLibkernelBase` y `executeRop`. No es un artefacto 13.02/13.04: usa el API antiguo `p.read8`, `int64`, `rop`, mapas de importaciones históricos y offsets de otra generación de WebKit. No contiene mount UFS, `ffs_mountfs`, Celsius ni offsets del scanner.

## Comparación de lagunas

| Función faltante en Jordy | Fuente relacionada | ¿Hay implementación encontrada? | Limitación |
|---|---|---:|---|
| `findWebkitBase()` | Cryptogenic histórico; zecoxao conceptual. | Parcial, sólo histórica. | Offset/vtable 13.04 ausente. |
| `findLibkernelBase()` | Cryptogenic histórico; Luac0re runtime. | Sí, en otros contextos. | GOT/import map 13.04 ausente. |
| `dlsym` | Luac0re `func.lua`. | Sí, Lua. | No adaptado al contexto Jordy. |
| fcall | Luac0re `func.lua` + `rop.lua`; Cryptogenic. | Sí, en otros contextos. | Gadgets, pivots y estructuras incompatibles/no portados. |
| Mount UFS/FFS | Sólo comentarios de Jordy. | No. | Sin imagen UFS, argumentos, dirección o código. |
| `ffs_mountfs` | Claim en `webkit_gadgets_1304.js`. | No. | Sin bytes, símbolo o disassembly. |
| Kernel R/W | Claims de README/stage 2. | No. | No hay primitive ni log de hardware. |
| ROP pivot | Luac0re/Cryptogenic históricos. | Sí, fuera del target. | No integrado ni verificado para 13.04. |

## Valor probatorio para Celsius y 13.02

La nueva evidencia permite decir que el stage 2 fue diseñado como una pieza de integración que esperaba una primitive Jordy ya viva y pretendía conectarla con un fcall ROP, `dlsym`, una llamada a `mount` y una supuesta transición Celsius. También permite identificar de dónde parecen proceder sus gadgets: la tabla WebKit 13.04 del commit anterior.

No permite afirmar que exista una imagen UFS funcional, que `mount` llegue a `ffs_mountfs`, que la cadena produzca kernel R/W o que los offsets del scanner hayan sido probados en 13.02. Las implementaciones relacionadas son históricas o de PS5 y no constituyen corroboración independiente de Celsius.

El artefacto más informativo que falta sigue siendo uno de estos: el SPRX 13.04 atribuido a zecoxao con hash y bytes; el supuesto kernel 13.00/13.04 usado para la comparación `0x7d021f`; una copia del bootstrap Jordy que defina `targetAddress` y el pivot; o un log/documento de hardware que muestre la llamada de montaje y una primitive fuera del proceso. Sin uno de ellos, las piezas no se pueden reconstruir de forma verificable.

## Clasificación consolidada

> **VERIFIED:** el commit 1089382 existe; su padre y su diff son recuperables; los gadgets se copian del archivo 13.04 adyacente; existen implementaciones históricas de ROP/fcall en Cryptogenic y Luac0re para sus respectivos objetivos.

> **CORROBORATED:** `jordy_stage2.js` es una pieza de diseño conectada conceptualmente con drivers Luac0re/P2JB y con técnicas históricas de WebKit ROP.

> **SOURCE_ONLY:** los claims de que el kernel 13.00/13.04 tiene una cadena `ffs_mountfs` en el mismo offset, que Celsius no está parcheado y que existen dumps de zecoxao/midohar36.

> **HYPOTHESIS / UNVERIFIED:** que esa pieza pudiera llegar a montar una imagen UFS y obtener kernel R/W en 13.04 o 13.02.

> **INVALID como PoC funcional:** presentar el archivo 1089382, las páginas zecoxao o los offsets aislados como una cadena ejecutable completa.

## Actualización de seguimiento

La auditoría posterior de todas las refs remotas confirma que sólo existen `main → 1089382` y `v2.0 → 3fd35a4`; no hay ramas ni tags públicos adicionales. La búsqueda completa del árbol tampoco encuentra la implementación de `org.bdj.api.API` importada por `SuidScanner.java`, por lo que incluso las llamadas `API.dlsym` y `API.call` del scanner dependen de un runtime externo y no completan la cadena WebKit/Jordy.

La búsqueda de identificadores internos (`call_rop_internal`, `LUA_PIVOT_SCRATCH`, `init_dlsym`) no encontró otro proyecto indexado fuera de Luac0re y sus derivados. Luac0re contiene una implementación real de `call_rop`, `func_wrap` y `init_dlsym`, pero sus dependencias son Lua, tablas de runtime y gadgets PS5/firmware específicos. El PoC histórico de Cryptogenic contiene otra implementación real de fcall/base/pivot para PS4 antiguo; tampoco aporta mount UFS, FFS o Celsius.

Estos hallazgos refuerzan la conclusión de que `jordy_stage2.js` es una pieza de diseño que reutiliza gadgets y nomenclatura de otras cadenas, pero no una integración incompleta cuya lógica decisiva esté publicada en otro archivo del repositorio. La única evidencia nueva sobre Celsius sigue siendo el claim textual en `webkit_gadgets_1304.js`; no se ha encontrado el kernel, SPRX, imagen UFS, bootstrap Jordy ni log de hardware que lo respalde.

## Nueva comparación: P2JB C frente a Jordy

La revisión de `jit_shellcode/p2jb/p2jb.c` de Luac0re encuentra una implementación C real de una fase posterior con `kread64`/`kwrite64`, resolución de funciones mediante `dlsym`, manipulación de `ucred`, localización de `curproc`/`allproc` y parcheo de `rootvnode`. No obstante, la cabecera fija un entorno PS5 con sockets IPv6, triple-free, kqueue, `KQUEUEEX_*`, `UCRED_SIZE` y offsets específicos de estructuras PS5. No hay símbolos UFS, `ffs_mountfs`, imagen de filesystem ni Celsius.

Esto permite separar dos conceptos que el repositorio mezcla en sus comentarios. Luac0re/P2JB contiene una fase kernel-R/W concreta, pero para otra plataforma y otra vulnerabilidad; `jordy_stage2.js` contiene una capa de helpers y una arquitectura propuesta, pero no contiene la primitive de entrada, el pivot ni el trigger FFS. La existencia de código PS5 con nombres similares (`dlsym`, `func_wrap`, `kread64`, `kwrite64`) no es evidencia de compatibilidad con PS4 13.02.

| Afirmación | Evidencia encontrada | Clasificación |
|---|---|---|
| P2JB tiene código C de kernel-R/W | `p2jb.c` modifica `ucred`, `rootvnode` y estructuras de proceso. | **VERIFIED en PS5/P2JB** |
| Jordy puede reutilizar directamente P2JB | No hay adaptación de plataforma, offsets ni ABI. | **INVALID** |
| P2JB demuestra Celsius | No contiene FFS/mount ni `ffs_mountfs`. | **INVALID** |
| `jordy_stage2.js` era sólo una interfaz a una pieza C externa | No se encontró ninguna referencia a `p2jb.c`/Luac0re en su árbol Git. | **HYPOTHESIS**, no demostrada |

## Nuevo hallazgo: commit zecoxao “kern and user jordy”

El rastreo de la referencia `p2jb/index.html` descubrió el commit [`1630d79d2a7146a65436e5f2fc0ff5dc6d9ba07b`][7], cuyo mensaje es `kern and user jordy`. El commit añade tres páginas de 1110/1111 líneas (`p2jb`, `poops` y `userland_only`) y tiene metadatos de autoría genéricos (`Your Name`, `you@example.com`).

La recuperación exacta del commit confirma que no es una cadena operativa oculta. `FW_OFFSETS` contiene cero para dlsym, JIT, gadgets y pivots; `make_fcall`, `alloc_rwx_and_write` y `create_sockets` siguen siendo TODOs; `libkernel_base` y `eboot_base` se dejan como cero; `SHELLCODE_HEX` está vacío en userland mode; y no hay imagen UFS, mount, `ffs_mountfs` ni código Celsius. El commit es una pista de procedencia conceptual —el nombre “kern and user jordy”—, pero no una pieza que complete el stage 2.

| Hallazgo del commit 1630d79 | Estado |
|---|---|
| Commit y tres páginas existen | **VERIFIED** |
| “kern and user” como implementación completa | **SOURCE_ONLY / misleading title** |
| Valores 13.02/13.04 utilizables | **INVALID** |
| fcall/dlsym/pivot completo | **INVALID** |
| Celsius/FFS | **UNVERIFIED; no código presente** |

## Nuevo hallazgo de linaje: Jordy 11.60 y la cadena PS4 histórica

El commit padre de `1630d79`, [`c6b52aea`][9], añade únicamente `jordy/index.html` (786 líneas). El archivo se identifica expresamente como bootstrap de WebKit/RW para **PS5 FW 11.60 / WebKit 616.1**. La implementación valida arbitrary read/write userland mediante el layout `JSFinalObject`/`m_vector`, pero el escaneo completo no encuentra `kernel`, `kread`, `kwrite`, `ffs`, `Celsius`, `mount`, `dlsym`, `pivot`, `ROP`, `libkernel`, `SHELLCODE` ni `FW_OFFSETS`. Por tanto, “jordy 11.60” no es la pieza kernel omitida de `jordy_stage2.js`.

La cadena PS4 completa localizada en esta investigación procede de una línea distinta y anterior: `ps3120/CSSFontFace-Exploit` → `ntfargo/CSSFontFace-Exploit`/`ufm42/wobkot`. El commit [`6f33986`][10] añade `netctrl.js`, `ps4/kernel.js`, `ps4/userland.js`, workers, constantes, ROP y blobs de parches para 6.00–11.02. Los progenitores y la cadena primaria contienen implementación real de kernel R/W histórica, pero no contienen 13.02/13.04, `ffs_mountfs`, Celsius ni el nombre `jordy_stage2`.

Esta separación es importante: el stage 2 de `ps4-suid-scanner` parece combinar terminología de bootstrap WebKit/Jordy con una arquitectura de segunda fase que no está presente en el artefacto PS5 11.60 ni se puede atribuir textualmente a la cadena PS4 Netctrl/Lapse. La evidencia de reutilización directa sigue siendo insuficiente.

## Nuevo candidato relacionado: CSSFontFace/Lapse PS4 histórico

La búsqueda de proyectos citados por `netctrl-ps5.js` localizó [`Feyzee61/cssfontface_lapse`][8], un fork declarado de `wobkot` y `CSSFontFace-Exploit`. Su `public/lapse.js` contiene una fase PS4 real de kernel R/W basada en `pktopts`: valida una lectura de una cadena del kernel, deriva `kbase`, recorre `pcpu → curthread → proc`, obtiene `p_ucred`, y construye `KernelMemory` con `copyin`, `copyout`, `read64` y `write64`. También contiene blobs de parche kernel por firmware y modificación de `sysent[661]`.

La procedencia y el alcance deben limitarse cuidadosamente. El README declara pruebas completas sólo en 9.00 y 9.60, 11.02 funcionando en el entrypoint y ROP 10.00–11.02 todavía pendiente. La tabla de firmware no contiene 13.02 ni 13.04. Los binarios payload se excluyen del repositorio. Por ello, este proyecto demuestra que existió una cadena pública PS4 WebKit → kernel R/W en una generación anterior, pero no completa `jordy_stage2.js`, no contiene Celsius/FFS y no demuestra supervivencia de Netctrl/Lapse en 13.02.

| Evidencia de CSSFontFace/Lapse | Clasificación |
|---|---|
| Código estático de kernel R/W PS4 histórico | **VERIFIED** dentro de su alcance declarado |
| Prueba de 9.00/9.60 según README | **SOURCE_ONLY** hasta recuperar logs independientes |
| 11.02 completo | **SOURCE_ONLY / INCOMPLETE** |
| 13.02/13.04 | **UNVERIFIED** |
| Relación directa con Celsius o `jordy_stage2.js` | **INVALID / no demostrada** |

## Referencias

[1]: https://github.com/Cryptogenic/PS4-4.0x-Code-Execution-PoC/blob/master/index.html "Cryptogenic PS4 4.0x Code Execution PoC"

[2]: https://github.com/adri22235/ps4-suid-scanner/commit/1089382ec1e0000e9557b7748d39b57952bbc4f3 "Commit 1089382"

[3]: https://github.com/adri22235/ps4-suid-scanner/commit/702fcc397d45546baab5311bc0a264870ae90042 "Commit de gadgets WebKit 13.04"

[4]: https://github.com/Gezine/Luac0re/blob/main/lua/func.lua "Luac0re func.lua"

[5]: https://github.com/Gezine/Luac0re/blob/main/lua/rop.lua "Luac0re rop.lua"

[6]: https://github.com/zecoxao/zecoxao.github.io "Páginas relacionadas zecoxao"

[7]: https://github.com/zecoxao/zecoxao.github.io/commit/1630d79d2a7146a65436e5f2fc0ff5dc6d9ba07b "Commit zecoxao: kern and user jordy"

[8]: https://github.com/Feyzee61/cssfontface_lapse "Feyzee61 CSSFontFace Lapse"

[9]: https://github.com/zecoxao/zecoxao.github.io/commit/c6b52aea9e212427aa54b12b35557877363f1940 "Commit zecoxao: jordy 11.60"

[10]: https://github.com/ntfargo/CSSFontFace-Exploit/commit/6f3398616ac0e3a0a7b45bf33730529a75578db7 "Commit ntfargo/ufm42: full chain exploit with lapse and netctrl"


## Seguimiento adicional: forks, archivos eliminados y origen de las referencias FFS

La enumeración limpia de 80 forks públicos de `ntfargo/CSSFontFace-Exploit` encontró repetidamente la familia histórica `lapse.js`/`netctrl.js`/`ps4/kernel.js`, y en algunos casos `offsets.mjs`. No se encontró ningún `jordy_stage2.js`, archivo dedicado de Celsius, `ffs_mountfs` ni extensión 13.02/13.04. El resultado es propagación de la cadena histórica, no corroboración independiente.

El fork `hejran7/CSSFontFace-Exploit` contiene dos binarios adicionales, `pl_KernelDumper.bin` y `pl_KernelClock.bin`, introducidos exactamente por `d29bd6c` el 4 de agosto de 2026. El análisis estático da tamaños de 17.832 y 13.184 bytes, prólogos x86-64 y strings de APIs PS4/libkernel. `menu.js` los registra como payloads de dumper. No son imágenes de kernel, no tienen marcador 13.02 y no contienen UFS/FFS/Celsius. Además, `host/src/ps4/kernel.js` comenta que `kernel_patches()` está destinada a usarse “only after kernel arw”, confirmando que es infraestructura consumidora de una primitive ya obtenida.

La búsqueda de archivos eliminados muestra que `ps4-suid-scanner` sí elimina `stage2_jordy.js`, pero no aparece un sucesor más completo en el historial recuperable. En los repositorios CSSFontFace relacionados se eliminan módulos y parches históricos, no una implementación Celsius/13.02. El pickaxe Git muestra que `ffs_mountfs` y Celsius aparecen como texto añadido en `ps4-suid-scanner` en `96a7948` y `1089382`, además de la documentación de gadgets; no aparecen en la genealogía textual de `ntfargo`, `ps3120`, `wobkot` o `hejran7`.

**Clasificación:** red de forks históricos, **DERIVED/NO INDEPENDIENTE**; payloads `hejran7`, **VERIFIED como herramientas** pero **UNVERIFIED para 13.02**; archivos eliminados, **VERIFIED**; procedencia de la narrativa `ffs_mountfs`/Celsius desde el scanner, **CORROBORATED por historial Git**; existencia de una pieza externa que complete Jordy, **no encontrada / UNVERIFIED**.


## Verificación directa del commit de gadgets 13.04

La respuesta limpia de la API de GitHub para `702fcc397d45546baab5311bc0a264870ae90042` muestra que el commit añade exactamente un archivo: `webkit_gadgets_1304.js`. El patch introduce literalmente los claims `1304_libSceNKWebKit.sprx.decrypted (68 MB) from zecoxao`, `ffs_mountfs string at 0x7d021f in BOTH (Celsius NOT patched)` y `CONFIRMED: Celsius (ffs_mount) is present in 13.04 kernel`. No añade URL de descarga, hash, binario, bytes circundantes, disassembly, límites de función, log de prueba ni referencia cruzada. La clasificación correcta es: existencia del texto `VERIFIED`; existencia del SPRX y comparación de kernels `SOURCE_ONLY`; Celsius en 13.04/13.02 `UNVERIFIED`.

## Auditoría de refs completas del scanner

El clon completo, con ramas remotas y tags, expone únicamente `main`, `origin/main`, `origin/HEAD` y `v2.0`; todos apuntan a la historia pública auditada. Los únicos archivos de stage 2 son `stage2_jordy.js` (añadido en `96a7948`, 2026-08-09) y `jordy_stage2.js` (añadido en `1089382`, 2026-08-09, reemplazando al anterior). No aparecen archivos alternativos con nombres `stage2`, `jordy`, `rop`, `webkit` o `dlsym` en otras ramas/tags.

El historial conserva además `webkit_gadgets_1304.js` (`702fcc3`) y `webkit_gadgets_1350.js` (`b1570ef`), pero no un blob de kernel ni una implementación separada de Celsius. El resultado no prueba que no existan copias fuera de GitHub; sí demuestra que no están en refs públicas del repositorio consultado. Clasificación: inventario de refs/archivos `VERIFIED`; ausencia de copias fuera del repositorio `UNVERIFIED`.
