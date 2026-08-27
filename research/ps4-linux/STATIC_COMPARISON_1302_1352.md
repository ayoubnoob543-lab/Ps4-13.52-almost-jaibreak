# Comparación estática: PS4 Linux Loader 13.02 frente a 13.52

## Alcance y fuentes

Se compararon los artefactos públicos de `ps4-linux/ps4-linux-loader`:

- `v21.5`, commit `841cd7885f06ed10ebe600842d8cb6570de6beb1`, release histórica que declara soporte hasta 13.02.
- `v25`, commit `9acef9fbf79097a2bb39d6c9c17228198bc445cc`, release titulada `PS4 13.52 support + edid fix`.

Assets conservados localmente:

- `PS4-Linux-Payloads-v21.5.zip`, SHA-256 `75739b4afcf5fd1be392b71c866b6353e3005fecd8bbaeda4a738968903603e6`.
- `PS4-Linux-Loader-v25.zip`, SHA-256 `fe64a196bf91f5447225e1b3418981fd860b221847e6fc1a92ea1fd3ac321e34`.

El análisis es estático: hashes, listados ZIP, formatos, tamaños, tablas fuente y referencias de código. No se ejecutó ningún ELF/BIN.

## Resultado ejecutivo

Los dos releases no son el mismo payload renombrado. v21.5 conserva árboles específicos por firmware y variantes de hardware; v25 reorganiza el proyecto alrededor de un loader común, detección de firmware en tiempo de ejecución y una tabla unificada de offsets. La interfaz de ejecución del payload sigue siendo ELF64 x86-64, pero los artefactos entregados cambiaron sustancialmente de tamaño y organización.

La reutilización segura se limita a conceptos, headers, formato de carga, lógica general de kexec/firmware y estructuras de detección. Los offsets de kernel y cualquier código que dependa de layout interno no deben trasladarse sin usar la entrada exacta del firmware correspondiente.

## Artefactos y formato

| Aspecto | 13.02 / v21.5 | 13.52 / v25 | Evaluación |
|---|---|---|---|
| Organización | Directorios `fw1302/` y otros por firmware | Payload unificado `bin/linux-*` y `elf/linux-*` | Requiere adaptación de empaquetado/selección |
| Variantes | Normal, `-pro`, `-baikal`, `-pro-baikal` | Unificado con detección runtime | La separación antigua no debe asumirse en v25 |
| ELF | ELF64 x86-64, estáticamente enlazado, no stripped; 27.840 bytes normal y 27.848 bytes Baikal | ELF64 x86-64, estáticamente enlazado, no stripped; 320.936 bytes | ABI de archivo compatible a nivel de arquitectura, payload interno distinto |
| BIN | 21.315 bytes por variante | 312.640 bytes por variante VRAM | No intercambiables por tamaño o layout |
| Memoria | Selección mediante variantes de payload | Selección por `linux-{VRAM}mb` y detección común | VRAM sigue siendo una dimensión reutilizable |
| Integridad | ZIP y hashes verificados | ZIP y hashes verificados | Reutilizable como proceso de auditoría |

Los nombres `1gb`, `2gb`, `3gb` y `4gb` en v21.5 conviven con variantes de southbridge/hardware. v25 utiliza capacidades de VRAM de 32 MB a 4096 MB en un formato unificado.

## Offsets y ABI interno del loader

v21.5 dispone de fuentes específicas en directorios como `linux/ps4-kexec-1302/`, `linux/ps4-kexec-1302-pro/` y variantes Baikal. v25 centraliza el código en `linux/ps4-kexec-common/` y añade `linux/fw_offsets.h` como tabla común.

La tabla de v25 declara entradas diferenciadas para 13.02, 13.50 y 13.52, y el comentario fuente indica que las versiones con entrada propia no son aliases. Los campos son `xfast_syscall`, `printf`, `kmem_alloc`, `kernel_map`, `patch1`, `patch2` y `pstate`.

| Firmware | xfast | printf | kmem_alloc | kernel_map | patch1 | patch2 | pstate |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 13.02 | `0x1c0` | `0x2E0450` | `0x465A50` | `0x22D1D50` | `0x465B1C` | `0x465B24` | `0x3A23D0` |
| 13.50 | `0x1c0` | `0x2E0460` | `0x465E90` | `0x22D1D50` | `0x465F5C` | `0x465F64` | `0x3A2780` |
| 13.52 | `0x1c0` | `0x2E0510` | `0x466290` | `0x22D1D50` | `0x46635C` | `0x466364` | `0x3A2B90` |

