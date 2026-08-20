# Estado de acceso a módulos dentro del PUP PS4 13.52

**PUP:** oficial Sony, SHA-256 `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11`  
**Ruta fuera de Git:** `/home/ubuntu/ps4-1352-authorized-pup/PS4UPDATE.PUP`  
**Método:** parsing SLB2, inspección de cabeceras raw y búsqueda de magic bytes/nombres. No se descifró, extrajo ni ejecutó contenido protegido.

## Respuesta directa

**No hemos pasado todavía de “PUP verificado” a “módulo WebKit 13.52 analizable”.** El PUP sí permite confirmar estructuralmente el contenedor SLB2 y sus dos rangos internos, pero las entradas no exponen un módulo ELF/SELF accesible con las herramientas actuales.

## Estructura confirmada

| Campo | Resultado | Categoría |
|---|---|---|
| Magic exterior | `SLB2` | **MATCH** |
| Versión | `2` | **MATCH** con manifest |
| Flags | `0` | **MATCH** con manifest |
| Número de entradas | `2` | **MATCH** con manifest |
| Tamaño declarado/real | `503310848` / `503310848` | **MATCH** |
| Entrada 1 | `PS4UPDATE1.PUP`, offset `1024`, tamaño `326026951` | **MATCH** |
| Entrada 2 | `PS4UPDATE2.PUP`, offset `326028288`, tamaño `177282367` | **MATCH** |
| Descifrado | No realizado | **UNVERIFIED** para contenido interno |

Los hashes de las dos entradas coinciden con el análisis previo y se mantienen como metadata verificable del rango raw:

```text
PS4UPDATE1.PUP  fd5e6c16398e628b3f258bce5f395c9fda687011a1a985d4b507928f54e6b580
PS4UPDATE2.PUP  44cd0c0e85b5912150112df99867357c3822a90f366198d11e2ec4c1e10adee7
```

## Qué puede verse sin descifrado

Las dos entradas comienzan con datos binarios no interpretables por el parser SLB2. La búsqueda de nombres literales no encontró `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, `eboot.bin`, `WebProcess`, `JSCell`, `MarkedVector` ni `CloneSerializer`.

Además, una búsqueda separada de magic bytes reales dentro de cada rango no encontró:

| Magic | Resultado |
|---|---|
| `\x7fELF` | **NO MATCH** en ambas entradas |
| `SCE\0` (SELF) | **NO MATCH** en ambas entradas |
| `SLB2` anidado | **NO MATCH** en ambas entradas |
| `PK\x03\x04` | **NO MATCH** en ambas entradas |

La búsqueda ASCII de la palabra `ELF` sí produce coincidencias aisladas, pero no son cabeceras ELF reales y no se clasifican como módulos. No se deben usar como evidencia de un ELF incluido.

## Herramientas disponibles y límite

El repositorio ya contiene `tools/parse_slb2_static.py`, que valida el contenedor, límites, nombres de entradas y hashes de rangos sin descifrar. También existe `webkit-kit/tools/analyze_module_evidence.py`, pero requiere un archivo ELF/SELF-like accesible; no puede operar sobre las entradas raw del PUP sin convertirlas en un módulo interpretable.

El scanner `webkit-kit/tools/scan_pup_static_names.py` y la búsqueda de magic bytes confirman que no hay un módulo desempaquetado claramente accesible dentro de los rangos raw. No se inventó ni se aplicó ningún formato interno adicional.

## Firmas JS solicitadas

Las firmas `JSCell::toX`, `MarkedVector`/GC y `CloneSerializer`/`objectPool` no pueden evaluarse sobre un módulo WebKit porque no existe un ELF/SELF WebKit accesible para `analyze_module_evidence.py`. El resultado correcto es:

| Familia | Estado |
|---|---|
| `JSCell::toX` | **UNVERIFIED** |
| `MarkedVector` / GC | **UNVERIFIED** |
| `CloneSerializer` / `objectPool` | **UNVERIFIED** |

El escaneo literal devuelve **NO MATCH** en el raw PUP y en los blobs históricos de libkernel, pero eso no equivale a una conclusión sobre código protegido o descifrado.

## Artefactos WebKit

| Artefacto | Estado actual |
|---|---|
| `libSceNKWebKit.sprx` | **UNVERIFIED**; no aparece como archivo ni magic SELF/ELF raw |
| `libkernel_web.sprx` | **UNVERIFIED**; no aparece como archivo ni magic SELF/ELF raw |
| `libSceLibcInternal.sprx` | **UNVERIFIED**; no aparece como archivo; solo existe una referencia textual en el blob histórico de libkernel |
| `eboot.bin` | **UNVERIFIED**; no aparece como archivo ni nombre literal raw |

## Bloqueo exacto y siguiente paso legítimo

El bloqueo no es el PUP ni el parser SLB2: ambos están verificados. El bloqueo es que las entradas `PS4UPDATE1.PUP` y `PS4UPDATE2.PUP` contienen payloads protegidos/no interpretables para las herramientas autorizadas actuales y no exponen directamente los módulos retail. Falta un artefacto intermedio legítimo: un módulo WebKit ya extraído y autorizado, o una herramienta/documentación oficial/autorizada capaz de interpretar el formato interno protegido sin recurrir a descifrado no autorizado.

No se intentará descifrar el PUP ni se tratarán los strings ASCII como módulos. Cuando exista un `libSceNKWebKit.sprx` o `libkernel_web.sprx` accesible con procedencia y hash correlacionados con este PUP, podrá pasarse a `analyze_module_evidence.py` y clasificarse cada firma como `MATCH`, `PARTIAL MATCH`, `VULNERABLE_LIKE`, `FIXED_LIKE` o `NO MATCH`. En esta fase todas permanecen **UNVERIFIED**.

## Resultado de fase

| Pregunta | Respuesta |
|---|---|
| ¿PUP verificado? | Sí — **MATCH** |
| ¿SLB2 verificable? | Sí — **MATCH** |
| ¿Entrada raw interpretada como módulo? | No — **UNVERIFIED** |
| ¿Módulo WebKit 13.52 analizable? | **No** |
| ¿Familias JS evaluadas? | No — **UNVERIFIED** |

El PUP grande permanece fuera de Git. Solo se publicará este informe y metadata pequeña reproducible.
