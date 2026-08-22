# Inventario local de PUP y búsqueda de WebKit — Sesión 73

## Alcance

Auditoría sólo de lectura de los archivos ya presentes en `/home/ubuntu`. No se descifraron, ejecutaron, renombraron ni modificaron los PUP. La búsqueda de nombres se hizo sobre el workspace local y la búsqueda dentro del repositorio `/home/ubuntu/firmware-lab-runtime` no encontró PUP, módulos `.sprx` ni archivos grandes asociados.

## PUP encontrados fuera del repositorio

| Ruta | Tamaño | Tipo `file` | SHA-256 | Identidad/procedencia observable |
|---|---:|---|---|---|
| `/home/ubuntu/ps4-1352-pup-audit-session42/original/PS4SYS_CRC[DC9D6197]_PS4UPDATE.PUP` | 503,310,848 bytes | `data` | `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11` | Nombre contiene CRC `DC9D6197`; firmware exacto no se demuestra sólo por el nombre |
| `/home/ubuntu/ps4-1352-pup-audit-session42/pup1350/original/PS4SYS_CRC[6E6D1610]_PS4UPDATE.PUP` | 503,293,952 bytes | `data` | `04585405bf3ad0836103c1eea5c21657327a377824ad5cda7674ecb94f03822f` | Directorio `pup1350` y CRC `6E6D1610`; atribución 13.50 plausible por ruta, pero requiere metadata interna para confirmación |
| `/home/ubuntu/ps4-1352-pup-audit-session42/pup1_attachment/original/PS4UPDATE1.PUP` | 326,026,951 bytes | `data` | `fd5e6c16398e628b3f258bce5f395c9fda687011a1a985d4b507928f54e6b580` | Copia identificada previamente como contenedor 13.52; este inventario conserva su hash |
| `/home/ubuntu/upload/PS4UPDATE1.PUP` | 326,026,951 bytes | `data` | `fd5e6c16398e628b3f258bce5f395c9fda687011a1a985d4b507928f54e6b580` | Duplicado byte a byte del archivo anterior |

## Resultado de la búsqueda de módulos

Dentro de `/home/ubuntu/firmware-lab-runtime` no aparecieron archivos llamados `libSceNKWebKit*`, `libkernel_web*` ni `*WebKit*.sprx`. Tampoco aparecieron PUP con extensión `.PUP`/`.pup` ni archivos de más de 100 MiB dentro del repositorio. La búsqueda más amplia en `/home/ubuntu` encontró los cuatro PUP enumerados arriba, pero no encontró un módulo WebKit con esos nombres.

## Interpretación

Los cuatro archivos prueban que existen contenedores PUP locales y que dos rutas contienen copias idénticas de `PS4UPDATE1.PUP`. No prueban por sí solos que una entrada interna concreta sea `libSceNKWebKit.sprx`. Para avanzar hay que enumerar el formato interno mediante un parser estático legítimo y obtener una entrada con nombre/ruta, tamaño, formato y hash que identifique inequívocamente el módulo. Hasta ese punto, no se debe renombrar ningún PUP ni tratar el contenedor completo como si fuera WebKit.

## Estado

Clasificación actual: `PUP_PRESENT_LOCALLY`; `LIBSCE_NKWEBKIT_1352 = UNVERIFIED`; `LIBKERNEL_WEB_1352 = UNVERIFIED`; `WEBKIT_RETAIL_BYTES_1352 = UNVERIFIED`.

No se realizó ningún análisis de ejecución ni se abrió el contenido con herramientas que intenten descifrarlo.


## Escaneo literal de rangos PUP 13.52

Se ejecutó `webkit-kit/tools/scan_pup_static_names.py` únicamente sobre el PUP local `/home/ubuntu/ps4-1352-pup-audit-session42/original/PS4SYS_CRC[DC9D6197]_PS4UPDATE.PUP`, usando los offsets y tamaños del manifest `analysis/pup_13.52_manifest.json`. El PUP analizado conserva SHA-256 `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11` y tamaño `503310848` bytes.

El resultado fue vacío para todos los literales buscados (`libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, `eboot.bin`, `WebProcess`, `JSCell`, `MarkedVector` y `CloneSerializer`) tanto en `PS4UPDATE1.PUP` (offset 1024, tamaño 326026951) como en `PS4UPDATE2.PUP` (offset 326028288, tamaño 177282367). El informe reproducible es `webkit-kit/runtime/PUP_1352_LITERAL_SCAN_SESSION73.json`, SHA-256 `076845acf9d2a88cc9eda49fd9728cf9c7967b08a8b1ee5695bbbef7560371e1`.

Interpretación: el escaneo no demuestra que el WebKit no exista; sólo demuestra que esos nombres no aparecen como ASCII literal en los dos rangos analizados en esta capa del contenedor. El manifest sigue clasificando el contenido interno como `ABSENT_UNTIL_DECRYPTED`, por lo que no se debe tratar este resultado como una extracción negativa del módulo.
