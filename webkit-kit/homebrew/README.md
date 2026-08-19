# Base homebrew separada

Este directorio define únicamente el contrato de una aplicación homebrew legítima que podría usar OpenOrbis cuando el usuario aporte una instalación autorizada del toolchain. No contiene un loader de jailbreak, un payload, un exploit ni módulos retail.

## Entradas necesarias

```text
OO_PS4_TOOLCHAIN=<ruta local verificada>
OO_PS4_SYSROOT=<sysroot autorizado>
OO_PS4_HEADERS=<headers compatibles>
BUILD_PROFILE=ps4-homebrew
```

## Bloqueo actual

El entorno auditado no tiene `clang`, `ld.lld`, CMake, Ninja, Docker, un sysroot OpenOrbis o una PS4 conectada. Por tanto, todavía no se genera un ELF/SELF. El estado correcto es `TOOLCHAIN_REQUIRED`, no `BUILD_PASS`.

## Validación prevista

Cuando exista el toolchain, la aplicación debe compilarse en un directorio separado, producir un manifest SHA-256 y registrar el formato del artefacto. La ejecución debe realizarse sólo mediante un método legítimo de desarrollo autorizado. Un smoke test homebrew no demostraría compatibilidad con `libSceNKWebKit.sprx` retail 13.52.
