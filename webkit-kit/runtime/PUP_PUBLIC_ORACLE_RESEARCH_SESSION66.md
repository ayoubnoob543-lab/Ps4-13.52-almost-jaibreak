# Investigación pública sobre oracle/interpretación PUP — sesión 66

## Alcance

Investigación pasiva de fuentes públicas; no se ejecutaron payloads, binarios, exploits ni acciones contra hardware. No se descargaron PUPs ni se intentó descifrado no autorizado.

## Evidencia pública

1. **PS4 Developer wiki, página PUP** — https://www.psdevwiki.com/ps4/PUP. La página describe que los fragmentos `PS4UPDATE#.PUP` tienen una cabecera visible de 0x10 bytes y que el resto de la cabecera, la tabla de segmentos y la metadata permanecen cifrados en los archivos raw. También describe `ScePupSegmentHeader` de 0x20 bytes y `ScePupMetadataEntry` de 0x50 bytes. La propia página afirma que la sección de segmentos puede observarse usando el sistema como oracle para descifrar PUPs. Clasificación: `DOCUMENTED_ONLY` para la existencia del método; no demuestra acceso offline ni compatibilidad concreta con 13.52.

2. **andy-man/ps4-pup-decrypt** — https://github.com/andy-man/ps4-pup-decrypt. El README declara que es un payload que invoca el kernel de PS4 para descifrar un PUP y producir `PS4UPDATE1.PUP.dec` y otros fragmentos. Declara que sólo descifra actualizaciones compatibles con la versión instalada y que el sistema rechaza, en general, versiones anteriores o productos distintos. Clasificación: `HISTORICAL_ONLY`/`DOCUMENTED_ONLY`; no es un oracle offline y su uso contra hardware no forma parte de esta sesión.

3. **idc/ps4_pup_decrypt** — https://github.com/idc/ps4-pup_decrypt. El README describe la misma arquitectura: utilidad para invocar el kernel de PS4, con salida de fragmentos `.dec`, y restricciones por versión instalada y product code. Clasificación: `HISTORICAL_ONLY`; no prueba que el método funcione en 13.52 ni ofrece una clave estática.

4. **PSXHAX / ps4_dec_pup_info.py** — https://www.psxhax.com/threads/ps4_dec_pup_info-py-script-for-ps4-decrypted-pup-info-by-socraticbliss.8158/. El artículo presenta un parser para PUP ya descifrado. El código requiere explícitamente `PS4UPDATE#.PUP.dec`, interpreta cabecera y blobs, y no contiene una rutina de descifrado. Clasificación: `DOCUMENTED_ONLY`; confirma la separación entre descifrado y desempaquetado, no un camino para descifrar bytes raw offline.

## Conclusión provisional

Las fuentes públicas corroboran el bloqueo ya registrado: el material raw permite observar la cabecera inicial y realizar análisis estructural, pero la tabla de segmentos, la metadata y los recursos internos requieren una etapa de descifrado asociada al sistema/oracle. Las herramientas públicas encontradas son parsers o payloads diseñados para invocar el kernel de una PS4; no constituyen una clave, especificación completa ni método offline demostrado para 13.52.

## Relevancia para el respaldo local

La coincidencia estructural de `3 × 0x50 = 240` bytes en el respaldo es compatible con el tamaño público de una entrada de metadata, pero no prueba la semántica del bloque ni permite extraer claves. No se debe tratar una coincidencia de tamaño como evidencia de `libSceNKWebKit`, offsets WebKit o una primitive de memoria.

## Siguiente dato decisivo

El mínimo dato nuevo sería una cabecera extendida/tabla de segmentos legítimamente descifrada de una entrada PS4 compatible, o una especificación pública adicional que describa la transformación sin depender del servicio del sistema. Sin ello, cambiar nombres, probar offsets arbitrarios o correlacionar entropía con WebKit produciría falsos positivos.

## Correlación local de las tres familias

Se ejecutó `webkit-kit/tools/correlate_three_families.py` sobre el árbol fuente local `webkit-kit` con configuración `webkit-kit/three_family_signatures.json`. El resultado reproducible tiene SHA-256 `6f62b79396acde3e0e4904c7003903016c7241a9577d9cae0d7fef4de3da498c`.

| Familia | Resultado estructural | Estado de vulnerabilidad | Estado 13.52 |
|---|---|---|---|
| `jscell_tox_type_validation` | `NO MATCH` | `UNVERIFIED` | `UNVERIFIED` |
| `markedvector_gc_containers` | `NO MATCH` | `UNVERIFIED` | `UNVERIFIED` |
| `clone_object_pool_alignment` | `NO MATCH` | `UNVERIFIED` | `UNVERIFIED` |

El correlador procesó 12 archivos de código del kit homebrew/WPE. La ausencia de coincidencias sólo demuestra que esos archivos no contienen las implementaciones upstream buscadas; no demuestra que las familias estén ausentes del WebKit retail de PS4 13.52. El propio resultado marca la procedencia como `UNVERIFIED`, por lo que el árbol OSS/WPE no puede sustituir a `libSceNKWebKit.sprx`.

## Integridad de publicación

El informe y el JSON del correlador se publicaron en la rama privada `pup-byte-manifest-1350-1352`. La versión final del informe quedó en el commit `e3f4cb01fa164c3e4638c1bc189d717daf167d1c`; la consulta directa de la referencia remota confirmó ese mismo SHA-1 y el árbol local no contiene cambios pendientes. El `origin/*` local tenía un rastreo obsoleto durante la primera comprobación, por lo que la verificación final se hizo contra `git ls-remote`, no contra ese caché local.
