# Correlación estática de blobs PS4 13.52

**Base:** `919c1ff9d62eb44b0240834bc959f5657d5a72aa`  
**Método:** comparación byte a byte, búsqueda de subcadenas contiguas, hashes, entropía, strings con offsets y revisión de historial Git. No se ejecutaron binarios, payloads ni exploits.

## Resultado principal

Los tres dumps no son módulos independientes ni datos sin relación. Son fragmentos consecutivos exactos de `libkernel_sys_13.52.bin`:

```text
libkernel_sys_13.52.bin
├── offset 0       .. 159743:  lk_dump1.bin
├── offset 159744  .. 319487:  lk_dump2.bin
└── offset 319488  .. 479231:  lk_dump3.bin
```

Cada dump mide 159.744 bytes y los tres suman exactamente 479.232 bytes. La concatenación produce el mismo SHA-256 que el archivo completo:

```text
ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c  lk_dump1 + lk_dump2 + lk_dump3
ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c  libkernel_sys_13.52.bin
```

La igualdad se verificó además con `cmp`, que devolvió identidad exacta. Esto es **DIRECT_BYTES** y una relación estructural sólida entre los cuatro blobs. No demuestra por sí sola que el nombre `13.52` sea una procedencia retail independiente.

## Hashes y comparación

| Blob | Tamaño | SHA-256 | Entropía | Relación |
|---|---:|---|---:|---|
| `libkernel_sys_13.52.bin` | 479.232 | `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c` | 5,026693 | Fuente completa |
| `lk_dump1.bin` | 159.744 | `d4a9a642f85446785469750532d9353c9010ebec4373b8e9c4c06d594536da57` | 6,322598 | Prefijo exacto en offset 0 |
| `lk_dump2.bin` | 159.744 | `e044d0e5303596df94f86190d34bee6dda8e87f9a51578d067e8d1650ca15e8d` | 6,031004 | Fragmento exacto en offset 159.744 |
| `lk_dump3.bin` | 159.744 | `e31dd16ddc488851c98bc1782cfe919ece1cab2c141bd0ef7c8a9ef82fb9fdf2` | 1,226799 | Sufijo exacto en offset 319.488 |

La similitud no es una coincidencia estadística: las tres subcadenas de longitud completa aparecen una sola vez en el archivo completo, en offsets consecutivos y sin solapamiento.

## Pista `lk_dump2.bin` y libkernel

`lk_dump2.bin` contiene, en offsets relativos, las mismas cadenas que aparecen en `libkernel_sys_13.52.bin` desplazadas exactamente `159744` bytes. Entre ellas están:

```text
W:\Build\J02697906\sys\internal\usermode\src\libkernel\pthread\src\thread\thr_umtx.c
W:\Build\J02697906\sys\internal\usermode\src\libkernel\pthread\src\thread\thr_attr.c
W:\Build\J02697906\sys\internal\usermode\src\libkernel\pthread\src\thread\thr_cond.c
ShellCore
ShellUI
_orbis_rtld_entry
libkernel.sprx
libSceLibcInternal.sprx
libSceFios2.sprx
libSceFontGsm.sprx
```

La ruta interna `J02697906` es una pista **STRUCTURAL** de una familia de compilación interna de libkernel. La repetición con el desplazamiento exacto demuestra que `lk_dump2.bin` es el segundo fragmento del mismo archivo; no es una segunda muestra independiente ni un módulo WebKit.

La búsqueda textual no encontró `libSceNKWebKit`, `libkernel_web`, `WebKit`, `ORBISDMP` ni `NXDP` en ninguno de los cuatro blobs. Sí aparece `libSceLibcInternal.sprx` en el archivo completo y en el fragmento central, pero como nombre de módulo referenciado por libkernel. Eso no aporta los bytes de `libSceLibcInternal.sprx` ni demuestra una relación con WebKit.

## Procedencia Git

Los cuatro blobs fueron introducidos juntos en el commit `930e3af24294ebe405920de2b0cdfaddd4acb4e7`, con mensaje genérico `Add files via upload`, autor GitHub `Suchi96`, fecha `2026-08-11`, y fueron añadidos como cuatro archivos binarios separados. Esa carga conjunta explica por qué los dumps son fragmentos consecutivos del archivo completo, pero no aporta una firma oficial Sony, URL de PUP, Build ID, certificado, metadata SELF ni una cadena de custodia independiente.

La clasificación correcta es:

| Afirmación | Clasificación |
|---|---|
| Los cuatro archivos existen como bytes Git | **DIRECT_BYTES** |
| Los tres dumps concatenan exactamente el archivo completo | **DIRECT_BYTES** |
| El archivo contiene estructuras/textos de una familia Orbis libkernel | **STRUCTURAL** |
| El nombre y manifest lo etiquetan como 13.52 | **VERIFIED_METADATA** |
| Los bytes están autenticados independientemente como retail 13.52 | **UNVERIFIED** |
| Los bytes son `libSceNKWebKit.sprx` o `libkernel_web.sprx` | **UNVERIFIED / NO** |
| Existe una pista verificable hacia WebKit 13.52 | **NO** |

## Conclusión

El análisis sí produjo información nueva: `lk_dump1/2/3` son una partición exacta, ordenada y demostrable de `libkernel_sys_13.52.bin`. La pista de `lk_dump2.bin` no abre una vía hacia WebKit: solo confirma, de forma más fuerte, el origen común dentro de libkernel y la presencia de nombres auxiliares como `libSceLibcInternal.sprx`, `ShellCore` y `ShellUI`.

No se obtuvo ningún `libSceNKWebKit.sprx`, `libkernel_web.sprx`, WebProcess, SELF/ELF, Build ID ni metadata que correlacione WebKit con la misma build. Por tanto, la evidencia directa de WebKit retail PS4 13.52 permanece en **0%**.

## Porcentajes conservadores

| Métrica | Antes | Ahora | Motivo |
|---|---:|---:|---|
| Infraestructura estática | 90% | **95%** | Se añadió comparación contigua exacta y prueba de concatenación reproducible |
| Evidencia directa de WebKit retail 13.52 | 0% | **0%** | Ningún módulo WebKit objetivo está presente |
| Evidencia directa de bytes libkernel/dumps | 100% de blobs inventariados | **100%** | Hashes y relación completa verificados |
| Evidencia estructural/documental 13.52 | 35% | **40%** | Se añadió relación interna J02697906, Shell y loader de libkernel; sigue sin correlación WebKit |

## Reproducción

```sh
python3 webkit-kit/tools/compare_ps4_1352_blobs.py \
  /tmp/git-blobs/libkernel_sys_13.52.bin \
  /tmp/git-blobs/lk_dump1.bin \
  /tmp/git-blobs/lk_dump2.bin \
  /tmp/git-blobs/lk_dump3.bin \
  --output ps4-1352-blob-comparison.json

cat lk_dump1.bin lk_dump2.bin lk_dump3.bin > libkernel_sys.concat.bin
sha256sum libkernel_sys.concat.bin libkernel_sys_13.52.bin
cmp libkernel_sys.concat.bin libkernel_sys_13.52.bin
```

## Referencias

[1]: <https://github.com/Suchi96/mast1c0re-13_52-test> "Repositorio público citado en la documentación local de investigación 13.52"  
[2]: <https://www.playstation.com/en-us/oss/ps4/webkit/> "Sony PlayStation 4 WebKit OSS"  
[3]: <https://github.com/kmeps4/PSFree/blob/main/send.mjs> "PSFree send.mjs"
