# Evidencia pública de WebKit/JSC PS4 13.52

## Resumen ejecutivo

La auditoría no recuperó bytes retail, snapshot Sony ni metadata nueva que permita reconstruir directamente `libSceNKWebKit` o el runtime JSC de PS4 13.52. Las fuentes públicas revisadas aportan afirmaciones de compatibilidad, demos o tablas secundarias, pero no un artefacto con procedencia, ruta, tamaño, hash y vínculo verificable a PS4 13.52.

El estado correcto continúa siendo:

```text
libSceNKWebKit.sprx retail 13.52: MISSING / UNVERIFIED
JSC/WebKit retail 13.52: MISSING / UNVERIFIED
CSSFontFace layout 13.52: UNVERIFIED
JSCell::toX 13.52: UNVERIFIED
MarkedVector / SerializedScriptValue / CloneSerializer 13.52: UNVERIFIED
WebKit-616-1300 = PS4 13.52: no demostrado
```

## Fuentes y resultados

| Fuente | Autor/fecha | Evidencia concreta | Clasificación |
|---|---|---|---|
| ConsoleMods Exploit Chart, https://consolemods.org/wiki/PS4:Exploit_Chart | Wiki secundaria; revisión visible de 2026 | Tabla de métodos por firmware, con WebKit hasta 11.00/11.02; no aporta módulo, hash, Build ID ni snapshot 13.52 | `DOCUMENTED_ONLY` |
| YouTube Shorts `O70FxdT12f4`, https://www.youtube.com/shorts/O70FxdT12f4 | Canal `@mbcrump`; título “PS4 13.52 CSSFontFace WebKit Userland Demo” | La página está actualmente “Video unavailable”; sólo quedan título, canal y enlace a vídeo largo `1THu446fKF4` | `UNVERIFIED` |
| Repositorio CSSFontFace de ntfargo, commit `221baa6e7349b96a6fd299808a25a4178e47741c` | Nathan Fargo/ufm42 | Documenta un alcance declarado hasta 13.52, pero la implementación publicada soporta PS4 6.00–11.02; afirma cambios de layout posteriores | `INDIRECT_13.52` para el alcance; código 13.52 `UNVERIFIED` |
| WebKit upstream actual, `CSSFontFace.h`, `CSSFontFaceSet.cpp`, `FontFaceSet.cpp` | WebKit project | Muestra el modelo moderno `RefCounted`, `m_propertiesOrCSSConnection`, `Vector<Ref<CSSFontFace>>` y retención en `FontFaceSet::load()` | `HISTORICAL_ONLY` / referencia estructural |
| WebKit-601-1300, commit Sony `d636699770323d7968a2c37955aa513bda5f8a37` | Sony OSS mirror | Baseline público PS4 13.00–13.04; contiene código WebCore/JSC, no artefactos 13.52 | `HISTORICAL_ONLY` |
| Búsqueda GitHub específica “PS4 13.52 WebKit/libSceNKWebKit/CSSFontFace” | Índice público | Sin resultados de artefactos identificables en la consulta acotada | ausencia de hallazgo; no prueba inexistencia universal |

## Artefactos no encontrados

No se encontró públicamente un archivo con bytes o metadata verificable para:

```text
libSceNKWebKit.sprx
libkernel_web.sprx
libSceLibcInternal.sprx
SELF/ELF WebKit 13.52
eboot.bin vinculado a WebKit 13.52
bdjstack.jar / rt.jar 13.52
snapshot system_ex 13.52
manifest retail con hash de WebKit 13.52
Build ID o tabla de símbolos de WebKit 13.52
```

Tampoco se encontró una fuente pública que vincule de forma técnica `WebKit-616-1300` con PS4 13.52. El nombre de la rama o la proximidad temporal no son suficientes para esa atribución.

## Qué permite comparar actualmente

El material Sony `WebKit-601-1300` permite comparar nombres de archivos, clases, funciones y estructuras públicas de WebCore/JSC con commits upstream posteriores. Esto permite preparar patrones para `CSSFontFace`, `FontFaceSet`, `JSCell::toX`, DFG/FTL y otras familias.

No permite establecer que PS4 13.52 conserve esas estructuras, que Sony haya aplicado un backport concreto o que una CVE upstream esté presente o corregida en el retail 13.52.

## Cadena de evidencia

```text
fuente pública
→ firmware explícitamente atribuido
→ archivo/ruta
→ bytes o metadata
→ hash/tamaño/identificador
→ parser estático
→ símbolo/clase/estructura
→ correlación con 13.52
```

La cadena se rompe actualmente después de “firmware explícitamente atribuido”: las demos y tablas no entregan bytes ni metadata retail; el código 601-1300 tiene procedencia Sony, pero no es 13.52.

## Siguiente evidencia mínima

El artefacto decisivo sería cualquiera de los siguientes, siempre con procedencia PS4 13.52 verificable:

```text
libSceNKWebKit.sprx o SELF/ELF equivalente
snapshot de filesystem que contenga WebKit
manifest con hash/tamaño/Build ID del módulo
extracción documentada de `app0` con `bdjstack.jar` y `rt.jar`
```

Para una comparación útil de CSSFontFace/JSC, el archivo debe conservar bytes, ruta, firmware, tamaño y SHA-256. Un vídeo, título, offset aislado o rama WebKit sin vínculo documental al firmware no basta.

## Conclusión

No apareció evidencia nueva que permita reconstruir el runtime real de PS4 13.52. La mejor clasificación global es `UNVERIFIED`, con `INDIRECT_13.52` únicamente para afirmaciones públicas de alcance o compatibilidad. No se debe promover ninguna de ellas a `DIRECT_13.52` ni usarla para confirmar una vulnerabilidad, un UAF vivo, una primitive de memoria o native usermode.

## Referencias

[1]: https://consolemods.org/wiki/PS4:Exploit_Chart "ConsoleMods PS4 Exploit Chart"
[2]: https://www.youtube.com/shorts/O70FxdT12f4 "PS4 13.52 CSSFontFace WebKit Userland Demo"
[3]: https://github.com/ntfargo/CSSFontFace-Exploit/tree/221baa6e7349b96a6fd299808a25a4178e47741c "CSSFontFace-Exploit commit"
[4]: https://github.com/WebKit/WebKit/blob/main/Source/WebCore/css/CSSFontFace.h "WebKit CSSFontFace.h"
[5]: https://github.com/WebKit/WebKit/blob/main/Source/WebCore/css/CSSFontFaceSet.cpp "WebKit CSSFontFaceSet.cpp"
[6]: https://github.com/WebKit/WebKit/blob/main/Source/WebCore/css/FontFaceSet.cpp "WebKit FontFaceSet.cpp"
[7]: https://github.com/FreeBSDKernel9-0/PS4OSSCode/tree/d636699770323d7968a2c37955aa513bda5f8a37 "PS4OSSCode WebKit-601-1300"
