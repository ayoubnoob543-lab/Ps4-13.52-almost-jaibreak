# Artefactos públicos para analizar Orbis PS4 13.02

## Objetivo y estándar

Este informe evalúa qué puede inferirse de artefactos públicos sobre PS4 FW 13.02, 13.04 y 13.50, con especial atención a la afirmación de `adri22235/ps4-suid-scanner` de que los offsets 13.04 están “based on 13.02 (identical kernel)” y fueron verificados por una tabla de Pharaoh2k. No se ejecutaron payloads, corrupción de memoria ni pruebas contra hardware.

Se distingue entre igualdad de archivos o tablas, igualdad de offsets, base común con cambios y mera afirmación editorial. **Una tabla de offsets idéntica no equivale a bytes de kernel idénticos.**

## 1. Artefactos 13.02 encontrados

| Artefacto | Estado de procedencia | Contenido | Utilidad para el kernel Orbis |
|---|---|---|---|
| `kpayload/source/offsets/1302.c` | Local versionado; hash `5a0b…` registrado en snapshot | Tabla de offsets de payload | Permite comparar direcciones, no reconstruir el kernel |
| `kpayload/include/offsets/1302.h` | Local versionado; SHA-256 `ec8b59f7a43a2ba5460e5d0d87d7252062885dfc4b35dee7a8b1cf92b7c43939` | Declaración de tabla | Sin código FFS |
| `research/results/slopos/1302.h` | Copia local de tabla pública SLOPOS | Offsets `sysent`, `prison0`, `rootvnode`, VM y otros | No contiene símbolos ni bytes FFS |
| `research/webkit-1302/upstream/riyon-kernel.ts` | Snapshot local de GitHub Riyon/Vue | Tablas de payload y offsets mmap/RWX | La entrada 13.02 no demuestra Netctrl ni FFS |
| `research/webkit-1302/upstream/ps4-linux-loader-13xx-check.txt` | Snapshot de consulta pública | Commits y referencias de offsets/kexec | Aporta offsets/payload, no FFS |
| `13.02` en documentación local | Documentación derivada | Afirmaciones sobre WebKit, kexec y offsets | No es artefacto de kernel |
| Fuentes de `adri22235/ps4-suid-scanner` | Repo público creado 18 jul. 2026 | `1304.c`, `1304.h`, README y análisis | Contiene offsets y afirmaciones, no kernel Orbis |

No se encontró ningún `kernel.bin`, `system_fs_image.img` descifrado, ELF de kernel, dump retail, `ffs_mountfs` symbol map, pseudocódigo de Orbis, `Orbis*.hpp` con FFS, header de `struct fs` específico de Orbis ni tabla de referencias cruzadas para 13.02.

El repositorio local contiene `libkernel_sys_13.52.bin`, pero es de 13.52, no es kernel Orbis y no permite demostrar FFS en 13.02. También contiene `scanner_1304.iso` y manifests estáticos, que no son kernels ni dumps de FFS.

## 2. Fuente adri22235 y frase “identical kernel”

El README de `adri22235/ps4-suid-scanner` dice:

> “Full offsets in `1304.c` — based on 13.02 (identical kernel) verified by Pharaoh2k's offset table.”

El mismo repo se creó el 18 de julio de 2026 y su historial público tiene commits concentrados entre el 18 de julio y el 9 de agosto. El archivo `1304.c` incluye comentarios equivalentes a “Based on 13.02 offsets (identical kernel) + Pharaoh2k's verification table”.

Esto demuestra que la frase existe en el repo de Adrián y que la atribución a Pharaoh2k forma parte de su documentación. No demuestra quién produjo la tabla original ni qué significa “identical”. La consulta directa al perfil público de Pharaoh2k —27 repositorios visibles— no localizó una tabla pública identificable de 13.02/13.04, un commit de offsets FFS o un kernel Orbis. El repositorio público de Pharaoh2k más relacionado, `PlayStation-Payload-Center`, es un catálogo/cliente de payloads y no aporta un análisis FFS 13.02/13.04.

**Clasificación de la frase:** `SOURCE_ONLY`.

## 3. Comparación de tablas 13.02 y 13.04

Los archivos locales `kpayload/source/offsets/1302.c` y `1304.c` tienen tamaños diferentes —5895 y 5968 bytes— y hashes diferentes. Sin embargo, el parser de campos encontró los mismos valores para todos los campos de offsets presentes en ambas tablas: `SYSENT_addr`, `PRISON0_addr`, `ROOTVNODE_addr`, `ALLPROC_addr`, `kernel_map`/VM, funciones de memoria, funciones de autenticación, hooks, parches de shell y offsets de procesos.

Esto permite afirmar:

| Afirmación | Resultado |
|---|---|
| Los archivos `1302.c` y `1304.c` son byte a byte idénticos | **Falso**; tienen hashes/tamaños distintos |
| Las tablas locales contienen los mismos campos y valores | **Verdadero para el contenido de esas tablas** |
| Los offsets relevantes publicados son iguales | **Corroborado por comparación local** |
| Los kernels Orbis 13.02 y 13.04 tienen bytes idénticos | No demostrado |
| Los kernels comparten una base o build con cambios menores | Plausible, pero no demostrado por estas tablas |
| “Identical kernel” significa sólo igualdad de offsets | Es la interpretación más compatible con la evidencia disponible, pero sigue siendo inferencia |

