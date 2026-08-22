# Revisión estática de `PS4-BAR-dump` — sesión 71

## Fuente

- Repositorio: `DEBARSHI-SARKAR/PS4-BAR-dump`
- URL: https://github.com/DEBARSHI-SARKAR/PS4-BAR-dump
- Rama por defecto declarada: `deb`
- Commit/ref consultado: página pública del repositorio; no se descargaron archivos.
- Descripción: dumps de memoria y registros de hardware PS4.

## Contenido observado

El repositorio contiene `DDR3.pdf`, `aeolia_dump.pdf`, `bar4_dump.pdf` y `README.md`. El README describe mapas PCI/BAR, regiones MMIO, registros Belize DDR3 y arquitectura de memoria física. Los documentos se presentan como evidencia de hardware y registros, no como firmware, módulos ELF/SELF ni dumps de procesos.

## Relevancia para WebKit/JSC

No aparecen `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `JavaScriptCore`, `WebCore`, `CSSFontFace`, `MarkedVector`, `CloneDeserializer` ni símbolos de WebKit. Tampoco se observa una ruta hacia el runtime del navegador, BD-J o el contenido de `NPXS20113`. Los valores BAR/MMIO no sirven para reconstruir imports/exports ni estructuras C++ de WebKit.

El repositorio puede ser útil como referencia independiente de arquitectura física y hardware PS4, pero no aporta bytes retail de WebKit ni permite clasificar una vulnerabilidad JSC. No se debe mezclar con el dump local de `libkernel_sys` ni tratar una dirección MMIO como una dirección de módulo o de proceso.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| Existencia pública del repositorio y sus PDFs de hardware | `DIRECT_HISTORICAL` |
| Evidencia de mapas PCI/BAR y registros descritos por el README | `DOCUMENTED_ONLY` hasta validar los PDFs originales |
| Evidencia de `libSceNKWebKit` o `libkernel_web` | `DISCARDED` |
| Evidencia de PS4 13.52 | `UNVERIFIED`; no hay firmware ni versión de sistema en el contenido revisado |
| Utilidad para correlación WebKit/JSC | Baja; sólo contexto de hardware |

## Conclusión

`PS4-BAR-dump` no resuelve el bloqueo actual. Es un repositorio de hardware/MMIO, no un repositorio de WebKit ni un dump de runtime. No contiene un artefacto que permita analizar imports, exports, Build ID o estructuras de `libSceNKWebKit.sprx`.
