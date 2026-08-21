# Búsqueda de estructura interna de segundo nivel — PS4 13.50/13.52

**Fecha de análisis:** 2026-08-21
**Alcance:** análisis local, estático y de sólo lectura. No se descifró, ejecutó, extrajo ni modificó contenido de firmware.

## Objetivo

Comprobar si las imágenes `PS4SYS` completas contienen una segunda cabecera, índice o mapa interno que permita relacionar offsets con módulos como WebKit/JSC sin asumir nombres ni descifrar contenido.

## Artefactos analizados

| Firmware | Ruta | Tamaño | SHA-256 |
|---|---|---:|---|
| 13.50 | `/home/ubuntu/ps4-1352-pup-audit-session42/pup1350/original/PS4SYS_CRC[6E6D1610]_PS4UPDATE.PUP` | 503293952 | `04585405bf3ad0836103c1eea5c21657327a377824ad5cda7674ecb94f03822f` |
| 13.52 | `/home/ubuntu/ps4-1352-pup-audit-session42/original/PS4SYS_CRC[DC9D6197]_PS4UPDATE.PUP` | 503310848 | `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11` |

El parser SLB2 local identifica dos entradas en ambas imágenes:

| Entrada | Offset 13.50 | Tamaño 13.50 | Offset 13.52 | Tamaño 13.52 |
|---|---:|---:|---:|---:|
| `PS4UPDATE1.PUP` | 1024 | 326026471 | 1024 | 326026951 |
| `PS4UPDATE2.PUP` | 326027776 | 177266167 | 326028288 | 177282367 |

## Escaneo de segundo nivel

La nueva herramienta `webkit-kit/tools/scan_second_level_structure.py` buscó la cabecera interna observada en ambas entradas:

```text
4f 15 3d 1d 00 01 01 12
```

Resultados:

| Imagen | Apariciones de la cabecera |
|---|---|
| 13.50 | offset `1024` y offset `326027776` |
| 13.52 | offset `1024` y offset `326028288` |

Las dos apariciones corresponden exactamente al comienzo de `PS4UPDATE1.PUP` y `PS4UPDATE2.PUP`. No se encontraron apariciones adicionales de esa cabecera dentro de los payloads. Esto no revela un índice o subcontenedor adicional del mismo formato.

## Firmas conservadoras

En ambas imágenes sólo se validó `SLB2` en offset `0`. No se encontró `SELF`, `ELF` ni `SCEUF` como firma válida. En 13.52 apareció una coincidencia aislada de `\x7fPKG` en offset `84844490`; no se considera un módulo porque no se validó una cabecera PKG completa ni una estructura coherente alrededor de ella. Las coincidencias ASCII `PKG` y `SCE` se comportan como patrones aislados en datos de alta entropía.

No aparecieron literales de:

```text
libSceNKWebKit
libkernel_web
JavaScriptCore
WebKit
CSSFontFace
MarkedVector
CloneDeserializer
CloneSerializer
```

La ausencia de literales no prueba que esos componentes no estén presentes; sólo demuestra que no son visibles como texto plano en estos blobs.

## Interpretación

La búsqueda no descubrió una tabla de nombres, índice de módulos ni subcontenedor reconocible que permita convertir un offset bruto en `libSceNKWebKit.sprx` o JavaScriptCore. Las entradas internas siguen siendo blobs opacos después de su cabecera de 16 bytes. El análisis previo midió una entropía aproximada de 7.9998 bits/byte en ventanas de 1 MiB y una diferencia alineada del 96.8718% para UPDATE1 y 99.4179% para UPDATE2 entre 13.50 y 13.52.

Por tanto, los PUP completos contienen los bytes y sus límites están identificados, pero no existe en la capa examinada una relación verificable entre las regiones y los módulos WebKit/JSC.

## Clasificación de resultados

| Hallazgo | Clasificación |
|---|---|
| Las dos imágenes completas son contenedores SLB2 válidos con dos entradas | `DIRECT_13.50` / `DIRECT_13.52` |
| La cabecera interna aparece sólo al inicio de cada entrada | `DIRECT_13.50` / `DIRECT_13.52` |
| No hay cabeceras SELF/ELF/SCEUF visibles en la capa analizada | `DIRECT_13.50` / `DIRECT_13.52` |
| La coincidencia `PKG` aislada representa un módulo | `DISCARDED` |
| Los blobs contienen código WebKit/JSC | `UNVERIFIED` |
| Una región concreta corresponde a `CSSFontFace`, `MarkedVector` o `CloneDeserializer` | `UNVERIFIED` |

## Conclusión

La adquisición de bytes deja de ser el bloqueo: tenemos las dos imágenes completas y hemos identificado sus dos entradas internas. El bloqueo restante es de **interpretación de la capa interna**. El escaneo no encontró un mapa de módulos ni una segunda estructura reconocible; por ello todavía no es legítimo asignar los cambios a WebKit/JSC mediante offsets brutos.

El siguiente dato de mayor valor sería una metadata/índice interno legítimo o una extracción decodificada de una entrada concreta. Hasta entonces, la afirmación correcta es: **bytes PUP completos disponibles; WebKit retail todavía no identificado como módulo analizable**.

## Reproducibilidad

```bash
cd /home/ubuntu/firmware-lab-runtime
python3 -m py_compile webkit-kit/tools/scan_second_level_structure.py
python3 webkit-kit/tools/scan_second_level_structure.py \
  /home/ubuntu/ps4-1352-pup-audit-session42/pup1350/original/PS4SYS_CRC\[6E6D1610\]_PS4UPDATE.PUP \
  /home/ubuntu/ps4-1352-pup-audit-session42/original/PS4SYS_CRC\[DC9D6197\]_PS4UPDATE.PUP \
  --output second_level_scan.json
```

El script es conservador: no descifra, no extrae, no ejecuta y no asigna procedencia de módulo a ninguna coincidencia.
