# README de continuidad: WebKit/WPE en `webkit-ps4-1352-kit`

Este documento permite que otra sesión de Manus retome el trabajo **exclusivamente relacionado con WebKit, JavaScriptCore, WebKitGTK y WPE WebKit**. No es un resumen de la investigación general de PS4/Baikal ni una especificación de compatibilidad retail.

> **Regla principal:** el objetivo actual es demostrar un WebKit OSS moderno desacoplado de GTK mediante WPE en host Linux. No se deben introducir SDK retail, módulos `.sprx`, offsets, gadgets, exploits, payloads, ROP/JOP, JSCBRIDGE propietario ni APIs Sony inventadas.

## 1. Identidad del repositorio y rama

| Campo | Valor |
|---|---|
| Repositorio | `https://github.com/ayoubnoob543-lab/firmware-lab` |
| Rama de trabajo | `webkit-ps4-1352-kit` |
| Último commit antes de este README | `7c572769c8e6d1a85dc82960fc2be34386a2c6d8` |
| Commit anterior de build WPE | `3aac225c3472653a79f07cf5886b812b9ea3410e` |
| Sistema analizado | Ubuntu 24.04 amd64 |
| Estado PS4 13.52 | `UNKNOWN`; no demostrado |
| Estado WPE host | Configurado, dependencias base compiladas, MiniBrowser pendiente |

La rama contiene el historial técnico de la migración conceptual, el prototipo host, la investigación del WebKit histórico y el intento reproducible de WPE. La rama debe mantenerse separada de `main` y de cualquier material propietario.

## 2. Decisión arquitectónica

Se abandonó como ruta principal el WebKit histórico de PS4OSSCode/WebKit-601-1300 porque depende de un componente externo llamado **JSCBRIDGE** que no está presente en los objetos Git ni en el checkout público disponible. No se inventó `bridge/Memory.h`, no se fabricaron allocators, vtables ni bibliotecas equivalentes.

La ruta actual es:

```text
WebKit OSS moderno
        |
        +-- WebCore / JavaScriptCore / WTF / WebKit
        |
        +-- Port WPE
                |
                +-- libwpe 1.16.3
                +-- WPEBackend-fdo 1.16.1 para host Linux
                +-- futuro backend OpenOrbis: MISSING/UNKNOWN
```

El backend WPE host no es un backend PS4. La compilación y el smoke test host no permiten afirmar compatibilidad con firmware 13.52.

## 3. Componentes y procedencia fijada

| Componente | Versión | Fuente pública | SHA-256 | Estado |
|---|---:|---|---|---|
| WPE WebKit | 2.52.6 | `https://wpewebkit.org/releases/wpewebkit-2.52.6.tar.xz` | `b2bafef2751625b7fdf530f230ff0f542ff0eeba3590c3a989d931b2a55c858e` | Fuente descargada y CMake configurado |
| libwpe | 1.16.3 | `https://wpewebkit.org/releases/libwpe-1.16.3.tar.xz` | `c880fa8d607b2aa6eadde7d6d6302b1396ebc38368fe2332fa20e193c7ee1420` | Configurado y compilado en prefijo temporal |
| WPEBackend-fdo | 1.16.1 | `https://wpewebkit.org/releases/wpebackend-fdo-1.16.1.tar.xz` | `544ae14012f8e7e426b8cb522eb0aaaac831ad7c35601d1cf31d37670e0ebb3b` | Configurado y compilado; 53/53 tareas |
| WebKitGTK baseline | 2.52.3 Ubuntu | Paquetes públicos Ubuntu 24.04 | Versión documentada en `WEBKITGTK_VERSION.txt` | Ejecutable y smoke validados |

El único tarball WPE pequeño versionado en la rama es `webkit-kit/homebrew/wpe-source/wpebackend-fdo-1.16.1.tar.xz`. Los tarballs grandes de libwpe y WPE WebKit no se versionaron; sus URLs y hashes están documentados arriba y en `WPE_HOST_BUILD_STATUS.md`.

## 4. Build WPE realizado

### 4.1 Prefijos temporales

