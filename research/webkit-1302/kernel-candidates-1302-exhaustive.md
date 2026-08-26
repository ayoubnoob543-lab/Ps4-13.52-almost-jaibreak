# Investigación exhaustiva de candidatos de kernel para PS4 FW 13.02

**Fecha de corte:** 26 de agosto de 2026. **Alcance:** análisis estático y documental de fuentes públicas y artefactos legítimamente disponibles. No se ejecutaron payloads, cadenas de corrupción ni pruebas contra hardware real.

## Criterio de clasificación

`VERIFIED` significa que existe una implementación o prueba reproducible para el firmware indicado. `CORROBORATED` significa que dos fuentes con cierta independencia coinciden en un hecho limitado, sin demostrar necesariamente R/W. `SOURCE_ONLY` identifica una afirmación de una fuente sin confirmación independiente. `HYPOTHESIS` identifica una extrapolación técnica razonable pero no demostrada en Orbis. `UNVERIFIED_13_02` significa que el candidato puede ser interesante, pero no existe prueba específica para 13.02. `DISPROVEN/PATCHED` significa que la evidencia disponible sitúa el candidato fuera de 13.02 o muestra que fue corregido antes de esa versión.

## Resumen ejecutivo

La evidencia pública no demuestra actualmente una ruta reproducible de userland a kernel R/W en PS4 FW 13.02. El candidato directamente más cercano sigue siendo **Netctrl/ucred**, cuyo código público llega hasta 13.00. El nuevo candidato con mayor interés documental es **Celsius/ffs_mount**, porque fuentes de la escena le atribuyen alcance hasta 13.04; sin embargo, el material público revisado no contiene una PoC PS4 13.02 independiente con R/W observable, y parte de la evidencia procede de un repositorio reciente con offsets derivados de otras tablas.

Los CVEs recientes de FreeBSD son valiosos como corpus de investigación, pero la mayoría están documentados únicamente en FreeBSD 13.5–15.0, no en FreeBSD 9.x. Su aplicabilidad a Orbis requiere demostrar que la función y el código vulnerable existían en la base de Sony, que el componente está expuesto desde el contexto disponible y que el comportamiento no fue alterado. Un CVE FreeBSD moderno no es automáticamente un candidato PS4.

## Candidatos con evidencia fuerte o cercana

| Candidato | Alcance publicado | Autor y fecha | Primitive | PoC PS4/hardware | Estado 13.02 |
|---|---|---|---|---|---|
| **Netctrl/ucred / Poopsploit** | PS4 7.00–13.00 en el árbol público de Riyon; Vue userland llega a 13.02 | TheOfficialFloW; código público y adaptaciones 2025 | Triple-free/corrupción de `ucred`, leak de `kqueue`, después `kread/kwrite` | Sí para PS4 hasta 13.00; no para 13.02 | **UNVERIFIED_13_02** |
| **Celsius / ffs_mount** | Reivindicado hasta PS4 13.04, parcheado según la escena en 13.50 | bollars, 18 jul. 2026 según repositorio `adri22235/ps4-suid-scanner` | Overflow de heap durante mount/reload UFS/FFS; R/W posterior sólo hipotético | El repositorio contiene análisis y artefactos 13.04; no hay prueba pública independiente de R/W en 13.02 | **HYPOTHESIS / UNVERIFIED_13_02** |
| **ExFAThax v2** | PS4 anterior a 13.52 según análisis de PSDevWiki; no hay demostración de cadena kernel para 13.02 | TheFloW y análisis posteriores; 2021–2026 | Integer/rounding overflow en `UVFAT_readupcasetable`, posible heap corruption | v1 implementado en PS4 9.00; v2 no tiene PoC PS4 pública validada en 13.02 | **HYPOTHESIS / UNVERIFIED_13_02** |
| **CVE-2026-3038 routing socket** | PSDevWiki especula hasta 13.04, pero la propia descripción dice que `rtsock_msg_buffer()` es de FreeBSD 13.5–15 y probablemente no existe en FreeBSD 9 | Adam Crosser/Praetorian, 24 feb. 2026 | Stack OOB, normalmente panic por canary; no R/W demostrado | Se menciona PoC de panic en PS4 13.52, no exploit R/W | **HYPOTHESIS / UNVERIFIED_13_02** |

