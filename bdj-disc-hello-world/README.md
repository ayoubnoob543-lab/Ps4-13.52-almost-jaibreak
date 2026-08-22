# BD-J Hello World Disc

Proyecto **benigno** de prueba de authoring BD-J. Su objetivo es generar una aplicación Blu-ray Disc Java mínima que inicialice un Xlet y muestre un mensaje `Hello World` en pantalla.

**No contiene exploits, payloads, código nativo, acceso a kernel, escape de sandbox ni lógica de jailbreak.**

## Situación exacta

| Afirmación | Estado |
|---|---|
| ¿Carga en la PS4? | **No sabemos** — no se ha probado en el reproductor BD-J propietario |
| Validación de la ISO | Solo Linux, estructura UDF/BDMV (sin ejecución) |
| Hello World = vulnerabilidad | **No** — comportamiento normal de BD-J si la consola lo acepta |
| Primitive de seguridad | **No** (ni memoria, ni tipos, ni UAF, ni R/W arbitraria) |
| Escape del sandbox | **No** |
| Ejecución nativa | **No** (sin ELF, payload, carga dinámica ni native) |
| Acceso al kernel | **No** |
| Evidencia específica PS4 13.52 | **No** — SDK/plantilla públicos y genéricos |
| Impacto Bug Bounty | **No** — sin condición vulnerable ni impacto reproducible |

### Qué sí tenemos

ISO BD-J reproducible, JAR firmado, BDJO coherente, código fuente, Makefile, hashes, documentación y paquete textual para revisión. Eso prueba que el disco está **bien construido**, no que contenga un exploit.

## Estructura

```text
src/org/homebrew/        Código fuente del Xlet benigno
build/                   JAR, árbol discdir, ISO y hashes generados
third_party/bdj-sdk/     SDK público fijado como submódulo Git
tools/                   Scripts estáticos de empaquetado/validación
docs/                    Notas de authoring, estado y reporte
```

## Dependencias y build

El submódulo `third_party/bdj-sdk` aporta los stubs BD-J `target/lib/enhanced-stubs.zip`, la plantilla BDMV/BDJO, `bdsigner` y el código público de `makefs_termux`. El build usa JDK8 para producir bytecode compatible con BD-J y `libbsd-dev` para compilar `makefs`.

```console
git clone --recurse-submodules <repository-url>
cd bdj-disc-hello-world/third_party/bdj-sdk
ln -sfn /usr/lib/jvm/java-8-openjdk-amd64 host/jdk8
make -C host/src/makefs_termux
make -C host/src/makefs_termux install DESTDIR="$PWD/host"
cd ../../..
JAVA8_HOME="$PWD/third_party/bdj-sdk/host/jdk8" make all
python3 tools/validate_project.py
```

El resultado se escribe en `build/bdj-hello-world.iso` y su hash en `build/bdj-hello-world.iso.sha256`.

## Validación segura

Las validaciones locales se limitan a comprobar estructura, nombres, tamaños, hashes, manifests y formato de la imagen. **No se ejecutan** JARs, ISOs, clases compiladas ni código procedente de la consola.

| Artefacto | SHA-256 |
|---|---|
| `build/bdj-hello-world.iso` (16 MiB, UDF 2.50) | `ad043fc4a1ac6ecd1a9a5cabb876e6daa849d52e5ec1afb3de29822dff148fdb` |

La compatibilidad real con una PS4 **sólo** puede determinarse mediante una prueba autorizada en hardware propio.

## Fuentes públicas

- [BD-J SDK de john-tornblom](https://github.com/john-tornblom/bdj-sdk)
- [HDcookbook](https://github.com/enteractive-dev/hdcookbook)
- [Documentación Oracle BD-J](https://www.oracle.com/technical-resources/articles/javabluray.html)

## Alcance excluido

No se incluyen instrucciones para BD-JB, HEN, GoldHEN, payloads, escalada de privilegios, native usermode, kernel execution o bypasses de seguridad.

Ver también: [`docs/BUILD_STATUS.md`](docs/BUILD_STATUS.md), [`docs/PLAYSTATION_BUG_BOUNTY_REPORT.md`](docs/PLAYSTATION_BUG_BOUNTY_REPORT.md).
