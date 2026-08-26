# Investigación de kernel R/W para PS4 13.02

**Fecha de corte:** 26 de agosto de 2026  
**Ámbito:** únicamente candidatos de kernel exploit y primitivas que pudieran conducir a kernel R/W en PS4 13.02.  
**Regla:** userland, escape de sandbox, offsets y un PoC de FreeBSD no se cuentan como kernel R/W de PS4 13.02 sin una prueba específica.

## Conclusión ejecutiva

No se localizó una ruta pública reproducible que demuestre `userland → kernel R/W` en PS4 13.02. El candidato más cercano sigue siendo **Netctrl/ucred triple-free**, porque su implementación pública alcanza PS4 13.00 y contiene una ruta explícita de lectura/escritura de kernel; sin embargo, sus propios README y tablas separan el userland 13.02 del jailbreak funcional 13.00. La entrada de mmap para 13.02 en algunos árboles no demuestra que la explotación sobreviva en 13.02.

La investigación pública también muestra varios bugs de FreeBSD con etiquetas tentativas `?<=13.02?`, `?<=13.04?` o `?<=13.50?` en PSDevWiki. Esas etiquetas expresan una hipótesis de afectación o una comparación de código, no soporte PS4. En los casos revisados faltan PoC PS4 13.02, evidencia de hardware y demostración de R/W.

## Matriz de candidatos

| Candidato | Firmware máximo confirmado | Fuente primaria | PoC disponible | Evidencia en hardware PS4 13.02 | Evidencia de parche 13.00→13.02 | Primitive | Estado |
|---|---|---|---|---|---|---|---|
| **Netctrl / ucred triple-free** | **13.00** para jailbreak funcional publicado; el userland Vue llega a 13.02 | Gist de TheOfficialFloW y código derivado en `RiyonAbib07/ps-vue-jb-2.5` | Sí, código Java público: spray de `ucred`, triple-free, leak de kqueue y uso de `kread/kwrite` posterior | No localizada para 13.02 | No se encontró diff público que pruebe supervivencia o parche específico 13.00→13.02 | Corrupción/liberación múltiple de `ucred`, leak de punteros y primitive posterior de lectura/escritura | **UNVERIFIED_13_02** |
| **Offsets mmap asociados a Netctrl** | Entrada documental 13.02; no implica exploit funcional | `src/download0/kernel.ts` de Riyon y árboles derivados | Sí como código de selección de offsets, no como prueba de R/W | No | No | Parcheo de mmap/RWX, no primitive por sí mismo | **SOURCE_ONLY** |
| **Lapse / semctl histórico** | **12.02** para Lapse publicado | `Feyzee61/psfree_lapse`, Vue/Netctrl publicados y tabla comunitaria | Sí para rangos históricos | No en 13.02 | No hay análisis público suficiente que demuestre compatibilidad 13.02 | Depende del bug semctl/UAF de la cadena histórica; no se debe equiparar automáticamente al CVE nuevo | **HISTORICAL_ONLY** para 13.02 |
| **CVE-2026-58087 semctl TOCTOU** | PSDevWiki lo marca tentativamente `?<=13.52?` | PSDevWiki; advisories/fix de FreeBSD citados allí | No hay exploit PS4 en la entrada revisada | No; PSDevWiki dice que PS4/PS5 pueden estar afectadas | No hay diff PS4 13.00→13.02 ni prueba de que el código PS4 contenga la misma ruta | OOB read/write de heap por carrera al dimensionar conjuntos de semáforos | **UNVERIFIED_13_02** |
| **CVE-2026-5398 TIOCNOTTY** | PSDevWiki lo marca tentativamente `?<=13.02?` | PSDevWiki, advisory FreeBSD y writeup de Calif.io citado | PoC citado para FreeBSD 15, no para PS4 | No; la página advierte que PS4/PS5 pueden no estar afectadas | No hay diff PS4 13.00→13.02 | UAF de puntero de sesión; posible elevación en el sistema afectado | **UNVERIFIED_13_02** |
| **Overflow UFS/FFS al montar** | PSDevWiki lo marca tentativamente `?<=13.04?` | PSDevWiki y fix histórico de FreeBSD | No hay PoC PS4 13.02 | No | La página sólo indica parche desde PS4 13.50; no valida la build 13.02 | Overflow durante mount/reload; requiere partición malformada y, según la página, posiblemente otra vía para cifrarla | **UNVERIFIED_13_02** |
| **CVE-2026-3038 routing sockets** | `?<=13.04?` como hipótesis de la página | PSDevWiki; PoC citado para panic PS4 13.52 | Sí para provocar panic en PS4 13.52 según la página | No para 13.02; no hay R/W | La propia página dice que el PS4 basado en FreeBSD 9 probablemente no es vulnerable al bug upstream | Stack overflow con canario; sólo DoS citado, escalada hipotética | **UNVERIFIED_13_02** |
| **CVE-2025-14558 ND6/rtsold** | `?<=13.02?` como hipótesis de la página | PSDevWiki, advisory/PoCs de FreeBSD | Sí para FreeBSD, no PS4 | No; PSDevWiki advierte que PS4/PS5 pueden no estar afectadas | No hay diff PS4 13.00→13.02 | RCE en `rtsold/resolvconf` si aplica; no es demostración de kernel R/W PS4 | **UNVERIFIED_13_02** |
| **CVE-2026-49412 IPV6_MSFILTER** | `?<=13.50?` como hipótesis | PSDevWiki y fix FreeBSD | Sin PoC PS4 | No; la página dice “maybe since PS4 13.52” | No | UAF por carrera en filtro multicast; posible elevación si la implementación aplica | **UNVERIFIED_13_02** |
| **CVE-2026-45251 file descriptors** | `?<=13.50?` como hipótesis | PSDevWiki y writeup/PoC de Calif.io para FreeBSD | PoC FreeBSD, no PS4 | No; la página dice que PS4/PS5 quizá no estén afectadas | No | UAF convertido en escritura arbitraria de puntero de kernel mediante reclaim SCM_RIGHTS | **UNVERIFIED_13_02** |
| **CVE-2026-45250 setcred** | `?<=13.50?` como hipótesis | PSDevWiki y fix FreeBSD | Sin PoC PS4 | No; la entrada describe una diferencia de versiones FreeBSD que no prueba PS4 | No | Overflow de stack; potencial ejecución kernel si la ruta existe | **UNVERIFIED_13_02** |
| **aio_multi_delete** | Histórico aproximadamente hasta 11.52; parche observado alrededor de 12.00 | PSDevWiki y diffs de kernel citados | No | No | No | Bug de locking en AIO; la propia página dice que es difícil y sin PoC | **HISTORICAL_ONLY** |

