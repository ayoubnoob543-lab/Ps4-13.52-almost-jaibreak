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

## Navegador mínimo portable

`src/minimal_browser_main.c` y `src/homebrew_browser.c` implementan el primer escalón de navegador: inicialización, memoria controlada, comprobación del root de filesystem, un event loop mínimo y un hilo POSIX de timer que se une antes de finalizar. La salida es textual y no abre red, GPU, memoria ejecutable ni interfaces privilegiadas.

El puente `oss_webkit_bridge` separa la futura integración del motor. Una variable `WEBKIT_SOURCE_DIR` sólo registra una fuente candidata; **no basta para declarar el motor disponible**, porque aún deben generarse headers, compilar JSC/WebCore/WebKit y proporcionar un port adapter. En el entorno actual el estado es `oss-source-not-configured`.

La integración real de JSC/WebCore/WebKit queda bloqueada por la ausencia de toolchain OpenOrbis, sysroot, headers target, dependencias de build y capa de plataforma. El backend gráfico permanece en `graphics=stub`. No se añadió ninguna API propietaria ni se inventó un ABI PS4.

## JavaScriptCore host real

El target `minimal-browser` detecta JavaScriptCore GTK mediante `pkg-config javascriptcoregtk-4.1`, compila contra la API C pública `jsc_context_new`, `jsc_context_evaluate`, `jsc_value_to_boolean` y `jsc_value_to_string`, y ejecuta un programa JavaScript determinista dentro del navegador host. La expresión prueba `Array.prototype.map`, `Uint32Array` y `JSON.parse`.

La dependencia instalada en el host es `libjavascriptcoregtk-4.1-dev` versión `2.52.3-0ubuntu0.24.04.1`. Esta biblioteca es un runtime WebKitGTK host y no es la fuente histórica PS4 601/616, no es un módulo Sony y no prueba compatibilidad con firmware 13.52.

El árbol OSS PS4 ya auditado está en `/home/ubuntu/ps4-lab-1352/analysis/webkit_oss_sources_2026-08-19/PS4OSSCode`, commit `d636699770323d7968a2c37955aa513bda5f8a37`. El repositorio contiene fuentes de referencia, pero no un sistema de build host listo para compilar el árbol histórico completo dentro de este prototipo. Por ello la integración actual utiliza la API pública de JavaScriptCore GTK para probar el contrato de ejecución, mientras que el corpus PS4OSSCode permanece separado como fuente estructural.

El estado `jsc-host-available-oss-source-not-configured` significa que el motor host está disponible pero no se ha configurado una ruta de árbol OSS para un port adapter. `WEBKIT_SOURCE_DIR` nunca convierte automáticamente una fuente en un motor compilado.

## WebKit OSS histórico real

El árbol histórico más adecuado es `WebKit-601-1300/WebKit-601-1300` dentro de `PS4OSSCode`, commit `d636699770323d7968a2c37955aa513bda5f8a37`. Sus objetos Git contienen CMake, JavaScriptCore, WTF, WebCore y los ports GTK y Manx. El checkout físico no está materializado completo, por lo que el nuevo probe registra qué archivos existen en Git y cuáles requieren un archive de trabajo.

Se intentó la configuración CMake del port GTK con WebKit/WebKit2/tools desactivados. La configuración histórica avanzó hasta la detección de dependencias y quedó bloqueada por metadata de desarrollo de Cairo; el conjunto GTK completo también requiere LibSoup 2.42, GTK3/GDK3, ATK, HarfBuzz, ICU, LibXML2, LibXSLT, SQLite y otras dependencias. El espacio libre actual no permite instalar de forma segura todo el conjunto.

El port `Manx` es el port Orbis/PlayStation del árbol, pero exige `ORBIS`, headers y bibliotecas públicas de plataforma, además de componentes gráficos. No se convierte en port host ni se rellenan sus variables con SDK retail o símbolos Sony.

## Resultado de build histórico real

Se materializó el árbol completo necesario para build (`Source/`, CMake, `Tools/Scripts` y `WebKitLibraries`) en el workspace de análisis. La configuración CMake del port GTK terminó correctamente después de instalar dependencias públicas y aplicar en la copia de trabajo la inclusión estándar `CheckIncludeFiles` requerida por CMake moderno.

La compilación real de `JavaScriptCore` avanzó hasta fuentes WTF/JSC y se detuvo por la cabecera ausente `bridge/Memory.h`. Esa ruta no aparece en el checkout ni en los objetos Git del corpus; no se creó una cabecera inventada. Como WebCore/WebKit dependen de JSC, sus builds quedan bloqueados por la misma ausencia.

El port Manx no configura en Linux: `OptionsManx.cmake` termina con `Unknown OS 'Linux'`. Su `ORBIS.cmake` requiere `orbis-clang`, `orbis-clang++` y `SCE_ORBIS_SDK_DIR`; además `FindLibmanx.cmake` y `FindPrecompiledShaders.cmake` requieren headers y bibliotecas target específicas. Todas esas dependencias permanecen separadas y marcadas como `MISSING` o `UNKNOWN`.