Estos son offsets del loader/Linux y del kernel interno usado por el mecanismo de carga. No son offsets de WebKit/JSC, no localizan `ffs_mountfs` y no prueban Celsius. El hecho de que `kernel_map` permanezca igual entre estas filas no implica que el resto del layout sea idéntico.

## Syscalls y flujo del loader

El código común v25 incluye una ruta de detección y normalización de firmware, obtiene una referencia al entrypoint de syscall del kernel y resuelve offsets mediante la entrada firmware-específica. También contiene la infraestructura de kexec y la extracción de firmware gráfico/EDID para el Linux cargado.

La diferencia importante es arquitectónica: v21.5 usa código y builds separados por firmware/hardware, mientras que v25 intenta usar un payload común y seleccionar el comportamiento mediante detección runtime. Por ello, la existencia de una misma syscall o de una misma llamada C no garantiza que sus direcciones internas sean reutilizables.

No se debe confundir esta ruta de syscalls del payload Linux con syscalls disponibles al JavaScript de WebKit. Los artefactos no proporcionan por sí mismos una primitive WebKit, una salida de sandbox ni un mecanismo de entrada.

## Dependencias

| Dependencia | 13.02 / v21.5 | 13.52 / v25 | Reutilización |
|---|---|---|---|
| Headers FreeBSD/PS4 | Copiados bajo árboles firmware-específicos | Centralizados/ampliados en el árbol común | Alta a nivel de tipos, no a nivel de offsets |
| ABI ELF | x86-64 SysV estático | x86-64 SysV estático | Alta para herramientas de inspección |
| Southbridge | Selección explícita `pro`/`baikal` | Detección y loader unificado | La lógica conceptual se reutiliza; la implementación cambia |
| Firmware GPU/EDID | Código por árbol firmware | Extracción común y EDID fix de v25 | Alta en la idea; requiere el código de la versión |
| Kernel layout | Valores específicos 1302 | Valores específicos 1352 | No trasladable |
| WebKit/JSC | No incluido en estos releases | No incluido en estos releases | Ninguno |
| PFS/UFS/Celsius | No incluido | No incluido | Ninguno |

## Qué puede reutilizarse

Puede reutilizarse de manera razonable el formato de análisis, los scripts de inventario, la convención de seleccionar payload por capacidad de memoria, las estructuras generales de firmware/ELF y la idea de una tabla por firmware. También puede reutilizarse la documentación de procedencia y el proceso de hash.

La reutilización de código fuente del loader debe hacerse desde la versión v25 para 13.52 y desde el árbol `1302` de v21.5 para 13.02. No es correcto copiar una dirección de una fila a otra ni usar un ELF de un firmware distinto sólo porque comparte arquitectura.

## Qué requiere adaptación

Requieren adaptación la tabla de offsets, la selección de payload, la detección de firmware/southbridge, la extracción de firmware GPU/EDID, el tamaño y empaquetado BIN/ELF, los puntos de entrada internos y cualquier llamada que use direcciones del kernel. También requiere adaptación cualquier integración con otro userland: estos releases esperan un mecanismo de carga previo y no implementan WebKit.

## Conclusión

La evidencia fuente permite afirmar que v25 tiene soporte de tabla específico para 13.52 y que v21.5 tiene artefactos etiquetados para 13.02. La compatibilidad estática de arquitectura es real, pero la compatibilidad funcional entre payloads no es automática. Los artefactos Linux son reutilizables como loader/payload posterior, no como primitive WebKit ni como prueba de Celsius o kernel R/W.

## Referencias

[1]: https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v21.5 "Release v21.5"
[2]: https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v25 "Release v25"
[3]: https://github.com/ps4-linux/ps4-linux-loader/commit/9acef9fbf79097a2bb39d6c9c17228198bc445cc "Commit v25"
[4]: https://github.com/ps4-linux/ps4-linux-loader/tree/v25/linux/fw_offsets.h "Tabla fw_offsets.h v25"
