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

## Auditoría A ampliada: proyectos de análisis y SDK

| Artefacto | URL/origen | Fecha | Hash | Firmware | Relación con Celsius | Pieza que aporta | Procedencia |
|---|---|---:|---|---|---|---|---|
| `Al-Azif/ps4-re-utilities` | https://github.com/Al-Azif/ps4-re-utilities | 2025-12-04; un commit visible | No se descargó un kernel | Afirma compatibilidad de herramientas hasta 13.50 | Ninguna directa; no incluye `ffs_mountfs` ni bytes Orbis objetivo | `split_kernel.py` puede separar el FreeBSD kernel de un Kernel ELF `80010002` para análisis offline | Fuente primaria de herramienta; **VERIFIED como utilidad, sin dump 13.02/13.04** |
| `OpenOrbis-PS4-Toolchain` | https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain | Creado 2020-05-11; 558 commits visibles | N/A | SDK general | No contiene kernel retail ni Celsius | Headers, stubs, documentación y scripts de ELF; el README dice que el repo evita incluir binarios pesados | Fuente primaria de toolchain; **VERIFIED como SDK, no artefacto Orbis** |
| OpenOrbis SDK en ConsoleMods | https://consolemods.org/wiki/PS4:OpenOrbis_SDK | Editado 2025-01-27 | N/A | Documenta principalmente 1.05–9.00 en PS4LibDoc | No contiene Celsius ni análisis 13.02 | Referencia secundaria del ecosistema SDK/Mira | **CORROBORATED como documentación; no evidencia de kernel 13.02** |
| PS4 Module Loader / IDA | https://www.psxhax.com/threads/ps4-module-loader-for-ida-userland-modules-by-socraticbliss.6945/ | 2019-07-30 | N/A | Histórico | No implementa Celsius; sirve para módulos userland y kernel antiguos | Cargador IDA y contexto de reversing, sin proyecto de kernel Orbis 13.02/13.04 | Fuente secundaria que enlaza descargas restringidas; **SOURCE_ONLY para artefactos no recuperados** |
| CTurt, “Hacking the PS4, part 3” | https://cturt.github.io/ps4-3.html | 2015-12-17 | N/A | Firmwares antiguos | No es Celsius | Metodología histórica de WebKit, ROP, sysctl y análisis de kernel | Fuente primaria histórica; **VERIFIED en su alcance, no transferible a 13.02** |

Conclusión A provisional: ningún resultado contiene bytes, pseudocódigo, call graph o proyecto RE de Orbis 13.02/13.04 que permita identificar `ffs_mountfs`, `ffs_reload` o la función situada en `0x001512A7`. Los SDK y loaders encontrados son infraestructura, no el artefacto objetivo.

## Búsqueda B ampliada: cadena de referencias públicas

| Artefacto | URL/origen | Fecha | Hash | Firmware | Relación con Celsius | Pieza que aporta | Procedencia |
|---|---|---:|---|---|---|---|---|
| Artículo GameGaz sobre Celsius | https://gamegaz.com/2026071945823/ | 2026-07-19; cita post de Dr.Yenyen del 2026-07-18 | N/A | Afirma PS4 hasta 13.04 y PS5 hasta 12.70 | Es la referencia secundaria más detallada: menciona `ffs_mount`, heap overflow, USB 3.0/HDD 250 GB+, Vue/BD-J y parche 13.50 | Requisitos declarados y fecha del primer anuncio público citado; no PoC ni imagen | **SOURCE_ONLY**; la propia página advierte que no estaba en fase práctica |
| Post de Dr.Yenyen citado por GameGaz | https://x.com/calmboy2019/status/2078549759460094065 | 2026-07-18 | N/A | Afirma PS4 hasta 13.04 y PS5 hasta 12.70 | Fuente primaria del anuncio público y del nombre Celsius, pero el texto sólo pide paciencia y no adjunta implementación | Fecha y claim original; no transición técnica | **SOURCE_ONLY** para la existencia de artefactos no publicados |
| Post de GAMERZ 56K | https://www.youtube.com/post/UgkxE2BPYs9Rf7TJgKq8GqnZlTh-kOpDU15F | 2026-07-26 aprox. | N/A | Repite PS4 hasta 13.04, incluyendo 13.02 | Añade que se recomienda USB de 320/500 GB y que el timing de inserción sería crítico, pero no enlaza código o imagen | Hipótesis operativa no reproducible | **SOURCE_ONLY / rumor secundario** |
| Entrada Wikova | https://wikova.com/wiki/DQm4J1HU | Actualizada 2026-08-10 | N/A | Resume 13.02–13.04 | Reutiliza el relato general y cita GameGaz entre sus fuentes; no aporta artefacto independiente | Sólo índice narrativo y referencias | **DERIVED**, no corroboración independiente |

