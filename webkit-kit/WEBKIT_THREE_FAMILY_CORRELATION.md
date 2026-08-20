# Correlación estática de tres familias WebKit para PS4 13.52

**Fecha:** 2026-08-20  
**Alcance:** `JSCell::toX`, `JSC::MarkedVector` y `CloneSerializer/CloneDeserializer/objectPool`.  
**Método:** comparación de código y metadatos públicos; no se ejecutaron exploits, payloads ni binarios contra dispositivos.

## Regla de evidencia

Este documento prepara una correlación futura; **no confirma ninguna vulnerabilidad en PS4 13.52**. Los corpus locales disponibles son WPE 2.52.6 y referencias públicas WebKit-601-1300/616-1300. El manifiesto local identifica 601-1300 y 616-1300 como referencias de 13.00–13.04, no como código exacto 13.52. Los módulos retail necesarios siguen ausentes.

Se distinguen dos preguntas que no deben mezclarse:

1. **Detección de familia:** ¿el módulo contiene la misma función/clase/ruta semántica?
2. **Estado de corrección:** ¿la implementación corresponde al patrón anterior a la corrección o al patrón posterior?

Un `MATCH` de familia no equivale a una vulnerabilidad confirmada.

## 1. JSCell::toX y validación de tipos

### Referencia pública principal

El commit upstream `2a042fede0e705bae4b8ce039b18442696ebb5ce`, del 2024-03-11, está titulado `[JSC] JSCell::toX should use jsDynamicCast/jsSecureCast`, enlaza Bugzilla 270797 y modifica `Source/JavaScriptCore/runtime/JSCell.cpp` [1]. El cambio afecta estas funciones:

| Función | Patrón anterior observable | Patrón posterior observable |
|---|---|---|
| `JSC::JSCell::toPrimitive` | `isString()`, `isSymbol()`, `isHeapBigInt()`, `static_cast<const JSString*>`, `static_cast<const Symbol*>`, `static_cast<const JSBigInt*>`, `static_cast<const JSObject*>` | `jsDynamicCast<const JSString*>`, `jsDynamicCast<const Symbol*>`, `jsDynamicCast<const JSBigInt*>`, `jsSecureCast<const JSObject*>` |
| `JSC::JSCell::toNumber` | Las mismas comprobaciones `is*` y `static_cast` | `jsDynamicCast` para string/symbol/bigint y `jsSecureCast` para objeto |
| `JSC::JSCell::toObjectSlow` | `ASSERT(!isObject())`, ramas `isString`/`isHeapBigInt`/`isSymbol` y `static_cast` | `jsDynamicCast<const JSString*>`, `jsDynamicCast<const JSBigInt*>` y `jsSecureCast<const Symbol*>` |

El commit se describe como una mejora de calidad general y añade una aserción de release para el caso final; no debe resumirse como una prueba de explotación. La relevancia para 13.52 proviene únicamente de la referencia comunitaria que lo etiqueta con el rango incierto `?6.00-13.52?`, no de bytes retail [4].

### Qué buscar en un módulo retail

La búsqueda debe combinar, en este orden:

| Nivel | Señales |
|---|---|
| Funcional | Xrefs o funciones que implementen conversiones `JSCell`→primitive/number/object; llamadas consecutivas a ramas para String, Symbol, BigInt y Object |
| Strings/símbolos | `JSCell`, `toPrimitive`, `toNumber`, `toObjectSlow`, `jsDynamicCast`, `jsSecureCast`, `isHeapBigInt`, `auditStructureID` |
| Estructural | Tres rutas de conversión con orden String/Symbol/BigInt y una ruta final Object; llamadas a dispatch de `toPrimitive`, `toNumber` o `toObject` |
| Estado anterior a la corrección | Predominio de tests `isString/isSymbol/isHeapBigInt/isObject` seguido de casts no comprobados |
| Estado posterior a la corrección | Ramas `jsDynamicCast` para tipos concretos y `jsSecureCast` en la rama final; posible validación de `structureID` |

En un binario optimizado los nombres pueden desaparecer. En ese caso, la ausencia de strings no es `NO MATCH`; sólo reduce la evidencia a estructural.

### Criterios

