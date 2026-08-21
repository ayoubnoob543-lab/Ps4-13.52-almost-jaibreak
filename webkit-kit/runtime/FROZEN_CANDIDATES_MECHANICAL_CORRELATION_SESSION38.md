# Estado congelado: correlación mecánica de candidatos WebKit/JSC

## Alcance

Esta sesión congela tres líneas ya investigadas y no añade nuevas CVE ni búsquedas públicas:

1. `MarkedVector` / GC como candidato principal.
2. `CloneSerializer` / `CloneDeserializer` / `objectPool` como candidato principal relacionado.
3. `CSSFontFace` como candidato secundario.

La salida es una preparación de diagnóstico. No confirma ninguna vulnerabilidad ni ningún estado de PS4 13.52.

## Baseline público disponible

El baseline Sony público es `WebKit-601-1300`, commit `d636699770323d7968a2c37955aa513bda5f8a37`, asociado documentalmente a PS4 13.00–13.04.

Anclas verificadas:

| Archivo | Git blob | Tamaño | Observación |
|---|---|---:|---|
| `Source/JavaScriptCore/runtime/JSCell.cpp` | `2c403c813fb38568b0e60ce78989ddea4c953c12` | 7742 B | conversiones con checks `is*` y casts estáticos en las rutas observadas |
| `Source/JavaScriptCore/heap/Heap.cpp` | `842625eae6341d18eda50bdc5549ea11e03be2e1` | 44918 B | registro de `MarkedArgumentBuffer::markLists` |
| `Source/JavaScriptCore/runtime/ArgList.h` | `fdfe00102cd38701e93ce759a7223aac4c03899e` | 4330 B | `MarkedArgumentBuffer`, no interfaz posterior `MarkedVector` |
| `Source/WebCore/bindings/js/SerializedScriptValue.cpp` | `6786119069805e75b7c94addcd71527fafd7ebe3` | 92486 B | `CloneDeserializer` con `m_gcBuffer` y referencias `ObjectReferenceTag` |

La referencia `WebKit-616-1300` no conserva un árbol `Source` equivalente en el corpus accesible. Su resultado correcto es `UNVERIFIED`, no `NO MATCH`.

## Invariantes mecánicas

### MarkedVector / GC

Un `MATCH` requiere un contenedor marcado conectado simultáneamente con el heap y con una ruta que almacene `JSCell`/`JSValue`, idealmente deserialización. Las señales principales son `MarkedVector`, `MarkedVectorBase`, `markLists`, `addMarkSet`, `Heap::markListSet`, `slowEnsureCapacity` y `CrashOnOverflow`.

`VULNERABLE_LIKE` sólo puede asignarse si la ruta almacena celdas en un vector no visible para el GC o carece de registro/barrera equivalente. `FIXED_LIKE` exige un contenedor marcado registrado en raíces y visitado por el GC. Nombres aislados producen `UNVERIFIED`.

El 601-1300 muestra `MarkedArgumentBuffer` y registro de listas, pero no prueba si una futura rama Sony cambió a `MarkedVector` ni si un backport privado corrigió la ruta.

### CloneSerializer / CloneDeserializer / objectPool

Un `MATCH` requiere ambas rutas, pool de referencias y tags/índices comparables. `VULNERABLE_LIKE` requiere demostrar que un único buffer sirve a la vez para pool indexado y keep-alive, o que las altas serializer/deserializer quedan desalineadas. `FIXED_LIKE` requiere separación efectiva entre `m_objectPool` y `m_keepAliveBuffer`, tags compatibles y altas sincronizadas.

En 601-1300 se observa `m_gcBuffer` en el deserializador, lectura de índices para `ObjectReferenceTag` y `m_objectPool` en la serialización. Esto es evidencia directa del baseline, pero no demuestra por sí solo que pool y retención estén fusionados.

### CSSFontFace

Se conserva como línea secundaria. La evidencia pública posterior a 11.02 documenta `m_propertiesOrCSSConnection`, cambios de layout y un modelo de ownership distinto. La primitive antigua basada en `m_featureSettings` no es transferible automáticamente. El estado de 13.52 sigue `UNVERIFIED`.

## Diagnóstico local

Se añadió `webkit-kit/tools/correlate_three_families.py`. El programa:

- consume `webkit-kit/three_family_signatures.json`;
- analiza sólo texto fuente por defecto;
- puede incluir `.txt`/`.json` sólo con `--include-docs`;
- distingue `MATCH`, `PARTIAL MATCH`, `NO MATCH`;
- separa `VULNERABLE_LIKE`, `FIXED_LIKE` y `UNVERIFIED`;
- fija siempre `status_13_52` en `UNVERIFIED`;
- no compila, importa, ejecuta, descifra ni atribuye procedencia.

La exclusión de documentación por defecto es necesaria: al analizar un workspace completo, los informes contienen literalmente los nombres de las familias y producirían falsos positivos. La ejecución correcta debe apuntar a un árbol fuente o a archivos concretos, no a un corpus documental mezclado.

Ejemplo:

```bash
python3 webkit-kit/tools/correlate_three_families.py \
  /ruta/a/extraccion_fuente_autorizada \
  --output correlation.json
```

Para un módulo binario retail se debe usar primero el analizador ELF/SELF existente; este correlador no convierte bytes en símbolos ni permite declarar equivalencia semántica.

## Separación de la cadena

La investigación mantiene estas etapas separadas:

```text
WebKit/JSC
→ condición de bug o estado fixed-like
→ primitive de memoria (si se demuestra)
→ ejecución/control dentro de WebContent
→ límites de sandbox
→ siguiente etapa independiente
```

`MATCH` sólo identifica una familia. `VULNERABLE_LIKE` sólo indica que una estructura parece anterior a un fix. Ninguno de los dos demuestra una primitive controlable, escape de sandbox, ejecución nativa o jailbreak.

## Resultado de validación local

Sobre el workspace completo, usando únicamente archivos fuente y excluyendo informes/documentación, el correlador inspeccionó 12 archivos y devolvió `NO MATCH / UNVERIFIED` para las tres familias. Este resultado no es una conclusión sobre WebKit-601-1300: el checkout actual no contiene el árbol completo de fuentes Sony; sirve para demostrar que el diagnóstico ya no confunde documentación con código.

| Validación | Resultado |
|---|---|
| `python3 -m py_compile webkit-kit/tools/correlate_three_families.py` | PASS |
| Tests del repositorio | 31 PASS, 2 SKIPPED |
| `git diff --check` | PASS |
| Ejecución de WebKit/JSC | NOT RUN |
| Exploits/PoC/payloads | NOT RUN |
| Hardware | NOT USED |

## Estado de evidencia

| Elemento | Estado |
|---|---|
| Baseline Sony 601-1300 | `DIRECT` para sus fuentes públicas |
| MarkedVector/GC en PS4 13.52 | `UNVERIFIED` |
| Clone/objectPool en PS4 13.52 | `UNVERIFIED` |
| CSSFontFace layout en PS4 13.52 | `UNVERIFIED` |
| Primitive de memoria | `UNVERIFIED` |
| Ejecución WebContent | `UNVERIFIED` |
| Escape de sandbox/native usermode | `UNVERIFIED` |

La comprobación mecánica queda lista para cualquier fuente o módulo PS4 13.52 obtenido legítimamente con procedencia verificable. No se realizaron commits ni push.