La igualdad completa de los valores de la tabla incluye, entre otros, `SYSENT_addr = 0x01102B70`, `PRISON0_addr = 0x0111FA18`, `ROOTVNODE_addr = 0x02136E90`, `ALLPROC_addr = 0x01B28538`, `malloc_addr = 0x00009520`, `free_addr = 0x000096E0`, `memcpy_addr = 0x002BD4F0`, `memset_addr = 0x001FA1B0`, `pmap_extract`, `pmap_protect`, funciones SBL y múltiples hooks. La igualdad de direcciones es evidencia de una tabla reutilizada o de una fuerte similitud de layout, no una prueba de igualdad de bytes.

## 4. 13.02 ↔ 13.04 ↔ 13.50

Las tablas locales contienen archivos para 13.02, 13.04, 13.50 y 13.52. El análisis de offsets 13.02/13.04 muestra igualdad de los campos extraídos. La presencia de `1350.c` y `1352.c` no aporta por sí sola un dump ni el código FFS. Para 13.50, se dispone de tablas de payload y artefactos parciales de `libkernel_sys`, pero no de una comparación de `ffs_mountfs()`.

Por ello, la diferencia observable actual es **de corpus y de tablas de offsets**, no de implementación FFS. No hay suficiente material para concluir si 13.50 cambió FFS, si parcheó Celsius o si simplemente cambió otros componentes del kernel.

## 5. ¿Qué artefactos permiten inferir código de `ffs_mountfs()`?

Ninguno de los artefactos Orbis 13.02/13.04 permite inferir directamente el código compilado de `ffs_mountfs()`. Sólo el código histórico de FreeBSD disponible en `research/webkit-1302/upstream/freebsd-9.1-ffs_vfsops.c` y los extractos de `ffs_mountfs()`/`ffs_reload()` documentan un patrón genérico con `fs_cssize`, `fs_contigsumsize`, `fs_ncg`, `fs_bsize`, `fs_fsize`, cálculos de `size`, reserva con `malloc` y un bucle posterior controlado por `fs_ncg`.

La referencia a `ffs_mountfs` en `webkit_gadgets_1304.js` es un comentario de análisis que dice que una string aparece en `0x7d021f` en dos kernels. El binario fuente que el comentario menciona —`1304_libSceNKWebKit.sprx.decrypted`— no está en el repositorio. Además, `libSceNKWebKit.sprx` es un módulo WebKit, no una prueba del kernel FFS. No hay bytes, hash ni script reproducible que valide la afirmación.

Estado: `SOURCE_ONLY` para la existencia de la string; `UNVERIFIED_13_02` para cualquier conclusión sobre `ffs_mountfs()`.

## 6. ¿Qué evidencia existe de Celsius?

La evidencia disponible es una cadena de afirmaciones:

| Fuente | Evidencia | Clasificación |
|---|---|---|
| X/Dr.Yenyen, 18 jul. 2026 | Nombre Celsius, atribución a bollars, `ffs_mount`, PS4 “up to 13.04”, con “in theory” | `SOURCE_ONLY` |
| `adri22235/ps4-suid-scanner` | Análisis secundario de `ffs_mountfs`, offsets 13.04 y atribución a Pharaoh2k | `SOURCE_ONLY` |
| PSDevWiki | Entrada de Celsius/FFS y rango tentativo | `SOURCE_ONLY` |
| `webkit_gadgets_1304.js` | Comentario “Celsius NOT patched” y “CONFIRMED” | `SOURCE_ONLY`; no reproducible |
| FreeBSD 9.1 | Código histórico FFS con cálculos relacionados | `VERIFIED` para FreeBSD, no Orbis |
| FreeBSD r309172 | Fix histórico de tamaños en FFS | `VERIFIED` para stable/11, no Orbis |
| PS4 13.02 kernel bytes | No localizados | `MISSING` |
| PS4 13.04 kernel bytes | No localizados | `MISSING` |
| PS4 13.50 kernel bytes/diff FFS | No localizados | `MISSING` |

Los offsets de 13.02/13.04 no contienen una función FFS ni demuestran que Celsius sea un exploit funcional. La afirmación “identical kernel” tampoco es evidencia de Celsius; como mucho, podría explicar por qué se reutilizó una tabla de offsets.

## 7. Clasificación de la equivalencia 13.02/13.04

La opción más defendible es **D para bytes y C/B para tablas**, no A:

| Opción | Evaluación |
|---|---|
| **A) bytes idénticos de kernel** | `DISPROVEN` como conclusión: no hay kernels para comparar; además, las tablas `.c` no son idénticas como archivos |
| **B) mismos offsets relevantes** | `CORROBORATED` para los offsets publicados en estas dos tablas |
| **C) mismo build/base con cambios menores** | `HYPOTHESIS`; compatible con offsets idénticos, no demostrada |
| **D) simple afirmación sin evidencia binaria** | `SOURCE_ONLY`; es el estado correcto respecto a la frase editorial |

