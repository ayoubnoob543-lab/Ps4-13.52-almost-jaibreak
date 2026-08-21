# Diagnóstico estático de CVE-2020-9802 en WebKit-601-1300

## Alcance

Se eligió CVE-2020-9802 porque su condición está descrita con precisión y tiene un commit upstream verificable. El análisis se limita a lectura de fuentes públicas y a un comprobador estático que inspecciona texto fuente. No se compiló ni ejecutó JavaScriptCore, no se ejecutó el testcase de explotación y no se generaron payloads.

## Condición upstream

Project Zero describe un error en JavaScriptCore DFG/CSE: `DFGClobberize` trataba ciertas operaciones aritméticas como `PureValue` sin incluir el `ArithMode`. En particular, `ArithNegate` y `ArithAbs` podían quedar representadas sin distinguir el modo checked/unchecked. Esto permitía que una optimización CSE reutilizara una operación bajo una premisa incorrecta. El caso límite documentado es la negación de `INT_MIN`, cuyo resultado no es representable como `Int32`.

El parche upstream identificado es:

```text
951d27d5ba08b6c29370b05dc6b4ffe18be1ca18
```

La forma esencial del cambio es:

```diff
- def(PureValue(node));
+ def(PureValue(node, node->arithMode()));
```

El artículo de Project Zero documenta CVE-2020-9802 como corregido en iOS 13.5 y menciona CVE-2020-9870/CVE-2020-9910 como bypasses de mitigaciones corregidos en iOS 13.6. Eso es evidencia de Apple/iOS y no de PS4.

## Comprobación sobre WebKit-601-1300

Se descargaron pasivamente desde el mirror público Sony los siguientes archivos:

```text
Source/JavaScriptCore/dfg/DFGClobberize.h
Source/JavaScriptCore/dfg/DFGSpeculativeJIT.cpp
Source/JavaScriptCore/runtime/JSArray.cpp
Source/JavaScriptCore/runtime/JSArray.h
```

La fuente `DFGClobberize.h` de 601-1300 contiene explícitamente:

```cpp
case ArithNegate:
    ...
    def(PureValue(node, node->arithMode()));
```

También agrupa `ArithNegate` con operaciones que usan `node->arithMode()`, y la fuente conserva referencias de `ArithAbs` y `ArithNegate` en el clobberizer. El comprobador estático devolvió `FIXED_LIKE` para CVE-2020-9802 sobre este archivo.

Este resultado es una evidencia fuerte de que **la copia pública Sony 601-1300 consultada contiene la forma del fix de `ArithMode`**, aunque el resultado no prueba que el snapshot sea idéntico al binario de ningún firmware ni que todas las ramas de compilación lo utilicen.

El mismo análisis no observó `fastToReversed`/`toReversed` en los archivos `JSArray`/`ArrayPrototype` disponibles. Para CVE-2022-42856 y CVE-2023-32439 no se puede declarar presencia o ausencia en todo 601-1300 a partir de los archivos descargados: el path `FTLLowerDFGToB3.cpp` no estaba disponible en el subconjunto consultado, y la ausencia de un archivo no equivale a ausencia de la lógica en otra organización de la rama.

## Diagnóstico no explotativo

Se añadió:

```text
webkit-kit/tools/jsc_vulnerability_condition_check.py
```

El script sólo lee archivos fuente y produce JSON. Para CVE-2020-9802 busca `ArithNegate`, `ArithAbs`, `PureValue` y `arithMode()` y distingue:

| Resultado | Criterio textual |
|---|---|
| `FIXED_LIKE` | aparece `PureValue(node, node->arithMode())` en el conjunto JSC/DFG analizado |
| `VULNERABLE_LIKE` | aparece `PureValue(node)` junto a `ArithNegate`/`ArithAbs` y no aparece la forma corregida |
| `UNVERIFIED` | faltan señales suficientes o no está disponible el archivo relevante |

Uso futuro con una fuente retail ya autorizada:

```bash
python3 webkit-kit/tools/jsc_vulnerability_condition_check.py \
    /ruta/a/fuente-o-extraccion-no-protegida \
    --output diagnostico.json
```

Para un módulo retail sin fuentes, el script no debe recibir el binario como si fuera código fuente. En ese caso se requiere primero el analizador ELF/SELF existente y una capa de extracción de strings/bytes que genere un informe de señales, manteniendo la clasificación `UNVERIFIED` salvo que la evidencia sea suficiente.

## Firmas exactas para verificar en 13.52

Una comparación estática futura debe localizar conjuntamente:

```text
DFGClobberize
ArithNegate
ArithAbs
PureValue
arithMode()
CheckOverflow / Unchecked, si la nomenclatura permanece
```

El resultado sólo puede promoverse a `DIRECT_13.52` si el archivo o módulo tiene procedencia verificable de PS4 13.52. Las coincidencias de nombres en WPE, upstream o WebKit-601-1300 son `STRONG_INDIRECT_13.52` como máximo.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| CVE-2020-9802 y su causa DFG/CSE | `HISTORICAL_ONLY` para upstream/Apple |
| Commit upstream `951d27d5...` | `HISTORICAL_ONLY` |
| `DFGClobberize.h` 601-1300 contiene `PureValue(node, node->arithMode())` | `STRONG_INDIRECT_13.52` sólo como evidencia de línea Sony antigua; `DIRECT` para el snapshot 601-1300 |
| CVE-2020-9802 presente en PS4 13.52 | `UNVERIFIED` |
| CVE-2020-9802 corregido en PS4 13.52 | `UNVERIFIED` |
| `toReversed` ausente del subconjunto JSArray consultado | `HISTORICAL_ONLY`/`UNVERIFIED`, no ausencia retail |
| Condición vulnerable encontrada en 13.52 | `UNVERIFIED` |

## Conclusión

El candidato CVE-2020-9802 queda preparado para correlación inmediata. La comprobación más importante es que el snapshot público Sony 601-1300 ya muestra la forma corregida de `PureValue` con `ArithMode`, de modo que no debe asumirse que la vulnerabilidad histórica de Apple estaba presente en esa rama Sony.

Esto no resuelve PS4 13.52: falta una revisión Sony posterior o bytes retail verificables. Con ellos, las primeras búsquedas deben centrarse en `DFGClobberize`, `ArithNegate`, `ArithAbs`, `PureValue` y `arithMode()`, y el diagnóstico debe comparar la condición completa, no sólo la existencia de una cadena.

## Referencias

[1]: https://projectzero.google/2020/09/jitsploitation-one.html "Project Zero — JITSploitation I"
[2]: https://github.com/WebKit/WebKit/commit/951d27d5ba08b6c29370b05dc6b4ffe18be1ca18 "WebKit upstream fix for CVE-2020-9802"
[3]: https://github.com/FreeBSDKernel9-0/PS4OSSCode/tree/d636699770323d7968a2c37955aa513bda5f8a37/WebKit-601-1300 "Sony WebKit-601-1300 mirror"
[4]: https://www.playstation.com/content/dam/global_pdc/en-us/external-resources/oss/ps4/webkit/WebKit-601-1300.zip "Sony WebKit-601-1300 OSS archive"
