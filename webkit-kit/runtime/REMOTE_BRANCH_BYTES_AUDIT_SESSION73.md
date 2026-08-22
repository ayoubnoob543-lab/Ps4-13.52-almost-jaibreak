# Auditoría de ramas con bytes — Sesión 73

## Pregunta

Se comprobó si alguna rama del repositorio `ayoubnoob543-lab/firmware-lab` contiene todos los bytes necesarios para analizar el WebKit retail de PS4 13.52.

## Ramas remotas

Las ramas visibles son `main`, `ps4-13.52-build`, `pup-byte-manifest-1350-1352` y `webkit-ps4-1352-kit`.

La rama relevante es `ps4-13.52-build`. Su commit punta es `17ffee3ea1bd035dbfd77c20fc57e0bf2a535f6a`, con fecha `2026-08-21T18:38:16+00:00` y mensaje `analysis: compare PUP metadata transformation`. Contiene 515 archivos rastreados.

## Blobs binarios/candidatos encontrados en `ps4-13.52-build`

| Ruta en la rama | Tamaño | SHA-256 calculado desde el objeto Git | Interpretación |
|---|---:|---|---|
| `hen.bin` | 499,680 bytes | `32570b6e54c9531dc8a7d75ef4da6557d440bf69c4b765a85a77d428db3a4b73` | Payload/binario histórico; no es WebKit retail |
| `libkernel_sys_13.52.bin` | 479,232 bytes | `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c` | Blob identificado como `libkernel_sys`; no es `libSceNKWebKit` |
| `lk_dump1.bin` | 159,744 bytes | `d4a9a642f85446785469750532d9353c9010ebec4373b8e9c4c06d594536da57` | Fragmento de libkernel; apoyo del blob combinado |
| `lk_dump2.bin` | 159,744 bytes | `e044d0e5303596df94f86190d34bee6dda8e87f9a51578d067e8d1650ca15e8d` | Fragmento de libkernel; apoyo del blob combinado |
| `lk_dump3.bin` | 159,744 bytes | `e31dd16ddc488851c98bc1782cfe919ece1cab2c141bd0ef7c8a9ef82fb9fdf2` | Fragmento de libkernel; apoyo del blob combinado |
| `scanner_1304.iso` | 16,777,216 bytes | `6ed15acd9cfb2539e034cde72a9003f52cf6338f04549670e1b8d515d948bd30` | ISO histórica etiquetada 13.04; no es WebKit 13.52 |
| `analysis/webkit_modules_1352_audit.txt` | 1,210,985 bytes | `f1dccce37738cd691ddcf2c237da76b1b4fe2cdbbecb65d0a1c5eb70da0e29ee` | Informe textual de auditoría; no es módulo binario |

No se encontraron blobs de tamaño igual o superior a 1 MiB aparte de `analysis/webkit_modules_1352_audit.txt` y `scanner_1304.iso`. La rama no contiene rutas que terminen en `.sprx` o `.self`, ni nombres `libSceNKWebKit.sprx` o `libkernel_web.sprx`.

## Qué sí contiene la rama

La rama contiene informes, manifests, offsets, scripts de validación, el `libkernel_sys_13.52.bin` de 479,232 bytes y sus tres fragmentos coherentes. También contiene un informe grande denominado `analysis/webkit_modules_1352_audit.txt`, pero su contenido es inventario/documentación y afirma que los módulos WebKit/libkernel_web/libc retail están ausentes; no debe confundirse con bytes del módulo.

## Conclusión

Existe una rama con **bytes reales de `libkernel_sys` y fragmentos de libkernel**, pero no existe en ella una rama con “todos los bytes” del WebKit retail 13.52. La rama `ps4-13.52-build` no aporta `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, un SELF/ELF/eboot de WebKit ni un dump NXDP/ORBISDMP equivalente. Por tanto, la evidencia de WebKit 13.52 sigue siendo `ABSENT/UNVERIFIED`.

Los blobs se inspeccionaron desde objetos Git y no se hizo checkout de la rama ni se ejecutó ningún archivo.

## Análisis estático del `libkernel_sys_13.52.bin`

Se copió el blob desde el objeto Git de `origin/ps4-13.52-build` a `/tmp` sólo para análisis. El SHA-256 volvió a ser `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c` y el tamaño `479232` bytes. La concatenación de `lk_dump1.bin`, `lk_dump2.bin` y `lk_dump3.bin` coincidió byte a byte con el blob combinado y produjo el mismo SHA-256.

`file` lo clasifica como `data`, no como ELF/SELF reconocible por la herramienta estándar. Los primeros bytes son `8d0d3ae9`; los tres fragmentos comienzan respectivamente por `8d0d3ae9`, `85280100` y `00410e10`. Esto es compatible con un blob raw fragmentado, pero no aporta por sí solo una cabecera ELF/SELF.

La búsqueda explícita de strings no encontró `libSceNKWebKit`, `libkernel_web`, `WebKit`, `JavaScriptCore`, `WebCore`, `JSCell`, `MarkedVector`, `CloneSerializer` ni `CSSFontFace`. Sí encontró strings genéricos de infraestructura Orbis/libkernel, incluidos `SCE_KERNEL_JIT_SHM_AREA`, `SCE_KERNEL_JIT_SHM_AREA2`, `_sceKernelLoadStartModule`, `SYS_dynlib_unload_prx`, `dlopen` y mensajes de TLS. El recuento combinado de términos `WebKit|JavaScriptCore|WebCore|libkernel_web|libSceNKWebKit|JIT|dynlib|mprotect|mmap` fue 4, explicado por referencias genéricas de JIT/dynlib/mmap; no hubo coincidencias WebKit/JSC.

Interpretación: el blob puede aportar contexto sobre APIs genéricas de carga dinámica, áreas de memoria JIT y libkernel, pero no identifica el módulo WebKit, sus imports/exports ni sus estructuras JSC. La presencia de `SCE_KERNEL_JIT_SHM_AREA` no demuestra una ruta de ejecución nativa desde WebKit ni un exploit; sólo es una huella de soporte genérico del sistema.
