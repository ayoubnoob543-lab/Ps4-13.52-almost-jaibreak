# Registro de fuentes — PS4 13.02

## Fuentes locales

| Fuente | Aporte | Clasificación |
|---|---|---|
| `docs/remaining-gaps.md` | Resume Netctrl, offsets mmap, diez offsets faltantes y búsqueda de fuentes | `PRIMARY_LOCAL_RESEARCH` |
| `research/results/slopos/1302.h` | Tabla 13.02 con `sysent`, `prison0`, `rootvnode`, `kernel_map`, `pmap_protect` y otros valores | `SOURCE_ONLY` |
| `kpayload/source/offsets/1302.c` | Integración local de offsets para el payload | `IMPLEMENTATION_REFERENCE` |
| `webkit-kit/runtime/` | Notas de WebKit, BD-J, policy/classloading y límites entre firmwares | `RESEARCH_CORPUS` |
| `analysis/` y `research/` | Hashes, manifests, logs y resultados reproducibles | `EVIDENCE_SUPPORT` |

## Fuente pública consultada directamente

### Vue After Free Lite

URL: <https://github.com/owendswang/vue-after-free-lite>

El README visible declara dos cosas distintas: el userland funciona de 5.05 a 13.02, pero el repositorio ofrece jailbreak funcional sólo hasta 13.00. La FAQ afirma explícitamente que en 13.02 o superior sólo funciona el userland y que los archivos del repositorio no permiten jailbreak por encima de 13.00.

**Clasificación:** `DIRECT_PUBLIC_DOCUMENTATION` para el alcance declarado; `USERLAND_CORROBORATED` para 13.02; `NO_FULL_JAILBREAK_13_02` para la cadena completa.

El árbol también muestra código de NetCtrl, payloads, BD-J y `requirements.txt`. La presencia de código NetCtrl no prueba que la primitiva funcione en 13.02.

### Vuemony/vue-after-free

URL: <https://github.com/Vuemony/vue-after-free>

La fuente aparece como proyecto upstream de Vue After Free. Su documentación pública coincide con la frontera: userland extendido hasta 13.02, jailbreak funcional limitado a 13.00 en los archivos publicados.

**Clasificación:** `DIRECT_PUBLIC_DOCUMENTATION` para la declaración de alcance; no constituye evidencia de kernel R/W 13.02.

### SLOPOS / tabla 13.02

La tabla local `research/results/slopos/1302.h` atribuye valores a 13.02, incluidos `sysent=0x1102B70` y `prison0=0x111FA18`. Hasta encontrar una fuente independiente y bytes de la build, se conserva como `CORROBORATED_SOURCE_ONLY` o `SOURCE_ONLY`, no como `VERIFIED`.

## Fuentes que deben investigarse a continuación

| Fuente o línea | Pregunta |
|---|---|
| `RiyonAbib07/ps-vue-jb-2.5` | ¿Por qué se conocen offsets mmap 13.02 si no se publica el payload kernel completo? |
| Forks de `Vuemony/vue-after-free` | ¿Comparten origen o contienen una derivación independiente? |
| `alferdoss/SLOPOS-offsets` | ¿Existe commit, método o artefacto que documente la derivación de `1302.h`? |
| psdevwiki/consolemods/PS4 exploit charts | ¿Qué alcance público se declara hoy para 13.02 y qué es sólo histórico? |
| Releases y assets GitHub | ¿Hay kernel, system image, ISO/BD-J o manifests específicos 13.02 con hashes? |

## Regla anti-duplicación

Antes de considerar una segunda confirmación, comparar autoría, commit base, hashes y contenido. Forks sin modificaciones sustantivas y repositorios que copian la misma tabla cuentan como una única línea de procedencia.

## Consulta directa adicional — 26 de agosto de 2026

