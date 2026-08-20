# Análisis estático del PUP oficial PS4 13.52

**Fuente:** endpoint oficial de Sony  
**Ruta local fuera de Git:** `/home/ubuntu/ps4-1352-authorized-pup/PS4UPDATE.PUP`  
**Restricción:** no se ejecutó, descifró ni publicó el PUP; no se ejecutaron módulos, payloads ni exploits.

## Verificación del archivo

El PUP no estaba disponible localmente al inicio. Se obtuvo una única copia desde el endpoint oficial de Sony y se conservó fuera del repositorio. La verificación coincidió exactamente con la metadata documentada:

| Campo | Resultado | Clasificación |
|---|---|---|
| Tamaño | `503310848` bytes | **DIRECT_BYTES** |
| SHA-256 | `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11` | **DIRECT_BYTES** |
| ETag | `2ce20d9fbb48274ceb369b40412e616c:1781579172.795957` | **VERIFIED_METADATA** |
| Endpoint | `pc.ps4.update.playstation.net` | **VERIFIED_METADATA** |
| Formato observado | `SLB2` | **DIRECT_BYTES** |

## Parser SLB2

El parser existente confirmó un contenedor SLB2 válido:

| Campo | Resultado |
|---|---:|
| Magic | `SLB2` |
| Versión | `2` |
| Flags | `0` |
| Entradas | `2` |
| Sectores declarados | `983029` |
| Tamaño declarado | `503310848` |
| Tamaño real | `503310848` |
| Coincidencia de tamaños | **PASS** |
| Descifrado | **No realizado** |

Las entradas raw son:

| Entrada | Offset | Tamaño | SHA-256 | Estado |
|---|---:|---:|---|---|
| `PS4UPDATE1.PUP` | `1024` | `326026951` | `fd5e6c16398e628b3f258bce5f395c9fda687011a1a985d4b507928f54e6b580` | **VERIFIED_METADATA** |
| `PS4UPDATE2.PUP` | `326028288` | `177282367` | `44cd0c0e85b5912150112df99867357c3822a90f366198d11e2ec4c1e10adee7` | **VERIFIED_METADATA** |

El parser identifica el contenedor y hashea los rangos de entrada, pero no interpreta el contenido interno de las entradas. En consecuencia, los módulos retail no pueden confirmarse únicamente desde la cabecera SLB2.

## Búsqueda estática de nombres

Se escanearon las dos entradas raw por streaming, sin descifrado, buscando literalmente:

```text
libSceNKWebKit.sprx
libkernel_web.sprx
libSceLibcInternal.sprx
eboot.bin
WebProcess
JSCell
MarkedVector
CloneSerializer
```

No hubo coincidencias literales en ninguna entrada raw. Esto no prueba que los módulos no estén dentro del PUP: el resultado solo demuestra que esos nombres no aparecen en claro en los bytes de las entradas tal como están almacenados.

| Objetivo | Raw PUP | Interpretación |
|---|---|---|
| `libSceNKWebKit.sprx` | Sin coincidencia literal | **UNVERIFIED**; no ausencia demostrada |
| `libkernel_web.sprx` | Sin coincidencia literal | **UNVERIFIED**; no ausencia demostrada |
| `libSceLibcInternal.sprx` | Sin coincidencia literal | **UNVERIFIED**; no ausencia demostrada |
| `eboot.bin` | Sin coincidencia literal | **UNVERIFIED**; no ausencia demostrada |
| `WebProcess` | Sin coincidencia literal | **UNVERIFIED** |
| `JSCell` | Sin coincidencia literal | **UNVERIFIED** |
| `MarkedVector` | Sin coincidencia literal | **UNVERIFIED** |
| `CloneSerializer` | Sin coincidencia literal | **UNVERIFIED** |

## Correlación con la auditoría anterior

Los cuatro blobs anteriores (`libkernel_sys_13.52.bin` y `lk_dump1/2/3`) tampoco contienen las strings `JSCell`, `MarkedVector` o `CloneSerializer`. El `libkernel_sys` sí contiene referencias estructurales a `ShellCore`, `ShellUI` y `libSceLibcInternal.sprx`, pero no `libSceNKWebKit.sprx`, `libkernel_web.sprx` ni `WebKit`.

Por tanto, no existe una correlación estática nueva entre los candidatos de kernel anteriores y las clases de JavaScript solicitadas. El WPE 2.52.6 sigue siendo únicamente referencia **PORTABLE**; no se usa para atribuir clases o módulos al firmware PS4 13.52.

## Conclusión y límite correcto

Se consiguió una evidencia nueva y reproducible: el PUP oficial 13.52 está disponible, su tamaño y SHA-256 coinciden, y su contenedor SLB2 es estructuralmente válido. No se identificaron los módulos objetivo porque sus entradas internas no se interpretaron ni descifraron, y los nombres tampoco aparecen en claro en el raw PUP.

La clasificación actual es:

| Evidencia | Estado |
|---|---|
| PUP oficial con bytes verificables | **DIRECT_BYTES** |
| Contenedor SLB2 y dos entradas | **DIRECT_BYTES / VERIFIED_METADATA** |
| Presencia de `libSceNKWebKit.sprx` | **UNVERIFIED** |
| Presencia de `libkernel_web.sprx` | **UNVERIFIED** |
| Presencia de `libSceLibcInternal.sprx` | **UNVERIFIED** |
| Correlación JSCell/MarkedVector/CloneSerializer con PUP | **UNVERIFIED** |
| Ausencia de nombres en raw | **DIRECT_BYTES**, pero no ausencia del módulo |

No se debe afirmar que el PUP contiene o no contiene los módulos hasta disponer de un método autorizado para interpretar sus entradas internas. El PUP y cualquier fragmento grande permanecen fuera de Git.

## Porcentajes

| Métrica | Estado |
|---|---:|
| Fuente/artefacto PUP verificado | **100%** |
| Contenedor SLB2 analizado | **100%** |
| Módulos WebKit retail identificados | **0%** |
| Correlación JSCell/MarkedVector/CloneSerializer con PS4 13.52 | **0%** |
| Evidencia directa de WebKit retail 13.52 | **0%** |

## Reproducción

```sh
sha256sum /home/ubuntu/ps4-1352-authorized-pup/PS4UPDATE.PUP
python3 tools/parse_slb2_static.py \
  /home/ubuntu/ps4-1352-authorized-pup/PS4UPDATE.PUP \
  --json /home/ubuntu/ps4-1352-authorized-pup/PS4UPDATE.PUP.slb2.json
python3 webkit-kit/tools/scan_pup_static_names.py \
  /home/ubuntu/ps4-1352-authorized-pup/PS4UPDATE.PUP \
  --entries-json /home/ubuntu/ps4-1352-authorized-pup/PS4UPDATE.PUP.slb2.json \
  --output /home/ubuntu/ps4-1352-authorized-pup/PS4UPDATE.PUP.static-name-scan.json
```

## Referencias

[1]: <https://www.playstation.com/en-us/support/hardware/ps4/system-software/> "Sony PS4 system software update instructions"  
[2]: <https://www.playstation.com/en-us/oss/ps4/webkit/> "Sony PS4 WebKit OSS source archive page"  
[3]: <https://pc.ps4.update.playstation.net/update/ps4/image/2026_0611/sys_2ce20d9fbb48274ceb369b40412e616c/PS4UPDATE.PUP> "Official Sony PS4UPDATE.PUP endpoint"
