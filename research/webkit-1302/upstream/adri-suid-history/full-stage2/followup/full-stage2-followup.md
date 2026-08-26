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

## Referencias

[1]: https://github.com/Cryptogenic/PS4-4.0x-Code-Execution-PoC/blob/master/index.html "Cryptogenic PS4 4.0x Code Execution PoC"

[2]: https://github.com/adri22235/ps4-suid-scanner/commit/1089382ec1e0000e9557b7748d39b57952bbc4f3 "Commit 1089382"

[3]: https://github.com/adri22235/ps4-suid-scanner/commit/702fcc397d45546baab5311bc0a264870ae90042 "Commit de gadgets WebKit 13.04"

[4]: https://github.com/Gezine/Luac0re/blob/main/lua/func.lua "Luac0re func.lua"

[5]: https://github.com/Gezine/Luac0re/blob/main/lua/rop.lua "Luac0re rop.lua"

[6]: https://github.com/zecoxao/zecoxao.github.io "Páginas relacionadas zecoxao"
