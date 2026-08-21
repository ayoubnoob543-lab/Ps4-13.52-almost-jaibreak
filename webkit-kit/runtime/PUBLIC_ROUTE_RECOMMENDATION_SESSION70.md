# Recomendación de ruta para obtener evidencia WebKit 13.52 — sesión 70

## Fuentes públicas revisadas

1. **MODDED WARFARE, vídeo del 4 de agosto de 2026**: https://www.youtube.com/watch?v=mWX9uj0mKIQ. El título y la descripción afirman que existen bugs de userland WebKit para PS4 hasta 13.52 y enlazan al repositorio `ntfargo/CSSFontFace-Exploit`, además de referencias a publicaciones X. La fuente demuestra una afirmación pública y una ruta documental hacia un repositorio, pero no aporta por sí sola un módulo retail, hash de `libSceNKWebKit.sprx`, offsets ni una primitive reproducible en nuestro entorno. Clasificación: `DOCUMENTED_ONLY`.

2. **Vídeo de TheeEvolutionYT del 23 de julio de 2026**: https://www.youtube.com/watch?v=ZG-SGV4c-kQ. El título y la descripción afirman que un bug BD-J userland afecta a 13.52 y que falta un bug de kernel estable para un jailbreak completo. Esto confirma una afirmación pública sobre una fase userland, no la disponibilidad de los bytes del runtime ni la primitive concreta. Clasificación: `DOCUMENTED_ONLY`.

3. **Feyzee61/psfree_lapse**: https://github.com/Feyzee61/psfree_lapse. El README identifica soporte para PS4 7.00–9.60, no 13.52, y declara que los binarios de payload se excluyen. Es útil como precedente de cómo una implementación pública separa WebKit, kernel y payload, pero no es una fuente de WebKit 13.52. Clasificación: `HISTORICAL_ONLY` para nuestro objetivo.

4. **Reddit, “Updating a PS4 4.73 to 13.52 so you don't have to”**: https://www.reddit.com/r/ps4homebrew/comments/1vk06yc/updating_a_ps4_473_to_13_52_so_you_dont_have_to/. La página contiene comentarios sobre configuraciones de reversión y pruebas entre firmwares, pero no presenta un artefacto WebKit 13.52 verificable. Clasificación: `DOCUMENTED_ONLY`/`UNVERIFIED`.

## Recomendación

La ruta más rápida y legítima no es intentar obtener claves desde los PUP raw ni ejecutar payloads. Es solicitar o localizar un artefacto público ya divulgado con procedencia técnica suficiente: `libSceNKWebKit.sprx` 13.52, un dump parcial autorizado que lo contenga, o una cabecera/tabla `.PUP.dec` obtenida mediante un método legítimo. El primer paso de validación debe ser SHA-256, arquitectura, formato, Build ID, tamaño, procedencia y cadena de custodia; sólo después se ejecutaría el correlador estático.

El repositorio CSSFontFace enlazado por la fuente pública puede ser útil como **referencia de código y testcase**, pero no debe tratarse como evidencia de que el binario retail 13.52 contiene la misma implementación. El fork PSFree revisado tampoco debe usarse como fuente para 13.52, porque declara soporte 7.00–9.60.

## Ranking de rutas

| Ruta | Valor | Riesgo de falso positivo | Dependencia |
|---|---|---:|---|
| Artefacto retail público con hash/procedencia | Muy alto | Bajo | Que exista y sea verificable |
| Extracción autorizada de una cabecera/tabla `.PUP.dec` | Muy alto | Bajo | Acceso legítimo a la salida del sistema/oracle |
| Repositorio de exploit/testcase como referencia estructural | Medio | Alto | No demuestra equivalencia retail |
| Inferir claves/offsets desde bytes raw | Bajo | Muy alto | No recomendado |
| Copiar WebKitGTK/WPE al objetivo PS4 | Bajo para retail | Muy alto | ABI/sysroot/backend ausentes |

## Conclusión

La evidencia pública nueva mejora la ruta documental hacia CSSFontFace/WebKit userland 13.52, pero no cierra el puente hacia el runtime retail. El artefacto mínimo que debemos conseguir es una muestra binaria o metadata descifrada con procedencia verificable; mientras no exista, el laboratorio y el correlador pueden prepararse, pero la presencia de una vulnerabilidad concreta en 13.52 queda `UNVERIFIED`.

## Búsqueda nueva sin artefacto verificable

