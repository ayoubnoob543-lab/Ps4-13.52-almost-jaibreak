# PS4 FW 13.02 — Estado público de Celsius/FFS

**Autor:** Manus AI  
**Alcance:** exclusivamente PS4 FW 13.02 y la ruta de disco/Celsius. Se excluyen 13.52 y Linux salvo referencias necesarias para 13.02. No se ejecutaron payloads ni se probó corrupción de memoria.

## Conclusión ejecutiva

La evidencia pública verificable permite afirmar que existen: (1) una descripción upstream de un integer overflow en `ffs_mountfs`/`ffs_reload`; (2) un repositorio público de investigación que contiene código BD-J, offsets y una descripción técnica de Celsius; (3) una afirmación pública de que Celsius cubriría 13.02–13.04; y (4) artefactos de entrada BD-J/escáner para 13.04 que pueden ser relevantes para una ruta de acceso a disco.

No permite afirmar que exista una cadena reproducible **PS4 13.02 → montaje UFS/FFS → corrupción controlada → kernel R/W**. En particular, no apareció un PoC original completo, una imagen UFS/FFS malformada asociada, un dump/disassembly Orbis 13.02 que identifique `ffs_mountfs`, ni el código de la primitive que convierte la corrupción en kernel R/W.

## Piezas reales disponibles

| Pieza | Evidencia pública | Qué contiene realmente | Estado |
|---|---|---|---|
| Bug upstream | FreeBSD commit `442f0608ec7e4b8ccb13f3101f294acbf0fce446` | Corrección de cálculos de tamaño en FFS; sirve para entender la clase de bug, no prueba que Orbis conserve los mismos bytes | **VERIFIED upstream** |
| Código/artefactos de `ps4-suid-scanner` | Repositorio público `adri22235/ps4-suid-scanner` | `1304.c`, `1304.h`, `scanner_1304.iso`, `hen.bin`, `jordy_stage2.js`, offsets parciales y documentación | **VERIFIED como repositorio**, no como PoC Celsius completo |
| Entrada BD-J 13.04 | `scanner_1304.iso` y `src/org/bdj/SuidScanner.java` según el README | Escáner SUID/SGID y uso de BD-J; aporta un entrypoint/infraestructura de investigación, no la primitive de kernel | **VERIFIED como infraestructura BD-J** |
| Offsets 13.04 | `1304.c`/`1304.h` y tabla atribuida a Pharaoh2k en el README | Offsets declarados para investigación; no son un dump del kernel ni localizan automáticamente FFS | **SOURCE_ONLY/CORROBORATED según entrada** |
| Offsets 13.02 | Material histórico de tablas y afirmación de equivalencia 13.02/13.04 | Permiten orientar análisis, pero no demuestran igualdad byte a byte ni relación con `ffs_mountfs` | **DERIVED/UNVERIFIED_13_02** |
| Parámetros UFS | `earthonion/mkufs2` | Generador UFS2 genérico (`newfs`), sin manipulación Celsius de `struct fs` | **VERIFIED genérico; no Celsius** |
| Herramientas PFS/LVD | `MkPFS`, `MicroMount`, ShadowMount/SonicLoader | Infraestructura PFS/PFSC/LVD, no imagen UFS/FFS malformada de Celsius | **VERIFIED no relacionada directamente** |

## Qué afirma exactamente la fuente secundaria principal

El README público de `adri22235/ps4-suid-scanner` afirma que Celsius (`ffs_mount`) funciona hasta 13.04, que fue parcheado en 13.50 y que requiere un entrypoint BD-J/Vue y un HDD de 250 GB o más. El mismo README muestra la categoría “13.04 complete” y dice que los offsets están “based on 13.02 (identical kernel)”.

Estas frases son evidencia de lo que el repositorio afirma, pero el repositorio no adjunta el dump de kernel, la imagen UFS, el hash de una build Orbis ni el código completo de la primitive. Por ello se clasifican como **SOURCE_ONLY**, no como verificación independiente.

