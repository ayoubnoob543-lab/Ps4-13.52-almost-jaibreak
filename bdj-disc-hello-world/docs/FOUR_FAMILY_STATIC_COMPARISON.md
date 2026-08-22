# Comparación estática: BD-J Hello World frente a familias históricas WebKit/JSC

## Alcance

Se comparó el código fuente del proyecto BD-J benigno con las tres familias configuradas en el correlador local: `JSCell::toX`, `MarkedVector/GC` y `CloneSerializer/CloneDeserializer/objectPool`. `CSSFontFace` se revisó como cuarta familia por inventario de componentes y no forma parte de la configuración actual del correlador.

El objetivo es determinar si el disco BD-J contiene esas superficies. No se intentó ejecutar código, cargar el Xlet en hardware, adaptar una vulnerabilidad ni inferir estado de PS4 13.52 a partir de un `NO MATCH`.

## Entrada analizada

- Entrada: `src/`
- Archivos fuente: 1
- Fuente: `src/org/homebrew/MyXlet.java`
- SHA-256 del contenido analizado: `3d8086a6faa09ff235f43d52e3e1984fa1f1ee68a0e8830f3624626d5de5c1fc`
- Target configurado por la herramienta: `13.52`
- Proveniencia retail: `UNVERIFIED`

## Resultados exactos del correlador

| Familia | Resultado | Estado de vulnerabilidad | Evidencia encontrada |
|---|---|---|---|
| `JSCell::toX` / Bugzilla 270797 | `NO MATCH` | `UNVERIFIED` | Ninguna función, cadena o marcador de la familia |
| `MarkedVector` / GC / Bugzilla 254797 | `NO MATCH` | `UNVERIFIED` | Ninguna función, cadena o marcador de la familia |
| `CloneSerializer` / `CloneDeserializer` / `objectPool` / Bugzilla 265975 | `NO MATCH` | `UNVERIFIED` | Ninguna función, cadena o marcador de la familia |
| `CSSFontFace` / `CSSFontFaceSet` / `FontFaceSet::load` | No configurada en el correlador | `UNVERIFIED` | No aparecen referencias en el único fuente del Xlet |

## Interpretación técnica

El Xlet usa únicamente las APIs necesarias para el ciclo de vida BD-J y para pintar una interfaz: `javax.tv.xlet.Xlet`, `javax.tv.xlet.XletContext`, `org.havi.ui.HScene`, `org.havi.ui.HSceneFactory` y clases gráficas AWT. No contiene JavaScriptCore, WebCore, WebKit, `JSCell`, `MarkedVector`, `SerializedScriptValue`, `CloneSerializer`, `CloneDeserializer`, `CSSFontFace` ni `FontFaceSet`.

La ausencia de estas referencias es esperable: el disco BD-J no incorpora el navegador ni el código fuente de WebKit/JSC. Un Xlet que muestre Hello World no ejecuta automáticamente una ruta del navegador y no convierte una vulnerabilidad de WebKit en una vulnerabilidad BD-J.

## Qué sí se puede concluir

La comparación demuestra que las cuatro familias no están presentes en el código fuente del Xlet ni en su alcance de authoring. El resultado no dice si alguna familia existe o no en `libSceNKWebKit` de PS4 13.52, porque ese binario no forma parte de este proyecto y no se ha analizado aquí.

Por tanto, la clasificación correcta es:

| Pregunta | Clasificación |
|---|---|
| ¿El Xlet contiene una familia histórica WebKit/JSC? | `NO MATCH` |
| ¿La ISO prueba una vulnerabilidad WebKit/JSC? | `NOT DEMONSTRATED` |
| ¿La ISO prueba una vulnerabilidad BD-J? | `NOT DEMONSTRATED` |
| ¿El Hello World demuestra ejecución nativa? | `NO` |
| ¿El Hello World demuestra escape del sandbox? | `NO` |
| ¿El estado de esas familias en PS4 13.52 está resuelto? | `UNVERIFIED` |

## Bloqueo restante

Para correlacionar una familia WebKit/JSC con PS4 13.52 haría falta un artefacto autorizado del navegador —por ejemplo, una extracción verificable de `libSceNKWebKit`— o evidencia pública equivalente con procedencia y versión. El disco BD-J actual no puede sustituir ese artefacto.

Para el proyecto BD-J, el siguiente paso independiente es probar la ISO en la unidad autorizada y registrar si carga. Ese resultado sólo confirmaría ejecución BD-J normal; no resolvería el estado de WebKit/JSC ni constituiría por sí solo un reporte de vulnerabilidad.

## Referencia metodológica

El correlador local está diseñado para correlación estructural de fuentes y declara explícitamente que no ejecuta, importa, descifra ni asigna procedencia retail. Sus resultados son señales de presencia textual/estructural, no confirmaciones de vulnerabilidad [1].

## Referencias

[1]: ../../webkit-kit/tools/correlate_three_families.py "Correlador estático local de las familias WebKit/JSC"
[2]: ../README.md "README del proyecto BD-J Hello World"
[3]: validation.json "Validación estática del proyecto"
