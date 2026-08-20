# Fuente legítima para artefactos retail PS4 13.52

**Alcance:** localizar una fuente autorizada para obtener posteriormente `libSceNKWebKit.sprx` y `libkernel_web.sprx`. No se repitieron auditorías de `lk_dump*`, `libkernel_sys`, Git/reflogs ni búsquedas generales de esos módulos. No se descargó ni ejecutó ningún binario, payload o exploit.

## Candidato principal: PUP oficial de Sony

La mejor fuente legítima identificada es el enlace directo de actualización publicado por Sony/PlayStation y registrado en el manifest local de 13.52:

```text
https://pc.ps4.update.playstation.net/update/ps4/image/2026_0611/sys_2ce20d9fbb48274ceb369b40412e616c/PS4UPDATE.PUP
```

La página oficial de soporte de Sony instruye a descargar el archivo de actualización desde el botón oficial, guardarlo como `PS4UPDATE.PUP` dentro de `PS4/UPDATE` y usarlo mediante el procedimiento de actualización por USB.[1] La misma página advierte que no se debe utilizar una fuente distinta del archivo oficial proporcionado por Sony.[1]

Se realizó únicamente una petición HTTP `HEAD` al enlace, sin descargar el cuerpo. La respuesta fue `200 OK` con estos datos:

| Campo | Valor | Clasificación |
|---|---|---|
| URL | Enlace `pc.ps4.update.playstation.net` de Sony | **VERIFIED_METADATA** |
| Estado HTTP | `200 OK` | **VERIFIED_METADATA** |
| Tamaño declarado | `503310848` bytes | **VERIFIED_METADATA** |
| Tipo declarado | `text/plain` | **VERIFIED_METADATA** |
| Accept-Ranges | `bytes` | **VERIFIED_METADATA** |
| ETag | `2ce20d9fbb48274ceb369b40412e616c:1781579172.795957` | **VERIFIED_METADATA** |
| Last-Modified | `Thu, 11 Jun 2026 11:14:05 GMT` | **VERIFIED_METADATA** |
| SHA-256 del PUP completo | `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11` | **DOCUMENTED_ONLY / VERIFIED_METADATA** |
| Formato esperado | Contenedor `SLB2`, versión 2, dos entradas | **DOCUMENTED_ONLY / VERIFIED_METADATA** |

El SHA-256 y la estructura SLB2 proceden del manifest versionado existente, no de bytes presentes actualmente en el sandbox. Por ello no se elevan a `DIRECT_BYTES` en esta sesión.

## Qué puede proporcionar el PUP

El PUP es la única fuente oficial localizada que puede contener los artefactos retail del firmware. El PUP contiene el paquete de actualización completo; Sony no publica en su página una descarga separada de `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, WebProcess, `eboot` o SELF. La página oficial de OSS sí publica fuentes WebKit para rangos anteriores y para PS4 `13.00 -` —en dos archivos `WebKit-601-1300.zip` y `WebKit-616-1300.zip`—, pero esas descargas son código fuente OSS, no módulos retail compilados de 13.52.[2]

Por tanto, el PUP es un **candidato real de contenedor**, pero todavía no es evidencia directa de los módulos objetivo. Esa evidencia solo podrá clasificarse después de disponer legalmente del PUP, verificar su SHA-256 y ejecutar sobre una copia el parser estático de SLB2 ya existente. La presencia, ruta y hash interno de los módulos WebKit deberán comprobarse posteriormente; no se debe inferirlos desde la existencia del PUP.

## Candidatos descartados o insuficientes

| Candidato | Contenido/procedencia | Versión | Estado para 13.52 |
|---|---|---|---|
| Sony PUP directo | Paquete oficial de actualización, 503 MB declarados | 13.52 según manifest y URL oficial | **MEJOR CANDIDATO; VERIFIED_METADATA**, bytes ausentes localmente |
| Sony PS4 OSS WebKit | Fuentes OSS WebKit en ZIP | 13.00 -; también 12.50-12.52 | **STRUCTURAL**, no retail 13.52 |
| `libkernel_sys_13.52.bin` y `lk_dump*` | Bytes Git ya inventariados | Etiqueta 13.52, autenticidad independiente no demostrada | **DIRECT_BYTES** de libkernel; no WebKit |
| `hen.bin` / `scanner_1304.iso` | Artefactos históricos del laboratorio | 13.04 | **DIRECT_BYTES**, no 13.52 y no fuente WebKit |
| Mirrors, foros, enlaces de terceros | No se acepta procedencia por nombre o snippet | Variable | **UNVERIFIED**; no son candidatos autorizados |

## Mejor ruta legítima

La ruta de mayor valor es que el propietario del trabajo descargue el PUP desde la URL oficial de Sony en un entorno autorizado y lo coloque fuera de Git, conservando el archivo original. Una vez disponible, el procedimiento reproducible y no ejecutable es:

```sh
curl -fL --retry 3 --output PS4UPDATE.PUP \
  'https://pc.ps4.update.playstation.net/update/ps4/image/2026_0611/sys_2ce20d9fbb48274ceb369b40412e616c/PS4UPDATE.PUP'
sha256sum PS4UPDATE.PUP
python3 webkit-kit/tools/parse_slb2_static.py \
  PS4UPDATE.PUP --json PS4UPDATE.PUP.slb2.json
```

El hash debe coincidir con `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11` antes de continuar. Si coincide, el pipeline puede documentar el contenedor y sus rangos. La extracción de módulos retail deberá mantenerse dentro de la autorización y las condiciones aplicables; no se incluye aquí ningún procedimiento de descifrado, ejecución o explotación.

## Estado final

Se encontró una **fuente oficial y verificable de contenedor**, pero no los bytes locales de `libSceNKWebKit.sprx` ni `libkernel_web.sprx`. El bloqueo actual se reduce de “no existe una fuente identificable” a “falta obtener y preservar el PUP oficial para realizar la comprobación estática del contenido”.

| Métrica | Estado |
|---|---:|
| Fuente legítima de PUP 13.52 identificada | **100%** |
| Bytes PUP 13.52 presentes en el sandbox | **0%** |
| Bytes directos de `libSceNKWebKit.sprx` | **0%** |
| Bytes directos de `libkernel_web.sprx` | **0%** |
| Ruta OSS WebKit documental | **100%**, pero solo estructural/portable |

## Referencias

[1]: <https://www.playstation.com/en-us/support/hardware/ps4/system-software/> "Sony: How to update system software on a PS4 console"  
[2]: <https://www.playstation.com/en-us/oss/ps4/webkit/> "Sony: WebKit source code for PS4 system software versions"  
[3]: <https://pc.ps4.update.playstation.net/update/ps4/image/2026_0611/sys_2ce20d9fbb48274ceb369b40412e616c/PS4UPDATE.PUP> "Sony official PS4UPDATE.PUP endpoint"
