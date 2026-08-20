# Límite de inferencia upstream sobre PS4 13.52

**Fecha:** 2026-08-20. Este informe rastrea código público WebKit/JSC; no analiza SPRX, PUP, dumps ni exploits.

## Resultado

Las tres correcciones tienen una línea de descendencia upstream visible, pero no existe una rama Sony pública posterior a `WebKit-601-1300` que permita decidir si el código de PS4 13.52 las contiene. La snapshot Sony 601-1300, cuyo import público se identifica como PS4 13.00–13.04, conserva las implementaciones anteriores. Por tanto, la evidencia permite acotar un límite inferior para Sony OSS público, pero no clasificar 13.52 como anterior o posterior a ninguna corrección.

| Familia | Corrección base | Variantes posteriores verificadas | Qué demuestra | Estado 13.52 |
|---|---|---|---|---|
| `JSCell::toX` | [`2a042fe`](https://github.com/WebKit/WebKit/commit/2a042fede0e705bae4b8ce039b18442696ebb5ce), `JSCell.cpp`, `toPrimitive`, `toNumber`, `toObjectSlow`; `jsDynamicCast`/`jsSecureCast` | [`178cea00`](https://github.com/WebKit/WebKit/commit/178cea00b798cd742bb8342e614a2f3ef6bc4f05) reemplaza `jsSecureCast` por `downcast`; [`1953979`](https://github.com/WebKit/WebKit/commit/195397957f976f8920ba3310698dc69dc6b0c12a) adapta downcast/dynamicDowncast para subclases JSCell | Existe evolución posterior de la familia de casts; no es un backport Sony | **UNVERIFIED** |
| `MarkedVector` / GC | [`c9880de`](https://github.com/WebKit/WebKit/commit/c9880de4a28b9a64a5e1d0513dc245d61a2e6ddb), `MarkedArgumentBuffer`→`MarkedVector`, `Heap::m_markListSet`, `CloneDeserializer` | [`929c0df`](https://github.com/WebKit/WebKit/commit/929c0df4fd46d057005e2f6c953838dc2bad4b4d) hace que `MarkedVector::fill` se registre como raíz; [`f7c81e4`](https://github.com/WebKit/WebKit/commit/f7c81e42deb4fecc8aaf52139138cfbb0f481f01) separa `MarkedVector` de `ArgList.h`; [`4bd1aab`](https://github.com/WebKit/WebKit/commit/4bd1aab3f384604aa1cd8152c675fe5ca4c90bcc) amplía la interfaz | `c9880de` es el punto inicial público del comportamiento; las posteriores son evolución del mismo diseño | **UNVERIFIED** |
| `CloneSerializer/objectPool` | [`010c6bd`](https://github.com/WebKit/WebKit/commit/010c6bdfb0cde0485d31f0260ab9a046fa9b8567), separación `m_objectPool`/`m_keepAliveBuffer`, APIs `addToObjectPool`, tags y validator | [`3a900e1`](https://github.com/WebKit/WebKit/commit/3a900e192fe7c22dccc007fde344d3a373476175) corrige confusión de índices; [`442482a`](https://github.com/WebKit/WebKit/commit/442482adf1bd2ac184111e7745464cf6a0848b64) corrige protección GC de `CachedString`; [`cfe3893`](https://github.com/WebKit/WebKit/commit/cfe38930db92bdf1fecc71b3c014c861bf4033df) corrige carrera en `dumpIfTerminal` | Hay una cadena de correcciones structured-clone posterior, pero ninguna referencia Sony/PS4 | **UNVERIFIED** |

## Evidencia Sony pública

El espejo [FreeBSDKernel9-0/PS4OSSCode](https://github.com/FreeBSDKernel9-0/PS4OSSCode) importa `WebKit-601-1300` mediante [`d636699`](https://github.com/FreeBSDKernel9-0/PS4OSSCode/commit/d636699770323d7968a2c37955aa513bda5f8a37), con mensaje `Add WebKit WebKit-601-1300 (PS4 13.00-13.04)`. En sus archivos raw se observan los diseños pre-corrección:

- [`JSCell.cpp`](https://raw.githubusercontent.com/FreeBSDKernel9-0/PS4OSSCode/main/WebKit-601-1300/WebKit-601-1300/Source/JavaScriptCore/runtime/JSCell.cpp) usa `isString/isSymbol` y `static_cast`, sin `jsDynamicCast`/`jsSecureCast` en las rutas objetivo.
- [`ArgList.h`](https://raw.githubusercontent.com/FreeBSDKernel9-0/PS4OSSCode/main/WebKit-601-1300/WebKit-601-1300/Source/JavaScriptCore/runtime/ArgList.h) y [`ArgList.cpp`](https://raw.githubusercontent.com/FreeBSDKernel9-0/PS4OSSCode/main/WebKit-601-1300/WebKit-601-1300/Source/JavaScriptCore/runtime/ArgList.cpp) contienen `MarkedArgumentBuffer`, no `MarkedVector`.
- [`SerializedScriptValue.cpp`](https://raw.githubusercontent.com/FreeBSDKernel9-0/PS4OSSCode/main/WebKit-601-1300/WebKit-601-1300/Source/WebCore/bindings/js/SerializedScriptValue.cpp) contiene `m_gcBuffer`, `ObjectPool m_objectPool` y llamadas directas `m_gcBuffer.append`; no contiene `m_keepAliveBuffer`, `addToObjectPool`, `objectPoolTags` ni `validateSerializedValue`.

El directorio público `WebKit-616-1300` del mismo espejo no expone un árbol `Source` completo. En consecuencia, no puede servir como evidencia de presencia o ausencia de estas correcciones. Sony publica las fuentes OSS de `WebKit-601-1300` y `WebKit-616-1300` como fuentes asociadas a 13.00-, pero no una rama pública identificada como 13.50 o 13.52.

## Acotación razonable

| Pregunta | Respuesta | Clasificación |
|---|---|---|
| ¿La snapshot Sony 601-1300 contiene `2a042fe`? | No; conserva los casts anteriores | **DIRECT** |
| ¿La snapshot Sony 601-1300 contiene `c9880de`? | No; conserva `MarkedArgumentBuffer` | **DIRECT** |
| ¿La snapshot Sony 601-1300 contiene `010c6bd`? | No; conserva `m_gcBuffer` y el object pool antiguo | **DIRECT** |
| ¿Las variantes posteriores llegaron a una rama Sony? | No hay evidencia pública | **UNVERIFIED** |
| ¿13.52 usa código anterior o posterior a `2a042fe`? | No determinable con fuentes públicas | **UNVERIFIED** |
| ¿13.52 usa código anterior o posterior a `c9880de`? | No determinable con fuentes públicas | **UNVERIFIED** |
| ¿13.52 usa código anterior o posterior a `010c6bd`? | No determinable con fuentes públicas | **UNVERIFIED** |

La inferencia temporal correcta es únicamente que el árbol Sony 13.00–13.04 disponible públicamente es anterior a estos cambios upstream. No es válido extender esa inferencia a 13.50/13.52, porque faltan una snapshot Sony posterior, un diff Sony, un manifest de revisiones o bytes de código correlacionados.

## Referencias

[1]: https://www.playstation.com/en-us/oss/ps4/webkit/ "Sony PS4 WebKit OSS"
[2]: https://github.com/WebKit/WebKit/commit/2a042fede0e705bae4b8ce039b18442696ebb5ce "JSCell::toX"
[3]: https://github.com/WebKit/WebKit/commit/c9880de4a28b9a64a5e1d0513dc245d61a2e6ddb "MarkedVector and CloneDeserializer"
[4]: https://github.com/WebKit/WebKit/commit/010c6bdfb0cde0485d31f0260ab9a046fa9b8567 "CloneSerializer objectPool"
[5]: https://webkit.org/blog/12967/understanding-gc-in-jsc-from-scratch/ "JSC GC architecture"

**Clasificación final:** Sony 601-1300 y diffs upstream observables = **DIRECT**; variantes como continuidad de código = **STRONG_INDIRECT**; uso en PS4 13.52 = **UNVERIFIED**.