Se realizó una búsqueda separada por `libSceNKWebKit.sprx`, hashes/Build IDs y extracción de WebKit 13.52. Los resultados nuevos fueron principalmente páginas editoriales, vídeos, Reddit y posts de redes sociales que repiten afirmaciones de userland/jailbreak; no apareció un archivo binario, hash retail, Build ID ni snapshot verificable. `PSDevWiki/Bugs` es una referencia documental útil, pero no constituye por sí sola un artefacto de 13.52. Los repositorios derivados de PSFree encontrados declaran rangos antiguos o no aportan el módulo retail, por lo que quedan apartados y no se volverán a usar como fuente principal.

La lectura adicional de `PSDevWiki/Bugs` y `Feyzee61/ps4jb` no produjo un módulo retail 13.52 ni hashes/Build IDs de `libSceNKWebKit`. `PSDevWiki/Bugs` contiene una clasificación documental de superficies y rangos, pero las entradas no equivalen a bytes del firmware. `Feyzee61/ps4jb` declara soporte 5.05, 6.72 y 7.00–9.60; queda explícitamente descartado como fuente de 13.52. Estas URLs quedan marcadas como revisadas y no se reutilizarán en la siguiente pasada salvo que aparezca un enlace nuevo dentro de ellas.

## Exploración pública autónoma adicional

