# Estado de investigación — PS4 13.52

**Proyecto:** PS4-13.52-Jailbreak-Research
**Estado:** en desarrollo; no es un jailbreak.
**Última auditoría:** 2026-08-16
**Método:** análisis estático, sin ejecutar el dump ni usar hardware.

## Resumen ejecutivo

El corpus contiene un blob x86-64 de 479232 bytes cuya integridad puede reproducirse mediante la concatenación exacta de tres chunks. Las strings, rutas internas y patrones de código son coherentes con la familia Sony/Orbis `libkernel`, pero el blob aislado no contiene una prueba autónoma de que la captura corresponda exactamente a FW 13.52. El nombre del repositorio, el README original y la procedencia declarada favorecen esa atribución, pero no sustituyen un manifest, hash oficial o valor runtime de versión.

No existe en este repositorio un jailbreak ni un exploit confirmado. Los stubs JITSHM y los wrappers documentados son resultados de reverse engineering; no constituyen por sí mismos una primitive de explotación ni una cadena reproducible.

## Clasificaciones actuales

| Categoría | Resultado |
|---|---|
| **CONFIRMADO** | hash del combinado; concatenación de chunks; offsets de archivo; instrucciones syscall `0x215`, `0x216` y `0xf0`; XREFs RIP-relative enumeradas; existencia de strings/version-query code |
| **FUERTEMENTE SOPORTADO** | pertenencia a la familia libkernel/Orbis; helper TLS/error alrededor de `0x1bb0`; función temporal alrededor de `0x13b20`; dispatch alrededor de `0x114d0–0x11520`; consultas de versión mediante `0x10240` |
| **POTENCIAL** | nombres semánticos `usleep`, `jitshm_create`, `jitshm_alias`, `mmap`, `connect` y varios wrappers POSIX, a falta de exports/relocations |
| **NO VERIFICABLE** | versión exacta 13.52 desde el blob solo; GOT del eboot; validación de hardware; deltas entre firmwares sin imágenes comparables |
| **CONTRADICHO** | rango/tamaño del README histórico: decía `0x75fff`/468 KB, pero el archivo real es `0x75000` bytes y termina en `0x74fff` |

## Evidencia incorporada

Se han incorporado al repositorio scripts y salidas para:

1. Verificar SHA-256 y tamaños de los cuatro binarios.
2. Verificar byte a byte la concatenación de los tres chunks.
3. Comprobar prólogos como sanity check, sin usarlos como identificación de símbolo.
4. Desensamblar estáticamente el blob como x86-64 Intel.
5. Extraer XREFs RIP-relative a `kern.sdk_version`, `%2x.%03x.%03x` y las cuatro cadenas `machdep.*`.
6. Analizar las zonas `0x19720`, `0x19790`, `0x19860`, `0x198e0`, `0x19970`, `0x19a00`, `0x19a40`, `0x1be10`, `0x1be70`, `0x1bed0`, `0x1bf40`, `0x1bfd0`, `0x1c030` y helpers `0x10240`, `0x10130`, `0x13d90`, `0x1bb0`, `0xdde0`.

## Prioridades

La prioridad 1 es obtener el eboot exacto de Okage v1.01 usado en la captura, o un mapa estático de imports/relocations, para comprobar el slot GOT `0x0083d1c0`. La prioridad 2 es conseguir una imagen comparable de `libkernel_sys` de una versión conocida, especialmente 11.02 o 12.52. La prioridad 3 es conseguir un manifest/hash que relacione `J02697906` con FW 13.52.

## Reglas de contribución

Las contribuciones deben conservar la distinción entre hecho e inferencia, indicar offsets como offsets de archivo salvo que se demuestre una dirección virtual, no asignar símbolos por coincidencia de prólogo y no afirmar explotación sin una demostración reproducible. No deben subirse eboots, claves, credenciales, dumps adicionales propietarios ni datos personales.
