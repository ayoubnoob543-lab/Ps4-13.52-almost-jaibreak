# Auditoría estática de ELF/BIN: FW 13.02 y FW 13.52

## Alcance

Se auditaron los artefactos descargados de las releases oficiales de `ps4-linux/ps4-linux-loader` v21.5 y v25. Las operaciones fueron lectura de bytes, hashes, identificación de formato, extracción de cabecera ELF, secciones y tabla de símbolos. No se ejecutó ningún ELF ni BIN.

## Clasificación por firmware

| Grupo | Archivos | Clasificación | Especificidad |
|---|---|---|---|
| 13.02 normal | `fw1302/payload-1302-{1gb,2gb,3gb,4gb}.elf/.bin` | Payload PS4 Linux/kexec | Sí, por etiqueta y árbol de release; el ELF contiene código del loader y su variante de kexec asociada |
| 13.02 Pro | `fw1302/payload-1302-{1gb,2gb,3gb,4gb}-pro.elf/.bin` | Payload PS4 Linux/kexec | Misma familia que normal: cada `.pro` comparte hash con su normal equivalente |
| 13.02 Baikal | `fw1302/payload-1302-{1gb,2gb,3gb,4gb}-baikal.elf/.bin` | Payload PS4 Linux/kexec | Variante southbridge/hardware; comparte hash dentro de la familia Baikal |
| 13.02 Pro-Baikal | `fw1302/payload-1302-{1gb,2gb,3gb,4gb}-pro-baikal.elf/.bin` | Payload PS4 Linux/kexec | Variante southbridge/hardware; comparte hash con Baikal equivalente |
| 13.52 v25 | `elf/linux-{32,64,128,256,512,1024,2048,3072,4096}mb.elf` | Payload unificado PS4 Linux/kexec | Específico de la release v25; selección por VRAM, no por nombre de firmware |
| 13.52 v25 | `bin/linux-{32,64,128,256,512,1024,2048,3072,4096}mb.bin` | Blob binario del payload Linux/kexec | Específico del paquete v25; selección por VRAM |

## Formato y tamaño

| Propiedad | 13.02 v21.5 | 13.52 v25 |
|---|---:|---:|
| ELF normal | 27.840 bytes | 320.936 bytes |
| ELF variante hardware | 27.848 bytes | No hay variantes separadas en el ZIP v25 |
| BIN | 21.315 bytes | 312.640 bytes |
| Arquitectura ELF | ELF64 LSB x86-64 | ELF64 LSB x86-64 |
| Enlazado | Estático, no stripped | Estático, no stripped |
| Organización | Árboles por firmware y hardware | Payload unificado por VRAM |

La diferencia de tamaño y organización demuestra que los artefactos no son intercambiables aunque compartan arquitectura ELF64. Los BIN son blobs derivados/transportables del payload; su identificación como DOS/COM por `file` no significa que sean programas DOS.

## Símbolos estáticos observados

### ELF 13.02 normal

En `payload-1302-1gb.elf` se observan, entre otros, los símbolos:

| Símbolo | Interpretación |
|---|---|
| `ps4kexec` / `ps4kexec_end` | Región o blob de kexec específico del payload |
| `kexec_load` | Enlace/entrypoint del mecanismo kexec |
| `get_syscall` | Rutina para obtener la referencia necesaria del entorno PS4 |
| `kernel_main` | Inicialización relacionada con la fase kernel/payload |
| `main` | Entrada principal del ELF |
| `syscalls.asm` | Unidad de compilación asociada a la interfaz syscall |
| `main.c` o `main-baikal.c` | Unidad de compilación que identifica la variante de hardware |

Las variantes normal/pro comparten los mismos hashes por capacidad; las variantes Baikal tienen un ELF ligeramente diferente y una unidad de compilación `main-baikal.c`.

### ELF 13.52 v25

En `linux-128mb.elf` se observan:

| Símbolo | Interpretación |
|---|---|
| `kexec_505` … `kexec_1352` | Segmentos internos de kexec para versiones canónicas distintas |
| `kexec_1352` / `kexec_1352_end` | Región interna marcada específicamente para 13.52 |
| `find_offsets_by_fw` | Selección de tabla de offsets por firmware |
| `get_kexec_blob` | Selección del blob interno correspondiente |
| `pack_kexec_args` | Preparación de argumentos del mecanismo kexec |
| `get_syscall` | Resolución de la referencia syscall del entorno PS4 |
| `get_firmware` | Detección/normalización de firmware |
| `g_firmware` | Estado global del firmware detectado |
| `kernel_main` | Inicialización del payload |
| `main` | Entrada principal |
| `syscalls.asm` / `main-aio.c` | Unidades de compilación del payload unificado |

