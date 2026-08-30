# firmware-lab

`firmware-lab` es un repositorio de investigación y análisis estático centrado en artefactos de PlayStation 4, especialmente en las versiones de firmware 13.02 y 13.52.

El objetivo del proyecto es conservar herramientas, análisis, hashes, manifests, fixtures y documentación que puedan revisarse y repetirse. El repositorio separa lo que está comprobado de lo que sigue siendo una hipótesis o una línea de investigación abierta.

> **Estado actual:** este repositorio no contiene un jailbreak completo reproducible ni afirma compatibilidad funcional con una consola concreta.

## Resumen del estado

| Área | Estado | Qué puede afirmarse hoy |
|---|---|---|
| PS4 13.02 — WebKit/Vue userland | `CORROBORATED` | Hay documentación y correlación pública de la parte userland. Esto no demuestra acceso de kernel ni R/W. |
| PS4 13.02 — Netctrl/ucred | `UNVERIFIED_13_02` | El alcance funcional localizado no cubre de forma demostrada la versión 13.02. |
| PS4 13.02 — offsets | `SOURCE_ONLY` / `CORROBORATED_SOURCE_ONLY` | Existen tablas y referencias, pero no están validadas sobre bytes retail completos de 13.02. |
| PS4 13.02 — kernel retail | `MISSING_DIRECT_BYTES` | No hay un conjunto público verificado suficiente para validar toda la tabla. |
| PS4 13.02 — jailbreak completo | `NOT_REPRODUCIBLE` | No está demostrada la cadena userland → kernel R/W → parcheo. |
| PS4 13.52 — `libkernel_sys` | `DIRECT_BYTES` | Hay un blob y chunks con hashes reproducibles. Es `libkernel_sys`, no el kernel retail completo. |
| PS4 13.52 — PUP/SLB2 | `VERIFIED_METADATA` | Se han comprobado tamaño, hashes y estructura del contenedor; parte de su contenido sigue opaca. |
| PS4 13.52 — WebKit retail | `MISSING` | No hay bytes verificables de los módulos retail objetivo. |
| PS4 13.52 — kernel R/W | `UNVERIFIED` | Hay candidatos de investigación, pero no una cadena reproducible confirmada. |
| Build local | `REQUIRES_TOOLCHAIN` | Requiere toolchain x86-64, `xxd`, SDK preparado y entradas con procedencia. |
| Tests estáticos | `PASS_WITH_SKIPS` | Las pruebas disponibles pasan; algunas se omiten cuando falta una dependencia o un clon externo. |

Estas etiquetas hablan de evidencia y reproducibilidad. No son porcentajes de progreso, probabilidades de jailbreak ni una valoración general de la seguridad del firmware.

## Cómo leer el repositorio

La investigación sigue una secuencia sencilla:

```text
artefacto identificado → hash y procedencia → análisis estático
→ comparación independiente → prueba específica de firmware
```

Los hashes comprueban la integridad de un archivo, pero por sí solos no prueban que ese archivo proceda del firmware que se está estudiando. Del mismo modo, una tabla de offsets o una referencia de código puede ser útil para investigar, pero no sustituye la validación sobre bytes del firmware objetivo.

El análisis se realiza de forma estática por defecto. No se ejecutan automáticamente payloads, exploits, ISO, SELF, SPRX ni binarios recuperados. No deben publicarse claves, credenciales, dumps propietarios ni artefactos cuya procedencia no esté clara.

## Organización

| Ruta | Contenido |
|---|---|
| `kpayload/` | Código y tablas de payload de bajo nivel. |
| `installer/` | Integración, configuración y empaquetado. |
| `webkit-kit/` | Herramientas y documentos relacionados con WebKit, JSC, WPE y BD-J. |
| `research/` | Hipótesis, experimentos y resultados de investigación. |
| `analysis/` | Manifests, hashes, scans y resultados reproducibles. |
| `docs/` | Política de evidencia y documentación del repositorio. |
| `tests/` | Pruebas automatizadas y fixtures. |
| `tools/` | Validadores y utilidades de inspección. |
| `third_party/` | Dependencias externas fijadas por submódulos. |

La diferencia entre fuente, fixture, evidencia preservada y resultado generado está explicada en [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md). Las categorías usadas para describir la evidencia están en [`docs/EVIDENCE_POLICY.md`](docs/EVIDENCE_POLICY.md).

## Reproducibilidad

Para preparar el repositorio y sus submódulos:

```bash
git submodule update --init --recursive
bash tools/check_env.sh
```

Para ejecutar las comprobaciones disponibles:

```bash
python3 -m pytest -q tests webkit-kit/tests
python3 tools/check_source_quality.py
bash tools/run_static_audit.sh
```

El build local puede requerir un SDK, un toolchain x86-64 y entradas de plugins con hashes verificables. Que una herramienta compile en el host no demuestra que funcione en una consola ni que exista un jailbreak para una versión concreta.

## Estado de publicación

El repositorio está preparado como laboratorio público de investigación, no como producto terminado. Las conclusiones deben conservar siempre su firmware exacto, el artefacto utilizado, su hash, la procedencia, el método de análisis y el resultado observable.

Para conocer el detalle más reciente, consulta [`RESEARCH_STATUS.md`](RESEARCH_STATUS.md), [`ARTIFACTS.md`](ARTIFACTS.md) y la documentación de [`docs/`](docs/).
