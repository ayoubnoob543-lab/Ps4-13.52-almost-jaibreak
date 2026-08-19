# Parámetros pendientes y criterios de promoción — PS4 13.52

## Propósito

Este documento evita que una tabla, un payload histórico o una inferencia documental se promocione automáticamente a un parámetro confirmado de firmware 13.52. Cada valor debe conservar procedencia, hash del artefacto que lo respalda y una ruta de validación.

| Parámetro o artefacto | Estado actual | Evidencia necesaria para `CONFIRMED` |
|---|---|---|
| `libSceNKWebKit.sprx` 13.52 | `MISSING` | Bytes legalmente aportados, SHA-256, formato SELF/SPRX y Build ID. |
| `libkernel_web.sprx` 13.52 | `MISSING` | Bytes de la misma imagen y relación de procedencia con WebKit. |
| `libSceLibcInternal.sprx` 13.52 | `MISSING` | Bytes de la misma imagen, hash y metadatos de build. |
| Identidad común de build WebKit/libkernel/libc | `MISSING` | Manifest o metadatos que vinculen los tres módulos. |
| GOT/import tables | `UNVERIFIED` | Relocations/imports analizados directamente desde esos módulos. |
| Vtables/estructuras WebKit | `UNVERIFIED` | Bytes de WebKit 13.52 y referencias cruzadas reproducibles. |
| Gadgets/firmas | `NOT_MIGRATED` | No se generan en este repositorio; cualquier análisis permitido debe ser descriptivo y no operativo. |
| Offsets WebKit 13.52 | `UNVERIFIED` | Módulo 13.52 con límites de sección, Build ID y XREFs verificables. |
| `SYSENT`, `pmap_protect` y `ALLPROC` | `STRUCTURAL/UNVERIFIED` | Kernel retail 13.52 y validación por prologue/callers/XREFs. |
| PUP 13.52 | `VERIFIED_METADATA` | El contenedor está verificado; la presencia de un PUP no implica módulos descifrados disponibles. |
| Toolchain retail-compatible | `MISSING` | SDK/ABI legal, versión de compiler/linker y librerías target. |
| WebKit OSS 13.00–13.04 | `STRUCTURAL` | Útil como base pública; no es fuente 13.52. |
| OpenOrbis toolchain | `RECOVERABLE` | Toolchain homebrew; no sustituye el SDK retail. |

## Reglas de procedencia

Un valor sólo puede pasar a `CONFIRMED` si el informe contiene el archivo de origen, su SHA-256, el commit/URL o procedencia local, el firmware declarado y una comprobación independiente que no dependa únicamente de la misma tabla fuente.

Los valores que aparezcan en una tabla de offsets, un README, un exploit histórico o un comentario se mantienen como `DOCUMENTED`, `STRUCTURAL` o `UNVERIFIED`. Nunca se rellenan mediante interpolación entre firmwares.

## Bloqueos actuales

La ausencia de los tres módulos WebKit 13.52 impide verificar identidad de build, GOT/imports, vtables, estructuras y offsets. La ausencia de un SDK/ABI retail impide afirmar que una build OSS enlazará como navegador Orbis. El proyecto puede continuar con análisis estático, pruebas de parsers y harnesses seguros, pero no con una afirmación de compatibilidad real 13.52.
