# WebKit/JSC PS4 13.52 — kit de compatibilidad estática

Este directorio contiene un kit reproducible para **auditar, preparar y validar artefactos WebKit/JSC** destinados a investigación de compatibilidad con PS4 13.52. No contiene un WebKit retail de Orbis, un SDK propietario, un payload de explotación ni una cadena de escape de sandbox.

## Estado de evidencia

El repositorio contiene referencias estructurales y el blob `libkernel_sys_13.52.bin`, pero no contiene una copia verificada de `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, `eboot.bin` o un WebKit retail 13.52. Por ello, el kit puede validar y comparar una imagen suministrada por el usuario, pero no puede fabricar una identidad binaria ausente.

| Componente | Estado |
|---|---|
| Scanner ELF/SELF estático | Incluido en `tools/inspect_artifact.py` |
| Manifiesto de hashes y procedencia | Incluido en `tools/make_manifest.py` |
| Harness JavaScript no explotativo | Incluido en `harness/` |
| Compatibilidad WebKit/JSC real en PS4 | Requiere artefactos y SDK/ABI de la misma build |
| Kernel Baikal #6 | Sólo identidad documental; bytes ausentes |

## Uso

```sh
python3 webkit-kit/tools/inspect_artifact.py /ruta/a/libSceNKWebKit.sprx
python3 webkit-kit/tools/make_manifest.py webkit-kit/artifacts > webkit-kit/artifacts/SHA256SUMS
python3 webkit-kit/tools/check_host.py
```

Las herramientas realizan lectura estática. No cargan ELF/SELF/SPRX, no ejecutan JavaScript recibido desde red y no invocan exploits.

## Flujo de integración legítimo

Primero se debe aportar un artefacto con procedencia, fecha, tamaño y SHA-256. Después se inspeccionan sus cabeceras, segmentos, imports/exports disponibles y cadenas. La compilación de un WebKit para hardware real requiere además un árbol de fuentes compatible, toolchain, headers, ABI de Orbis y librerías de plataforma; ninguno de esos elementos se presume aquí.

El harness de `harness/` sólo prueba capacidades estándar de ECMAScript y APIs WebKit documentadas si el ejecutor anfitrión las proporciona. No contiene pruebas de corrupción de memoria, escape de sandbox, kread/kwrite ni ejecución de payloads.

## Clasificación

`DIRECT_BYTES` significa que el archivo y su hash están disponibles. `STRUCTURAL` significa que sólo existe código, tabla o documentación compatible. `MISSING` significa que no hay bytes verificables en el corpus. Las referencias al kernel #6 y a `wifissh` permanecen separadas de este kit y no se promocionan como inputs de WebKit.