Los builds previos se hicieron en rutas temporales, que pueden no existir después de una nueva sesión del sandbox:

```text
/tmp/libwpe-1.16.3-build
/tmp/wpe-prefix
/tmp/wpebackend-fdo-build
/tmp/wpewebkit-2.52.6-src
/tmp/wpewebkit-2.52.6-build
```

La fuente extraída de WPE WebKit ocupa aproximadamente 482 MB. El build directory parcial llegó aproximadamente a 113 MB y conservó headers/objetos reutilizables.

### 4.2 Configuración de WPE WebKit

La configuración real utilizada fue conceptualmente:

```sh
cmake -S /tmp/wpewebkit-2.52.6-src/wpewebkit-2.52.6 \
  -B /tmp/wpewebkit-2.52.6-build \
  -G Ninja \
  -DPORT=WPE \
  -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_MINIBROWSER=ON \
  -DUSE_LIBBACKTRACE=OFF \
  -DUSE_GSTREAMER=OFF \
  -DENABLE_INTROSPECTION=OFF \
  -DENABLE_WEBDRIVER=OFF \
  -DENABLE_GAMEPAD=OFF \
  -DENABLE_SPEECH_SYNTHESIS=OFF
```

CMake terminó con:

```text
Configuring done
Generating done
```

El target `MiniBrowser` fue generado por Ninja. Se resolvieron dependencias públicas como GLib, Soup 3, ICU, HarfBuzz, JPEG, JPEG XL, AVIF, PNG, SQLite, WebP, ATK, Freetype, LibXslt, libsystemd, libseccomp y `unifdef`. GStreamer se mantuvo desactivado para reducir dependencias y no se usó GTK en la configuración WPE.

### 4.3 Resultado de compilación

El build del target se inició realmente y se reanudó varias veces sin limpiar el directorio:

```sh
ninja -C /tmp/wpewebkit-2.52.6-build MiniBrowser -j2
ninja -C /tmp/wpewebkit-2.52.6-build MiniBrowser -j4
ninja -C /tmp/wpewebkit-2.52.6-build MiniBrowser -j1
```

El proceso alcanzó la generación de headers y posteriormente unidades pesadas de JavaScriptCore. El workspace disponía aproximadamente de 3,8 GiB de RAM, 2 GiB de swap y 2,6 GiB libres. Los compiladores fueron terminados por el límite operativo/presión de recursos durante unidades unificadas C++; no se estableció un error semántico reproducible de WPE.

Resultado final verificado:

```text
LIBWPE_BUILD       = PASS
WPEBACKEND_FDO     = PASS
WPE_CMAKE_CONFIG   = PASS
WPE_MINIBROWSER    = BLOCKED_BY_WORKSPACE_RESOURCES
WPE_EXECUTABLE     = NOT_PRESENT
```

No afirmar `MiniBrowser` compilado hasta encontrar un ejecutable enlazado y verificarlo con `file`, `ldd`/`readelf` y ejecución controlada.

## 5. Smoke tests y baseline GTK

### 5.1 Fixtures existentes

Los tres fixtures se encuentran en:

```text
webkit-kit/homebrew/fixtures/page1.html
webkit-kit/homebrew/fixtures/page2.html
webkit-kit/homebrew/fixtures/page3.html
```

El flujo probado por el baseline GTK es:

```text
page1.html -> page2.html -> page3.html
```

El conjunto cubre DOM, Flexbox, Grid, CSS, animaciones, JavaScript, eventos, formularios, SVG, imagen data URI, Canvas 2D, localStorage y navegación/history.

### 5.2 Resultado GTK

El smoke GTK se ejecuta mediante el Makefile con Xvfb:

```sh
make -C webkit-kit/homebrew clean all
```

El resultado GTK ha sido validado con las tres etapas:

```text
stage=1: DOM/event/text/flex/grid/animation/form/svg/image/canvas/storage = PASS
stage=2: page/storage/dom/js/event = PASS
stage=3: page/history/dom/js = PASS
```

