# Revisión estática de dumps públicos PS4 6.72/7.00 y kernel dumpers — sesión 72

## Fuentes revisadas

- `a0zhar/PS4.badhoist`: https://github.com/a0zhar/PS4.badhoist
- PSXHAX, “PS4 Webkit Bad_Hoist 6.72 Exploit Port WIP…”: https://www.psxhax.com/threads/ps4-webkit-bad_hoist-6-72-exploit-port-wip-by-sleirsgoevy-6-72-dumps.7533/
- `obhq/kernel-dumper`: https://github.com/obhq/kernel-dumper
- `driaptor/ps4-kernel-dumper`: https://github.com/driaptor/ps4-kernel-dumper

Las páginas se consultaron como texto. No se descargaron ni ejecutaron dumps, payloads o scripts.

## Dato nuevo relevante

`a0zhar/PS4.badhoist` declara que sus releases históricas contienen módulos pre-volcados de PS4 6.72: `webkit.bin`, `webkit.elf`, `libkernel.bin`, `libkernel.elf`, `libc.bin` y `libc.elf`, además de tablas de gadgets y syscalls. El README dice que esos módulos proceden de dumps frescos preparados con el método de Sleirsgoevy y que se usaron para construir PS4JB2. Esto es una referencia pública concreta a archivos WebKit antiguos, aunque la página consultada no entrega aquí hashes ni demuestra firmware 13.52.

La página PSXHAX de 2020 distingue dos conjuntos históricos: `dumps_672.7z` con `webkit.bin`, `webkit.elf`, `libkernel.bin` y libc para 6.72; y `700.7z` con `libc.sprx`, `libkernel.sprx`, `libkernel_sys.sprx`, `libkernel_web.sprx`, `libSceWebKit2.sprx` y otros módulos para 7.00. La misma página explica que el compilador ROP necesita dumps de WebKit, libc y libkernel, y que los offsets deben ajustarse por firmware.

Esta fuente es especialmente útil para nuestro objetivo porque documenta una diferencia de nomenclatura: en 7.00 aparecen `libSceWebKit2.sprx` y `libkernel_web.sprx`, mientras las referencias PSFree posteriores usan `libSceNKWebKit.sprx`. No se debe asumir que los nombres históricos sean intercambiables sin verificar el firmware y el módulo real.

## Relación con los kernel dumpers

Los repositorios `obhq/kernel-dumper` y `driaptor/ps4-kernel-dumper` describen payloads para volcar el kernel, no módulos WebKit. El material de 6.72/7.00 demuestra que históricamente existieron dumps WebKit públicos, pero no establece que los kernel dumpers produzcan esos archivos ni que sean aptos para 13.52.

## Valor para 13.52

El hallazgo eleva la viabilidad de obtener referencias históricas locales: si los archivos `dumps_672.7z` o `700.7z` estuvieran disponibles legítimamente, podrían analizarse estáticamente para preparar un comparador de ELF/SELF, imports, exports, strings y estructuras WebKit. No deben usarse para trasladar offsets a 13.52 ni como evidencia de que una vulnerabilidad posterior sigue viva.

No se encontró en estas páginas un dump 13.52, un hash de `libSceNKWebKit.sprx` 13.52, un Build ID 13.52 ni un enlace verificable a los bytes dentro del repositorio consultado. La existencia de los archivos históricos se clasifica como `DIRECT_HISTORICAL`; cualquier relación con 13.52 es `UNVERIFIED`.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| Dumps WebKit/libkernel anunciados para 6.72 | `DIRECT_HISTORICAL` |
| Conjunto de módulos anunciado para 7.00 | `DIRECT_HISTORICAL` |
| Separación `libSceWebKit2`/`libSceNKWebKit` por generación | `DIRECT_HISTORICAL` |
| Hashes y procedencia criptográfica de los archivos | `UNVERIFIED` |
| Disponibilidad de bytes 13.52 | `DISCARDED` en estas fuentes |
| Utilidad para preparar un diferencial | Alta, pero sólo histórica |

## Conclusión

Este hallazgo sí es más útil que un kernel dumper genérico: documenta públicamente conjuntos concretos de módulos WebKit y `libkernel_web` de 6.72/7.00. Puede permitir preparar una comparación real si los archivos históricos se obtienen por una vía legítima. Sin embargo, no resuelve el bloqueo de 13.52: seguimos necesitando un módulo retail 13.52 o metadata equivalente con procedencia verificable.
