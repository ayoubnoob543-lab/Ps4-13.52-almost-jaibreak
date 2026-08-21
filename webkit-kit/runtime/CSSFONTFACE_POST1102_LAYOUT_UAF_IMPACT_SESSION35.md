# CSSFontFace después de 11.02: layout y efecto sobre el UAF

## Conclusión

La evidencia pública disponible no demuestra que el UAF de CSSFontFace haya desaparecido en todas las versiones posteriores a 11.02. Sí demuestra algo más acotado y decisivo: la **primitive publicada para PS4 6.00–11.02 deja de ser utilizable cuando cambia el layout y el acceso a propiedades de CSSFontFace**, según el propio repositorio público del exploit.

La clasificación correcta para PS4 13.52 es:

```text
UAF histórico: DOCUMENTED_ONLY
layout posterior a 11.02: INDIRECT_13.52
primitive antigua m_featureSettings: descartada para 13.52 por la documentación pública
UAF residual o primitive alternativa: UNVERIFIED
native usermode: UNVERIFIED
```

## Evidencia pública y procedencia

El repositorio [`ntfargo/CSSFontFace-Exploit`][1], auditado en el commit `221baa6e7349b96a6fd299808a25a4178e47741c`, separa el alcance declarado de la versión realmente soportada por su implementación. Su README dice que el problema tiene alcance PS4 6.00–13.52, pero que el repositorio es explotable en PS4 sólo 6.00–11.02. También afirma que las versiones PS4 11.5x y posteriores rediseñaron el manejo get/set de CSSFontFace e introdujeron `m_propertiesOrCSSConnection`; por esos cambios y otros cambios de layout, la primitive basada en `m_featureSettings` ya no es utilizable sobre el rango publicado.

El write-up de Nathan Fargo y ufm42 [2] describe el defecto de lifetime en la ruta de fuentes. La versión histórica usa referencias no propietarias devueltas por `CSSFontFaceSet::matchingFacesExcludingPreinstalledFonts()` y consumidas más tarde por `FontFaceSet::load()`. La reentrada JavaScript ocurre durante la resolución de una promesa de carga; la mutación de stylesheet puede retirar la cara CSS mientras el consumidor aún conserva una referencia no propietaria.

El mismo write-up describe una corrección de ownership basada en referencias fuertes `Ref<CSSFontFace>`. No se ha demostrado que esa corrección concreta sea la razón exacta del comportamiento de PS4 13.52, porque no existen los bytes ni la fuente Sony de esa build.

## Qué cambia en el layout moderno

El código WebKit upstream público actual muestra la forma moderna de `CSSFontFace` como un objeto ref-counted con ownership explícito y una variante de propiedades:

```cpp
class CSSFontFace final : public RefCountedAndCanMakeWeakPtr<CSSFontFace>;

const Variant<Ref<MutableStyleProperties>, Ref<StyleRuleFontFace>>
    m_propertiesOrCSSConnection;

FontFeatureSettings m_featureSettings;
WeakHashSet<CSSFontFaceClient> m_clients;
WeakPtr<FontFace> m_wrapper;
Timer m_timeoutTimer;
```

Los getters y setters ya no dependen simplemente de leer o escribir un campo plano. Se encaminan mediante `properties()` y `mutableProperties()`, que seleccionan la alternativa activa de `m_propertiesOrCSSConnection`. En el `CSSFontFaceSet` moderno, las tablas y listas usan `Vector<Ref<CSSFontFace>>`; en `FontFaceSet::load()` cada cara se recorre como `Ref` mientras se carga, se comprueba su estado y se obtiene el wrapper.

Este diseño tiene dos efectos relevantes para la investigación:

1. **Desplaza los offsets y cambia la interpretación del objeto.** El campo `m_featureSettings` ya no ocupa la posición que la cadena antigua esperaba y el primer campo de propiedades puede ser una `Variant` con referencias fuertes.
2. **Cambia el modelo de lifetime.** Las colecciones y el consumidor pueden mantener referencias fuertes durante la operación, reduciendo la posibilidad de que una eliminación de stylesheet convierta una referencia almacenada en dangling reference.

Estas observaciones son de WebKit upstream moderno y sirven como patrón estructural. No deben presentarse como una reconstrucción binaria de PS4 13.52.

## Efecto sobre el UAF

Hay tres escenarios posibles y la evidencia actual sólo permite discriminar parcialmente:

