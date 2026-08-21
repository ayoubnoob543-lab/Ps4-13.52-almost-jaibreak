# Reevaluación de CSSFontFace después de 11.02

## Dictamen

La evidencia pública actual respalda esta conclusión: **la vulnerabilidad de lifetime de CSSFontFace no puede declararse eliminada universalmente, pero la primitive de memoria publicada para PS4 6.00–11.02 queda invalidada por cambios posteriores de layout y acceso a propiedades. No existe evidencia pública suficiente de una primitive alternativa en PS4 13.52.**

## Evidencia primaria disponible

El repositorio público `ntfargo/CSSFontFace-Exploit` fue auditado en el commit `221baa6e7349b96a6fd299808a25a4178e47741c`. Su README separa explícitamente el alcance del problema (`PS4 6.00–13.52`) del rango explotable por la implementación publicada (`PS4 6.00–11.02`). También afirma que las versiones 11.5x y posteriores rediseñaron el manejo get/set de CSSFontFace e introdujeron `m_propertiesOrCSSConnection`, haciendo inutilizable la primitive basada en `m_featureSettings`.

El write-up público de Nathan Fargo y ufm42 atribuye el UAF a una secuencia de referencias no propietarias: `CSSFontFaceSet::matchingFacesExcludingPreinstalledFonts()` devuelve referencias a objetos `CSSFontFace`, `FontFaceSet::load()` las conserva mientras existen puntos de reentrada y la mutación de una stylesheet puede retirar el objeto. La corrección conceptual descrita usa referencias fuertes `Ref<CSSFontFace>`.

Estas fuentes son evidencia pública del mecanismo y de sus límites declarados, no un dump de PS4 13.52.

## Diferencia de representación

La referencia WebKit moderna pública muestra una forma de objeto muy distinta de la implementación antigua esperada por la cadena de 11.02. `CSSFontFace` es ref-counted y contiene, en este orden conceptual, una variante fuerte de propiedades/conexión, familia, rangos, `m_featureSettings`, fuentes, clientes débiles, wrapper débil, estado y temporizador. Los getters/setters consultan `properties()` o `mutableProperties()` mediante la alternativa activa de la variante.

`CSSFontFaceSet` moderno utiliza `Vector<Ref<CSSFontFace>>` en sus colecciones, y `FontFaceSet::load()` itera con `Ref`. Esto produce dos cambios verificables a nivel de modelo:

| Aspecto | Modelo antiguo de la cadena publicada | Modelo moderno observable |
|---|---|---|
| Retención en lista de coincidencias | `reference_wrapper<CSSFontFace>` | `Ref<CSSFontFace>` |
| Propiedades | Campo/layout esperado directamente | `Variant<Ref<MutableStyleProperties>, Ref<StyleRuleFontFace>>` + accessors |
| Lista de caras | referencias no propietarias en la ruta relevante | colecciones con referencias fuertes |
| Efecto de mutar stylesheet | puede dejar referencia obsoleta en consumidor | la retención fuerte reduce esa condición |
| Lectura/escritura de `m_featureSettings` | dependiente de offsets antiguos | desplazada y semánticamente separada por accessors |

La presencia moderna de estos patrones no prueba que PS4 13.52 utilice exactamente el mismo código, pero explica por qué los offsets y la primitive antigua no pueden trasladarse.

## Análisis de los tres escenarios

### 1. UAF completamente inutilizado

Sería el resultado si el producer y el consumer de la lista de coincidencias ya conservaran referencias fuertes o si una protección equivalente cubriera toda la operación de `FontFaceSet::load()`. No puede confirmarse para 13.52 porque falta su implementación.

### 2. UAF residual, primitive antigua rota

Es el escenario mejor respaldado indirectamente. El bug de lifetime podría conservar alguna reentrada, pero `m_propertiesOrCSSConnection` cambia la forma del objeto y los accessors ya no permiten interpretar `m_featureSettings` como lo hacía la cadena 6.00–11.02. El README del proyecto declara explícitamente esa ruptura para el rango posterior a 11.02.

### 3. Ruta de memoria alternativa

Para sostener este escenario habría que demostrar, en la misma build, una referencia no propietaria o estado obsoleto, un campo/relación que sobreviva al rediseño y una operación segura que permita observar una inconsistencia de memoria. No hay fuente Sony, layout ni testcase público específico de 13.52 que lo demuestre. Permanece como `HYPOTHESIS`.

## Sobre el rango 11.50 frente a 11.02

Un mirror secundario del write-up menciona PS4 11.50, mientras que el README y la tabla de soporte del repositorio declaran 11.02. Al no existir un commit de implementación separado, offsets ni artifacto de 11.50 que resuelva la contradicción, el límite 11.50 se clasifica `DOCUMENTED_ONLY/UNVERIFIED` y no se usa como evidencia para 13.52.

## Relación con native usermode

El UAF y la diferencia de layout no son equivalentes a una primitive de ejecución nativa. La publicación histórica describe etapas posteriores de memoria y control de ejecución para versiones antiguas, pero no aporta una ruta operativa válida para 13.52. El estado actual es:

```text
UAF en la familia CSSFontFace: DOCUMENTED_ONLY
primitive m_featureSettings en 13.52: descartada indirectamente
primitive alternativa en 13.52: UNVERIFIED
native usermode en 13.52: UNVERIFIED
```

## Siguiente evidencia decisiva

La cuestión se resolvería con una fuente o metadata de una build Sony posterior a 11.02, preferiblemente 13.52, que permita comparar:

```text
CSSFontFace layout y sizeof
m_propertiesOrCSSConnection
m_featureSettings
matchingFacesExcludingPreinstalledFonts return type
FontFaceSet::load local collection type
FontFace::fontStateChanged re-entry behavior
CSSFontFaceSet::remove lifetime protection
```

Una captura textual de un offset aislado no sería suficiente; se necesita la relación producer/consumer y la procedencia de la build.

## Clasificación final

| Pregunta | Clasificación |
|---|---|
| ¿Cambió CSSFontFace después de 11.02? | `INDIRECT_13.52` por documentación pública; contenido exacto 13.52 `UNVERIFIED` |
| ¿La primitive antigua sigue siendo transferible? | `DISCARDED` como transferencia directa; `STRONG_INDIRECT_13.52` para su ruptura |
| ¿El UAF desapareció por completo? | `UNVERIFIED` |
| ¿Existe una primitive residual? | `HYPOTHESIS` |
| ¿Existe una ruta a native usermode? | `UNVERIFIED` |

## Referencias

[1]: https://github.com/ntfargo/CSSFontFace-Exploit/tree/221baa6e7349b96a6fd299808a25a4178e47741c "CSSFontFace-Exploit, commit público auditado"
[2]: https://linearfox.com/blog/cssfontface-uaf-playstation "From CSSFontFace to ARW: A PlayStation Webkit Exploit Writeup"
[3]: https://github.com/WebKit/WebKit/blob/main/Source/WebCore/css/CSSFontFace.h "WebKit upstream CSSFontFace.h"
[4]: https://github.com/WebKit/WebKit/blob/main/Source/WebCore/css/CSSFontFaceSet.cpp "WebKit upstream CSSFontFaceSet.cpp"
[5]: https://github.com/WebKit/WebKit/blob/main/Source/WebCore/css/FontFaceSet.cpp "WebKit upstream FontFaceSet.cpp"
[6]: https://www.psx-place.com/threads/write-up-ps5-ps4-from-cssfontface-to-arw-a-playstation-webkit-exploit-writeup.50478/ "Secondary mirror with inconsistent upper-range wording"
