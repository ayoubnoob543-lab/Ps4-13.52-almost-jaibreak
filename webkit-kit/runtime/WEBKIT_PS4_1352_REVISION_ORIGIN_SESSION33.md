# Procedencia pública del WebKit/JSC de PS4 13.52

**Autor:** Manus AI  
**Ámbito:** investigación pública y análisis estático. No se utilizó hardware ni se ejecutaron exploits, payloads o binarios de consola.

## Conclusión ejecutiva

No se encontró un tag, commit, manifest, banner, símbolo, SHA de módulo o árbol fuente público que vincule inequívocamente PS4 13.52 con una revisión concreta de WebKit/JSC.

El último punto de correlación verificable es `WebKit-601-1300`, cuyo commit público es `d636699770323d7968a2c37955aa513bda5f8a37` y cuya propia descripción atribuye el árbol a PS4 13.00–13.04. El repositorio OSS comunitario también contiene una carpeta llamada `WebKit-616-1300`, pero su nombre no identifica PS4 13.52 y su contenido público es parcial: no contiene un directorio `Source` ni un árbol JSC completo, sólo `WebKit.xcworkspace`, `WebKitLibraries` y `resources`.

Por tanto, la transición pública verificable termina en:

```text
WebKit-601-1300
  → PS4 13.00–13.04
  → siguiente revisión Sony no identificada públicamente
  → PS4 13.50: sin SHA/revisión pública inequívoca
  → PS4 13.52: sin SHA/revisión pública inequívoca
```

## Inventario de candidatos

| Candidato | Evidencia pública | Qué contiene | Relación con 13.52 | Clasificación |
|---|---|---|---|---|
| `WebKit-601-1300` | Commit `d636699770323d7968a2c37955aa513bda5f8a37` en [PS4OSSCode][1] | Árbol fuente completo con `Source/JavaScriptCore`, `WebCore`, `WebKit2` y plataforma Orbis | La propia descripción limita el árbol a 13.00–13.04 | `HISTORICAL_ONLY` |
| `WebKit-616-1300` | Carpeta pública en [PS4OSSCode][1], introducida en el commit comunitario `c6c250c5b7e1a8ab711472acc27e9a7cbaabd785` | `WebKit.xcworkspace`, `WebKitLibraries` y `resources`; no hay `Source` completo | El sufijo `1300` no demuestra 13.52; no hay firmware ni banner posterior | `DOCUMENTED_ONLY` |
| `WebKit-616-1250` | Carpeta listada en [PS4OSSCode][1] | Árbol OSS nominal; no se encontró una etiqueta PS4 13.52 | No permite extrapolar 13.50/13.52 | `HISTORICAL_ONLY` |
| `wpewebkit-2.52.6` | Tag público WPE analizado localmente | Código portable, no Orbis retail | Sirve para comparar estructuras, no para fechar PS4 | `DOCUMENTED_ONLY` |
| Repositorio `zecoxao.github.io` | [Repositorio público de zecoxao][2] | Proyectos PS4/PS5/WebKit/JSC | No aparece revisión retail BD/WebKit 13.52 ni SHA de módulo | `DOCUMENTED_ONLY` |
| Forks `Feyzee61/ps4jb` y similares | [Feyzee61/ps4jb][3] | Código de exploits históricos hasta 9.60 | No contienen revisión WebKit de 13.50/13.52 | `HISTORICAL_ONLY` |

## Revisión `WebKit-601-1300`

La API pública de GitHub muestra dos commits relevantes del repositorio consolidado. `c6c250c5b7e1a8ab711472acc27e9a7cbaabd785`, fechado el 22 de abril de 2026, restaura y extrae código OSS; `d636699770323d7968a2c37955aa513bda5f8a37`, también del 22 de abril, añade explícitamente `WebKit-601-1300` con el mensaje “Add WebKit WebKit-601-1300 (PS4 13.00-13.04)”.

El árbol contiene `Source/JavaScriptCore`, `Source/WebCore`, `Source/WebKit2`, `Source/WTF`, `Source/bmalloc` y `Source/PlatformManx`/Orbis-related code. Esta es evidencia histórica directa del árbol público y de su rango declarado, pero no contiene una relación posterior con 13.50 o 13.52.

