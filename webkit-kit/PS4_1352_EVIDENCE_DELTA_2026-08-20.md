# Delta de evidencia PS4 13.52 — 2026-08-20

## Alcance y método

Se revisó el estado de `webkit-ps4-1352-kit`, sus informes y manifests, la página oficial de Sony OSS para PS4, el repositorio público `kmeps4/PSFree` y `ntfargo/CSSFontFace-Exploit`. También se ejecutó una búsqueda exacta de código público en GitHub por `libSceNKWebKit.sprx`, `libkernel_web.sprx` y referencias combinadas con `13.52`. No se descargó ni ejecutó ningún módulo propietario ni ningún payload.

## Evidencia nueva o confirmada

### 1. Límite de las fuentes OSS oficiales de Sony

La página oficial de Sony lista fuentes WebKit por rangos de firmware hasta `13.00 -` mediante `WebKit-601-1300.zip` y `WebKit-616-1300.zip`. No lista un paquete específico para 13.52. La fuente más cercana sigue siendo la familia 13.00, pero no puede tratarse como la implementación exacta de 13.52.

Fuente: <https://www.playstation.com/en-us/oss/ps4/webkit/>.

Los estados correctos son:

| Elemento | Estado |
|---|---|
| Fuente OSS PS4 13.00 | **CONFIRMED/PUBLIC** |
| Fuente OSS exacta 13.52 | **MISSING/UNVERIFIED** |
| Equivalencia 13.00→13.52 | **UNVERIFIED** |

### 2. PSFree documenta un dumper genérico, no un artefacto 13.52

`kmeps4/PSFree/send.mjs` confirma conceptualmente que, en firmwares >=6.00, el módulo del navegador se denomina `libSceNKWebKit.sprx` y que `libkernel_web.sprx` y `libSceLibcInternal.sprx` participan en el entorno del navegador. El propio archivo declara que su script corresponde a firmware 8.0x y que debe portarse a cada firmware. Además, sólo extrae `.text` y `PT_SCE_RELRO`, no el ELF completo.

Fuente: <https://github.com/kmeps4/PSFree/blob/main/send.mjs>.

Esto confirma nomenclatura y arquitectura de adquisición, pero no proporciona bytes, hashes, Build ID, GOT/imports o vtables de 13.52. Por tanto:

| Elemento | Estado |
|---|---|
| Nombres/relación de módulos | **DOCUMENTED_ONLY/CONFIRMED** |
| Bytes 13.52 | **MISSING** |
| Identidad común de build | **MISSING** |
| GOT/vtables/offsets 13.52 | **MISSING/UNVERIFIED** |

### 3. CSSFontFace separa firmware afectado de firmware explotable

El README público de `ntfargo/CSSFontFace-Exploit` declara un alcance de comportamiento CSSFontFace para PS4 `6.00-13.52`, pero limita la explotación implementada del repositorio a PS4 `6.00-11.02`. También afirma que las versiones PS4 11.5x–latest rediseñaron el manejo de propiedades CSSFontFace y que la primitiva `m_featureSettings` deja de ser utilizable por encima del rango soportado.

Fuente: <https://github.com/ntfargo/CSSFontFace-Exploit>.

La distinción correcta es:

| Afirmación | Estado |
|---|---|
| 13.52 está dentro del rango de cambios/alcance investigado | **DOCUMENTED_ONLY** |
| El exploit publicado funciona en 13.52 | **FALSE/NOT_SUPPORTED_BY_REPO** |
| Bytes retail de módulos 13.52 incluidos | **MISSING** |
| Offsets/gadgets/vtables 13.52 confirmados | **MISSING** |

### 4. Búsqueda exacta de GitHub

La búsqueda pública encontró referencias de código a los nombres de módulos en scripts, Makefiles, stubs y documentación de distintas versiones, pero no localizó un blob binario verificable ni un conjunto con identidad común 13.52. La única referencia combinada `13.52` + `libSceNKWebKit` recuperada en la búsqueda fue el propio análisis versionado del proyecto, que ya clasifica el mismo-build 13.52 como faltante.

Los resultados históricos de PSFree contienen lógica de dumpeo y referencias de firmwares anteriores; no se promovieron a artefactos 13.52.

## Artefactos locales relacionados

El repositorio conserva `libkernel_sys_13.52.bin` con SHA-256 `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c`. Este archivo es un módulo/syscall dump distinto y no sustituye a `libSceNKWebKit.sprx`, `libkernel_web.sprx` ni `libSceLibcInternal.sprx`; no permite confirmar la identidad WebKit 13.52.

El laboratorio WPE 2.52.6 continúa confirmado como runtime Linux x86_64 funcional, pero sólo sirve como laboratorio comparativo. No prueba equivalencia con WebKit retail PS4.

## Conclusión del ciclo

Este ciclo resolvió una contradicción importante: que un proyecto documente el rango `6.00-13.52` no significa que su exploit publicado soporte 13.52, y que Sony publique una fuente `13.00 -` no significa que exista fuente o binario OSS exacto 13.52. No apareció ningún artefacto nuevo con bytes verificables de los tres módulos retail ni un dump NXDP/ORBISDMP/orbisstate atribuible a la misma build.

Estados actuales:

```text
WPE_2.52.6_LINUX_RUNTIME       = CONFIRMED/PASS
PS4_OSS_WEBKIT_13.00           = CONFIRMED/PUBLIC
PS4_RETAIL_WEBKIT_13.52_BYTES  = MISSING
COMMON_BUILD_ID_13.52          = MISSING
GOT_IMPORTS_13.52              = MISSING
VTABLES_OFFSETS_13.52          = MISSING/UNVERIFIED
NXDP_ORBISDMP_13.52           = MISSING/UNVERIFIED
```

## Referencias

[1]: <https://www.playstation.com/en-us/oss/ps4/webkit/> "Sony PlayStation 4 WebKit OSS"
[2]: <https://github.com/kmeps4/PSFree/blob/main/send.mjs> "PSFree send.mjs"
[3]: <https://github.com/ntfargo/CSSFontFace-Exploit> "CSSFontFace Exploit README"
