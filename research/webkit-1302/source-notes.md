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

## Comparación directa de `riyon-kernel.ts` — 26 de agosto de 2026

El archivo público `src/download0/kernel.ts` de `RiyonAbib07/ps-vue-jb-2.5` separa una tabla `offset_ps4_12_00` que agrupa 12.02 de otra `offset_ps4_12_50` que agrupa 12.52 y 13.00. La tabla 12.50/12.52/13.00 conserva `PRISON0`, `ROOTVNODE`, `SYSENT_661`, `JMP_RSI_GADGET` y `KL_LOCK`, pero deja `EVF_OFFSET` y `TARGET_ID_OFFSET` en cero y los comenta como faltantes/no necesarios en Netctrl. No existe una entrada `offset_ps4_13_02` para la cadena Netctrl.

El mismo archivo contiene una tabla separada `kpatch_mmap_offsets` que sí incluye una entrada 13.02. El código posterior verifica bytes de parches mmap y prueba una asignación RWX, pero esas comprobaciones pertenecen a la fase de parcheo y no demuestran que Netctrl/ucred haya producido R/W en 13.02. Esta diferencia es evidencia directa de que 13.02 aparece en la tabla de mmap, pero no en la tabla de offsets de la primitive Netctrl completa.

## Afirmaciones de parche 13.02 — comprobación adicional 26 de agosto de 2026