## Netctrl/ucred: auditoría de procedencia y alcance

La fuente primaria visible enlazada desde discusiones comunitarias es el gist de **TheOfficialFloW**, `ExploitNetControlImpl.java`. El código implementa una secuencia de triple-free de `ucred`, fuga de objetos `kqueue`, búsqueda de `allproc` y operaciones `kread/kwrite` sobre estructuras de credenciales. Eso sí es una primitive de kernel R/W en el contexto de una build compatible; no prueba por sí mismo que la misma build sea PS4 13.02.

El repositorio `RiyonAbib07/ps-vue-jb-2.5` no es un fork de GitHub y declara en su descripción `7.00-13.00`, con mejoras de estabilidad para 12.50+ mediante Netctrl/Poopsploit. Su README separa claramente `vue-after-free` userland hasta 13.04 de Netctrl hasta 13.00 y dice que en 13.02 o superior sólo funciona el userland. Su `kernel.ts` contiene entradas de mmap 13.02, pero la tabla de offsets de la cadena Netctrl agrupa 12.50/12.52/13.00 y no añade una cadena funcional 13.02.

`owendswang/vue-after-free-lite` es un fork de `Vuemony/vue-after-free`; sus commits de estabilidad Netctrl no constituyen una segunda línea independiente. `Vuemony/vue-after-free` a su vez recibe merges de otros árboles de la misma escena. Por ello, README, offsets mmap o correcciones de estabilidad repetidos entre esos repositorios cuentan como una sola línea de procedencia, salvo que aporten bytes, método de derivación y una prueba independiente.

## Otros candidatos

`Feyzee61/psfree_lapse` fija explícitamente su alcance en PS4 7.00–9.60, por lo que no es candidato 13.02. `iaceene/HENloader_Source` declara Lapse/Poopsploit de 9.00 a 12.52. Ambos son útiles como evidencia histórica de la cadena, no como confirmación 13.02.

