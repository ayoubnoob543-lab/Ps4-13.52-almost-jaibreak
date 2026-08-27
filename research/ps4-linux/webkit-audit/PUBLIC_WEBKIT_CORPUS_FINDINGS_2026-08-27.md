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
