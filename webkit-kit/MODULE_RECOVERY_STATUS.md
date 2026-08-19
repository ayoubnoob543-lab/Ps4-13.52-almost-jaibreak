# Estado de recuperación de módulos WebKit 13.52

## Resultado

No hay en el corpus local ni en las fuentes públicas consultadas una copia verificable de:

- `libSceNKWebKit.sprx` para 13.52;
- `libkernel_web.sprx` para 13.52;
- `libSceLibcInternal.sprx` para 13.52;
- una identidad de build que vincule esos tres módulos a la misma revisión 13.52.

El repositorio sí contiene `libkernel_sys_13.52.bin`, con SHA-256 `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c`, pero ese archivo no es ninguno de los tres módulos WebKit solicitados y no permite reconstruir por sí solo sus offsets, GOT, vtables o ABI.

## Evidencia pública

La página oficial de Sony publica fuentes WebKit OSS para 12.50–12.52 y 13.00–13.04, pero no una fuente específica 13.52. El corpus `PS4OSSCode` conserva las fuentes OSS 13.00–13.04. OpenOrbis proporciona un toolchain legal de homebrew, headers y stubs, pero no el SDK propietario ni las librerías internas de WebKit de Orbis.

El PS4 Developer Wiki documenta los nombres y relaciones de módulos del navegador, además de referencias de user-agent para 13.52. Esa información es `DOCUMENTED_ONLY`: no aporta bytes, hashes de módulo, Build ID o símbolos verificables.

Algunos índices públicos mencionan módulos de otros firmwares o muestran resultados de análisis de archivos no identificados como 13.52. No se aceptan como evidencia de esta build ni se descargan automáticamente.

## Qué sería necesario para elevar la clasificación

Un módulo sólo se aceptaría como candidato 13.52 si se dispone del archivo o de un dump legalmente aportado, SHA-256, tamaño, formato SELF/SPRX, Build ID o timestamp, relación de procedencia con firmware 13.52 y, preferentemente, un segundo módulo de la misma imagen o manifest. Los offsets, símbolos, GOT y vtables sólo se marcarían como `CONFIRMED` después de analizarlos sobre esos bytes.

## Entorno de compilación

La ruta abierta reproducible disponible es: fuente WebKit OSS 13.00–13.04, OpenOrbis Toolchain commit `0a1aaf9dd4a92695538bdeb09fb056d06dd11725`, y PS4OSSCode commit `d636699770323d7968a2c37955aa513bda5f8a37`. Esto permite construir una base estructural o una aplicación homebrew de prueba, pero no una réplica ejecutable del navegador retail 13.52 sin SDK/ABI/librerías internas.

## Clasificación final

`libSceNKWebKit.sprx`: `MISSING`

`libkernel_web.sprx`: `MISSING`

`libSceLibcInternal.sprx`: `MISSING`

Identidad exacta de build 13.52: `MISSING`

Offsets/GOT/vtables verificados contra bytes: `MISSING`; las tablas existentes permanecen `STRUCTURAL/UNVERIFIED`.

Toolchain legal de homebrew: `RECOVERABLE`; toolchain/SDK retail-compatible 13.52: `MISSING`.
