# Búsqueda independiente Orbis 13.02/13.04 y Celsius/Jordy

Punto de partida: rama `research/webkit-disk-1302`, commit `d42bf9c`.

## Alcance A: Orbis 13.02/13.04

Buscar únicamente dumps, proyectos IDA/Ghidra/Binary Ninja, pseudocódigo, disassembly, call graphs o análisis de kernel que permitan identificar `ffs_mountfs`, `ffs_reload` o la función situada en `0x001512A7`. No se recopilarán tablas genéricas de offsets.

## Alcance B: Celsius/Jordy

Buscar únicamente copias históricas del bootstrap/PoC, imágenes UFS/FFS y artefactos atribuidos a autores originales, incluyendo material eliminado, mirrors, commits antiguos, gists, pastes y archivos enlazados desde publicaciones originales. No se reauditará `ps4-suid-scanner`.

## Criterio de independencia

Un fork, espejo o publicación que conserve el mismo hash, commit, texto o blob se clasificará como derivado, no como corroboración independiente. Las afirmaciones sin artefacto serán `SOURCE_ONLY`; los bytes, hashes o proyectos analizables se clasificarán por separado de sus claims.

## Registro

Cada hallazgo se documentará como: artefacto | URL/origen | fecha | hash | firmware | relación con Celsius | pieza que aporta | procedencia.

## Búsqueda B: fuentes públicas relacionadas

| Artefacto | URL/origen | Fecha | Hash | Firmware | Relación con Celsius | Pieza que aporta | Procedencia |
|---|---|---:|---|---|---|---|---|
| `Feyzee61/ps4jb` | https://github.com/Feyzee61/ps4jb | 2026-02-24 | No se descargó un blob nuevo | 5.05–9.60 | No implementa Celsius; sus puentes `kread`/`kwrite` pertenecen a PSFree/Lapse | Referencia histórica de WebKit y R/W separado; no bootstrap Jordy ni 13.02 | Proyecto derivado/consolidado de cadenas antiguas; **VERIFIED en su propio alcance, INVALID como PoC Celsius** |
| Publicación Reddit de WebKit 13.00 | https://www.reddit.com/r/ps4homebrew/comments/1vy0xhg/ps4_1300_webkit_jailbreak_release/ | 2026-08-25 según la página | N/A | 13.00 | Menciona “Jordy's AI WebKit” y enlaza `raw-game.com/zrm/`; no menciona implementación Celsius ni imagen UFS | Confirma un entrypoint WebKit público para 13.00, pero no la transición a mount/FFS | **SOURCE_ONLY** para Jordy; no es evidencia de Celsius |
| Publicación Instagram sobre Celsius | https://www.instagram.com/reel/Da_MVTKJupu/ | 2026-07-19 | N/A | Afirma 13.02–13.04 en PS4 y 12.70 en PS5 | Repite el claim de firmware y el requisito de USB, pero no adjunta PoC, imagen, hash, código o bootstrap | Sólo metadata pública del claim | Fuente secundaria; **SOURCE_ONLY** |
| Perfil de Dr.Yenyen | https://github.com/DrYenyen | Perfil consultado 2026-08-27 | N/A | No específico | No contiene repositorio Celsius/Jordy ni artefacto FFS visible | Sólo identifica repositorios generales del autor | **VERIFIED como perfil; sin artefacto relevante** |

`Feyzee61/ps4jb` es la pista más cercana a una implementación pública de WebKit→kernel R/W, pero sus propios metadatos limitan el soporte a 5.05–9.60 y describen PSFree/Lapse, no Celsius. No debe emplearse como sustituto del bootstrap Jordy para 13.02. Las fuentes Reddit e Instagram son claims o entrypoints secundarios sin artefacto de transición.

## Búsqueda A: resultado provisional

`Al-Azif/ps4-re-utilities` (https://github.com/Al-Azif/ps4-re-utilities, creado 2025-12-04, un commit visible) contiene herramientas para separar el kernel FreeBSD de un Kernel ELF `80010002` y preparar el archivo para depuradores. Es infraestructura de análisis, no un dump 13.02/13.04 y no incluye `ffs_mountfs`, `ffs_reload` ni una referencia a `0x001512A7`. El artículo histórico de CTurt (https://cturt.github.io/ps4-3.html, 2015-12-17) documenta análisis de kernel y WebKit en firmwares antiguos, pero no aporta un artefacto Orbis 13.02/13.04 ni una relación con Celsius. Los resultados Reddit/YouTube recientes son secundarios y no contienen bytes ni proyectos RE del kernel.
