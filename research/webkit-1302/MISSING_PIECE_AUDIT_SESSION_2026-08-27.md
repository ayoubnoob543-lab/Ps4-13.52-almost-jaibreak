# Auditoría de la pieza faltante para PS4 FW 13.02

**Fecha:** 2026-08-27  
**Ámbito:** investigación pública y análisis estático exclusivamente. No se ejecutaron payloads, exploits ni corrupción de memoria en hardware.  
**Rama:** `research/webkit-disk-1302`

## Conclusión ejecutiva

La pieza concreta que falta para cerrar la ruta PS4 13.02 no es otro offset aislado. Es un **artefacto de transición verificable** que conecte una primitive de entrada con la vulnerabilidad FFS y demuestre una primitive de kernel R/W. En términos documentales, debe contener al menos una de estas formas de evidencia: bytes/disassembly de Orbis 13.02 o 13.04 que permitan identificar la ruta `mount → UFS/FFS → ffs_mountfs`; un bootstrap Jordy/WebKit completo con bases, `dlsym`, pivot y fcall; o un log reproducible de hardware que pruebe la corrupción y la conversión a kernel R/W.

La investigación no encontró ese artefacto. Los resultados nuevos refuerzan, pero no cambian, el veredicto anterior: **Celsius permanece en `SOURCE_ONLY`/`UNVERIFIED_13_02`; `patch_mount` permanece en `DERIVED` con relación a FFS sólo como `HYPOTHESIS`; Netctrl/ucred tiene una implementación histórica real, pero no una demostración pública para 13.02**.

## Hallazgos nuevos

### 1. El commit `702fcc3` sólo contiene afirmaciones, no el supuesto SPRX

La consulta directa de la API de GitHub para [`702fcc397d45546baab5311bc0a264870ae90042`][1] muestra que el commit añade exactamente un archivo, `webkit_gadgets_1304.js`. El archivo afirma que sus gadgets proceden de `1304_libSceNKWebKit.sprx.decrypted (68 MB) from zecoxao` y afirma que `ffs_mountfs` aparece en `0x7d021f` en kernels 13.00 y 13.04.

El commit no contiene URL de descarga, hash del SPRX, binario, bytes circundantes, disassembly, límites de función, referencias cruzadas ni log de prueba. Por tanto, la existencia del texto es **VERIFIED**, pero el SPRX y la comparación de kernels son **SOURCE_ONLY**. La presencia de Celsius en Orbis 13.02/13.04 sigue siendo **UNVERIFIED**.

### 2. El repositorio público de zecoxao no aporta una copia independiente

La revisión del árbol y del historial textual de [`zecoxao/zecoxao.github.io`][2] no encontró `1304_libSceNKWebKit`, `ffs_mountfs`, `midohar36` ni una copia identificable del supuesto dump. Las coincidencias de “Celsius” pertenecen a commits genéricos de herramientas, tests o material de desarrollo, no a un kernel PS4 13.04.

Esto no demuestra que el archivo nunca existiera fuera del repositorio; sí demuestra que no está disponible como fuente primaria en el repositorio público auditado. La afirmación “from zecoxao” no puede tratarse como corroboración independiente.

### 3. No existen refs públicas adicionales con una versión completa de stage 2

El clon completo de [`adri22235/ps4-suid-scanner`][3], con ramas remotas y tags, expone `main`, `origin/main`, `origin/HEAD` y `v2.0`. Los únicos archivos de stage 2 son `stage2_jordy.js`, añadido en `96a7948`, y `jordy_stage2.js`, añadido en `1089382` como reemplazo.

No aparecen en otras refs archivos que completen `targetAddress`, la base WebKit, la base libkernel, `dlsym`, el pivot, la llamada UFS/FFS o la primitive kernel R/W. La ausencia sólo está demostrada para las refs públicas de ese repositorio; copias privadas o no indexadas siguen siendo desconocidas.

### 4. El tag `v2.0` repite Celsius, pero no aporta prueba técnica

El README y `cve_analysis.md` del tag `v2.0` presentan Celsius como “CONFIRMED”, lo atribuyen a bollars, indican alcance hasta 13.04 y parche en 13.50, y reproducen aritmética basada en `fs_ncg`, `fs_cssize` y `fs_contigsumsize`. Sin embargo, otra sección del mismo material sólo declara un crash confirmado en FW 11.00 y describe 13.04 como probable.

