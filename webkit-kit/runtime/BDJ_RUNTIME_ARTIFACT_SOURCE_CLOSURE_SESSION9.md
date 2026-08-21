# Cierre de fuentes de artefactos BD-J 13.52 — Sesión 9

## Alcance

Esta sesión buscó únicamente una fuente legítima y reproducible de `app0/bdjstack/bdjstack.jar`, `app0/bdjstack/lib/rt.jar`, `sunjce_provider.jar`, `enhanced-stubs.zip` y metadata JVM/BD-J de PS4 13.52. No se descargaron PUPs, firmware propietario, discos ni dumps; no se ejecutaron JAR/ELF/BIN, exploits, payloads ni código contra hardware.

## Hallazgos nuevos

La fuente pública atribuida a ASaudidos, reproducida por [Thread Reader][1], afirma que una cadena userland BD-J funciona en 12.02, 13.02, 13.50 y 13.52, y que Sony eliminó el grant original de `sunjce_provider.jar` en una actualización reciente, mientras la vulnerabilidad utilizada por esa cadena sería distinta. La misma publicación afirma ejecución nativa dentro del proceso BD-J, pero no proporciona archivos, hashes, clases, métodos, símbolos, diffs ni un repositorio del runtime.

El estado comunitario de [GBAtemp][2] enumera “BD-JB: 13.50 (Gezine unreleased patched in 13.52)” y conserva la ruta histórica `file:///app0/bdjstack/lib/ext`. Es una referencia de estado y ruta, no una fuente de bytes 13.52.

Estas dos fuentes son evidencia documental nueva sobre afirmaciones y contexto, pero no convierten ningún artefacto en disponible ni verificable.

## Disponibilidad efectiva

| Artefacto | Estado local | Fuente pública legítima identificada | Hash 13.52 | Clasificación |
|---|---|---|---|---|
| `app0/bdjstack/bdjstack.jar` | Ausente | Ruta documentada por BlueLoader/BD-JB | Ninguno | **BLOCKED** |
| `app0/bdjstack/lib/rt.jar` | Ausente | Ruta documentada por BlueLoader/BD-JB | Ninguno | **BLOCKED** |
| `sunjce_provider.jar` | Ausente | Sólo afirmación pública de cambio/eliminación | Ninguno | **STRONG_INDIRECT** para la afirmación; **BLOCKED** para bytes |
| `enhanced-stubs.zip` | Ausente | Dependencia de build BD-JB/BDJ-SDK | Ninguno | **BLOCKED** |
| Librería JVM/BD-J nativa | Ausente | No se identificó fuente pública que la publique | Ninguno | **BLOCKED** |
| Manifest de procedencia 13.52 | Ausente | No localizado | Ninguno | **BLOCKED** |

La auditoría local de `/home/ubuntu`, `/tmp` y los workspaces de investigación no encontró ninguno de los nombres exactos, archivos comprimidos que los contengan o snapshots de filesystem BD-J. La rama ya contenía el informe de la sesión 8 y la documentación de herramientas; no se encontró un artefacto nuevo durante esta sesión.

## Qué puede confirmarse

**CONFIRMED:** las rutas esperadas de los JARs son conocidas por documentación pública de BD-JB/BlueLoader; BDJ-SDK y `ps4-payload-dev/sdk` son herramientas, no copias del runtime retail; el repositorio público de TheOfficialFloW no ofrece releases binarias del runtime.

**STRONG_INDIRECT:** existe una afirmación pública atribuida a ASaudidos de compatibilidad userland con 13.52 y de que el grant original de `sunjce_provider.jar` fue eliminado; la afirmación dice que la cadena usada sería distinta y no parcheada.

**UNVERIFIED:** qué clase/método implementa la cadena 13.52, si `rt.jar`/`bdjstack.jar` cambiaron, y si la ejecución nativa declarada puede conectarse a un loader externo.

**BLOCKED:** comparación estática real 13.50→13.52, porque no hay bytes ni manifest de procedencia.

## Único bloqueo restante

El único bloqueo de evidencia es obtener legítimamente una copia o snapshot verificable de los componentes del runtime 13.52. El mínimo práctico es `bdjstack.jar` y `rt.jar` de la misma build, con ruta, tamaño y SHA-256; para resolver la frontera Java→native usermode se requiere además metadata o bytes de la JVM/BD-J nativa y un manifest de procedencia. No existe una vía pública accesible en el corpus actual que proporcione esos bytes sin una fuente externa autorizada.

## Referencias

[1]: https://twitter-thread.com/t/2081061116025692373 — Thread Reader de la publicación de @ASaudidos del 25-07-2026.

[2]: https://gbatemp.net/threads/ps4-exploit-guide.497858/page-1392 — PS4 Exploit Guide, estado comunitario de BD-JB 13.50/13.52.

[3]: https://github.com/kimariin/BlueLoader — BlueLoader, rutas históricas y herramienta de extracción documentada.

[4]: https://github.com/ayasns/BD-JB-1250 — BD-JB-1250, dependencias `rt.jar`/`bdjstack.jar`.

[5]: https://github.com/john-tornblom/bdj-sdk — BDJ-SDK, herramientas de build.
