# Revisión de releases `PS4.badhoist` — sesión 72

## Fuente

- Repositorio: `a0zhar/PS4.badhoist`
- URL: https://github.com/a0zhar/PS4.badhoist
- Releases: https://github.com/a0zhar/PS4.badhoist/releases
- Rama: `main`
- Estado: páginas públicas leídas; no se descargaron assets ni se ejecutaron archivos.

## Evidencia de releases

La página de releases expone tres releases descritas como módulos pre-dumpados para PS4 **6.72**. La release más reciente, `v2`, se presenta como “New dump of modules!!! (FW 6.72)” y dice que incluye un archivo `.rar` con módulos ya preparados para PS4JB2. La lista publicada incluye `libc.bin`, `libc.elf`, `libkernel.bin`, `libkernel.elf`, `webkit.bin`, `webkit.elf`, `gadgets.txt`, `webkit-gadgets.txt`, `libc-gadgets.txt` y `syscalls.txt`.

La release `v1.2`, fechada en la página como 16/04/2023, vuelve a declarar diez archivos para firmware 6.72 y explica que se añadieron porque el dumper podía quedarse sin memoria. La release `v1.0`, fechada como 07/03, declara tres módulos: `webkit.bin`, `libkernel.bin` y `libc.bin`. Los commits de las releases aparecen con firmas GitHub verificadas, aunque la página también indica que las claves están expiradas; esa firma autentica el commit de GitHub, no la procedencia original de los dumps ni su correspondencia con un firmware distinto de 6.72.

## Qué aporta al objetivo actual

Este repositorio ofrece una ruta pública y concreta para obtener referencias WebKit antiguas si los assets de release siguen disponibles. Es más sólido que una afirmación editorial porque especifica nombres de archivos, firmware atribuido y el contenido esperado del paquete. Sin embargo, no proporciona evidencia de 13.52, no incluye hashes de los assets en la página consultada y no demuestra que los binarios sigan descargables o que procedan de una cadena de custodia independiente.

La nomenclatura `webkit.bin`/`webkit.elf` tampoco debe confundirse automáticamente con `libSceNKWebKit.sprx`: el README los describe como módulos WebKit pre-dumpados y generados para una toolchain concreta. Para atribuirlos a un módulo se necesitarían los bytes, cabeceras/metadata y hash.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| Releases públicas con nombres de archivos WebKit/libkernel | `DIRECT_HISTORICAL` |
| Firmware declarado 6.72 | `DIRECT_HISTORICAL` |
| Assets accesibles actualmente | `UNVERIFIED` |
| Hashes y cadena de custodia de los dumps | `UNVERIFIED` |
| Relación con PS4 13.52 | `DISCARDED` |
| Utilidad para comparar estructuras antiguas | Alta, si se obtienen legítimamente los assets |

## Conclusión

La página de releases confirma que existen precedentes públicos de módulos WebKit PS4 6.72 empaquetados para análisis y compilación. Puede servir para validar un pipeline ELF/RAW y estudiar la evolución histórica frente a 9.50/9.60. No resuelve el bloqueo de 13.52 ni autoriza trasladar offsets o cadenas de explotación a firmware posterior.

## Referencias

[1] [Repositorio `a0zhar/PS4.badhoist`](https://github.com/a0zhar/PS4.badhoist)

[2] [Releases de `a0zhar/PS4.badhoist`](https://github.com/a0zhar/PS4.badhoist/releases)

[3] [README público](https://github.com/a0zhar/PS4.badhoist/blob/main/README.md)
