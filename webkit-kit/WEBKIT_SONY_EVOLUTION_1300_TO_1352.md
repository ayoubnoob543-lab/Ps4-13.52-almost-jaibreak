# Evolución pública Sony/WebKit: 13.00–13.04 → 13.52

**Fecha:** 2026-08-20  
**Alcance:** evolución pública de `JSCell::toX`, `MarkedVector`/GC y `CloneSerializer`/`objectPool`.  
**Exclusiones:** no se buscaron módulos retail, PUPs, dumps ni exploits.  
**Regla:** ningún resultado se eleva a `CONFIRMED_13.52`.

## Resumen

El repositorio público `FreeBSDKernel9-0/PS4OSSCode` sólo tiene una rama (`main`) y no tiene tags publicados. Su commit más reciente es `d636699770323d7968a2c37955aa513bda5f8a37`, fechado el 22 de abril de 2026, cuyo mensaje es `Add WebKit WebKit-601-1300 (PS4 13.00-13.04)`. El historial del repositorio muestra que los blobs WebKit se añadieron en ese snapshot; no hay commits Sony posteriores que permitan construir una evolución hasta 13.50/13.52.

La página oficial de Sony lista como referencias más recientes de código fuente PS4 las familias `WebKit-601-1300` y `WebKit-616-1300`, ambas descritas para PS4 13.00–13.04. No lista una fuente WebKit exacta para 13.50 o 13.52 [1].

## Inventario Sony público

| Corpus/ref | Evidencia de refs | Estado temporal | Fuerza |
|---|---|---|---|
| `WebKit-601-1300` | Rama única `main`, commit `d636699...`; árbol fuente completo anidado | Snapshot 13.00–13.04 | `DIRECT` para ese corpus |
| `WebKit-616-1300` | El árbol accesible contiene `LayoutTests`, `WebKit.xcworkspace`, `WebKitLibraries` y `resources`, pero no `Source` equivalente | 13.00–13.04 según Sony; no permite inspección de implementación en este corpus | `DIRECT` para la composición del árbol; `UNVERIFIED` para las familias |
| Versiones Sony posteriores | No hay ramas/tags ni commits posteriores en `PS4OSSCode`; Sony no lista 13.50/13.52 en la página OSS consultada | No disponible | `UNVERIFIED` |

El lockfile local fija `WebKit-601-1300` con SHA-256 `dc2a7584695474c9b878dcfdc16b2358bda61041053220b146320d6cfed3f02b`. El hash de `WebKit-616-1300` no está fijado localmente.

## Cadena upstream verificable

| Familia | Commit upstream | Fecha | Archivos relevantes | Cambio |
|---|---|---:|---|---|
| `JSCell::toX` | `2a042fede0e705bae4b8ce039b18442696ebb5ce` | 2024-03-12 | `Source/JavaScriptCore/runtime/JSCell.cpp` | Sustituye casts tras comprobaciones `is*` por `jsDynamicCast`/`jsSecureCast` |
| `MarkedVector`/GC | `c9880de4a28b9a64a5e1d0513dc245d61a2e6ddb` | 2023-04-17 | `Heap.*`, `ArgList.*`, `SerializedScriptValue.cpp`, AudioWorklet | Almacena punteros de celdas deserializadas en `MarkedVector` para visibilidad del GC |
| `CloneSerializer`/`objectPool` | `010c6bdfb0cde0485d31f0260ab9a046fa9b8567` | 2024-01-26 | `SerializedScriptValue.cpp`, opciones y tests structured-clone | Hace coincidir el object pool serializer/deserializer y separa su propósito del keep-alive |
| Interfaz posterior de `MarkedVector` | `4bd1aab3f384604aa1cd8152c675fe5ca4c90bcc` | 2026-03-30 | `MarkedVector.*`, `Heap.*`, API/tests | Amplía la interfaz; no es el parche histórico relevante para PS4 13.52 |

## Comparación estructural con 601-1300

Los blobs públicos del snapshot Sony tienen estos hashes Git:

| Archivo Sony 601-1300 | Blob Git | Tamaño | Observación |
|---|---|---:|---|
| `Source/JavaScriptCore/runtime/JSCell.cpp` | `2c403c813fb38568b0e60ce78989ddea4c953c12` | 7.742 B | `toPrimitive` y `toNumber` muestran `isString`/`isSymbol`/`isHeapBigInt` y `static_cast`; no aparece el patrón posterior en esas rutas |
| `Source/JavaScriptCore/heap/Heap.cpp` | `842625eae6341d18eda50bdc5549ea11e03be2e1` | 44.918 B | Invoca `MarkedArgumentBuffer::markLists` |
| `Source/JavaScriptCore/runtime/ArgList.h` | `fdfe00102cd38701e93ce759a7223aac4c03899e` | 4.330 B | Declara `MarkedArgumentBuffer`, no la interfaz posterior `MarkedVector` |
| `Source/WebCore/bindings/js/SerializedScriptValue.cpp` | `6786119069805e75b7c94addcd71527fafd7ebe3` | 92.486 B | `CloneDeserializer` mantiene `m_gcBuffer` como `MarkedArgumentBuffer`; `ObjectReferenceTag` usa índices de ese buffer y existe `m_objectPool` en serialización |