Netctrl es el candidato con la mejor combinación de código PS4 histórico y primitive explícita. El repositorio primario de TheOfficialFloW describe NetControl y el árbol de Riyon integra la cadena con Vue, pero su tabla de kernels detiene la ruta Netctrl en 13.00. Las entradas 13.02 que aparecen en el mismo ecosistema son offsets auxiliares de mmap/RWX o tablas de kernel para otras etapas; no prueban que el triple-free, el leak y el reclaim continúen funcionando.

Celsius merece conservarse como candidato abierto, no como exploit confirmado. El análisis público atribuye el problema a `ffs_mountfs()`, donde valores del superbloque controlan cálculos de tamaño antes de una escritura sobre una región asignada. El mismo material exige una imagen FFS/UFS malformada, acceso de montaje y condiciones de almacenamiento que no están demostradas para el entorno de PS4 13.02. Además, convertir un overflow en kernel R/W exige una estrategia de heap grooming y un target overwrite; esa segunda parte no está demostrada públicamente en 13.02.

## Candidatos PS4 históricos confirmados, pero fuera de 13.02

| Candidato | Rango y fecha | Componentes/primitive | PoC y hardware | Parche/estado |
|---|---|---|---|---|
| **CVE-2020-7457 IPV6_2292PKTOPTIONS** | PS4 hasta 7.02; publicado 2020–2021 | UAF en `ip6_setpktopt`; corrupción de `ip6po_pktinfo`, arbitrary kernel R/W | PoC FreeBSD y adaptaciones PS4; evidencia de funcionamiento PS4 6.72–7.02 | Corregido en PS4 7.50; **DISPROVEN/PATCHED** para 13.02 |
| **CVE-2020-9892 IP6_EXTHDR_CHECK** | PS4 hasta 7.55 | Double-free/UAF de mbuf en loopback IPv6 | Implementaciones PS4 7.50–7.55 y PoC FreeBSD 9 | Corregido en 8.00; **DISPROVEN/PATCHED** |
| **BPF race/double-free** | PS4 hasta 5.07 o 4.55 según variante | Race en `SETWF`/`SETIF`, double-free o OOB write, ring0 | Writeups e implementaciones PS4 4.55/5.05 | Corregido en 4.70/5.50; **DISPROVEN/PATCHED** |
| **NamedObj type confusion** | PS4 1.01–4.05 | Confusión de tipo, arbitrary free, UAF y ejecución ring0 | Writeups de fail0verflow/Specter y exploit PS4 4.05 | Corregido en 4.06; **DISPROVEN/PATCHED** |
| **sys_dynlib_prepare_dlclose** | PS4 temprano, corregido alrededor de 2.00 | Integer overflow y OOB write en heap de `rtld`; camino Sony específico | Writeup técnico de CTurt; no se publicó weaponized exploit PS4 completo | Parcheado antes de 2.xx; **DISPROVEN/PATCHED** |
| **BadIRET** | PS4 1.76 | Control de retorno de interrupción, kernel code execution | CTurt confirmó vulnerabilidad en 1.76 | Corregido antes de versiones modernas; **DISPROVEN/PATCHED** |
| **CVE-2018-17155 `sys_getcontext`** | Hasta aproximadamente 6.00 | Information leak/kASLR defeat, no R/W directo | Referencias de PS4, sin primitive R/W independiente | Corregido entre 6.00 y 6.20; **DISPROVEN/PATCHED** |
| **`sys_thr_get_ucontext` leak** | Hasta 4.07 | Information leak, derrota de kASLR | Incluido en cadena PS4 4.05 | Corregido en 4.50; **DISPROVEN/PATCHED** |
| **CVE-2016-1885 `amd64_set_ldt`** | Versiones antiguas hasta 4.05 según PSDevWiki | Heap overflow en eliminación de LDT; posible OOB write | No hay prueba PS4 sólida; además puede faltar compatibilidad IA-32 | `set_ldt` fue eliminado; **DISPROVEN/PATCHED** |
| **CVE-2022-3349 exFAThax v1** | PS4 1.01–9.00 | Type confusion/heap overflow en `UVFAT_readupcasetable` | Implementación PS4 9.00 y evidencia de hardware de la cadena 9.00 | Fix de longitud desde 9.03; **DISPROVEN/PATCHED** como v1 para 13.02 |
| **CVE-2020-7456 `hib_get_item`** | Vulnerabilidad USB histórica; sin alcance 13.02 confirmado | OOB kernel heap access en ruta de hibernación/USB | Fuente de TheFloW y referencias públicas; no hay validación PS4 13.02 | Sin evidencia de supervivencia; **UNVERIFIED_13_02** |

