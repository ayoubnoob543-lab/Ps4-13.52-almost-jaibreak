# Inventario reproducible de artefactos PS4 13.52

**Fecha:** 2026-08-20  
**Rama:** `webkit-ps4-1352-kit`  
**Clasificación:** inventario estático; no carga ni ejecuta módulos propietarios.

## Resultado nuevo

Se ejecutó `tools/inventory_ps4_1352_artifacts.py` sobre el repositorio, `/home/ubuntu/Downloads` y `/tmp`, excluyendo montajes FUSE. El resultado JSON asociado registra una ausencia negativa reproducible: no apareció ningún archivo candidato con nombre `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, `eboot.bin`, `.sprx`, `.self`, `.nxdp`, `.orbsdmp`, `.dmp` u `orbisstate` en esas rutas.

| Artefacto | Resultado | Clasificación | Evidencia |
|---|---|---|---|
| `libSceNKWebKit.sprx` | No encontrado | **MISSING / UNVERIFIED** | Inventario de rutas permitido |
| `libkernel_web.sprx` | No encontrado | **MISSING / UNVERIFIED** | Inventario de rutas permitido |
| `libSceLibcInternal.sprx` | No encontrado | **MISSING / UNVERIFIED** | Inventario de rutas permitido |
| `eboot.bin` | No encontrado | **MISSING / UNVERIFIED** | Inventario de rutas permitido |
| NXDP/ORBISDMP/orbisstate | No encontrado | **MISSING / UNVERIFIED** | Inventario de extensiones/nombres |
| `libkernel_sys_13.52.bin` | No existe como blob en el árbol remoto actual | **VERIFIED_METADATA** | Solo existe `libkernel_sys_13.52.signatures.json`; no se puede elevar a `DIRECT_BYTES` |
| `libkernel_sys_13.52.signatures.json` | Presente como JSON versionado | **DIRECT_BYTES** del archivo de metadata | Blob Git de 22.138 bytes; no es un módulo retail |
| Fuente Sony WebKit 13.00 family | Referencia pública | **STRUCTURAL** | No es fuente exacta 13.52 |
| WPE WebKit 2.52.6 | Runtime Linux probado | **PORTABLE** | Laboratorio, no equivalencia PS4 |

## Contradicción resuelta

La documentación histórica del kit describía `libkernel_sys_13.52.bin` como blob disponible y le atribuía el SHA-256 `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c`. La inspección del árbol remoto actual (`git ls-tree -r origin/webkit-ps4-1352-kit`) no encuentra ese path ni un blob binario correspondiente; únicamente aparece `libkernel_sys_13.52.signatures.json`. Por tanto, el estado correcto para los bytes es **UNVERIFIED/MISSING** y el hash histórico queda como metadata no reproducible desde el checkout actual. Esta corrección evita presentar signatures o documentación como bytes ejecutables.

## Comandos reproducibles

```sh
python3 webkit-kit/tools/inventory_ps4_1352_artifacts.py \
  --root /home/ubuntu/wpe-private-repo \
  --root /home/ubuntu/Downloads \
  --root /tmp \
  --output /tmp/ps4-1352-artifact-inventory.json

git ls-tree -r --name-only origin/webkit-ps4-1352-kit \
  | grep -Ei 'libkernel.*13[._-]?52|13[._-]?52.*libkernel|\\.(sprx|self|dmp|nxdp|orbsdmp)$'
```

El scanner solo enumera nombres, tamaños y SHA-256. No invoca un loader, no parsea ni ejecuta ELF/SELF/SPRX y no procesa payloads.

## Estado específico de 13.52

Los nombres de módulos y la existencia conceptual del entorno WebKit están documentados públicamente, pero faltan los bytes de una misma instalación 13.52, sus Build IDs, imports/exports, segmentos, dumps y un `eboot/SELF` correlacionado. La fuente OSS pública cercana de Sony corresponde a la familia 13.00 y permanece **STRUCTURAL**, no una identidad 13.52. El análisis CSSFontFace publicado en `PS4_1352_EVIDENCE_DELTA_2026-08-20.md` ya distingue el rango documentado del exploit implementado; no se repite aquí.

## Referencias

[1]: <https://www.playstation.com/en-us/oss/ps4/webkit/> "Sony PlayStation 4 WebKit OSS"  
[2]: <https://github.com/kmeps4/PSFree/blob/main/send.mjs> "PSFree send.mjs"  
[3]: <https://github.com/ntfargo/CSSFontFace-Exploit> "CSSFontFace Exploit README"
