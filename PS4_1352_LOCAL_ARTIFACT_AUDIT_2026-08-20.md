# Auditoría local de artefactos PS4 13.52

**Commit de partida:** `831303f03132664d2281093651affd2d32f03fb0`  
**Método:** lectura de blobs Git, hashes, cabeceras, strings, entropía y metadata de contenedores. No se ejecutó ningún binario, payload, PUP, ISO ni módulo propietario.

## Hallazgo nuevo principal

La auditoría anterior había buscado nombres de módulos, pero el checkout sparse ocultaba varios blobs binarios versionados en la raíz del repositorio. Se confirmó que existen bytes Git de `libkernel_sys_13.52.bin` y tres dumps `lk_dump*.bin`. Esto corrige el estado anterior de disponibilidad: los bytes del kernel/sys están presentes en el objeto Git, aunque **no son WebKit** y su procedencia retail 13.52 no queda demostrada únicamente por el nombre.

| Archivo | Tamaño | SHA-256 | Observación estática | Clasificación |
|---|---:|---|---|---|
| `libkernel_sys_13.52.bin` | 479.232 | `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c` | Raw data; sin magic ELF/SELF; no Build ID | **DIRECT_BYTES**; procedencia 13.52 = **VERIFIED_METADATA**, no WebKit |
| `lk_dump1.bin` | 159.744 | `d4a9a642f85446785469750532d9353c9010ebec4373b8e9c4c06d594536da57` | Raw data; sin magic ELF/SELF | **DIRECT_BYTES**; identidad/procedencia = **UNVERIFIED** |
| `lk_dump2.bin` | 159.744 | `e044d0e5303596df94f86190d34bee6dda8e87f9a51578d067e8d1650ca15e8d` | Raw data; sin magic ELF/SELF; contiene string `...libkernel...thr_umtx.c` | **DIRECT_BYTES**; identidad/procedencia = **UNVERIFIED** |
| `lk_dump3.bin` | 159.744 | `e31dd16ddc488851c98bc1782cfe919ece1cab2c141bd0ef7c8a9ef82fb9fdf2` | Raw data; sin magic ELF/SELF; baja entropía | **DIRECT_BYTES**; identidad/procedencia = **UNVERIFIED** |
| `hen.bin` | 499.680 | `32570b6e54c9531dc8a7d75ef4da6557d440bf69c4b765a85a77d428db3a4b73` | DOS/COM según `file`; strings de payload y módulos genéricos | **DIRECT_BYTES**, pero procedencia confirmada 13.04; no evidencia 13.52 |
| `scanner_1304.iso` | 16.777.216 | `6ed15acd9cfb2539e034cde72a9003f52cf6338f04549670e1b8d515d948bd30` | ISO/UDF `scanner_1304`; contiene `GOLDHEN.BIN` y estructura BDMV | **DIRECT_BYTES**, pero scanner identificado como 13.04 |

## Módulos WebKit retail objetivo

