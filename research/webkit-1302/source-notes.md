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

## Netctrl/HENloader — comprobación pública directa 26 de agosto de 2026

La página de [RiyonAbib07/ps-vue-jb-2.5](https://github.com/RiyonAbib07/ps-vue-jb-2.5) declara explícitamente un alcance de jailbreak 7.00–13.00. Su README separa `vue-after-free` userland 5.05–13.04, Lapse 1.01–12.02 y Netctrl 1.01–13.00; la FAQ indica que en 13.02 o superior sólo funciona userland. El repositorio tiene 226 commits, una rama, ningún tag y su commit visible `1e8e2ad` es una corrección de estabilidad fechada 11 de marzo de 2026. La metadata consultada indica que no es fork, tiene dos forks y fue actualizado en GitHub el 17 de agosto de 2026.

El archivo público `src/download0/kernel.ts` contiene offsets mmap etiquetados para 13.02 (`0x1fa78a`, `0x1fa78d`) y una tabla que agrupa 12.50/12.52/13.00 para la parte Netctrl. Esto demuestra que el código contiene una entrada documental para 13.02, pero no demuestra una primitive kernel R/W en 13.02: la propia tabla de soporte funcional termina en 13.00.

La página de [iaceene/HENloader_Source](https://github.com/iaceene/HENloader_Source), commit `a42fef8` del 25 de noviembre de 2025, declara soporte de HENloader LP de 9.00 a 12.52 dependiendo de Lapse/Poopsploit. No aporta soporte 13.02, PoC 13.02 ni evidencia de hardware 13.02. Se clasifica `HISTORICAL_ONLY` para 13.02 y `SOURCE_ONLY` respecto a su propio alcance.

Conclusión: Netctrl sigue siendo el candidato público más cercano, con máximo funcional publicado 13.00; 13.02 sólo aparece como userland/offset mmap documental, no como kernel R/W probado.

## PSDevWiki — comprobación directa 26 de agosto de 2026

La página [PS4 Developer wiki — Vulnerabilities](https://www.psdevwiki.com/ps4/Vulnerabilities) separa explícitamente los exploits usermode de los kernel exploits. Enumera `BD-JB-13.00` como exploit de usermode para PS4 13.00–13.02 y también lista vectores BD-JB con estados `untested`; esa entrada no es un kernel exploit ni proporciona por sí sola R/W.

La misma página identifica mast1c0re/Luac0re como vías de usermode/JIT y describe cadenas con exploits kernel sólo para rangos históricos o diferentes. La página no aporta una demostración pública de una primitive kernel R/W específica para 13.02.

La página [PS4 Developer wiki — Bugs](https://www.psdevwiki.com/ps4/Bugs) también distingue usermode, BD-J y kernel. Sus entradas de BD-JB 13.00–13.02 describen escape de sandbox; no deben contarse como kernel exploit. La existencia de una vulnerabilidad de usermode o de un escape de sandbox no prueba lectura/escritura arbitraria del kernel.

Clasificación: BD-JB 13.00–13.02 = `CORROBORATED` como usermode/entrada; kernel R/W 13.02 desde estas páginas = `UNVERIFIED_13_02`.

## PSDevWiki kernel candidates — consulta directa 26 de agosto de 2026

La sección Kernel de [PSDevWiki Bugs](https://www.psdevwiki.com/ps4/Bugs) se marca `Untested` y enumera los siguientes candidatos cercanos a 13.02:

| Candidato | Alcance que muestra la página | PoC/estado PS4 | Primitive descrita | Clasificación 13.02 |
|---|---|---|---|---|
| CVE-2026-58087, carrera TOCTOU en `semctl(2)` | `?<=13.52?` | Sin implementación de exploit en la página; la entrada dice que PS4/PS5 pueden estar afectadas | OOB read/write de heap con posible elevación | `UNVERIFIED_13_02` |
| CVE-2026-49412, UAF `IPV6_MSFILTER` | `?<=13.50?` | Sin implementación PS4; “maybe since PS4 13.52” | UAF por carrera en filtro multicast, potencial elevación | `UNVERIFIED_13_02` |
| CVE-2026-45251, UAF por file descriptors | `?<=13.50?` | PoC citado sólo para FreeBSD 15; PS4/PS5 “maybe not affected” | Escritura arbitraria de puntero de kernel mediante reclaim SCM_RIGHTS | `UNVERIFIED_13_02` |
| CVE-2026-45250, overflow de stack `setcred(2)` | `?<=13.50?` | Sin implementación PS4; la página indica que la vulnerabilidad upstream afecta FreeBSD 14.3–15, no necesariamente FreeBSD 9 | Overflow de stack con posible ejecución kernel | `UNVERIFIED_13_02` |
| Overflow UFS/FFS al montar | `?<=13.04?` | Sin PoC; requiere partición FFS malformada y posiblemente otra vulnerabilidad para cifrarla | Overflow durante mount/reload; potencial impacto kernel | `UNVERIFIED_13_02` |
| CVE-2026-3038, routing sockets | `?<=13.04?` | PoC citado para panic PS4 13.52; la página dice que probablemente PS4 basado en FreeBSD 9 no es vulnerable al bug upstream | Stack overflow con canario; sólo DoS demostrado, escalada hipotética | `UNVERIFIED_13_02` |
| CVE-2026-5398, UAF `TIOCNOTTY` | `?<=13.02?` | PoC sólo para FreeBSD 15; PS4/PS5 “maybe not affected” | UAF de puntero de sesión, posible elevación | `UNVERIFIED_13_02` |
| CVE-2025-14558, ND6/rtsold | `?<=13.02?` | PoCs de FreeBSD/Linux; la página advierte que PS4/PS5 pueden no estar afectados | RCE remoto en rtsold/resolvconf, no kernel R/W PS4 demostrado | `UNVERIFIED_13_02` |
| `aio_multi_delete` | `5.00-?11.52?` | Sin PoC; parche observado en 12.00 según la página | Bug de locking en kernel, impacto no demostrado | `HISTORICAL_ONLY` |

La página distingue explícitamente `Exploit Implementation` de la descripción del bug y deja vacíos varios campos. Por tanto, que una cabecera diga `?<=13.02?` o `?<=13.50?` no equivale a soporte PS4: en todos los casos anteriores falta una PoC PS4 13.02, log de hardware y demostración de R/W. La única excepción parcial es la entrada de routing sockets, que menciona un PoC de panic para PS4 13.52, pero no demuestra R/W ni aplicabilidad a 13.02.

## PSFree/Lapse — comprobación directa 26 de agosto de 2026

La fuente [Feyzee61/psfree_lapse](https://github.com/Feyzee61/psfree_lapse) se describe como PSFree WebKit + Lapse Kernel Exploit para PS4 **7.00–9.60**. La página visible indica que integra shellcodes de parche kernel y AIO patch sets para 7.00–9.60; muestra 47 commits, tres tags, 19 forks y commit visible `ba736c0` de actualización del README. No hay declaración ni PoC para 13.02. Se clasifica `HISTORICAL_ONLY` para 13.02.

El nombre del repositorio y su presencia en muchos forks no constituyen una fuente independiente para 13.02; su propio README fija el límite en 9.60.

## ConsoleMods y Reddit — estado comunitario 26 de agosto de 2026

La tabla [ConsoleMods PS4 Exploit Chart](https://consolemods.org/wiki/PS4:Exploit_Chart) agrupa `13.02–13.04` y declara que no existe kernel exploit público para el firmware reciente/latest; la acción recomendada es conservar o vender la consola. La página es una tabla secundaria, no una PoC ni un log de hardware, por lo que se clasifica `CORROBORATED` sólo para el estado público, no como prueba de ausencia absoluta.

La discusión de [Reddit r/ps4homebrew](https://www.reddit.com/r/ps4homebrew/comments/1omgsul/new_kernel_exploit_up_to_1300_for_ps4_and_1200/) enlaza un gist de TheOfficialFloW y repite que el nuevo kernel exploit llega a PS4 13.00, no 13.02. Los comentarios indican que requiere BD-JB/WebKit/Mast1c0re y que no era utilizable en 12.50 en el momento de la discusión; también aparece un comentario de un usuario con 13.02 “hoping to release it someday”, que es una expectativa comunitaria, no una demostración. Se clasifica `CORROBORATED` para la frontera pública 13.00 y `UNVERIFIED_13_02` para cualquier extrapolación.
