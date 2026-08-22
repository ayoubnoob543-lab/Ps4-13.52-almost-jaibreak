# Wrapper JIT público de PS4-SDK — sesión 72

## Fuente

- `CTurt/PS4-SDK/libPS4/source/jit.c`: https://github.com/CTurt/PS4-SDK/blob/master/libPS4/source/jit.c
- Ejemplo JIT: https://github.com/CTurt/PS4-SDK/tree/master/examples/jit

El código se leyó como fuente pública y no se compiló ni ejecutó.

## Contrato histórico observado

El archivo declara tres punteros de función resueltos dinámicamente desde `libKernelHandle`: `sceKernelJitCreateSharedMemory`, `sceKernelJitCreateAliasOfSharedMemory` y `sceKernelJitMapSharedMemory`. La función histórica `allocateJIT` crea una memoria compartida con permisos de ejecución, crea un alias con permisos de lectura/escritura y realiza dos mapeos separados: uno ejecutable y otro escribible. El diseño permite escribir en un alias y ejecutar desde otro, evitando un mapeo virtual único RWX.

Este código confirma de forma directa, para la toolchain histórica de PS4-SDK, la existencia nominal de un contrato JIT y sus tres wrappers. No confirma que el contrato siga igual en 13.52, que un proceso WebKit tenga permiso para usarlo, ni que exista una primitive WebKit que permita alcanzar esas llamadas.

## Relación con WebKit

La fuente de CTurt describe la interfaz como una capacidad del sistema/SDK, no como una vulnerabilidad. La propia documentación histórica distingue entre código nativo dentro del WebProcess y escape de sandbox/kernel. Por ello, el wrapper debe usarse como referencia para reconocer imports y dependencias en módulos antiguos, no como evidencia de una cadena de explotación.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| Tres wrappers JIT nombrados en PS4-SDK histórico | `DIRECT_HISTORICAL` |
| Modelo de memoria compartida con alias RX/RW | `DIRECT_HISTORICAL` |
| Existencia del mismo contrato en PS4 13.52 | `UNVERIFIED` |
| Permiso JIT del WebProcess en 13.52 | `UNVERIFIED` |
| Primitive WebKit que alcance los wrappers | `DISCARDED` como conclusión; no está demostrada |
| Utilidad para comparar imports/exports antiguos | `INDIRECT_13.52` |

## Conclusión

El archivo mejora la especificación de lo que habría que buscar estáticamente en un módulo antiguo: nombres o equivalentes de los tres wrappers y sus referencias desde WebKit/JIT. No resuelve la ausencia de `libSceNKWebKit.sprx` 13.52 ni demuestra una ruta nativa en esa versión.

## Referencias

[1] [CTurt/PS4-SDK — `jit.c`](https://github.com/CTurt/PS4-SDK/blob/master/libPS4/source/jit.c)

[2] [CTurt/PS4-SDK — ejemplo JIT](https://github.com/CTurt/PS4-SDK/tree/master/examples/jit)
