# Rastreo upstream y posibles backports JSC/WebKit

**Fecha:** 2026-08-20  
**Alcance:** código público únicamente. No se analizaron SPRX, PUP, dumps ni exploits.

## Conclusión ejecutiva

Los tres commits tienen diffs upstream precisos y reproducibles. Dos de ellos (`c9880de` y `010c6bd`) contienen una referencia explícita a una rama interna de Safari mediante `Originally-landed-as`; eso demuestra una integración Apple/Safari, no un backport Sony/PS4. No se encontró un commit público que relacione cualquiera de los tres cambios con Sony, PS4 13.52 o una rama `WebKit-601/616-1300`.

La comparación directa contra el árbol público `FreeBSDKernel9-0/PS4OSSCode`, que declara importar el código Sony `WebKit-601-1300` para PS4 13.00–13.04, aporta una evidencia nueva: ese árbol 601-1300 conserva las implementaciones anteriores y no contiene los patrones introducidos por los tres commits. Esto demuestra una diferencia entre la snapshot pública Sony 13.00–13.04 y upstream posterior, pero **no permite extrapolar el estado de PS4 13.50 o 13.52**.

## Tabla principal

| Familia | Corrección upstream | Primera aparición pública | Backports encontrados | Evidencia Sony | Relación posible con 13.52 | Confianza |
|---|---|---|---|---|---|---|
| `JSCell::toX` | `2a042fede0e705bae4b8ce039b18442696ebb5ce`, WebKit `275948@main`, 2024-03-11/12. En `JSCell.cpp`, `toPrimitive` y `toNumber` sustituyen `isString/isSymbol/isHeapBigInt` + `static_cast` por `jsDynamicCast`; `toObjectSlow` usa `jsDynamicCast` y `jsSecureCast`. El mensaje lo califica como mejora de calidad, con release assert, no como parche de CVE. | Commit upstream exacto; bug 270797. | No se encontró otro commit de WebKit main con el bug/hash que sea cherry-pick del mismo cambio. Posteriormente, `178cea00` (2026-04-18) reemplaza usos de `jsSecureCast` por `downcast`, y `1953979` adapta casts de subclases JSCell; son evoluciones posteriores, no backports a PS4. | En Sony 601-1300 `JSCell.cpp` sigue usando `isString/isSymbol` y `static_cast` en `toPrimitive`, `toNumber` y `toObject`; no aparecen `jsDynamicCast`/`jsSecureCast`. | La snapshot 13.00–13.04 no contiene la corrección. No hay evidencia pública para 13.50/13.52. | **DIRECT** para upstream y 601-1300; **UNVERIFIED** para 13.52. |
| `MarkedVector` / GC | `c9880de4a28b9a64a5e1d0513dc245d61a2e6ddb`, WebKit `263041@main`, 2023-04-17. Refactoriza `MarkedArgumentBuffer` en `MarkedVector`, cambia `Heap::m_markListSet` y el marking de listas, añade tipos de cell pointers y `CrashOnOverflow`, y sustituye Vectors sin raíz GC en `CloneDeserializer::deserialize`. | Commit upstream exacto y referencia `Originally-landed-as: 259548.530@safari-7615-branch` (`2c49ff7`). | La rama Safari interna está explícitamente documentada en el mensaje. No se encontró una referencia Sony ni un cherry-pick público posterior del mismo cambio. | Sony 601-1300 contiene `MarkedArgumentBuffer` en `ArgList.h/cpp`; `Heap` y `CloneDeserializer` usan el diseño anterior. No aparece `MarkedVector` en los archivos consultados. | Evidencia negativa para la snapshot 13.00–13.04; no prueba el estado 13.50/13.52. | **DIRECT** para diff upstream, Safari branch y 601-1300; **UNVERIFIED** para 13.52. |
| `CloneSerializer/objectPool` | `010c6bdfb0cde0485d31f0260ab9a046fa9b8567`, WebKit `273557@main`, 2024-01-26. Separa `m_gcBuffer` en `m_objectPool` y `m_keepAliveBuffer`, renombra métodos, añade `CloneDeserializer::addToObjectPool`, elimina inserciones erróneas BigInt/map/set, alinea tags/orden serializer-deserializer y añade validator debug `validateSerializedValue`. | Commit upstream exacto y referencia `Originally-landed-as: 267815.623@safari-7617-branch` (`430d474`). | La rama Safari interna está explícitamente documentada. Posteriores cambios en `SerializedScriptValue.cpp` —por ejemplo `3a900e1` y `cfe3893`— son cambios distintos sobre structured clone; no prueban backport Sony. | Sony 601-1300 conserva `CloneBase::m_gcBuffer`, un `ObjectPool m_objectPool` y llamadas directas `m_gcBuffer.append`; no aparecen `m_keepAliveBuffer`, `addToObjectPool` ni `validateSerializedValue`. | Evidencia negativa para 13.00–13.04; sin evidencia pública del backport a 13.52. | **DIRECT** para upstream, Safari branch y 601-1300; **UNVERIFIED** para 13.52. |

