# Límite entre parseo y descifrado en un decrypter PUP público

**Alcance:** revisión estática de código público; no se compiló ni ejecutó el payload.

## Fuente

Repositorio revisado temporalmente:

- `andy-man/ps4-pup-decrypt`
- Commit: `74c64c0e8726a7cd6c1de6a9d0b1b751f8fe9b97`
- Tree: `cbdab5513859acc90d300cd178c8b3d93b06d0b0`
- Archivos relevantes: `include/pup.h`, `source/decrypt.c`, `source/encryptsrv.c`.
- SHA-256 de `include/pup.h`: `16e700ed52c229e80a83d006e380c2fe5af33ccc38f1b06b432cca53c36b94b6`.
- SHA-256 de `source/encryptsrv.c`: `447c0654ac4eac16e7ea4aaa163e6689e21b7d323aa3d4a7783401fcf2353947`.
- SHA-256 de `source/decrypt.c`: `47711ca281337068aec1a47b2570f8c6b667d7ca9beedda25c60555cf683ceea`.

## Qué puede parsearse localmente

`include/pup.h` define una cabecera visible de 16 bytes (`pup_file_header`) con:

```c
uint32_t magic;
uint32_t unknown_04;
uint16_t unknown_08;
uint8_t  flags;
uint8_t  unknown_0B;
uint16_t unknown_0C;
uint16_t unknown_0E;
```

La estructura completa posterior (`pup_header`) añade `file_size`, `segment_count` y otros campos. `pup_file_header` tiene tamaño comprobado de 16 bytes en `source/checkheaders.c`, coincidiendo con la frontera observada localmente.

`source/decrypt.c` lee esos 16 bytes, valida `magic == 0x1D3D154F` y calcula `header_size = unknown_0C + unknown_0E`. Después lee el resto del header desde el PUP y no lo interpreta como tabla de segmentos hasta que ha pasado por la operación de descifrado.

## Dónde empieza la dependencia protegida

El flujo estático documentado por el código es:

```text
leer cabecera visible
→ leer header extendido protegido
→ encsrv_decrypt_header(...)
→ interpretar pup_header y pup_segment
→ verificar segmentos
→ encsrv_decrypt_segment(...) o encsrv_decrypt_segment_block(...)
```

`source/encryptsrv.c` implementa las operaciones como `ioctl()` sobre un descriptor `encsrv`:

| Operación | IOCTL |
|---|---:|
| Verificar BLS header | `0xC010440D` |
| Descifrar header | `0xC0184401` |
| Verificar segmento | `0xC0184402` / `0xC0184403` |
| Descifrar segmento | `0xC0184404` |
| Descifrar bloque de segmento | `0xC0284405` |

Los argumentos incluyen buffers, longitudes e índices de segmento. Esto demuestra que el repositorio no contiene una clave offline genérica en el código revisado: la operación de descifrado se delega al servicio del sistema mediante IOCTL.

## Relación con los bytes locales

Los bytes locales de 13.50 y 13.52 muestran:

```text
4f153d1d0001011204000000f006f00b  # UPDATE1
4f153d1d0001011204000000b0013003  # UPDATE2
```

El prefijo de 16 bytes coincide con el magic y el tamaño de `pup_file_header` documentados por el código público. La tabla de segmentos no aparece en texto plano porque el código espera descifrar el header extendido antes de interpretarla.

## Comparación con otro fork público

También se revisó estáticamente el fork público `Scene-Collective/ps4-pup-decrypt`, commit `1325f74307b67a9acc4af8145d9dc7c49965fd5b`. Su interfaz conserva las mismas operaciones `encsrv_decrypt_header`, `encsrv_decrypt_segment` y `encsrv_decrypt_segment_block`, con los mismos IOCTL `0xC0184401`, `0xC0184404` y `0xC0284405`. Las diferencias observadas son de includes y organización del código, no de la frontera criptográfica.

Esto refuerza que el límite `parseo local → servicio encsrv` es una propiedad compartida por las implementaciones públicas revisadas, aunque no constituye evidencia específica del firmware retail 13.52.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| La cabecera visible del fragmento mide 16 bytes | `STRONG_INDIRECT_13.52` |
| El magic local coincide con `0x1D3D154F` | `DIRECT_13.50` / `DIRECT_13.52` |
| La metadata posterior debe pasar por `encsrv_decrypt_header` antes del parseo | `HISTORICAL_ONLY` como código público; `STRONG_INDIRECT_13.52` para la interpretación local |
| Las operaciones de descifrado usan IOCTL del servicio del sistema | `HISTORICAL_ONLY` |
| El código público proporciona la clave privada o una transformación offline completa | `DISCARDED` |
| Se puede identificar `libSceNKWebKit` directamente desde el blob protegido | `UNVERIFIED` |

## Conclusión

La nueva evidencia explica el bloqueo con precisión: no estamos mirando una segunda tabla mal localizada; estamos mirando únicamente la cabecera visible de un formato cuya tabla de segmentos y metadata extendida se procesa mediante un servicio de cifrado. El siguiente artefacto de mayor valor sería una salida legítima ya descifrada del `encsrv` para 13.52 o metadata equivalente; el decrypter público revisado no permite obtenerla offline sólo con los PUP.

## Comprobación de ausencia de clave offline

Una búsqueda estática en el commit revisado no encontró constantes o llamadas AES/HMAC/OpenSSL/mbedTLS ni una clave privada embebida. El flujo abre `/dev/pup_update0` y delega la verificación y el descifrado en `ioctl()`/`encsrv`.

Esto no demuestra que ninguna otra herramienta pública tenga una ruta offline, pero sí descarta que este decrypter concreto proporcione una regla de transformación aplicable directamente desde Ubuntu a los PUP 13.50/13.52.

## Segundo unpacker público

Se revisó también estáticamente `Dextura/PS4-PUP-UNPACKER`. Su código C# lee la cabecera de 32 bytes (`magic`, tamaños, `fileSize`, `entryCount`) y después interpreta directamente la tabla de entradas/segmentos. No implementa la transformación criptográfica; espera que el archivo de entrada ya tenga la estructura extendida legible. Esto coincide con la separación pública `decrypt → unpack` y no proporciona una ruta adicional para interpretar offline los blobs locales protegidos.

## Tercer parser público: PS4Delta/Prosperity

Se revisó el archivo público `Force67/prosperity/delta/formats/pup_object.cpp`, commit `34752578f273617d6567e0185cccb04b6cd87ae4`, disponible en:

https://github.com/Force67/prosperity/blob/34752578f273617d6567e0185cccb04b6cd87ae4/delta/formats/pup_object.cpp

El código distingue entre el contenedor PUP y los payloads de segmentos. Para PS4, intenta descomprimir segmentos; si la operación falla, marca el contenido como cifrado y conserva los bytes raw. Su mensaje final distingue explícitamente entre imágenes de contenedor extraídas y módulos SELF cifrados dentro de ellas, indicando que hace falta un conjunto de módulos `.sprx` preextraídos para analizar el firmware.

Este proyecto refuerza la separación conceptual:

```text
PUP/segmentos → contenedor o imagen → SELF cifrado → módulo SPRX analizable
```

La fuente no demuestra nada específico de 13.52 ni identifica `libSceNKWebKit`; se clasifica como `HISTORICAL_ONLY`/`STRONG_INDIRECT_13.52` para la interpretación de la capa local.
