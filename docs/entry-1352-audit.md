# Auditoría de entrada PS4 13.52

## Resultado

Este repositorio no contiene una entrada HTML/JS/cache para PS4 13.52 ni una cadena pública completa que conecte una entrada 13.52 con el `installer.bin` de esta rama.

La fuente pública [Exploit Chart de ConsoleMods](https://consolemods.org/wiki/PS4:Exploit_Chart) clasifica `13.52 or higher` con Mast1c0re como userland y declara que no existe un kernel exploit público para el firmware reciente. La documentación pública de [BD-JB](https://consolemods.org/wiki/PS4:BD-JB) limita BD-JB/Henloader a PS4 `12.52 or lower`; su procedimiento usa Lapse hasta 12.02 y Poops para 12.50/12.52.

## Artefactos locales

`scanner_1304.iso` es una imagen UDF de 16 MiB que contiene clases Java BD-J, incluido `org/bdj/SuidScanner.class` y `org/bdj/payload.jar`. Su nombre, README y flujo de grabación la identifican como un artefacto de 13.04. No se ha convertido ni etiquetado como entrada 13.52.

Los únicos JavaScript del repositorio son material de referencia o incompleto:

- `jordy_stage2.js`: borrador de etapa 2 para 13.04 con TODOs explícitos.
- `webkit_gadgets_1304.js`: gadgets de referencia para 13.04.
- `webkit_gadgets_1350.js`: referencias para 13.50; indica que deben portarse mediante BinDiff y no contiene 13.52.

No existen archivos HTML/HTM/CSS, manifest de caché, IndexedDB, localStorage, service worker ni código de servidor web en el repositorio.

## Flujo que sí existe

```text
build.sh
  -> kpayload/kpayload.bin
  -> includes C de hen.ini y plugins
  -> installer/installer.bin
  -> hen.bin
```

El flujo BD-J separado es:

```text
scanner_1304.iso
  -> Blu-ray grabado
  -> BD-J
  -> org/bdj/SuidScanner
  -> pantalla y /mnt/usb0/suid_scan.txt o /mnt/usb1/suid_scan.txt
```

Este segundo flujo no demuestra una entrada 13.52 ni una carga del installer de esta rama.

## Conclusión operativa

No se crea HTML, JavaScript, caché, loader ni exploit nuevo porque no hay una implementación pública 13.52 válida en las fuentes consultadas que permita reconstruirlos sin inventar una cadena. El bloqueo que queda después del build es obtener una entrada/loader/chain 13.52 pública y compatible, o disponer de hardware y una implementación legítima que permita validar el flujo. La compilación correcta no sustituye esa evidencia.