## Detalle de la comparación Sony 601-1300

La fuente pública Sony OSS está enlazada en [Sony WebKit OSS](https://www.playstation.com/en-us/oss/ps4/webkit/). El espejo navegable utilizado es [FreeBSDKernel9-0/PS4OSSCode](https://github.com/FreeBSDKernel9-0/PS4OSSCode), cuyo commit de importación `d636699770323d7968a2c37955aa513bda5f8a37` se titula `Add WebKit WebKit-601-1300 (PS4 13.00-13.04)`.

En `Source/JavaScriptCore/runtime/JSCell.cpp`, la snapshot 601-1300 contiene:

```cpp
if (isString())
    return static_cast<const JSString*>(this)->toPrimitive(exec, preferredType);
if (isSymbol())
    return static_cast<const Symbol*>(this)->toPrimitive(exec, preferredType);
return static_cast<const JSObject*>(this)->toPrimitive(exec, preferredType);
```

y el equivalente antiguo de `toNumber`; no contiene `jsDynamicCast` ni `jsSecureCast` en esas rutas.

En `Source/JavaScriptCore/runtime/ArgList.h` y `ArgList.cpp`, la snapshot contiene `class MarkedArgumentBuffer`, `MarkedArgumentBuffer::addMarkSet`, `markLists`, `expandCapacity` y `slowAppend`. No contiene `MarkedVector`.

En `Source/WebCore/bindings/js/SerializedScriptValue.cpp`, la snapshot contiene `CloneBase::m_gcBuffer`, `ObjectPool m_objectPool` y llamadas directas a `m_gcBuffer.append`. No contiene `m_keepAliveBuffer`, `CloneSerializer::addToObjectPool`, `CloneDeserializer::addToObjectPool`, `objectPoolTags` ni `validateSerializedValue`.

Estas observaciones son comprobables en los archivos raw publicados por el espejo:

- [`JSCell.cpp` 601-1300](https://raw.githubusercontent.com/FreeBSDKernel9-0/PS4OSSCode/main/WebKit-601-1300/WebKit-601-1300/Source/JavaScriptCore/runtime/JSCell.cpp)
- [`ArgList.h` 601-1300](https://raw.githubusercontent.com/FreeBSDKernel9-0/PS4OSSCode/main/WebKit-601-1300/WebKit-601-1300/Source/JavaScriptCore/runtime/ArgList.h)
- [`ArgList.cpp` 601-1300](https://raw.githubusercontent.com/FreeBSDKernel9-0/PS4OSSCode/main/WebKit-601-1300/WebKit-601-1300/Source/JavaScriptCore/runtime/ArgList.cpp)
- [`SerializedScriptValue.cpp` 601-1300](https://raw.githubusercontent.com/FreeBSDKernel9-0/PS4OSSCode/main/WebKit-601-1300/WebKit-601-1300/Source/WebCore/bindings/js/SerializedScriptValue.cpp)

## Estado de WebKit-616-1300

El espejo público consultado contiene un directorio `WebKit-616-1300`, pero el contenido navegable no expone un árbol `Source` equivalente: aparecen `LayoutTests`, `WebKit.xcworkspace`, `WebKitLibraries` y `resources`. Por ello no se puede usar ese espejo para afirmar presencia o ausencia de las tres correcciones en 616-1300. Los ZIP oficiales de Sony existen, pero miden aproximadamente 829 MB para 601-1300 y 1.62 GB para 616-1300; no se descargaron para esta tarea.

## Backports y equivalentes posteriores

La búsqueda de commits públicos por los bugs 270797, 254797 y 265975 devuelve los commits objetivo como coincidencias principales, no una serie de cherry-picks Sony. Los mensajes de `c9880de` y `010c6bd` sí identifican ramas internas Safari, que son la evidencia más fuerte de integración fuera de `main`.

El historial posterior muestra evolución del mismo código, pero no equivalencia automática. `178cea00` reemplaza `jsSecureCast` por `downcast`; `3a900e1` corrige una confusión de índices en structured clone; `cfe3893` trata una condición de carrera en `CloneSerializer::dumpIfTerminal`; y `442482a` corrige protección GC de `CachedString::m_jsString`. Son cambios relacionados por archivo o subsistema, no pruebas de que los tres commits originales estén en PS4 13.52.

## Relación con PS4 13.52

No se encontró commit, issue, changelog o manifest público que mencione simultáneamente cualquiera de los tres hashes/canonical links y PS4 13.52. Tampoco se encontró un backport Sony verificable. La evidencia disponible solo permite afirmar que:

1. Las correcciones existen upstream y, en dos casos, fueron integradas en ramas internas Safari.
2. La snapshot pública Sony 601-1300, identificada como 13.00–13.04, es anterior a las tres correcciones y conserva los diseños antiguos.
3. El estado de WebKit/JSC en 13.50 y 13.52 sigue siendo **UNVERIFIED** para las tres familias.
4. No es válido clasificar PS4 13.52 como `FIXED_LIKE`, `VULNERABLE_LIKE` o confirmado a partir de estos datos.

## Referencias

[1]: https://github.com/WebKit/WebKit/commit/2a042fede0e705bae4b8ce039b18442696ebb5ce "WebKit commit 2a042fe"
[2]: https://github.com/WebKit/WebKit/commit/c9880de4a28b9a64a5e1d0513dc245d61a2e6ddb "WebKit commit c9880de"
[3]: https://github.com/WebKit/WebKit/commit/010c6bdfb0cde0485d31f0260ab9a046fa9b8567 "WebKit commit 010c6bd"
[4]: https://www.playstation.com/en-us/oss/ps4/webkit/ "Sony PS4 WebKit OSS"
[5]: https://github.com/FreeBSDKernel9-0/PS4OSSCode/commit/d636699770323d7968a2c37955aa513bda5f8a37 "PS4OSSCode 601-1300 import"
[6]: https://webkit.org/blog/12967/understanding-gc-in-jsc-from-scratch/ "WebKit JSC GC architecture"
[7]: https://github.com/WebKit/WebKit/commit/178cea00b798cd742bb8342e614a2f3ef6bc4f05 "Later jsSecureCast evolution"
[8]: https://github.com/WebKit/WebKit/commit/3a900e192fe7c22dccc007fde344d3a373476175 "Later structured clone fix"
[9]: https://github.com/WebKit/WebKit/commit/cfe38930db92bdf1fecc71b3c014c861bf4033df "Later CloneSerializer race fix"
[10]: https://github.com/WebKit/WebKit/commit/442482adf1bd2ac184111e7745464cf6a0848b64 "Later CloneDeserializer GC protection fix"

**Clasificación final:** evidencia upstream y Sony 601-1300 **DIRECT**; backport Sony a 13.52 **UNVERIFIED**; inferencia de 13.52 desde 13.00–13.04 **UNVERIFIED**.