| Escenario | Qué tendría que observarse | Estado 13.52 |
|---|---|---|
| UAF completamente inutilizado | producer y consumer usan ownership fuerte; no queda referencia no propietaria tras la reentrada | `UNVERIFIED` |
| UAF conservado, primitive antigua rota | el lifetime defectuoso sigue, pero el layout/getters ya no permiten usar `m_featureSettings` como antes | `STRONG_INDIRECT_13.52` para la ruptura de la primitive; UAF `UNVERIFIED` |
| UAF conservado con ruta residual | sigue existiendo una referencia obsoleta y otro campo/flujo produce un estado de memoria controlable | `HYPOTHESIS` |

El README y el write-up apoyan con fuerza el segundo escenario para la implementación publicada: el fallo puede tener un alcance amplio, pero la primitive `m_featureSettings` sólo fue implementada y declarada operativa hasta 11.02. La frase del mirror PSX-Place que extiende el rango explotable a 11.50 contradice el README y no aporta offsets ni una implementación separada; se conserva como documentación secundaria no verificada.

## Qué comprobar cuando exista una fuente posterior

La comparación debe ser estática y limitada a invariantes, no a construcción de una cadena de explotación. Para cada versión deben registrarse:

| Área | Invariante que debe compararse |
|---|---|
| Producer | tipo exacto de retorno de `matchingFacesExcludingPreinstalledFonts()` |
| Consumer | tipo de la colección local en `FontFaceSet::load()` |
| Ownership | `reference_wrapper`/puntero frente a `Ref`/`RefPtr` |
| Reentrada | operaciones posteriores a `fontStateChanged()` y resolución de promise |
| Eliminación | protección local de `remove()` y referencias externas que sobreviven |
| Layout | orden y tamaño relativo de `m_propertiesOrCSSConnection`, `m_family`, `m_ranges`, `m_featureSettings` |
| Accessors | si getters/setters usan propiedades cacheadas o campos directos |
| Wrapper/clientes | weak/strong references y notificación durante la mutación |

Un resultado `VULNERABLE_LIKE` sólo sería justificable si el mismo artifacto posterior muestra la combinación de referencia no propietaria, reentrada y uso posterior. Un resultado `FIXED_LIKE` requeriría ownership fuerte o una protección equivalente. Un layout distinto por sí solo debe quedar como `PARTIAL/UNVERIFIED`.

## Native usermode

El cambio de layout no demuestra ni descarta por sí mismo native usermode. La cadena histórica necesita al menos una primitive de memoria controlable antes de cualquier salto de ejecución; la documentación pública de 13.52 no proporciona esa primitive. Por ello, la conclusión actual es:

> CSSFontFace sigue siendo una línea independiente y técnicamente interesante, pero la evidencia pública más sólida indica que la primitive publicada para 6.00–11.02 no se transfiere a 13.52. No se ha identificado una primitive alternativa ni una ruta a native usermode para 13.52.

## Dictamen

El mejor dictamen actual es **“UAF histórico con primitive antigua rota por cambios posteriores de layout; variante residual no demostrada”**. No procede descartar todo CSSFontFace como UAF sin los bytes posteriores, pero tampoco procede afirmar que PS4 13.52 sea explotable. El mínimo dato que resolvería la cuestión es una fuente, snapshot o metadata de layout de `CSSFontFace`/`CSSFontFaceSet`/`FontFaceSet` de una build Sony posterior a 11.02, idealmente 13.52.

## Referencias

[1]: https://github.com/ntfargo/CSSFontFace-Exploit/tree/221baa6e7349b96a6fd299808a25a4178e47741c "CSSFontFace-Exploit, commit auditado"
[2]: https://linearfox.com/blog/cssfontface-uaf-playstation "From CSSFontFace to ARW: A PlayStation WebKit Exploit Writeup"
[3]: https://github.com/WebKit/WebKit/blob/main/Source/WebCore/css/CSSFontFace.h "WebKit current CSSFontFace.h"
[4]: https://github.com/WebKit/WebKit/blob/main/Source/WebCore/css/CSSFontFaceSet.cpp "WebKit current CSSFontFaceSet.cpp"
[5]: https://github.com/WebKit/WebKit/blob/main/Source/WebCore/css/FontFaceSet.cpp "WebKit current FontFaceSet.cpp"
[6]: https://www.psx-place.com/threads/write-up-ps5-ps4-from-cssfontface-to-arw-a-playstation-webkit-exploit-writeup.50478/ "Secondary mirror of the write-up"
