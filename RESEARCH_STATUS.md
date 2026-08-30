# Estado de investigación — firmware-lab

**Última revisión documental:** 30 de agosto de 2026
**Estado global:** investigación abierta; no es un jailbreak terminado ni una herramienta lista para usuarios finales.
**Método por defecto:** análisis estático, hashes, manifests, tests host-side y correlación de fuentes. La ejecución en hardware se marca por separado.

## Estado por firmware

| Firmware | Estado verificable | Bloqueador principal |
|---|---|---|
| **13.02** | Vue After Free/userland `CORROBORATED`; Netctrl/ucred `UNVERIFIED_13_02`; offsets SLOPOS `SOURCE_ONLY/CORROBORATED_SOURCE_ONLY`; kernel R/W `MISSING`; jailbreak completo `NOT_REPRODUCIBLE`. | Kernel exploit específico y demostración de R/W. |
| **13.52** | `libkernel_sys` y chunks `DIRECT_BYTES` con hashes reproducibles; PUP/SLB2 `VERIFIED_METADATA`; WebKit retail `MISSING`; candidatos kernel `UNVERIFIED`; jailbreak completo `NOT_REPRODUCIBLE`. | Bytes WebKit/kernel retail y cadena kernel reproducible. |

## Componentes verificables

| Componente | Resultado |
|---|---|
| Integridad del blob `libkernel_sys_13.52.bin` | La concatenación de `lk_dump1.bin`, `lk_dump2.bin` y `lk_dump3.bin` coincide byte a byte con el blob documentado. |
| Análisis estático libkernel | Reproducible con `tools/run_static_audit.sh`, `objdump` y manifests locales. |
| PUP 13.50/13.52 | Tamaños, hashes y estructura SLB2 verificados; entradas internas permanecen opacas. |
| WebKit retail 13.52 | No presente en el corpus como módulo verificable. |
| WebKit/Vue userland 13.02 | Alcance público documentado hasta 13.02; no implica kernel R/W. |
| Offsets 13.02 | `sysent=0x1102B70`, `prison0=0x111FA18` y otros valores aparecen en tablas; no son validación de bytes retail. |
| SDK y submódulos | Fijados por commit; requieren `git submodule update --init --recursive`. |
| Tests host-side | La suite disponible pasa con skips documentados cuando faltan dependencias o clones externos. |
| Build payload | Requiere toolchain x86-64 y inputs con procedencia; la compilación host no demuestra compatibilidad con hardware PS4. |

## Qué significa cada resultado

Un hash de archivo confirma integridad del archivo, no su identidad de firmware. Un parser SLB2 confirma la estructura del contenedor, no el contenido de módulos cifrados. Un análisis de código upstream demuestra una relación estructural o histórica, no presencia en la build retail. Un test host-side demuestra el contrato probado, no ejecución en consola. Las tablas de offsets deben conservarse como `SOURCE_ONLY` hasta que exista una fuente independiente o bytes del firmware objetivo.

## Próximos bloqueadores

Para 13.02, la prioridad es encontrar o validar una vulnerabilidad de kernel que proporcione R/W y asociarla con un artefacto de la misma build. A continuación deben validarse `sysent`, `prison0`, `rootvnode`, `kernel_map`, `pmap_protect` y los offsets de parcheo sobre bytes reales. Netctrl/ucred es el candidato público prioritario; Lapse/semctl permanece fuera de alcance demostrado para 13.02.

Para 13.52, la prioridad es obtener módulos WebKit retail o un artefacto legítimo equivalente, además de una prueba de kernel R/W. El blob libkernel y el PUP verificado no deben presentarse como sustitutos de esos artefactos.

## Documentación canónica

- [`README.md`](README.md): resumen general y estado verificable.
- [`docs/EVIDENCE_POLICY.md`](docs/EVIDENCE_POLICY.md): vocabulario y reglas de clasificación.
- [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md): organización y política de archivos.
- [`ARTIFACTS.md`](ARTIFACTS.md): inventario y procedencia.
- [`research/webkit-1302/`](research/webkit-1302/): línea específica de 13.02.
- [`webkit-kit/README.md`](webkit-kit/README.md): alcance del kit WebKit.

## Reproducibilidad

```bash
git submodule update --init --recursive
bash tools/check_env.sh
python3 -m pytest -q tests webkit-kit/tests
python3 tools/check_source_quality.py
bash tools/run_static_audit.sh
```

Los comandos anteriores validan el entorno y análisis disponibles. No ejecutan payloads ni prueban un jailbreak.
