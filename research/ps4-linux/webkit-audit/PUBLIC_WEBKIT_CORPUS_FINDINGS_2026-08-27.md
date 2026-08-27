# Corpus público WebKit PS4 13.02/13.52 — primera pasada

## Alcance

Búsqueda pública centrada en SPRX/SELF/ELF, blobs, proyectos de reversing, commits, releases y mirrors. No se descargaron ni ejecutaron binarios en esta pasada.

## Hallazgos

| Artefacto | Origen y fecha | Firmware declarado | Contenido real | Clasificación |
|---|---|---|---|---|
| `CSSFontFace-Exploit` | `ntfargo/CSSFontFace-Exploit`, creado 2026-06-13, 38 commits, 310 stars y 84 forks en la extracción pública | Vulnerabilidad declarada PS4 6.00–13.52; tabla “Exploitable In” sólo PS4 6.00–11.02 | Repositorio con `public/`, `host.py`, certificado y código de exploit CSSFontFace para rangos antiguos. El README declara que los cambios de layout posteriores a 11.5x hacen inutilizable la primitive `m_featureSettings` de este repo | Código WebKit real para rangos antiguos; **no es un artefacto 13.52 funcional** |
| PR #4 de `ntfargo/CSSFontFace-Exploit` | ArabPixel, 2026-06-27/29; rama `ArabPixel:main` → `ntfargo:main`; cerrada 2026-07-18 | 9.xx/10.xx/11.0x/11.50, parcial | Commits `9e6fb11`, `d22a549`, `c741fe7`, `254b622`; el PR enumera gadgets ROP y offsets relativos CSSFontFace como faltantes. Los comentarios aportan patrones y análisis de layouts para versiones antiguas, no un blob 13.02/13.52 | Código/commits reales, pero **parcial y no 13.52** |
| `Feyzee61/cssfontface_lapse` | Fork creado 2026-07-04, 14 commits, 3 stars, 1 fork | Objetivo 9.00–11.02; 9.00/9.60 probados y 11.02 en entrypoint | Fork de `ufm42/wobkot`, `ps3120/CSSFontFace-Exploit` y `ntfargo`; excluye payloads `.bin`/`.elf` y no aporta módulo WebKit | Derivado, no independiente; **no 13.52** |
| `MasterPS0/SIMPLE-WEBKIT-USERLAND-FOR-PS4-PS5` | Creado 2026-05-04, 8 commits | Afirma “any firmware” | Sólo `index.html` e `inject.js`, interfaz genérica para cargar JavaScript; no contiene bug, SPRX, blob, gadget ni primitive | Infraestructura documental/genérica; **no evidencia WebKit explotable** |
| `Vuemony/vue-after-free` | Repositorio con 411 commits, creado 2025-12-20 | README declara userland 5.05–13.04; tabla funcional actual 7.00–13.00 | Código real de Vue/PSFree, pero el propio README dice que por encima de 13.00 sólo queda userland y no jailbreak; no contiene WebKit 13.52 | Código real para rangos anteriores; **no 13.52** |

## Conclusiones provisionales

1. En esta pasada no apareció ningún `libSceNKWebKit.sprx`, SELF, ELF de WebKit, dump de `libSceNKWebKit`, proyecto IDA/Ghidra/Binary Ninja de Orbis 13.02/13.52 ni blob con hash verificable para esas versiones.
2. El repositorio `ntfargo/CSSFontFace-Exploit` es el artefacto de código WebKit más relevante encontrado, pero su propia documentación limita la primitive implementada a PS4 6.00–11.02 y explica que los cambios de layout posteriores a 11.5x la rompen.
3. El PR de ArabPixel confirma por historial que incluso la extensión a 11.50 era parcial y que faltaban offsets relativos/gadgets. No contiene soporte 13.02/13.52.
4. Los forks de CSSFontFace y Vue son líneas derivadas o de versiones antiguas; no constituyen corroboración independiente de WebKit 13.52.
5. La única afirmación de 13.52 localizada en esta pasada procede de claims/README o resultados secundarios, no de bytes de WebKit ni de un proyecto de reversing.

