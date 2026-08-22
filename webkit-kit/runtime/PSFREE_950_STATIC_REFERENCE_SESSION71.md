# Referencia estática PSFree PS4 9.50 — sesión 71

## Fuente

- Repositorio: `xxKawa/xxkawa.github.io`
- Archivo: `psfree/rop/ps4/950.mjs`
- Commit: `fa0db413dd020ae3cbea999276d554e3775535d6`
- URL: https://github.com/xxKawa/xxkawa.github.io/blob/fa0db413dd020ae3cbea999276d554e3775535d6/psfree/rop/ps4/950.mjs
- Longitud declarada: 280 líneas
- Estado: leído como texto; no ejecutado.

## Observaciones estáticas

El archivo agrupa explícitamente los firmwares `9.50, 9.51, 9.60` y declara bases para `libSceNKWebKit.sprx`, `libkernel_web.sprx` y `libSceLibcInternal.sprx`. Incluye offsets de imports de WebKit (`stack_chk_fail`, `strlen`), cálculo de bases mediante una `textarea` y una vtable de WebCore, además de una tabla de gadgets JOP/ROP dependiente de esa versión. El comentario funcional sitúa la llamada en el getter nativo `scrollLeft` y utiliza estructuras internas de un objeto `textarea`.

La referencia es valiosa para establecer que PSFree tenía una correlación explícita entre un WebKit PS4 identificado por rango de firmware y las bibliotecas `libSceNKWebKit`/`libkernel_web`. También muestra que los offsets son específicos de la familia 9.50–9.60 y no deben trasladarse a 13.52.

## Clasificación

- Existencia pública del archivo y su rango 9.50–9.60: `DIRECT_HISTORICAL`.
- Evidencia de que la cadena usa WebKit y `libkernel_web` en ese rango: `DIRECT_HISTORICAL`.
- Evidencia de equivalencia estructural con PS4 13.52: `UNVERIFIED`.
- Evidencia de que los offsets sirvan para 13.52: `DISCARDED`.
- Utilidad para el diferencial futuro: alta; permite comparar nombres de imports, forma de localizar bases y organización de módulos cuando aparezca un artefacto 13.52.

## Límite de seguridad y alcance

El archivo contiene una cadena de explotación y offsets operativos. Este informe registra únicamente metadatos y relaciones estructurales; no reproduce la cadena, no calcula offsets nuevos, no ejecuta el módulo y no lo adapta a firmware posterior. La fuente no contiene `libSceNKWebKit.sprx` ni `libkernel_web.sprx` binarios.

## Conclusión

Sí aporta una referencia histórica concreta de la interfaz WebKit/`libkernel_web` de PS4 9.50–9.60, pero no resuelve la presencia ni el estado de `CSSFontFace`, `MarkedVector`, `CloneDeserializer` o `JSCell::toX` en 13.52. El siguiente uso legítimo es como plantilla de nombres y organización para comparar un módulo retail posterior, no como fuente de offsets o explotación.
