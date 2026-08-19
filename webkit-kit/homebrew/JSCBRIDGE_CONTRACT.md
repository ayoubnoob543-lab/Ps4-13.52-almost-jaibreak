# Contrato público observable de JSCBRIDGE en WebKit-601-1300

## Veredicto

El árbol público `WebKit-601-1300` expone una dependencia externa de split-process JIT y memoria compartida denominada **JSCBRIDGE**. El contrato puede reconstruirse parcialmente desde sus call sites, pero el proveedor no está incluido en `PS4OSSCode` y no apareció con otro nombre en las búsquedas públicas realizadas. No se integra código equivalente ni se intenta compilar contra un stub.

Estado:

```text
JSCBRIDGE_CALL_SITES = CONFIRMED
JSCBRIDGE_PROVIDER_SOURCE = MISSING
JSCBRIDGE_BUILD = BLOCKED_BY_MISSING_BRIDGE_HEADERS/LIBRARIES
SONY_RETAIL_COMPONENTS = NOT_USED
```

## Inventario de headers externos

El árbol contiene referencias, pero ninguno de estos archivos existe en el checkout materializado ni en los objetos Git del corpus:

| Header | Referencias aproximadas | Estado |
|---|---:|---|
| `bridge/JSCBridge.h` | 1 | `MISSING` |
| `bridge/JSCBridge_comp.h` | 8 | `MISSING` |
| `bridge/JSCBridge_inline.h` | 13 | `MISSING` |
| `bridge/JSCBridge_vm.h` | 11 | `MISSING` |
| `bridge/Memory.h` | 9 | `MISSING` |
| `bridge/VTableMap.h` | 1 | `MISSING` |
| `bridge/VirtualMethodCall.h` | 12 | `MISSING` |
| `bridge/unique_ptr_shared.h` | 5 | `MISSING` |
| `bridge/unique_ptr_virtual.h` | 2 | `MISSING` |

El inventario completo reproducible está en `jscbridge-contract-inventory.txt`.

## Superficie de memoria y allocator

`MarkedBlock.cpp` usa `JSCBRIDGE_INSTANCE().poolAllocator16K()` bajo `PLATFORM(MANX) && ENABLE(SPLITPROC_JIT)`. El objeto esperado ofrece al menos:

```text
PoolAllocator16K& poolAllocator16K()
size_t chunkAlignment() const
size_t chunkSize() const
void* allocate()
void deallocate(void*)
```

La misma ruta también usa `sharedAlignedMalloc` y `sharedAlignedFree`. El código decide si una capacidad/alineación coincide con el pool de 16 KiB; en caso contrario vuelve a la asignación compartida genérica. El inventario muestra referencias análogas a `PoolAllocator32K` en otras rutas.

`ExecutableAllocatorFixedVMPool.cpp` revela el contrato de memoria ejecutable:

### VM side

Bajo `ENABLE(SPLITPROC_JIT) && BUILDING_SPLITPROC_VM`:

```text
JSCBridgeVM::sharedInstance()
JSCBridgeVM::jscExecutableAllocator()
JSCBridgeVM::jscFixedExecutableMemoryAddr()
JSCBridgeVM::jscFixedExecutableMemorySize()
```

### Compiler side

Bajo `ENABLE(SPLITPROC_JIT) && BUILDING_SPLITPROC_COMP`:

```text
JSCBridgeComp::sharedInstance()
JSCBridgeComp::jscExecutableAllocator(allocator)
JSCBridgeComp::jscFixedExecutableMemoryAddr(start)
JSCBridgeComp::jscFixedExecutableMemorySize(size)
```

La clase `FixedVMPoolExecutableAllocator` lleva `JSCBRIDGE_MAKE_SHARED_DATA_ALLOCATED`. Esto demuestra que el bridge gestiona un allocator compartido y un rango fijo de memoria ejecutable entre dos procesos, pero no define la implementación ni sus garantías de seguridad.

## Superficie de JIT split-process

`Source/JavaScriptCore/PlatformManx.cmake` añade `LIBJSCBRIDGE_INCLUDE_DIRS` a `JavaScriptCore_INCLUDE_DIRECTORIES`. Cuando `MANX_ENABLE_SPLITPROC_JIT` está activo, define:

```text
ENABLE_SPLITPROC_JIT=1
BUILDING_SPLITPROC_VM=1
```

Y elimina del target VM una serie de implementaciones JIT locales, incluyendo `ExecutableAllocator.cpp`, `JITStubs.cpp`, `JITPropertyAccess.cpp`, `Repatch.cpp`, `LLIntThunks.cpp` y `YarrJIT.cpp`. El comentario del árbol dice que esa funcionalidad será proporcionada por el bridge.

En `Source/WebKit2/PlatformManx.cmake`, cuando `ORBIS && MANX_ENABLE_SPLITPROC_JIT`, se enlazan:

```text
JscBridge_vm
SceJitBridge
```