## Fuentes

[1]: https://github.com/ntfargo/CSSFontFace-Exploit "CSSFontFace-Exploit"
[2]: https://github.com/ntfargo/CSSFontFace-Exploit/pull/4 "PR #4 — partial firmware support"
[3]: https://github.com/Feyzee61/cssfontface_lapse "Feyzee61 CSSFontFace/Lapse fork"
[4]: https://github.com/MasterPS0/SIMPLE-WEBKIT-USERLAND-FOR-PS4-PS5 "Generic WebKit userland framework"
[5]: https://github.com/Vuemony/vue-after-free "Vue After Free"

## PSDevWiki: nuevas entradas de bugs

La página pública `PS4:WebKit_Bugs` contiene una sección de vulnerabilidades asociadas a explotación de PS5 13.60 y lista varias entradas con rango PS4 `?6.00-13.52?`, entre ellas conversiones/casts de `JSC::JSCell`, `JSC::MarkedVector` y `WebCore::CloneSerializer/Deserializer`. El uso de signos de interrogación es literal y la propia página las sitúa en el contexto de bugs documentados/untested, no como soporte PS4 13.52 verificado.

La misma página lista otras entradas “Promising” o “Untested”, incluida una posible vulnerabilidad ICU para `String.prototype.normalize` marcada `<=?13.02?`. Estas entradas son fichas de investigación y no proporcionan, en el extracto público revisado, un `libSceNKWebKit.sprx`, hash de blob, proyecto IDA/Ghidra o testcase PS4 13.02/13.52 descargable.

Por tanto, PSDevWiki aporta nombres de funciones, rangos hipotéticos y procedencia documental, pero no un artefacto binario real de WebKit de los firmwares objetivo. Clasificación: **SOURCE_ONLY / HYPOTHESIS** para 13.02/13.52; no es evidencia de primitive funcional.

[6]: https://www.psdevwiki.com/ps4/WebKit_Bugs "PS4 Developer wiki — WebKit Bugs"
[7]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer wiki — Vulnerabilities"

## Artefacto de código real: CSSFontFace-Exploit

Se clonó para inspección estática `ntfargo/CSSFontFace-Exploit` en su rama principal. Contiene código JavaScript real en `public/src/ps4/userland.js`, archivos de constantes/gadgets y parches `.bin` para 6.00, 6.20, 6.50, 6.70, 7.00, 7.50, 8.00, 8.50, 9.00, 9.03, 9.50, 10.00, 10.50, 11.00 y 11.02. No contiene SPRX/SELF/ELF de WebKit ni parches 13.02/13.52.

La implementación contiene referencias a `CSSFontFace`, `m_featureSettings`, vtables, gadgets y resolución de bases de libc/libkernel, por lo que es código de exploit userland real para versiones históricas. Sin embargo, el README limita la tabla funcional del repositorio a PS4 6.00–11.02 y explica que los cambios de layout posteriores a 11.5x rompen la primitive basada en `m_featureSettings`. El commit auditado es el tip de la rama principal obtenido el 27 de agosto de 2026; su hash completo y los hashes de todos los parches están en el inventario de la sesión.

Clasificación: **VERIFIED como código fuente y assets de parches para firmwares antiguos**; **INVALID como evidencia de un userland 13.02/13.52**. El artefacto demuestra qué tipo de bytes/layouts serían necesarios para una adaptación, pero no aporta los bytes WebKit retail objetivo.

## PSDevWiki — entradas recientes para PS4 13.52

La página `WebKit_Bugs` lista tres entradas con rango PS4 `?6.00-13.52?`: `JSC::JSCell::toX`, `JSC::MarkedVector` y `WebCore::CloneSerializer/Deserializer`. El signo de interrogación forma parte del rango publicado. La sección está presentada como bugs asociados a explotación de PS5 13.60 y no aporta en el extracto revisado un blob PS4 13.52, hash de módulo, proyecto de reversing ni testcase hardware.