## Candidatos recientes de FreeBSD potencialmente heredables

| Candidato | Versiones FreeBSD oficiales | Función y primitive | PoC | Relación con Orbis 9.x/13.02 | Estado |
|---|---|---|---|---|---|
| **CVE-2026-58087 semctl** | Advisory público limita productos a FreeBSD 14.4/15.0/15.1 antes de sus parches | Race de secuencia en `semctl(GETALL/SETALL)`; OOB read/write heap | No se encontró PoC PS4 | PSDevWiki localiza código potencial en FreeBSD 9.1, pero falta demostrar equivalencia de implementación y exposición | **HYPOTHESIS / UNVERIFIED_13_02** |
| **CVE-2026-49412 IPV6_MSFILTER** | FreeBSD 13.5/14.3/14.4/15 antes de patch | UAF en `in6p_set_source_filter()` por lock liberado durante copyin | PoC de Calif.io para FreeBSD moderno | Es necesario demostrar que la ruta y el locking antiguo existen en Orbis; no hay PS4 | **HYPOTHESIS / UNVERIFIED_13_02** |
| **CVE-2026-45251 procdesc/poll** | FreeBSD 14/15 en la referencia consultada | UAF de `pd_selinfo`, posible arbitrary kernel-pointer write mediante reclaim SCM_RIGHTS | PoC FreeBSD 15 | `procdesc` y su semántica pueden no existir en Orbis; sin prueba de presencia | **HYPOTHESIS / UNVERIFIED_13_02** |
| **CVE-2026-5398 TIOCNOTTY** | FreeBSD 13.5–15 según CVE/CNA | UAF por back-pointer de terminal/sesión no limpiado; posible elevación | PoC FreeBSD 15 | La wiki lo etiqueta tentativamente `?<=13.02?`, pero no demuestra que Orbis tenga la misma sesión/tty code path | **HYPOTHESIS / UNVERIFIED_13_02** |
| **CVE-2025-14558 ND6/rtsold** | FreeBSD moderno; relación de código introductorio con 9.0 | Inyección de comandos en `rtsold`/`resolvconf` por Router Advertisement; no es kernel R/W directo | PoCs FreeBSD/Metasploit; no PS4 | Requiere que Orbis use esa ruta de userland y acepte RA; no prueba kernel exploit | **SOURCE_ONLY / UNVERIFIED_13_02** |
| **CVE-2022-23090 aio_aqueue** | FreeBSD 12.3/13.0 | Credential reference leak, eventual UAF | PoC FreeBSD 12/13 | La propia PSDevWiki señala que AIO fue ampliado después y probablemente no coincide con FreeBSD 9.1 | **DISPROVEN/PATCHED** para traslado directo; hipótesis histórica separada |
| **CVE-2022-23088 net80211 Mesh ID** | FreeBSD 13 | Heap overflow remoto durante escaneo Wi-Fi | PoC FreeBSD 13 | Posible PS4 9.x según wiki, sin PS4 13.02 ni prueba Orbis | **UNVERIFIED_13_02** |
| **CVE-2020-7460 `freebsd32_copyin_control`** | FreeBSD kernels desde 2014 en la ruta 32-bit; corregido 2020 | TOCTOU en 32-bit `sendmsg`, heap overflow de mbuf, después code exec | PoC ZDI para FreeBSD, fiabilidad declarada 90% | PS4 amd64/Orbis necesitaría la compatibilidad 32-bit y la ruta exacta; no hay prueba 13.02 | **UNVERIFIED_13_02** |
| **FreeBSD-SA-19:02.fd / CVE-2019-5596** | FreeBSD moderno de la época del advisory | Reference count de UNIX sockets/file structures; posible liberación incorrecta | PoC FreeBSD público | Falta demostrar misma implementación en FreeBSD 9/Orbis y primitive | **HYPOTHESIS** |
| **FreeBSD-SA-19:15.mqueuefs** | FreeBSD moderno de la época del advisory | Bug de mqueuefs, posible elevación | Exploit FreeBSD público | No hay evidencia de que mqueuefs estuviera habilitado o implementado igual en Orbis | **HYPOTHESIS / UNVERIFIED_13_02** |
| **Routing dst/netmask validation** | Fix FreeBSD 13.0, 2021 | Mensajes de routing con sockaddr malformado; corrupción de consumidores posteriores | Sin PoC PS4 R/W | La lógica moderna no es portable literalmente a FreeBSD 9; puede inspirar auditoría, no confirmar vulnerabilidad | **DISPROVEN/PATCHED** como traslado literal |
| **CVE-2013-5209 SCTP** | Bug FreeBSD histórico; entrada PSDevWiki lo sitúa cerca de 1.01 | Kernel stack disclosure en INIT-ACK | Sin exploit PS4 público | Demasiado antiguo y limitado a leak; no 13.02 | **DISPROVEN/PATCHED** |
| **CVE-2013-3077 IP_MSFILTER** | Bug FreeBSD histórico; entrada lo sitúa cerca de 1.01 | Integer overflow, posible kernel read/write | Sin PoC PS4 moderno | No hay evidencia de supervivencia | **DISPROVEN/PATCHED** |