- **MATCH — familia:** se identifican las tres conversiones y el orden de tipos mediante símbolos, xrefs o una firma estructural fuerte.
- **PARTIAL MATCH — familia:** sólo se identifica una o dos conversiones, o la secuencia aparece sin poder distinguir `JSCell` de una rutina de conversión genérica.
- **NO MATCH — familia:** se descartan las funciones tras revisar símbolos, strings y código relevante, o el módulo carece del componente JSC correspondiente.
- **VULNERABLE-LIKE:** MATCH de familia más evidencia del patrón anterior, sin `jsDynamicCast/jsSecureCast` en las rutas equivalentes.
- **FIXED-LIKE:** MATCH de familia más evidencia del patrón posterior. No significa que el parche upstream esté presente byte por byte.
- **UNVERIFIED:** sólo hay strings, nombres de documentación o similitud estadística.

## 2. JSC::MarkedVector, GC y contenedores

### Referencia pública principal

El commit `c9880de4a28b9a64a5e1d0513dc245d61a2e6ddb`, del 2023-04-17, se titula `CloneDeserializer::deserialize() should store cell pointers in a MarkedVector` y enlaza Bugzilla 254797. Su mensaje explica que unos `Vector` ordinarios contenían punteros a celdas recién creadas que el GC no podía escanear; el cambio refactoriza `MarkedArgumentBuffer` hacia `MarkedVector` y sustituye esos contenedores en `CloneDeserializer::deserialize()` [2].

El commit modifica, entre otros:

- `Source/JavaScriptCore/runtime/ArgList.h` y `ArgList.cpp`.
- `Source/JavaScriptCore/heap/Heap.cpp`, `Heap.h` y `HeapInlines.h`.
- `Source/WebCore/bindings/js/SerializedScriptValue.cpp`.
- `Source/WebCore/Modules/webaudio/AudioWorkletProcessor.cpp/.h`.

Las señales relevantes del cambio son `MarkedVectorBase`, `MarkedVectorWithSize`, `markLists`, `addMarkSet`, `CrashOnOverflow`, `slowEnsureCapacity`, `expandCapacity`, `slowAppend`, y la sustitución de `MarkedArgumentBufferBase` en el conjunto de raíces del heap.

Un commit posterior, `4bd1aab3f384604aa1cd8152c675fe5ca4c90bcc`, del 2026-03-30, amplía la interfaz de `MarkedVector` para acercarla a `Vector`: `span`, `mutableSpan`, `operator[]`, `fillWith`, `data`, constructor de capacidad inicial, soporte de punteros en ports de 32 bits y tests API [3]. **No debe utilizarse como el parche histórico original para 13.52**, porque es posterior y principalmente de interfaz.

### Qué buscar en un módulo retail

| Nivel | Señales |
|---|---|
| Funcional | Tipos marcados que almacenan `JSValue` o punteros a `JSCell` y se registran en el conjunto de raíces del heap |
| Strings/símbolos | `MarkedVector`, `MarkedVectorBase`, `MarkedArgumentBuffer`, `markLists`, `addMarkSet`, `slowEnsureCapacity`, `CrashOnOverflow`, `SerializedScriptValue`, `CloneDeserializer` |
| Estructural | Un contenedor dinámico con tamaño/capacidad, crecimiento controlado, barrera/registro en `Heap`, recorrido de elementos por un visitor y handler de overflow |
| Estado anterior a la corrección | `CloneDeserializer::deserialize()` usa `Vector` para punteros a celdas recién creadas; el heap sólo conoce las estructuras antiguas o no existe una ruta equivalente de marcado |
| Estado posterior a la corrección | Punteros almacenados en `MarkedVector`, clase base registrada en `Heap::markListSet`, recorrido por `markLists`, y overflow explícito `CrashOnOverflow` o equivalente |

La equivalencia de nombres no es obligatoria: un fork Sony puede renombrar tipos o integrar el código. Por eso debe buscarse también la relación entre almacenamiento de celdas, registro de raíces y deserialización.

### Criterios

- **MATCH — familia:** se observa un contenedor marcado que se integra con el GC y se usa en una ruta de JSC/WebCore que almacena celdas.
- **PARTIAL MATCH — familia:** existe un contenedor marcado o un registro de raíces, pero no se puede conectar con `CloneDeserializer` ni con el flujo de serialización.
- **NO MATCH — familia:** sólo aparecen `Vector` ordinarios y no se identifica ningún mecanismo equivalente de marcado para la ruta examinada.
- **VULNERABLE-LIKE:** la ruta de deserialización almacena celdas en un vector no visible para el GC, o el equivalente carece de registro/barrera.
- **FIXED-LIKE:** la ruta usa un contenedor marcado y éste aparece en el conjunto de raíces visitado por el GC.
- **UNVERIFIED:** sólo se detectan strings `MarkedVector` o una similitud de nombres sin xrefs.

