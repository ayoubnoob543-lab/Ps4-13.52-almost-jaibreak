# Partes privadas de PS4SYS 13.50/13.52

Esta carpeta contiene partes de 20.000.000 bytes de las dos imágenes locales `PS4SYS` usadas en el análisis. El repositorio remoto es privado.

Los archivos se reconstruyen por orden lexicográfico con `cat`. La integridad se comprueba con `webkit-kit/runtime/PUP_PARTS_MANIFEST_1350_1352.json` y con los SHA-256 de las imágenes completas publicados en los informes de runtime.

Ejemplo de reconstrucción local:

```bash
cat artifacts/pup_chunks_1350_1352/PS4SYS_1350.part-* > /tmp/PS4SYS_13.50.rebuilt.PUP
cat artifacts/pup_chunks_1350_1352/PS4SYS_1352.part-* > /tmp/PS4SYS_13.52.rebuilt.PUP
sha256sum /tmp/PS4SYS_13.50.rebuilt.PUP /tmp/PS4SYS_13.52.rebuilt.PUP
```

Los SHA-256 esperados son:

| Imagen | SHA-256 esperado |
|---|---|
| 13.50 | `04585405bf3ad0836103c1eea5c21657327a377824ad5cda7674ecb94f03822f` |
| 13.52 | `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11` |

Las partes no se han descifrado ni ejecutado. La carpeta contiene bytes de firmware del usuario y debe mantenerse privada y con acceso restringido.

## Utilidad automática

También puede usarse la herramienta reproducible:

```bash
python3 webkit-kit/tools/reconstruct_pup_parts.py \
  webkit-kit/runtime/PUP_BYTE_MANIFEST_1350_1352.json \
  artifacts/pup_chunks_1350_1352 \
  --firmware 13.50 \
  --output /tmp/PS4SYS_13.50.rebuilt.PUP

python3 webkit-kit/tools/reconstruct_pup_parts.py \
  webkit-kit/runtime/PUP_BYTE_MANIFEST_1350_1352.json \
  artifacts/pup_chunks_1350_1352 \
  --firmware 13.52 \
  --output /tmp/PS4SYS_13.52.rebuilt.PUP
```

La herramienta exige que tamaño y SHA-256 coincidan con la manifest antes de informar éxito.