Una búsqueda nueva encontró un anuncio de Facebook titulado `If you need a 13.52 DevKit pup for PlayStation 4 hit me up` (https://www.facebook.com/MrAndrew2007/posts/if-you-need-a-1352-devkit-pup-for-playstation-4-hit-me-up-this-is-not-my-pup-fil/4344670032516286/). El resultado sólo muestra un anuncio y no aporta un archivo descargable, hash, procedencia, manifest ni acceso verificable al DevKit PUP; por tanto se clasifica `UNVERIFIED` y no se descarga ni se trata como evidencia. Los demás resultados fueron debates, guías o páginas editoriales sin módulos `libSceNKWebKit` ni hashes atribuibles a 13.52. Esta URL queda registrada como nueva y no se repetirá salvo que aparezca un archivo público verificable asociado.

La extracción directa del anuncio de Andrew Marques devuelve exactamente: `If you need a 13.52 DevKit pup for PlayStation 4 hit me up. THIS IS NOT MY PUP FILE, it is someone else’s file I’m partnering up with.` La publicación está fechada el 3 de agosto y sólo muestra texto, reacciones y una compartición; no contiene enlace de descarga ni hash. Clasificación final: `DOCUMENTED_ONLY` para la existencia de una afirmación pública y `UNVERIFIED` para la existencia/procedencia del archivo. No se descargó nada ni se contactó con el autor.

## Archivos públicos adicionales: resultado

`PSDevWiki/System_Software` documenta la nomenclatura de PUP, los tipos retail/TestKit/DevKit y la estructura de URLs; no aporta por sí sola el módulo WebKit ni una extracción descifrada. `darthsternie.net/ps4-rare-files/` sólo lista `PS4-DEVKIT-TRIAL-300.PUP` (MD5 `197730abd3d952073c558b1870c30f3e`, 276 MB) y archivos antiguos de controlador; no es 13.52. `darthsternie.net/ps4-firmwares/` lista un PUP retail 13.50 de 480 MB con MD5 `1b27ba86ee1d9c95cc4ce26da9a18d39`, pero no muestra un PUP 13.52 en el extracto disponible. Esto puede servir como referencia pública de 13.50, no como sustituto del WebKit retail 13.52 ni como evidencia de sus bytes internos. Clasificación: `DIRECT_13.50` para el listado/hash publicado de 13.50, `HISTORICAL_ONLY` para el DevKit Trial 3.00 y `UNVERIFIED` para cualquier inferencia hacia 13.52.

## Herramientas y archivos descifrados: nueva comprobación

`PFU-PupFileUnpacker` (https://github.com/seregonwar/PFU-PupFileUnpacker) puede desempaquetar metadata y contenedores PUP, pero su propio README declara que no puede extraer correctamente todos los archivos cifrados y que faltan las claves Sony; por tanto no resuelve el bloqueo de 13.52. `idc/ps4-pup_decrypt` (https://github.com/idc/ps4-pup_decrypt/) confirma documentalmente que la operación de descifrado se realiza invocando el kernel de una PS4 y genera `PS4UPDATE*.PUP.dec`; no es un descifrador offline y no se ejecutó. `darthsternie.net/ps4-decrypted-firmwares/` ofrece índices MEGA de firmwares descifrados oficiales, DevKit y TestKit, pero no expone en la página un listado verificable de 13.52 ni hashes individuales. Por seguridad y trazabilidad, no se descargaron archivos de MEGA ni se asumió que el índice contiene 13.52. Clasificación: `DIRECT_DOCUMENTATION` para el mecanismo de PFU/oracle, `UNVERIFIED` para la existencia de una copia 13.52 en esos índices.

## Búsqueda adicional del índice descifrado

Las búsquedas nuevas siguen devolviendo el índice `darthsternie.net/ps4-decrypted-firmwares/` sin nombres ni hashes de archivos 13.52 expuestos en la página. El resultado nuevo `andy-man/ps4-pup-decrypt` describe un payload para invocar el descifrado en la PS4, igual que la familia `idc`, y no proporciona un descifrado offline. Los vídeos que afirman un bug BD-J/userland 13.52 son evidencia editorial únicamente; no aportan módulos, hashes ni Build IDs. Se mantiene la clasificación `DOCUMENTED_ONLY`/`UNVERIFIED` y no se descargan payloads ni se ejecutan binarios.

## Internet Archive: comprobación adicional

La búsqueda pública encontró los directorios `PS4-System-Firmwares` y `PS4-Recovery-Firmwares` en Internet Archive, con listados antiguos y archivos PUP retail, pero no mostró una entrada `13.52`, un `.PUP.dec`, `libSceNKWebKit.sprx` ni un hash/Build ID de WebKit. Los resultados de Reddit y YouTube repiten afirmaciones de userland 13.52, sin artefacto técnico. Se clasifica el directorio como `DOCUMENTED_ONLY` para la existencia de un archivo histórico y `UNVERIFIED` para cualquier disponibilidad de 13.52. No se descargó ningún archivo.

## PSDevWiki WebKit Bugs y Reddit: detalle nuevo

`PSDevWiki/WebKit_Bugs` mantiene tres entradas con rango editorial `?6.00-13.52?`: `JSC::JSCell::toX`, `JSC MarkedVector` y `WebCore::CloneSerializer/Deserializer objectPool`. La propia notación con signos de interrogación expresa incertidumbre del rango; la página no aporta `libSceNKWebKit.sprx` 13.52, hash, Build ID ni bytes retail. Clasificación: `DOCUMENTED_ONLY`/`UNVERIFIED` para PS4 13.52.

La publicación de Reddit `PS4 and PS5 WebKit userland till latest firmwares 13.52 and 13.60 respectively` atribuye a `ufm42` un workaround para cambios que rompieron WebKit hasta 11.02 y enlaza posts de X, pero los comentarios indican que los enlaces estaban caídos y que las actualizaciones 13.52 aún no se habían publicado. Otros comentarios distinguen explícitamente userland de jailbreak y dicen que 13.52 no tiene homebrew sin kernel. Esto aporta contexto comunitario, no un artefacto ni una primitive reproducible. Clasificación: `DOCUMENTED_ONLY` para las afirmaciones y `UNVERIFIED` para la implementación 13.52.

## CSSFontFace y ufm42: alcance documentado

El artículo de OneJailbreak (https://onejailbreak.com/blog/cssfontface-webkit-exploit-ps4-ps5/) afirma que el repositorio CSSFontFace lista presencia de la vulnerabilidad en PS4 6.00–13.52, pero también dice que el código público fue construido/probado en PS4 9.00 y que la cadena actual sólo es utilizable en PS4 6.00–11.50; además explica que cambios de WebKit desde 11.5x modificaron el manejo de CSSFontFace y eliminaron la primitive de lectura/escritura usada por esa implementación. Esto es una pista fuerte sobre el bloqueo estructural posterior a 11.5x, pero no prueba que el workaround de ufm42 esté publicado ni que sea compatible con 13.52. Clasificación: `STRONG_INDIRECT_13.52` para la afirmación de que se requiere una variante distinta; `UNVERIFIED` para una implementation 13.52.

Logic-Sunrise reproduce la misma distinción: CSSFontFace se describe como presente 6.00–13.52, pero la cadena publicada sólo llega a 11.02 y menciona `m_propertiesOrCSSConnection` como cambio posterior que rompe la primitive `m_featureSettings`. Es una fuente secundaria y no aporta binarios retail, hash ni Build ID. Clasificación: `DOCUMENTED_ONLY`/`STRONG_INDIRECT_13.52`.

El perfil de Abkarino sólo muestra publicaciones históricas generales y no contiene el código ni el artefacto 13.52 atribuido a ufm42. Clasificación: `DOCUMENTED_ONLY`.
