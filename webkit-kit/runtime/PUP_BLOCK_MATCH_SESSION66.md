# Comparación de bloques PUP 13.50→13.52

Este análisis local compara bloques de igual tamaño y posición relativa dentro de `PS4UPDATE1.PUP` y `PS4UPDATE2.PUP`. No descifra ni ejecuta los payloads.

## Resultados

| Entrada | Tamaño de bloque | Bloques comparados | Bloques idénticos | Fracción |
|---|---:|---:|---:|---:|
| UPDATE1 | 16 bytes | 20376654 | 560015 | 2.7483% |
| UPDATE1 | 64 bytes | 5094163 | 140001 | 2.7483% |
| UPDATE1 | 512 bytes | 636770 | 17498 | 2.7479% |
| UPDATE2 | 16 bytes | 11079135 | 21252 | 0.1918% |
| UPDATE2 | 64 bytes | 2769783 | 5311 | 0.1917% |
| UPDATE2 | 512 bytes | 346222 | 663 | 0.1915% |

## Interpretación

Las fracciones son casi iguales al cambiar el tamaño de bloque, por lo que no aparece una capa evidente de coincidencias largas que permita alinear funciones o módulos. UPDATE2 tiene una coincidencia exacta mucho menor que UPDATE1. Esto es compatible con un reempaquetado o transformación amplia, pero no identifica por sí solo cifrado, compresión ni una clave concreta.

Las coincidencias exactas no se deben convertir automáticamente en regiones WebKit: pueden proceder de padding, cabeceras repetidas, ceros o datos constantes. Para atribuir una región se necesitaría una cabecera de módulo, índice, plaintext conocido o una extracción decodificada.

## Clasificación

| Conclusión | Clasificación |
|---|---|
| UPDATE1 conserva aproximadamente 2.75% de bloques en la misma posición | `DIRECT_13.50` / `DIRECT_13.52` |
| UPDATE2 conserva aproximadamente 0.19% de bloques en la misma posición | `DIRECT_13.50` / `DIRECT_13.52` |
| Existe alineación directa de funciones WebKit entre ambas imágenes | `DISCARDED` |
| Las coincidencias identifican una clave de descifrado | `UNVERIFIED` |
| Las coincidencias representan padding o datos constantes | `HYPOTHESIS` |

## Siguiente comprobación

Un análisis posterior de mayor valor debe agrupar las coincidencias por regiones y separar cabeceras/padding de payload, pero incluso una región coincidente no demostrará WebKit sin metadata independiente.
