# Preparación del análisis estático de WebKit PS4 13.52

## Herramientas disponibles

| Herramienta | Estado | Capacidad |
|---|---|---|
| `structural_signatures.py` | **MEJORADA/PASS** | SHA-256, detección ELF64/raw, cabeceras, PT_LOAD, PT_NOTE, GNU Build ID, PT_SCE_RELRO, dynamic NEEDED/SONAME, marcadores SCE y tokens de strings/ventanas |
| `compare_signatures.py` | **AVAILABLE** | Comparación estructural conservadora; no resuelve semántica ni offsets |
| `make_triple_manifest.py` | **AVAILABLE** | Manifiesto de los tres módulos y estado de presencia |
| `analyze_module_evidence.py` | **NUEVA/PASS** | Pipeline de un target con referencias OSS/WPE opcionales; produce JSON y clasificación `CANDIDATE_STRUCTURAL_ONLY` |
| `kit_health.py` | **AVAILABLE** | Auditoría de secretos/políticas inseguras |
| smoke host | **PASS** | Sólo ECMAScript host; no prueba retail PS4 |

El pipeline no ejecuta el archivo, no desensambla, no genera gadgets, no resuelve offsets absolutos y no promueve una coincidencia estructural a identidad de firmware.

## Uso cuando aparezca un módulo legalmente accesible

```bash
python3 webkit-kit/tools/structural_signatures.py \
  /ruta/libSceNKWebKit.sprx \
  -o evidence/libSceNKWebKit.signatures.json

python3 webkit-kit/tools/analyze_module_evidence.py \
  /ruta/libSceNKWebKit.sprx \
  --reference /ruta/WebKit-601-1300-reference.bin \
  --reference /ruta/wpe-reference.bin \
  -o evidence/libSceNKWebKit.evidence.json

python3 webkit-kit/tools/make_triple_manifest.py \
  /ruta/al/conjunto -o evidence/triple-manifest.json
```

La salida debe conservar SHA-256, tamaño, formato, clase, endianness, machine, entry, program headers, PT_LOAD, PT_SCE_RELRO, PT_NOTE/build-id, NEEDED/SONAME, marcadores SCE, tokens de strings y ventanas hash. Las referencias WPE/OSS se usan sólo como `STRUCTURAL/PORTABLE`; nunca como prueba de equivalencia retail.

## Qué puede cruzarse ahora

Sin bytes retail 13.52 sólo son válidos los cruces siguientes:

1. La existencia y forma de fuentes OSS WebKit 601/616 y el runtime WPE 2.52.6.
2. La presencia de interfaces, nombres de procesos, bibliotecas y contratos documentados.
3. Fingerprints de archivos de referencia que permitan detectar similitud o divergencia cuando llegue el target.
4. Diferencias de contenedor, máquina, segmentos, SONAME/NEEDED y Build ID cuando ambos lados tengan bytes.

No son válidos ahora los cruces de offsets, vtables, GOT concretas, gadgets, ABI retail ni funciones equivalentes por nombre solamente.

## Clasificación de hipótesis

| Hipótesis/afirmación | Clasificación | Razón |
|---|---|---|
| WPE 2.52.6 ejecuta DOM/CSS/JS en Linux | **CONFIRMADA EN WPE/LINUX** | Smoke real 2.52.6 publicado |
| WebKit OSS 13.00 es una fuente pública cercana | **CONFIRMADA/DOCUMENTADA** | Página OSS oficial de Sony |
| WebKit OSS 13.00 es idéntico al retail 13.52 | **IMPOSIBLE DE DETERMINAR SIN BYTES** | Falta target 13.52 |
| CSSFontFace tiene cambios que alcanzan PS4 13.52 | **DOCUMENTADA PERO NO DEMOSTRADA COMO EQUIVALENCIA BINARIA** | README público del proyecto |
| El exploit CSSFontFace publicado funciona en PS4 13.52 | **PARCHEADA/NO SOPORTADA POR EL REPO** | El README limita la explotación implementada a 6.00–11.02 |
| `libkernel_sys_13.52.bin` identifica WebKit 13.52 | **FALSA/NO VÁLIDA** | Es un módulo distinto; no contiene los tres módulos WebKit target |
| GOT/vtables/offsets retail 13.52 pueden derivarse de WPE u OSS | **IMPOSIBLE DE DETERMINAR SIN BYTES** | Requieren layout y compilación target |
| WPE es un laboratorio comparativo útil | **CONFIRMADA COMO PORTABLE** | Engine host probado, sin promoción a PS4 retail |

## Dependencia crítica

El pipeline está listo, pero la evidencia directa sigue siendo cero para los tres módulos WebKit retail 13.52. El siguiente informe puede ser completo sólo después de recibir un archivo target legalmente accesible con procedencia y hash. Hasta entonces, cualquier `Build ID`, GOT, vtable, offset o coincidencia semántica debe permanecer `MISSING` o `UNVERIFIED`.