Este resultado es únicamente **WebKitGTK 2.52.3 baseline**. No debe copiarse al resultado WPE.

### 5.3 Resultado WPE actual

Como no existe aún un `MiniBrowser` WPE enlazado, la matriz correcta es:

| Capacidad | GTK baseline | WPE 2.52.6 | Comparación |
|---|---:|---:|---:|
| DOM | PASS | NOT_TESTED | NOT_TESTED |
| Flexbox/Grid | PASS | NOT_TESTED | NOT_TESTED |
| CSS | PASS | NOT_TESTED | NOT_TESTED |
| JavaScript | PASS | NOT_TESTED | NOT_TESTED |
| Eventos | PASS | NOT_TESTED | NOT_TESTED |
| Formularios | PASS | NOT_TESTED | NOT_TESTED |
| SVG/imágenes | PASS | NOT_TESTED | NOT_TESTED |
| Canvas | PASS | NOT_TESTED | NOT_TESTED |
| localStorage | PASS | NOT_TESTED | NOT_TESTED |
| page1→page2→page3 | PASS | NOT_TESTED | NOT_TESTED |

No se debe marcar ninguna capacidad WPE como `PASS` hasta ejecutar el mismo conjunto con el binario WPE.

## 6. Código host y pruebas existentes

Los archivos principales son:

| Ruta | Función |
|---|---|
| `webkit-kit/homebrew/Makefile` | Compila los smokes host y ejecuta validaciones GTK |
| `webkit-kit/homebrew/src/modern_webkitgtk_smoke.c` | Navegador mínimo GTK que ejecuta los tres fixtures |
| `webkit-kit/homebrew/src/homebrew_smoke.c` | Smoke seguro del prototipo portable |
| `webkit-kit/homebrew/src/minimal_browser_main.c` | Navegador mínimo host |
| `webkit-kit/homebrew/src/oss_webkit_bridge.c` | Puente conceptual; no equivale a WebKit completo |
| `webkit-kit/homebrew/README.md` | Descripción técnica del prototipo y WPE |
| `webkit-kit/tools/run_host_regression.py` | Regresión host segura |
| `webkit-kit/tools/kit_health.py` | Auditoría estática de salud |
| `webkit-kit/tools/check_host.py` | Comprobación de herramientas y dependencias |
| `webkit-kit/WPE_HOST_BUILD_STATUS.md` | Estado detallado del build WPE |
| `webkit-kit/homebrew/WPE_VERSION_RESEARCH.md` | Fuentes, versiones y hashes de WPE |
| `webkit-kit/WEBKITGTK_CAPABILITY_MATRIX.md` | Resultado GTK y separación conceptual de WPE |
| `webkit-kit/IMPLEMENTATION_STATUS.md` | Estado central de componentes |

El prototipo `minimal-browser` puede ejecutar JavaScriptCore host mediante la API pública `javascriptcoregtk-4.1`. Esto demuestra JSC host real, pero **no demuestra WebCore, WebKit completo, WPE ni PS4**.

## 7. WebKit histórico 601-1300 y JSCBRIDGE

Se investigó y materializó parcialmente el árbol público histórico `WebKit-601-1300/WebKit-601-1300` del corpus PS4OSSCode, commit:

```text
d636699770323d7968a2c37955aa513bda5f8a37
```

El árbol contiene JSC, WTF, WebCore, WebKit2 y ports públicos/históricos. La build host llegó a un bloqueo real por:

```text
bridge/Memory.h
```

El header no aparece en el checkout ni en los objetos Git consultados. También faltan el proveedor externo y símbolos asociados a:

```text
JSCBridge.h
JSCBridge_comp.h
JSCBridge_vm.h
VTableMap.h
VirtualMethodCall.h
PoolAllocator16K
JscBridge_vm
SceJitBridge
LIBJSCBRIDGE_INCLUDE_DIRS
```

La decisión fue **no inventar** esos headers ni implementar stubs que pudieran falsear una build histórica compatible. Por ello:

```text
JSCBRIDGE_SOURCE = NOT_FOUND
WEBKIT_601_HOST_BUILD = BLOCKED
MANX/ORBIS_BUILD = BLOCKED
```

