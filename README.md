# PS4 13.52 WebKit

> Investigación técnica de bajo nivel sobre WebKit, Orbis OS y los artefactos de sistema del firmware PS4 13.52.

## Objetivo

Este proyecto reúne y valida evidencia reproducible sobre PS4 Firmware 13.52. La meta es pasar de referencias públicas, tablas de offsets y candidatos estructurales a artefactos verificables: dumps de WebKit, libc, libkernel, kernel, `eboot.bin`, módulos Shell, ELF/SELF y crash dumps.

El proyecto **no se presenta como terminado**. No afirma la existencia de un jailbreak funcional para 13.52. La investigación es pasiva y estática: no ejecuta exploits, payloads ni binarios recuperados, y no requiere hardware PS4.

## Progreso

### 86 % de infraestructura estática / 35 % de evidencia específica 13.52

Ya están identificadas las principales piezas y líneas técnicas necesarias. El repositorio contiene el ancla `libkernel_sys`, validación de hash/chunks, manifests conservadores, scanner RAW/ELF64/SELF, tests negativos de límites ELF y una matriz separada por capas. El trabajo que queda se concentra en obtener y validar artefactos de la misma build 13.52 que permitan pasar de referencias estructurales a evidencia directa.

El primer porcentaje mide la infraestructura y migración estática; el segundo mide únicamente evidencia binaria específica de 13.52. Ninguno es una probabilidad de éxito ni una afirmación de jailbreak.

## Lo que ya sabemos

