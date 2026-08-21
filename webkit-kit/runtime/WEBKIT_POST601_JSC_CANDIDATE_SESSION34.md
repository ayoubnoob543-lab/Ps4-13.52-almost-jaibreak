# Candidato JSC posterior a WebKit-601-1300: CVE-2023-32439

## Resumen ejecutivo

El mejor candidato de las familias revisadas para una correlación estructural con WebKit-601-1300 es **CVE-2023-32439 / WebKit Bug 256567**. Tiene un commit pequeño y perfectamente identificable, un testcase público y afecta directamente a la representación de ubicaciones de memoria abstractas del DFG.

La evidencia no demuestra una vulnerabilidad en PS4 13.52 ni una ruta a native usermode. El candidato produce una condición de **colisión de heap locations en el compilador DFG**, que puede provocar razonamiento abstracto incorrecto y una mala optimización. Para afirmar una primitive de memoria concreta —y mucho menos ejecución nativa— todavía se necesitan bytes o una revisión Sony correlacionable.

## Identidad upstream

| Campo | Valor |
|---|---|
| CVE | CVE-2023-32439 |
| Bugzilla | https://bugs.webkit.org/show_bug.cgi?id=256567 |
| Commit fix | `52fe95e5805c735cc1fa4d6200fcaa1912efbfea` |
| Fecha del commit | 2023-05-10, según GitHub |
| Autor | `hyjorc1` |
| Enlace canónico | https://commits.webkit.org/263909@main |
| Título | `EnumeratorNextUpdateIndexAndMode and HasIndexedProperty should have different heap location kinds` |
| Archivos modificados | `DFGClobberize.h`, `DFGHeapLocation.cpp`, `DFGHeapLocation.h`, `DFGInPlaceAbstractState.cpp` y un testcase JSTests |

El commit explica que `EnumeratorNextUpdateIndexAndMode` y `HasIndexedProperty` son nodos DFG diferentes, pero podían introducir el mismo `LocationKind` en `DFGClobberize.h` y producir una colisión de hash.

## Diff exacto

El parche introduce el enum:

```cpp
EnumeratorNextUpdateIndexAndModeLoc
```

y lo imprime en `DFGHeapLocation.cpp`. En `DFGClobberize.h`, el código corregido propaga un `locationKind` separado en las ubicaciones asociadas al nuevo nodo, en lugar de reutilizar `HasIndexedPropertyLoc`.

El parche también endurece `DFGInPlaceAbstractState.cpp`: para proyecciones tuple comprueba `node->isTuple()`, exige que el estado abstracto haya sido limpiado y evita mezclar su valor con `forNode(node)` durante la convergencia del estado.

La comparación local entre el padre `be05571` y el commit fix confirma cambios en esos cinco archivos. Los SHA-256 de la copia descargada se registraron en el material de trabajo temporal; la fuente de autoridad sigue siendo el commit upstream y su árbol público.

## Testcase público

El commit añade:

```text
JSTests/stress/heap-location-collision-dfg-clobberize.js
```

Su contenido visible en GitHub crea `arr = [0]`, ejecuta una enumeración `for (let _ in arr)`, evalúa `0 in arr` y mantiene un bucle con watchdog. El test es una prueba de regresión/estabilidad del compilador, no un payload y no demuestra por sí mismo lectura/escritura arbitraria.

La existencia del testcase es `DIRECT_UPSTREAM`. No se ejecutó porque el objetivo de esta investigación es análisis estático y el entorno no dispone de un build autorizado de JSC correspondiente al commit.

## Correlación con WebKit-601-1300

El mirror público Sony es:

```text
FreeBSDKernel9-0/PS4OSSCode
commit d636699770323d7968a2c37955aa513bda5f8a37
path WebKit-601-1300/WebKit-601-1300
```

En 601-1300 existen `DFGClobberize.h`, `DFGHeapLocation.cpp`, `DFGHeapLocation.h` y `DFGInPlaceAbstractState.cpp`. La inspección directa muestra `HasIndexedPropertyLoc` y el uso de `DFGClobberize`, pero no encontró `EnumeratorNextUpdateIndexAndModeLoc` ni el identificador completo `EnumeratorNextUpdateIndexAndMode` en los archivos relevantes consultados.

La comparación es útil porque afecta a las mismas unidades conceptuales —`LocationKind`, `HeapLocation`, `DFGClobberize` y el merge del estado abstracto—, pero el resultado correcto es:

```text
601-1300: baseline estructural anterior
CVE-2023-32439 fix: introduce una distinción posterior
PS4 13.52: revisión exacta y backports UNVERIFIED
```