Esta ruta queda documentada para análisis, pero no es la ruta activa del navegador host.

## 8. Estado de interfaces y PS4

El kit mantiene separados los elementos conceptuales que un futuro backend OpenOrbis necesitaría: ventana/surface, presentación, input, timers/event loop, memoria, filesystem, networking/TLS, fuentes, sincronización y composición/renderizado.

No existe evidencia suficiente para afirmar que OpenOrbis proporcione todos esos contratos para WebKit moderno. Siguen clasificados como:

```text
OpenOrbis toolchain/sysroot = MISSING/UNKNOWN
Backend gráfico WPE para Orbis = MISSING
ABI/runtime Orbis para WebKit = UNKNOWN
Compatibilidad PS4 13.52 = UNKNOWN
```

No usar ni buscar como sustitutos los módulos retail `libSceNKWebKit.sprx`, `libkernel_web.sprx` o `libSceLibcInternal.sprx`. Sus bytes verificables no forman parte de esta ruta OSS.

## 9. Validaciones ya ejecutadas

En la rama WebKit se han ejecutado satisfactoriamente:

```sh
make -C webkit-kit/homebrew clean all
python3 -m py_compile $(find webkit-kit -type f -name '*.py')
python3 webkit-kit/tools/kit_health.py
git diff --check
```

Resultados conocidos:

```text
MAKE = PASS
PY_COMPILE = PASS
KIT_HEALTH = PASS; findings=[]
GIT_DIFF_CHECK = PASS
```

El commit que documenta la última reanudación WPE es:

```text
7c572769c8e6d1a85dc82960fc2be34386a2c6d8
```

## 10. Próximos pasos recomendados

La próxima sesión debe seguir este orden:

1. Comprobar el espacio disponible y confirmar si `/tmp/wpewebkit-2.52.6-build` todavía existe.
2. No limpiar ese build hasta registrar su tamaño, `CMakeCache.txt`, número de objetos y última tarea Ninja.
3. Si hay menos de 10 GiB libres, crear un workspace de build WPE separado con mayor capacidad o liberar únicamente duplicados verificados.
4. Configurar una segunda variante `MinSizeRel`/`-Os`, sin LTO ni optimizaciones interprocedurales, manteniendo `PORT=WPE` y `ENABLE_MINIBROWSER=ON`.
5. Compilar con `ninja -j1` y aumentar a `-j2` sólo si el consumo es estable.
6. Cuando exista el ejecutable, ejecutar primero `file`, `readelf -d` y `ldd`; después lanzar el MiniBrowser WPE con `page1.html`.
7. Implementar o adaptar un harness WPE que devuelva resultados estructurados para los tres fixtures. Marcar cada capacidad como `PASS`, `FAIL` o `NOT_TESTED`.
8. Comparar automáticamente ese JSON WPE con el resultado GTK ya registrado, sin mezclar las etiquetas.
9. Ejecutar `make`, `py_compile`, `kit_health.py` y `git diff --check`.
10. Documentar el resultado y hacer commit/push sólo si el árbol queda limpio y todos los datos son reproducibles.

## 11. Criterios de finalización

La fase WPE sólo puede declararse funcional cuando se cumplan simultáneamente:

```text
WPE WebKit CMake = PASS
MiniBrowser WPE enlazado = PASS
MiniBrowser WPE ejecutado = PASS
page1/page2/page3 = ejecutadas por WPE
DOM/CSS/JS/eventos/formularios/SVG/Canvas/storage/navigation = etiquetados individualmente
Comparación WPE vs GTK = generada automáticamente
Tests y auditorías = PASS
Commit/push = PASS
```

Hasta entonces, el estado honesto es:

```text
WPE_CMAKE_PASS
WPE_LIBWPE_PASS
WPEBACKEND_FDO_PASS
WPE_MINIBROWSER_PENDING_OR_BLOCKED
WPE_HTML_SMOKE_NOT_TESTED
PS4_13_52_COMPATIBILITY_NOT_CLAIMED
```
