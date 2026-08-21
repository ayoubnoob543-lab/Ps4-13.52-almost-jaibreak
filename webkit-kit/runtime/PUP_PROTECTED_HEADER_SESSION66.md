# Cabecera protegida PUP — longitudes y comparación 13.50/13.52

El analizador `webkit-kit/tools/analyze_pup_protected_header.py` lee únicamente la cabecera visible de 16 bytes y mide la extensión indicada por sus campos de tamaño. No descifra ni ejecuta contenido.

## Resultados

| Firmware | Entrada | Header visible | Campo `unknown_0C` | Campo `unknown_0E` | Extensión total indicada | Bytes posteriores protegidos | Entropía de región protegida |
|---|---|---:|---:|---:|---:|---:|---:|
| 13.50 | UPDATE1 | 16 | `0x06f0` (1776) | `0x0bf0` (3056) | 4832 (`0x12e0`) | 4816 | 7.961669 |
| 13.52 | UPDATE1 | 16 | `0x06f0` (1776) | `0x0bf0` (3056) | 4832 (`0x12e0`) | 4816 | 7.957656 |
| 13.50 | UPDATE2 | 16 | `0x01b0` (432) | `0x0330` (816) | 1248 (`0x04e0`) | 1232 | 7.844464 |
| 13.52 | UPDATE2 | 16 | `0x01b0` (432) | `0x0330` (816) | 1248 (`0x04e0`) | 1232 | 7.835368 |

## Hashes de la región completa indicada

| Firmware | Entrada | SHA-256 de los primeros `header_extent` bytes |
|---|---|---|
| 13.50 | UPDATE1 | `e5bdc91fbc3f2d634280862d034d5eaee131be8b81b74d87a3c26ec4012a2f3d` |
| 13.52 | UPDATE1 | `940bcba8eb3b3ce91a40a72bae7103e8d3fd9d51165e016a3292bea8c097444d` |
| 13.50 | UPDATE2 | `58997c737b55dca0730aa5763b764c1bed19dcac25b4183f1dafae5fbb0e4417` |
| 13.52 | UPDATE2 | `22a3230670bd33c610f57caebdfc0c4af90b95de62d4d6643737914493d038c1` |

## Interpretación

Las longitudes del header extendido son **idénticas entre 13.50 y 13.52 para cada entrada**. Por tanto, el crecimiento de UPDATE1 (`+480` bytes) y UPDATE2 (`+16200` bytes) no procede de un cambio del tamaño de la cabecera PUP visible/extendida. Los cambios están en los segmentos o datos posteriores, no en la longitud indicada por estos campos.

La entropía de aproximadamente 7.84–7.96 bits/byte en la zona posterior al header es consistente con metadata protegida. No identifica por sí sola el algoritmo; la clasificación correcta es `HYPOTHESIS` para cifrado/combinación de cifrado y compresión, no una identificación criptográfica.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| Header visible de 16 bytes y magic `4f153d1d` | `DIRECT_13.50` / `DIRECT_13.52` |
| UPDATE1 usa una extensión de header de 4832 bytes en ambas versiones | `DIRECT_13.50` / `DIRECT_13.52` |
| UPDATE2 usa una extensión de header de 1248 bytes en ambas versiones | `DIRECT_13.50` / `DIRECT_13.52` |
| Los tamaños adicionales de 13.52 están en segmentos/payload, no en el header | `STRONG_INDIRECT_13.52` |
| El algoritmo concreto puede deducirse sólo de la entropía | `DISCARDED` |
