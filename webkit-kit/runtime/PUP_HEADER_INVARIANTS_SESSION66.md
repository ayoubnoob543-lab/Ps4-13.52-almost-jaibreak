# Invariantes del header protegido PUP — sesión 66

Se compararon byte a byte los headers protegidos completos indicados por la cabecera visible de `PS4UPDATE1.PUP` y `PS4UPDATE2.PUP` entre 13.50 y 13.52.

## Resultado principal

Aparece una región idéntica de **240 bytes** en ambas versiones y en ambas entradas:

| Entrada | Offset relativo dentro de la entrada | Offset absoluto 13.50 | Offset absoluto 13.52 | Longitud |
|---|---:|---:|---:|---:|
| UPDATE1 | `0x6f0` (`1776`) | `0xaf0` (`2800`) | `0xaf0` (`2800`) | 240 bytes |
| UPDATE2 | `0x1b0` (`432`) | `0x136ecbb0` (`326028208`) | `0x136ecdb0` (`326028720`) | 240 bytes |

Los offsets absolutos de UPDATE2 se calculan desde las cabeceras internas encontradas en `0x136eca00` (13.50) y `0x136ecc00` (13.52), no desde un offset fijo reutilizado entre versiones.

La región tiene SHA-256:

```text
dd5f5f7509c0b2a1c8558f1c81522b926c0ed16513007ff60014ac7a453bbbab
```

Ese hash es idéntico en UPDATE1/UPDATE2 y en 13.50/13.52. El bloque no es cero ni padding ASCII; comienza con:

```text
21b9e2df65251b571d233dcea6b7a6a0d95949cc31a92c9cf6c5e87d09521e50
```

## Contexto de límites

Los offsets relativos `0x6f0` y `0x1b0` coinciden exactamente con el valor visible `unknown_0C` de cada cabecera. El resto del header protegido cambia casi por completo:

| Entrada | Bytes protegidos comparados | Bytes iguales | Región continua de 240 bytes |
|---|---:|---:|---|
| UPDATE1 | 4816 | 260 | Sí, en `0x6f0–0x7df` |
| UPDATE2 | 1232 | 243 | Sí, en `0x1b0–0x29f` |

Los bytes iguales adicionales son coincidencias aisladas de un solo byte. No hay otra región continua comparable.

## Interpretación prudente

La región de 240 bytes es un **invariante real y reproducible**, pero su significado no está identificado. Posibilidades compatibles incluyen una estructura constante, una firma o material de metadata que no cambia entre estas versiones; ninguna se puede afirmar sólo por el contenido. No se debe llamarla clave AES, digest, tabla de segmentos o componente WebKit sin una especificación o descifrado que lo confirme.

El hecho de que el bloque empiece en el campo visible `unknown_0C` puede ser una pista de layout, pero no demuestra que sea el inicio de una tabla. La evidencia pública revisada indica que la metadata posterior al límite visible está protegida, por lo que este bloque podría ser parte de una región de formato común que sobrevive sin cambios.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| Existe un bloque idéntico de 240 bytes en ambas entradas y versiones | `DIRECT_13.50` / `DIRECT_13.52` |
| El bloque coincide con una frontera indicada por `unknown_0C` | `STRONG_INDIRECT_13.52` |
| El bloque es una clave o permite derivar la clave | `HYPOTHESIS` / `UNVERIFIED` |
| El bloque contiene WebKit/JSC | `DISCARDED` |

Herramienta reproducible: `webkit-kit/tools/find_pup_header_invariants.py`.

## Observación de tamaño

Los 240 bytes invariantes equivalen exactamente a `3 × 0x50`. La documentación pública describe `ScePupMetadataEntry` con tamaño `0x50` bytes, compuesto por clave AES-128, IV, digest y clave de digest. Por ello existe una **correspondencia de tamaño** entre el bloque común y tres entradas de metadata documentadas.

Esta correspondencia no demuestra que el bloque sea metadata ni que contenga claves utilizables: el contenido no se ha descifrado, no se han identificado límites semánticos y un tamaño coincidente puede ser accidental. Se clasifica como `HYPOTHESIS`/`UNVERIFIED`, pero es una pista estructural concreta que merece comprobarse si aparece una cabecera extendida legítimamente descifrada.

Los tres subbloques de `0x50` tienen hashes, respectivamente:

```text
b05e5a1060ced8e6d17114579052bdb192887683cce20813433a829f693abaa4
210b3f5da85003857f6ba7883d1a33a7d91d8a1a79a7b1a68fd8ffff0c4dc55d
d6003c3577480722dafc016d52f19690892a59eaf44db16fb2233b824651e6fd
```

El espacio inicial de la tercera línea en este bloque es sólo presentación; el hash correcto comienza por `d6003c...`.

## Relación aritmética adicional

Para UPDATE1, los campos visibles suman:

```text
0x06f0 + 0x0bf0 = 0x12e0 = 4832
```

Para UPDATE2:

```text
0x01b0 + 0x0330 = 0x04e0 = 1248
```

Esto coincide con la extensión total del header que el parser público calcula como `unknown_0C + unknown_0E`. El bloque invariante empieza exactamente en `unknown_0C`, es decir, en la frontera entre ambas cantidades. Según la nomenclatura pública de `ScePupHeader`, esto es compatible con que `unknown_0C` sea el tamaño de la parte de header y `unknown_0E` el tamaño de metadata.

La lectura más fuerte que permiten los datos es, por tanto, **una región de 240 bytes situada al comienzo de la zona compatible con metadata**. Como `0xf0 = 3 × 0x50`, también es compatible en tamaño con tres entradas `ScePupMetadataEntry`. Esto sigue sin probar que el contenido esté en claro ni que sean claves o digests utilizables; se mantiene como `STRONG_INDIRECT_13.52` para la frontera de layout y `HYPOTHESIS` para la semántica de las tres entradas.

## Evidencia adicional de PS4Delta/Prosperity

En `Force67/prosperity/delta/formats/pup_object.cpp`, el comentario asociado a las entradas especiales `0xE.../0xF...` describe una tabla `ScePupMetadataEntry` que contiene por segmento `AES key/IV/digest/HMAC`. El mismo comentario indica que un archivo `.PUP.dec` obtenido mediante un oracle de consola ya habría consumido y puesto a cero esa tabla.

Esta observación es **código público de la ruta PS5 del proyecto**, no una prueba directa de que el bloque de 240 bytes de los PUP PS4 13.50/13.52 sea esa tabla. Su valor es estructural: aporta una semántica pública posible para el tamaño `0x50` y para regiones especiales de metadata, pero debe clasificarse como `HISTORICAL_ONLY`/`HYPOTHESIS` al trasladarla a PS4 13.52.
