# Correlación pública del formato interno PUP — sesión 66

## Fuentes públicas consultadas

1. PSDevWiki, página `PUP`: https://www.psdevwiki.com/ps4/PUP
2. PSDevWiki, página `SLB2`: https://www.psdevwiki.com/ps4/SLB2
3. PSXHAX, comparación de inner PUP 4.07/4.55: https://www.psxhax.com/threads/ps4-inner-pup-files-of-ps4update-system-comparison-by-masterzorag.2562/
4. andy-man/ps4-pup-decrypt: https://github.com/andy-man/ps4-pup-decrypt

## Hallazgo relevante

PSDevWiki documenta que cada fragmento PUP tiene una cabecera `ScePupHeader` cuyo magic es `4f153d1d`. La página indica que los primeros `0x10` bytes son visibles y que los `0x10` bytes restantes de la cabecera, junto con la metadata posterior, están cifrados. También documenta una tabla de segmentos con `flags`, `offset`, `compressed_size` y `uncompressed_size`, además de metadata con claves AES-128, IV, digest y clave de digest.

Esto coincide con la observación local: las entradas 13.50/13.52 empiezan con una cabecera común de 16 bytes y después presentan datos de alta entropía sin una tabla de segmentos visible.

La misma fuente pública indica que la metadata contiene el material criptográfico intermedio necesario para descifrar/verificar segmentos y que la extracción normal requiere un primer paso de descifrado antes del desempaquetado.

PSXHAX documenta históricamente que las comparaciones de inner PUP se hacían sobre datos cifrados y que los primeros ocho bytes podían permanecer iguales aunque el resto difiriera. Esto respalda la interpretación de que el diferencial bruto no es un mapa directo de funciones.

El repositorio público `andy-man/ps4-pup-decrypt` describe un descifrador que opera mediante un payload en la consola y advierte que sólo descifra actualizaciones compatibles con el firmware instalado; no proporciona una clave estática genérica para convertir offline el PUP retail en módulos.

## Aplicación a 13.50/13.52

| Observación local | Relación con fuente pública | Clasificación |
|---|---|---|
| Magic `4f153d1d` en ambas entradas | Coincide con `PS4PUPMAGIC` documentado | `DIRECT_13.50` / `DIRECT_13.52` |
| Primeros 16 bytes comunes y resto opaco | Coincide con límite público de cabecera visible/cifrada | `STRONG_INDIRECT_13.52` |
| Falta tabla de segmentos visible | Esperable si la metadata posterior está cifrada | `STRONG_INDIRECT_13.52` |
| Diferencial bruto casi completo | Compatible con datos cifrados/reempaquetados; no identifica funciones | `DIRECT_13.50` / `DIRECT_13.52` |
| Clave derivable sólo de la cabecera visible | No demostrada; la metadata criptográfica está después del límite visible | `UNVERIFIED` |

## Consecuencia

La búsqueda debe dejar de tratar los 16 bytes visibles como si fueran un índice de módulos. El formato público explica por qué no aparece `SELF`, `ELF`, `libSceNKWebKit` o la tabla de segmentos: esos datos están dentro de la parte protegida del fragmento.

No se ha usado ningún descifrador contra hardware ni se ha ejecutado payload. Esta nota sólo correlaciona documentación pública con bytes locales ya adquiridos.

## Búsqueda pública adicional

Se consultaron también:

- PSXHAX, `PS4 PUP_Decrypt & PUP_Unpack` (30 enero 2017): https://www.psxhax.com/threads/ps4-pup_decrypt-pup_unpack-decrypt-unpack-ps4-updates-by-idc.1602/
- Reddit, `PS4 Firmware 6.xx was decrypted...`: https://www.reddit.com/r/ps4homebrew/comments/airtlf/ps4_firmware_6xx_was_decrypted/
- Vídeo de TheeEvolutionYT, `PS4 13.52 BD-J USERLAND BUG FULLY ACHIEVED!`: https://www.youtube.com/watch?v=ZG-SGV4c-kQ

PSXHAX describe históricamente `pup_decrypt` como una utilidad que invoca el kernel de PS4 para descifrar PUP y luego usa `pup_unpack` sobre los `.PUP.dec`; también documenta que la compatibilidad dependía de la versión instalada y del product code. La lista pública citada llega a firmwares antiguos, no a 13.52. Esto es `HISTORICAL_ONLY` y no demuestra una ruta offline para nuestros PUP.

La página del vídeo de 13.52 (fecha mostrada: 23 julio 2026) afirma en título/descripción que existe BD-J userland en 13.52 y que todavía falta un kernel bug para un jailbreak completo. El contenido extraído no proporciona una cabecera descifrada, hash, módulo `libSceNKWebKit`, offset ni primitive reproducible. Se clasifica como `DOCUMENTED_ONLY`/`UNVERIFIED` respecto a la transformación PUP y como `UNVERIFIED` para cualquier primitive concreta.
