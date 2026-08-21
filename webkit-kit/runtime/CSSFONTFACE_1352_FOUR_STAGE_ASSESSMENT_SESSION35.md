# CSSFontFace en PS4 13.52: evaluación de los cuatro escalones

## Conclusión ejecutiva

La evidencia pública actual permite identificar un **UAF histórico y una cadena de explotación publicada para PS4 hasta 11.02**, pero no permite afirmar que CSSFontFace sea reproducible como primitive de memoria en PS4 13.52.

El README público de `ntfargo/CSSFontFace-Exploit`, commit `221baa6e7349b96a6fd299808a25a4178e47741c`, separa expresamente:

| Categoría | PS4 |
|---|---|
| Alcance declarado del problema | 6.00–13.52 |
| Versiones declaradas explotables por el repositorio | 6.00–11.02 |

El mismo README dice que en PS4 11.5x y posteriores se rediseñó el manejo de propiedades get/set de CSSFontFace y apareció `m_propertiesOrCSSConnection`; por esos cambios de layout, la primitive basada en `m_featureSettings` ya no es utilizable en las versiones superiores al rango explotable publicado.

Por tanto, el estado correcto de la cadena para 13.52 es:

```text
implementación exacta 13.52: MISSING
bug UAF vivo: UNVERIFIED
primitive controlable: UNVERIFIED
escape/nativemode: UNVERIFIED
```

## 1. Implementación 13.52

No existe en el corpus un módulo retail PS4 13.52 ni símbolos/vtables/layouts verificables de `CSSFontFace`, `CSSFontFaceSet` o `FontFaceSet`. El árbol público Sony `WebKit-601-1300` contiene las fuentes de referencia:

```text
Source/WebCore/css/CSSFontFace.cpp
Source/WebCore/css/CSSFontFace.h
Source/WebCore/css/CSSFontFaceSet.cpp
Source/WebCore/css/CSSFontFaceSet.h
Source/WebCore/css/FontFaceSet.cpp
Source/WebCore/css/FontFaceSet.h
Source/WebCore/css/FontFace.cpp
Source/WebCore/css/FontFace.h
```

Ese árbol representa la referencia pública PS4 13.00–13.04, no 13.52. La existencia de los archivos es útil para localizar nombres y relaciones, pero no permite derivar offsets o layouts de 13.52.

La primera evidencia específica que falta es una de estas opciones:

1. bytes retail de WebKit 13.52 con procedencia verificable;
2. snapshot de fuentes Sony que identifique una revisión posterior;
3. símbolos, vtables, tamaños y campos de `CSSFontFace`/`CSSFontFaceSet` de una build 13.52.

## 2. ¿Sobrevive el UAF?

El write-up público de Nathan Fargo y ufm42 describe el defecto de lifetime así:

```text
CSSFontFaceSet::matchingFacesExcludingPreinstalledFonts()
→ Vector<std::reference_wrapper<CSSFontFace>>
→ FontFaceSet::load()
→ uso repetido de face.get()
→ reentrada durante resolución de promesa
→ mutación de stylesheet/remoción de CSSFontFace
→ referencia no propietaria obsoleta
```

El mismo write-up describe como corrección conceptual el cambio a:

```text
Vector<Ref<CSSFontFace>>
```

para conservar una referencia fuerte mientras finaliza `FontFaceSet::load()`.

Esta es evidencia pública del mecanismo histórico. No demuestra que la variante concreta exista en 13.52. El README del exploit aporta una falsación importante: aunque el problema pueda tener alcance hasta 13.52, el layout posterior a 11.5x rompe la primitive publicada. Eso impide transferir el resultado de 11.02 a 13.52.

La comprobación estática futura debe buscar conjuntamente:

| Señal | Interpretación |
|---|---|
| `Vector<std::reference_wrapper<CSSFontFace>>` en el producer | patrón histórico no propietario |
| `Vector<Ref<CSSFontFace>>` en el producer | retención fuerte compatible con el fix descrito |
| `matchingFacesExcludingPreinstalledFonts` y `FontFaceSet::load` con las mismas firmas | correlación estructural parcial |
| `m_propertiesOrCSSConnection` y layout de campos | posible familia de layout posterior; no demuestra seguridad ni vulnerabilidad |
| `FontFace::fontStateChanged`/resolución de promise | punto de reentrada potencial |

La presencia de un único nombre no basta: se deben comparar tipos de retorno, ownership y todas las lecturas posteriores a puntos de reentrada.

## 3. ¿Existe una primitive de memoria?

