# Verificación de reconstrucción de partes PUP

La rama privada `pup-byte-manifest-1350-1352` contiene 52 partes de 20.000.000 bytes de las dos imágenes PS4SYS. Se reconstruyeron localmente mediante concatenación lexicográfica.

```bash
cat artifacts/pup_chunks_1350_1352/PS4SYS_1350.part-* > /tmp/PS4SYS_13.50.rebuilt.PUP
cat artifacts/pup_chunks_1350_1352/PS4SYS_1352.part-* > /tmp/PS4SYS_13.52.rebuilt.PUP
sha256sum /tmp/PS4SYS_13.50.rebuilt.PUP /tmp/PS4SYS_13.52.rebuilt.PUP
```

Resultado observado:

| Imagen reconstruida | Tamaño | SHA-256 observado | Estado |
|---|---:|---|---|
| 13.50 | 503293952 bytes | `04585405bf3ad0836103c1eea5c21657327a377824ad5cda7674ecb94f03822f` | Coincide |
| 13.52 | 503310848 bytes | `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11` | Coincide |

La reconstrucción se realizó sólo para validar integridad. No se descifró ni ejecutó ningún contenido.
