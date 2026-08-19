# Plan de build reproducible

## Objetivos separados

### A. Smoke build host

Compilar y probar JavaScriptCore/WebKit de la fuente pública más cercana en un host Linux. Esto valida la toolchain, la configuración y el harness, pero no demuestra compatibilidad con Orbis.

### B. Build PS4 homebrew legítima

Usar OpenOrbis para una aplicación de prueba que enlace contra sus headers/stubs y ejecute el harness seguro. Esto requiere una instalación legal del toolchain y un método legítimo de instalación/ejecución en el dispositivo. No se incluye aquí un loader de exploit.

### C. WebKit retail-compatible 13.52

Este objetivo permanece bloqueado hasta disponer de una fuente WebKit específica de 13.52, headers/ABI de plataforma, librerías internas y un contrato de empaquetado compatible. Las fuentes Sony 13.00–13.04 son la base OSS más cercana, pero no deben etiquetarse como 13.52.

## Variables de build

```text
WEBKIT_SOURCE_DIR=<fuente OSS descargada y hash verificado>
OO_PS4_TOOLCHAIN=<instalación OpenOrbis verificada>
LLVM_VERSION=<versión exacta, obligatoria antes de compilar>
TARGET_FIRMWARE=13.52
BUILD_PROFILE=host-smoke | ps4-homebrew | retail-compatible-blocked
```

## Adaptaciones que aún deben demostrarse

La adaptación de WebKit/JSC para PS4 requiere determinar, a partir de una fuente y ABI legítimas, el target CPU, endianess y ABI de libc, threading, allocator, filesystem, sandbox, graphics backend, event loop, JIT policy, formato ELF/SELF y librerías importadas. No se rellenan estas piezas con offsets del kernel #6 ni con `libkernel_sys_13.52.bin`, porque ese blob no constituye un WebKit ni un SDK.

## Criterios de validación

Una build sólo se considera reproducible si conserva el commit de fuente, parche, versión de toolchain, flags, entorno, hashes de entradas y logs. Una build sólo se considera PS4-compatible si el binario enlaza con el ABI target y el empaquetado es aceptado por un entorno legítimo de desarrollo. Una ejecución real requiere además validación en hardware y logs separados de la investigación del kernel #6.
