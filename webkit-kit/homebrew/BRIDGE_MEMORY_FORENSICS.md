# Forense de `bridge/Memory.h`

## Veredicto

`bridge/Memory.h` no procede del WebKit OSS estándar de las revisiones Safari-601 consultadas. En `PS4OSSCode` aparece como una dependencia introducida por la variante modificada `WebKit-601-1300`, pero el archivo y el proyecto bridge que define su contrato no están incluidos en el commit público disponible. No se recuperó una fuente compatible y no se añadió ningún stub.

Estado final:

```text
BRIDGE_MEMORY_SOURCE = NOT_FOUND_IN_PUBLIC_OSS_CORPUS
JSC_BUILD = BLOCKED_BY_MISSING_SOURCE_DEPENDENCY
PROPRIETARY_COMPONENTS = NOT_USED
```

## Evidencia local

El corpus local está fijado en `d636699770323d7968a2c37955aa513bda5f8a37`, con un único ref público local (`main`). La consulta de historial para el path exacto no devuelve ningún commit:

```text
git log --all --full-history -- '*bridge/Memory.h'  # sin resultados
```

El path exacto tampoco existe en ningún árbol Git local. En cambio, diez archivos del árbol `WebKit-601-1300` incluyen `<bridge/Memory.h>`, entre ellos `GCActivityCallback.h`, `Vector.h`, `HashTable.h`, `MallocPtr.h`, `StructureChain.h`, `YarrPattern.h` y varias fuentes JIT.

La comparación de `GCActivityCallback.h` con upstream demuestra que la variante 601-1300 no es un simple checkout estándar. Frente a `Safari-601.1.32.1` introduce simultáneamente:

```diff
-#include <wtf/PassRefPtr.h>
+#include <bridge/Memory.h>
+#include <wtf/RefPtr.h>
...
-WTF_MAKE_FAST_ALLOCATED;
+JSCBRIDGE_MAKE_SHARED_DATA_ALLOCATED;
```

El mismo árbol usa además `JSCBRIDGE_INSTANCE().poolAllocator16K()` y la macro `JSCBRIDGE_MAKE_SHARED_DATA_ALLOCATED` en múltiples clases. No hay definiciones de estas macros ni una carpeta `bridge` que contenga `Memory.h` en el checkout materializado.

## Comparación entre variantes PS4OSS

| Variante | Referencias `bridge/Memory.h` | Referencias `JSCBRIDGE_*` | Archivo `Memory.h` |
|---|---:|---:|---|
| WebKit-601-1250 | 0 | 0 | Ausente |
| WebKit-601-1300 | 9 archivos con inclusión | 25 archivos con referencias | Ausente |
| WebKit-616-1250 | 0 | 0 | Ausente |
| WebKit-616-1300 | 0 | 0 | Ausente |

Esto acota el problema al delta específico de `WebKit-601-1300`; no es una dependencia común del corpus OSS.

## Comparación con WebKit upstream público

Se comprobaron las tags públicas `Safari-601.1.32.1` y `Safari-601.1.46.25.2` del repositorio WebKit. En ambas, las rutas siguientes devuelven HTTP 404:

```text
Source/WebCore/bridge/Memory.h
Source/JavaScriptCore/bridge/Memory.h
Source/WTF/wtf/bridge/Memory.h
Source/WebCore/bridge/jsc/Memory.h
```

`GCActivityCallback.h` upstream tampoco contiene la inclusión `<bridge/Memory.h>`. El árbol navegable de Chromium WebKit muestra la capa estándar `Source/WebCore/bridge` con `Bridge.h`, runtime y NP bridge, pero no `Memory.h`.

La búsqueda pública de código para `JSCBRIDGE_MAKE_SHARED_DATA_ALLOCATED`, `JSCBRIDGE_INSTANCE` y la cadena exacta `<bridge/Memory.h>` no produjo un repositorio OSS legítimo con una implementación coincidente.

## Procedencia técnica más probable

La evidencia permite afirmar que `bridge/Memory.h` pertenece al contrato de un componente adicional denominado por el propio código como **JSC bridge**. Ese contrato no es el bridge JavaScript estándar de `Source/WebCore/bridge`: sus símbolos son específicos de la variante 601-1300 y afectan asignación de objetos compartidos, allocators de pools y rutas JIT.

No es posible afirmar, sólo con el corpus público, si el componente era un paquete interno, un submódulo omitido, una biblioteca del port Manx o un árbol adicional del SDK. El `PlatformManx.cmake` referencia `LIBJSCBRIDGE_INCLUDE_DIRS`, lo que refuerza que el proveedor debía llegar como una dependencia externa del port, pero no demuestra su contenido ni licencia.

## Build reintentada

La configuración CMake GTK histórica continúa siendo reproducible y termina correctamente. La compilación real de `JavaScriptCore` vuelve a detenerse en:

```text
fatal error: bridge/Memory.h: No such file or directory
```

No se reintentó con un archivo inventado, un header upstream no compatible ni un stub, porque eso cambiaría la semántica de la memoria/JIT y no sería una recuperación válida.

## Qué falta para desbloquear JSC

Se necesita una fuente verificable que contenga, como mínimo:

1. `bridge/Memory.h` con licencia/procedencia compatible.
2. Las definiciones de `JSCBRIDGE_MAKE_SHARED_DATA_ALLOCATED` y `JSCBRIDGE_INSTANCE`.
3. Las clases o funciones de `JSC::bridge`, incluyendo `PoolAllocator16K`.
4. Los include paths y bibliotecas que el `LIBJSCBRIDGE_INCLUDE_DIRS` del port Manx presupone.
5. Una confirmación de que esa fuente corresponde a la misma revisión ABI de 601-1300.

Ninguno de esos cinco elementos está disponible en el corpus público consultado. Por eso la fuente no puede recuperarse legítimamente desde las revisiones upstream comparadas.

## Referencias públicas

[1]: https://github.com/WebKit/WebKit/tree/Safari-601.1.32.1/Source/WebCore/bridge "WebKit Safari-601.1.32.1, Source/WebCore/bridge"
[2]: https://github.com/WebKit/WebKit/tree/Safari-601.1.46.25.2/Source/WebCore/bridge "WebKit Safari-601.1.46.25.2, Source/WebCore/bridge"
[3]: https://chromium.googlesource.com/external/Webkit/+/refs/heads/master/Source/WebCore/bridge/ "Chromium external WebKit bridge tree"
[4]: https://github.com/FreeBSDKernel9-0/PS4OSSCode "PS4OSSCode public repository"
