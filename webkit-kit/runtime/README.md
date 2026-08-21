# Runtime PS4 legítimo

Este directorio no contiene un exploit, payload, jailbreak ni loader para evadir controles de seguridad. Describe únicamente el contrato de ejecución para una aplicación homebrew construida con un SDK/toolchain legítimo.

## Estado actualizado — sesión 60

Los PUP retail 13.50 y 13.52 están disponibles en el workspace de auditoría y fueron verificados por SHA-256 y SLB2. El diferencial del contenedor es `+16896` bytes (`+480` en `PS4UPDATE1.PUP` y `+16200` en `PS4UPDATE2.PUP`), pero las entradas internas siguen opacas y no permiten atribuir cambios a WebKit o BD-J.

El módulo `libSceNKWebKit.sprx` de 13.52 sigue ausente. Los candidatos públicos `JSCell::toX`, `MarkedVector` y `CloneSerializer/Deserializer` se mantienen como `STRONG_INDIRECT/UNVERIFIED`; `DocumentFontLoader`, `TransformStream` y DFG StoreBarrier son candidatos upstream sin evidencia retail 13.52. Los informes de las sesiones 49–60 contienen la procedencia y clasificación detalladas.

## Entradas requeridas

| Entrada | Estado |
|---|---|
| ELF/SELF de aplicación generado por OpenOrbis | Debe generarse en el entorno del usuario |
| `param.sfo`/paquete de aplicación | Debe generarse con herramientas autorizadas y verificadas |
| Librerías WebKit/JSC target | No presentes para 13.52 |
| Headers y stubs de plataforma | Dependen del SDK/toolchain elegido |
| PS4 13.52 de laboratorio | Requerida para cualquier prueba física autorizada; no se usa en este kit |

## Secuencia segura

1. Crear una aplicación mínima que sólo ejecute `basic_capabilities.js` o su equivalente embebido.
2. Verificar hashes y dependencias antes del empaquetado.
3. Instalarla únicamente mediante el flujo de desarrollo autorizado disponible para el dispositivo.
4. Capturar logs de arranque, carga de librerías, renderizado y ejecución JavaScript.
5. Comparar los logs con la matriz de compatibilidad; no reutilizar dmesg del kernel #6 como prueba de WebKit.

El `libkernel_sys_13.52.bin` del repositorio sólo puede usarse como entrada de análisis estático y procedencia. No se carga ni se enlaza automáticamente, y no se interpreta como sustituto de `libkernel_web`, de un SDK o de las bibliotecas de WebKit.

Los informes recientes están en `webkit-kit/runtime/`, especialmente `WEBKIT_JSC_CANDIDATE_DEEP_RESEARCH_SESSION60.md`, `PUP_1350_1352_STATIC_DIFF_SESSION51.md` y `UFM42_WOBKOT_HISTORY_SESSION49.md`.
