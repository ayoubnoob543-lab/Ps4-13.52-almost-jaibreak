# Auditoría profunda de `ayoubnoob543-lab/firmware-lab`

**Fecha:** 26 de agosto de 2026  
**Rama revisada:** `main`  
**HEAD:** `f0031f194500eb2e15150a3bdeb5f9d598d92ab3` (`pre-release-main-270`)  
**Alcance:** archivos rastreados por Git, submódulos inicializados, configuración de CI, documentación, código C/JavaScript/Java/Python/shell, manifiestos, binarios y pruebas declaradas. No se ejecutaron payloads, exploits ni experimentos contra hardware.

## Resumen ejecutivo

El repositorio es un laboratorio de investigación estática y de ingeniería de payloads para PS4 13.52. La separación conceptual entre **evidencia directa**, **evidencia estructural** y **afirmaciones no verificadas** está bien documentada, y el proyecto contiene controles de integridad de dumps, manifests y análisis reproducibles. La suite de pruebas disponible pasó después de completar el entorno: **36 pruebas aprobadas, 4 omitidas y 3 subtests aprobados**.

La principal debilidad inmediata es operativa: el build publicado en `main` **no compila con GCC 13.3.0** porque ambos Makefiles incluyen `-Wno-error=return-mismatch`, una opción no reconocida por este compilador. El workflow depende de una imagen/acción externa para proporcionar otro toolchain, por lo que la compilación local y la reproducibilidad fuera de CI quedan rotas.

También hay riesgos de cadena de suministro y publicación. `build.sh` descarga `plugins.zip` desde una URL mutable `releases/latest/download` sin verificar el SHA-256 documentado en `ARTIFACTS.md`; además, `sanity-check.yml` tiene `contents: write` y crea una pre-release automáticamente en cada push que no sea pull request. Esto amplía innecesariamente la superficie de publicación y puede convertir un cambio ordinario en un artefacto distribuido.

| Prioridad | Hallazgo | Impacto | Estado |
|---|---|---|---|
| P0 | El build falla con GCC por `-Wno-error=return-mismatch` | No se puede reproducir el build estándar localmente | Confirmado |
| P1 | Descarga mutable de plugins sin verificación criptográfica en el script | Riesgo de supply chain y builds no deterministas | Confirmado |
| P1 | CI con permiso de escritura y publicación automática en cada push | Riesgo de publicación accidental o abuso del token | Confirmado |
| P1 | Literales `777` decimales en `mkdir` | Permisos distintos de los pretendidos en runtime | Confirmado por inspección |
| P2 | Gestión de errores débil en `write_blob` (`fd > 0`) | Falla silenciosa si `open()` devuelve descriptor 0 | Confirmado por inspección |
| P2 | Dependencias Python no declaradas/pinneadas | Entorno de pruebas no reproducible | Confirmado |
| P2 | Documentación extensa y parcialmente duplicada | Mayor coste de mantenimiento y riesgo de contradicciones | Observado |

## 1. Inventario y composición

El checkout contiene **676 entradas rastreadas por Git** en el repositorio principal. Al inicializar los submódulos, se cubrieron además **100 archivos** de `third_party/henloader_lp` y **76 archivos** de `third_party/ps4-payload-sdk`, fijados respectivamente en `15f49b2e18b3f233dcbc9744b8aa527d54e1fb5d` y `46efae910f3705e0171edea5b94e572d01bc00e8`.

La huella local ocupó aproximadamente **1008 MB**, dominada por binarios, dumps, corpus de investigación, fuentes históricas y artefactos de análisis. La distribución funcional es la siguiente:

| Área | Contenido | Evaluación |
|---|---|---|
| `kpayload/` | Payload kernel, offsets por firmware, linker y helpers | Implementación de bajo nivel; depende de toolchain x86-64/FreeBSD-compatible |
| `installer/` | Instalador, configuración, empaquetado de plugins y payload | Punto de integración y mayor superficie operacional |
| `webkit-kit/` | Pipeline WPE/WebKit, fixtures, harnesses y análisis runtime | Predominantemente experimental/host-side |
| `research/` y `analysis/` | Resultados, logs, manifests, fuentes y experimentos | Gran volumen de evidencia y trazabilidad |
| `tools/` | Validadores, analizadores, conversores y generadores | Buena automatización, pero dependencias no formalizadas |
| `tests/` | Pruebas estáticas, manifests y migración | Cobertura útil; depende de pytest aunque CI usa unittest |
| `goldhen/`, binarios raíz y dumps | Artefactos históricos y blobs | Requieren políticas claras de procedencia, licencia y distribución |
| `third_party/` | SDK y loader como submódulos Git | Versiones fijadas, pero no vendorizadas |

El inventario detectó binarios PS4, dumps `libkernel`, imágenes ISO, payloads y datos de investigación. El repositorio los trata como artefactos de análisis, no como evidencia automática de compatibilidad con 13.52; esa distinción es correcta y debe conservarse.

## 2. Arquitectura y flujo de build

El flujo principal es:

