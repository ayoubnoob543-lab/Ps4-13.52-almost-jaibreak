# Estructura del repositorio

## Principio

`firmware-lab` mezcla código ejecutable, herramientas de análisis, evidencia preservada y resultados generados. Esa mezcla es histórica y no se debe “limpiar” borrando archivos por tamaño. La organización se realiza mediante rutas, índices y reglas claras.

| Clase | Rutas principales | Tratamiento |
|---|---|---|
| Código fuente | `kpayload/`, `installer/`, `src/`, `webkit-kit/homebrew/src/` | Revisión de código, build y tests. |
| Herramientas | `tools/`, `webkit-kit/tools/`, `research/experiments/*/run*` | Deben documentar entradas, salidas y si ejecutan procesos externos. |
| Tests/fixtures | `tests/`, `webkit-kit/tests/`, `tests/fixtures/` | No son evidencia de hardware; sólo validan contratos o parsers. |
| Evidencia | `analysis/`, `research/results/`, `research/logs/` | Conservar hash, fecha, fuente y clasificación. |
| Experimentos | `research/experiments/`, `experiments/` | Deben marcar requisitos de hardware y riesgos; no se ejecutan automáticamente. |
| Documentación | `README.md`, `docs/`, `RESEARCH_STATUS.md`, READMEs locales | Debe diferenciar hechos, inferencias y precedentes. |
| Artefactos binarios | raíz, `goldhen/`, `research/libkernel/`, `installer/source/*.inc.c` | No mover ni borrar automáticamente; revisar licencia y procedencia. |
| Dependencias | `third_party/` | Submódulos fijados; inicialización explícita mediante Git. |

## Regla para nuevos archivos

Cada archivo nuevo debe poder responder a estas preguntas: qué firmware cubre, si es fuente o resultado, cómo se reproduce, qué hash tiene cuando es un artefacto, y si requiere hardware. Si no se puede responder, debe clasificarse como `UNVERIFIED` o `LOCAL_NOTE`.

## Qué no debe hacerse

No se deben renombrar masivamente rutas usadas por Makefiles, scripts o CI sin actualizar referencias y ejecutar tests. No se deben eliminar binarios grandes, dumps, chunks o logs protegidos sólo para reducir el tamaño. No se deben convertir resultados de una versión en evidencia de otra versión por similitud.

## Índices canónicos

`ARTIFACTS.md` es el índice de artefactos y procedencia. `docs/EVIDENCE_POLICY.md` define las etiquetas. `RESEARCH_STATUS.md` resume el estado global. Los READMEs dentro de subdirectorios describen únicamente su área y no deben copiar el estado completo de otra rama.