La clasificación correcta es **SOURCE_ONLY / UNVERIFIED_13_52**. Estas entradas pueden ser candidatos de investigación, pero no prueban que una implementación PS4 13.52 exista ni que produzca una primitive.

[8]: https://www.psdevwiki.com/ps4/WebKit_Bugs "PS4 Developer wiki — WebKit Bugs"

## Procedencia anterior: `ps3120/FontFace-Lapse` y `ufm42/wobkot`

`ps3120/FontFace-Lapse` (creado 2026-02-09, 3 commits) contiene código real de FontFace/Lapse, un `payload.bin` y módulos de ROP, pero su descripción es explícitamente de PS4 9.00. No contiene SPRX/SELF de WebKit ni assets 13.02/13.52.

`ufm42/wobkot` (creado 2026-06-24, 16 commits) es un userland basado en CSSFontFace y atribuye la información técnica a `ntfargo`, además de enlazar a `synacktiv/PS4-webkit-exploit-6.XX`. Su README sólo describe cómo colocar un payload y servir la página; no aporta un dump WebKit 13.02/13.52.

El write-up de LinearFox/Nathan Fargo y ufm42 describe el UAF de CSSFontFace y la transición hasta arbitrary read/write en PS4, pero establece el rango práctico PS4 en 6.00–11.02. También documenta que cambios de layout posteriores a 11.5x invalidan la primitive `m_featureSettings` usada por el código público. El artículo es una fuente técnica de la vulnerabilidad antigua, no un artefacto WebKit 13.02/13.52.

Clasificación: código real y procedencia corroborada para firmwares antiguos; **UNVERIFIED_13_02 / UNVERIFIED_13_52** para los objetivos actuales.

[9]: https://github.com/ps3120/FontFace-Lapse "ps3120 FontFace-Lapse"
[10]: https://github.com/ufm42/wobkot "ufm42 wobkot"
[11]: https://linearfox.com/blog/cssfontface-uaf-playstation "From CSSFontFace to ARW"

## Forks públicos inspeccionados

Se clonaron e inspeccionaron forks públicos seleccionados de CSSFontFace-Exploit, entre ellos `bucifal13/PS4WK`, `kamaeff/ps4-jb-webkit`, `Deladrians/CSSExploit` y `neo305/css`. Los hashes de `userland.js`, `constants.js`, parches y `payload.bin` se registraron en `forks_static_hashes.txt`.

Los forks con estructura CSSFontFace comparten hashes de archivos clave con la línea `ntfargo` o con forks inmediatos; por ejemplo, `ps4-jb-webkit` tiene el mismo `userland.js`, `constants.js` y parches que `css`. No aparecieron assets `libSceNKWebKit`, `*.sprx`, `*.self`, ELF de WebKit ni parches 13.02/13.52. La similitud confirma derivación/copia, no independencia.

Clasificación: **DERIVED / SOURCE_ONLY** para el código antiguo; **INVALID** como evidencia de un artefacto WebKit 13.02/13.52.

## Nueva búsqueda por claims 13.52

Las búsquedas adicionales devuelven vídeos y publicaciones que afirman un userland PS4 13.52, pero no identifican un repositorio, commit, SPRX, SELF, ELF, dump o hash descargable. Los resultados GitHub vuelven a apuntar a `ntfargo/CSSFontFace-Exploit` y forks, cuyo soporte implementado termina en 11.02; los resultados de YouTube/Shorts no son fuentes primarias de bytes.

Clasificación provisional de esos claims: **SOURCE_ONLY / UNVERIFIED_13_52**. No se incorporan como artefactos.

## Línea Synacktiv: artefacto histórico real

`synacktiv/PS4-webkit-exploit-6.XX` es un repositorio público de un solo commit con `index.html`, `int64.js`, `ps4.js` y `utils.js`. Su write-up de 2020 describe un exploit WebKit PS4 6.xx que convierte un UAF en una primitive de lectura/escritura y ejecución en ese contexto. No contiene SPRX/SELF/ELF ni blobs de WebKit 13.02/13.52.