Los CVEs modernos de esta tabla son **candidatos de investigación**, no vulnerabilidades PS4 confirmadas. Sus registros oficiales describen versiones FreeBSD 13.5–15 o 14/15, mientras que Orbis deriva de una base FreeBSD 9 modificada por Sony. Las etiquetas tentativas de PSDevWiki se conservan porque son útiles para orientar una comparación estática, pero no sustituyen un diff del código de Orbis.

## Familias solicitadas sin candidato confirmado

**kqueue/knote.** `kqueue` aparece como parte importante de la cadena Netctrl/ucred y de varias rutas de file descriptors, pero no se encontró un CVE público independiente que demuestre un UAF kqueue/knote en PS4 13.02. Las referencias a kqueue en Netctrl son dependencia de la primitive histórica, no evidencia de un bug nuevo.

**UDF.** No se encontró una vulnerabilidad pública de kernel UDF con PoC PS4 13.02. La superficie debe mantenerse como hipótesis de auditoría de parser/mount, pero no puede elevarse a candidato técnico sin una función, commit o writeup que señale un defecto concreto.

**ioctl y filesystem genérico.** Hay antecedentes de `TIOCNOTTY`, BPF, `amd64_set_ldt`, `aio`, exFAT y UFS/FFS. Ninguno aporta por sí solo una ruta 13.02 confirmada. El siguiente paso documental debe ser localizar implementaciones Orbis de las funciones y compararlas con los commits de corrección, no asumir que el nombre del syscall implica identidad de código.

## Independencia y procedencia

La línea `Vue After Free → Riyon/ps-vue-jb-2.5 → forks de Vue` no debe contarse como varias confirmaciones independientes: comparten ascendencia, archivos o ideas. Los offsets SLOPOS/13.02 también deben tratarse con cautela porque el propio material revisado declara dependencia de tablas de `ps4-linux-loader`/ArabPixel para offsets de kexec. Un header 13.02 en un fork demuestra que alguien publicó una tabla; no demuestra que se derivara de bytes independientes ni que corresponda a la primitive del exploit.

El repositorio `adri22235/ps4-suid-scanner` es una fuente reciente y útil para registrar las afirmaciones Celsius/13.04, pero tiene diez commits concentrados entre el 18 de julio y el 9 de agosto de 2026, y su propia documentación atribuye offsets 13.04 a una base 13.02 y a verificación de Pharaoh2k. Eso es procedencia trazable, no independencia completa ni prueba de R/W.

## Ranking final

### A) Evidencia fuerte para 13.02

No hay actualmente un candidato que cumpla el estándar de **evidencia fuerte específica de PS4 13.02** para kernel R/W. Netctrl/ucred es el más cercano por código PS4 y primitive; Celsius es el más cercano por alcance nominal hasta 13.04. Ambos permanecen `UNVERIFIED_13_02`.

Para subir Netctrl a `CORROBORATED` se necesita una segunda fuente independiente que muestre la misma ruta funcionando en 13.02, o un artefacto de kernel 13.02 que permita confirmar que las condiciones de triple-free/reclaim no fueron alteradas. Para subir Celsius se necesita una imagen FFS/UFS reproducible, un análisis de la ruta Orbis `ffs_mountfs()` y una demostración estática o documentada de que el overflow puede convertirse en una primitive controlable.