- `libkernel_sys_13.52.bin` forma parte del corpus público actual y tiene SHA-256 `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c`. Su existencia no demuestra por sí sola que todos los offsets asociados pertenezcan al kernel retail.
- El análisis estático de `libkernel_sys` identifica wrappers y patrones compatibles con syscalls, incluyendo stubs que cargan `rax=0x215` y `rax=0x216`, además de funciones candidatas para operaciones temporales, lectura, escritura y posicionamiento. Los nombres semánticos permanecen separados de la evidencia de bytes.
- [`RuxaXa/ps4-research`][14] documenta el PUP oficial de sistema 13.52 con versión `13.520.000`, SDK `13.520.001`, tamaño `503310848` y un SHA-256 declarado. En este ciclo se comprobó pasivamente que la [URL oficial de Sony][13] responde `200`, anuncia exactamente ese tamaño y que su prefijo de 32 bytes contiene la magia `SLB2`; el PUP completo no se conserva localmente y su SHA-256 no se recalculó de forma independiente. Por ello esta evidencia queda como `UNVERIFIED` a nivel de hash completo y no confirma módulos internos.
- `SYSENT=0x1102B70` aparece en dos proyectos versionados con soporte específico para 13.52: [`ps4-linux-loader`][2] y [`ps4-hen`][3]. Es el candidato estructural preferido, pero todavía no está confirmado mediante bytes del kernel retail.
- `SYSENT=0x110A760` aparece en una tabla parcial cuya fuente se declara anónima e incompleta. Permanece sin verificar.
- `pmap_protect` aparece como `0x58570` en `ps4-linux-loader` y SLOPOS, y como `0x59DF0` en `ps4-hen`, con `0x59E37` como patch site asociado en HEN. `0x58570` es el candidato estructural prioritario por procedencia de la tabla PS4_13_52, pero ambos valores siguen sin confirmación por bytes del kernel retail.
- [`bad_hoist`][4] aporta la metodología más útil para el siguiente paso: obtener dumps de WebKit, localizar GOT, separar módulos, identificar libc/libkernel y generar información de gadgets desde la build concreta.
- La auditoría completa de [`PS4.badhoist`][15] encontró releases v1.0, v1.2 y v2 anunciados para FW 6.72. Los assets RAR tienen bytes y hashes verificables; v1.2 y v2 contienen ELF históricos de `webkit`, `libc` y `libkernel`, pero su firmware se conserva como una atribución declarada y no como identidad independiente de build. Se registraron tamaños, hashes, cabeceras ELF, `.text`, PT_LOAD, ausencia de RELRO/build ID y los fallos de extracción de algunos raw `.bin`.
- [`PS4OSSCode`][16] es una colección de código fuente OSS de WebKit/FreeBSD y no un repositorio de dumps retail. Su HEAD documenta `WebKit-601-1300` como PS4 13.00–13.04; no contiene `libSceNKWebKit`, `libkernel_web`, `libSceLibcInternal` ni ORBISDMP 13.52. Las coincidencias literales `13.52` son falsos positivos en datos de LayoutTests. Su utilidad queda clasificada como `STRUCTURAL`, no como evidencia binaria 13.52.
- El commit [`ps4-hen` `2beb4cf`][17] añade una tabla de offsets etiquetada 13.52. Contiene `SYSENT=0x01102B70`, `pmap_protect=0x00059DF0`, `pmap_protect_patch_site=0x00059E37`, `ALLPROC=0x01B28538`, `ROOTVNODE=0x02136E90` y `PMAP_STORE=0x01B2C3A0`. Es una referencia versionada de fuente, clasificada `UNVERIFIED`: el repositorio no contiene bytes retail del kernel 13.52 que permitan validar esos valores.
- La release `pre-release-main-179` de ps4-hen aporta un `hen.bin` de 498.880 bytes, SHA-256 `54b39b0e56efe00287238f55317b8111b895b96a5a4f779507b3931a58e6c4a2`, cuyo texto contiene `libkernel_web.sprx` y `libkernel_sys.sprx`. La nota de release indica soporte 13.50, no 13.52. Es `DIRECT_BYTES` de un payload 13.50, no un dump retail ni una prueba de compatibilidad 13.52.
- [`ps4-kern-dump`][18] es una fuente adicional de metodología para dumpear `kernel_map` y tablas de páginas mediante salida Z85. No incluye dumps binarios, firmware, SELF, SPRX o NXDP; queda clasificado como `PORTABLE`.
- [`PS4OSSCode`][19] fue auditado como el mayor corpus público disponible en el laboratorio: 7,7 GiB en el árbol de trabajo, 1,54 GiB de objetos Git, 584.706 archivos rastreados y 8 commits. Contiene fuentes WebKit/FreeBSD y archives históricos de WebKit 601.2.7 para ramas 6.00–11.00, pero ningún `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx`, SELF, SPRX, NXDP, ORBISDMP, PUP o kernel retail 13.52. Las 30 coincidencias de `13.52` en fuentes/documentación son numéricas o pertenecen a LayoutTests; el corpus queda clasificado `STRUCTURAL`.
- `pOOBs4`, `bad_hoist` y el exploit WebKit de PS4 6.20 son material histórico de 6.20–9.00. Sirven como referencia de metodología, no como evidencia de 13.52.
- La investigación pública de UAF `kqueue/knote` para 13.52 documenta una línea experimental, pero no demuestra una primitiva estable de kread/kwrite ni un jailbreak funcional.
- [`BillZaiD/ps4-kernel-uaf-research-fw1352`][20], commit `aa5802c`, contiene sólo README, FINDINGS y PoC Lua; no contiene kernel, WebKit, libkernel, crash dump, build ID ni logs runtime adjuntos. Sus afirmaciones sobre `EVFILT_USER=-7`, la base `0x80a67c000` y el UAF quedan `UNVERIFIED`; la construcción de `kevent` y la metodología de inventario syscall son `PORTABLE`.
- [`alferdoss/SLOPOS-offsets`][21], commit `42273e2`, aporta una tabla `ps4/1352.h` con `SYSENT=0x1102B70`, `pmap_protect=0x58570`, `kernel_map=0x22D1D50`, `kernel_pmap_store=0x1B2C3A0` y `rootvnode=0x2136E90`. Su `CREDITS.md` declara que los offsets kexec se copian de `ps4-linux-loader` y atribuye 13.52 a ArabPixel. Esto mejora la trazabilidad de `0x58570`, pero no resuelve la discrepancia con `ps4-hen` (`0x59DF0`) ni convierte ninguna tabla en `DIRECT_BYTES`.
- [`Gustuds/PS4-AIO-Host-by-Gustuds`][22], commit `7792f6e`, conserva CSSFontFace histórico con layouts, vtables, `m_featureSettings` y parches `.bin` hasta 11.02; su manifest no incluye 13.52. Los hashes y tamaños de sus patches se registran en `analysis/github_indirect_findings_13.52.json`; sólo sirven como correlación histórica.
- La auditoría GitHub profunda de [`Leandrobts/Test`][23], [`Gezine/BD-JB5`][24] y [`ps4-linux-loader`][2] añadió código y tablas que explican mejor la procedencia de los candidatos. `Leandrobts/Test` contiene una tabla WebKit/libkernel 13.52 y un scanner runtime, pero no contiene los tres módulos `.decrypted` que sus comentarios mencionan: sus valores quedan `UNVERIFIED` y la lógica de configuración es sólo `PORTABLE`. `BD-JB5` mantiene `SYSENT_661_OFFSET=0x110A760` y shellcode bajo la clave 13.52, pero su propia puerta de soporte PS4 rechaza versiones superiores a 13.00; no es prueba de compatibilidad 13.52. `ps4-linux-loader` contiene un bloque `PS4_13_52` con `SYSENT=0x1102B70` y `pmap_protect=0x58570` en `linux/magic.h:678-710`, mientras que `ps4-hen` mantiene `0x59DF0`/`0x59E37`. Todas son tablas fuente sin bytes del kernel objetivo y la contradicción permanece abierta. El detalle reproducible está en `analysis/github_deep_audit_13.52.json`.
- Un adjunto público del issue [`ps4-linux-payloads-archive #5`][25] contiene `11.02/kernel.bin`: 44.040.192 bytes, ELF64 FreeBSD x86-64 sin section headers, SHA-256 `451f87357637beedc92fe822fc5942f86e12231a53fa8dfd81c24433093408d4`. Es `DIRECT_BYTES` sólo para un kernel histórico 11.02; aporta validación del pipeline de ELF program headers y comparación estructural, pero no confirma ningún offset de 13.52. Los metadatos y scans están en `analysis/github_downloaded_artifacts_13.52.json`.