## Revisión `WebKit-616-1300`

La carpeta `WebKit-616-1300/WebKit-616-1300` existe en el repositorio, pero la inspección estructural muestra solamente:

| Ruta | Estado |
|---|---|
| `WebKit.xcworkspace` | Presente |
| `WebKitLibraries/DownlevelFrameworkStubs` | Presente |
| `WebKitLibraries/WebKitPrivateFrameworkStubs` | Presente |
| `WebKitLibraries/win` | Presente |
| `resources` | Presente |
| `Source/JavaScriptCore` | Ausente en el árbol inspeccionado |
| `Source/WebCore` | Ausente en el árbol inspeccionado |
| `Source/WebKit2` | Ausente en el árbol inspeccionado |
| Manifest o banner de firmware 13.50/13.52 | No encontrado |

El árbol `616-1300` no es suficiente para comparar `JSArray`, DFG, FTL, Butterfly o cualquier clase JSC. Su nombre es una etiqueta de colección, no evidencia de una correspondencia con PS4 13.52.

## Correlación con CVEs y correcciones JSC

| Candidato | Código/fix público | Estado frente al baseline | PS4 13.52 |
|---|---|---|---|
| CVE-2020-9802 | Project Zero documenta un bug JIT/CSE de JSC y su corrección en iOS 13.5 [4]. El análisis enlaza el parche público de `DFGClobberize` (`951d27d5...`) | Bug y corrección son reconstruibles upstream; el producto de corrección citado es Apple, no PS4 | `UNVERIFIED` |
| CVE-2022-42856 | Commit `98940f219ba0e3eb6d958af483b73dd9cc75c28c` cambia `~SpecFullDouble` por `~SpecDoubleReal` en `LowerDFGToB3::compileCompareStrictEq`; NVD fija correcciones Apple en Safari 16.2 y sistemas relacionados [5] | Código y causa raíz verificables; no hay mapeo PS4 | `UNVERIFIED` |
| CVE-2023-32439 | Commit `52fe95e5805c735cc1fa4d6200fcaa1912efbfea` separa `EnumeratorNextUpdateIndexAndModeLoc` de `HasIndexedPropertyLoc`; Apple vincula el caso al Bugzilla 256567 y Safari 16.5.1 [6] | Código y corrección verificables; no hay mapeo PS4 | `UNVERIFIED` |
| `Array.prototype.toReversed()` | `053d9a84ec27095cb583274daaf41ef796c80633` introdujo la ruta; `9158c52898ef7f10c47c884c12c67de5ee47d711` inicializó el excedente del butterfly. WPE 2.52.6 contiene `Butterfly::clearRange` | Mitigación verificable en WPE portable; no identifica la revisión Orbis | `UNVERIFIED` |

### `CVE-2020-9802`

Project Zero describe el defecto como una vulnerabilidad de compilación JIT/CSE en JavaScriptCore, probada contra Safari/iOS y corregida en iOS 13.5. La evidencia muestra una familia de bug compatible con un motor JSC sofisticado, pero no demuestra que el árbol PS4 13.52 derive del commit vulnerable, que conserve el defecto o que incluya el fix.

### `CVE-2022-42856`

El NVD describe una confusión de tipos corregida con mejor manejo de estado y fija las versiones de corrección Apple. El diff upstream proporciona función y expresión exactas, pero no existe una referencia pública que sitúe ese cambio en `WebKit-616-1300`, en OrbisOS o en PS4 13.52. No puede clasificarse como `DIRECT_13.52` ni `STRONG_INDIRECT_13.52`.

### `CVE-2023-32439`

El cambio de `HeapLocation` es una diferencia estructural verificable. El advisory de Apple confirma que el Bugzilla 256567 se corrigió en Safari 16.5.1, pero la fecha y el producto Apple no permiten inferir un backport Sony. Para atribuirlo a PS4 sería necesario un diff Sony, un árbol de la revisión retail o un símbolo/banner que lo conecte con la build.

### `toReversed()`