Se consultó mediante GitHub API el repositorio [RiyonAbib07/ps-vue-jb-2.5](https://github.com/RiyonAbib07/ps-vue-jb-2.5). Su metadata declara como descripción `PS4 PlayStation Vue Jailbreak exploit for firmware 7.00-13.00, with enhanced stability improvements for 12.50+ (Netctrl/Poopsploit)` y actualización `2026-08-17T02:51:54Z`. Esta descripción refuerza que el alcance de jailbreak publicado termina en 13.00, aunque el userland Vue cubra 13.02.

El archivo público `src/download0/kernel.ts` contiene `get_mmap_patch_offsets` con `13.02: [0x1fa78a, 0x1fa78d]`. El mismo archivo implementa rutas de lectura/escritura kernel y parcheo, pero la presencia del código y de los offsets no prueba que la primitiva kernel R/W o la cadena completa funcionen en 13.02. La clasificación se mantiene `DOCUMENTED_UNVERIFIED`.

Se recuperó directamente `research/results/slopos/1302.h` desde [alferdoss/SLOPOS-offsets](https://github.com/alferdoss/SLOPOS-offsets). La cabecera se identifica como `PS4 13.02 — kexec offsets: ArabPixel` y contiene, entre otros, `prison0=0x111FA18`, `rootvnode=0x2136E90`, `kernel_map=0x22D1D50`, `kernel_pmap_store=0x1B2C3A0`, `sysent=0x1102B70`, `pmap_extract=0x573D0` y `pmap_protect=0x58570`. También marca algunos campos como `TODO/help wanted`, lo que confirma que la tabla no es un conjunto completo de offsets verificados.

Clasificación actualizada: `SOURCE_ONLY` para la tabla completa; `CORROBORATED_SOURCE_ONLY` para los valores que coinciden con otra tabla local, sin elevarlos a `VERIFIED`.

## ConsoleMods Exploit Chart — consulta directa 26 de agosto de 2026

Fuente: [PS4 Exploit Chart](https://consolemods.org/wiki/PS4:Exploit_Chart).

La tabla pública agrupa `13.02–13.04` y declara que no existe un kernel exploit público para el firmware reciente/latest; recomienda esperar o conservar la consola. Esto coincide con el estado local: puede existir userland Vue para 13.02, pero no hay una cadena kernel pública verificada para 13.02.

Clasificación: `PUBLIC_STATUS_CORROBORATION`, no evidencia binaria ni demostración de hardware. La tabla es secundaria y debe conservarse como corroboración del estado público, no como prueba de ausencia absoluta de vulnerabilidades privadas.

## Vue After Free upstream — consulta directa 26 de agosto de 2026

Fuente: [Vuemony/vue-after-free](https://github.com/Vuemony/vue-after-free), commit visible `6e37d51` (1 de junio de 2026). El repositorio se describe como un exploit de ejecución de código userland para PlayStation 4. La documentación y la estructura del proyecto deben interpretarse como userland; no se encontró en la página una demostración directa de kernel R/W 13.02.

La fuente upstream refuerza la separación utilizada en esta rama: `Vue After Free` puede ser una vía de entrada userland, pero la compatibilidad del jailbreak completo depende de una cadena kernel posterior y de offsets de la build exacta.

Clasificación: `DIRECT_PUBLIC_DOCUMENTATION` para userland; `NOT_KERNEL_VERIFIED` para 13.02.

## Búsqueda adicional de kernel exploit — 26 de agosto de 2026

Las búsquedas públicas sobre `Netctrl/ucred`, `Lapse/semctl` y kernel exploit 13.02 devolvieron principalmente discusiones, vídeos y tablas de estado. La fuente secundaria más clara continúa siendo [ConsoleMods Exploit Chart](https://consolemods.org/wiki/PS4:Exploit_Chart), que agrupa 13.02–13.04 y declara que no existe kernel exploit público posterior a 13.00.

También apareció un repositorio de investigación [Feyzee61/psfree_lapse](https://github.com/Feyzee61/psfree_lapse), que debe auditarse por separado; el resultado de búsqueda no basta para atribuirle soporte 13.02. Los resultados de Reddit, YouTube y redes sociales se conservan como leads, no como evidencia técnica.

Conclusión de esta ronda: no se localizó una fuente pública primaria nueva que demuestre Netctrl/ucred o Lapse/semctl funcionando en PS4 13.02. Se mantiene `UNVERIFIED_13_02`.
