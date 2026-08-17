# PS4 13.52 WebKit

> Investigación técnica de bajo nivel sobre WebKit, Orbis OS y los artefactos de sistema del firmware PS4 13.52.

## Objetivo

Este proyecto reúne y valida evidencia reproducible sobre PS4 Firmware 13.52. La meta es pasar de referencias públicas, tablas de offsets y candidatos estructurales a artefactos verificables: dumps de WebKit, libc, libkernel, kernel, `eboot.bin`, módulos Shell, ELF/SELF y crash dumps.

El proyecto **no se presenta como terminado**. No afirma la existencia de un jailbreak funcional para 13.52. La investigación es pasiva y estática: no ejecuta exploits, payloads ni binarios recuperados, y no requiere hardware PS4.

## Progreso

### 40 %

Ya están identificadas las principales piezas y líneas técnicas necesarias. El repositorio contiene un dump de `libkernel_sys`, análisis reproducibles, tablas de offsets, documentación de WebKit/Orbis y límites de validación claramente separados. El trabajo que queda se concentra en obtener y validar artefactos de la misma build 13.52 que permitan pasar de referencias estructurales a evidencia directa.

Este porcentaje representa el avance del plan técnico, no una probabilidad de éxito ni una afirmación de jailbreak.

## Lo que ya sabemos

- `libkernel_sys_13.52.bin` forma parte del corpus público actual y tiene SHA-256 `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c`. Su existencia no demuestra por sí sola que todos los offsets asociados pertenezcan al kernel retail.
- El análisis estático de `libkernel_sys` identifica wrappers y patrones compatibles con syscalls, incluyendo stubs que cargan `rax=0x215` y `rax=0x216`, además de funciones candidatas para operaciones temporales, lectura, escritura y posicionamiento. Los nombres semánticos permanecen separados de la evidencia de bytes.
- El PUP oficial de sistema 13.52 se validó en el laboratorio local por tamaño y MD5. El archivo comienza con `SLB2`, pero el PUP no expone directamente un ELF, `kernel.elf` ni los módulos Shell mediante el escaneo estático realizado. El PUP completo no se incorpora al repositorio.
- `SYSENT=0x1102B70` aparece en dos proyectos versionados con soporte específico para 13.52: [`ps4-linux-loader`][2] y [`ps4-hen`][3]. Es el candidato estructural preferido, pero todavía no está confirmado mediante bytes del kernel retail.
- `SYSENT=0x110A760` aparece en una tabla parcial cuya fuente se declara anónima e incompleta. Permanece sin verificar.
- `pmap_protect` aparece como `0x58570` en `ps4-linux-loader` y como `0x59DF0` en `ps4-hen`, con `0x59E37` como patch site asociado en HEN. La discrepancia sigue abierta porque no existe una firma binaria pública de la misma imagen 13.52 que permita compararlos.
- [`bad_hoist`][4] aporta la metodología más útil para el siguiente paso: obtener dumps de WebKit, localizar GOT, separar módulos, identificar libc/libkernel y generar información de gadgets desde la build concreta.
- `pOOBs4`, `bad_hoist` y el exploit WebKit de PS4 6.20 son material histórico de 6.20–9.00. Sirven como referencia de metodología, no como evidencia de 13.52.
- La investigación pública de UAF `kqueue/knote` para 13.52 documenta una línea experimental, pero no demuestra una primitiva estable de kread/kwrite ni un jailbreak funcional.

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
| PUP oficial 13.52 validado localmente por tamaño y MD5 | `DIRECT_BYTES`, artefacto no publicado aquí |
| Commits de soporte 13.52 en `ps4-linux-loader` y `ps4-hen` | `STRONG_STRUCTURAL` |
| `SYSENT=0x1102B70` en ambas tablas de soporte | `STRONG_STRUCTURAL` |
| Metodología de dumps WebKit/libc/libkernel en `bad_hoist` | `DOCUMENTATION / STRONG_METHODOLOGY` |
| Imágenes exFAT de `pOOBs4` y sus hashes | `DIRECT_BYTES`, pero sólo firmware 9.00 |

### Candidato o sin verificar

| Evidencia | Clasificación |
|---|---|
| `SYSENT=0x110A760` | `OFFSET_REFERENCE / UNVERIFIED` |
| `pmap_protect=0x58570` | `STRONG_STRUCTURAL`, sin bytes del kernel 13.52 |
| `pmap_protect=0x59DF0` | `STRONG_STRUCTURAL`, conflictivo y sin bytes |
| Patch site `0x59E37` | `OFFSET_REFERENCE` |
| Versión exacta del firmware deducida sólo desde el blob libkernel | `UNVERIFIED` |
| UAF `kqueue/knote` como vía explotable | `UNVERIFIED` para una primitiva de kernel |

