# Proveniencia pública de dumps WebKit 6.72/7.00 — sesión 72

## Fuentes revisadas

- GBAtemp, “PS4 Webkit Bad_Hoist 6.72 dumps”: https://gbatemp.net/threads/ps4-webkit-bad_hoist-6-72-dumps.605764/
- AlexAltea/Nucleus, `_README.md`: https://github.com/AlexAltea/nucleus/blob/master/bin/platforms/ps4/system/common/lib/_README.md
- Exploit-DB, “Hacking the PS4, part 2”: https://www.exploit-db.com/docs/44208

Las páginas fueron leídas pasivamente. No se descargaron dumps ni se ejecutaron scripts o payloads.

## GBAtemp

El hilo de 2022 documenta que los dumps de 6.72 eran difíciles de localizar porque un enlace anterior había caducado. En respuestas públicas se enumera el contenido esperado de `dumps_672.7z`: `gadgets.txt`, `libc.bin`, `libc.elf`, `libc-gadgets.txt`, `libkernel.bin`, `libkernel.elf`, `syscalls.txt`, `webkit-gadgets.txt`, `webkit.bin` y `webkit.elf`.

El hilo también distingue entre un archivo `.bin`/`.elf` generado para análisis y los módulos descargados por FTP. Las respuestas atribuidas a participantes de la comunidad describen que un módulo descargado puede estar descifrado y comenzar con una cabecera ELF, pero el hilo no aporta hashes ni una cadena de custodia criptográfica de esos bytes.

La fuente refuerza que los dumps históricos se obtenían desde un proceso PS4 ya habilitado y que el archivo `webkit.bin` no debe confundirse automáticamente con un ELF retail completo. Es evidencia histórica/documental, no una ruta legítima offline para 13.52.

## Nucleus

El README de `AlexAltea/nucleus` lista dependencias de módulos PS4 que deben extraerse desde `/system/common/lib` de una consola propia. Entre la lista aparecen `libSceJitBridge.sprx`, `libSceJscCompiler.sprx`, `libSceWebKit2.sprx`, `libSceWebBrowserDialog.sprx`, `libSceWebBrowserInjectedBundle.sprx` y otras bibliotecas.

El mismo README indica que los módulos SELF/SPRX deben ser descifrados en la consola antes de colocarlos en el directorio local y afirma que no existe una forma conocida de extraer las claves de descifrado desde la consola. Esto es una referencia técnica importante para el inventario de dependencias, pero no contiene los archivos ni demuestra que correspondan a 13.52. La presencia nominal de `libSceJscCompiler.sprx` o `libSceJitBridge.sprx` tampoco demuestra una ruta de explotación ni su estado en 13.52.

## Exploit-DB

El artículo histórico describe que el proceso WebKit tenía restricciones de sandbox y que el código nativo ejecutado dentro de WebKit seguía perteneciendo al proceso WebKit. La fuente es útil para separar conceptualmente `WebKit → código nativo en WebProcess` de `sandbox escape/kernel`, pero no aporta bytes 13.52 ni debe usarse como guía operativa.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| Lista pública de archivos WebKit/libkernel 6.72 | `DIRECT_HISTORICAL` |
| Lista de dependencias PS4 que incluye WebKit/JIT | `DIRECT_HISTORICAL` |
| Dato de que los módulos deben proceder de `/system/common/lib` | `DOCUMENTED_ONLY` |
| Dato de que exista `libSceJscCompiler` en PS4 13.52 | `UNVERIFIED` |
| Bytes/hashes de WebKit 6.72 o 7.00 desde estas páginas | `UNVERIFIED` |
| Evidencia de `libSceNKWebKit` 13.52 | `DISCARDED` |
| Evidencia de una primitive WebKit funcional | `DISCARDED` |

## Conclusión

GBAtemp aporta nombres y contexto de procedencia de los dumps históricos; Nucleus aporta una lista pública de módulos de sistema relevantes, incluidos componentes JIT/WebKit. Ninguna fuente aporta el módulo retail 13.52. El artefacto de máximo valor sigue siendo `libSceNKWebKit.sprx` o un dump WebKit parcial con firmware, hash y procedencia verificables.

## Referencias

[1] [GBAtemp — PS4 Webkit Bad_Hoist 6.72 dumps](https://gbatemp.net/threads/ps4-webkit-bad_hoist-6-72-dumps.605764/)

[2] [AlexAltea/Nucleus — PS4 system libraries README](https://github.com/AlexAltea/nucleus/blob/master/bin/platforms/ps4/system/common/lib/_README.md)

[3] [Exploit-DB — Hacking the PS4, part 2](https://www.exploit-db.com/docs/44208)
