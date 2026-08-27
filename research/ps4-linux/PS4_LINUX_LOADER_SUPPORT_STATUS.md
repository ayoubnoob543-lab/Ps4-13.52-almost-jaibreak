# Estado literal del soporte declarado

Fuente principal: repositorio oficial `ps4-linux/ps4-linux-loader`.

## Release v21.5

- Tag: `v21.5`
- Commit: `841cd7885f06ed10ebe600842d8cb6570de6beb1`
- Título: `Fixes for PS4 Linux Payloads for up to 13.02`
- ZIP auditado: `PS4-Linux-Payloads-v21.5.zip`
- SHA-256 del ZIP: `75739b4afcf5fd1be392b71c866b6353e3005fecd8bbaeda4a738968903603e6`

La cabecera del README dice `FW 5.05 - 13.02`. En la tabla, 13.00 aparece como `✅`, mientras que `13.02(?)` aparece con un signo de interrogación antes del `✅`. Por tanto, la forma rigurosa de expresarlo es:

| Firmware | Texto de la release | Clasificación |
|---|---|---|
| 13.00 | `FW 13.00 ✅` | Soporte declarado sin `?` |
| 13.02 | `13.02(?) ✅` | Soporte declarado, pero incierto |

El ZIP sí contiene un directorio `fw1302/` con payloads `.elf` y `.bin`; eso verifica que existen artefactos etiquetados 1302, pero no elimina el `?` de la documentación ni prueba hardware por sí mismo.

## Release v25

- Tag: `v25`
- Commit: `9acef9fbf79097a2bb39d6c9c17228198bc445cc`
- Fecha del commit: `2026-07-25T17:24:27+02:00`
- Título: `PS4 13.52 support + edid fix`
- ZIP auditado: `PS4-Linux-Loader-v25.zip`
- SHA-256 del ZIP: `fe64a196bf91f5447225e1b3418981fd860b221847e6fc1a92ea1fd3ac321e34`

La tabla de v25 expresa:

| Firmware | Texto de la release | Clasificación |
|---|---|---|
| 13.00 | `FW 13.00 ✅` | Soporte declarado sin `?` |
| 13.02 | `FW 13.02(?)` | Soporte declarado, pero incierto |
| 13.04 | `FW 13.04(?)` | Soporte declarado, pero incierto |
| 13.50 | `FW 13.50(?)` | Soporte declarado, pero incierto |
| 13.52 | `FW 13.52(?)` | Soporte declarado, pero incierto |

Aunque el título del commit dice “13.52 support”, la tabla conserva el signo `?`. La release v25 utiliza payload unificado y no contiene una carpeta separada `fw1352`; los archivos están bajo `bin/linux-*.bin` y `elf/linux-*.elf`.

## Conclusión probatoria

El soporte oficialmente publicado para 13.02 y 13.52 debe citarse como **declarado pero incierto**, no como confirmado en hardware. Los formatos, tamaños, hashes y etiquetas de los assets están verificados. La compatibilidad efectiva de cada firmware no se ejecutó ni se valida aquí.

Este loader es una herramienta posterior para cargar Linux cuando ya existe un mecanismo de carga. No demuestra WebKit, Celsius, FFS, kernel R/W ni una ruta de entrada para ningún firmware.

## Referencias

[1]: https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v21.5 "PS4 Linux Loader v21.5"
[2]: https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v25 "PS4 Linux Loader v25"
[3]: https://github.com/ps4-linux/ps4-linux-loader/commit/9acef9fbf79097a2bb39d6c9c17228198bc445cc "PS4 Linux Loader v25 commit"
