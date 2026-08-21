# Auditoría GitHub: herramientas PUP/SLB2/PS4

## Resumen

Las fuentes públicas revisadas se dividen en tres grupos: unpackers que requieren un PUP ya descifrado, herramientas nuevas que extraen parte del contenedor pero reconocen que no pueden completar AES sin claves de Sony, y payloads que invocan la capacidad de descifrado del kernel de una PS4.

| Proyecto | Alcance declarado | Entrada requerida | ¿Entrega WebKit 13.52? |
|---|---|---|---|
| `Zer0xFF/ps4-pup-unpacker` | Desempaqueta blobs previamente descifrados | PUP descifrado | No |
| `idc/ps4-pup_unpack` | Desempaqueta blobs previamente descifrados | PUP descifrado | No |
| `seregonwar/PFU-PupFileUnpacker` | Extrae/analiza PUP y metadata; reconoce limitación AES | PUP y claves/soporte criptográfico | No demostrado |
| `andy-man/ps4-pup-decrypt` | Payload para usar el kernel de PS4 y descifrar PUP | PS4 vulnerable/compatible y payload | No; README probado hasta 11.05 |
| `SocraticBliss/ps4_dec_pup_info` | Lee metadata de `PUP.dec` | PUP ya descifrado | No |

## Hallazgos clave

`Zer0xFF/ps4-pup-unpacker` e `idc/ps4-pup_unpack` declaran explícitamente que no descifran y que requieren un PUP previamente descifrado. También indican que no desempaquetan sistemas de archivos anidados.

`PFU-PupFileUnpacker` ofrece una extracción parcial y documentación de metadata, pero su propio README reconoce que no puede completar correctamente la extracción de archivos cifrados sin las claves de Sony. Su estado no prueba soporte 13.52.

`andy-man/ps4-pup-decrypt` no es un descifrador offline: es un payload que pide a una PS4 que descifre el update mediante capacidades del kernel. El README indica como última versión probada 11.05 y condiciones de producto/firmware. No se ejecutó ni se intentó adaptar.

## Conclusión

No apareció en GitHub una herramienta offline pública que convierta nuestro PUP 13.52 protegido en `PUP.dec` y luego extraiga `libSceNKWebKit.sprx`. La vía de payload queda fuera de esta auditoría; las herramientas de Linux/Windows disponibles sólo procesan metadata, SLB2 o imágenes ya descifradas.

Fuentes:

- https://github.com/Zer0xFF/ps4-pup-unpacker
- https://github.com/idc/ps4-pup_unpack
- https://github.com/seregonwar/PFU-PupFileUnpacker
- https://github.com/andy-man/ps4-pup-decrypt
- https://www.psxhax.com/threads/ps4_dec_pup_info-py-script-for-ps4-decrypted-pup-info-by-socraticbliss.8158/