## Lo que falta

1. Obtener un dump de kernel retail 13.52 con bytes, SHA-256, tamaño, build string y base de imagen.
2. Confirmar SYSENT mediante el dispatcher de syscalls, `sysentvec`, XREFs y la estructura real de sus entradas.
3. Comparar `0x58570`, `0x59DF0` y `0x59E37` dentro de una misma imagen, registrando prologues, callers, límites de función y referencias PMAP/PTE.
4. Localizar y validar `kernel`, `eboot.bin`, `SceShellCore`, `SceShellUI` y `SceRemotePlay` de 13.52 con hashes recomputables.
5. Determinar si existe un crash dump NXDP/ORBISDMP u `orbiscore-systemcrash.orbisstate` de 13.52 que pueda analizarse estáticamente.
6. Separar siempre kernel, `libkernel_sys.sprx`, WebKit, libc y módulos Shell; un artefacto de una categoría no valida offsets de otra.
7. Verificar cualquier vulnerabilidad candidata contra el código de la build, su versión base, el parche aplicable y una reproducción técnica independiente.

## Evidencia

### Confirmado

| Evidencia | Clasificación |
|---|---|
| Hash y concatenación del dump local de `libkernel_sys` | `DIRECT_BYTES` |
| Instrucciones syscall observadas en el blob | `DIRECT_BYTES` |
| URL oficial Sony + tamaño HTTP + prefijo `SLB2` del PUP 13.52 | `UNVERIFIED` para el hash completo; no es evidencia de módulos internos |
| Commits de soporte 13.52 en `ps4-linux-loader` y `ps4-hen` | `STRUCTURAL` (referencia de payload/tabla, no bytes de kernel) |
| `SYSENT=0x1102B70` en tablas de soporte | `STRUCTURAL` (sin bytes de kernel objetivo) |
| Metodología de dumps WebKit/libc/libkernel en `bad_hoist` | `PORTABLE` |
| Imágenes exFAT de `pOOBs4` y sus hashes | `DIRECT_BYTES`, pero sólo firmware 9.00 |

### Candidato o sin verificar

| Evidencia | Clasificación |
|---|---|
| `SYSENT=0x110A760` | `UNVERIFIED` |
| `pmap_protect=0x58570` | `UNVERIFIED`, sin bytes del kernel 13.52 |
| `pmap_protect=0x59DF0` | `UNVERIFIED`, conflictivo y sin bytes |
| Patch site `0x59E37` | `STRUCTURAL`, sin bytes objetivo |
| Versión exacta del firmware deducida sólo desde el blob libkernel | `UNVERIFIED` |
| UAF `kqueue/knote` como vía explotable | `UNVERIFIED` para una primitiva de kernel |