El repositorio y el artículo son fuentes primarias para una línea histórica de WebKit 6.xx, y varios forks posteriores los citan como ascendencia. No constituyen evidencia de que la misma primitive funcione en 13.02 o 13.52.

Clasificación: **VERIFIED como artefacto WebKit histórico 6.xx**; **INVALID/UNVERIFIED_13_02/UNVERIFIED_13_52** para los firmwares objetivo.

[12]: https://github.com/synacktiv/PS4-webkit-exploit-6.XX "Synacktiv PS4 WebKit exploit 6.XX"
[13]: https://www.synacktiv.com/en/publications/this-is-for-the-pwners-exploiting-a-webkit-0-day-in-playstation-4 "Synacktiv WebKit 0-day write-up"

## Vídeos que afirman userland 13.52

Se revisaron tres publicaciones públicas. Un Short de @mbcrump titulado `PS4 13.52 CSSFontFace WebKit Userland Demo` afirma una demo y enlaza a una publicación de X, pero el vídeo aparece como no disponible y la descripción no proporciona código, hash, módulo ni proyecto. Otro vídeo titulado `PS4 13.52 BD-J USERLAND BUG FULLY ACHIEVED!` afirma un bug userland en 13.52, pero su descripción sólo habla de una demo y reconoce que todavía falta un kernel bug estable. Un tercer vídeo titulado `PS4/PS5 13.52/13.60 WEBKIT USERLAND BUG WORKING` no expone artefactos en la extracción pública.

Estas fuentes prueban que existen afirmaciones públicas y material audiovisual, no que exista un artefacto WebKit descargable ni que la primitive haya sido reproducida. Clasificación: **SOURCE_ONLY / UNVERIFIED_13_52**.

[14]: https://www.youtube.com/shorts/O70FxdT12f4 "PS4 13.52 CSSFontFace WebKit Userland Demo"
[15]: https://www.youtube.com/watch?v=ZG-SGV4c-kQ "PS4 13.52 BD-J USERLAND BUG FULLY ACHIEVED"
[16]: https://www.youtube.com/watch?v=jMwu0uJ5SY4 "PS4/PS5 13.52/13.60 WEBKIT USERLAND BUG WORKING"

## Publicación primaria de X: claim de workaround 13.52

La publicación de Dr.Yenyen/@calmboy2019 del 4 de agosto de 2026 afirma literalmente que existe userland WebKit PS4 hasta 13.52 y que `ufm42` encontró un workaround para que el exploit FontFace funcionara; una respuesta agradece a ArabPixel por pruebas y offsets. La publicación no adjunta en la extracción pública un repositorio, commit, blob, SPRX, hash, tabla de offsets ni proyecto de reversing.

Esto es una pista de procedencia más fuerte que un vídeo secundario, porque atribuye autores concretos (`ufm42`, `ArabPixel`) y una fecha, pero sigue siendo **SOURCE_ONLY / UNVERIFIED_13_52** hasta que aparezca el workaround en código o un artefacto verificable. No se debe confundir con la implementación pública de `ntfargo`, cuyo límite documentado es 11.02.

[17]: https://x.com/calmboy2019/status/2084636491628663088 "Dr.Yenyen — PS4 WebKit userland up to 13.52"

## Corroboración secundaria de la pista `ufm42`

La discusión de `r/ps4homebrew` repite que `ufm42` encontró un workaround para los cambios que impedían usar FontFace por encima de 11.02 y afirma userland hasta 13.52. El mismo post aclara que el jailbreak continúa limitado a 13.00. No enlaza un repositorio, commit, blob, SPRX, hash ni instrucciones técnicas del workaround.

La página de respuestas de ArabPixel en X sólo expone el perfil y un enlace a GitHub; no añade un artefacto técnico. La publicación original de Dr.Yenyen es la fuente más concreta de la afirmación, pero sigue siendo un claim de autoría y fecha, no una entrega de código.

