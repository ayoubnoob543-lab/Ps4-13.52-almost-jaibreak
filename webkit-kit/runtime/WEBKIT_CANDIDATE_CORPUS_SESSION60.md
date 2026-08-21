# Corpus de candidatos WebKit/JSC posteriores a 601-1300

## Fuente principal

Índice PSDevWiki: https://www.psdevwiki.com/ps4/WebKit_Bugs

El índice separa bugs usados en explotación PS5 13.60, candidatos prometedores, bugs no probados y bugs históricos. No debe interpretarse como evidencia de presencia en PS4 13.52 salvo que la propia página lo indique.

## Candidatos destacados

| Candidato | Descripción del índice | Estado PS4 indicado | Valor para 13.52 |
|---|---|---|---|
| CVE-2026-43705 | Type confusion en `WebCore::TransformStream` al sobrescribir `Array.prototype[Symbol.iterator]` | “Working on PS4 FW 13.40? and PS5 FW 13.40?” | `STRONG_INDIRECT`, pero no específico 13.52 |
| CVE-2025-43429 | Heap buffer overflow en ICU vía `JSC String.prototype.normalize` | `FW <=?13.02?` | No llega públicamente a 13.52 |
| CVE-2024-54502 | UAF en `DocumentFontLoader::fontLoadingTimerFired` | Sin rango PS4 probado visible | Candidato estructural relacionado con fuentes, pero `UNVERIFIED` |
| CVE-2025-43541 | Type confusion | Sección “Untested” | `UNVERIFIED` |
| WriteBarrier.h OOB | Heap buffer overflow en JSC runtime | Sección “Untested” | `UNVERIFIED` |
| RenderLayer UAF | `computeCompositingRequirements` | `FW <=?12.50?` | No llega públicamente a 13.52 |
| TransformStream | Fix upstream `8fd92b1021d310b2580eb3ac7913911eb14dc476` | Candidato PS4 13.40? | Requiere diff/código del fix y correlación real |

## Advisory primario

WSA-2025-0010: https://webkitgtk.org/security/WSA-2025-0010.html

Enumera CVE-2025-14174, CVE-2025-43501, CVE-2025-43529, CVE-2025-43531, CVE-2025-43535, CVE-2025-43536 y CVE-2025-43541. El advisory describe impactos y versiones WPE/WebKitGTK afectadas, pero no demuestra que una build Sony PS4 13.52 contenga el código vulnerable.

## Prioridad de investigación

1. CVE-2026-43705/TransformStream: único candidato del índice explícitamente asociado a PS4 13.40? y con fix upstream identificable.
2. CVE-2024-54502/DocumentFontLoader: relación conceptual con fuentes y un UAF público; falta rango PS4.
3. CVE-2025-43529/DFG StoreBarrierInsertionPhase: primitive y fix bien documentados, pero presencia PS4 13.52 desconocida.
4. CVE-2025-43429/String.prototype.normalize: diff potencialmente pequeño, pero rango público sólo hasta 13.02?.

## Límite

El índice utiliza signos de interrogación en varios rangos. Son límites de investigación, no confirmaciones de firmware. Sin `libSceNKWebKit.sprx` 13.52 o una fuente Sony equivalente, todos los candidatos siguen siendo `UNVERIFIED` para retail 13.52.


## Detalles técnicos verificados

### CVE-2026-43705 / TransformStream

Fix upstream: https://github.com/WebKit/WebKit/commit/8fd92b1021d310b2580eb3ac7913911eb14dc476. El código vulnerable tenía sólo `ASSERT(results.size() == 3)`, que no opera en builds release, y hacía `dynamicDowncast<JSReadableStream>(results[1])->wrapped()` y equivalente sin comprobar el resultado. El fix añade un chequeo runtime del tamaño, comprueba ambos downcasts y devuelve `TypeError` si el resultado tiene tamaño o tipos inesperados. Añade LayoutTest `transform-stream-poisoned-iterator-crash.html`.

El índice PSDevWiki dice “Working on PS4 FW 13.40? and PS5 FW 13.40?”, pero no dice 13.52. El commit tiene copyright 2023 y el baseline Sony 601-1300 no devolvió el archivo por la ruta pública usada; por tanto la presencia en PS4 13.52 queda `UNVERIFIED`.

