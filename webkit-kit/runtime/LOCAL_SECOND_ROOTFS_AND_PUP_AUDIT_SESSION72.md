# Auditoría local del segundo rootfs y metadata PUP — sesión 72

## Alcance y seguridad

Se inspeccionó localmente `/home/ubuntu` de forma recursiva, excluyendo explícitamente los árboles conocidos de WPE en `/home/ubuntu/wpe-artifacts-2526/arch/rootfs` y `/home/ubuntu/wpe-artifacts-2526/db-extract`. La inspección fue sólo de lectura: no se ejecutaron binarios, PUPs, payloads, JARs, ELF/SELF ni herramientas de descifrado.

## Localización

No apareció un segundo rootfs PS4 identificable. Los nombres que parecían candidatos fueron principalmente documentación, stubs del laboratorio (`orbis_webkit_stub.[ch]`), scripts de auditoría y bibliotecas WPE/Linux. Los archivos grandes adicionales fueron PUPs y bundles WPE:

| Ruta | Tamaño | Interpretación |
|---|---:|---|
| `/home/ubuntu/upload/PS4UPDATE1.PUP` | 326,026,951 | Contenedor PUP 13.52 ya conocido |
| `/home/ubuntu/ps4-1352-pup-audit-session42/pup1_attachment/original/PS4UPDATE1.PUP` | 326,026,951 | Duplicado byte a byte del anterior |
| `/home/ubuntu/ps4-1352-pup-audit-session42/original/PS4SYS_CRC[DC9D6197]_PS4UPDATE.PUP` | 503,310,848 | Contenedor PUP estructurado, etiquetado en el corpus como candidato 13.52 |
| `/home/ubuntu/ps4-1352-pup-audit-session42/pup1350/original/PS4SYS_CRC[6E6D1610]_PS4UPDATE.PUP` | 503,293,952 | Contenedor PUP estructurado, etiquetado en el corpus como candidato 13.50 |
| `/home/ubuntu/wpe-artifacts-2526/root/usr/lib/libWPEWebKit-2.0.so.1.9.10` | 133,528,480 | WPE/Linux, no PS4 |
| `/home/ubuntu/wpe-bundles/wpe-minibrowser-2.53.1/extracted/lib/libWPEWebKit-2.0.so.1.10.0` | 150,623,704 | WPE/Linux, no PS4 |

El manifiesto detallado de búsqueda está en `LOCAL_SECOND_ROOTFS_CANDIDATES_SESSION72.txt`, SHA-256 `c800a0f956311703273ca9156097d8da53fb1f9b67b9e54c4a7bd4ba026fcd99` antes de esta ampliación.

## Identidad y hashes

| Archivo | SHA-256 |
|---|---|
| `/home/ubuntu/upload/PS4UPDATE1.PUP` | `fd5e6c16398e628b3f258bce5f395c9fda687011a1a985d4b507928f54e6b580` |
| Duplicado `pup1_attachment/original/PS4UPDATE1.PUP` | `fd5e6c16398e628b3f258bce5f395c9fda687011a1a985d4b507928f54e6b580` |
| `PS4SYS_CRC[DC9D6197]_PS4UPDATE.PUP` | `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11` |
| `PS4SYS_CRC[6E6D1610]_PS4UPDATE.PUP` | `04585405bf3ad0836103c1eea5c21657327a377824ad5cda7674ecb94f03822f` |

`PS4UPDATE1.PUP` aparece como `data` en `file` y comienza con bytes no identificados como ELF/SELF. Los dos contenedores `PS4SYS_CRC[...]` comienzan con `SLB2` y contienen literalmente `PS4UPDATE1.PUP` y `PS4UPDATE2.PUP` en su cabecera. Esto confirma formato de contenedor y consistencia superficial, no el contenido descifrado de módulos.

## Diferencial estático de cabecera 13.50/13.52

Tomando como A el archivo etiquetado `PS4SYS_CRC[6E6D1610]` (13.50) y como B el etiquetado `PS4SYS_CRC[DC9D6197]` (13.52), los primeros 4 KiB no son idénticos. Los primeros offsets distintos reportados por `cmp -l` son 17, 37–38, 81, 85–87 y 513–537. Las palabras little-endian iniciales muestran, entre otros cambios:

