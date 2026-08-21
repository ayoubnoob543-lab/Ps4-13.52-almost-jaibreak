# Inventario técnico de artefactos PS4 13.52 desde el corpus local

**Repositorio:** `ayoubnoob543-lab/firmware-lab`  
**Rama:** `webkit-ps4-1352-kit`  
**Ámbito:** auditoría estática de archivos ya presentes, metadata y herramientas versionadas.  
**Restricciones:** no se descargó material nuevo, no se descifró contenido protegido y no se ejecutaron PUP, ELF, SELF, SPRX, JAR, payloads ni hardware.

## 1. Resultado ejecutivo

El repositorio contiene **metadata verificable del PUP oficial identificado como PS4 13.52**, un inventario estructural de su contenedor SLB2, referencias históricas y herramientas para analizar un módulo accesible. No contiene, sin embargo, un `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, `eboot.bin`, `bdjstack.jar` ni `rt.jar` retail 13.52 analizables.

La distinción importante es la siguiente:

> El corpus permite demostrar la identidad y estructura exterior del PUP y preparar el análisis de un módulo futuro, pero no permite demostrar la presencia, contenido o versión de los módulos internos protegidos.

Por tanto, el estado correcto de WebKit y BD-J/JVM retail 13.52 sigue siendo **UNVERIFIED**. La metadata del PUP es evidencia `DIRECT_BYTES`/`DIRECT_13.52` únicamente para el contenedor y sus rangos; no es evidencia directa del contenido interno.

## 2. Archivos 13.52 realmente presentes

| Archivo local | Qué contiene | Estado | Clasificación |
|---|---|---|---|
| `analysis/pup_13.52_manifest.json` | Manifest estructural del PUP y entradas SLB2 | Archivo versionado y accesible | `DIRECT_13.52` para metadata |
| `PS4_1352_PUP_STATIC_METADATA_2026-08-20.json` | Fuente declarada, tamaño, SHA-256, ETag, SLB2 y hashes de las dos entradas | Archivo versionado y accesible | `DIRECT_13.52` para metadata |
| `PS4_1352_PUP_MODULE_ACCESS_STATUS_2026-08-20.md` | Resultado de inspección estática de rangos y estado de módulos | Informe versionado | `DIRECT_13.52` para resultados de inspección; módulos `UNVERIFIED` |
| `analysis/webkit_13.52.json` | Registro de disponibilidad del artefacto WebKit | `status: ABSENT`, sin bytes WebKit | `DIRECT_13.52` para inventario de ausencia |
| `analysis/webkit_13.52_research.json` | Registro de investigación/estado del artefacto | Metadata de investigación, no módulo | `DOCUMENTED_ONLY` |
| `webkit-kit/libkernel_sys_13.52.signatures.json` | Firmas/anotaciones de un blob de `libkernel_sys` | No es WebKit ni BD-J | `DIRECT_13.52` sólo para ese blob, no extrapolable |
| `PS4_1352_STATIC_BLOB_ANALYSIS_2026-08-20.json` | Análisis de blobs locales, incluyendo `libkernel_sys_13.52.bin` | Evidencia de blobs concretos, no runtime Java/WebKit | `DIRECT_13.52` sólo para cada blob con procedencia |

El PUP grande referenciado por el informe está fuera del repositorio Git en:

```text
/home/ubuntu/ps4-1352-authorized-pup/PS4UPDATE.PUP
```

Su existencia fuera de Git no convierte los módulos internos en archivos disponibles ni autoriza descifrado. El informe local registra que fue inspeccionado sólo mediante parsing estructural, cabeceras raw, nombres literales y magic bytes.

## 3. Metadata del PUP y hashes conocidos

La metadata versionada registra los siguientes valores:

| Campo | Valor |
|---|---|
| Firmware label | `13.52` |
| Fuente declarada | `https://pc.ps4.update.playstation.net/update/ps4/image/2026_0611/sys_2ce20d9fbb48274ceb369b40412e616c/PS4UPDATE.PUP` |
| Tamaño PUP | `503310848` bytes |
| SHA-256 PUP | `daa44e91f3d505977d6c64872cee2c0454c36cd2eccb784eb74d3b1bcd762c11` |
| ETag registrado | `2ce20d9fbb48274ceb369b40412e616c:1781579172.795957` |
| Contenedor | `SLB2`, versión `2`, flags `0` |
| Entradas | `2` |
| Tamaño declarado | `503310848` bytes |
| Descifrado | `false` |

