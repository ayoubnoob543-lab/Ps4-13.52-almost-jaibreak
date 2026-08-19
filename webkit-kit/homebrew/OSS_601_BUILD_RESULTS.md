# Resultados operativos del build WebKit-601-1300

## Materialización

El corpus Git `PS4OSSCode` está fijado en `d636699770323d7968a2c37955aa513bda5f8a37`. La materialización literal de todo el directorio histórico, incluyendo sitios, fixtures y herramientas auxiliares, no es viable en el volumen actual: el `tar` consumió el espacio disponible antes de completar el árbol. No se conserva esa extracción parcial.

Sí se materializó el árbol completo necesario para build:

```text
/home/ubuntu/ps4-lab-1352/analysis/webkit_oss_sources_2026-08-19/extracted/WebKit-601-1300-build-tree
```

Incluye todo `Source/`, `CMakeLists.txt`, `Tools/CMakeLists.txt`, `Tools/Scripts` y `WebKitLibraries`. Tiene 18.231 archivos y ocupa aproximadamente 314 MB. Se excluyeron únicamente Websites, LayoutTests y herramientas no necesarias para la compilación de bibliotecas.

## Configuración host GTK

Se instaló sólo software público de Ubuntu: CMake, Ninja, Gperf, Ruby, GTK2/GTK3, Cairo, ICU, LibSoup 2.4, LibXML2, LibXSLT, SQLite, HarfBuzz, Fontconfig, Freetype, ATK, WebP, OpenGL/EGL y dependencias de desarrollo relacionadas.

La configuración usa el port GTK histórico y desactiva componentes opcionales para aislar bibliotecas:

```sh
cmake -S WebKit-601-1300-build-tree -B host-build-601 -G Ninja \
  -DPORT=GTK -DENABLE_TOOLS=OFF -DENABLE_WEBKIT=OFF \
  -DENABLE_WEBKIT2=OFF -DENABLE_MINIBROWSER=OFF \
  -DENABLE_API_TESTS=OFF -DENABLE_GTKDOC=OFF \
  -DENABLE_INTROSPECTION=OFF -DENABLE_OPENGL=OFF \
  -DENABLE_GLES2=OFF -DENABLE_WEBGL=OFF -DENABLE_VIDEO=OFF \
  -DENABLE_WEB_AUDIO=OFF -DENABLE_NOTIFICATIONS=OFF \
  -DENABLE_GEOLOCATION=OFF -DENABLE_CREDENTIAL_STORAGE=OFF \
  -DENABLE_SPELLCHECK=OFF
```

La configuración terminó con `cmake_rc=0` y generó targets reales `JavaScriptCore`, `WTF`, `WebCore` y WebKit-related CMake targets. Se aplicó sólo en la copia de trabajo una compatibilidad CMake estándar: `FindOpenGL.cmake` necesitaba `include(CheckIncludeFiles)` con CMake moderno. El objeto Git original no fue modificado.

## Compilación JSC

La compilación real de `JavaScriptCore` se ejecutó con Ninja y falló durante la compilación de fuentes de WTF/JSC:

```text
fatal error: bridge/Memory.h: No such file or directory
```

La ruta no existe en el checkout materializado ni en ningún path del commit Git. La búsqueda del historial Git no encontró `bridge/Memory.h`; tampoco aparece como archivo en las variantes del corpus. Las únicas coincidencias de `Memory.h` pertenecen a FreeBSD/LLVM u otros árboles no relacionados.

Por tanto, este error no es una dependencia GTK ni una cabecera que deba inventarse: es una pieza ausente del árbol de fuentes requerido por este checkout histórico. No se creó un sustituto porque cambiar la semántica de la gestión de memoria/JIT sería incorrecto y podría ocultar el origen del port.

No se produjo `libJavaScriptCore`, `jsc`, `WebCore` ni `WebKit` histórico compilado.

## Port Manx/Orbis

El probe del port `Manx` sin variables target terminó con:

```text
CMake Error at Source/cmake/OptionsManx.cmake:2
Unknown OS 'Linux'
```

Esto ocurre antes de buscar las dependencias de plataforma y confirma que Manx no es un port host disfrazado. `ORBIS.cmake` cambia `CMAKE_SYSTEM_NAME` a `ORBIS`, requiere `SCE_ORBIS_SDK_DIR` y busca `orbis-clang`/`orbis-clang++` en `host_tools/bin`.

El cruce estático de `OptionsManx.cmake`, `ORBIS.cmake`, `FindLibmanx.cmake`, `FindPrecompiledShaders.cmake` y `PlatformManx.cmake` produce esta matriz:

| Interfaz/dependencia | Estado | Evidencia |
|---|---|---|
| `orbis-clang` y `orbis-clang++` | MISSING | `ORBIS.cmake` los busca bajo `SCE_ORBIS_SDK_DIR/host_tools/bin`. |
| `SCE_ORBIS_SDK_DIR` y sysroot | MISSING | No existe en el entorno. |
| `manx/System.h` | MISSING | `FindLibmanx.cmake` lo exige. |
| `SceOrbisCompat_stub_weak` | MISSING | Biblioteca exigida por `FindLibmanx.cmake`. |
| `precompiled_shaders.h` | MISSING | `FindPrecompiledShaders.cmake` lo exige. |
| `ScePrecompiledShaders_stub_weak` | MISSING | Biblioteca exigida por `FindPrecompiledShaders.cmake`. |
| `ScePigletv2VSH_stub_weak`/EGL target | MISSING | Rama gráfica de `OptionsManx.cmake`. |
| `ScePosix_stub_weak` | MISSING | Ruta de SDK público seleccionada por `MANX_ORBIS_USE_PUBLIC_SDK`. |
| `LIBJSCBRIDGE_INCLUDE_DIRS` | UNKNOWN/MISSING | Referenciado por `PlatformManx.cmake`, sin proveedor localizado. |
| `libmanx` 2.4 | MISSING | Include y library se resuelven externamente. |
| ABI, empaquetado y runtime Orbis | UNKNOWN | No inferibles de este árbol host. |

No se añadieron stubs para estas bibliotecas porque no son interfaces genéricas: son componentes target específicos y sus contratos binarios no están disponibles en el entorno.

## Veredicto

```text
SOURCE_BUILD_TREE_MATERIALIZED = YES (build-relevant subset)
CMAKE_GTK_CONFIGURATION = PASS
HISTORICAL_JSC_BUILD = BLOCKED_BY_MISSING_BRIDGE_MEMORY_H
HISTORICAL_WEBCORE_WEBKIT_BUILD = BLOCKED_BY_JSC
MANX_ORBIS_CONFIGURATION = BLOCKED_BY_ORBIS_TOOLCHAIN_AND_PLATFORM_DEPS
SONY_RETAIL_13_52 = NOT_USED / MISSING
```
