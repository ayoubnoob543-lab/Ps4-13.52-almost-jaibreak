# Revisión estática de kernel dumpers PS4 — sesión 71

## Fuentes

- `obhq/kernel-dumper`: https://github.com/obhq/kernel-dumper
- `driaptor/ps4-kernel-dumper`: https://github.com/driaptor/ps4-kernel-dumper

Ambos repositorios fueron consultados como páginas públicas. No se clonaron, compilaron ni ejecutaron sus payloads.

## `obhq/kernel-dumper`

El repositorio se describe como un payload para volcar el kernel de PS4 y declara soporte únicamente para firmware 11.00. Su README explica que el resultado esperado es un `kernel.elf` escrito en USB y que puede cargarse en Ghidra como `Raw Binary` con una dirección base obtenida de sus program headers. El proyecto está implementado principalmente en Rust y requiere una cadena de kernel exploit/PPPwn para ejecutarse.

No contiene un `kernel.elf` preextraído ni `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `rt.jar` o `bdjstack.jar`. El propio rango declarado 11.00 lo hace histórico para nuestro objetivo 13.52. Su valor principal es documental: muestra que un dump de kernel no equivale a un dump de módulos de usuario y que la identificación del kernel requiere base/metadata.

## `driaptor/ps4-kernel-dumper`

El repositorio se describe como un dumper que escribe el kernel desde memoria a USB. Declara compatibilidad con cualquier firmware soportado por `ps4-payload-sdk`, pero no proporciona en la página revisada una matriz concreta de versiones ni un dump preextraído. Tampoco muestra `libSceNKWebKit`, `libkernel_web`, WebKit/JSC o BD-J. Su procedencia se remonta al proyecto de `eversion/PS4-Kernel-Dumper`, según el README.

La afirmación de compatibilidad es genérica y no demuestra soporte 13.52. Al igual que el primer repositorio, describe una operación que requeriría ejecución en hardware y privilegios de kernel; no constituye una fuente estática de bytes WebKit.

## Relevancia para nuestro objetivo

Los dos proyectos pueden ser útiles para entender la diferencia entre `kernel.elf` y módulos de usuario, pero no resuelven el bloqueo de `libSceNKWebKit.sprx`. Un kernel dump podría contener referencias, rutas o estructuras globales, pero sólo si el dump real está disponible y si se analiza pasivamente; los repositorios consultados no lo proporcionan.

Tampoco es correcto usar estos proyectos para obtener el WebKit 13.52: sus READMEs describen payloads de kernel y operaciones sobre una PS4, no una ruta pública de extracción offline. No se recomienda ejecutarlos ni adaptarlos a la consola.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| `obhq/kernel-dumper` existe y declara soporte 11.00 | `DIRECT_DOCUMENTATION` / `HISTORICAL_ONLY` |
| `driaptor/ps4-kernel-dumper` existe y describe un dumper USB | `DIRECT_DOCUMENTATION` |
| Soporte específico 13.52 | `UNVERIFIED` |
| Contienen `libSceNKWebKit` o `libkernel_web` | `DISCARDED` |
| Proporcionan un dump de kernel descargable | `DISCARDED` |
| Sirven como fuente de WebKit 13.52 | `DISCARDED` |

## Conclusión

Estos repositorios no aportan el archivo que buscamos. Son referencias de payloads de kernel, no dumps ni extractores offline de `libSceNKWebKit.sprx`. El siguiente artefacto de mayor valor continúa siendo el propio módulo WebKit o un dump parcial legítimamente obtenido con hash, firmware y procedencia verificables.