El artículo de [XDG Mods sobre el release de TheFlow](https://xdgmods.com/news/theflow-kernel-exploit-ps4-ps5) afirma que el exploit afecta hasta PS4 13.00 y que Sony lo parcheó en 13.02. El artículo no adjunta diff de kernel, advisory de Sony, hashes de builds, PoC 13.02 fallida ni log de hardware; por ello la afirmación de parche se clasifica `SOURCE_ONLY`, no `VERIFIED`.

La discusión de [Reddit sobre 13.00/13.02/13.04](https://www.reddit.com/r/ps4piracy/comments/1qv6ohi/clearing_up_ps4_jailbreak_confusion_current/) repite “Poopsploit patched” para 13.02 y “userland only”, pero es una discusión comunitaria sin prueba técnica primaria. Se clasifica `CORROBORATED` sólo como consenso público de la frontera 13.00/13.02 y `UNVERIFIED_13_02` para la causalidad exacta del parche.

Conclusión de procedencia: existe evidencia pública repetida de que el soporte publicado termina en 13.00 y una afirmación secundaria de que Sony parcheó 13.02; no existe en el corpus revisado evidencia directa que demuestre qué función o condición de Netctrl cambió entre 13.00 y 13.02.

## SLOPOS y ps4-linux-loader — comparación de procedencia 13.00/13.02

`SLOPOS-offsets` declara en `README.md` y `CREDITS.md` que sus offsets kexec se copian de `ps4-linux/ps4-linux-loader` (`magic.h` y `fw_offsets.h`), y atribuye conjuntamente `12.50 / 13.00 / 13.02 / 13.50 / 13.52` a ArabPixel. El historial de SLOPOS muestra que `ps4/1300.h` y `ps4/1302.h` fueron introducidos juntos en `42273e2180ca` (2026-08-07).

En `ps4-linux-loader`, el header 13.02 aparece en `3d7a5456b75c` (2025-12-31). Las releases `v21`, `v21.5` y `v24b.1` anuncian payloads 13.02, pero escriben `13.02(?)`; el commit posterior `217e272eb099` (2026-05-11) añade 13.04/13.50 y mantiene 13.02 como payload de kexec/Linux. No se encontró en ese repositorio la implementación Netctrl/ucred ni una prueba de que los payloads de Linux demuestren la primitive Netctrl en 13.02.

La comparación local de `1300.h` y `1302.h` tiene SHA-256 `a95c48e23743e193f7d1b543dc35a817d68bb71f129476de03c3deff38b1e94b` y `34a206ffa48a406f6d15879b40e941de5e9d0db094bfd2d0932a6cf58961066a`. Muchos offsets 13.02 son exactamente 13.00 + 0x10, mientras otros son idénticos. Sin bytes de kernel, esto es una diferencia documentada de tablas, no una validación binaria ni una prueba de cambio de función.

## Corpus ampliado de PSDevWiki — 26 de agosto de 2026

Fuente principal: [PSDevWiki Vulnerabilities](https://www.psdevwiki.com/ps4/Vulnerabilities) y su sección [PSDevWiki Bugs](https://www.psdevwiki.com/ps4/Bugs).

Candidatos documentados por la wiki que deben mantenerse separados por estado:

- `CVE-2026-58087` semctl TOCTOU: la wiki lo etiqueta `?<=13.52?`; describe OOB read/write por cambio concurrente del tamaño de un conjunto de semáforos entre desbloqueo y realloc. No hay implementación PS4 ni evidencia de hardware; la propia entrada remite a FreeBSD 15 y lo deja sin PoC. `HYPOTHESIS`/`UNVERIFIED_13_02`.
- `CVE-2026-49412` IPV6_MSFILTER UAF: la wiki lo etiqueta `?<=13.50?`; UAF en `in6p_set_source_filter()` tras soltar el lock durante copia de filtros. PoC pública es FreeBSD 14/15; no hay PS4. `HYPOTHESIS`/`UNVERIFIED_13_02`.
- `CVE-2026-45251` procdesc/poll UAF: la wiki lo etiqueta `?<=13.50?`; describe posible arbitrary kernel-pointer write mediante reclaim SCM_RIGHTS, pero la PoC es FreeBSD 15 y la entrada advierte que PS4 puede no estar afectada. `HYPOTHESIS`/`UNVERIFIED_13_02`.
- `CVE-2026-45250` setcred stack overflow: la propia descripción limita el bug a FreeBSD 14.3–15.0 porque el campo problemático no existía antes; no es candidato Orbis 9.x. `DISPROVEN/PATCHED` para PS4 por incompatibilidad de base.
- UFS/FFS mount overflow (“Celsius”): la wiki describe overflow al calcular buffers auxiliares en mount/reload y requiere imagen FFS malformada; para PS4 exige resolver además PFS/HDD y la entrada declara parche desde 13.50. Se conserva como `SOURCE_ONLY`/`UNVERIFIED_13_02`, no como R/W probado.
- `CVE-2026-3038` routing sockets: la wiki explica que `rtsock_msg_buffer()` es una función de FreeBSD 13.5–15 y probablemente no existe en FreeBSD 9; como máximo sería un patrón para buscar bugs análogos antiguos. `DISPROVEN/PATCHED` para trasladarlo literalmente a Orbis; hipótesis separada para una variante vieja.
- `CVE-2026-5398` TIOCNOTTY: UAF por back-pointer de sesión/terminal no limpiado; PoC FreeBSD 15, no PS4. La wiki lo etiqueta `?<=13.02?` pero también dice que PS4/PS5 pueden no estar afectadas. `HYPOTHESIS`/`UNVERIFIED_13_02`.
- `CVE-2025-14558` ND6/rtsold: inyección de comandos mediante Router Advertisements y `resolvconf`, no kernel R/W directo; la entrada relaciona el código introductorio con FreeBSD 9.0, pero requiere rtsold/rtsol y aceptación de RA. No hay PoC PS4 ni prueba de que la ruta exista en Orbis. `SOURCE_ONLY`/`UNVERIFIED_13_02`.
- `aio_multi_delete()`: bug no identificado, con código parcheado observado en PS4 12.50; sin PoC y probablemente corregido alrededor de 12.00. No llega a 13.02 como candidato. `SOURCE_ONLY`/`DISPROVEN-PATCHED` para 13.02.
- `CVE-2022-23090` aio_aqueue/lio_listio: fuga de referencias de credencial que puede acabar en UAF; PoC FreeBSD 12/13, pero la wiki señala que AIO fue ampliado después de FreeBSD 9 y probablemente no existe igual en Orbis. `DISPROVEN/PATCHED` como traslado directo; `HYPOTHESIS` sólo para una variante histórica.
- `CVE-2022-23088` net80211 Mesh ID: heap overflow remoto en beacon durante escaneo; PoC FreeBSD 13, posible PS4 9.x según la wiki, pero no 13.02 y no hay prueba Orbis. `DISPROVEN/PATCHED` para 13.02.
- Routing socket wrong dst/netmask: bug de validación/KPI en FreeBSD 13.0, corregido en 2021; la wiki lo limita tentativamente a PS4 <=9.x y no ofrece PoC PS4. `DISPROVEN/PATCHED` para 13.02.
- `CVE-2013-5209` SCTP stack disclosure y `CVE-2013-3077` IP_MSFILTER integer overflow: la wiki los sitúa alrededor de PS4 1.01; no son candidatos 13.02. `DISPROVEN/PATCHED`.
- exFAThax `CVE-2022-3349`: heap overflow en `UVFAT_readupcasetable`; funcional PS4 9.00 y corregido en 9.03. La lógica de 9.03–13.50 contiene una comprobación de overflow que la wiki identifica como fix. `VERIFIED` histórico, `DISPROVEN/PATCHED` para 13.02.
- `CVE-2020-9892` IP6_EXTHDR_CHECK double-free: PS4 7.50–7.55, parcheado en 8.00; `DISPROVEN/PATCHED` para 13.02.
- `CVE-2020-7457` IPV6_2292PKTOPTIONS UAF: arbitrary kernel R/W en PS4 hasta 7.02, parcheado en 7.50 según la wiki; `VERIFIED` histórico, `DISPROVEN/PATCHED` para 13.02.
- BPF race/double-free: PS4 <=5.07 o <=4.55 según variante, parcheado 5.50/4.70; `DISPROVEN/PATCHED` para 13.02.
- `CVE-2018-17155` sys_getcontext leak: hasta ~6.00, parcheado entre 6.00 y 6.20; sólo leak/kASLR, no R/W directo. `DISPROVEN/PATCHED` para 13.02.
- NamedObj type confusion: PS4 1.01–4.05, parcheado 4.06; `VERIFIED` histórico, `DISPROVEN/PATCHED` para 13.02.
- `CVE-2016-1885` amd64_set_ldt: limitado a versiones antiguas y posiblemente no aplicable por falta de compatibilidad IA-32; `DISPROVEN/PATCHED` para 13.02.

La página pública es colaborativa y varias entradas son tentativas; su contenido se usa como fuente secundaria, nunca como prueba de que Orbis 13.02 sea vulnerable.

## Reddit sobre Celsius — revisión 26 de agosto de 2026

Fuente: https://www.reddit.com/r/PS5_Jailbreak/comments/1v180lp/ps4ps5_jailbreak_news_new_celsius_kernel_bug_27k/

La discusión y el post revisado son material secundario/comunitario. El contenido visible habla de avances generales y mantiene el límite público de jailbreak de PS4 en 13.00; no aporta el repositorio original de Celsius, una PoC, un log de PS4 13.02/13.04, un diff de kernel ni una explicación independiente del supuesto parche 13.50. Clasificación para Celsius en 13.02: `SOURCE_ONLY` como rumor/seguimiento de escena, no `VERIFIED` ni `CORROBORATED`.

La búsqueda pública de GitHub tampoco localizó un repositorio o commit bajo la cuenta `bollars` que contenga Celsius/ffs_mount: la cuenta pública tiene un único repositorio, `bollars/ddoslib`, no relacionado. El repositorio `adri22235/ps4-suid-scanner` es el principal artefacto público que atribuye Celsius a bollars, con commits entre 2026-07-18 y 2026-08-09; por tanto, documenta la atribución pero no constituye una fuente primaria independiente del descubrimiento.

## Fuentes secundarias adicionales sobre Celsius — 26 de agosto de 2026

[GameGaz, 19 de julio de 2026](https://gamegaz.com/2026071945823/) atribuye a bollars el hallazgo de Celsius en `ffs_mount`, afirma PS4 hasta 13.04 y PS5 hasta 12.70, y dice que PS4 13.50/PS5 13.00 ya lo corrigen. También afirma requisito de HDD USB 3.0 de 250 GB o más y una entrada userland Vue/BD-J, pero declara expresamente que aún no estaba en etapa práctica ni podía llamarse kernel exploit confirmado.

[Publicación de GAMERZ 56K en YouTube](https://www.youtube.com/post/UgkxE2BPYs9Rf7TJgKq8GqnZlTh-kOpDU15F) repite las mismas afirmaciones: `ffs_mount`, integer overflow/heap overflow, PS4 hasta 13.04 incluyendo 13.02, patch 13.50+, disco USB 3.0 recomendado de 320/500 GB y ausencia de garantía de estabilidad. No aporta código, commit, log de hardware ni fuente primaria independiente. Clasificación: `SOURCE_ONLY`.

[Wikova, artículo PlayStation 4 Jailbreak](https://wikova.com/wiki/DQm4J1HU) resume Celsius como descubierto en julio de 2026 por bollars, hasta PS4 13.04/PS5 12.70, con requisito de HDD USB 3.0 de 250 GB o más y parcheado en 13.50/13.00. Es una fuente terciaria conectada a GameGaz y no una corroboración independiente. También mantiene que Poopsploit/Netctrl llega a PS4 13.00, por lo que no sustituye la evidencia primaria de Netctrl.

La búsqueda del perfil público de bollars en GitHub encontró sólo `bollars/ddoslib`, sin Celsius, PoC ni código FFS. Esto deja la atribución original sin artefacto primario público localizable; `adri22235/ps4-suid-scanner` y las noticias citadas son fuentes secundarias o derivadas.

## X / Silent_Logic sobre Celsius — revisión 26 de agosto de 2026

Fuente: https://x.com/Slient_Logic/status/2082855345844797681, publicada el 30 de julio de 2026.

La publicación dice “Big Rumor” y atribuye a fuentes internas que el jailbreak Celsius de PS4 13.02 podría ser inservible, con tasa de éxito muy baja y requisitos difíciles; el 31 de julio añade que el rumor estaría “confirmado” y que sería inútil. La página no aporta código, PoC, log, hash, identidad verificable de las fuentes internas ni enlace a evidencia técnica. Clasificación: `SOURCE_ONLY` como rumor comunitario; no es evidencia de que el bug esté parcheado ni de que sobreviva.

## Primera difusión pública localizada: Dr.Yenyen/X

Fuente: https://x.com/calmboy2019/status/2078549759460094065. Fecha visible: 18 de julio de 2026, 18:37.

Texto: “Here you go. You'll still have to be patient but this is what you might get. It's named ‘Celsius’ Posting it as of now so that you guys don't go crazy. Just wait and see how usable it is if at all. Up to 13.04 PS4 and 12.70 PS5.”

La publicación contiene tres imágenes y no contiene código, PoC, commit, hash, log de hardware ni explicación técnica del alcance. En la imagen se atribuye el descubrimiento a bollars y se menciona `ffs_mount`, integer overflow y heap overflow; la respuesta de Dr.Yenyen vuelve a decir “13.04 PS4” “in theory”. Clasificación: `SOURCE_ONLY` para la atribución y el rango; no es prueba de funcionamiento.

## ConsoleMods Exploit Chart — revisión 26 de agosto de 2026

Fuente: https://consolemods.org/wiki/PS4:Exploit_Chart

La tabla muestra para firmware 13.02–13.04: “No public kernel exploit exists for the recent/latest firmware” y explica que no hay exploits públicos posteriores a 13.00. No menciona Celsius como exploit funcional. Clasificación: `CORROBORATED` para el estado público de ausencia de kernel exploit reproducible; no prueba que Celsius no exista ni que esté parcheado.

## Pharaoh2k — revisión directa del perfil público

Fuente: https://github.com/Pharaoh2k. El perfil muestra 27 repositorios públicos y repositorios fijados como `PlayStation-Payload-Center`, `ps5debug-NG`, `ScriptSK/Reaper-Software-Suite` y un fork de FileZilla. La búsqueda local/GitHub no localizó en los repositorios visibles una tabla `1302.h`/`1304.h`, código FFS, kernel Orbis ni el artefacto original de Celsius. La atribución de `adri22235/ps4-suid-scanner` a una “Pharaoh2k offset table” queda por tanto sin artefacto primario identificado: `SOURCE_ONLY`.