Rangos internos registrados:

| Entrada | Offset | Tamaño | SHA-256 del rango |
|---|---:|---:|---|
| `PS4UPDATE1.PUP` | `1024` | `326026951` | `fd5e6c16398e628b3f258bce5f395c9fda687011a1a985d4b507928f54e6b580` |
| `PS4UPDATE2.PUP` | `326028288` | `177282367` | `44cd0c0e85b5912150112df99867357c3822a90f366198d11e2ec4c1e10adee7` |

Estos hashes prueban la identidad de los bytes registrados del PUP y de sus rangos SLB2. No son hashes de `bdjstack.jar`, `rt.jar`, `libSceNKWebKit.sprx` ni de ningún ELF/SELF interno.

## 4. Qué entradas se relacionan con BD-J, JVM y WebKit

El manifest no expone una tabla de archivos internos con nombres de BD-J/JVM/WebKit. La auditoría de nombres literales tampoco encontró, dentro de los rangos raw inspeccionados, los siguientes nombres o marcadores:

```text
libSceNKWebKit.sprx
libkernel_web.sprx
libSceLibcInternal.sprx
eboot.bin
WebProcess
JSCell
MarkedVector
CloneSerializer
```

La ausencia de un nombre literal en los rangos raw **no demuestra ausencia del módulo**. Sólo demuestra que el nombre no apareció en la representación inspeccionada sin descifrado/extracción del formato interno.

Tampoco se encontraron magic bytes interpretables como archivos internos directamente accesibles:

| Firma buscada | Resultado documentado |
|---|---|
| `\x7fELF` | No match en las dos entradas raw |
| `SCE\0` | No match |
| `SLB2` anidado | No match |
| `PK\x03\x04` | No match |

En consecuencia, no puede afirmarse desde el manifest que exista una entrada concreta `app0/bdjstack/bdjstack.jar` o `app0/bdjstack/lib/rt.jar` dentro del PUP. Esas rutas son referencias históricas importantes, pero actualmente están clasificadas como `HISTORICAL_ONLY` respecto a 13.52.

## 5. Artefactos locales relacionados pero no equivalentes

El repositorio sí contiene material que puede ser útil como referencia estructural, pero no debe confundirse con runtime retail 13.52:

| Material | Utilidad | Límite de inferencia |
|---|---|---|
| `webkit-kit/three_family_signatures.json` | Firmas de correlación para `JSCell::toX`, `MarkedVector`/GC y `CloneSerializer`/`objectPool` | No contiene bytes retail 13.52 |
| Fuentes WebKit OSS/WPE y builds host | Comparación de clases, símbolos y estructura upstream | No equivalen a `libSceNKWebKit.sprx` |
| `libkernel_sys_13.52.bin` y sus firmas | Análisis estático de un blob con etiqueta/procedencia local 13.52 | No contiene el runtime WebKit ni demuestra clases Java |
| Informes `webkit-kit/runtime/BDJ_*.md` | Reconstrucción histórica de contratos y mitigaciones | `HISTORICAL_ONLY` o `UNVERIFIED` sin bytes 13.52 |
| `analysis/phase16_binary_fingerprints.md` | Fingerprints estructurales y metodología | No prueba que un módulo ausente exista |
| `webkit-kit/tools/analyze_webkit_retail.py` | Pipeline para un módulo retail accesible | No puede crear ni extraer el módulo |
| `webkit-kit/tools/analyze_module_evidence.py` | Hash, formato, arquitectura, segmentos, símbolos, strings y correlación | Requiere un archivo ELF/SELF/SPSRX accesible |