### B) Candidatos plausibles pero sin prueba

El grupo B incluye Celsius/ffs_mount, exFAThax v2, semctl, IPV6_MSFILTER, TIOCNOTTY, CVE-2020-7460, net80211, CVE-2025-14558 y las variantes históricas de file descriptor/mqueuefs. Son plausibles sólo en el sentido de que existe una descripción técnica o una relación de código; ninguno tiene una PoC PS4 13.02 con R/W observable en las fuentes revisadas.

La evidencia concreta necesaria para subirlos es diferente en cada caso: presencia de la función en el kernel Orbis, equivalencia del código vulnerable, acceso desde userland autorizado, primitive más allá de un crash, y un artefacto independiente de hardware o de diff de firmware.

### C) Probablemente parcheados antes de 13.02

Aquí están IPV6_2292PKTOPTIONS, IP6_EXTHDR_CHECK, BPF, NamedObj, `dlclose`, BadIRET, sys_getcontext, sys_thr_get_ucontext, exFAThax v1, routing dst/netmask, SCTP y `IP_MSFILTER` antiguo. Sus rangos documentados terminan mucho antes de 13.02 o sus fixes son anteriores. Pueden servir para estudiar técnicas y familias de bugs, pero no son candidatos realistas para una cadena 13.02 sin nueva evidencia.

### D) Descartados

Se descartan como candidatos directos a Orbis 13.02 `CVE-2026-7270` porque `exec_args_adjust_args()` fue introducida en FreeBSD 13 y no existe en la base FreeBSD 9; `CVE-2026-45250 setcred` porque depende de campos de FreeBSD 14.3–15; la variante literal de `rtsock_msg_buffer()` de CVE-2026-3038 porque esa función no pertenece a la base antigua; y cualquier claim de UDF/exFAT/MP4 que sólo muestre un crash o parser issue sin acceso a kernel R/W.

## Fuentes principales revisadas

[PSDevWiki Vulnerabilities](https://www.psdevwiki.com/ps4/Vulnerabilities), [PSDevWiki Bugs](https://www.psdevwiki.com/ps4/Bugs), [TheOfficialFloW NetControl gist](https://gist.github.com/TheOfficialFloW/7174351201b5260d7780780f4059bebf), [RiyonAbib07/ps-vue-jb-2.5](https://github.com/RiyonAbib07/ps-vue-jb-2.5), [adri22235/ps4-suid-scanner](https://github.com/adri22235/ps4-suid-scanner), [ConsoleMods Exploit Chart](https://consolemods.org/wiki/PS4:Exploit_Chart), [The ZDI CVE-2020-7460 writeup](https://www.thezdi.com/blog/2020/9/1/cve-2020-7460-freebsd-kernel-privilege-escalation), [CTurt dlclose analysis](https://cturt.github.io/dlclose-overflow.html), [CTurt kernel exploitation](https://cturt.github.io/ps4-3.html), [FreeBSD CVE-2026-5398 record](https://www.cve.org/CVERecord?id=CVE-2026-5398), [NVD CVE-2026-5398](https://nvd.nist.gov/vuln/detail/CVE-2026-5398), [CVE-2026-58087/OpenCVE](https://app.opencve.io/cve/CVE-2026-58087), [FreeBSD CVE-2020-7460 PoC](https://github.com/thezdi/PoC/tree/master/CVE-2020-7460), [Secfault FreeBSD-SA-19:02.fd writeup](https://secfault-security.com/blog/FreeBSD-SA-1902.fd.html), [Exploit-DB exFAT entry](https://www.exploit-db.com/exploits/48644).

## Conclusión

La investigación amplía sustancialmente el corpus, pero no cambia el bloqueo principal: **no existe evidencia pública suficiente de kernel R/W reproducible en PS4 FW 13.02**. La prioridad estática razonable es comparar implementaciones Orbis o dumps legítimos de 13.00/13.02 para NetControl/ucred y `ffs_mountfs()`, verificar la presencia de los campos y rutas vulnerables y rastrear los commits de corrección. Hasta que exista ese artefacto, toda compatibilidad 13.02 debe conservarse como hipótesis o `UNVERIFIED_13_02`.
