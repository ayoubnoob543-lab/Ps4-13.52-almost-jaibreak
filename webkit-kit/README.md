# WebKit/JSC PS4 13.52 — kit de compatibilidad estática

Este directorio contiene un kit reproducible para **auditar, preparar y validar artefactos WebKit/JSC** relacionados con PS4 13.52. No contiene un WebKit retail de Orbis, un SDK propietario, un payload de explotación ni una cadena de escape de sandbox.

## Estado actual — sesión 60

Se verificaron públicamente dos PUP retail, PS4 13.50 y PS4 13.52, mediante tamaño, MD5, SHA-256 y tablas SLB2. El PUP 13.52 mide `503310848` bytes y tiene SHA-256 `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11`. El PUP 13.50 mide `503293952` bytes y tiene SHA-256 `04585405bf3ad0836103c1eea5c21657327a377824ad5cda7674ecb94f03822f`.

El diferencial de contenedor muestra un aumento de `16896` bytes: `+480` en `PS4UPDATE1.PUP` y `+16200` en `PS4UPDATE2.PUP`. Estas diferencias demuestran cambios de bytes internos, pero no identifican por sí solas WebKit, kernel o BD-J porque las entradas siguen siendo opacas.

El repositorio todavía **no contiene una copia verificable de `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, `bdjstack.jar`, `rt.jar` ni un WebKit retail PS4 13.52**. El blob `libkernel_sys_13.52.bin` es una entrada de análisis estático independiente y no sustituye al módulo WebKit.

## Candidatos WebKit/JSC actuales

La investigación pública identificó tres candidatos etiquetados tentativamente por PSDevWiki como `?6.00–13.52?`: `JSCell::toX`, `MarkedVector` y `CloneSerializer/Deserializer`. La propia fuente indica que no fueron probados en PS4, por lo que se clasifican como **STRONG_INDIRECT/UNVERIFIED**, no como vulnerabilidades confirmadas en 13.52.

También se documentaron candidatos upstream con diff y testcase: `DocumentFontLoader` (CVE-2024-54502), `TransformStream` (CVE-2026-43705) y la fase DFG `StoreBarrierInsertionPhase` (CVE-2025-43529). Ninguno tiene evidencia retail PS4 13.52 en este corpus.

La cadena pública CSSFontFace de `wobkot` está documentada para firmwares históricos hasta 11.02. El repositorio público no contiene una adaptación 13.52; los claims audiovisuales de un workaround posterior permanecen **DOCUMENTED_ONLY/UNVERIFIED**.

## Artefactos y herramientas

| Componente | Estado |
|---|---|
| PUP retail 13.50/13.52 | Hashes y SLB2 verificados; entradas internas opacas |
| Scanner ELF/SELF estático | Incluido en `tools/inspect_artifact.py` |
| Comparador de módulos 13.50/13.52 | `runtime/compare_extracted_modules.py` |
| Correlador de familias JSC | `tools/correlate_three_families.py` |
| Harness JavaScript no explotativo | Incluido en `harness/` |
| WebKit retail 13.52 | Ausente |
| Runtime BD-J/JVM retail 13.52 | Ausente |
| Laboratorio WPE/Linux | Disponible para análisis upstream, no equivalente a PS4 retail |

Las herramientas realizan lectura estática. No cargan ELF/SELF/SPRX, no ejecutan JavaScript recibido desde red y no invocan exploits.

## Flujo de integración legítimo

Cuando aparezca un artefacto con procedencia, fecha, tamaño y SHA-256, se inspeccionarán sus cabeceras, segmentos, imports/exports, strings y estructuras. Para una comparación funcional se necesita el mismo módulo en dos builds, por ejemplo:

```text
libSceNKWebKit_13.50.sprx  ↔  libSceNKWebKit_13.52.sprx
```

El comparador clasificará diferencias como `MATCH`, `PARTIAL` o `NO MATCH`; una coincidencia no constituye un exploit. La compilación de WebKit para hardware real requiere además un árbol de fuentes compatible, toolchain, headers, ABI de Orbis y librerías de plataforma; ninguno de esos elementos se presume aquí.

## Documentos recientes

- `runtime/WEBKIT_JSC_CANDIDATE_DEEP_RESEARCH_SESSION60.md`
- `runtime/WEBKIT_CANDIDATE_CORPUS_SESSION60.md`
- `runtime/UFM42_FONTFACE_DEEP_RESEARCH_SESSION59.md`
- `runtime/UFM42_WOBKOT_HISTORY_SESSION49.md`
- `runtime/PUP_1350_1352_STATIC_DIFF_SESSION51.md`
- `runtime/PS4_1350_1352_CLAIMS_VERIFICATION_SESSION50.md`
- `runtime/GITHUB_PUP_TOOLS_AUDIT_SESSION54.md`
- `runtime/PS4_PUP_EXTRACTOR_STATIC_AUDIT_SESSION52.md`

## Clasificación

`DIRECT_BYTES` significa que el archivo y su hash están disponibles. `STRUCTURAL` significa que sólo existe código, tabla o documentación compatible. `DOCUMENTED_ONLY` significa que sólo existe una afirmación pública. `UNVERIFIED` significa que falta evidencia específica de PS4 13.52. `MISSING` significa que no hay bytes verificables en el corpus.

Las referencias al kernel #6, `wifissh`, payloads históricos y binarios externos permanecen separadas de este kit y no se promocionan como inputs de WebKit.

## Reglas

No se suben claves, credenciales, PUP completos, eboots, payloads, ejecutables descargados ni dumps propietarios adicionales. Las conclusiones deben conservar la separación entre hecho, inferencia y precedente histórico, y no deben asignar un símbolo u offset únicamente por coincidencia de prólogo.