| Campo relativo | 13.50 | 13.52 | Significado seguro |
|---:|---:|---:|---|
| palabra en offset 0x10 | `982996` | `983029` | metadata del contenedor; semántica interna no resuelta |
| palabra en offset 0x28 | `326026471` | `326026951` | relacionado con el tamaño de `PS4UPDATE1.PUP` observado |
| bytes en 0x50–0x57 | `65 b7 09 00 f7 dd 90 0a` | `66 b7 09 00 3f 1d 91 0a` | campos de cabecera; no se atribuyen a WebKit |
| bloque alrededor de 0x200 | distinto | distinto | metadata/hash/descriptor del contenedor; no interpretado |

La cabecera B refleja `326026951`, que coincide con el tamaño de `PS4UPDATE1.PUP` 13.52. La diferencia de cabecera demuestra que los contenedores locales no son copias idénticas; no demuestra qué módulos internos cambiaron, porque los bytes relevantes pueden estar comprimidos/cifrados y no se ha realizado descifrado.

## Búsqueda de WebKit/JSC y segundo rootfs

La búsqueda de nombres `libSceNKWebKit`, `libkernel_web`, `JavaScriptCore`, `WebCore`, `CSSFontFace`, `MarkedVector`, `CloneSerializer`, `JSCell`, `system_ex`, `app0`, `SELF` y `eboot.bin` no localizó un módulo Sony/Orbis autónomo fuera de los PUP y de los informes del laboratorio. Los únicos `orbis` encontrados son stubs de interfaz creados para el laboratorio. No se observó un filesystem montado o symlink que expusiera un rootfs PS4 separado.

## Tres familias congeladas

No se encontraron bytes, símbolos ni fuentes retail nuevos que permitan ejecutar de manera significativa `correlate_three_families.py` contra PS4 13.52. En el BIN de `libkernel_sys` ya identificado, la búsqueda de strings no encontró `WebKit`, `JavaScriptCore`, `CSSFontFace`, `WebCore`, `MarkedVector`, `CloneSerializer` ni `libSceNKWebKit`; sí encontró marcadores coherentes con libkernel/Orbis. Por tanto, ese BIN no resuelve ninguna de las tres familias.

Los artefactos WPE/Linux quedan descartados como evidencia PS4 aunque contengan implementaciones upstream de WebKit: no existe una base demostrada para asumir equivalencia con el layout retail de PS4 13.52.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| Existencia local de contenedores PUP 13.50/13.52 etiquetados | `DIRECT_DOCUMENTED` para identidad local del archivo; procedencia del firmware según corpus |
| Coincidencia SHA-256 de los dos `PS4UPDATE1.PUP` | `DIRECT_13.52` para identidad del contenedor exterior ya verificado |
| Diferencias estructurales en cabeceras `SLB2` | `INDIRECT_13.52`; son diferencias del contenedor, no de WebKit |
| Segundo rootfs PS4 extraído | `UNVERIFIED` / no encontrado |
| `libSceNKWebKit.sprx` 13.52 | `UNVERIFIED`; no aparece localmente |
| WPE 2.52/2.53 como sustituto del WebKit retail | `DISCARDED` |
| Correlación 13.52 de MarkedVector/CloneDeserializer/CSSFontFace | `UNVERIFIED` |

## Conclusión y siguiente paso de mayor valor

El entorno local contiene los contenedores PUP y un BIN de `libkernel_sys` consistente, pero no contiene un segundo rootfs PS4 ni `libSceNKWebKit.sprx`/`libkernel_web.sprx` extraídos. El diferencial de cabecera permite confirmar que los PUP candidatos no son idénticos y ofrece metadata para una futura tabla de contenedores, pero no permite recuperar ni atribuir funciones WebKit/JSC.

El siguiente paso de mayor valor es obtener legítimamente un módulo WebKit/JSC PS4 o una tabla/manifest descifrado con procedencia verificable. Hasta entonces, sólo pueden prepararse comparadores y clasificar las tres familias como `UNVERIFIED`; no puede afirmarse presencia, ausencia, primitive de memoria ni ejecución nativa en 13.52.

## Evidencia local

- `LOCAL_SECOND_ROOTFS_CANDIDATES_SESSION72.txt`, SHA-256 inicial `c800a0f956311703273ca9156097d8da53fb1f9b67b9e54c4a7bd4ba026fcd99`.
- `LOCAL_PUP_METADATA_SESSION72.txt`, SHA-256 tras la diferencial de cabecera `910f6c26acf6e8b4c57f7d1aacb0c1c4fb0db9227e6879c90dc892baa7db579e`.
- `PS4_IPV6_UAF_670_702_STATIC_REVIEW_SESSION72.md`, SHA-256 `b864f722dfd96b9e43953e08dbd8d1aae1cdf2de6050449356b68e3c54c1cc10`.