PSDevWiki enumera bugs nuevos de FreeBSD con alcances tentativos que incluyen 13.02. El patrón común es que el análisis tiene una descripción upstream, un advisory o un PoC del sistema FreeBSD, pero carece de una implementación PS4. En particular, una cabecera `?<=13.02?` no confirma afectación de PS4: la misma página añade advertencias explícitas de que PS4/PS5 pueden no estar afectadas.

La tabla de ConsoleMods y la discusión de Reddit corroboran el estado público de la escena: el kernel exploit publicado llega a 13.00 y 13.02 conserva userland/BD-J, pero ninguna de esas fuentes aporta una demostración binaria de R/W en 13.02. Reddit contiene además comentarios especulativos de usuarios, que no se elevan a evidencia.

## Evidencia concreta que falta

Para elevar Netctrl a `VERIFIED` en 13.02 se necesitan, como mínimo, un firmware exacto identificado, una PoC o build que seleccione offsets 13.02 para la cadena Netctrl completa, un log de ejecución en hardware PS4 13.02 que muestre la primitiva antes del parcheo, y una demostración observable de lectura y escritura de una dirección controlada. También hace falta conservar el hash de los artefactos y separar el log de crash/panic del log de R/W exitoso.

Para los CVE/bugs candidatos se necesita además comparar el código vulnerable y parcheado con el kernel PS4 real de 13.00 y 13.02. Una similitud con FreeBSD upstream o un rango tentativo de PSDevWiki no sustituye ese diff. El overflow UFS/FFS requiere verificar tanto la ruta de mount como la posibilidad de preparar el artefacto cifrado en una consola concreta; no es un reemplazo inmediato de kernel R/W.

## Respuestas solicitadas

**1. Candidato más prometedor.** Netctrl/ucred triple-free, porque es el único candidato público revisado que combina una implementación de explotación PS4 cercana al objetivo —funcional publicada hasta 13.00— con una ruta explícita de leak y `kread/kwrite`. Aun así, su estado correcto para 13.02 es **`UNVERIFIED_13_02`**.

**2. Evidencia concreta que falta.** Falta una ejecución reproducible de Netctrl en hardware PS4 13.02 que demuestre la triple-free/ucred, el leak, la primitive de kernel R/W y un write observable, junto con los artefactos y offsets de la misma build. También falta un diff o dump que explique qué cambia entre 13.00 y 13.02 y por qué la cadena sobrevive.

**3. Ruta reproducible actual.** **No existe actualmente una ruta pública reproducible `userland → kernel R/W` para PS4 13.02.** Lo que sí existe es userland/BD-J para 13.02, código Netctrl funcional publicado hasta 13.00, tablas y entradas de offsets de procedencia limitada, y varios bugs FreeBSD/PSDevWiki que siguen siendo hipótesis para PS4.

## Referencias

[1]: https://gist.github.com/TheOfficialFloW/7174351201b5260d7780780f4059bebf "TheOfficialFloW — ExploitNetControlImpl.java"
[2]: https://github.com/RiyonAbib07/ps-vue-jb-2.5 "RiyonAbib07/ps-vue-jb-2.5"
[3]: https://github.com/Vuemony/vue-after-free "Vuemony/vue-after-free"
[4]: https://github.com/owendswang/vue-after-free-lite "owendswang/vue-after-free-lite"
[5]: https://github.com/Feyzee61/psfree_lapse "Feyzee61/psfree_lapse"
[6]: https://github.com/iaceene/HENloader_Source "iaceene/HENloader_Source"
[7]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer wiki — Vulnerabilities"
[8]: https://www.psdevwiki.com/ps4/Bugs "PS4 Developer wiki — Bugs"
[9]: https://consolemods.org/wiki/PS4:Exploit_Chart "ConsoleMods — PS4 Exploit Chart"
[10]: https://www.reddit.com/r/ps4homebrew/comments/1omgsul/new_kernel_exploit_up_to_1300_for_ps4_and_1200/ "Reddit — New kernel exploit up to 13.00 for PS4 and 12.00 for PS5"
[11]: https://github.com/alferdoss/SLOPOS-offsets "alferdoss/SLOPOS-offsets"
[12]: https://cturt.github.io/ps4-3.html "CTurt — Hacking the PS4, part 3: Kernel exploitation"