En lenguaje operativo: **la evidencia confirma igualdad de las tablas conocidas, no igualdad de los kernels**. “Identical kernel” debe reescribirse en el repositorio como “las tablas de offsets publicadas para 13.02 y 13.04 coinciden en los campos comparados; no hay evidencia pública de igualdad byte a byte”.

## 8. Artefacto siguiente objetivo

El siguiente objetivo concreto es obtener, por una fuente pública y legítima, un par de artefactos comparables:

1. `kernel_orbis_13.02` retail o un dump/pseudocódigo equivalente, con versión, procedencia y SHA-256.
2. `kernel_orbis_13.04` equivalente, con versión, procedencia y SHA-256.
3. Idealmente, `kernel_orbis_13.50` para probar la hipótesis de parche.
4. Un mapa de símbolos o al menos referencias cruzadas de `ffs_mountfs()`/`ffs_reload()` y los campos del superbloque.

Si no aparece el kernel completo, un artefacto parcial suficiente sería un disassembly de la función con bytes y referencias a `fs_cssize`, `fs_contigsumsize`, `fs_ncg`, `fs_bsize`, `fs_fsize`, las sumas antes de `malloc` y el bucle posterior. Sin ese artefacto, Celsius no puede subir de `HYPOTHESIS / UNVERIFIED_13_02`.

## Respuestas finales

### 1. Todos los artefactos 13.02 encontrados

Se encontraron `kpayload` offsets 13.02, SLOPOS 13.02, tablas de Riyon/Vue, entradas de `ps4-linux-loader`, documentación local, headers 13.02 y copias en la rama de investigación. No se encontró kernel Orbis 13.02, dump retail, símbolo FFS ni pseudocódigo Orbis.

### 2. ¿Cuáles permiten inferir código de `ffs_mountfs()`?

Ninguno de forma directa. Sólo FreeBSD 9.1 permite estudiar el patrón histórico; los artefactos Orbis aportan offsets o comentarios.

### 3. ¿Qué evidencia existe de equivalencia 13.02/13.04?

Los archivos de offsets locales tienen hashes y tamaños distintos, pero los campos y valores parseados coinciden completamente. Esto es `CORROBORATED` para igualdad de offsets, no para igualdad de bytes.

### 4. ¿Qué evidencia existe de Celsius?

Hay una atribución pública, una descripción secundaria de `ffs_mountfs` y comentarios locales, todos sin kernel Orbis ni PoC reproducible. Estado: `SOURCE_ONLY / HYPOTHESIS / UNVERIFIED_13_02`.

### 5. ¿Qué diferencia observable hay entre 13.02, 13.04 y 13.50?

Entre 13.02 y 13.04, la diferencia observable de los artefactos disponibles está en los archivos y su procedencia, no en los valores de offsets: los campos comparados son iguales. Para 13.50 hay una tabla separada, pero no hay material FFS comparable. No puede afirmarse un cambio o parche de Celsius.

### 6. ¿Qué artefacto cierra la incertidumbre?

Un kernel Orbis retail 13.02 con hash y disassembly/pseudocódigo verificable de `ffs_mountfs()` y `ffs_reload()`, idealmente acompañado por el mismo material de 13.04 y 13.50. El mínimo decisivo sería un diff 13.02→13.50 de esa función que muestre si cambiaron tipos, cálculos, validaciones o bucles.

## Referencias

[1]: https://github.com/adri22235/ps4-suid-scanner "adri22235/ps4-suid-scanner"
[2]: https://github.com/Pharaoh2k "Perfil público de Pharaoh2k"
[3]: https://github.com/alferdoss/SLOPOS-offsets "SLOPOS offsets"
[4]: https://github.com/ps4-linux/ps4-linux-loader "ps4-linux-loader"
[5]: https://github.com/RiyonAbib07/ps-vue-jb-2.5 "RiyonAbib07/ps-vue-jb-2.5"
[6]: https://www.psdevwiki.com/ps4/Bugs "PSDevWiki Bugs"
[7]: https://www.psdevwiki.com/ps4/Vulnerabilities "PSDevWiki Vulnerabilities"
[8]: https://mail-archive.freebsd.org/cgi/mid.cgi?201611260043.uAQ0hcWs008737 "FreeBSD r309172"
[9]: https://nvd.nist.gov/vuln/detail/CVE-2006-5679 "NVD CVE-2006-5679"
[10]: https://x.com/calmboy2019/status/2078549759460094065 "Primera difusión pública localizada de Celsius"

> **Conclusión:** la afirmación “13.02 y 13.04 tienen kernel idéntico” no está demostrada como igualdad de bytes. La evidencia pública disponible sólo permite afirmar que dos tablas de offsets coinciden en los campos comparados, y que la frase editorial de `adri22235/ps4-suid-scanner` atribuye esa tabla a Pharaoh2k. No hay artefactos Orbis suficientes para identificar `ffs_mountfs()` ni para confirmar Celsius en 13.02.