La presencia de `kexec_1352` y de una tabla con entrada `1352` es evidencia directa de que v25 contiene código interno etiquetado para esa versión. No convierte el payload en un exploit WebKit ni demuestra una cadena de entrada funcional.

## Offsets relevantes

La fuente `linux/fw_offsets.h` de v25 define los campos `xfast_syscall`, `printf`, `kmem_alloc`, `kernel_map`, `patch1`, `patch2` y `pstate`. Las filas relevantes son:

| Firmware | xfast_syscall | printf | kmem_alloc | kernel_map | patch1 | patch2 | pstate |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 13.02 | `0x1c0` | `0x2E0450` | `0x465A50` | `0x22D1D50` | `0x465B1C` | `0x465B24` | `0x3A23D0` |
| 13.50 | `0x1c0` | `0x2E0460` | `0x465E90` | `0x22D1D50` | `0x465F5C` | `0x465F64` | `0x3A2780` |
| 13.52 | `0x1c0` | `0x2E0510` | `0x466290` | `0x22D1D50` | `0x46635C` | `0x466364` | `0x3A2B90` |

Estos campos son del loader Linux y del layout de kernel que éste espera. No son símbolos WebKit/JSC. En particular, `kernel_map`, `kmem_alloc` y `xfast_syscall` no deben utilizarse para inferir una dirección de `ffs_mountfs`, `patch_mount` o una primitive WebKit.

## Syscalls y dependencias

El payload 13.02 expone una estructura más pequeña y específica por versión/hardware. El payload v25 conserva una interfaz syscall y kexec, pero añade detección de firmware, tabla común y blobs internos para múltiples versiones, incluido 13.52.

Las dependencias comunes son arquitectura x86-64, ABI ELF estático, código de transición kexec, información de firmware y soporte de firmware gráfico. Las dependencias que cambian son los offsets del kernel, la tabla/selector de firmware, el layout de los blobs kexec y la lógica de southbridge/VRAM.

No hay símbolos WebKit en estos ELF. Tampoco hay tablas de `ArrayBuffer`, `butterfly`, vtables de WebCore, imports de `libSceNKWebKit` ni símbolos de `dlsym` de WebKit.

## Reutilización

**Reutilizable con alta confianza:** formato de archivo ELF64, lectura estática, organización conceptual del payload Linux, estructura general de kexec, extracción de firmware/EDID, idea de selección por firmware y documentación de hashes.

**Reutilizable sólo con adaptación:** código común de loader, headers, detección de firmware, selección de VRAM, empaquetado BIN/ELF y extracción de firmware. La adaptación debe usar la entrada exacta de cada firmware.

**No reutilizable automáticamente:** offsets del kernel, segmentos `kexec_*` específicos, dirección de syscall, `kernel_map`, `kmem_alloc`, `patch1`, `patch2`, `pstate`, cualquier ABI interno del kernel y cualquier inferencia hacia WebKit/Celsius.

## Conclusión

Los artefactos de 13.02 son payloads específicos etiquetados por firmware y hardware, con un ELF pequeño y símbolos de loader/kexec. Los artefactos de 13.52 son payloads unificados de mayor tamaño, con blobs internos `kexec_1302`, `kexec_1350` y `kexec_1352`, detección de firmware y tabla de offsets diferenciada. La evidencia permite afirmar especificidad del loader Linux para ambas versiones, pero no proporciona offsets ni símbolos WebKit ni prueba de una primitive WebKit/kernel.

## Referencias

[1]: https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v21.5 "PS4 Linux Loader v21.5"
[2]: https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v25 "PS4 Linux Loader v25"
[3]: https://github.com/ps4-linux/ps4-linux-loader/tree/v25/linux/fw_offsets.h "fw_offsets.h v25"
[4]: https://github.com/ps4-linux/ps4-linux-loader/commit/9acef9fbf79097a2bb39d6c9c17228198bc445cc "v25 commit"
