# Auditoría local del segundo rootfs/artefacto

## Alcance

Se inspeccionó exclusivamente el almacenamiento local bajo `/home/ubuntu`, excluyendo el contenido persistente de `/home/ubuntu/wpe-artifacts-2526/arch/rootfs`, que ya está identificado como WPE/Linux 2.52.6. Se buscaron directorios `rootfs`, imágenes, archivos comprimidos, nombres `system_ex`, `app0`, `orbis`, `sprx`, `SELF`, `eboot`, módulos `libSce*`/`libkernel*` y artefactos grandes.

No se hicieron búsquedas web, no se ejecutaron exploits, PoC, payloads, binarios ni clases y no se interactuó con hardware. No se modificaron, borraron, renombraron ni sobrescribieron artefactos auditados.

## A. Localización

No existe otro directorio local llamado `rootfs` fuera de:

```text
/home/ubuntu/wpe-artifacts-2526/arch/rootfs
```

Tampoco apareció un directorio `app0`, `system_ex` u `orbis` independiente. El escaneo local detectó archivos PS4-like en copias de workspaces ya existentes, pero no un segundo rootfs:

```text
scanner_1304.iso
hen.bin
libkernel_sys_13.52.bin
```

Las copias en `firmware-lab-runtime`, `firmware-lab-audit`, `firmware-lab-aux`, `firmware-lab-bundle` y `firmware-lab-offscreen` son byte-identical por SHA-256; son duplicados de trabajo, no rootfs independientes.

## B. Artefactos candidatos

### `scanner_1304.iso`

| Campo | Resultado |
|---|---|
| Ruta inspeccionada | `/home/ubuntu/firmware-lab-runtime/scanner_1304.iso` |
| Tamaño | 16.777.216 bytes |
| Permisos/propietario | `-rw-r--r--`, UID/GID 1000/1000 |
| Fecha local | 2026-08-20 13:22:37 UTC |
| SHA-256 | `6ed15acd9cfb2539e034cde72a9003f52cf6338f04549670e1b8d515d948bd30` |
| Tipo | UDF filesystem data, version 1.5, volume `scanner_1304` |
| Firmware atribuible | El nombre y contenido apuntan a `13.04`; no demuestra 13.52 |
| Clasificación | `HISTORICAL_ONLY` / `UNVERIFIED` para 13.52 |

El análisis pasivo de strings del volumen encontró:

```text
BD-JB TEST
BDJO / BDJO0200
00000.jar
00000.bdjo
/app0/bdjstack/lib/ext/sunjce_provider.jar/../../../../../disc/BDMV/JAR/00000.jar
org/bdj/InitXlet.class
org/bdj/SuidScanner.class
org/bdj/InternalJarLoader.class
org/bdj/RemoteJarLoader.class
org/bdj/NativeInvoke.class
org/bdj/UnsafeInterface.class
org/bdj/UnsafeSunImpl.class
org/bdj/sandbox/XletManagerExploit.class
```

Esto es evidencia fuerte de una **imagen BD-J de laboratorio asociada al nombre `scanner_1304`**, con clases Java y rutas históricas de BD-J. No es un rootfs Linux y no contiene por sí mismo `libSceNKWebKit`, `libkernel_web`, JavaScriptCore ni WebCore. El contenido puede servir para estudiar un descriptor BDJO y clases de scanner de forma estática, pero no para identificar el WebKit/JSC retail 13.52.

La existencia de nombres `Unsafe`, `NativeInvoke` o `XletManagerExploit` no se interpreta como ejecución ni como vulnerabilidad confirmada. Sólo son entradas de un contenedor no ejecutado.

La imagen es idéntica en los cinco workspaces:

```text
/home/ubuntu/firmware-lab-runtime/scanner_1304.iso
/home/ubuntu/firmware-lab-audit/scanner_1304.iso
/home/ubuntu/firmware-lab-aux/scanner_1304.iso
/home/ubuntu/firmware-lab-bundle/scanner_1304.iso
/home/ubuntu/firmware-lab-offscreen/scanner_1304.iso
```

### `libkernel_sys_13.52.bin`

| Campo | Resultado |
|---|---|
| Tamaño | 479.232 bytes |
| SHA-256 | `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c` |
| Tipo | `data` sin ELF/SELF identificable por `file` |
| Strings | `machdep.system_ex_version`, símbolos `__orbis_rtld_*`, `orbis_rtld_*` |
| Firmware | El nombre lo atribuye a 13.52; el archivo no contiene por sí solo una prueba criptográfica de esa atribución |
| Relación WebKit | No contiene strings identificables de `libSceNKWebKit`, `JavaScriptCore`, `CSSFontFace` ni WebCore |
| Clasificación | Artefacto PS4 ya conocido; no es un rootfs ni evidencia WebKit 13.52 |

Está duplicado con el mismo SHA-256 en los cinco workspaces mencionados. No se volvió a analizar su contenido ni se ejecutó.

### `hen.bin`