Clasificación: **CORROBORATED como existencia de una afirmación pública repetida**; **SOURCE_ONLY / UNVERIFIED_13_52** como soporte técnico.

[18]: https://www.reddit.com/r/ps4homebrew/comments/1vfbae9/ps4_and_ps5_webkit_userland_till_latest_firmwares/ "Reddit discussion repeating the ufm42 claim"
[19]: https://x.com/arabpixell/with_replies "ArabPixel X profile"

## Repositorios públicos actuales de ufm42

La lista pública de repositorios de `ufm42` contiene `wobkot`, `kexp`, `vue-after-free`, `Netflix-N-Hack`, `cobolt`, `ps5-linux-loader`, `shsrv` y `Playstation-5-Save-Mounter`. No aparece un repositorio con nombre que identifique el workaround FontFace 13.52.

`ufm42/kexp` es un payload post-jailbreak y su README describe una ruta que presupone que el proceso userland ya está jailbroken; por tanto no es el workaround WebKit. `ufm42/vue-after-free` es un fork experimental del proyecto Vue y no se presenta como soporte 13.52. `ufm42/ps5-linux-loader` es exclusivamente PS5 y sus firmwares son 3.00–7.61.

Esto estrecha la procedencia: la afirmación pública de que `ufm42` halló un workaround 13.52 no está acompañada, en sus repositorios públicos actuales, por un proyecto identificable o un artefacto binario. Clasificación: **SOURCE_ONLY / UNVERIFIED_13_52**.

[20]: https://github.com/ufm42 "Repositorios públicos de ufm42"
[21]: https://github.com/ufm42/kexp "ufm42 kexp"
[22]: https://github.com/ufm42/vue-after-free "ufm42 vue-after-free"
[23]: https://github.com/ufm42/ps5-linux-loader "ufm42 ps5-linux-loader"

## Pista adicional: Gezine/BD-JB5

La búsqueda pública muestra actividad de `Gezine/BD-JB5` con referencias a `Add PS4 13.52 offsets`, mejoras de Poops y una integración de shellcode de `ufm42/kexp`. La página de actividad extraída no expone el diff ni un blob WebKit; el contexto del proyecto es BD-JB5/Poops y soporte de payload, no un módulo `libSceNKWebKit` o un proyecto de reversing del WebKit.

Clasificación: **CORROBORATED como infraestructura BD-J/payload 13.52**; **INVALID como evidencia directa de WebKit 13.52** hasta revisar un commit/archivo específico que contenga bytes o código WebKit.

[24]: https://github.com/Gezine/BD-JB5/activity "Gezine BD-JB5 activity"

## Inspección estática de Gezine/BD-JB5

El árbol público `Gezine/BD-JB5` contiene infraestructura BD-J/Poops para PS4/PS5, APIs Java de buffer y kernel, `PS4_KernelOffset.java`, un loader de BIN y una referencia a `ufm42/kexp`. No se localizaron archivos `libSceNKWebKit`, `sprx`, `self`, dumps WebKit, firmas de WebKit ni código CSSFontFace. Las coincidencias `13.52`/`1352` de la actividad pública son soporte de BD-J/offsets, no un artefacto WebKit.

Clasificación: **VERIFIED como infraestructura BD-J/Poops**; **INVALID como evidencia directa de WebKit 13.02/13.52**. La presencia de APIs de buffer o de offsets de kernel no demuestra una primitive WebKit ni una relación con `ffs_mountfs`.

## BD-JB5: entradas concretas 13.52

En el commit `4c28ff2d36cf9cade6763f2a8b801c2219e951f5` de `Gezine/BD-JB5`, `payloads/poops/src/org/bdj/external/PS4_KernelOffset.java` contiene una entrada `addFirmwareOffsets("13.52", ...)` y una cadena larga de shellcode asociada a la clave `"13.52"`. El archivo es código Java de Poops/BD-J y kernel offsets/shellcode; no es WebKit ni un dump del módulo WebKit. La procedencia es pública y el commit está fechado 2026-08-05.

