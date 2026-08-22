# Comparación estática PSFree PS4 8.00–9.60 — sesión 71

## Fuentes públicas

Repositorio: `xxKawa/xxkawa.github.io`, commit `fa0db413dd020ae3cbea999276d554e3775535d6`.

- `psfree/rop/ps4/800.mjs`: https://github.com/xxKawa/xxkawa.github.io/blob/fa0db413dd020ae3cbea999276d554e3775535d6/psfree/rop/ps4/800.mjs; rango declarado 8.00/8.01/8.03.
- `psfree/rop/ps4/900.mjs`: https://github.com/xxKawa/xxkawa.github.io/blob/fa0db413dd020ae3cbea999276d554e3775535d6/psfree/rop/ps4/900.mjs; rango declarado 9.00/9.03/9.04.
- `psfree/rop/ps4/950.mjs`: https://github.com/xxKawa/xxkawa.github.io/blob/fa0db413dd020ae3cbea999276d554e3775535d6/psfree/rop/ps4/950.mjs; rango declarado 9.50/9.51/9.60.

Los tres archivos fueron leídos como texto; no se ejecutó ningún módulo.

## Diferencias estructurales observables

Los tres archivos exponen bases separadas para `libSceNKWebKit.sprx`, `libkernel_web.sprx` y `libSceLibcInternal.sprx`. La función `get_bases()` usa un objeto DOM `textarea`, localiza una estructura WebCore y deriva la base de WebKit mediante una constante de vtable; después resuelve imports de `stack_chk_fail` y `strlen` para derivar las bases de `libkernel_web` y libc. La organización de módulos y el mecanismo de resolución de imports son una referencia histórica directa de cómo el código público relacionaba WebKit con sus bibliotecas dependientes.

El archivo 8.00 usa una ruta de redirección basada en `JSC::CustomGetterSetter` y offsets de `JSC::CustomGetterSetter`, mientras que 9.00 y 9.50 describen una ruta basada en el getter nativo `scrollLeft`, una vtable de WebCore y una cadena JOP. La diferencia demuestra cambios importantes de estructura y gadgets entre generaciones; no permite extrapolar offsets a 13.52.

Las constantes de imports `stack_chk_fail` y `strlen` son `0x8d8/0x918` en 8.00, pero `0x178/0x198` en 9.00 y 9.50. La constante usada para derivar la base de la vtable de `textarea` también cambia entre las tres familias. En 9.00 y 9.50 la forma general es similar, pero las tablas de gadgets, los desplazamientos de vtable y las constantes de derivación cambian.

## Valor para PS4 13.52

Esta comparación aporta una plantilla histórica de nombres de módulos, imports y dependencias, y demuestra que la correlación de WebKit es fuertemente específica de firmware. También sirve para comprobar que un supuesto artefacto posterior debería presentar una identidad de módulo, un esquema de imports y estructuras compatibles antes de comparar familias JSC.

No aporta `libSceNKWebKit.sprx`, `libkernel_web.sprx`, símbolos retail, Build ID ni bytes de PS4 13.52. No contiene evidencia de `CSSFontFace`, `MarkedVector`, `CloneDeserializer` o `JSCell::toX` en 13.52.

## Clasificación

- Archivos públicos y rangos 8.00–9.60: `DIRECT_HISTORICAL`.
- Relación explícita entre WebKit y `libkernel_web`: `DIRECT_HISTORICAL`.
- Cambios estructurales entre 8.00, 9.00 y 9.50: `DIRECT_HISTORICAL`.
- Equivalencia con PS4 13.52: `UNVERIFIED`.
- Transferencia de offsets o cadena operativa a 13.52: `DISCARDED`.

## Límite

Los archivos contienen código de explotación y datos operativos. Este documento registra sólo metadatos, dependencias y diferencias estructurales; no reproduce la cadena, no calcula offsets nuevos, no ejecuta código y no convierte la referencia histórica en una receta para 13.52.

## Conclusión

Las versiones antiguas de `libSceNKWebKit.sprx` y `libkernel_web.sprx` sí son útiles para construir un diferencial histórico y reconocer cambios de ABI/estructura. La comparación 8.00→9.00→9.50 muestra que los desplazamientos y las estructuras cambian incluso entre firmwares antiguos. Por eso, una versión antigua puede reducir el trabajo de análisis, pero no confirmar una primitive ni un offset en 13.52.