El anuncio de Dr.Yenyen enlazado por GameGaz es la primera fuente pública localizada que da nombre y rango de firmware, pero no entrega la PoC. GameGaz aporta requisitos declarados y una advertencia explícita de que Celsius aún no estaba en fase práctica. Los posts de YouTube y Wikova son derivados; ninguno cierra la transición `WebKit/Jordy → mount → FFS → corrupción → primitive`.

## Evidencia visual del anuncio primario de Dr.Yenyen

La revisión directa de `https://x.com/calmboy2019/status/2078549759460094065` confirmó que el post del 18 de julio de 2026 contiene tres imágenes adjuntas. El texto visible dice: “Here you go. You’ll still have to be patient but this is what you might get. It’s named ‘Celsius’ … Up to 13.04 PS4 and 12.70 PS5.” Las imágenes muestran una conversación/captura de carácter declarativo sobre el descubrimiento atribuido a bollars y el rango afirmado; no muestran código fuente, pseudocódigo, bytes, hash, URL de descarga, imagen UFS/FFS, argumentos de montaje ni una secuencia de kernel R/W. La página también muestra respuestas de Dr.Yenyen y Echo Stretch, pero ninguna adjunta un artefacto técnico. Clasificación: anuncio primario del nombre y rango **SOURCE_ONLY** para la PoC no publicada; evidencia visual insuficiente para reconstruir la cadena.

Imágenes referenciadas por X: `https://pbs.twimg.com/media/HNh9-w8WgAAmTFd?format=webp&name=medium`, `https://pbs.twimg.com/media/HNh9_EUWEAA3fwf?format=webp&name=medium` y `https://pbs.twimg.com/media/HNh9_YGWgAANBEm?format=webp&name=medium`. No se descargaron como artefactos ejecutables ni se trató su contenido como prueba binaria.

