# Investigación pública sobre authoring BD-J legítimo — Sesión 74

## Fuentes consultadas

[1] Oracle, “Blu-ray Disc Application Development with Java ME, Part 1: Creating Your First Application”, septiembre de 2008: https://www.oracle.com/technical-resources/articles/javabluray.html

[2] oliverlietz/bd-j, “free open source tools and documentation around Blu-ray”, GitHub: https://github.com/oliverlietz/bd-j

[3] HDcookbook, “HDcookbook - a place for Blu-ray Disc Java and GEM”: https://jovial.com/hdcookbook_repo/index.html

## Hallazgos verificables

Oracle describe BD-J como una plataforma Java ME para aplicaciones en discos Blu-ray y enumera como requisitos de desarrollo una máquina de trabajo compatible, una unidad grabadora Blu-ray y medios BD-RE para pruebas. La misma fuente distingue el disco, los títulos, los menús, el ciclo de vida de los Xlets y las APIs BD-J (`org.bluray.*`), GEM/MHP, Java TV y Personal Basis Profile. También indica que un Xlet BD-J puede dibujar texto, imágenes y animación, responder a entradas y controlar reproducción; estas capacidades no equivalen a escape de sandbox ni a ejecución nativa.

El repositorio `oliverlietz/bd-j` contiene herramientas Maven separadas en `AuthoringTools/` y `DiscCreationTools/`. Su README indica que antes de compilar hay que configurar una definición de plataforma BD-J y ejecutar `mvn clean install` en ambos módulos. El README advierte que existen componentes con problemas conocidos, por lo que la disponibilidad del código no equivale a un flujo moderno garantizado.

HDcookbook describe herramientas para crear imágenes de disco BD-J, ejemplos de Xlets y un proyecto `HelloWorldXlet` que puede generar una imagen BD-J sencilla. También documenta una imagen de disco de ejemplo y herramientas de creación de BDJO y seguridad para generar certificados, firmar JARs BD-J y firmar BUMF. La página explica que la imagen debe ensamblarse y puede grabarse en un BD-RE para reproducirse en reproductores Blu-ray compatibles; esta evidencia se refiere al funcionamiento BD-J estándar y no a la PS4 13.52 específicamente.

## Implicación para nuestro proyecto

Para una demo BD-J legítima necesitamos como mínimo: un Xlet compatible con la plataforma BD-J objetivo, una definición de plataforma y toolchain que permita compilarlo, la estructura BD-J/BDMV correspondiente, BDJO/BUMF y firmas según el perfil del disco, una imagen de disco generada y un medio BD-RE o un método de prueba compatible. El corpus actual del laboratorio no demuestra que todos esos componentes estén instalados ni que una imagen genérica de HDcookbook sea compatible con el runtime BD-J específico de PS4 13.52.

La fuente pública más concreta para un “Hello World” estándar es HDcookbook, pero no se debe confundir con BD-JB ni adaptarla para escape de sandbox. Cualquier prueba futura debe limitarse a una aplicación legítima, revisar estáticamente sus archivos y registrar hashes antes de una eventual prueba autorizada en hardware propio.

## Límites

Las fuentes consultadas no proporcionan el runtime BD-J propietario de PS4 13.52, sus `rt.jar`/`bdjstack.jar`, sus clases internas, ni una garantía de que el flujo genérico de HDcookbook se ejecute sin cambios en PS4. Tampoco prueban una ruta BD-J hacia WebKit, native usermode o kernel.

## Fuentes adicionales

[4] Oracle Java ME SDK, “Compiling, Deploying, and Running a Stubs for BD-J Platform Project”: https://docs.oracle.com/javame/dev-tools/jme-sdk-3.0-win/html-helpset/z40005431292529.html

[5] zathras/java.net, directorio archivado `hdcookbook`: https://github.com/zathras/java.net/tree/master/hdcookbook

La documentación del Java ME SDK indica que un proyecto BD-J de plataforma externa puede compilarse/desplegarse en un directorio de deployment, abrirse con un reproductor que soporte BDMV y, para crear un disco reproducible, grabarse ese directorio en un Blu-ray. Esto describe un flujo estándar de authoring y reproducción, no compatibilidad específica con PS4 13.52.

El archivo archivado de HDcookbook declara que fue actualizado para JDK 1.8 y probado en 2022 con OpenJDK 8 y Apache Ant. Incluye `AuthoringTools`, `DiscCreationTools`, `xlets`, scripts de build y utilidades de seguridad. Su README muestra que el flujo de build estándar puede ejecutarse en Ubuntu/macOS con JDK 8 y Ant, pero no demuestra que la definición de plataforma BD-J de Sony/PS4 esté disponible ni que una imagen generada sea aceptada por PS4.

La página de Oracle sobre BD-J (fuente [1]) no pudo extraerse completamente en su segunda parte; no se usa esa URL como soporte de detalles adicionales.

## Detalles concretos del flujo público

[6] Blu-Play, “Getting started”: https://www.blu-play.com/developer/getting-started

Blu-Play describe un entorno BD-J restringido basado en Java 1.3/AWT, sin SDL/OpenGL ni APIs 3D, y señala un límite de 4 MiB para el JAR de la aplicación, con posibilidad de mantener recursos fuera del JAR. Su flujo mínimo usa un `bdj.jar` de clases de plataforma como classpath y compilación `javac -source 1.3 -target 1.3`; después se empaquetan las clases en un JAR y se añade un archivo de solicitud de permisos. La fuente ofrece un ejemplo `HelloWorld` con `Xlet`, `HSceneFactory` y AWT.

La misma fuente afirma que la firma no es necesaria para un juego simple y la reserva para acceso a archivos fuera del JAR o red. Esta afirmación es una guía de Blu-Play y no debe extrapolarse automáticamente al runtime propietario de PS4. La fuente propone probar con reproductores de software como PowerDVD o VLC abriendo una carpeta Blu-ray/ISO; esto valida el authoring en un reproductor compatible, no la compatibilidad de PS4 13.52.

La documentación de `net.java.bd.tools.security` [7] https://github.com/oliverlietz/bd-j/blob/master/DiscCreationTools/net.java.bd.tools.security/README.md añade que los JAR BD-J firmados necesitan el atributo de manifest `BDJ-Signature-Version: 1.0`, que un JAR BD-J puede requerir certificados de raíz de aplicación y que BUMF se firma por separado cuando se usa VFS. Estas son exigencias de authoring BD-J estándar; no constituyen permisos privilegiados ni una ruta hacia native usermode.