Esto sí aporta un artefacto específico 13.52 para BD-J/Poops, pero no permite localizar `libSceNKWebKit`, `CSSFontFace`, una vtable WebKit ni una primitive WebKit. Clasificación: **VERIFIED como soporte BD-J/Poops 13.52**; **INVALID como artefacto WebKit 13.52**.

## Historial completo de `ufm42/wobkot`

El historial público contiene, entre otros, `2f96abf1796bf05e913b298c9932284b6cac38d3` (2026-07-26, `full chain exploit added`), `bba4e8fdc5b59b781e0d26eea49bdbf8f748fe34` (2026-07-03, actualización de ROP/gadgets), `f0ab54dd8a8d1e8393ab1f7d6f2f3e010f1bec81` (2026-07-01, soporte 10.xx) y `6108c0507cda099ae03cfa3329129ecb16da4017` (2026-06-24, commit inicial). La rama pública sólo expone `main`.

La revisión de los archivos actuales no encontró tokens `13.52`, `13.50` o `13.02` en los ficheros WebKit consultados; los commits de `full chain` y ROP son de la línea antigua del exploit. No apareció un commit público que describa el workaround 13.52 ni un blob WebKit objetivo.

Clasificación: **VERIFIED como historial público**; **SOURCE_ONLY / UNVERIFIED_13_52** para el claim del workaround.

## `ufm42/wobkot`: límites del snapshot público

En el snapshot actual de `ufm42/wobkot`, `public/src/ps4/userland.js` contiene ramas de implementación para versiones históricas (condiciones para major 6, 9 y >=10) y usa campos CSSFontFace como `m_featureSettings`, `m_clients`, `m_wrapper`, `m_status` y `m_thread`. `public/src/ps4/constants.js` contiene tablas históricas de vtables/gadgets; no aparece una clave explícita `13.52`, `13.50` o `13.02` en los archivos consultados.

SHA-256 del snapshot auditado: `userland.js` `0d5fc478a1114a0a1514934ddd97b126d879a691fc872fbd921302a156a4dee8`; `constants.js` `52c6af4a7f75c87238345ad6f6e0761a04e3c54a052ed68a5363461a5a92ef72`. La estructura demuestra código de exploit userland real para versiones antiguas, pero no aporta el workaround 13.52.

Clasificación: **VERIFIED como código histórico**; **UNVERIFIED_13_52** para el claim atribuido a `ufm42`.

## Búsqueda directa en GitHub API

Las búsquedas públicas de repositorios con `CSSFontFace 13.52`, `PS4 WebKit 13.52` y `fontface 1352 PS4` no devolvieron repositorios adicionales mediante la API pública. Los candidatos identificados siguen siendo `ntfargo/CSSFontFace-Exploit`, sus forks, `ufm42/wobkot`, `ps3120/FontFace-Lapse` y `Gezine/BD-JB5`; ninguno aporta un módulo WebKit 13.02/13.52 verificable.

Clasificación: resultado negativo; no se eleva ningún claim a evidencia primaria.

## PSDevWiki — separación entre BD-J 13.02 y WebKit 13.52

La página pública `Vulnerabilities` separa explícitamente los rangos: BD-JB-13.00 aparece como `FW 13.00–13.02`; el workaround de path traversal BD-J aparece con rangos distintos; y el apartado WebKit lista CSSFontFace como `FW 6.00–11.50`. Por tanto, la tabla pública no presenta CSSFontFace como implementación verificada para PS4 13.02/13.52.

La misma página incluye otras entradas WebKit con rangos hipotéticos o de investigación, pero no añade un SPRX/SELF/ELF ni hashes de módulos 13.02/13.52. Esto refuerza que el claim de userland FontFace hasta 13.52 debe mantenerse como **SOURCE_ONLY / UNVERIFIED_13_52**, mientras que la separación BD-J 13.02 es una categoría independiente.

[25]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer wiki — Vulnerabilities"