El baseline WPE 2.52.6 contiene `JSArray::fastToReversed` y `Butterfly::clearRange`. Esto permite comparar el comportamiento portable y verificar que el rango excedente se inicializa en ese baseline. No permite afirmar que PS4 13.52 use la misma implementación ni que Sony haya aplicado el mismo backport.

## Evaluación de backports Sony

No se encontró un commit Sony público posterior a `d6366997` que mencione simultáneamente PS4 13.50/13.52 y cualquiera de los commits JSC solicitados. Tampoco se encontró un branch público con nombres `WebKit-616-1350`, `WebKit-616-1352`, `WebKit-601-1350` o `WebKit-601-1352`.

La ausencia de un commit público no demuestra que Sony no haya hecho un backport privado. Sólo permite clasificar la hipótesis de backport como `UNVERIFIED`.

## Último punto verificable y bloqueo

El último punto de correlación verificable es `WebKit-601-1300` → PS4 13.00–13.04. `WebKit-616-1300` es un candidato nominal posterior dentro de una colección OSS comunitaria, pero no tiene una asociación pública con 13.50/13.52, no presenta un árbol JSC completo y no contiene metadata de firmware que permita fecharlo.

El artefacto mínimo que permitiría continuar es uno de los siguientes:

| Artefacto mínimo | Pregunta que resolvería |
|---|---|
| `libSceNKWebKit.sprx` o equivalente retail 13.52 con hash/procedencia | Identificar banners, símbolos o firmas de JSC/WebKit |
| Árbol fuente Sony posterior a `WebKit-601-1300` con commit/tag de firmware | Establecer la revisión exacta y comparar commits |
| Manifest/listado OSS de Sony que asocie `WebKit-616-1300` a una versión concreta | Confirmar o descartar la correspondencia 13.50/13.52 |
| Strings/version info/build ID de la librería retail | Correlacionar el binario con una revisión pública |
| Diff Sony de `JSArray.cpp`, `DFGClobberize.h` o `DFGHeapLocation.h` | Determinar backport independiente de los fixes |

## Conclusión

No se encontró una revisión pública inequívoca de WebKit/JSC para PS4 13.52. La afirmación correcta es:

> **El origen público de PS4 13.52 permanece `UNVERIFIED`; el último origen verificable es WebKit-601-1300 para PS4 13.00–13.04.**

Las vulnerabilidades y correcciones upstream analizadas son útiles como familias estructurales para comparación, pero ninguna puede declararse `DIRECT_13.52` ni como vulnerabilidad confirmada de PS4 13.52 por similitud de código.

## Referencias

[1]: https://github.com/FreeBSDKernel9-0/PS4OSSCode "PS4OSSCode — colección pública de OSS de PS4"

[2]: https://github.com/zecoxao/zecoxao.github.io "zecoxao/zecoxao.github.io"

[3]: https://github.com/Feyzee61/ps4jb "Feyzee61/ps4jb — fork histórico de PS4 WebKit/kernel"

[4]: https://projectzero.google/2020/09/jitsploitation-one.html "Project Zero — JITSploitation I: A JIT Bug"

[5]: https://nvd.nist.gov/vuln/detail/cve-2022-42856 "NVD — CVE-2022-42856"

[6]: https://support.apple.com/en-us/106353 "Apple — Security content of Safari 16.5.1 / Bugzilla 256567"

[7]: https://github.com/WebKit/WebKit/commit/98940f219ba0e3eb6d958af483b73dd9cc75c28c "WebKit commit 98940f2"

[8]: https://github.com/WebKit/WebKit/commit/52fe95e5805c735cc1fa4d6200fcaa1912efbfea "WebKit commit 52fe95e"

[9]: https://github.com/WebKit/WebKit/commit/053d9a84ec27095cb583274daaf41ef796c80633 "WebKit commit 053d9a84"

[10]: https://github.com/WebKit/WebKit/commit/9158c52898ef7f10c47c884c12c67de5ee47d711 "WebKit commit 9158c52"

[11]: https://www.playstation.com/en-us/oss/ps4/ "Sony — Open Source Software Used in PlayStation 4"

[12]: https://consolemods.org/wiki/PS4:Exploit_Chart "ConsoleMods — PS4 Exploit Chart"