### Matriz de evidencia

| Familia | Commit/blob | Versión/rango Sony | Cambio observado | Equivalencia upstream | Fuerza | Implicación 13.52 |
|---|---|---|---|---|---|---|
| `JSCell::toX` | Blob `2c403c...`; commit upstream `2a042f...` | 601-1300, 13.00–13.04 | Snapshot contiene el patrón previo a `jsDynamicCast`/`jsSecureCast` | Coincide con el estado anterior al commit | `DIRECT` para 601-1300; `STRONG_INDIRECT` para el estado pre-corrección | No demuestra si Sony backporteó el cambio después |
| `MarkedVector`/GC | Blobs `842625...` y `fdfe001...`; upstream `c9880de...` | 601-1300, 13.00–13.04 | `Heap` y `ArgList` usan `MarkedArgumentBuffer` | Coincide con la arquitectura previa a la transición `MarkedVector` | `DIRECT` para 601-1300; `STRONG_INDIRECT` para pre-transición | No demuestra la composición de 13.52 |
| `CloneSerializer`/`objectPool` | Blob `678611...`; upstream `010c6b...` | 601-1300, 13.00–13.04 | `m_gcBuffer` participa en deserialización y el serializer mantiene `m_objectPool` | Compatible con el diseño anterior al parche de sincronización | `DIRECT` para 601-1300; `STRONG_INDIRECT` para pre-parche | La separación pool/keep-alive de 13.52 sigue desconocida |

## Interpretación correcta

La evidencia Sony pública permite afirmar directamente cómo está compuesto el **snapshot 601-1300**. Permite inferir con fuerza que ese snapshot es anterior a los tres commits upstream posteriores, porque contiene las formas antiguas de las rutas relevantes. No permite afirmar que PS4 13.52 mantenga esas formas: entre 13.04 y 13.52 pudieron existir backports Sony, merges privados, cambios de compilación o refactorizaciones no publicadas.

La revisión `616-1300` no se puede usar para declarar ausencia de las familias: en el árbol consultado no existe el `Source` completo. El estado correcto es `UNVERIFIED`, no `NO MATCH`.

## Conclusión

No existe una cadena pública Sony continua entre 13.00–13.04 y 13.52 en el corpus consultado. El resultado más fuerte es una línea base directa y reproducible: **601-1300 contiene los tres patrones previos a los commits upstream posteriores**. Para 13.52, las tres familias permanecen `UNVERIFIED`; no hay evidencia pública suficiente para elegir `VULNERABLE_LIKE` o `FIXED_LIKE`.

## Referencias

[1]: https://www.playstation.com/en-us/oss/ps4/webkit/ "Sony PS4 WebKit open-source releases"
[2]: https://github.com/FreeBSDKernel9-0/PS4OSSCode/tree/d636699770323d7968a2c37955aa513bda5f8a37 "PS4OSSCode snapshot and refs"
[3]: https://github.com/WebKit/WebKit/commit/2a042fede0e705bae4b8ce039b18442696ebb5ce "JSCell::toX should use jsDynamicCast/jsSecureCast"
[4]: https://github.com/WebKit/WebKit/commit/c9880de4a28b9a64a5e1d0513dc245d61a2e6ddb "CloneDeserializer should store cell pointers in a MarkedVector"
[5]: https://github.com/WebKit/WebKit/commit/010c6bdfb0cde0485d31f0260ab9a046fa9b8567 "CloneSerializer/Deserializer's objectPool should match"
[6]: https://github.com/WebKit/WebKit/commit/4bd1aab3f384604aa1cd8152c675fe5ca4c90bcc "Enhance MarkedVector's interface"
[7]: https://github.com/FreeBSDKernel9-0/PS4OSSCode/blob/d636699770323d7968a2c37955aa513bda5f8a37/WebKit-601-1300/WebKit-601-1300/Source/JavaScriptCore/runtime/JSCell.cpp "Sony OSS JSCell.cpp blob"
[8]: https://github.com/FreeBSDKernel9-0/PS4OSSCode/blob/d636699770323d7968a2c37955aa513bda5f8a37/WebKit-601-1300/WebKit-601-1300/Source/JavaScriptCore/heap/Heap.cpp "Sony OSS Heap.cpp blob"
[9]: https://github.com/FreeBSDKernel9-0/PS4OSSCode/blob/d636699770323d7968a2c37955aa513bda5f8a37/WebKit-601-1300/WebKit-601-1300/Source/JavaScriptCore/runtime/ArgList.h "Sony OSS ArgList.h blob"
[10]: https://github.com/FreeBSDKernel9-0/PS4OSSCode/blob/d636699770323d7968a2c37955aa513bda5f8a37/WebKit-601-1300/WebKit-601-1300/Source/WebCore/bindings/js/SerializedScriptValue.cpp "Sony OSS SerializedScriptValue.cpp blob"
