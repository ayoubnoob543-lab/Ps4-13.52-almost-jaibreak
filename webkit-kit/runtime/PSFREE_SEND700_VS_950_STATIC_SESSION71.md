# Comparación estática PSFree `send.js` 7.00 frente a `950.mjs` 9.50

## Fuentes

- `GamerHack/GamerHack.github.io`, `g2all/700/send.js`, commit `e00f40ab52d965ca73ef968bf06bc0da17cad157`: https://github.com/GamerHack/GamerHack.github.io/blob/e00f40ab52d965ca73ef968bf06bc0da17cad157/g2all/700/send.js
- `xxKawa/xxkawa.github.io`, `psfree/rop/ps4/950.mjs`, commit `fa0db413dd020ae3cbea999276d554e3775535d6`: https://github.com/xxKawa/xxkawa.github.io/blob/fa0db413dd020ae3cbea999276d554e3775535d6/psfree/rop/ps4/950.mjs

Ambos archivos fueron leídos como texto y no se ejecutaron.

## Qué demuestra `send.js`

El archivo se presenta como un script de volcado para firmware 8.0x. Documenta explícitamente que puede localizar y volcar segmentos `.text` y `PT_SCE_RELRO` de `libSceNKWebKit.sprx`, `libkernel_web.sprx` y `libSceLibcInternal.sprx`, pero también advierte que sólo cubre esos segmentos y que debe portarse al firmware objetivo. Explica una relación estática importante: `libkernel_web.sprx` contiene la interfaz de syscalls utilizada por el navegador desde firmwares >= 6.00, mientras `libkernel_sys.sprx` contiene otras syscalls, como `mount`/`nmount`, y es usado por la aplicación BD-J.

El flujo documentado empieza localizando una `textarea`, leyendo la estructura WebCore y su vtable para obtener una referencia a WebKit. Después busca imports de `__stack_chk_fail` y `strlen` para resolver las bases de `libkernel_web` y libc. El archivo también describe funciones para obtener dumps de `eval()` y del getter `scrollLeft`, además de enviar los segmentos a un servidor HTTP. Esta descripción es evidencia histórica del método de adquisición usado por PSFree en 8.0x, no un procedimiento que se deba ejecutar aquí.

## Comparación con `950.mjs`

`950.mjs` agrupa 9.50/9.51/9.60 y conserva la misma organización de tres módulos: WebKit, `libkernel_web` y `libSceLibcInternal`. La relación de imports `stack_chk_fail`/`strlen` también se mantiene conceptualmente, pero los offsets y las estructuras cambian. En 9.50 el archivo declara los imports WebKit en `0x178` y `0x198`, mientras `send.js` usa para 8.0x `0x8d8` y `0x918`. La constante de derivación de la vtable y los offsets de gadgets también son distintos.

Por tanto, `send.js` es más útil que `950.mjs` para entender la **procedencia y composición** de un dump: especifica que el resultado normal no es el ELF completo, sino segmentos concretos de módulos identificados desde memoria. `950.mjs` es más útil como tabla histórica de correlación de una familia posterior. Ninguno aporta bytes 13.52.

## Relación con nuestro `libkernel_sys` 13.52

La documentación de `send.js` distingue `libkernel_sys.sprx` de `libkernel_web.sprx` y atribuye a la aplicación BD-J el uso de `libkernel_sys`. Esto hace coherente que el BIN local identificado como `libkernel_sys_13.52` no contenga necesariamente strings o símbolos de WebKit. La ausencia de `libSceNKWebKit` dentro de ese BIN no es una contradicción; confirma que hay que buscar el módulo WebKit por separado.

La fuente no permite inferir que el dump local de `libkernel_sys` proceda de ese script, porque no tenemos un log, nombre de salida, timestamp o cadena de custodia que conecte ambos artefactos.

## Clasificación

- Descripción pública de módulos y relaciones WebKit/libkernel: `DIRECT_HISTORICAL`.
- Evidencia de que el navegador usa `libkernel_web` desde >=6.00: `DIRECT_HISTORICAL`.
- Evidencia de que BD-J usa `libkernel_sys`: `DIRECT_HISTORICAL`.
- Procedencia del BIN local a partir de `send.js`: `UNVERIFIED`.
- Equivalencia con PS4 13.52: `UNVERIFIED`.
- Transferencia de offsets de 7.00/9.50 a 13.52: `DISCARDED`.

## Conclusión

Los dos enlaces sí aportan algo distinto: `send.js` explica la separación de módulos y la naturaleza parcial de los dumps, mientras `950.mjs` muestra una familia posterior con offsets y layout propios. Juntos refuerzan la conclusión de que el `libkernel_sys` 13.52 local puede ser legítimo como módulo independiente sin resolver el WebKit. Para avanzar hacia 13.52 sigue siendo necesario localizar `libSceNKWebKit.sprx` o un dump parcial equivalente con procedencia verificable.
