# Safe WebKit homebrew prototype

Este directorio contiene un **prototipo de frontera portable y verificable en host** para una futura integración WebKit homebrew. No es un WebKit retail, no contiene módulos Sony propietarios y no implementa exploits, payloads ni loaders.

## Alcance

El prototipo usa únicamente la base OSS ya incorporada y un contrato C pequeño. `src/orbis_webkit_stub.c` proporciona una implementación host con red y gráficos deshabilitados. Valida ciclo de vida, reporte de capacidades y un smoke path determinista sin acceder a hardware, APIs privilegiadas, interfaces de kernel o binarios propietarios.

El código OSS completo de WebKit/JSC se conserva como corpus de referencia. No se copia silenciosamente dentro de este adaptador porque un port completo requiere sistema de build target, sysroot, capa de plataforma y headers generados. Así se evita presentar un stub host como runtime PS4.

## Build y smoke test

```sh
make -C webkit-kit/homebrew clean all
cat webkit-kit/homebrew/build/host/smoke-output.txt
```

El build acepta `CC`, `CPPFLAGS` y `CFLAGS` desde el entorno y produce `build/host/homebrew-safe-smoke`. El smoke test comprueba `profile=host-safe`, `network=false`, `graphics=false` y `sony_modules=false`.

No existe deliberadamente un target PS4 en este Makefile. Debe añadirse sólo después de disponer de una instalación legal de OpenOrbis, un sysroot compatible y un procedimiento documentado de empaquetado y ejecución.

## Entradas necesarias para OpenOrbis

```text
OO_PS4_TOOLCHAIN=<ruta local verificada>
OO_PS4_SYSROOT=<sysroot autorizado>
OO_PS4_HEADERS=<headers compatibles>
BUILD_PROFILE=ps4-homebrew
```

## Interfaces Orbis/Sony ausentes

Están marcadas como **MISSING**, no sustituidas por símbolos inventados: ABI y sysroot target; event loop; threads/timers; filesystem y sandbox; allocator y memory pressure; backend gráfico/compositor; red y almacén de certificados; política JIT/W^X y memoria ejecutable; entry point y empaquetado de aplicación; e integración interna de WebKit. Se excluyen expresamente nombres de módulos `.sprx`, imports, offsets, vtables, gadgets, ROP/JOP y payloads.

## Estados

`AVAILABLE` significa que está presente y es comprobable en el host. `MISSING` significa que es necesario para un target PS4 real pero no está disponible y no se fabrica. `UNKNOWN` significa que no puede establecerse sólo con fuentes OSS.

## Bloqueo actual

El entorno no tiene `clang`, `ld.lld`, CMake, Ninja, Docker, un sysroot OpenOrbis ni una PS4 conectada. Por tanto, el resultado permitido es un build host del adaptador; no se genera ELF/SELF ni se afirma compatibilidad con `libSceNKWebKit.sprx` retail 13.52.

## Seguridad

El prototipo no carga payloads externos, no busca ni invoca vulnerabilidades, no accede a una PS4, no usa binarios Sony y no afirma compatibilidad con firmware 13.52. Un smoke test host demuestra únicamente que el contrato del adaptador es coherente.