1. `kpayload/Makefile` compila todos los `.c` del payload con optimización `-Os`, sin libc ni startup estándar, genera el binario plano y crea `installer/source/kpayload.inc.c`.
2. `build.sh` verifica herramientas, obtiene cinco plugins, convierte cada `.prx` a arrays C mediante `xxd`, incorpora `hen.ini` y ejecuta `installer/Makefile`.
3. `installer/Makefile` copia el SDK a `installer/build/sdk-libps4`, aplica parches locales a `types.h`, `syscall.h` y `syscall.s`, compila una biblioteca local `libPS4.a`, enlaza el instalador y produce `hen.bin`.
4. La CI valida hashes y concatenación de los tres chunks `lk_dump*.bin`, ejecuta el análisis estático y publica el payload.

La estructura es razonable para un laboratorio que combina firmware, análisis binario y payloads, pero mezcla en el mismo árbol código de producción, corpus histórico, resultados generados, logs, herramientas de investigación y assets redistribuibles. Esto dificulta establecer qué debe pasar revisión de código, qué debe regenerarse y qué sólo debe conservarse como evidencia.

## 3. Hallazgos técnicos detallados

### P0 — El build estándar falla con GCC 13.3.0

**Ubicación:** `kpayload/Makefile:273`, `installer/Makefile:385`, `installer/Makefile:438`.

Durante la auditoría, después de instalar el toolchain declarado por el preflight, `bash build.sh` falló en la primera unidad de compilación:

```text
cc1: error: ‘-Wno-error=return-mismatch’: no option ‘-Wreturn-mismatch’
make: *** [Makefile:78: build/fpkg.o] Error 1
```

El flag aparece en ambos Makefiles. La acción recomendada es eliminarlo o condicionarlo al compilador que realmente lo soporte; no conviene silenciar globalmente advertencias desconocidas. Debe añadirse una prueba de build local con GCC y otra con Clang, porque el proyecto declara ambos modos.

### P1 — Descarga no determinista de plugins

**Ubicación:** `build.sh:55-57`; referencia de hash en `ARTIFACTS.md:26`.

El script usa:

```sh
https://github.com/Scene-Collective/ps4-hen-plugins/releases/latest/download/plugins.zip
```

La URL `latest` puede cambiar sin modificar el commit del laboratorio. Aunque `ARTIFACTS.md` documenta un SHA-256, `build.sh` no lo calcula ni falla si el contenido no coincide. Esto rompe la reproducibilidad y permite que un cambio upstream altere el payload construido.

Debe fijarse una URL de release/tag o un commit inmutable, descargar a un archivo temporal, verificar tamaño y SHA-256 esperado y rechazar cualquier discrepancia. Como defensa adicional, la CI debería conservar el hash de cada plugin y de `plugins.zip` como artefacto de build.

### P1 — Publicación automática excesivamente permisiva en CI

**Ubicación:** `.github/workflows/sanity-check.yml:20-23`, `:121-130`.

El job tiene `permissions: contents: write` y crea una pre-release para cada ejecución que no sea pull request. El workflow se dispara en `push`, por lo que un push normal a una rama puede generar y publicar un release. La escritura debería limitarse al job de publicación, ejecutarse sólo en tags o mediante aprobación explícita y usar permisos de lectura para los jobs de build y auditoría.

Una separación recomendada es `build-and-test` con `contents: read`, seguido por `publish` condicionado a `refs/tags/*`, con environment protegido y aprobación manual para distribución.

### P1 — Modos de archivo incorrectos por literales decimales

**Ubicación:** `installer/source/common.c:541-545`.

El código usa `mkdir(PS4UPDATE_FILE, 777)` y `mkdir(PS4UPDATE_TEMP_FILE, 777)`. En C, `777` es decimal; el literal octal habitual para permisos Unix es `0777`. Esto no produce los permisos esperados y puede causar comportamiento incorrecto o permisos inesperados en el entorno objetivo. Debe sustituirse por una constante explícita, idealmente una política mínima como `0700` o el modo documentado por el runtime, y comprobar el valor de retorno.

### P2 — Descriptor 0 tratado como error

**Ubicación:** `installer/source/common.c:512-522`.

`open()` puede devolver legítimamente el descriptor `0` si stdin está cerrado. El código sólo escribe cuando `fd > 0`; debería usar `fd >= 0`. Además, si `write()` devuelve un valor parcial, sólo se notifica y no se reintenta ni se limpia de forma explícita. La función debería distinguir `open < 0`, hacer un bucle de escritura hasta completar o fallar y preservar el código de error.

### P2 — Dependencias de Python no formalizadas

El repositorio contiene tests que se ejecutan con pytest, pero no declara `pytest` en un `requirements.txt`, `pyproject.toml` u otro lockfile. En el entorno inicial, `python3 -m pytest` falló porque pytest no estaba instalado. Tras instalarlo, la suite pasó. La CI usa `unittest discover` en `static-audit.yml`, mientras que varias pruebas están organizadas con clases/marcadores de pytest. Esta divergencia puede ocultar tests no ejecutados en CI.