Referencia: [Dr.Yenyen, post primario de Celsius, 18-07-2026](https://x.com/calmboy2019/status/2078549759460094065).

## Búsqueda de aliases del autor técnico

Las consultas públicas para `bollars PS4 exploit`, `bollars ffs_mount GitHub` y variantes ortográficas como `bollards Celsius PS4` no localizaron un perfil técnico, repositorio, gist, paste, dump o PoC atribuible directamente a bollars. Los resultados relevantes se reducen al repositorio del scanner —excluido de esta fase por estar agotado—, material histórico general de PS4 y resultados no relacionados. Clasificación: **búsqueda negativa**, sin artefacto independiente recuperado.

## Búsqueda global de commits

La búsqueda de commits para `ffs_mountfs` devuelve principalmente el historial de FreeBSD y repositorios que copian esos commits, por ejemplo cambios antiguos de locking o firmas de funciones. No aparece una implementación de Orbis, Celsius o una adaptación PS4. Las consultas `Celsius PS4` y `Jordy PS4 WebKit` no produjeron commits externos relevantes; las coincidencias útiles se limitaron al material ya conocido. No se consideraron los commits FreeBSD como evidencia de que Orbis conserve la misma ruta. Resultado: **sin artefacto nuevo**.

### Transcripción de la imagen primaria 2

La segunda imagen adjunta al post de Dr.Yenyen muestra un mensaje suyo que afirma: “There's a kernel exploit that's been posted around a bit. And it's difficult to deal with. Don't etawen don't ask in the servers about who and when will work on it. Don't annoy people. I've already tested it a bit. It has been named ‘Celsius’. It is for up to 13.04 on PS4 (yes yes 13.02 included) and up to 12.70 on PS5. It was patched on 13.50 PS4 and 13.00 PS5. No guarantee that it will work out or if it does that it will be easily usable. Again patched on 13.50 and 13.00 means as of those firmwares and above it no longer works. It's not Gezine's exploit btw. It requires a USB 3.0 250GB or above drive to trigger via extended storage. 250GB drives aren't all made the same so an actual recommendation for users is to get 320GB or 500GB to avoid issues or take your chances with 250GB drives. (And I mean get only when it gets announced as working)”.

Esta imagen aporta el dato más explícito localizado sobre requisitos operativos declarados y sobre una prueba informal (“I've already tested it a bit”), pero no contiene código, imagen UFS, hash, argumentos de `mount`, dirección, primitive de corrupción ni log reproducible. Se clasifica como **SOURCE_ONLY** para la implementación y como **HYPOTHESIS** para los detalles operativos no acompañados de artefacto.

Fuente de imagen: `https://pbs.twimg.com/media/HNh9_EUWEAA3fwf?format=webp&name=medium`; SHA-256 local del WebP: `cd6860811c80ab7c0f73a8c189ecad0c187eb41a751d4815fa6efba2e8f723b6`.

### Transcripción de la imagen primaria 3

La tercera imagen adjunta dice que los userlands esperados en PS4 son **Vue y BD-J**, y en PS5 **Y2JB y BD-J**. Añade que la ejecución no tarda 50 minutos, pero requiere conectar el USB en el momento correcto y que el éxito depende del timing. No proporciona nombres de archivos, código, parámetros de montaje, imagen UFS, dirección o primitive de kernel R/W. Clasificación: **SOURCE_ONLY** para la elección de entrypoints y **HYPOTHESIS** para el detalle del timing hasta que exista una PoC pública.

Fuente de imagen: `https://pbs.twimg.com/media/HNh9_YGWgAANBEm?format=webp&name=medium`; SHA-256 local del WebP: `767f2ce350dc97ed90298cd3de70aa5effe521d399d959658be0442b9ed14187`.

## Búsqueda por frases distintivas del anuncio

Las búsquedas textuales de `“250GB drives aren't all made the same”`, `“The expected userlands” “Vue and BD-J”` y `“It has been named Celsius” PS4` no devolvieron copias indexadas adicionales. No se localizó un hilo original alternativo, archivo enlazado, PoC, bootstrap o imagen UFS fuera de las referencias ya documentadas. Resultado: **búsqueda negativa**, sin corroboración independiente nueva.

## Búsqueda global de código fuera del scanner

La búsqueda de código para `Celsius`, `ffs_mount` y `Jordy`, excluyendo `adri22235/ps4-suid-scanner`, no encontró una PoC PS4, bootstrap, imagen UFS/FFS ni implementación Orbis. Las coincidencias de `ffs_mount` corresponden a FreeBSD/NetBSD, GRUB, SPIFFS u otros sistemas no relacionados; no son evidencia de Celsius. Las coincidencias de `Celsius`/`Jordy` recuperadas fueron documentación secundaria o proyectos sin relación técnica con la cadena. Se conserva el resultado bruto en `upstream/adri-suid-history/full-stage2/celsius_global_code_search.txt`. Clasificación: **búsqueda negativa**, sin artefacto independiente nuevo.

## Pista de mirrors: earthonion

Una referencia secundaria indica que repositorios retirados del GitHub de `earthonion` fueron re-subidos a `https://git.earthonion.com/earthonion`. La página pública del mirror muestra 45 repositorios, entre ellos `elfldr-autoldr`, `install_y2jb`, `ddd_pair_dump`, `sponsorblock-ps4-installer` y `ps4-enter-idu`, principalmente PS5/BD-drive/loader y utilidades generales. La revisión visible no muestra repositorio llamado Celsius, `ffs_mount`, UFS/FFS, Jordy PS4 o kernel Orbis 13.02/13.04. La pista merece conservarse como posible mirror histórico, pero hasta inspeccionar los árboles y commits concretos no es evidencia de una PoC Celsius. Clasificación: **SOURCE_ONLY / candidato de búsqueda**, sin artefacto técnico confirmado.

## Inventario adicional del mirror earthonion

Las páginas 2 y 3 del mirror público muestran repositorios que sí justifican una inspección focalizada: `vue-after-free`, `vue-mitm-poc`, `ps4debugportal` y `mkufs2`. También aparecen `np-fake-signin`, `micropython-for-ps4` y `netflix-n-hack`, pero no están vinculados por nombre a Celsius. El mirror indica que los repositorios fueron re-subidos/reconstruidos el 30 de abril de 2026, por lo que su fecha de mirror no equivale necesariamente a la fecha de origen. Hasta leer sus árboles, commits y hashes, se clasifican como **SOURCE_ONLY / candidatos de búsqueda**. No se debe inferir que `vue-after-free` o `mkufs2` contengan la cadena Celsius sólo por el nombre.

Fuente: [mirror público de earthonion, página 2](https://git.etawen.dev/earthonion?page=2&sort=recentupdate&q=&tab=repositories) y [página 3](https://git.etawen.dev/earthonion?page=3&sort=recentupdate&q=&tab=repositories).

## Artefacto nuevo: `vue-after-free` en mirror earthonion

El árbol público `https://git.etawen.dev/earthonion/vue-after-free` contiene 407 commits, 6 ramas y 6 tags visibles. Su README declara que el userland Vue cubre 5.05–13.04, pero también dice expresamente que los archivos del repositorio sólo permiten jailbreak hasta 13.00 porque Lapse llega a 12.02 y Netctrl a 13.00. Esto separa el alcance del userland de la cobertura del kernel.

El archivo `src/download0/kernel.ts` se identifica como **“PS4 Kernel Offsets for Lapse exploit”** y atribuye su fuente a `Helloyunho/yarpe`. Incluye `kpatch_mmap_offsets` con una entrada para 13.02 (`0x1fa78a`, `0x1fa78d`) y hace que 13.04 use la clave 13.02. Sin embargo, la tabla de offsets de kernel termina en `offset_ps4_12_50`, comentada como “AND 12.52, 13.00”; no existe objeto 13.02 ni 13.04. Esa entrada de mmap es un parche/consumidor de offsets, no una primitive Celsius ni evidencia de `ffs_mountfs`.

El archivo `src/download0/lapse.ts` contiene implementaciones de Lapse, filtrado de direcciones mediante AIO y una primitive IPv6 auxiliar. La auxiliar `ipv6_kernel_rw` exige como entradas `ofiles`, `kread8` y `kwrite8` ya existentes; por tanto, no origina por sí misma la primitive y no conecta con Celsius. El código contiene nombres `ucred`, `rootvnode`, `sysent`, `SO_PCB` e `INPCB_PKTOPTS`, pero todos pertenecen a cadenas históricas Lapse/Netctrl/IPv6, no al montaje UFS.

Clasificación: **VERIFIED** como artefacto público del mirror y como evidencia de que Vue 13.02/13.04 no equivale a kernel R/W; **INVALID** como implementación Celsius. SHA-256 de los WebP del anuncio primario se conserva por separado; no se descargaron blobs binarios del repositorio completo debido al timeout del clone, y la inspección se realizó mediante API/raw files públicos.

## Artefacto candidato de imagen: `earthonion/mkufs2`

El mirror `https://git.etawen.dev/earthonion/mkufs2` contiene sólo `mkufs2.sh` y `README.md`, con 8 commits, 2 ramas y ningún tag visible. El README describe explícitamente el procedimiento para crear una imagen UFS2 “mountable by PS5/PS4” desde un directorio mediante FreeBSD. El script crea un archivo disperso/zero-filled, usa `mdconfig`, ejecuta `newfs -O 2 -b 32768 -f 4096`, monta el dispositivo, copia el contenido y desmonta la imagen.

Hashes del estado auditado: `mkufs2.sh` SHA-256 `ba00e63f7f286925641070b5cd214dd05a48262951499c824b87ccb418399d64`; `README.md` SHA-256 `880c874bfdaa6db4d33bd0993bf047c696959029e966d012ad35f32db41d8242`. Primer commit del script: `ae8cd6b293c27d0cfa8e357547fdf657f5f0f26a` (2026-02-02 23:15:31 -05:00). Último commit auditado: `b3b5637c8f36c8076aef3dba7a7f3610d88df040` (2026-02-06 23:59:22 -05:00).

El script calcula `OVERHEAD=20%`, pero el valor no se suma a `TOTAL`; por tanto, la receta es una herramienta simple de construcción y no una prueba de que reproduzca la imagen usada por Celsius. No incluye nombre Celsius, `ffs_mountfs`, campos de superbloque manipulados, dispositivo original, tamaño de 250/320/500 GB, hash de imagen ni parámetros de corrupción. Aporta una **pieza parcial**: permite modelar una imagen UFS2 candidata offline. Clasificación: **VERIFIED** como receta pública de UFS2 PS4/PS5; **SOURCE_ONLY / HYPOTHESIS** como posible relación con Celsius; **NO EVIDENCIA** de que sea la imagen original.

Fuente: [earthonion/mkufs2](https://git.etawen.dev/earthonion/mkufs2).

### Auditoría completa de `mkufs2`

La revisión de todas las refs disponibles sólo muestra `main` y su HEAD remoto; la página del mirror indica una segunda rama, pero no aparece como ref alcanzable en el clone auditado. Hay 8 commits y 0 tags. Cada commit contiene únicamente `README.md` y `mkufs2.sh`. La búsqueda en todos los blobs alcanzables sólo encuentra la frase genérica de imagen UFS montable en PS4/PS5; no aparecen `Celsius`, `ffs_mountfs`, `13.02`, `13.04`, parámetros de corrupción, una imagen binaria ni una referencia a bollars/Jordy. Esto fortalece la clasificación de `mkufs2` como receta UFS independiente o derivada, no como PoC Celsius.

## Candidato descartado: `earthonion/vue-mitm-poc`

El repositorio público del mirror contiene 10 commits, una rama, ningún tag y seis archivos principales (`inject.js`, `proxy.py`, `log_server.py`, `hosts.txt`, `download0` y README). El README lo describe como “poc for ps4 vue js injection via mitm” y fija como objetivo la versión 1.01. No menciona Celsius, Jordy, UFS/FFS, `ffs_mountfs`, 13.02/13.04 ni kernel R/W. Aporta contexto histórico del entrypoint Vue, pero no una pieza reutilizable de la cadena Celsius 13.02. Clasificación: **VERIFIED** como PoC Vue 1.01; **INVALID** como PoC Celsius.

Fuente: [earthonion/vue-mitm-poc](https://git.etawen.dev/earthonion/vue-mitm-poc).

## Candidato descartado: `earthonion/ps4debugportal`

El repositorio del mirror tiene 36 commits, una rama y 3 tags. Su README lo describe como una interfaz web de depuración de memoria para PS4 con scanner, editor, disassembler y endpoints de lectura/escritura; exige que la consola ya esté ejecutando el payload `ps4debug`. No contiene Celsius, Jordy, UFS/FFS, `ffs_mountfs`, offsets 13.02/13.04 ni una cadena de explotación. Aporta únicamente una interfaz de consumo para memoria de procesos y no una primitive de kernel ni un bootstrap. Clasificación: **VERIFIED** como herramienta de depuración dependiente de payload; **INVALID** como artefacto Celsius.

Fuente: [earthonion/ps4debugportal](https://git.etawen.dev/earthonion/ps4debugportal).

## Búsqueda de vínculo `mkufs2` → Celsius

Las búsquedas externas de `mkufs2 Celsius PS4`, `mkufs2 bollars UFS` y `mkufs2 Jordy extended storage` no devolvieron referencias técnicas relevantes. Los resultados fueron páginas generales sobre temperaturas, UFS como tecnología de almacenamiento o configuración de almacenamiento extendido. No existe una cita pública que conecte el repositorio `mkufs2` con Celsius, bollars, Jordy o la imagen del anuncio. Clasificación: **sin vínculo independiente encontrado**.

### Comparación mirror ↔ GitHub de `mkufs2`

La comparación de refs muestra que el mirror `git.etawen.dev/earthonion/mkufs2` tiene HEAD `b3b5637c8f36c8076aef3dba7a7f3610d88df040`, mientras que `https://github.com/earthonion/mkufs2` publica HEAD `4d29e9fc2c6d18f8bb825dea0efb3e9bbc5887d3`. GitHub también expone la rama `copilot/add-test-workflow-for-mkufs2` y refs de PR que no aparecen en el clone del mirror. Esto convierte al mirror en un snapshot diferenciado que merece conservarse, pero no demuestra relación con Celsius. El primer commit del script coincide en el historial local; el estado final diverge. Clasificación: **VERIFIED** como divergencia de snapshots; **SOURCE_ONLY** para cualquier posible relación con Celsius, sin evidencia encontrada.

### Revisión de todas las refs GitHub de `mkufs2`

La comparación completa muestra que GitHub mantiene `main` (`4d29e9fc...`), la rama Copilot/PR #1 (`38f22e25...`) y PR #2/#3 (`9d4a8322...`, `9ebb28a5...`). Todas las refs principales contienen `README.md` y `mkufs2.sh`; PR #3 añade `mkufs2_linux.sh`. La diferencia entre el mirror y GitHub no oculta una PoC Celsius: el grep de todas las refs no encuentra `Celsius`, `ffs_mountfs`, `13.02`, `13.04`, `250GB`, `extended storage` ni `Jordy`. PR #3 sólo amplía la herramienta a Linux. Esto confirma que el mirror es un snapshot histórico diferenciado, pero no una fuente de la imagen Celsius.

### Variante Linux de `mkufs2` (PR #3)

La PR #3 de GitHub añade `mkufs2_linux.sh`, que usa `makefs -t ffs -B le -M 1m -o version=2,bsize=32768,fsize=4096,label=ffpkg`. Esta variante aporta una receta reproducible para construir una imagen FFS/UFS2 desde Linux, con parámetros explícitos de endianess, tamaño de bloque, tamaño de fragmento y etiqueta `ffpkg`. No añade campos de superbloque manipulados, tamaño de disco, imagen Celsius, `ffs_mountfs`, argumentos de corrupción ni bootstrap. Es una mejora de portabilidad de la herramienta, no el artefacto original de Celsius. Clasificación: **VERIFIED** como receta de imagen; **SOURCE_ONLY/HYPOTHESIS** para cualquier relación con Celsius.

## Refs históricas de `vue-after-free`

La API del mirror expone seis ramas: `main`, `ts-new`, `release`, `netctrl_c0w`, `test` y `ts`, además de seis tags: `2.0`, `v1.4`, `v1.3`, `v1.2`, `v1.1` y `v1.0`. La rama `netctrl_c0w` y los tags históricos son candidatos relevantes para comparar procedencia del puente WebKit→Netctrl, aunque el nombre no implica Celsius. El main ya muestra que su kernel bridge llega sólo hasta 13.00; las refs históricas deben verificarse antes de concluir que aportan algo para 13.02. El inventario de refs queda guardado en `earthonion_vue_after_free_refs_full.txt`.

## Auditoría de ramas y tags históricos de `vue-after-free`

Las refs históricas consultadas conservan una familia de archivos `src/download0/kernel.ts`, `lapse.ts`, `loader.ts`, `netctrl_c0w_twins.ts` y payloads `aiofix_network.elf`/`elfldr.elf`, además de textos de interfaz `jbBehaviorLapse` y `jbBehaviorNetctrl`. No apareció ningún archivo denominado Celsius, `ffs_mountfs`, UFS, FFS, `mount`, Jordy o un stage de transición equivalente. La presencia de `netctrl_c0w_twins.ts` y `aiofix_network.elf` confirma que el mirror contiene material histórico de Netctrl/AIO, pero no lo convierte en una PoC Celsius ni extiende su cobertura a 13.02. El resultado es útil para separar la cadena Netctrl histórica de Celsius: **VERIFIED** como artefactos Netctrl/AIO; **INVALID** como cierre Celsius 13.02.
