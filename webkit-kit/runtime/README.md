# Runtime PS4 legítimo

Este directorio no contiene un exploit, payload, jailbreak ni loader para evadir controles de seguridad. Describe únicamente el contrato de ejecución para una aplicación homebrew construida con un SDK/toolchain legítimo.

## Entradas requeridas

| Entrada | Estado |
|---|---|
| ELF/SELF de aplicación generado por OpenOrbis | Debe generarse en el entorno del usuario |
| `param.sfo`/paquete de aplicación | Debe generarse con herramientas autorizadas y verificadas |
| Librerías WebKit/JSC target | No presentes para 13.52 |
| Headers y stubs de plataforma | Dependen del SDK/toolchain elegido |
| PS4 13.52 de laboratorio | Requerida para la prueba física |

## Secuencia segura

1. Crear una aplicación mínima que sólo ejecute `basic_capabilities.js` o su equivalente embebido.
2. Verificar hashes y dependencias antes del empaquetado.
3. Instalarla únicamente mediante el flujo de desarrollo autorizado disponible para el dispositivo.
4. Capturar logs de arranque, carga de librerías, renderizado y ejecución JavaScript.
5. Comparar los logs con la matriz de compatibilidad; no reutilizar dmesg del kernel #6 como prueba de WebKit.

El `libkernel_sys_13.52.bin` del repositorio sólo puede usarse como entrada de análisis estático y procedencia. No se carga ni se enlaza automáticamente, y no se interpreta como sustituto de `libkernel_web`, de un SDK o de las bibliotecas de WebKit.
