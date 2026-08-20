# Búsqueda final dirigida de artefactos retail PS4 13.52

## Estado de partida

Se partió del commit `b95e9ec223bcccc57ef8be6795ae3a93318a24fb` y se revisaron primero los informes existentes. No se repitieron el smoke WPE 2.52.6 ni las auditorías públicas ya documentadas. El objetivo fue localizar al menos un artefacto retail 13.52 o metadatos primarios nuevos para `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, SELF/ELF relacionados o dumps NXDP/ORBISDMP/orbisstate.

## Vías nuevas examinadas

| Vía | Resultado | Clasificación |
|---|---|---|
| Variantes `SceNKWebKit`, `libSceWebkit2.sprx`, `libwebkit.sprx` en GitHub Code Search | Referencias históricas en scripts/Makefiles/stubs; ningún blob retail 13.52 | **UNVERIFIED/PORTABLE** |
| `NXDP`, `ORBISDMP`, `orbisstate` en GitHub Code Search | Herramientas/documentación genérica y repositorios no atribuibles a PS4 13.52; ningún dump verificable | **UNVERIFIED** |
| Releases/assets de PSFree, CSSFontFace y zecoxao | Sin releases/assets que contengan los módulos target | **VERIFIED_METADATA** |
| Reddit sobre WebKit userland hasta 13.52 | Afirma una workaround y enlaza publicaciones X; no contiene bytes, hashes, manifests ni dumps descargables | **UNVERIFIED/DOCUMENTED_ONLY** |
| ConsoleMods Getting Started | Confirma contexto público: 13.52 aparece como firmware no explotado y 13.00 como último firmware explotado; no contiene artefactos | **VERIFIED_METADATA** |
| Nombres alternativos `.sprx/.self/.elf/.bin/.decrypted` | No apareció un archivo target con procedencia 13.52 y hash reproducible | **MISSING** |

## Hallazgos

### Reddit: afirmación de userland, sin artefacto

La publicación [Reddit PS4/PS5 WebKit userland](https://www.reddit.com/r/ps4homebrew/comments/1vfbae9/ps4_and_ps5_webkit_userland_till_latest_firmwares/) atribuye a ufm42 una workaround para cambios que afectaron al WebKit anterior y afirma que el jailbreak continúa limitado a 13.00. El texto sólo enlaza publicaciones en X. No proporciona `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, un SELF/ELF, un manifest, SHA-256, Build ID o dump de crash.

Conclusión: es metadato contextual **UNVERIFIED/DOCUMENTED_ONLY**, no evidencia directa.

### ConsoleMods: estado público de firmware, sin artefacto

La guía [ConsoleMods PS4 Getting Started](https://consolemods.org/wiki/PS4:Getting_Started) identifica 13.52 como firmware más reciente no explotado y 13.00 como el más reciente explotado en el momento de la página. Sus secciones de métodos no publican los módulos ni dumps target.

Conclusión: **VERIFIED_METADATA** sobre el contexto de soporte público, pero no sobre bytes WebKit.

### Búsqueda de nombres alternativos

Las búsquedas exactas de `SceNKWebKit`, `libSceWebkit2.sprx`, `libwebkit.sprx`, `NXDP`, `ORBISDMP` y `orbisstate` devolvieron principalmente código histórico, stubs, herramientas de análisis o referencias genéricas. Ningún resultado proporcionó un artefacto descargable cuya procedencia 13.52 pudiera verificarse. Los resultados de `orbisstate` y `NXDP` no se promovieron por falta de atribución a la sesión/firmware target.

## Lo que permanece confirmado

| Elemento | Estado |
|---|---|
| WPE WebKit 2.52.6 en Linux x86_64 | **CONFIRMED/PASS**, pero no retail PS4 |
| Fuente OSS PS4 13.00 | **CONFIRMED/PUBLIC**, no exacta 13.52 |
| Nombres/relación de módulos WebKit PS4 | **DOCUMENTED_ONLY/PORTABLE** |
| `libkernel_sys_13.52.bin` | **CONFIRMED**, SHA-256 `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c` |
| `libSceNKWebKit.sprx` 13.52 | **MISSING** |
| `libkernel_web.sprx` 13.52 | **MISSING** |
| `libSceLibcInternal.sprx` 13.52 | **MISSING** |
| Build ID común | **MISSING** |
| GOT/imports/vtables/offsets 13.52 | **MISSING/UNVERIFIED** |
| NXDP/ORBISDMP/orbisstate target | **MISSING/UNVERIFIED** |

## Cobertura y bloqueo

La infraestructura estática y de laboratorio WPE permanece aproximadamente en **86%** según el estado del proyecto. La evidencia directa específica de PS4 13.52 no aumenta: permanece alrededor de **10–15% contextual/documental** y **0% para bytes de los tres módulos prioritarios**, Build ID común, GOT/vtables verificadas y dumps target.

El bloqueo principal es la ausencia de una fuente autorizada que publique o permita recuperar un módulo retail 13.52 con procedencia verificable. Las fuentes OSS Sony 13.00, WPE 2.52.6, scripts PSFree y afirmaciones de soporte no sustituyen esos bytes.

## Siguiente vía autorizada

La siguiente acción concreta de mayor valor es obtener un único módulo retail 13.52 desde una fuente autorizada o desde una sesión de depuración/backup del usuario que documente firmware, origen y hash. El análisis posterior debe ser estático: hash, formato ELF/SELF, cabeceras, segmentos, strings, imports y Build ID; no debe ejecutar exploits, payloads ni el módulo.

## Referencias

[1]: <https://www.reddit.com/r/ps4homebrew/comments/1vfbae9/ps4_and_ps5_webkit-userland-till-latest-firmwares/> "PS4 and PS5 WebKit userland till latest firmwares"
[2]: <https://consolemods.org/wiki/PS4:Getting_Started> "ConsoleMods PS4 Getting Started"
[3]: <https://www.playstation.com/en-us/oss/ps4/webkit/> "Sony PS4 WebKit OSS sources"
[4]: <https://github.com/kmeps4/PSFree/blob/main/send.mjs> "PSFree module dumper documentation"
[5]: <https://github.com/ntfargo/CSSFontFace-Exploit> "CSSFontFace exploit repository"