La ausencia del nuevo enum en 601-1300 no demuestra que PS4 13.52 lo carezca: Sony pudo incorporar el cambio, adaptarlo o mantener otra implementación.

## Diagnóstico estático preparado

Se añadió `webkit-kit/tools/jsc_vulnerability_condition_check.py`. El comprobador lee únicamente fuentes y genera JSON. Para CVE-2023-32439 busca señales en `DFGClobberize`, `DFGHeapLocation` y `DFGInPlaceAbstractState`:

| Resultado | Criterio |
|---|---|
| `FIXED_LIKE` | aparecen `EnumeratorNextUpdateIndexAndModeLoc` y la lógica separada de `EnumeratorNextUpdateIndexAndMode` |
| `VULNERABLE_LIKE` | aparece la colisión estructural antigua sin el enum separado |
| `UNVERIFIED` | faltan archivos o señales suficientes |

Se añadieron pruebas sintéticas para los estados `FIXED_LIKE` y `UNVERIFIED`. El diagnóstico no compila, carga ni ejecuta JSC.

Uso:

```bash
python3 webkit-kit/tools/jsc_vulnerability_condition_check.py \
  /ruta/a/fuentes-jsc \
  --output diagnostico.json
```

En un módulo retail ELF/SELF el resultado no debe promoverse automáticamente: primero se debe producir metadata estática y mantener la procedencia PS4 13.52 separada de cualquier comparación upstream.

## Capacidad de memoria y native usermode

La primitive demostrada por el commit es una **colisión de ubicaciones abstractas en el DFG**, con riesgo de optimización incorrecta. El commit no publica un read/write arbitrario, una corrupción de objeto o un control de flujo; el testcase tampoco demuestra esos efectos.

Por ello, la cadena siguiente no está demostrada:

```text
CVE-2023-32439
→ corrupción de memoria controlable
→ ejecución de código nativo usermode
```

Una ruta a native usermode exigiría evidencia adicional sobre el JSC concreto: compilación DFG/FTL activa, layout y representación de objetos, resultado de la optimización bajo el estado colisionado, mitigaciones de sandbox y una primitive posterior de control de memoria. Investigar esas condiciones de forma defensiva no equivale a desarrollar una cadena operativa.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| Commit, archivos y testcase upstream | `HISTORICAL_ONLY` |
| Bug de colisión de `LocationKind` descrito por el commit | `HISTORICAL_ONLY` |
| Mismos subsistemas conceptuales presentes en 601-1300 | `STRONG_INDIRECT_13.52` |
| Enum corregido presente en 601-1300 | `DISCARDED` |
| CVE-2023-32439 presente en PS4 13.52 | `UNVERIFIED` |
| CVE-2023-32439 corregido en PS4 13.52 | `UNVERIFIED` |
| Primitive de memoria arbitraria | `UNVERIFIED` |
| Capacidad native usermode | `UNVERIFIED` |

## Conclusión

CVE-2023-32439 es el candidato más limpio para correlación estática posterior a 601-1300 entre los casos analizados: diff pequeño, testcase público y estructuras DFG que sí existen en la referencia Sony. Sin embargo, no se ha encontrado una vulnerabilidad PS4 13.52 confirmada ni una primitive suficiente para native usermode.

La comprobación mínima cuando aparezcan bytes o una revisión Sony posterior es localizar conjuntamente:

```text
EnumeratorNextUpdateIndexAndMode
EnumeratorNextUpdateIndexAndModeLoc
HasIndexedPropertyLoc
DFGClobberize::clobberize
DFGHeapLocation::kind/hash/equality
DFGInPlaceAbstractState::merge/endBasicBlock
```

Después habrá que verificar la semántica de compilación y la procedencia exacta. Una coincidencia de strings o símbolos sin bytes PS4 13.52 sólo puede ser `STRONG_INDIRECT_13.52`.

## Referencias

[1]: https://github.com/WebKit/WebKit/commit/52fe95e5805c735cc1fa4d6200fcaa1912efbfea "WebKit fix commit for Bug 256567"
[2]: https://bugs.webkit.org/show_bug.cgi?id=256567 "WebKit Bug 256567"
[3]: https://commits.webkit.org/263909@main "Canonical WebKit commit"
[4]: https://github.com/FreeBSDKernel9-0/PS4OSSCode/tree/d636699770323d7968a2c37955aa513bda5f8a37/WebKit-601-1300 "Sony WebKit-601-1300 mirror"
[5]: https://nvd.nist.gov/vuln/detail/CVE-2023-32439 "NVD CVE-2023-32439"
