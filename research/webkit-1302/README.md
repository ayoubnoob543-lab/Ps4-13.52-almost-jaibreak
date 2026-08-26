# PS4 13.02 — WebKit y disco/artefactos

Esta rama (`research/webkit-disk-1302`) concentra la investigación específica de **PS4 firmware 13.02**, separándola del foco principal del laboratorio en 13.52. Su objetivo es ordenar la evidencia y preparar un pipeline reproducible para WebKit, BD-J/disco, userland y la obtención/validación de artefactos del kernel.

> Regla central: una tabla de offsets, un README de un repositorio o un payload para otra versión no se convierten automáticamente en evidencia verificada para 13.02.

## Estado resumido

| Componente | Estado actual | Interpretación |
|---|---|---|
| WebKit CVE-2017-7117 / Vue After Free | `VERIFIED/CORROBORATED` para userland | El alcance público declara userland 5.05–13.02. |
| Ejecución userland 13.02 | `CORROBORATED` | Primera etapa de la cadena; no implica privilegios de kernel. |
| Netctrl/ucred triple-free | `UNVERIFIED_13_02` | El árbol público llega funcionalmente hasta 13.00; 13.02 requiere demostración independiente. |
| Lapse/semctl | `UNVERIFIED_13_02` | El alcance público localizado no llega a 13.02. |
| SLOPOS offsets 13.02 | `CORROBORATED_SOURCE_ONLY` | Existe `research/results/slopos/1302.h`; no hay segunda fuente completamente independiente para toda la tabla. |
| `sysent` 13.02 | `CORROBORATED_SOURCE_ONLY` | `0x1102B70` aparece en SLOPOS y en `kpayload/source/offsets/1302.c`. |
| `prison0` 13.02 | `CORROBORATED_SOURCE_ONLY` | SLOPOS documenta `0x111FA18`. |
| Offsets mmap RWX | `DOCUMENTED_UNVERIFIED` | Se documentan `0x1fa78a` y `0x1fa78d`; la procedencia deriva de fuentes relacionadas. |
| Kernel retail 13.02 | `MISSING_DIRECT_BYTES` | No hay dump público verificado usado para validar la tabla completa. |
| Kernel R/W 13.02 | `MISSING` | Es el cuello de botella principal. |
| Jailbreak completo 13.02 | `NOT_REPRODUCIBLE` | No se ha demostrado el salto userland → kernel R/W. |

## Cadena de trabajo

```text
WebKit / Vue After Free
        ↓
Ejecución userland 13.02
        ↓
Candidato kernel (Netctrl/ucred, Lapse u otro)
        ↓
Kernel R/W
        ↓
Validación de offsets 13.02
        ↓
Parcheo / kexec
        ↓
Jailbreak reproducible
```

La primera transición está cubierta de forma razonable. La investigación debe detenerse explícitamente en la transición a kernel R/W hasta que exista evidencia de 13.02 específica, reproducible y separada de la evidencia de 13.00 o 13.52.

## Estructura de esta rama

| Archivo | Propósito |
|---|---|
| `README.md` | Alcance, taxonomía y estado ejecutivo. |
| `evidence-matrix.md` | Matriz detallada por pieza, fuente, confianza y prueba faltante. |
| `disk-artifacts.md` | Plan para BD-J/disco, PUP, system image y artefactos de WebKit. |
| `source-notes.md` | Registro de fuentes públicas consultadas y sus límites. |
| `public-source-notes.md` | Nota reproducible de la consulta directa a Vue After Free. |

## Fuentes internas principales

- `docs/remaining-gaps.md`, especialmente las secciones de Netctrl, offsets mmap y los diez offsets de kernel faltantes.
- `research/results/slopos/1302.h`, como tabla fuente que requiere corroboración.
- `kpayload/source/offsets/1302.c` y `kpayload/include/offsets/1302.h`, como integración local de offsets.
- `webkit-kit/runtime/` y `webkit-kit/docs/`, como corpus de análisis WebKit/BD-J y documentación histórica.
- `analysis/` y `research/`, como manifests, hashes, resultados y logs.

## Próximo criterio de éxito

La rama no se considerará completa por acumular más tablas. El siguiente hito verificable es obtener un artefacto 13.02 con procedencia clara —por ejemplo, bytes de kernel retail, un dump de consola o un log de ejecución firmado por hash— y usarlo para validar primero los offsets mmap, después los parches restantes y finalmente una primitiva de kernel R/W. Hasta entonces, las conclusiones deben permanecer en `UNVERIFIED_13_02` o `SOURCE_ONLY`.
