# Análisis de cabeceras y metadatos PUP 13.50→13.52

**Fecha:** 2026-08-21
**Alcance:** análisis local, estático y de sólo lectura. No se descifró, ejecutó ni modificó contenido de firmware.

## Resumen

Los PUP completos locales contienen una estructura SLB2 visible y estable. Entre 13.50 y 13.52 cambian únicamente algunos campos de metadata de nivel superior y el tamaño/sector inicial de la segunda entrada; las cabeceras internas de `PS4UPDATE1.PUP` y `PS4UPDATE2.PUP` son idénticas byte a byte. Esto descarta que el cambio visible de cabecera sea una clave de descifrado distinta para cada entrada.

La evidencia no permite derivar una clave ni identificar el contenido WebKit. La única transformación demostrable en esta capa es el cambio de tamaño total, el desplazamiento de la segunda entrada y el reempaquetado asociado.

## Artefactos y hashes

| Firmware | Ruta | Tamaño | SHA-256 |
|---|---|---:|---|
| 13.50 | `/home/ubuntu/ps4-1352-pup-audit-session42/pup1350/original/PS4SYS_CRC[6E6D1610]_PS4UPDATE.PUP` | 503293952 | `04585405bf3ad0836103c1eea5c21657327a377824ad5cda7674ecb94f03822f` |
| 13.52 | `/home/ubuntu/ps4-1352-pup-audit-session42/original/PS4SYS_CRC[DC9D6197]_PS4UPDATE.PUP` | 503310848 | `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11` |

La copia separada local de `PS4UPDATE1.PUP` coincide byte a byte con la entrada 13.52 y tiene SHA-256 `fd5e6c16398e628b3f258bce5f395c9fda687011a1a985d4b507928f54e6b580`.

## Cabecera SLB2

La cabecera visible es `SLB2` en ambas versiones. Los campos interpretados por el parser local son:

| Campo | 13.50 | 13.52 | Resultado |
|---|---:|---:|---|
| Magic | `SLB2` | `SLB2` | Igual |
| Version | 2 | 2 | Igual |
| Flags | 0 | 0 | Igual |
| Entry count | 2 | 2 | Igual |
| Size in sectors | 982996 | 983029 | +33 sectores |
| Bytes declarados | 503293952 | 503310848 | +16896 bytes |
| Tamaño declarado = archivo | Sí | Sí | Igual |

La única diferencia de la cabecera de 32 bytes está en el campo de tamaño de contenedor, en el offset `0x10`. No hay un campo visible que se comporte como una clave de descifrado.

## Tabla de entradas

| Entrada | Offset 13.50 | Offset 13.52 | Delta offset | Tamaño 13.50 | Tamaño 13.52 | Delta tamaño |
|---|---:|---:|---:|---:|---:|---:|
| `PS4UPDATE1.PUP` | 1024 | 1024 | 0 | 326026471 | 326026951 | +480 |
| `PS4UPDATE2.PUP` | 326027776 | 326028288 | +512 | 177266167 | 177282367 | +16200 |

La segunda entrada pasa del sector `636773` al `636774`. El desplazamiento de 512 bytes es coherente con la reserva por sectores del contenedor; no demuestra un desplazamiento de una función interna.

## Cabeceras internas

Las cabeceras de 16 bytes al comienzo de cada entrada son idénticas entre versiones:

```text
PS4UPDATE1: 4f153d1d0001011204000000f006f00b
PS4UPDATE2: 4f153d1d0001011204000000b0013003
```

No aparecen nombres de módulos, hashes de WebKit ni claves visibles en estos 16 bytes. La cabecera común `4f153d1d00010112` aparece exactamente dos veces por imagen, únicamente al inicio de las dos entradas. No se encontró una segunda tabla con el mismo formato dentro de los payloads.

## Patrones de transformación que sí y que no se pueden sostener

| Hipótesis | Evidencia | Clasificación |
|---|---|---|
| El contenedor SLB2 se mantiene y sólo cambia su tamaño declarado | Magic, versión, flags y entry count iguales; campo de tamaño cambia | `DIRECT_13.50` / `DIRECT_13.52` |
| `PS4UPDATE1` crece 480 bytes y `PS4UPDATE2` crece 16200 bytes | Tabla SLB2 y hashes de entradas | `DIRECT_13.50` / `DIRECT_13.52` |
| La segunda entrada se realinea por sectores | Offset cambia exactamente 512 bytes y sector +1 | `STRONG_INDIRECT_13.52` |
| La cabecera interna contiene una clave de descifrado | Cabecera idéntica en ambas versiones y sin campo reconocido de clave | `DISCARDED` |
| Existe una clave derivable comparando sólo estas cabeceras | No hay material visible suficiente ni campo variable con ese comportamiento | `UNVERIFIED` |
| Una región concreta del payload es WebKit/JSC | No hay índice, cabecera de módulo ni literales visibles | `UNVERIFIED` |
| El payload completo está cifrado | Alta entropía observada, ausencia de formatos/literales; no se ha identificado el algoritmo | `HYPOTHESIS`, no hecho confirmado |

## Qué buscaría una futura comprobación de la regla de transformación

Una clave o regla sólo podría inferirse de forma válida si se dispone de un par conocido-plaintext/ciphertext, metadata de autenticación, IV/nonce, una derivación documentada o una tercera muestra con relación conocida. La comparación actual no contiene ninguno de esos elementos. Probar claves arbitrarias contra el blob sin un criterio independiente produciría falsos positivos.

La siguiente comprobación legítima de mayor valor es obtener una capa interna decodificada o una metadata de procedencia que permita validar un bloque candidato. Con ella se podría comprobar si los offsets relativos, compresión y alineación corresponden a módulos concretos.

## Reproducibilidad

La herramienta nueva es:

```text
webkit-kit/tools/analyze_pup_metadata_transform.py
```

Validación realizada:

```bash
python3 -m py_compile webkit-kit/tools/analyze_pup_metadata_transform.py
```

El JSON completo del análisis se conserva junto al informe en el repositorio.

## Conclusión

Los PUP locales contienen estructura y metadata, no sólo bytes planos. La evidencia visible permite describir con precisión el empaquetado SLB2 y sus deltas, pero **no revela una clave de descifrado ni identifica el módulo WebKit**. El siguiente bloqueo no es conseguir más bytes, sino conseguir una relación verificable entre el payload opaco y una capa interna decodificada.
