# Build del WebKit OSS histórico PS4OSSCode

## Corpus identificado

El corpus Git local es `FreeBSDKernel9-0/PS4OSSCode`, fijado en `d636699770323d7968a2c37955aa513bda5f8a37`:

```text
/home/ubuntu/ps4-lab-1352/analysis/webkit_oss_sources_2026-08-19/PS4OSSCode
```

El checkout físico de sus subárboles está incompleto o ausente, pero los objetos Git contienen la familia `WebKit-601-1300/WebKit-601-1300`, incluyendo `Source/JavaScriptCore`, `Source/WTF`, `Source/WebCore`, `Source/WebKit`, `Source/WebKit2`, `Source/cmake`, `CMakeLists.txt` y los scripts de build. Por esta razón el probe distingue `git_required_files=true` de `required_files=false`: hay que crear un archive/checkout de trabajo antes de usar CMake.

## Ports disponibles

El CMake histórico declara los ports `Efl`, `GTK`, `AppleWin`, `WinCairo`, `Mac` y `Manx`. `GTK` es el candidato host público. `Manx` es el port Orbis/PlayStation del árbol, no un port host: exige la variable `ORBIS`, headers públicos de plataforma, bibliotecas de plataforma y dependencias gráficas. No se usa como sustituto ni se rellenan sus variables con datos inventados.

## Intento de configuración host

Se creó temporalmente un archive aislado de `WebKit-601-1300` que se eliminó después de la prueba para no llenar el repositorio ni modificar el corpus. El comando fue equivalente a:

```sh
cmake -S <archive-601-1300> -B <build> -G Ninja \
  -DPORT=GTK -DENABLE_TOOLS=OFF -DENABLE_WEBKIT=OFF \
  -DENABLE_WEBKIT2=OFF -DENABLE_MINIBROWSER=OFF \
  -DENABLE_API_TESTS=OFF -DENABLE_GTKDOC=OFF \
  -DENABLE_INTROSPECTION=OFF -DENABLE_OPENGL=OFF \
  -DENABLE_GLES2=OFF -DENABLE_WEBGL=OFF -DENABLE_VIDEO=OFF
```

La primera configuración bloqueó por Ruby incompleto. Se reparó la biblioteca pública `libruby3.2`; la siguiente configuración alcanzó la detección de ports y falló en la dependencia `Cairo` porque el sistema no tiene el paquete de desarrollo/metadata `cairo.pc` requerido por `FindCairo.cmake`. La configuración no generó un build ni un binario histórico.

## Dependencias host observadas

El `OptionsGTK.cmake` histórico exige, entre otras, Cairo, Fontconfig, Freetype2, HarfBuzz, ICU, JPEG, LibSoup 2.42, LibXml2, LibXslt, PNG, SQLite, Threads, Zlib, ATK, WebP, GTK3 y GDK3; además puede requerir OpenGL/EGL y varias dependencias opcionales. El entorno tiene algunas bibliotecas runtime, pero faltan varios paquetes `-dev` y sus archivos `pkg-config`. El almacenamiento quedó con aproximadamente 264 MB libres, por lo que instalar el conjunto GTK completo no es viable sin liberar espacio del laboratorio o aportar un entorno de build separado.

## Herramientas instaladas

Se instalaron herramientas públicas mínimas: CMake, Ninja y Gperf. Bison, Flex, Perl, Python y Ruby están disponibles. No se instaló ni se inventó un SDK Orbis, sysroot PS4, módulo Sony, biblioteca `.sprx` ni ABI retail.

## Estado de integración

El `minimal-browser` conserva su smoke JSC host independiente. El árbol histórico real queda integrado como **fuente/procedencia de build documentada**, no como biblioteca compilada. Añadir WebCore/WebKit al binario exige completar primero la ruta GTK host y sus dependencias, además de generar headers y resolver el sistema de build histórico.

La ruta Manx/Orbis permanece bloqueada por dependencias de plataforma que no están disponibles legalmente en este entorno. Esto no se puede resolver mediante stubs de nombres inventados: sólo pueden añadirse adaptadores genéricos si existe una API pública documentada.

> Resultado: `HISTORICAL_OSS_SOURCE_CONFIRMED`, `HOST_BUILD_BLOCKED_BY_DEPENDENCIES`, `ORBIS_PORT_BLOCKED`, `RETAIL_13_52_MISSING`.

## Reproducción futura

Para reintentar el build host, se necesita un workspace con espacio suficiente, un archive completo de `WebKit-601-1300`, los paquetes de desarrollo indicados y una versión compatible de los scripts Python/Ruby históricos. Para el port PS4 se necesitaría además un toolchain/sysroot OpenOrbis autorizado y documentación pública suficiente de la plataforma; ningún dato retail se deriva de este corpus.
