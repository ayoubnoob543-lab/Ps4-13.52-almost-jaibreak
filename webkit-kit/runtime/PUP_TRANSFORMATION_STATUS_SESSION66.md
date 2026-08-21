# Estado consolidado de la transformación PUP — sesión 66

## Estado de los datos

Las copias privadas contienen las dos imágenes completas PS4SYS de 13.50 y 13.52, divididas en 52 partes. La reconstrucción automática verifica tamaño y SHA-256. El respaldo no se modifica en este informe.

## Qué se ha demostrado

Las entradas `PS4UPDATE1.PUP` y `PS4UPDATE2.PUP` tienen el magic `4f153d1d` y una cabecera visible de 16 bytes. Los campos visibles indican una extensión total de header de 4832 bytes para UPDATE1 y 1248 bytes para UPDATE2, idénticas en ambas versiones. La documentación pública y dos familias de parsers confirman que la tabla de segmentos y la metadata necesaria para interpretar los payloads se encuentra después de esa frontera y se procesa mediante una etapa de descifrado/servicio del sistema.

El payload posterior tiene entropía alta y no contiene cabeceras `ELF`/`SELF` ni nombres de WebKit visibles. El diferencial bruto 13.50→13.52 cambia casi completamente el payload, por lo que no es un mapa directo de funciones u offsets.

Se ha encontrado una región continua de 240 bytes idéntica en ambas entradas y en ambas versiones: relativa a `0x6f0` en UPDATE1 y `0x1b0` en UPDATE2. Esa posición coincide con el campo visible `unknown_0C`. Los 240 bytes equivalen a `3 × 0x50`, el tamaño documentado públicamente para una entrada de metadata PUP; sin embargo, no se ha demostrado que el bloque tenga esa semántica en PS4 13.52.

## Qué no se ha demostrado

No se ha identificado una clave de descifrado, un algoritmo completo offline, la tabla de segmentos descifrada, ningún módulo `libSceNKWebKit.sprx` ni una correspondencia entre offsets PUP y funciones WebKit/JSC. La presencia de un bloque de tamaño compatible con metadata no prueba que contenga claves AES, IV, digest o HMAC.

## Siguiente experimento de mayor valor

El siguiente dato decisivo sería una cabecera extendida legítimamente descifrada (`.PUP.dec`) de una versión/entrada compatible, o una especificación pública que permita interpretar los campos sin depender del servicio `encsrv`. Con ese dato se podría comprobar si la región de 240 bytes es una tabla de metadata, identificar los segmentos y mapear posteriormente los contenedores a imágenes y módulos.

Mientras ese artefacto no exista, continuar cambiando nombres, adivinando offsets o tratando coincidencias de alta entropía como WebKit produciría falsos positivos.

## Clasificación global

| Elemento | Clasificación |
|---|---|
| Bytes completos de PS4SYS 13.50/13.52 en respaldo privado | `DIRECT_13.50` / `DIRECT_13.52` |
| Cabeceras visibles y tamaños de header | `DIRECT_13.50` / `DIRECT_13.52` |
| Región invariante de 240 bytes | `DIRECT_13.50` / `DIRECT_13.52` |
| Correspondencia `240 = 3 × 0x50` | `DIRECT` como aritmética; `HYPOTHESIS` como semántica |
| Metadata PUP protegida después de la cabecera visible | `STRONG_INDIRECT_13.52` |
| `libSceNKWebKit` dentro de un rango concreto | `UNVERIFIED` |
| Vulnerabilidad/primitive WebKit en 13.52 | `UNVERIFIED` |

Este informe es un estado de investigación, no una conclusión de compatibilidad ni una afirmación de exploit.

## Auditoría local de artefactos descifrados

Se revisó recursivamente `/home/ubuntu` buscando extensiones `.dec`, nombres `*PUP.dec*` y artefactos `*decrypted*`. El único resultado fue una página documental histórica; no apareció ningún `.PUP.dec`, tabla de segmentos descifrada, SELF legible ni módulo SPRX descifrado.

Esto confirma que el respaldo privado añade los bytes brutos completos, pero no elimina el bloqueo de interpretación de la capa protegida.