> **No se ha encontrado evidencia reproducible de jailbreak funcional para 13.52.**

## Próximo objetivo

El siguiente ciclo debe priorizar un único artefacto de alto valor: un dump verificable de WebKit, libc, `libkernel_sys` o kernel correspondiente a 13.52. Si aparece un archivo público y legalmente accesible, se conservará localmente, se calcularán SHA-256/SHA-1/MD5, se determinará su formato real y se analizarán cabeceras, strings, símbolos, segmentos y referencias sin ejecutarlo.

Si ya existe un artefacto local suficiente, no se repetirá la búsqueda pública. El análisis continuará descendiendo en sus contenedores, imágenes, caches, ELF/SELF o crash dumps hasta donde sea razonable y seguro.

## Investigación local

El corpus local prioritario se mantiene fuera de la publicación cuando contiene archivos grandes o sensibles. Incluye:

- dump de `libkernel_sys_13.52` y sus hashes;
- metadatos y prefijo HTTP del PUP oficial 13.52; el PUP completo se mantiene fuera del corpus publicado;
- documentación y pruebas locales de WebKit/Orbis;
- repositorios clonados de `900-host`, `pOOBs4`, `bad_hoist`, el exploit WebKit 6.20 y `ps4jb-payloads`;
- fuentes de parsers PUP y dumper ELF/SELF;
- investigaciones mast1c0re y UAF de 13.52.

La prioridad de análisis será:

```text
kernel / crash dump 13.52
→ WebKit / libc / libkernel 13.52
→ eboot y módulos Shell
→ ELF/SELF, caches y estructuras PUP
→ artefactos históricos sólo como comparación
```

## Regla de progreso

Cada ciclo debe producir algo nuevo que acerque el proyecto al objetivo. Se considera progreso válido:

- un artefacto nuevo conservado y hasheado;
- una estructura interna interpretada;
- una firma o símbolo confirmado en la misma build;
- una comparación binaria reproducible;
- una contradicción resuelta con evidencia;
- o una vía técnica descartada con una razón verificable.

Las búsquedas públicas ya agotadas no se repetirán como actividad principal. Cuando una vía deje de producir fuentes primarias nuevas, el proyecto cambiará automáticamente al análisis local de artefactos.

## Reproducción

Las auditorías principales se ejecutan desde la raíz:

```bash
./tools/run_static_audit.sh
python3 tools/verify_offsets.py --repo . --json
python3 tools/analyze_xref_versions.py ./libkernel_sys_13.52.bin --out-dir ./analysis
```

La compilación host de fuentes y payloads sólo demuestra que el código puede procesarse en el entorno de análisis. No demuestra ABI, ejecución, compatibilidad de consola ni jailbreak.

## Base de migración estática 13.52

La migración ya tiene una base reproducible, pero no rellena valores ausentes con offsets de otros firmwares:

```bash
python3 tools/validate_libkernel_1352.py --json
python3 tools/scan_webkit_patterns.py --image /ruta/a/webkit_13.52.bin --json
python3 tools/scan_kernel_structures.py --kernel /ruta/a/kernel_13.52.bin --firmware 13.52
python3 tools/cross_source_evidence.py \
  --lab . \
  --psfree /ruta/a/PSFree \
  --cssfontface /ruta/a/CSSFontFace-Exploit \
  --vue /ruta/a/vue-after-free \
  --loader /ruta/a/ps4-linux-loader \
  --out /tmp/cross_source_evidence.json
python3 -m unittest discover -s tests -v
```

`tools/libkernel_1352_manifest.json` fija el hash, tamaño, offsets secuenciales (`0x00000`, `0x27000`, `0x4e000`), chunks y offsets de la ancla real `libkernel_sys_13.52.bin`. La validación confirma la reconstrucción byte a byte y clasifica `jitshm_create`/`jitshm_alias` como `DIRECT_BYTES`; el manifest también registra `stat`, `pwrite`, `lseek`, `unlink`, `socket` y `connect_alt`, todos como `STRUCTURAL`.

