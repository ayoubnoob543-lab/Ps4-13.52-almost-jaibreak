# Investigación profunda WebKit/JSC posterior a 601-1300

**Fecha:** 2026-08-21
**Objetivo:** priorizar vulnerabilidades públicas con diff/fix/testcase que puedan correlacionarse con PS4 13.52 sin ejecutar exploits.

## 1. Estado de la evidencia

El índice público de PSDevWiki asigna PS4 11.50–13.52 aproximadamente a Safari/WebKit 17.0, pero no proporciona una revisión Sony exacta. La página marca tres candidatos usados en una cadena PS5 13.60 con títulos `?6.00-13.52?`, pero también indica que dos no fueron probados en PS4/PS5. Las interrogaciones son una incertidumbre editorial, no prueba directa de firmware.

Fuentes:

- https://www.psdevwiki.com/ps4/WebKit_Bugs
- https://github.com/WebKit/WebKit
- https://webkitgtk.org/security/WSA-2025-0010.html
- https://project-zero.issues.chromium.org/issues/374377963

## 2. Candidatos principales

| Candidato | Primitive histórica | Fix/testcase | Evidencia PS4 | Estado 13.52 |
|---|---|---|---|---|
| JSCell::toX | type confusion por cast no seguro | commit 2a042fe; no testcase detallado en el índice | usado en exploit PS5 13.60; PS4 no probado | `STRONG_INDIRECT` como hipótesis, `UNVERIFIED` retail |
| MarkedVector / GC | UAF por buffers no escaneados por GC | commit 4bd1aab; usado en PS5 13.60 | PS4 13.52 sólo por rango con `?` | `STRONG_INDIRECT`, `UNVERIFIED` |
| CloneSerializer/Deserializer objectPool | desincronización de pool y referencias; UAF/OOM histórico | commit 010c6bd; LayoutTest structured-clone | no probado en PS4/PS5 según página | `HISTORICAL/INDIRECT`, `UNVERIFIED` |
| TransformStream (CVE-2026-43705) | type confusion al envenenar Array iterator | commit 8fd92b1; LayoutTest nuevo | PSDevWiki: “Working on PS4 13.40?” | `STRONG_INDIRECT`, no específico 13.52 |
| DocumentFontLoader (CVE-2024-54502) | UAF tras `loadDone()` y callback que libera Document | Project Zero testcase/ASAN; fixes probables 4917f5e, c8d323b, 860c2ba | PSDevWiki: no en PS4 | `HYPOTHESIS`, no confirmado |
| DFG StoreBarrier (CVE-2025-43529) | UAF potencial por no propagar escape Phi→Upsilon | commit 304602; advisory WSA-2025-0010 | no evidencia Sony | `HISTORICAL/UPSTREAM_ONLY`, no confirmado |
| String.normalize ICU (CVE-2025-43429) | heap overflow en normalización NFKC | testcase público; PSDevWiki probado hasta 12.00 y no parcheado 13.02 según fechas | rango `<=?13.02?` | no llega públicamente a 13.52 |
| DNG/CVE-2025-43300 | OOB write en procesamiento DNG | PoC PS4/PS5; PSDevWiki probado hasta 12.02, parcheado 12.50 | no llega a 13.52 | descartado como candidato 13.52 |

## 3. Detalles técnicos verificados

### 3.1 TransformStream / CVE-2026-43705

Commit: https://github.com/WebKit/WebKit/commit/8fd92b1021d310b2580eb3ac7913911eb14dc476

El código vulnerable, en `Source/WebCore/Modules/streams/TransformStream.cpp`, convierte el resultado de `createInternalTransformStreamFromTransformer` a una secuencia IDL. Sólo usaba `ASSERT(results.size() == 3)`, que no valida en builds release. Luego hacía downcast dinámico de las posiciones readable/writable y desreferenciaba el resultado sin comprobarlo. El fix añade:

1. chequeo runtime de que el tamaño sea 3;
2. comprobación de `dynamicDowncast<JSReadableStream>` y `JSWritableStream`;
3. `TypeError` para tamaño/tipos inesperados;
4. LayoutTest `transform-stream-poisoned-iterator-crash.html`.

La entrada maliciosa sustituye los valores producidos por el builtin al sobrescribir `Array.prototype[Symbol.iterator]`. La fuente pública describe una type confusion controlable y una llamada virtual posterior sobre datos controlados, pero no prueba presencia en Sony PS4 13.52. La página PSDevWiki sólo dice “Working on PS4 FW 13.40?” y no da 13.52.

La ruta raw del baseline `d636699770323d7968a2c37955aa513bda5f8a37` no devolvió `TransformStream.cpp`; esto no demuestra ausencia porque el commit no se pudo recuperar por esa URL y Sony puede haber backporteado APIs. El archivo upstream visible tiene copyright 2023, lo que hace improbable que sea una estructura de WebKit 601 antigua sin backport, pero queda `UNVERIFIED`.

### 3.2 DocumentFontLoader / CVE-2024-54502

Fuente primaria: https://project-zero.issues.chromium.org/issues/374377963

La función `DocumentFontLoader::fontLoadingTimerFired()` llama a `m_document->protectedCachedResourceLoader()->loadDone(LoadCompletionType::Finish)`. Un EventHandler malicioso puede provocar que se libere el `Document` durante ese callback. Al volver, el mismo método usa `m_document->frame()` y `frame->protectedLoader()->checkLoadComplete()`, creando un UAF.