No se encontró ningún blob con bytes de `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, `eboot.bin`, SELF WebKit, WebProcess WebKit, NXDP, ORBISDMP u `orbisstate`. Los strings de `hen.bin` mencionan `libkernel_web.sprx`, `libkernel_sys.sprx` y `libSceLibcInternal.sprx`, pero eso es una referencia textual dentro de un binario de 13.04; no contiene esos módulos como archivos separados ni demuestra su identidad 13.52.

## PUP y contenedores

El manifest local versionado `analysis/pup_13.52_manifest.json` aporta **VERIFIED_METADATA** para un PUP oficial de Sony: tamaño declarado 503.310.848 bytes, contenedor SLB2, SHA-256 `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11`, y dos entradas internas con hashes. Sin embargo, las rutas históricas `/home/ubuntu/ps4-lab-1352/pup/PS4UPDATE.PUP`, sus ranges y fragments están ausentes en el sandbox actual. El propio manifest indica que no se realizó descifrado y que no confirma ningún módulo WebKit.

El ISO local `scanner_1304.iso` fue listado mediante parser ISO9660 estático sin montaje. Tiene volumen `scanner_1304` y 35 entradas; incluye `/GOLDHEN.BIN;1` de 286.336 bytes y contenido BD-J/BDMV, pero su commit de introducción lo identifica como scanner PS4 13.04. Se descarta como evidencia de la build retail 13.52.

## Procedencia y límites

El historial Git identifica `hen.bin` como “compiled ps4-hen for FW 13.04” y `scanner_1304.iso` como “PS4 SUID Scanner for FW 13.04 - BD-JB based”. Por ello, ambos son **DIRECT_BYTES** de artefactos históricos, pero no pueden elevarse a evidencia PS4 13.52 ni a evidencia WebKit. Los dumps de kernel sí son bytes reales versionados; no tienen formato ELF/SELF, Build ID, imports/exports ni correlación con `libSceNKWebKit.sprx`.

La cadena interna `W:\Build\J02697906\sys\internal\usermode\src\libkernel\pthread\src\thread\thr_umtx.c` observada en `lk_dump2.bin` es una pista estructural de origen de compilación, clasificada **STRUCTURAL**, no una prueba de firmware ni de WebKit.

## Porcentajes actualizados

| Métrica | Porcentaje | Base de cálculo |
|---|---:|---|
| Infraestructura estática | **90%** | Scanner de nombres, analizador de blobs, parser ISO, manifests, hashes y reportes; falta probar el flujo con módulos WebKit retail reales |
| Evidencia directa de WebKit retail PS4 13.52 | **0%** | 0 módulos objetivo (`libSceNKWebKit`, `libkernel_web`, `libSceLibcInternal`, WebProcess o SELF/eboot) presentes |
| Evidencia directa de bytes PS4 no-WebKit | **100%** para los blobs enumerados | Los seis blobs históricos tienen bytes Git y SHA-256 reproducibles |
| Evidencia estructural/documental 13.52 | **35%** | Metadata PUP, nomenclatura, fuentes cercanas y pistas kernel; sin correlación binaria WebKit 13.52 |

Estos porcentajes no convierten el kernel ni los artefactos 13.04 en evidencia WebKit. WPE 2.52.6 continúa siendo exclusivamente **PORTABLE**/laboratorio.

## Siguiente bloqueo de mayor valor

El siguiente artefacto de mayor valor sigue siendo el PUP oficial 13.52 completo en la ruta indicada por su manifest, o un bundle legítimo que contenga `libSceNKWebKit.sprx` y `libkernel_web.sprx` de la misma build. Con el PUP presente, el siguiente paso seguro sería ejecutar únicamente `parse_slb2_static.py` para verificar contenedor y ranges; no se debe descifrar ni ejecutar contenido sin una fuente autorizada y una tarea explícita distinta.

## Comandos reproducibles

```sh
python3 webkit-kit/tools/analyze_ps4_1352_blob.py \
  /tmp/extracted/libkernel_sys_13.52.bin \
  /tmp/extracted/lk_dump1.bin \
  /tmp/extracted/lk_dump2.bin \
  /tmp/extracted/lk_dump3.bin \
  --output ps4-1352-static-blob-analysis.json

python3 webkit-kit/tools/list_iso9660_static.py \
  /tmp/extracted/scanner_1304.iso \
  --output scanner_1304-iso-list.json
```

## Referencias

[1]: <https://pc.ps4.update.playstation.net/update/ps4/image/2026_0611/sys_2ce20d9fbb48274ceb369b40412e616c/PS4UPDATE.PUP> "Sony PS4 official update URL recorded in local manifest"  
[2]: <https://www.playstation.com/en-us/oss/ps4/webkit/> "Sony PlayStation 4 WebKit OSS"  
[3]: <https://github.com/kmeps4/PSFree/blob/main/send.mjs> "PSFree send.mjs"
