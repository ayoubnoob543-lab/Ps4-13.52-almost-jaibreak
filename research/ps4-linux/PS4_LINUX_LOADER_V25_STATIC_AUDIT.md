# PS4 Linux Loader v25 — auditoría estática

## Fuente

- Repositorio: https://github.com/ps4-linux/ps4-linux-loader
- Release: `v25`
- Commit visible en la release: `9acef9fbf79097a2bb39d6c9c17228198bc445cc`
- Fecha de release observada: 2026-07-25
- Asset descargado: `PS4-Linux-Loader-v25.zip`
- SHA-256 del ZIP: `fe64a196bf91f5447225e1b3418981fd860b221847e6fc1a92ea1fd3ac321e34`

## Firmware

La descripción pública de v25 indica “PS4 13.52 Support”. La release anterior v24b.1 indica soporte para 13.04 y 13.50. La release v23/v21.5 declara soporte hasta 13.02, pero marca 13.02 con `?` en la tabla pública. Estas etiquetas prueban el alcance declarado del loader, no una validación independiente del exploit de entrada ni del kernel exploit.

No se ejecutaron los payloads. El análisis se limitó a descarga, hash, listado ZIP, identificación de formato y strings simples.

## Contenido

El ZIP contiene nueve `.bin` y nueve `.elf`, diferenciados por cantidad de VRAM:

- `linux-32mb`, `64mb`, `128mb`, `256mb`, `512mb`, `1024mb`, `2048mb`, `3072mb` y `4096mb`, cada uno en `bin/` y `elf/`.
- Cada `.bin` mide 312.640 bytes.
- Cada `.elf` mide 320.936 bytes.
- Los `.bin` fueron identificados por `file` como DOS/COM; los `.elf` como ELF64 LSB x86-64, estáticamente enlazados y no stripped.
- Los ELF contienen Build ID, pero no aparecieron strings directas `13.02`, `13.04`, `13.50` o `13.52` en el escaneo simple realizado.

## Correspondencia

| Firmware | Artefacto | Estado |
|---|---|---|
| 13.02 | v25 unified loader/payload, según la documentación pública histórica | `DECLARED_SUPPORT`; no se ejecutó ni se verificó en hardware |
| 13.52 | v25 unified loader/payload, según la release v25 | `DECLARED_SUPPORT`; no se ejecutó ni se verificó en hardware |
| 13.04/13.50 | v24b.1 como referencia de release anterior | `DECLARED_SUPPORT` en v24b.1 |

La arquitectura v24/v25 se describe como payload unificado y firmware-agnostic en la release. Por eso el ZIP no contiene un archivo separado llamado `13.02` o `13.52`; la correspondencia se establece por la release/documentación y no por el nombre individual de cada ELF.

## Límites

Estos artefactos son payloads/loader para arrancar Linux en una consola que ya dispone del mecanismo de carga correspondiente. No son un WebKit exploit, no son una primitive de userland, no son Celsius/FFS y no demuestran por sí mismos un kernel R/W en 13.02 o 13.52.

La verificación fuerte disponible aquí es la integridad del asset, formato y contenido del archivo descargado. La compatibilidad real por firmware queda como `DECLARED_SUPPORT` hasta disponer de una matriz de pruebas autorizadas o evidencia técnica independiente.

## Archivos locales

- `PS4-Linux-Loader-v25.zip`
- `PS4-Linux-Loader-v25.zip.sha256`
- `PS4-Linux-Loader-v25.contents.txt`
- `v25_release.html`
- `v25_assets.html`
- `v25_release.json` — puede estar ausente o vacío si el API de GitHub devolvió HTTP 403.
- `v25_extracted/` — copia extraída para inspección estática.

## Referencias

[1]: https://github.com/ps4-linux/ps4-linux-loader/releases "PS4 Linux Loader releases"
[2]: https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v25 "PS4 Linux Loader v25"
[3]: https://github.com/ps4-linux/ps4-linux-loader/commit/9acef9fbf79097a2bb39d6c9c17228198bc445cc "v25 commit"