> **No se ha encontrado evidencia reproducible de jailbreak funcional para 13.52.**

## Próximo objetivo

El siguiente ciclo debe priorizar un único artefacto de alto valor: un dump verificable de WebKit, libc, `libkernel_sys` o kernel correspondiente a 13.52. Si aparece un archivo público y legalmente accesible, se conservará localmente, se calcularán SHA-256/SHA-1/MD5, se determinará su formato real y se analizarán cabeceras, strings, símbolos, segmentos y referencias sin ejecutarlo.

Si ya existe un artefacto local suficiente, no se repetirá la búsqueda pública. El análisis continuará descendiendo en sus contenedores, imágenes, caches, ELF/SELF o crash dumps hasta donde sea razonable y seguro.

## Investigación local

El corpus local prioritario se mantiene fuera de la publicación cuando contiene archivos grandes o sensibles. Incluye:

- dump de `libkernel_sys_13.52` y sus hashes;
- PUP oficial 13.52 y escaneo estático reproducible;
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

`tools/libkernel_1352_manifest.json` fija el hash, tamaño, chunks y offsets de la ancla real `libkernel_sys_13.52.bin`. La validación confirma la reconstrucción byte a byte y clasifica `jitshm_create`/`jitshm_alias` como `DIRECT_BYTES`; los wrappers restantes se conservan como `STRUCTURAL`.

`tools/webkit_1352_migration.json` deja parametrizados WebKit, `libkernel_web`, `libSceLibcInternal`, bases, `.text`, `PT_SCE_RELRO`, vtables, imports, GOT/PLT y gadgets. No contiene direcciones inventadas. `scan_webkit_patterns.py` sólo eleva una entrada cuando encuentra los bytes configurados; después siguen siendo necesarias XREFs y validación de módulo.

`tools/jordy_1352_migration.json` separa lógica portable de bases, GOT, gadgets, pivot y ROP pendientes. `tools/scan_kernel_structures.py` es independiente de la capa libkernel y devuelve candidatos conservadores para `sysent`, `pmap_protect`, `allproc`, `rootvnode` y `kernel_map`; no calcula deltas ni confirma offsets sin bytes del kernel objetivo.

La documentación ampliada está en [`docs/migration-1352.md`](docs/migration-1352.md). Actualmente la cadena queda así:

```text
WebKit 13.52:        AUSENTE
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

La herramienta sólo lee texto, hashes y manifests. No importa, construye ni ejecuta payloads o exploits. Las categorías permitidas son `CONFIRMED_1352`, `DIRECT_BYTES`, `STRUCTURAL`, `PORTABLE`, `REQUIRES_REANALYSIS`, `UNVERIFIED` y `ABSENT`.

Se añadió `tests/test_static_migration.py`, que valida hash/tamaño/chunks de `libkernel_sys_13.52.bin`, JSON de manifests, clasificación CSSFontFace y la matriz cruzada de fuentes.

## Estado del proyecto

Este proyecto está **en investigación activa**. Tiene una base técnica organizada y candidatos estructurales reproducibles, pero todavía no dispone de la evidencia binaria necesaria para cerrar los offsets críticos ni de una demostración reproducible de jailbreak en 13.52.

## Fuentes principales

[1]: https://www.playstation.com/en-us/support/hardware/ps4/system-software/ "Sony — PS4 system software"
[2]: https://github.com/ps4boot/ps4-linux-loader/commit/9acef9fbf79097a2bb39d6c9c17228198bc445cc "ps4-linux-loader — PS4 13.52 support"
[3]: https://github.com/Scene-Collective/ps4-hen/commit/2beb4cfcef1d416a32d6fb7b35f01189e9eb62e2 "ps4-hen — PS4 13.52 support"
[4]: https://github.com/sleirsgoevy/bad_hoist "bad_hoist — WebKit/ROP porting methodology"
[5]: https://github.com/Scene-Collective/ps4-kernel-dumper "PS4 kernel dumper"
[6]: https://www.psdevwiki.com/ps4/COREDMP "PS4 Developer Wiki — COREDMP/NXDP"
[7]: https://github.com/kmeps4/PSFree/tree/368d82aa40d3017c220757ce315761adb5f06678 "PSFree — audited commit"
[8]: https://github.com/ntfargo/CSSFontFace-Exploit/tree/221baa6e7349b96a6fd299808a25a4178e47741c "CSSFontFace-Exploit — audited commit"
[9]: https://github.com/Vuemony/vue-after-free/tree/6e37d510c7383aac2378b7215aefd14c1defd8d1 "Vue-After-Free — audited commit"
[10]: https://github.com/ps4-linux/ps4-linux-loader/commit/9acef9fbf79097a2bb39d6c9c17228198bc445cc "ps4-linux-loader v25 — PS4 13.52 support"
