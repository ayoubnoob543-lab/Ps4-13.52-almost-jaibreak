# Investigación pública del origen JSCBRIDGE

## Veredicto

No se encontró una implementación OSS legítima y compatible del proveedor JSCBRIDGE usado por `WebKit-601-1300`. Sí aparecieron referencias públicas a `libSceJitBridge.sprx` y metadatos de módulos, pero no contienen los headers, fuentes o bibliotecas que exige el árbol 601-1300.

```text
JSCBRIDGE_PROVIDER_SOURCE = NOT_FOUND_IN_PUBLIC_SOURCES
JSCBRIDGE_METADATA = FOUND_BUT_NOT_IMPLEMENTATION
JSC_BUILD = STILL_BLOCKED
PROPRIETARY_SDK_OR_MODULES = NOT_USED
```

## Búsquedas realizadas

Se consultaron el índice de código y repositorios de GitHub mediante la API autenticada, búsquedas de commits, búsqueda de repositorios, forks del repositorio PS4OSSCode y consultas web dirigidas a GitLab, mirrors y documentación. Las cadenas examinadas fueron `JSCBridge.h`, `JSCBridge_comp.h`, `JSCBridge_vm.h`, `Memory.h`, `VTableMap.h`, `VirtualMethodCall.h`, `unique_ptr_shared.h`, `unique_ptr_virtual.h`, `PoolAllocator16K`, `JSCBRIDGE_INSTANCE`, `JSCBRIDGE_MAKE_SHARED_DATA_ALLOCATED`, `JscBridge_vm` y `SceJitBridge`.

La búsqueda de commits exactos no devolvió resultados para `JSCBridge_vm`, `JSCBridge_comp`, `PoolAllocator16K`, `JSCBRIDGE_INSTANCE` ni `JSCBRIDGE_MAKE_SHARED_DATA_ALLOCATED`. La búsqueda de repositorios devolvió únicamente proyectos no relacionados llamados `JSCBridge` y ningún repositorio sobre `SceJitBridge`, split-process JIT WebKit, Manx WebKit o `PoolAllocator16K`. Los forks públicos de `FreeBSDKernel9-0/PS4OSSCode` no devolvieron candidatos.

## Candidatos públicos y descarte

| Candidato | Evidencia | Licencia/procedencia | Compatibilidad | Decisión |
|---|---|---|---|---|
| `ShawnTSH1229/pset4` | `libSceJitBridge.sprx.json` | Repositorio MIT; archivo JSON de metadatos de módulo PS4 | No contiene fuentes ni headers | `DESCARTADO` |
| `CrazyVoidProgrammer/orbisLibGen` | `libSceJitBridge.sprx.json` | Sin SPDX declarado; JSON de metadatos | No contiene provider JSCBRIDGE | `DESCARTADO` |
| `rtyker/ps4-linux-baikal` | Lista `ps4_system_files.txt` | Documentación/índice de archivos del sistema | No contiene código JSCBRIDGE | `DESCARTADO` |
| `astrelsky/libNidResolver` y forks | Tablas de nombres/NIDs | GPL-2.0 | Resolver metadatos, no implementación | `DESCARTADO` |
| `VV1LD/DumpFile405/455` | Referencias a rutas `libSceJitBridge.sprx` | Herramientas de dumps/archivos | No contiene headers ni implementación | `DESCARTADO` |
| `CTurt/PS4-SDK` | Wrapper `allocateJIT` en `libPS4/source/jit.c` | Archivo público archivado, 2019 | Resuelve exports propietarios del kernel; no es JSCBRIDGE | `DESCARTADO` |
| Repositorios `JSCBridge` no relacionados | Proyectos de bridge genéricos | MIT | No relacionados con WebKit/Manx/Orbis | `DESCARTADO` |
| Tags upstream WebKit/Safari-601 | WebCore bridge estándar | OSS WebKit | No contienen JSCBRIDGE | `DESCARTADO` |

Los dos JSON de metadata de `libSceJitBridge.sprx` se descargaron sólo a `/tmp` y se verificaron:

| Archivo | SHA-256 | Tamaño | Contenido |
|---|---|---:|---|
| `pset4` metadata | `b735eced2a270a7910df2312f06667d58abf73d31cff8ca4025296c88d192883` | 17.803 bytes | `shared_object_names` y `modules` |
| `orbisLibGen` metadata | `1a454dad6bb9843fda80b4c8ad55bb6f8cdccf2a377108caeecb2b5e3943686f` | 17.946 bytes | `shared_object_names` y `modules` |

No se copiaron al repositorio porque son inventarios de módulos propietarios, no una implementación OSS del contrato.

## Evidencia de CTurt

El artículo público [Hacking the PS4, part 3][1] dice que `libSceJitBridge.sprx` fue sometido a ingeniería inversa y enlaza un wrapper `allocateJIT` del repositorio PS4-SDK. El wrapper sólo resuelve `sceKernelJitCreateSharedMemory`, `sceKernelJitCreateAliasOfSharedMemory` y `sceKernelJitMapSharedMemory`, y crea alias de memoria ejecutable/escribible.

Ese wrapper no implementa `JSCBridgeVM`, `JSCBridgeComp`, `PoolAllocator16K`, `VTableMap`, `VirtualMethodCall`, `JSCBRIDGE_INSTANCE` ni las macros de memoria compartida del WebKit 601-1300. Por tanto, es evidencia de que existe una interfaz runtime propietaria relacionada con JIT, pero no es una fuente compatible que pueda integrarse en el build OSS.

## Comparación con el contrato 601-1300

El árbol exige headers ausentes:

```text
bridge/JSCBridge.h
bridge/JSCBridge_comp.h
bridge/JSCBridge_inline.h
bridge/JSCBridge_vm.h
bridge/Memory.h
bridge/VTableMap.h
bridge/VirtualMethodCall.h
bridge/unique_ptr_shared.h
bridge/unique_ptr_virtual.h
```

También exige los símbolos y dependencias de link `JscBridge_vm` y `SceJitBridge`. Los metadatos públicos de `libSceJitBridge.sprx` no contienen las clases C++ ni las APIs de allocator/vtable que el código OSS invoca. No hay coincidencia verificable de versión, ABI, include paths, implementación ni licencia para usar esos datos como provider.

## Resultado de integración

No se integró ningún candidato. No se inventó `Memory.h`, no se creó un stub, no se añadió una biblioteca `.sprx`, no se usó SDK retail y no se alteró la semántica de JSC para ocultar el bloqueo. El build histórico continúa fallando en la primera dependencia:

```text
fatal error: bridge/Memory.h: No such file or directory
```

## Referencias

[1]: https://cturt.github.io/ps4-3.html "CTurt — Hacking the PS4, part 3"
[2]: https://github.com/CTurt/PS4-SDK/blob/master/libPS4/source/jit.c "CTurt PS4-SDK allocateJIT wrapper"
[3]: https://github.com/FreeBSDKernel9-0/PS4OSSCode "PS4OSSCode"
[4]: https://github.com/ShawnTSH1229/pset4 "pset4 public repository"
[5]: https://github.com/CrazyVoidProgrammer/orbisLibGen "orbisLibGen public repository"
[6]: https://github.com/rtyker/ps4-linux-baikal "ps4-linux-baikal public repository"
[7]: https://github.com/astrelsky/libNidResolver "libNidResolver public repository"
[8]: https://github.com/WebKit/WebKit/tree/Safari-601.1.32.1 "WebKit Safari-601.1.32.1"