## Mecanismo FFS que sí puede reconstruirse documentalmente

El código upstream describe una ruta en la que valores del superbloque alimentan cálculos de tamaño para estructuras auxiliares. La corrección histórica sirve para identificar los campos y operaciones relevantes: `fs_cssize`, `fs_contigsumsize`, `fs_ncg`, `fs_bsize` y `fs_fsize`, además de sumas/multiplicaciones previas a una reserva de memoria y bucles posteriores que consumen el tamaño calculado.

Esto demuestra la plausibilidad de una clase de overflow en FFS upstream. No demuestra que la implementación Orbis 13.02 sea idéntica, que el dispositivo sea accesible desde el contexto requerido, ni que la corrupción sea controlable en el kernel retail.

## Ruta 13.02 evaluada

| Etapa | Estado para 13.02 | Evidencia que falta |
|---|---|---|
| Entry point de userland/BD-J/Vue | Hay infraestructura y claims, pero no una cadena 13.02 completa demostrada | PoC reproducible y artefacto de entrada específicamente 13.02 |
| Acceso al disco/dispositivo | El requisito de HDD de 250 GB+ aparece en documentación secundaria | Código que muestre cómo se selecciona y presenta el dispositivo al montador |
| Imagen UFS/FFS | No se encontró una imagen Celsius ni script que escriba los valores exactos del superbloque | Archivo de imagen, hash y script de generación asociados al autor original |
| Correspondencia Orbis `ffs_mountfs` | Sólo existe la referencia al código upstream y afirmaciones del repositorio | Dump/disassembly/pseudocódigo Orbis 13.02 con referencias cruzadas |
| Corrupción controlada | Descrita conceptualmente, no demostrada en Orbis 13.02 | PoC completo y evidencia de resultado controlado |
| Primitive kernel R/W | No encontrada públicamente | Código/artefacto que convierta el efecto de FFS en lectura/escritura arbitraria |
| HEN/jailbreak completo | No hay cadena pública reproducible para 13.02 | Demo técnica reproducible con logs y artefactos verificables |

## Evidencia de una cadena hasta kernel R/W

No existe en el corpus público revisado una cadena documentada y verificable que llegue desde un entrypoint de 13.02 hasta kernel R/W mediante Celsius. La existencia de offsets, un escáner BD-J, un generador UFS genérico o una descripción upstream no sustituye el PoC faltante.

La clasificación correcta de Celsius para 13.02 es **candidato respaldado documentalmente, pero ruta no reproducible públicamente**. El claim “hasta 13.04” incluye 13.02 por rango textual, pero no constituye una demostración independiente en hardware 13.02.

## Artefacto decisivo que falta

El artefacto más informativo sería un paquete original o espejo histórico que contenga simultáneamente:

1. la imagen UFS/FFS malformada o el script exacto que la genera;
2. el bootstrap/entrypoint que provoca el montaje en el contexto PS4;
3. logs o vídeo técnico con firmware 13.02;
4. y el código o pseudocódigo de la primitive posterior a la corrupción.

En ausencia de ese paquete, un dump legítimo y verificable del kernel Orbis 13.02 con disassembly de `ffs_mountfs` sería el segundo objetivo más valioso.

## Referencias

[1]: https://github.com/adri22235/ps4-suid-scanner "adri22235/ps4-suid-scanner"
[2]: https://github.com/freebsd/freebsd-src/commit/442f0608ec7e4b8ccb13f3101f294acbf0fce446 "FreeBSD commit 442f0608"
[3]: https://consolemods.org/wiki/PS4:Exploit_Chart "ConsoleMods PS4 Exploit Chart"
[4]: https://github.com/earthonion/mkufs2 "earthonion/mkufs2"
[5]: https://github.com/PSBrew/MkPFS "PSBrew/MkPFS"
[6]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer Wiki — Vulnerabilities"