En la publicación pública, el UAF es sólo el disparador inicial. La cadena publicada necesita además reclamación controlada, estado de objeto estable y una lectura/escritura posterior. Para PS4 13.52, el repositorio público no aporta una implementación funcional: su tabla declara como explotable sólo 6.00–11.02 y su propia limitación dice que la primitive `m_featureSettings` deja de ser utilizable desde 11.5x.

En consecuencia:

```text
UAF histórico: DOCUMENTED_ONLY
read/write en 11.02: HISTORICAL_ONLY según la publicación
read/write en 13.52: UNVERIFIED
```

No se debe llamar “primitive controlable” a la mera posibilidad de provocar una liberación o un crash. La condición mínima para elevar el estado en 13.52 sería una evidencia estática de layout y ownership, seguida de una prueba segura de invariantes —por ejemplo, que el objeto leído después de la reentrada ya no conserva el tipo/estado esperado— sin crear una cadena de explotación.

## 4. ¿Existe escape fuera del sandbox?

No. El repositorio público incluye una cadena histórica posterior hacia native usermode y kernel para versiones antiguas, pero eso no demuestra un escape en 13.52. El propio README sólo declara soporte del repositorio para PS4 6.00–11.02 y los parches históricos están ligados a firmwares antiguos.

La relación correcta es:

```text
CSSFontFace UAF
→ posible primitive de memoria (sólo demostrado históricamente en rango antiguo)
→ native usermode (histórico/publicado para ese rango)
→ kernel/Linux (dependencias adicionales, no parte de esta auditoría)
```

Para 13.52 faltan, como mínimo, una primitive de memoria reproducible en el layout posterior y una prueba independiente de que las mitigaciones, ASLR, vtables y límites de proceso permiten el siguiente salto. No se puede inferir native usermode sólo desde el UAF.

## Diagnóstico estático disponible

El repositorio ya contiene `tools/analyze_cssfontface_constants.py`, que trata las tablas de constantes como texto y marca `m_propertiesOrCSSConnection`, tamaños, campos y vtables como dependientes del firmware. Su regla explícita mantiene 13.52 como `ABSENT` sin bytes de la misma build.

Para una futura extracción autorizada, el diagnóstico debe registrar:

```text
SHA-256 y tamaño del artefacto
tipo ELF/SELF y arquitectura
segmentos y rango de .text
símbolos/vtables disponibles
nombres de CSSFontFace/CSSFontFaceSet/FontFaceSet
firmas de producer/consumer
campos m_featureSettings y m_propertiesOrCSSConnection
puntos de reentrada y referencias de ownership
```

El resultado debe permanecer en `DIRECT_13.52`, `STRONG_INDIRECT_13.52` o `UNVERIFIED`; ninguna señal textual debe promoverlo a una confirmación de exploit.

## Clasificación final

| Escalón | Estado | Clasificación |
|---|---|---|
| Implementación exacta de `CSSFontFace` en 13.52 | No disponible | `UNVERIFIED` |
| UAF de referencias no propietarias | Descrito públicamente | `HISTORICAL_ONLY` / `DOCUMENTED_ONLY` |
| Cambio de layout desde 11.5x (`m_propertiesOrCSSConnection`) | Declarado por el README público | `INDIRECT_13.52` |
| Primitive `m_featureSettings` en 13.52 | El propio repositorio la declara no utilizable sobre 11.02 | `UNVERIFIED` |
| Primitive alternativa controlable en 13.52 | No publicada ni demostrada | `UNVERIFIED` |
| Native usermode en 13.52 | No demostrado | `UNVERIFIED` |
| Escape de sandbox/kernel/Linux | Fuera de la evidencia disponible | `UNVERIFIED` |

## Referencias

[1]: https://github.com/ntfargo/CSSFontFace-Exploit/tree/221baa6e7349b96a6fd299808a25a4178e47741c "CSSFontFace-Exploit, audited public commit"
[2]: https://linearfox.com/blog/cssfontface-uaf-playstation "From CSSFontFace to ARW: A PlayStation Webkit Exploit Writeup"
[3]: https://github.com/FreeBSDKernel9-0/PS4OSSCode/tree/d636699770323d7968a2c37955aa513bda5f8a37/WebKit-601-1300 "Public Sony WebKit-601-1300 source tree"
[4]: https://bugs.webkit.org/show_bug.cgi?id=164902 "WebKit Bug 164902: FontFaceSet.load promises"
[5]: https://www.w3.org/TR/css-font-loading/ "CSS Font Loading Module Level 3"