### CVE-2024-54502 / DocumentFontLoader

Project Zero: https://project-zero.issues.chromium.org/issues/374377963. La función `DocumentFontLoader::fontLoadingTimerFired()` llama a `loadDone()`, que puede liberar el `Document` durante un callback/event handler, y luego usa `m_document->frame()` y `frame->protectedLoader()->checkLoadComplete()`. La evidencia incluye testcase, fuente, log ASAN y fecha de fix Safari 18.2 (11 Dec 2024).

PSDevWiki lista commits probables: https://github.com/WebKit/WebKit/commit/4917f5eb6c8729b1f573a6f8f98665c4ce820849, https://github.com/WebKit/WebKit/commit/c8d323b1851ec55adde59e1c5ccaa61d9effc0a9 y https://github.com/WebKit/WebKit/commit/860c2ba52717fbcc180fa51464d1a92fc8d10acd. La propia página marca `Patched: Maybe` y `Tested: No on PS4 and on PS5`; no asigna firmware PS4 13.52.

### CVE-2025-43529 / DFG StoreBarrierInsertionPhase

Fix/commit: https://results.webkit.org/commit?repository_id=webkit&id=304602@main. El error consiste en marcar el `Phi` escapado pero no todos los valores transitivamente entrantes por `Upsilon`, pudiendo omitir StoreBarrier en el camino de GC concurrente. El fix modifica `Source/JavaScriptCore/dfg/DFGStoreBarrierInsertionPhase.cpp`. Advisory: https://webkitgtk.org/security/WSA-2025-0010.html; CVE-2025-43529 aparece como memoria corruptible con posible ejecución de código, pero no hay evidencia de presencia en Sony PS4.

### Estado local

La búsqueda en `/home/ubuntu/wpe-artifacts-2526/**/*` no encontró `DFGStoreBarrierInsertionPhase`, `DocumentFontLoader::fontLoadingTimerFired`, `createInternalTransformStream` ni `TransformStream.cpp`; el rootfs local no contiene el árbol fuente completo de WebKit.

## Fuentes

- https://www.psdevwiki.com/ps4/WebKit_Bugs
- https://project-zero.issues.chromium.org/issues/374377963
- https://github.com/WebKit/WebKit/commit/8fd92b1021d310b2580eb3ac7913911eb14dc476
- https://results.webkit.org/commit?repository_id=webkit&id=304602@main
- https://webkitgtk.org/security/WSA-2025-0010.html


## Evidencia específica del índice PSDevWiki sobre el rango 13.52

La página lista la correspondencia PS4 11.50–13.52 = Safari 17.0. En la sección “Vulnerabilities used for PS5 13.60 exploitation” aparecen tres entradas con título `PS4 FW ?6.00-13.52?`:

1. `JSC::JSCell::toX should use jsDynamicCast/jsSecureCast`, fix/commit atribuido a 2024-03-12; marcado “Maybe not as of PS5 FW 13.60”; no probado en PS4 ni PS5.
2. `Enhance JSC MarkedVector's interface to more closely match Vector's`, fix/commit atribuido a 2026-03-30; marcado “Maybe not as of PS5 FW 13.60”; no probado en PS4 ni PS5.
3. `WebCore::CloneSerializer/Deserializer's objectPool should match`, con fix upstream de 2024-01-26 y uso atribuido a Jordy en PS5 13.60; el rango `?6.00-13.52?` es editorial/incerto, no una confirmación retail.

El índice dice que los tres fueron usados por Jordy en un exploit de PS5 13.60, pero sus propias secciones “Tested” indican “Not tested yet on PS4 or PS5” para los dos primeros. Por tanto, la etiqueta `?6.00-13.52?` es una hipótesis de rango, no evidencia directa de PS4 13.52.

La misma página documenta que PS4 11.50–13.52 corresponde aproximadamente a Safari 17.0, pero no vincula una revisión concreta de WebKit Sony ni proporciona bytes retail.

## Implicación

Estos tres candidatos siguen siendo los mejores para correlación cuando aparezca `libSceNKWebKit.sprx`, pero el índice no permite declarar presencia en PS4 13.52. La evidencia actual es `STRONG_INDIRECT` como hipótesis de trabajo y `UNVERIFIED` para retail 13.52.