## 3. CloneSerializer / CloneDeserializer / objectPool

### Referencias públicas principales

El commit `010c6bdfb0cde0485d31f0260ab9a046fa9b8567`, del 2024-01-26, se titula `CloneSerializer/Deserializer's objectPool should match`, enlaza Bugzilla 265975 y modifica `Source/WebCore/bindings/js/SerializedScriptValue.cpp` [4]. El parche separa dos propósitos que antes compartían `m_gcBuffer`:

- `m_objectPool`: orden de objetos al que apuntan `ObjectReferenceTag`.
- `m_keepAliveBuffer`: mantener objetos vivos durante la serialización.

También introduce o renombra operaciones observables: `writeObjectReferenceIfDupe`, `addToObjectPool`, `addToObjectPoolIfNotDupe`, `CloneDeserializer::addToObjectPool`, `objectPoolTags`, `appendObjectPoolTag` y `validateSerializedResult`. El mensaje del commit indica que se eliminan adiciones redundantes y tres adiciones de `BigInt` en la ruta del deserializador.

El commit anterior `c9880de...` es también relevante porque corrige la visibilidad ante el GC en `CloneDeserializer::deserialize()` mediante `MarkedVector` [2]. Por tanto, las familias 2 y 3 están relacionadas, pero no son la misma señal:

| Familia | Pregunta que responde |
|---|---|
| MarkedVector | ¿El GC puede ver y marcar las celdas almacenadas durante la deserialización? |
| objectPool | ¿Serializer y deserializer mantienen el mismo orden/tipo de referencias y separan pool de retención? |

### Qué buscar en un módulo retail

| Nivel | Señales |
|---|---|
| Funcional | Rutas de `structuredClone`, `SerializedScriptValue`, serialización de arrays/maps/sets/BigInt/ArrayBuffer y lectura/escritura de referencias |
| Strings/símbolos | `CloneSerializer`, `CloneDeserializer`, `SerializedScriptValue`, `ObjectReferenceTag`, `m_gcBuffer`, `m_objectPool`, `m_keepAliveBuffer`, `addToObjectPool`, `addToObjectPoolIfNotDupe`, `writeObjectReferenceIfDupe`, `validateSerializedResult` |
| Estructural | Dos estados que mantienen referencias y retención; tabla/lista de tags; índices de objeto; operaciones paralelas serializer/deserializer; manejo de duplicados |
| Estado anterior a la corrección | Un mismo buffer desempeña simultáneamente funciones de pool indexado y keep-alive; llamadas redundantes o desalineadas al añadir Map/Set/iterator/BigInt |
| Estado posterior a la corrección | Pool y keep-alive separados; operaciones explícitas de alta; tags comparables; validator opcional de Debug; orden de serializer/deserializer auditado |

`validateSerializedResult` y la opción `validateSerializedValue` son señales de una implementación posterior; su ausencia no demuestra vulnerabilidad, especialmente en builds Release. De igual forma, la presencia de `m_objectPool` por sí sola no demuestra que esté separado de la retención.

### Criterios

- **MATCH — familia:** se identifican ambas rutas de serialización y deserialización con pool de referencias y tags/índices.
- **PARTIAL MATCH — familia:** sólo se identifica una ruta, o hay `SerializedScriptValue` pero no se reconstruye el mecanismo de referencias.
- **NO MATCH — familia:** no existe el componente de structured clone/serialized script value en el módulo analizado.
- **VULNERABLE-LIKE:** un único buffer o estructura se usa para indexación de referencias y keep-alive, o existen desalineamientos demostrables en altas serializer/deserializer.
- **FIXED-LIKE:** pool indexado y buffer de retención están separados y las altas están etiquetadas/sincronizadas.
- **UNVERIFIED:** sólo aparecen nombres o strings, sin flujo de control ni datos suficientes.

## 4. Matriz consolidada para un módulo retail

