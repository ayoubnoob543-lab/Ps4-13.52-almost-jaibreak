# PS4 Linux Loader — correspondencia 13.02 / 13.52

## 13.02

La fuente pública es la release `v21.5` de `ps4-linux/ps4-linux-loader`, cuyo texto declara payloads “up to 13.02”. El asset descargado es `PS4-Linux-Payloads-v21.5.zip`, con SHA-256:

```text
75739b4afcf5fd1be392b71c866b6353e3005fecd8bbaeda4a738968903603e6
```

Los archivos específicamente etiquetados para 13.02 están bajo `fw1302/`:

```text
payload-1302-{1gb,2gb,3gb,4gb}.elf
payload-1302-{1gb,2gb,3gb,4gb}.bin
payload-1302-{1gb,2gb,3gb,4gb}-pro.elf
payload-1302-{1gb,2gb,3gb,4gb}-pro.bin
payload-1302-{1gb,2gb,3gb,4gb}-baikal.elf
payload-1302-{1gb,2gb,3gb,4gb}-baikal.bin
payload-1302-{1gb,2gb,3gb,4gb}-pro-baikal.elf
payload-1302-{1gb,2gb,3gb,4gb}-pro-baikal.bin
```

Cada ELF normal/pro de una misma capacidad comparte hash; los variantes Baikal/pro-Baikal comparten otro hash. Los ELF son ELF64 x86-64 estáticamente enlazados y no stripped. Los BIN son blobs identificados por `file` como DOS/COM. No se ejecutaron.

## 13.52

La fuente pública es la release `v25`, commit de release visible `9acef9fbf79097a2bb39d6c9c17228198bc445cc`, cuya descripción incluye “PS4 13.52 Support”. El asset descargado es `PS4-Linux-Loader-v25.zip`, con SHA-256:

```text
fe64a196bf91f5447225e1b3418981fd860b221847e6fc1a92ea1fd3ac321e34
```

La release v25 usa un payload unificado y no contiene una carpeta separada `fw1352`. Los archivos son:

```text
bin/linux-{32,64,128,256,512,1024,2048,3072,4096}mb.bin
elf/linux-{32,64,128,256,512,1024,2048,3072,4096}mb.elf
```

Cada BIN mide 312.640 bytes y cada ELF 320.936 bytes. Los ELF son ELF64 x86-64 estáticamente enlazados, no stripped y contienen Build ID. La correspondencia con 13.52 procede de la release v25 y su documentación, no de un nombre individual dentro del ELF.

## Interpretación

| Firmware | Artefacto | Tipo de soporte | Confianza |
|---|---|---|---|
| 13.02 | `v21.5/fw1302/*` | Payloads separados por capacidad y variante hardware | `DECLARED_SUPPORT`; formato/hash verificados, hardware no probado aquí |
| 13.52 | `v25/bin/*`, `v25/elf/*` | Payload unificado por capacidad VRAM | `DECLARED_SUPPORT`; formato/hash verificados, hardware no probado aquí |

Estos payloads presuponen que la consola ya dispone de un mecanismo autorizado para cargarlos. No son el exploit WebKit, no son Celsius/FFS y no demuestran por sí mismos kernel R/W. Los archivos se conservaron para análisis estático; no se ejecutó ningún ELF/BIN.

## Referencias

[1]: https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v21.5 "PS4 Linux Loader v21.5"
[2]: https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v25 "PS4 Linux Loader v25"
[3]: https://github.com/ps4-linux/ps4-linux-loader/commit/9acef9fbf79097a2bb39d6c9c17228198bc445cc "PS4 Linux Loader v25 commit"

## Confirmación desde el código fuente

En `linux/fw_offsets.h` del tag v25 aparecen entradas distintas para `1302`, `1350` y `1352`. La propia cabecera indica que las versiones con entrada distinta no son aliases y tienen layouts de kernel mediblemente diferentes. Estas entradas contienen `xfast_syscall`, `printf`, `kmem_alloc`, `kernel_map`, `patch1`, `patch2` y `pstate` para el loader Linux. No son offsets de WebKit, no identifican `ffs_mountfs` y no demuestran una primitive WebKit.

La tabla fuente observada es:

```text
1302 -> xfast 0x1c0, printf 0x2E0450, kmem_alloc 0x465A50, kernel_map 0x22D1D50, patch1 0x465B1C, patch2 0x465B24, pstate 0x3A23D0
1350 -> xfast 0x1c0, printf 0x2E0460, kmem_alloc 0x465E90, kernel_map 0x22D1D50, patch1 0x465F5C, patch2 0x465F64, pstate 0x3A2780
1352 -> xfast 0x1c0, printf 0x2E0510, kmem_alloc 0x466290, kernel_map 0x22D1D50, patch1 0x46635C, patch2 0x466364, pstate 0x3A2B90
```

La presencia de la entrada 1352 eleva el soporte del loader a `DIRECT_SOURCE_SUPPORT` para la tabla de offsets del loader, pero no a compatibilidad de la cadena de entrada ni a soporte de WebKit/Celsius.