| Campo | Resultado |
|---|---|
| Tamaño | 499.680 bytes |
| SHA-256 | `32570b6e54c9531dc8a7d75ef4da6557d440bf69c4b765a85a77d428db3a4b73` |
| Tipo | `DOS executable (COM)` según `file`; no se ejecutó |
| Strings relevantes | `OPENORBIS-HOMEBREW`, `Sce.Vsh.Orbis.Bgft.BgftWrapper...`, `libkernel_web.sprx` |
| Firmware | No demostrado por el archivo aislado |
| Relación WebKit | Menciona `libkernel_web.sprx`, pero no contiene el módulo ni bytes WebKit verificables |
| Clasificación | `HISTORICAL_ONLY`/`UNVERIFIED` como evidencia WebKit 13.52 |

`hen.bin` está duplicado byte a byte en los mismos cinco workspaces. El nombre y las strings no constituyen procedencia de WebKit ni de PS4 13.52.

## C. Material que pertenece definitivamente a WPE/Linux

El árbol excluido contiene el rootfs Linux/WPE 2.52.6 ya auditado: `libWPEWebKit-2.0.so.1.9.10`, `MiniBrowser`, `WPEWebProcess`, `libWPEBackend-fdo` y headers WPE. Es x86-64 ELF/Linux y contiene rutas `/usr/src/debug/wpewebkit/wpewebkit-2.52.6`. No se mezcló con evidencia PS4.

El resto de `db-extract` contiene descripciones y metadata de paquetes Linux, incluidos `wpewebkit-2.52.6-1`, `webkit2gtk-4.1-2.52.6-1` y `webkitgtk-6.0-2.52.6-1`. No son componentes Orbis.

## D. Tres familias

No apareció una fuente WebKit/JSC Sony ni un módulo retail que permita aplicar el correlador de manera válida. La ISO BD-J sólo contiene clases de aplicación/BD-J; no contiene el runtime JSC. Por tanto:

| Familia | Resultado válido frente a PS4 13.52 | Motivo |
|---|---|---|
| `MarkedVector` / GC | `NO MATCH` sobre artefactos analizados; estado 13.52 `UNVERIFIED` | No hay fuente/módulo JSC retail |
| `CloneSerializer` / `CloneDeserializer` / `objectPool` | `NO MATCH` sobre artefactos analizados; estado 13.52 `UNVERIFIED` | No hay WebKit/JSC ni símbolos equivalentes |
| `CSSFontFace` / `CSSFontFaceSet` / `FontFaceSet` | `NO MATCH` sobre artefactos analizados; estado 13.52 `UNVERIFIED` | La ISO es BD-J; los binarios WebKit son WPE/Linux excluido |

No se ejecutó el correlador sobre `scanner_1304.iso`, `hen.bin` o `libkernel_sys_13.52.bin` porque no son árboles fuente compatibles y hacerlo produciría resultados sin valor semántico. El correlador sólo debe usarse sobre fuentes o extracciones textuales autorizadas.

## E. Conclusión

**A)** El segundo rootfs no fue localizado. No existe otro directorio `rootfs` local fuera del WPE conocido.

**B)** Sí apareció una imagen BD-J local `scanner_1304.iso` con UDF, BDJO, JAR y clases históricas, pero su propio volumen se identifica como `scanner_1304`; no es una extracción 13.52.

**C)** No hay evidencia suficiente para atribuir ningún candidato a PS4 13.52. `libkernel_sys_13.52.bin` es un artefacto ya conocido y duplicado, no el segundo rootfs ni WebKit.

**D)** No se encontró `libSceNKWebKit`, `libkernel_web` real, SELF, SPRX, `system_ex`, `eboot.bin`, filesystem Orbis ni WebKit/JSC retail.

**E)** La imagen BD-J permite análisis estático de clases y rutas BD-J históricas, pero no reconstruye el runtime JSC/WebKit. Las tres familias permanecen `UNVERIFIED` para 13.52.

**F)** El siguiente paso de mayor valor sigue siendo una extracción real o metadata verificable de PS4 13.52 que contenga `libSceNKWebKit`, un snapshot de filesystem con `/app0/bdjstack`, o un manifest con ruta, tamaño, SHA-256 y procedencia del runtime.

## Manifest y validación

El escaneo reproducible se conservó en:

```text
/home/ubuntu/second_rootfs_locator_report.txt
```

El script usado fue:

```text
/home/ubuntu/second_rootfs_locator.py
```

No se modificaron ni eliminaron los artefactos auditados. El informe y los scripts auxiliares se dejaron fuera de cualquier commit/push.

- `py_compile`: PASS para los scripts de auditoría/correlación.
- Tests existentes: 31 PASS, 2 SKIPPED.
- `git diff --check`: PASS.
- Ejecución de binarios, clases o ISO: NOT RUN.
- Exploits/PoC/payloads: NOT RUN.
- Hardware: NOT USED.
- Commit/push: no realizados.
