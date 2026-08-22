# BD-J Hello World Disc

Proyecto **benigno** de prueba de authoring BD-J. Su objetivo es generar una aplicación Blu-ray Disc Java mínima que inicialice un Xlet y muestre un mensaje `Hello World` en pantalla. No contiene exploits, payloads, código nativo, acceso a kernel, escape de sandbox ni lógica de jailbreak.

## Estado

El proyecto contiene un flujo reproducible basado en un SDK BD-J público fijado como submódulo Git. La compatibilidad con PS4 13.52 sigue sin afirmarse hasta una prueba autorizada en un reproductor BD-J compatible.

## Estructura

```text
src/org/homebrew/        Código fuente del Xlet benigno
build/                   JAR, árbol discdir, ISO y hashes generados
third_party/bdj-sdk/     SDK público fijado como submódulo Git
tools/                   Scripts estáticos de empaquetado/validación
docs/                    Notas de authoring y procedencia
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

Las validaciones locales se limitan a comprobar estructura, nombres, tamaños, hashes, manifests y formato de la imagen. No se ejecutan JARs, ISOs, clases compiladas ni código procedente de la consola. La ISO UDF 2.50 actual mide 16 MiB y tiene SHA-256 `66fb8408dd9a7ff1f7053d3b87a0bfbd3d7617005ca12c26b2a6ce5fea596baf`. La compatibilidad real con una PS4 sólo puede determinarse mediante una prueba autorizada en hardware propio.

## Fuentes públicas

- [BD-J SDK de john-tornblom](https://github.com/john-tornblom/bdj-sdk)
- [HDcookbook](https://github.com/enteractive-dev/hdcookbook)
- [Documentación Oracle BD-J](https://www.oracle.com/technical-resources/articles/javabluray.html)

## Alcance excluido

No se incluyen instrucciones para BD-JB, HEN, GoldHEN, payloads, escalada de privilegios, native usermode, kernel execution o bypasses de seguridad.