`tools/webkit_1352_migration.json` deja parametrizados WebKit, `libkernel_web`, `libSceLibcInternal`, bases, `.text`, `PT_SCE_RELRO`, vtables, imports, GOT/PLT y gadgets. No contiene direcciones inventadas. `scan_webkit_patterns.py` acepta blobs RAW, ELF64 little-endian y contenedores SELF-like, registra SHA-256/tamaño, valida límites, extrae `.text`, `PT_LOAD`, `PT_SCE_RELRO`, `PT_GNU_RELRO`, notas/build ID cuando existen y relaciona cada hit con segmentos válidos. Un hit sólo es bytes encontrados; la identidad semántica sigue siendo `REQUIRES_REANALYSIS`.

`tools/jordy_1352_migration.json` separa lógica portable de bases, GOT, gadgets, pivot y ROP pendientes. `tools/scan_kernel_structures.py` es independiente de la capa libkernel y devuelve candidatos conservadores para `sysent`, `pmap_protect`, `allproc`, `rootvnode` y `kernel_map`; no calcula deltas ni confirma offsets sin bytes del kernel objetivo.

La documentación ampliada está en [`docs/migration-1352.md`](docs/migration-1352.md). El análisis específico de PSFree 8.50/8.52→13.52 está en [`docs/psfree-850-852-to-1352-porting.md`](docs/psfree-850-852-to-1352-porting.md). El mapa reproducible de candidatos binarios está en [`analysis/webkit_13.52_research.json`](analysis/webkit_13.52_research.json); registra origen, tamaño, SHA-256, formato, decisión y el siguiente artefacto prioritario. Actualmente la cadena queda así:

```text
WebKit 13.52:        AUSENTE (ver `analysis/webkit_13.52.json`; las páginas técnicas consultadas documentan módulos/User-Agent, pero no aportan bytes ni hashes)
libkernel_sys 13.52: VERIFICADO
kernel 13.52:        AUSENTE
```

## Higiene de publicación

Antes de cada publicación se comprueba que el cambio no incluya claves API, tokens, credenciales, claves privadas, logs privados, copias de seguridad, capturas personales ni archivos enormes que no deban distribuirse. Los binarios de investigación se conservan fuera del README y se referencian mediante ruta, tamaño, hash y procedencia cuando corresponde.

## Integración cruzada de fuentes

Se añadió `tools/cross_source_evidence.py` para auditar estáticamente y cruzar:

- PSFree: búsqueda de límites de módulos, resolución de imports y escaneo de wrappers de `libkernel_web`.
- CSSFontFace-Exploit: layouts históricos, `m_featureSettings` y ausencia de una tabla 13.52.
- Vue-After-Free: separación entre userland y kernel, sin elevar sus offsets históricos.
- `ps4-linux-loader` v25: bloque etiquetado `PS4_13_52` y entrada de dispatch `1352`, clasificados como `STRUCTURAL` porque el repositorio no contiene bytes de kernel retail.
- La auditoría GitHub profunda se conserva en `analysis/github_deep_audit_13.52.json`, con commits, rangos de líneas, hashes, issues y condiciones de migrabilidad. La auditoría de adjuntos descargables se conserva en `analysis/github_downloaded_artifacts_13.52.json`; produjo bytes históricos 11.02, pero no nuevos bytes `CONFIRMED_1352`.

La herramienta sólo lee texto, hashes y manifests. No importa, construye ni ejecuta payloads o exploits. Las categorías permitidas son `CONFIRMED_1352`, `DIRECT_BYTES`, `STRUCTURAL`, `PORTABLE`, `REQUIRES_REANALYSIS`, `UNVERIFIED` y `ABSENT`.

Se añadió `tools/audit_psfree_porting.py`, que lee PSFree como texto y genera un inventario de estructuras, algoritmos portables, offsets históricos y soporte explícito de firmware sin ejecutar JavaScript. `tools/run_static_audit.sh` lo ejecuta cuando se proporciona `PSFREE_ROOT`; sin esa variable produce un estado `ABSENT` explícito. Las suites `tests/test_static_migration.py` y `tests/test_webkit_artifact.py` validan hash/tamaño/chunks, offsets secuenciales, evidencia fuerte, JSON de manifests, clasificación CSSFontFace, matriz cruzada, auditor PSFree, límites ELF truncados/fuera de rango, RELRO inválido, `.text` inválido, máscaras incompatibles y separación hit/identidad. Actualmente pasan 24 tests, incluidos los tests conservadores de los manifests GitHub y artefactos descargados.