| Familia | Evidencia mínima para `MATCH` | Evidencia adicional para `VULNERABLE-LIKE` | Evidencia adicional para `FIXED-LIKE` |
|---|---|---|---|
| JSCell::toX | Tres conversiones equivalentes y ramas de tipo identificables | Casts no comprobados en las rutas equivalentes | `jsDynamicCast`/`jsSecureCast` o patrón semánticamente equivalente |
| MarkedVector/GC | Contenedor marcado conectado al heap y a almacenamiento de celdas | Vector no marcado en la ruta de deserialización | Contenedor registrado en raíces, visitor y overflow controlado |
| Clone/objectPool | Serializer y deserializer con pool de referencias | Pool y keep-alive confluyen o altas desalineadas | `objectPool`/keep-alive separados, tags y altas sincronizadas |

### Promoción de resultados

| Resultado | Condición |
|---|---|
| `MATCH` | Coincidencia de familia y flujo de control, con al menos dos clases de evidencia independientes: símbolos/xrefs, strings/relocaciones o estructura de código |
| `PARTIAL MATCH` | Coincidencia de una parte de la familia o una sola clase de evidencia fuerte |
| `NO MATCH` | Se revisó el componente correspondiente y no aparece la familia ni una implementación equivalente |
| `UNVERIFIED` | Sólo hay documentación, nombres aislados o similitud estadística |
| `CONFIRMED_13.52` | Reservado exclusivamente para bytes retail 13.52 verificados, procedencia coherente y correlación reproducible; no asignado actualmente |

## 5. Procedimiento futuro, sin ejecutar el módulo

Cuando exista un módulo retail, el análisis debe ser pasivo:

```text
1. SHA-256 y manifest de procedencia.
2. Identificación SELF/ELF y extracción sólo estructural.
3. PT_LOAD, Build ID, símbolos, imports/exports, relocaciones y strings.
4. Búsqueda de nombres y cadenas de cada familia.
5. Localización de xrefs a strings, imports y tablas de funciones.
6. Comparación de ventanas normalizadas de instrucciones contra referencias públicas.
7. Clasificación independiente de familia y estado vulnerable/corregido.
8. Informe con MATCH/PARTIAL MATCH/NO MATCH y evidencia que lo sostiene.
```

Los resultados no deben convertir una coincidencia con WPE 2.52.6 ni con WebKit-601/616 en equivalencia retail. Los offsets absolutos, gadgets, ABI y estructuras de Sony deben permanecer `MISSING` hasta que los bytes target permitan verificarlos.

## 6. Estado actual

| Elemento | Estado |
|---|---|
| Referencia upstream JSCell y diff exacto | `CONFIRMED_PUBLIC_REFERENCE` |
| Referencia upstream MarkedVector y diff exacto | `CONFIRMED_PUBLIC_REFERENCE` |
| Referencia upstream objectPool y diff exacto | `CONFIRMED_PUBLIC_REFERENCE` |
| Correlación contra bytes retail 13.52 | `NOT_RUN / MISSING_BYTES` |
| Vulnerabilidad confirmada en PS4 13.52 | `NONE` |

## Referencias

[1]: https://github.com/WebKit/WebKit/commit/2a042fede0e705bae4b8ce039b18442696ebb5ce "WebKit commit: JSCell::toX should use jsDynamicCast/jsSecureCast"
[2]: https://github.com/WebKit/WebKit/commit/c9880de4a28b9a64a5e1d0513dc245d61a2e6ddb "WebKit commit: CloneDeserializer::deserialize() should store cell pointers in a MarkedVector"
[3]: https://github.com/WebKit/WebKit/commit/4bd1aab3f384604aa1cd8152c675fe5ca4c90bcc "WebKit commit: Enhance MarkedVector's interface to more closely match Vector's"
[4]: https://github.com/WebKit/WebKit/commit/010c6bdfb0cde0485d31f0260ab9a046fa9b8567 "WebKit commit: CloneSerializer/Deserializer's objectPool should match"
[5]: https://bugs.webkit.org/show_bug.cgi?id=270797 "WebKit Bugzilla 270797"
[6]: https://bugs.webkit.org/show_bug.cgi?id=254797 "WebKit Bugzilla 254797"
[7]: https://bugs.webkit.org/show_bug.cgi?id=265975 "WebKit Bugzilla 265975"
[8]: https://www.psdevwiki.com/ps4/WebKit_Bugs "PS4 Developer Wiki: WebKit Bugs"
