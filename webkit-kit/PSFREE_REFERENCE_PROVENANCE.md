# Procedencia de la referencia PSFree

Repositorio: https://github.com/zacke0815/ps4-9.04_webkitJB

Commit fijado: `e9046aa49b44584ef1a8bbdbc63e8a77d0709e1d`

URL solicitada originalmente: `https://github.com/zacke0815/ps4-9.04_webkitJB/blob/e9046aa49b44584ef1a8bbdbc63e8a77d0709e1d/rop/960.mjs#L69`

El árbol completo fue clonado en modo sólo lectura fuera del repositorio y se analizó textualmente. El manifiesto externo de archivos es `REFERENCE_MANIFEST.tsv` en el laboratorio de análisis; el inventario JSON publicado en este repositorio es `psfree_reference_960_inventory.json`.

La referencia contiene lógica de memoria, resolución de bases, lectura de imports y construcción de cadenas ROP/JOP para targets históricos. Es material de investigación estática. Esta rama no copia los offsets/gadgets del target 9.60 en una implementación PS4 13.52, no ejecuta sus módulos y no emite payloads.

Resumen de la auditoría: 31 archivos fuente inspeccionados, 1.103 líneas clasificadas; 178 genéricas/estructurales, 207 datos candidatos específicos de target y 718 referencias de cadena de explotación documentadas. Todas las coincidencias se etiquetan `MISSING_UNVERIFIED` para 13.52 hasta disponer de bytes y una identidad de build verificable.