Estos nombres son referencias de link observables, no archivos disponibles. Su procedencia y licencia no están demostradas en el corpus OSS.

## Registro de metadatos y vtables

`ClassInfo.h` incluye `bridge/JSCBridge_vm.h`. Bajo `BUILDING_SPLITPROC_VM`, el constructor de `ClassInfo` llama:

```text
bridge::JSCBridgeVM::classInfoRegisterInstance(this)
```

Por tanto el bridge no sólo administra memoria: también registra instancias de metadatos de clases y participa en la identidad de tipos entre procesos.

`ThreadSafeRefCounted.h` incluye `JSCBridge_vm.h`, `VTableMap.h` y `VirtualMethodCall.h`. La variante `ThreadSafeRefCounted<T, needs_vtable_fixup>` llama a:

```text
SPLITPROC_VIRTUAL_TABLE_FIXUP(objectToDelete)
```

antes de borrar objetos que requieren reparación de vtable. Esto revela una segunda superficie ABI: mapeo/fixup de vtables y llamadas virtuales a través de la frontera split-process.

## Macros y contratos observables

El código usa, como mínimo:

```text
JSCBRIDGE_INSTANCE()
JSCBRIDGE_MAKE_SHARED_DATA_ALLOCATED
SPLITPROC_ASSERT_IS_IN_SHARED_DATA
SPLITPROC_VIRTUAL_DELETE
SPLITPROC_VIRTUAL_METHOD_CALL
SPLITPROC_VIRTUAL_METHOD_SCOPE
SPLITPROC_VIRTUAL_TABLE_FIXUP
SPLITPROC_TRAMPOLINE
```

Las definiciones de estas macros no están en el árbol público. No es seguro sustituirlas por macros vacías: algunas cambian layout, allocation, dispatch virtual y destrucción de objetos.

## CMake y dependencias Manx

`OptionsManx.cmake` requiere públicamente Cairo, Pixman, Freetype2, HarfBuzz, ICU, JPEG, LibXml2, PNG, SQLite, Zlib, `Libmanx` y shaders precompilados. Para ORBIS añade EGL, `ScePigletv2VSH_stub_weak` y, dependiendo de `MANX_ORBIS_USE_PUBLIC_SDK`, `ScePosix_stub_weak` o bibliotecas internas.

`PlatformManx.cmake` de WebCore y WebKit2 añade `LIBJSCBRIDGE_INCLUDE_DIRS`. WebKit2 además lista `JscBridge_vm` y `SceJitBridge` para split-process JIT. El port Manx exige `ORBIS`; en un host Linux normal aborta con `Unknown OS 'Linux'` antes de poder resolver esas variables.

## Búsqueda de nombres alternativos

Se comprobaron:

| Fuente | Resultado |
|---|---|
| Historial y objetos Git de PS4OSSCode | No hay provider ni headers `bridge/*`. |
| Variantes PS4OSS 601-1250, 616-1250 y 616-1300 | No contienen JSCBRIDGE. |
| Tags upstream Safari-601 | No contienen `Memory.h` ni macros JSCBRIDGE. |
| Chromium external/WebKit bridge | Sólo bridge estándar WebCore; no JSCBRIDGE. |
| Búsqueda pública de `JSCBRIDGE_INSTANCE`, `JSCBRIDGE_MAKE_SHARED_DATA_ALLOCATED`, `JscBridge_vm`, `SceJitBridge` | Sin fuente OSS legítima compatible recuperada. |

Los nombres `JscBridge_vm` y `SceJitBridge` aparecen únicamente como dependencias de link en el CMake del port Manx; no se debe asumir que sean redistribuibles ni que tengan una implementación pública.

## Conclusión de integración

No se recuperó una fuente legítima compatible. Por tanto:

1. No se copió ningún header externo.
2. No se creó `Memory.h`.
3. No se añadió un stub de JSCBRIDGE.
4. No se reintentó una compilación JSC con una implementación inventada.
5. El bloqueo correcto permanece `MISSING`, no `AVAILABLE` ni `RECOVERABLE`.

Para desbloquear una build real se necesita una distribución pública del proveedor completo, incluyendo headers `bridge/*`, implementación VM/compiler, bibliotecas `JscBridge_vm`/`SceJitBridge`, configuración de include/link y una licencia compatible. Sin ese conjunto no puede afirmarse compatibilidad con JSC 601-1300 ni con PS4/13.52.

## Referencias públicas

[1]: https://github.com/FreeBSDKernel9-0/PS4OSSCode "PS4OSSCode"
[2]: https://github.com/WebKit/WebKit/tree/Safari-601.1.32.1 "WebKit Safari-601.1.32.1"
[3]: https://github.com/WebKit/WebKit/tree/Safari-601.1.46.25.2 "WebKit Safari-601.1.46.25.2"
[4]: https://chromium.googlesource.com/external/Webkit/+/refs/heads/master/Source/WebCore/bridge/ "Chromium external WebKit bridge tree"