Project Zero incluye `child.html`, `index.html`, una fuente TTF, `server.py` y un log ASAN. El bug fue corregido en Safari 18.2. PSDevWiki lista commits probables 4917f5e, c8d323b y 860c2ba, pero marca el estado como `Maybe` y “No on PS4 and on PS5”. La relación con CSSFontFace es conceptual por el subsistema de carga de fuentes, pero no demuestra que el layout posterior de CSSFontFace lo active en PS4 13.52.

### 3.3 DFG StoreBarrier / CVE-2025-43529

Commit: https://results.webkit.org/commit?repository_id=webkit&id=304602@main

La fase DFG marca un `Phi` que escapa, pero no propaga la marca a todos los valores entrantes transitivos por `Upsilon`. Si un valor antiguo puede exponer el `Phi` a GC concurrente, se omite un StoreBarrier posterior y puede aparecer un UAF. El commit modifica `DFGStoreBarrierInsertionPhase.cpp` y el advisory WSA-2025-0010 lo trata como corrupción de memoria.

El laboratorio local WPE no contiene `DFGStoreBarrierInsertionPhase.cpp` ni el árbol fuente completo. No existe evidencia de que el WebKit Sony 13.52 contenga la fase vulnerable o que tenga las mismas condiciones de GC/JIT.

### 3.4 CloneSerializer/Deserializer

PSDevWiki describe que `m_gcBuffer` se usaba simultáneamente como object pool referenciado por `ObjectReferenceTag` y como buffer keep-alive. Esto podía desincronizar serializer/deserializer y dejar objetos no escaneados. El fix `010c6bd` y el LayoutTest de structured clone son evidencia upstream. La página indica “Maybe not as of PS5 FW 13.60” y “Not tested yet on PS4 or PS5”, por lo que no es una confirmación de PS4 13.52.

### 3.5 MarkedVector y JSCell::toX

Son los mejores candidatos del índice por su asociación con la cadena PS5 13.60. Sin embargo, el mismo índice marca `Tested: Not tested yet on PS4 or PS5` para `JSCell::toX` y `MarkedVector`. Por tanto, `?6.00-13.52?` no puede convertirse en `DIRECT_13.52`.

## 4. Comparación con el material local

El rootfs WPE 2.52.6 no contiene el árbol fuente completo ni coincidencias para `DFGStoreBarrierInsertionPhase`, `DocumentFontLoader::fontLoadingTimerFired`, `createInternalTransformStream` o `TransformStream.cpp`. El PUP 13.50/13.52 sólo aporta contenedores SLB2 y entradas opacas. El dump parcial de `libkernel_sys` no es WebKit.

## 5. Ranking práctico

### Prioridad 1: MarkedVector/CloneSerializer/JSCell::toX

No porque estén confirmados, sino porque son las tres familias que PSDevWiki relaciona con una cadena de explotación PS5 13.60 y las etiqueta tentativamente hasta 13.52. La pieza mínima que resolvería la cuestión es una función o tabla de `libSceNKWebKit.sprx` 13.52 que conserve o descarte las estructuras relevantes.

### Prioridad 2: DocumentFontLoader

Tiene UAF real, testcase y relación temática con fuentes. El índice dice que no fue probado en PS4, pero el código puede ser un candidato de regresión si Sony mantuvo una implementación cercana. Requiere encontrar el fix exacto y comparar la estructura del loader.

### Prioridad 3: TransformStream

Tiene diff pequeño, testcase y una condición de type confusion muy clara. Es un candidato moderno, pero la antigüedad de la API y la falta de evidencia PS4 13.52 lo hacen más débil que las tres familias ya vinculadas al exploit PS5 13.60.

### Prioridad 4: DFG StoreBarrier

Tiene primitive conceptual fuerte, pero depende de configuración JIT/GC y de una fase DFG que no aparece en nuestro baseline local. No hay conexión PS4 pública.

## 6. Diagnóstico seguro preparado

Cuando aparezca un módulo legible, el detector debe buscar:

- `TransformStream.cpp`: constantes/mensajes de `unexpected number of values`, `JSReadableStream`, `JSWritableStream`, comprobaciones de downcast;
- `DocumentFontLoader`: referencias a `loadDone`, `fontLoadingTimerFired`, retención fuerte de `Document` y orden de callbacks;
- DFG: `StoreBarrierInsertionPhase`, propagación transitiva `Phi`/`Upsilon`;
- Clone: `m_gcBuffer`, `ObjectReferenceTag`, `MarkedVector`, `MarkedArgumentBuffer`;
- JSCell: usos de `toX`, `jsDynamicCast`, `jsSecureCast` y validación de StructureID.

El resultado debe ser `MATCH`, `PARTIAL`, `NO MATCH` o `UNVERIFIED`; una coincidencia no constituye exploit.

## Conclusión

La búsqueda profunda sí produjo un mapa nuevo y útil: hay tres candidatos modernos con rangos editoriales hasta 13.52, pero el propio material público dice que no fueron probados en PS4. Hay dos bugs upstream recientes con testcases y fixes perfectamente identificables —TransformStream y DocumentFontLoader—, pero no existe evidencia retail de 13.52.

**Conclusión final:** `STRONG_INDIRECT_13.52` para MarkedVector/CloneSerializer/JSCell::toX como hipótesis de trabajo; `HYPOTHESIS` para DocumentFontLoader; `HISTORICAL/UPSTREAM_ONLY` para CVE-2025-43529; `UNVERIFIED` para cualquier primitive o native usermode en PS4 13.52. El bloqueo concreto sigue siendo una extracción legible de `libSceNKWebKit.sprx` o una publicación técnica del workaround 13.52.