## Estado del proyecto

Este proyecto está **en investigación activa**. Tiene una base técnica organizada y candidatos estructurales reproducibles, pero todavía no dispone de la evidencia binaria necesaria para cerrar los offsets críticos ni de una demostración reproducible de jailbreak en 13.52.

## Fuentes principales

[1]: https://www.playstation.com/en-us/support/hardware/ps4/system-software/ "Sony — PS4 system software"
[13]: https://pc.ps4.update.playstation.net/update/ps4/image/2026_0611/sys_2ce20d9fbb48274ceb369b40412e616c/PS4UPDATE.PUP "Sony CDN — PS4UPDATE.PUP candidate documented as 13.52"
[14]: https://github.com/RuxaXa/ps4-research/tree/e14d0647927c6675dc619f89ab700dfda50dcd55 "RuxaXa/ps4-research — 13.52 acquisition dossier"
[2]: https://github.com/ps4boot/ps4-linux-loader/commit/9acef9fbf79097a2bb39d6c9c17228198bc445cc "ps4-linux-loader — PS4 13.52 support"
[3]: https://github.com/Scene-Collective/ps4-hen/commit/2beb4cfcef1d416a32d6fb7b35f01189e9eb62e2 "ps4-hen — PS4 13.52 support"
[4]: https://github.com/sleirsgoevy/bad_hoist "bad_hoist — WebKit/ROP porting methodology"
[15]: https://github.com/a0zhar/PS4.badhoist "a0zhar/PS4.badhoist — historical FW 6.72 module releases"
[16]: https://github.com/FreeBSDKernel9-0/PS4OSSCode "FreeBSDKernel9-0/PS4OSSCode — PS4 OSS/WebKit source collection"
[19]: https://github.com/FreeBSDKernel9-0/PS4OSSCode "PS4OSSCode — largest public OSS/WebKit corpus audited"
[20]: https://github.com/BillZaiD/ps4-kernel-uaf-research-fw1352 "PS4 FW 13.52 kqueue/knote research"
[21]: https://github.com/alferdoss/SLOPOS-offsets "SLOPOS per-firmware kernel offset tables"
[22]: https://github.com/Gustuds/PS4-AIO-Host-by-Gustuds "Historical CSSFontFace PS4 host"
[23]: https://github.com/Leandrobts/Test "Leandrobts/Test — PS4 13.52 source-level offset table"
[24]: https://github.com/Gezine/BD-JB5 "Gezine/BD-JB5 — BD-JB5 PS4/PS5 source and payload references"
[25]: https://github.com/ps4boot/ps4-linux-payloads-archive/issues/5 "ps4-linux-payloads-archive issue #5 — public 11.02 kernel attachment"
[5]: https://github.com/Scene-Collective/ps4-kernel-dumper "PS4 kernel dumper"
[6]: https://www.psdevwiki.com/ps4/COREDMP "PS4 Developer Wiki — COREDMP/NXDP"
[7]: https://github.com/kmeps4/PSFree/tree/368d82aa40d3017c220757ce315761adb5f06678 "PSFree — audited commit"
[8]: https://github.com/ntfargo/CSSFontFace-Exploit/tree/221baa6e7349b96a6fd299808a25a4178e47741c "CSSFontFace-Exploit — audited commit"
[9]: https://github.com/Vuemony/vue-after-free/tree/6e37d510c7383aac2378b7215aefd14c1defd8d1 "Vue-After-Free — audited commit"
[10]: https://github.com/ps4-linux/ps4-linux-loader/commit/9acef9fbf79097a2bb39d6c9c17228198bc445cc "ps4-linux-loader v25 — PS4 13.52 support"
[11]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer Wiki — Vulnerabilities"
[12]: https://www.psdevwiki.com/ps4/Internet_Browser "PS4 Developer Wiki — Internet Browser"
