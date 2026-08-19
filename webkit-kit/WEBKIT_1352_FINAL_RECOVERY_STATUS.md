# Estado final de recuperación WebKit PS4 13.52

## Alcance

Se realizó una búsqueda dirigida de `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, Build IDs, GOT/imports, vtables, estructuras, offsets y toolchains asociados a una misma build 13.52. Se revisaron el corpus local, los manifests del proyecto, los repositorios públicos ya auditados y documentación pública del PS4 Developer Wiki.

## Resultado

| Elemento | Estado | Conclusión |
|---|---|---|
| `libSceNKWebKit.sprx` 13.52 | `MISSING` | No hay bytes verificables ni hash de una build 13.52. |
| `libkernel_web.sprx` 13.52 | `MISSING` | No hay bytes verificables ni relación de procedencia con WebKit. |
| `libSceLibcInternal.sprx` 13.52 | `MISSING` | No hay bytes verificables ni Build ID común. |
| Identidad/Build ID común | `MISSING` | Las tablas y páginas públicas no vinculan los tres módulos a una misma imagen. |
| GOT/imports reales | `MISSING` | No pueden calcularse de forma específica sin los módulos target. |
| Vtables/estructuras WebKit | `UNVERIFIED` | Las referencias históricas son estructurales y de otras versiones. |
| Offsets WebKit 13.52 | `UNVERIFIED` | No se promociona ningún offset sin bytes target y XREFs reproducibles. |
| Toolchain/ABI retail | `MISSING` | OpenOrbis es una base homebrew; no sustituye SDK/ABI retail de Sony. |
| Prueba real en PS4 13.52 | `NOT_PERFORMED` | No hay hardware PS4 conectado ni método legítimo de despliegue disponible en el entorno. |

## Fuentes públicas consultadas

La página [PS4 Developer Wiki — Vulnerabilities](https://www.psdevwiki.com/ps4/Vulnerabilities) documenta nombres y relaciones del navegador, y enumera vulnerabilidades por rangos de firmware. No proporciona los tres módulos binarios 13.52, sus hashes, un Build ID común ni offsets validados contra bytes.

La página [PS4 Developer Wiki — Internet Browser](https://www.psdevwiki.com/ps4/Internet_Browser) documenta módulos del navegador, user-agents y versiones históricas de WebKit. La mención de 13.52 es metadata/documentación, no una distribución de los módulos retail ni una identidad de build verificable.

La página [PS4 Developer Wiki — Bootprocess](https://www.psdevwiki.com/ps4/Bootprocess) contiene logs históricos y un Build ID de un testkit antiguo. Ese Build ID no se atribuye a 13.52 y no puede utilizarse para validar los módulos solicitados.

La fuente OSS oficial de Sony disponible en el proyecto cubre WebKit 601 para 13.00–13.04. OpenOrbis aporta un toolchain de homebrew, no el SDK ni las bibliotecas internas retail.

## Regla de evidencia

Los nombres de módulos, comentarios, tablas de offsets, user-agents y documentación de exploits se conservan como `DOCUMENTED_ONLY`, `STRUCTURAL` o `UNVERIFIED`. No se transforman en `DIRECT_BYTES`. Para confirmar una build se requiere cada archivo, SHA-256, formato SELF/SPRX, Build ID y una manifest que vincule los tres módulos.

## Conclusión

No se encontró legalmente una copia verificable de los tres módulos 13.52, ni una identidad común, ni bytes desde los que calcular GOT/imports, vtables u offsets. Tampoco puede afirmarse una build retail-compatible ni una prueba real en hardware con el material disponible. El siguiente artefacto de mayor valor sería un conjunto legalmente aportado de los tres módulos de la misma instalación 13.52 con manifest y hashes.
