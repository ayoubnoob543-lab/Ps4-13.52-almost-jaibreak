# Pipeline estático para un módulo WebKit retail autorizado

Este pipeline analiza únicamente un archivo local autorizado. No descarga PUPs, no intenta descifrar contenido protegido, no ejecuta el artefacto, no desensambla, no genera gadgets y no produce offsets operativos.

## Entrada y salida

La entrada puede ser un ELF, un SELF que contenga un ELF reconocible o un archivo raw. La salida es un JSON reproducible con SHA-256, cabeceras ELF disponibles, programas `PT_LOAD`, notas y Build ID, información dinámica, símbolos dinámicos, strings relevantes, candidatos de xrefs y correlación con las tres familias.

```bash
cd /home/ubuntu/firmware-lab-bundle
python3 webkit-kit/tools/analyze_webkit_retail.py \
  /ruta/local/al/modulo-autorizado \
  --signatures webkit-kit/three_family_signatures.json \
  --output /ruta/fuera-del-repo/modulo-static-evidence.json
```

Puede suministrarse un manifest pequeño para registrar la procedencia del archivo exacto. El hash debe calcularse sobre los mismos bytes que se analizan:

```json
{
  "firmware": "13.52",
  "source": "descripción/procedencia autorizada",
  "authorized": true,
  "artifact_sha256": "<sha256 del módulo>",
  "build_id": "<opcional>"
}
```

```bash
python3 webkit-kit/tools/analyze_webkit_retail.py \
  /ruta/local/al/modulo-autorizado \
  --signatures webkit-kit/three_family_signatures.json \
  --provenance /ruta/evidence/modulo.provenance.json \
  --output /ruta/evidence/modulo.static.json
```

`provenance.status` puede ser `MISSING`, `INVALID`, `NOT_13_52`, `INSUFFICIENT` o `ELIGIBLE_FOR_MANUAL_REVIEW`. El último sólo significa que el hash declarado coincide y que el manifest declara firmware 13.52, una fuente y autorización; no constituye una confirmación independiente de la build.

El resultado nunca puede tener `CONFIRMED_13.52`: el campo `target_promotion` queda fijado a `CONFIRMED_13.52_DISABLED`. La identidad semántica permanece `UNVERIFIED` hasta que se verifiquen procedencia, bytes y correspondencia de build por medios independientes.

## Campos principales

| Campo | Significado |
|---|---|
| `sha256` | Hash del archivo de entrada, calculado en modo lectura |
| `container.format` | `ELF`, `SELF_OR_EMBEDDED_ELF` o `UNKNOWN_OR_RAW` |
| `container.pt_load` | Segmentos `PT_LOAD` observados, sin modificar la entrada |
| `container.build_ids` | Notas GNU Build ID si están presentes |
| `container.dynamic_symbols` | Imports/exports dinámicos cuando las tablas son accesibles |
| `relevant_strings` | Strings del manifiesto de las tres familias y sus offsets |
| `xref_candidates` | Coincidencias conservadoras de valores 32/64-bit con offsets de strings; no son desensamblado |
| `family_correlations` | Clasificación `MATCH`, `PARTIAL MATCH`, `VULNERABLE_LIKE`, `FIXED_LIKE`, `NO MATCH` o `UNVERIFIED` |
| `evidence` | `DIRECT_BYTES` sólo significa que se leyó el archivo local; no prueba que sea retail 13.52 |
| `provenance` | Validación interna del manifest: hash, firmware declarado, fuente, autorización y elegibilidad para revisión manual |

## Interpretación de las tres familias

`JSCell::toX` se correlaciona mediante `toPrimitive`, `toNumber`, `toObjectSlow`, ramas para String/Symbol/BigInt/Object y los patrones `jsDynamicCast`/`jsSecureCast` frente a casts no comprobados.

`MarkedVector` se correlaciona mediante `MarkedVectorBase`, `markLists`, `addMarkSet`, `Heap::markListSet`, crecimiento/overflow y la conexión con almacenamiento de celdas o deserialización.

`CloneSerializer`/`CloneDeserializer` se correlaciona mediante `SerializedScriptValue`, `ObjectReferenceTag`, `m_gcBuffer`, `m_objectPool`, `m_keepAliveBuffer`, altas de object pool, tags e índices.

La clasificación `VULNERABLE_LIKE` o `FIXED_LIKE` sólo expresa que el patrón observado se parece al estado anterior o posterior de la referencia upstream. No equivale a una vulnerabilidad confirmada.

## Flujo recomendado cuando aparezca un módulo

```bash
set -e
mkdir -p /ruta/evidence
sha256sum /ruta/local/modulo > /ruta/evidence/modulo.sha256
python3 webkit-kit/tools/analyze_webkit_retail.py \
  /ruta/local/modulo \
  -o /ruta/evidence/modulo.static.json
python3 -m json.tool /ruta/evidence/modulo.static.json >/dev/null
```

Conserve el original fuera de Git y versiona sólo el manifest JSON pequeño, su hash, procedencia autorizada y el informe textual. No renombre un resultado a `13.52` salvo que exista documentación de procedencia y una verificación independiente de la build. Un manifest con hash incorrecto queda `INVALID` y nunca habilita revisión manual.

## Criterios de decisión

| Estado | Criterio |
|---|---|
| `MATCH` | Familia identificada por varias señales independientes, sin afirmar estado vulnerable |
| `PARTIAL MATCH` | Sólo una parte de la familia o evidencia insuficiente para reconstruir el flujo |
| `VULNERABLE_LIKE` | Evidencia de patrón anterior a la corrección upstream |
| `FIXED_LIKE` | Evidencia de patrón posterior a la corrección upstream |
| `NO MATCH` | ELF con tablas de símbolos dinámicos parseables y sin señales de la familia |
| `UNVERIFIED` | Raw/stripped o evidencia insuficiente para decidir |
| `CONFIRMED_13.52` | Estado deliberadamente deshabilitado por diseño en esta herramienta |

## Validación local

```bash
python3 -m json.tool webkit-kit/three_family_signatures.json >/dev/null
python3 -m py_compile webkit-kit/tools/*.py
PYTHONPATH=webkit-kit/tools python3 -m unittest discover -s webkit-kit/tests -p 'test_*.py' -q
git diff --check
```

Todos los tests usan fixtures sintéticos o archivos locales ya disponibles. Ningún test ejecuta un módulo PS4 ni intenta extraer o descifrar un PUP.