El tag no contiene kernel Orbis, SPRX, hash, diff binario, log de 13.02/13.04 ni PoC verificable. Sus afirmaciones son **SOURCE_ONLY** y **UNVERIFIED_13_02**.

### 5. `scanner_1304.iso` y `hen.bin` no son la pieza faltante

`scanner_1304.iso` fue añadido el 18 de julio de 2026 por Adrián García Casado como blob de 16 MiB, sin URL, hash o metadatos de importación. Su inspección estática lo identifica como UDF 1.5 y no revela código de stage 2, SPRX, kernel, UFS malformado o Celsius.

`hen.bin` fue añadido el 30 de julio de 2026 por el mismo autor. Mide 500736 bytes y tiene SHA-256 `f29bd1f0ac5cc1edef6ebccb735ef6c4dff702711cc3b9f465e66fd03dd707ce`. No es ELF; contiene código x86-64 y strings de HEN/kpayload, `sceKernelDlsym`, opciones de jailbreak, FTP y bloqueo de actualizaciones. No contiene una implementación identificable de `ffs_mountfs`, una imagen de kernel o el stage 2 de Celsius.

### 6. `patch_mount` no está identificado como `ffs_mountfs`

La tabla de Fusion contiene:

| Símbolo etiquetado | Offset relativo |
|---|---:|
| `patch_mount` | `0x001512A7` |
| `M_MOUNT` | `0x01A40250` |
| `getnewvnode` | `0x0036E2F0` |
| `vn_fullpath` | `0x00308CE0` |
| `kern_open` | `0x003435E0` |
| `malloc` | `0x00009520` |
| `free` | `0x000096E0` |
| `kmem_alloc` | `0x00465A50` |
| `kmem_free` | `0x00465C20` |

La inspección de las fuentes `kpayload` 13.02/13.04 no encuentra el nombre `patch_mount` ni una entrada `ffs_mountfs`; sus coincidencias de montaje se refieren a PFS/Shell y a `enable_data_mount_patch`. Las tablas 13.02/13.04 comparten varios offsets de esa familia, pero no aportan semántica de FFS.

No existe una descripción de operación, bytes objetivo, call site, símbolo, referencia cruzada o disassembly para `0x001512A7`. Por ello, **no es legítimo afirmar `patch_mount = ffs_mountfs`**. La relación sigue siendo una hipótesis de nomenclatura/contexto.

### 7. El único código FFS vulnerable localizado es FreeBSD histórico

La búsqueda de archivos fuente no documentales encuentra la aritmética vulnerable únicamente en la copia histórica [`freebsd-9.1-ffs_vfsops.c`][4]. También aparecen comentarios de Celsius en los scripts del scanner y código `makefs/ffs.c` para construir imágenes, pero no una implementación Orbis.

El código FreeBSD histórico demuestra que el patrón técnico es plausible en una base FreeBSD antigua. No demuestra que Orbis 13.02 conserve los mismos tipos, validaciones, orden de cálculos, bucles o layout de `struct fs`.

### 8. Las búsquedas externas siguen siendo secundarias

Las búsquedas refinadas devolvieron vídeos y discusiones que repiten que Celsius podría afectar 13.02/13.04, además de una tabla de ConsoleMods que indica que no existe un kernel exploit público para esos firmwares recientes. No apareció ningún nuevo byte, hash, pseudocódigo, commit primario, prueba de hardware ni referencia cruzada de `patch_mount`.

Estas fuentes tienen valor como registro del rumor y del estado público, pero no como prueba técnica independiente. La tabla de ConsoleMods es corroboración de la **ausencia de una ruta pública reproducible**, no prueba de que Celsius haya sido parcheado.

## Comparación de candidatos

| Candidato | Qué existe públicamente | Qué falta para 13.02 | Clasificación actual |
|---|---|---|---|
| Celsius / `ffs_mountfs` | Código FreeBSD histórico, claims del scanner y documentación derivada | Bytes/pseudocódigo Orbis, trigger, imagen UFS, primitive y prueba | **SOURCE_ONLY / UNVERIFIED_13_02** |
| `patch_mount` | Etiqueta y offset en Fusion/OSM | Semántica, bytes objetivo y cross-reference a VFS/FFS | **DERIVED / HYPOTHESIS** |
| Netctrl/ucred | Código PS4 histórico con kernel R/W hasta generaciones antiguas | Adaptación 13.02, offsets funcionales y prueba posterior a 13.00 | **VERIFIED histórico / UNVERIFIED_13_02** |
| Lapse/semctl | Código histórico y tablas antiguas | Alcance 13.02 y prueba de supervivencia | **VERIFIED histórico / UNVERIFIED_13_02** |
| `jordy_stage2.js` | Helpers y arquitectura propuesta | Primitive de entrada, bases, pivot, fcall y kernel R/W | **VERIFIED / INCOMPLETE** |
| SPRX zecoxao 13.04 | Sólo claim textual de procedencia | Archivo, hash, bytes y análisis reproducible | **SOURCE_ONLY** |
| `scanner_1304.iso` | Blob UDF de 16 MiB | Contenido de explotación verificable | **INVALID como prueba Celsius** |
| `hen.bin` | Binario HEN/kpayload con hash | Relación con Celsius/13.02 | **INVALID como pieza faltante** |

