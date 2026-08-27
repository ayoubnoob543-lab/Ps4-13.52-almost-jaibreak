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
