# Matriz de evidencia PS4 13.02

## Taxonomía

| Etiqueta | Significado |
|---|---|
| `VERIFIED` | Validado directamente sobre bytes o ejecución reproducible del firmware objetivo. |
| `CORROBORATED` | Coincide entre fuentes independientes o una fuente y una comprobación local, pero aún falta validación directa completa. |
| `SOURCE_ONLY` | Procede de una tabla, README, commit o código público sin validación independiente del firmware objetivo. |
| `HISTORICAL_ONLY` | Válido para otra versión o para una cadena histórica; no se debe trasladar a 13.02. |
| `UNVERIFIED_13_02` | Candidato plausible, pero sin prueba específica de 13.02. |
| `MISSING` | Pieza necesaria que no está disponible en el corpus actual. |

## Matriz por componente

| Pieza | Evidencia localizada | Estado | Qué falta para subir de nivel |
|---|---|---|---|
| CVE-2017-7117 / Vue After Free | README público y árbol de `vue-after-free`; el userland se declara funcional de 5.05 a 13.02 | `CORROBORATED` | Log reproducible de ejecución sobre una consola 13.02 con hash de build y versión exacta. |
| Ejecución userland | Código, fixtures y documentación de Vue After Free | `CORROBORATED` | Separar con claridad la ejecución JavaScript de cualquier afirmación de jailbreak. |
| Netctrl/ucred triple-free | Código público y tablas que llegan hasta 13.00; commits recientes mejoran estabilidad | `UNVERIFIED_13_02` | PoC o log específico 13.02 que demuestre la primitiva y sus offsets/runtime assumptions. |
| Lapse/semctl | Cadena histórica para firmwares inferiores; el alcance público revisado no cubre 13.02 | `HISTORICAL_ONLY` / `UNVERIFIED_13_02` | Fuente específica 13.02 o descarte formal basado en un análisis de parche/diff. |
| Offsets mmap RWX | `docs/remaining-gaps.md` registra `0x1fa78a` y `0x1fa78d`; las fuentes comparten origen | `SOURCE_ONLY` | Segunda fuente verdaderamente independiente o validación sobre kernel 13.02. |
| `sysent` | `research/results/slopos/1302.h` y `kpayload/source/offsets/1302.c` usan `0x1102B70` | `CORROBORATED_SOURCE_ONLY` | Bytes del kernel 13.02 y comprobación de referencias/estructura. |
| `prison0` | SLOPOS `1302.h` usa `0x111FA18` | `SOURCE_ONLY` | Otra fuente independiente y validación en bytes/runtime. |
| `rootvnode` | SLOPOS `0x2136E90` | `SOURCE_ONLY` | Misma validación requerida; no inferir desde 13.52. |
| `kernel_map` | SLOPOS `0x22D1D50` | `SOURCE_ONLY` | Dump y comprobación de estructura. |
| `pmap_protect` | SLOPOS `0x58570`; otras ramas pueden usar valores distintos para otros firmwares | `SOURCE_ONLY` | Confirmar build exacta y función en kernel 13.02. |
| Parches restantes del shellcode | Los 10 offsets no mmap no están publicados para 13.02 según la búsqueda local | `MISSING` | Kernel retail 13.02 o dump equivalente para calcularlos. |
| Kernel retail | No localizado en el checkout ni en las fuentes públicas revisadas | `MISSING_DIRECT_BYTES` | Obtener imagen/dump con procedencia y hash verificables. |
| Kernel R/W | No hay exploit público demostrado específicamente para 13.02 en el corpus revisado | `MISSING` | Vulnerabilidad, PoC controlada y log reproducible de lectura/escritura. |
| Parcheo/kexec | El código de payload existe para otras versiones y hay infraestructura local | `HISTORICAL_ONLY` para 13.02 | Encadenar con R/W 13.02 y offsets validados. |
| Jailbreak completo | No reproducible con la evidencia actual | `NOT_REPRODUCIBLE` | Todas las piezas anteriores más una ejecución completa documentada. |

## Candidatos priorizados

### 1. Netctrl/ucred

Es el candidato con mayor prioridad porque la implementación pública cubre hasta 13.00 y el árbol contiene trabajo sobre estabilidad. Sin embargo, el salto de 13.00 a 13.02 no debe inferirse a partir de la mera presencia del código. La primera prueba debe ser una verificación aislada de la primitiva, sin encadenarla a parcheo persistente.

### 2. Lapse/semctl

Debe mantenerse como referencia histórica y como hipótesis de compatibilidad únicamente mientras aparezca una fuente que declare 13.02. El alcance público localizado no permite elevarlo a candidato confirmado.

### 3. Otros exploits de kernel

La ausencia de un artefacto público específico no demuestra que no exista una vulnerabilidad, sólo que no está verificada en el corpus. Las búsquedas deben registrar consulta, fecha, fuente, commit y razón de descarte para evitar repetir trabajo.

### 4. kqueue/knote UAF de 13.52

No es transferible automáticamente a 13.02. Debe conservarse en la rama 13.52 y sólo usarse aquí como metodología comparativa, nunca como evidencia de compatibilidad.

## Reglas de decisión

Una fuente se eleva a `VERIFIED` sólo si identifica firmware exacto, artefacto o ejecución reproducible, hash, método de adquisición y resultado observable. Un offset se considera validado sólo cuando se demuestra que pertenece a la misma build objetivo; la coincidencia entre tablas derivadas del mismo origen no cuenta como independencia.
