# Integridad del respaldo privado PUP — sesión 66

La rama privada `pup-byte-manifest-1350-1352` contiene el respaldo binario dividido de las imágenes PS4SYS 13.50 y 13.52.

| Comprobación | Resultado |
|---|---:|
| Partes binarias encontradas | 52 |
| Punteros Git LFS detectados | 0 |
| Partes mayores de 25.000.000 bytes | 0 |
| Bytes totales de las partes | 1.006.604.800 |
| Árbol de trabajo | Limpio |

La reconstrucción y verificación SHA-256 de las dos imágenes está documentada en `PUP_CHUNK_REBUILD_VERIFICATION.md` y automatizada por `webkit-kit/tools/reconstruct_pup_parts.py`.

Este archivo sólo registra integridad del respaldo. No interpreta el contenido protegido ni implica que `libSceNKWebKit.sprx` esté identificado dentro de los PUP.