Debe definirse un entorno único, por ejemplo `pyproject.toml` con dependencias de test fijadas, y hacer que CI ejecute explícitamente la misma suite que se espera localmente. También debe fijarse la versión mínima de Python, ya que el entorno local observado usó Python 3.12.3 y la CI declara 3.11.

### P2 — Preflight correcto, pero inicialmente incompleto para un checkout limpio

`tools/check_env.sh` detectó inicialmente la falta de `gcc`, `xxd` y la ausencia de submódulos inicializados. Tras instalar el toolchain y ejecutar `git submodule update --init --recursive`, el preflight pasó. Esto demuestra que el chequeo es útil, pero el README debería incluir un bootstrap reproducible y la CI debería validar también que la ruta local sin la acción externa de SDK puede compilar.

### P2 — Documentación y resultados generados mezclados con fuentes

Hay numerosos informes de sesión, logs, JSON de resultados y archivos de investigación junto al código. La trazabilidad es buena, pero no existe una política automatizada visible que distinga fuente, fixture, resultado generado y artefacto descargado. Se recomienda separar `generated/`, `fixtures/`, `evidence/` y `src/`, o al menos documentar por directorio qué archivos son regenerables y cuáles son evidencia preservada.

## 4. Verificaciones ejecutadas

| Verificación | Resultado |
|---|---|
| Sintaxis shell de todos los `.sh` rastreados | Aprobada |
| Compilación sintáctica de Python (`compileall`) | Aprobada |
| Sintaxis JavaScript con `node --check` | Aprobada |
| Validación de todos los JSON rastreados | Aprobada |
| `git fsck --full --no-reflogs --unreachable` | Sin salida problemática observada |
| `tools/check_source_quality.py` | `source_quality=PASS`, shell/JS/Java/offsets aprobados |
| `tools/check_env.sh` con toolchain y submódulos | Aprobada después de preparar el entorno |
| Suite pytest (`tests` y `webkit-kit/tests`) | **36 passed, 4 skipped, 3 subtests passed** |
| Build completo `bash build.sh` con GCC 13.3.0 | **Falló por `-Wno-error=return-mismatch`** |
| `unittest discover` sin patrón/ruta explícitos | 0 tests; no es un runner fiable para este checkout |

Los cuatro skips de pytest corresponden a capacidades o clones externos no disponibles en el entorno, no a fallos de las pruebas ejecutadas. Deben quedar documentados como skips esperados y no como cobertura completa.

## 5. Prioridad de remediación

| Orden | Acción | Criterio de aceptación |
|---|---|---|
| 1 | Corregir el flag `return-mismatch` en ambos Makefiles | `bash build.sh` compila con GCC y Clang en un entorno limpio |
| 2 | Fijar y verificar criptográficamente `plugins.zip` | Hash esperado validado antes de `unzip`; build falla ante mismatch |
| 3 | Restringir publicación CI a tags/entornos protegidos | Push ordinario sólo construye y prueba; no publica releases |
| 4 | Corregir `777` a modos octales mínimos y comprobar errores | Tests estáticos detectan literales de modo sospechosos |
| 5 | Cambiar `fd > 0` por `fd >= 0` y robustecer escrituras parciales | Prueba host-side cubre fd 0, error y partial write |
| 6 | Formalizar dependencias y runner | Un comando documentado reproduce los 36 tests aprobados |
| 7 | Separar fuentes y resultados generados | Un contributor nuevo puede identificar qué se edita y qué se regenera |

## Conclusión

El repositorio tiene una base de investigación sólida: hashes y procedencia están mejor tratados que en un proyecto experimental típico, la documentación marca explícitamente límites de evidencia y los validadores estáticos son útiles. Sin embargo, **no debe considerarse reproducible de extremo a extremo todavía**: el build principal falla con el compilador estándar disponible, el input de plugins es mutable y la publicación CI tiene permisos más amplios de lo necesario. Corregir esos tres puntos elevaría sustancialmente la calidad operativa sin alterar el contenido de investigación ni exigir cambios en los artefactos históricos.

## Referencias internas

[1]: `README.md` — objetivo, estado de evidencia y límites del proyecto.  
[2]: `AGENTS.md` — reglas de almacenamiento, borrado y preservación de artefactos.  
[3]: `ARTIFACTS.md` — inventario, hashes y procedencia declarada.  
[4]: `build.sh` — flujo de descarga, empaquetado y build principal.  
[5]: `kpayload/Makefile` — compilación del payload kernel.  
[6]: `installer/Makefile` — build del SDK local e instalador.  
[7]: `installer/source/common.c` — escritura de blobs y bloqueo de actualizaciones.  
[8]: `.github/workflows/sanity-check.yml` — build, permisos y publicación.  
[9]: `.github/workflows/static-audit.yml` — controles de CI y runner alternativo.  
[10]: `tools/check_env.sh`, `tools/check_source_quality.py` — preflight y controles internos.  
[11]: `tests/`, `webkit-kit/tests/` — pruebas ejecutadas durante la auditoría.