No hay en el inventario de nombres versionados un archivo JAR retail 13.52, un snapshot de `system_ex`, un bootclasspath, una imagen de JVM o un módulo WebKit retail que pueda analizarse directamente.

## 6. Herramientas existentes y artefactos que aceptan

| Herramienta | Entrada prevista | Salida/capacidad | Aplicabilidad actual |
|---|---|---|---|
| `tools/parse_slb2_static.py` | PUP autorizado local | Valida magic SLB2, versión, flags, entradas, límites y rangos | Aplicable al contenedor; no interpreta payload protegido |
| `webkit-kit/tools/scan_pup_static_names.py` | PUP/rangos raw | Escaneo literal de nombres y marcadores | Aplicable; resultado negativo limitado a representación raw |
| `webkit-kit/tools/inspect_artifact.py` | Archivo local autorizado | Inspección inicial de magic, tamaño y hashes | Aplicable a cualquier archivo presente |
| `webkit-kit/tools/inventory_ps4_1352_artifacts.py` | Árbol/corpus local | Inventario de nombres, hashes y clasificación | Aplicable al corpus; no obtiene archivos ausentes |
| `webkit-kit/tools/analyze_module_evidence.py` | ELF/SELF/SPRX accesible | SHA-256, identificación, arquitectura, segmentos, Build ID, símbolos/imports/exports, strings y firmas | Preparado para módulo futuro; no aplicable como módulo al PUP raw |
| `webkit-kit/tools/analyze_webkit_retail.py` | WebKit retail accesible | Análisis retail y correlación WebKit | Bloqueado por ausencia de bytes retail |
| `webkit-kit/tools/make_manifest.py` | Archivos locales | Manifest/hash reproducible | Aplicable cuando aparezca un artefacto autorizado |
| `webkit-kit/tools/make_triple_manifest.py` | Artefactos de comparación | Manifest comparativo | Referencial; no crea equivalencia entre WPE y PS4 |
| `webkit-kit/tools/compare_signatures.py` | Informes/firmas | Comparación de patrones | Requiere evidencia de entrada real |
| `tests/test_pup_slb2_static.py` | Fixtures/parsers SLB2 | Tests de estructura estática | Validación del contenedor |
| `webkit-kit/tests/test_module_evidence_pipeline.py` | Fixtures de módulos sintéticos/locales | Tests del pipeline de módulos | No produce evidencia de 13.52 |

La cadena de análisis está diseñada como una cadena de **consumo de evidencia**, no como una cadena de extracción criptográfica:

```text
metadata PUP
  → identidad del contenedor SLB2 y rangos
  → archivo intermedio autorizado (ELF/SELF/SPRX/JAR o filesystem extraído)
  → parser específico del formato
  → componente/ruta interna
  → símbolo, clase, método o firma
  → clasificación de evidencia
```

Cada transición requiere un artefacto real. El manifest no puede saltar directamente a un símbolo de WebKit o a una clase de `rt.jar`.

## 7. Dato exacto que falta

El mínimo dato adicional depende de la pregunta:

| Pregunta | Artefacto mínimo necesario |
|---|---|
| Analizar `libSceNKWebKit.sprx` | Bytes del módulo ELF/SELF/SPRX ya extraídos y autorizados, con procedencia vinculada al PUP 13.52 |
| Analizar `libkernel_web.sprx` | El mismo tipo de módulo accesible, con hash y vínculo de procedencia |
| Analizar `libSceLibcInternal.sprx` | Bytes del módulo y metadata de procedencia; una referencia textual no basta |
| Analizar `bdjstack.jar` | Archivo JAR completo, hash y ruta/procedencia de filesystem 13.52 |
| Analizar `rt.jar` | Archivo JAR/bootclasspath completo, hash y procedencia 13.52 |
| Analizar JVM nativa | Imagen ELF/SELF/SO/SPRX de la JVM o snapshot de filesystem que preserve sus bytes |
| Determinar cambios 13.50→13.52 | Dos artefactos comparables del mismo componente, con procedencia y hashes independientes |
| Confirmar un símbolo/clase en 13.52 | Bytes o metadata de símbolo/clase pertenecientes inequívocamente a 13.52 |

Un nombre histórico, un hash de PUP, un informe de release o una similitud con WebKit OSS no satisface ese requisito.

## 8. Clasificación final

| Elemento | Clasificación correcta |
|---|---|
| Identidad exterior y tamaño del PUP | `DIRECT_13.52` |
| Estructura SLB2 y hashes de rangos | `DIRECT_13.52` |
| Pertenencia de `PS4UPDATE1.PUP`/`PS4UPDATE2.PUP` al contenedor registrado | `DIRECT_13.52` |
| Presencia de WebKit retail interno | `UNVERIFIED` |
| Presencia de `bdjstack.jar` en 13.52 | `UNVERIFIED` |
| Presencia de `rt.jar` en 13.52 | `UNVERIFIED` |
| Semántica exacta de JVM/BD-J en 13.52 | `UNVERIFIED` |
| WPE/WebKit OSS como sustituto retail | `DISCARDED` como equivalencia; `PORTABLE` sólo como referencia estructural |
| `libkernel_sys_13.52.bin` como WebKit | `DISCARDED` |
| Rutas históricas `app0/bdjstack/...` aplicadas automáticamente a 13.52 | `HISTORICAL_ONLY` |

## 9. Conclusión y siguiente punto de evidencia

No apareció un artefacto nuevo analizable. El inventario confirma que el repositorio ya contiene la evidencia exterior necesaria y que las herramientas para el siguiente análisis están preparadas. El bloqueo restante es específico: falta un **artefacto intermedio autorizado** que contenga los bytes de BD-J/JVM o WebKit, no otro parser del PUP.

La siguiente acción mínima es incorporar uno de estos elementos, sin descifrado no autorizado:

1. un `bdjstack.jar` o `rt.jar` extraído legítimamente del filesystem de 13.52, o
2. un `libSceNKWebKit.sprx`/`libkernel_web.sprx` accesible con hash y procedencia vinculados, o
3. un snapshot/manifest autorizado que incluya los bytes y rutas internas de esos componentes.

Hasta que aparezca uno de ellos, las conclusiones sobre clases Java, policy, Ixc, `ObjectStreamClass`, JIT o firmas WebKit deben permanecer `UNVERIFIED`.

## Referencias locales

[1]: `analysis/pup_13.52_manifest.json` — Manifest SLB2 versionado del PUP 13.52.
[2]: `PS4_1352_PUP_STATIC_METADATA_2026-08-20.json` — Metadata, fuente declarada, tamaño, ETag y hashes.
[3]: `PS4_1352_PUP_MODULE_ACCESS_STATUS_2026-08-20.md` — Resultado de inspección raw y estado de módulos.
[4]: `analysis/webkit_13.52.json` — Registro de disponibilidad del artefacto WebKit.
[5]: `webkit-kit/tools/analyze_module_evidence.py` — Analizador estático de módulos accesibles.
[6]: `tools/parse_slb2_static.py` — Parser estructural SLB2 sin descifrado.
[7]: `webkit-kit/tools/scan_pup_static_names.py` — Scanner literal de nombres y marcadores.
[8]: `webkit-kit/tools/inventory_ps4_1352_artifacts.py` — Inventario del corpus local.
[9]: `webkit-kit/three_family_signatures.json` — Firmas de correlación WebKit/JSC.