## La pieza decisiva, definida concretamente

La pieza mínima que cerraría la incertidumbre de **existencia** de Celsius en Orbis 13.02 sería un dump legítimo del kernel Orbis 13.02 —o un binario equivalente— con suficiente contexto para identificar la implementación de `ffs_mountfs` y comparar:

1. la lectura de `fs_cssize`, `fs_contigsumsize` y `fs_ncg`;
2. los tipos y promociones usados en las multiplicaciones y sumas;
3. la llamada a `malloc` y el tamaño calculado;
4. el bucle posterior que consume `fs_ncg`;
5. las validaciones de `fs_bsize`, `fs_fsize` y del superbloque;
6. cualquier diferencia frente a 13.50.

La pieza mínima que cerraría la **explotabilidad** de la ruta sería adicionalmente un artefacto que demostrara la transición desde userland hasta la corrupción controlable y luego a kernel R/W: bootstrap Jordy completo, argumentos de montaje, imagen UFS, grooming/objetivo y resultado observable. Un string `ffs_mountfs`, una tabla de offsets o `patch_mount` por sí solos no son suficientes.

## Veredicto

La evidencia nueva no convierte Celsius en un exploit PS4 13.02 respaldado. La mejor clasificación continua es:

> **Celsius:** candidato técnico plausible basado en FreeBSD y en claims de terceros, pero `SOURCE_ONLY`/`UNVERIFIED_13_02` para Orbis.

> **`patch_mount`:** offset derivado de Fusion/OSM, sin relación demostrada con `ffs_mountfs`; clasificación `DERIVED/HYPOTHESIS`.

> **Netctrl/ucred:** primitive PS4 histórica real, pero sin evidencia pública de supervivencia o prueba en 13.02.

> **Ruta completa 13.02:** no reproducible con los artefactos públicos localizados.

La próxima adquisición más informativa sería, en orden: un binario legítimo Orbis 13.02/13.04 con bytes de kernel; el SPRX 13.04 atribuido a zecoxao con hash y contexto; una copia del bootstrap Jordy que contenga `targetAddress`, bases y pivot; o un registro técnico de hardware que demuestre el montaje y la primitive de kernel R/W. La investigación debe mantener separadas esas piezas: obtener una no implica automáticamente obtener las demás.

## Referencias

[1]: https://github.com/adri22235/ps4-suid-scanner/commit/702fcc397d45546baab5311bc0a264870ae90042 — Commit `702fcc3`, gadgets WebKit 13.04.
[2]: https://github.com/zecoxao/zecoxao.github.io — Repositorio público de zecoxao auditado.
[3]: https://github.com/adri22235/ps4-suid-scanner — Repositorio e historial del scanner.
[4]: https://github.com/freebsd/freebsd-src/blob/release/9.1.0/sys/ufs/ffs/ffs_vfsops.c — Referencia histórica FreeBSD de `ffs_vfsops.c`.
[5]: https://github.com/ps4-payload-dev/sdk/releases — Releases públicas del SDK con tablas de offsets, sin prueba de Celsius.
[6]: https://consolemods.org/wiki/PS4:Exploit_Chart — Tabla pública del estado de exploits.

## Archivos de soporte en este branch

Los logs y copias forenses asociados se encuentran bajo `research/webkit-1302/upstream/`, especialmente en `adri-suid-history/full-stage2/followup/`, `osm-provenance/` y `artifact-inspection/`. Los commits de esta continuación incluyen `017e725`, `7e26c65`, `d2a9b4b`, `bf3d9c7`, `b172394`, `6412de9`, `ea80ceb`, `44c3f91`, `a6b5d59`, `4958666`, `ea558ae`, `a173371` y `08055fe`.
