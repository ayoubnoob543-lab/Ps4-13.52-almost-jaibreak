# Caracterización de subbloques invariantes PUP — sesión 66

Se dividió la región invariante de `0xf0` bytes en tres subbloques consecutivos de `0x50` bytes. La herramienta usada es `webkit-kit/tools/analyze_pup_invariant_subblocks.py`.

## Resultado

Los tres subbloques son idénticos entre UPDATE1 y UPDATE2 dentro del PUP 13.50 y también coinciden con las mismas posiciones del PUP 13.52. Sus medidas son:

| Subbloque | Entropía | Bytes distintos | SHA-256 |
|---:|---:|---:|---|
| 0 | 5.872 bits/byte | 62 | `b05e5a1060ced8e6d17114579052bdb192887683cce20813433a829f693abaa4` |
| 1 | 5.928 bits/byte | 65 | `210b3f5da85003857f6ba7883d1a33a7d91a8a79a7b1a68fd8ffff0c4dc55d` |
| 2 | 6.122 bits/byte | 72 | `d6003c3577480722dafc016d52f19690892a59eaf44db16fb2233b824651e6fd` |

La entropía es menor que la de la región protegida completa, pero no presenta texto, ceros predominantes ni una estructura semántica identificable. La distribución por sí sola no permite determinar si son claves, IV, digests, firmas, contadores o campos opacos.

## Interpretación

El hecho confirmado es la invariancia exacta de los 240 bytes y su división natural en tres unidades de `0x50`. La correspondencia de tamaño con `ScePupMetadataEntry` documentada públicamente sigue siendo una hipótesis estructural; no existe evidencia local que permita asignar los cuatro campos de cada unidad a AES key, IV, digest o HMAC.

Por tanto, el análisis no convierte el bloque en una clave ni proporciona una transformación offline. Sirve como huella reproducible para comparar otra extracción o una cabecera extendida legítimamente descifrada.

## Clasificación

| Conclusión | Clasificación |
|---|---|
| Tres unidades idénticas de `0x50` bytes en ambas entradas/versiones | `DIRECT_13.50` / `DIRECT_13.52` |
| El bloque podría corresponder a tres entradas de metadata | `HYPOTHESIS` |
| Los subbloques son claves AES utilizables | `UNVERIFIED` |
| El bloque contiene WebKit/JSC | `DISCARDED` |

## Corrección de offset y verificación cruzada

Una primera ejecución de la herramienta usó por error el offset absoluto de UPDATE2 de 13.50 también para 13.52. Esa prueba intermedia apuntó a la cabecera de 13.52 y fue descartada.

La herramienta fue corregida para localizar dinámicamente la cabecera interna única de cada entrada y sumar el desplazamiento relativo documentado (`0x6f0` para UPDATE1 y `0x1b0` para UPDATE2). Con el método corregido:

- UPDATE2 13.50: cabecera en `0x136eca00`, región en `0x136ecbb0`.
- UPDATE2 13.52: cabecera en `0x136ecc00`, región en `0x136ecdb0`.
- Las dos regiones corregidas tienen el mismo SHA-256: `dd5f5f7509c0b2a1c8558f1c81522b926c0ed16513007ff60014ac7a453bbbab`.
- Sus tres subbloques vuelven a producir exactamente los tres hashes indicados arriba.

La conclusión de invariancia es, por tanto, válida sólo después de alinear cada entrada por su propia cabecera; el offset absoluto sí cambia `0x200` entre las dos versiones para UPDATE2.
