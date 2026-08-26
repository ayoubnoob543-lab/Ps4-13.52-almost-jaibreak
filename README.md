# firmware-lab

Laboratorio de investigación estática y de ingeniería de herramientas para artefactos de PS4, con foco actual en las familias 13.02 y 13.52. El repositorio conserva código, analizadores, fixtures, manifests, dumps y documentación de procedencia. **No es un jailbreak terminado ni una afirmación de compatibilidad funcional con una consola concreta.**

## Estado verificable

| Área | Estado actual | Límite de la afirmación |
|---|---|---|
| PS4 13.02 — WebKit/Vue userland | `CORROBORATED` | La documentación pública cubre userland hasta 13.02; no demuestra kernel R/W. |
| PS4 13.02 — Netctrl/ucred | `UNVERIFIED_13_02` | El alcance funcional público localizado llega hasta 13.00. |
| PS4 13.02 — offsets | `SOURCE_ONLY` / `CORROBORATED_SOURCE_ONLY` | Existen tablas, pero no se han validado sobre bytes retail 13.02. |
| PS4 13.02 — kernel retail | `MISSING_DIRECT_BYTES` | No hay dump público verificado que permita validar toda la tabla. |
| PS4 13.02 — jailbreak completo | `NOT_REPRODUCIBLE` | Falta demostrar userland → kernel R/W → parcheo. |
| PS4 13.52 — libkernel_sys | `DIRECT_BYTES` | El blob y sus chunks tienen hashes reproducibles; sigue siendo libkernel, no kernel retail. |
| PS4 13.52 — PUP/SLB2 | `VERIFIED_METADATA` | Tamaño, hashes y contenedor verificados; las entradas internas siguen opacas. |
| PS4 13.52 — WebKit retail | `MISSING` | No están disponibles bytes verificables de los módulos WebKit retail objetivo. |
| PS4 13.52 — kernel R/W | `UNVERIFIED` | Hay candidatos de investigación, no una cadena reproducible confirmada. |
| Build local | `REQUIRES_TOOLCHAIN` | Requiere GCC/Clang x86-64, `xxd`, SDK inicializado y plugins con procedencia. |
| Tests estáticos | `PASS_WITH_SKIPS` | La suite disponible pasa; algunos tests requieren clones o dependencias externas. |

Estas etiquetas describen **evidencia y reproducibilidad**, no un porcentaje de avance, probabilidad de jailbreak ni seguridad del firmware. Se eliminan deliberadamente las métricas agregadas del tipo “100% de infraestructura / 15% indirecto / 0% bytes”, porque mezclaban unidades distintas y podían interpretarse como una medida objetiva de progreso global.

## Cadena de investigación

```text
artefacto identificado → hash/procedencia → análisis estático → correlación independiente
→ prueba específica de firmware → ejecución controlada autorizada
```

Para 13.02, la cadena relevante es WebKit/Vue userland → candidato de kernel → kernel R/W → offsets validados → parcheo/kexec. Sólo la primera etapa está razonablemente cubierta. Para 13.52, el laboratorio dispone de evidencia estática de `libkernel_sys` y metadata PUP, pero no de WebKit retail legible ni de un jailbreak reproducible.

## Organización del repositorio

| Ruta | Propósito |
|---|---|
| `kpayload/` | Código y tablas de payload de bajo nivel. |
| `installer/` | Integración del payload, configuración y empaquetado. |
| `webkit-kit/` | Herramientas y documentación de análisis WebKit/JSC/WPE/BD-J. |
| `research/` | Experimentos, resultados y líneas de investigación; cada hipótesis debe indicar alcance y requisitos. |
| `analysis/` | Manifests, hashes, scans y salidas de análisis reproducibles. |
| `docs/` | Documentación canónica, políticas y brechas conocidas. |
| `tests/` | Pruebas automatizadas y fixtures. |
| `tools/` | Validadores y utilidades de inspección. |
| `goldhen/` y binarios | Artefactos históricos o de referencia, no prueba automática de soporte. |
| `third_party/` | Dependencias externas fijadas mediante submódulos Git. |
| `research/webkit-1302/` | Investigación específica de WebKit y disco/BD-J para 13.02. |

La diferencia entre **fuente**, **fixture**, **evidencia preservada** y **resultado generado** se explica en [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md). La taxonomía de evidencia está en [`docs/EVIDENCE_POLICY.md`](docs/EVIDENCE_POLICY.md).

## Reglas de evidencia

Una afirmación `VERIFIED` exige firmware exacto, artefacto o ejecución reproducible, hash, método de adquisición y resultado observable. `CORROBORATED` significa que existe apoyo independiente o una comprobación local parcial, pero aún falta validación directa completa. `SOURCE_ONLY` indica una tabla, README, commit o inferencia sin bytes del firmware objetivo. `UNVERIFIED` y `MISSING` deben permanecer visibles; no se rellenan con extrapolaciones entre versiones.

No se ejecutan automáticamente payloads, exploits, ISO, SELF, SPRX ni binarios recuperados. El análisis de archivos es estático por defecto y no se publican claves, credenciales, dumps propietarios ni artefactos sin procedencia.

## Reproducibilidad

Preparar submódulos y toolchain:

```bash
git submodule update --init --recursive
bash tools/check_env.sh
```

Validar controles estáticos:

```bash
python3 -m pytest -q tests webkit-kit/tests
python3 tools/check_source_quality.py
bash tools/run_static_audit.sh
```

El build de payload requiere un toolchain x86-64 compatible, el SDK fijado y inputs de plugins con hash verificado. La compilación no demuestra ejecución ni compatibilidad con hardware PS4.

## Documentos canónicos

- [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md): estructura y reglas de clasificación de archivos.
- [`docs/EVIDENCE_POLICY.md`](docs/EVIDENCE_POLICY.md): vocabulario obligatorio para estados y conclusiones.
- [`ARTIFACTS.md`](ARTIFACTS.md): inventario de artefactos y procedencia.
- [`RESEARCH_STATUS.md`](RESEARCH_STATUS.md): estado factual consolidado sin porcentajes agregados.
- [`research/webkit-1302/`](research/webkit-1302/): rama documental de 13.02.
- [`webkit-kit/README.md`](webkit-kit/README.md): alcance específico del kit WebKit.

## Mantenimiento

Cada cambio importante debe conservar hashes, fechas, commits y límites de evidencia. Los resultados generados no deben presentarse como fuentes primarias. Las ramas especializadas pueden tener README propios: no son copias del estado global y deben describir únicamente su ámbito.
