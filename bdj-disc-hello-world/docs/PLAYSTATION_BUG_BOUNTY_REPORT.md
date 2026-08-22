# Informe técnico para PlayStation Bug Bounty

**Estado:** validación técnica; no se afirma una vulnerabilidad.

## Resumen ejecutivo

Se construyó una imagen Blu-ray Disc Java (BD-J) benigna y reproducible para validar el flujo de authoring. La imagen contiene un Xlet que inicializa una escena gráfica y muestra `Hello World — BD-J test`. El proyecto utiliza un SDK BD-J público fijado a una revisión concreta, stubs públicos, JDK8, un firmador del SDK y `makefs` para producir una imagen UDF 2.50 [1] [2].

La evidencia actual demuestra que la imagen puede generarse de forma reproducible en el entorno de authoring. **No demuestra todavía que una PS4 13.52 acepte la imagen ni demuestra una vulnerabilidad, un escape del sandbox, ejecución nativa, jailbreak o acceso al kernel.**

## Producto y entorno

| Campo | Valor |
|---|---|
| Producto objetivo | PS4 de pruebas autorizada |
| Firmware objetivo | PS4 13.52; compatibilidad de esta imagen: `UNVERIFIED` |
| Entorno de authoring | Ubuntu 24.04 |
| SDK | `john-tornblom/bdj-sdk` |
| Revisión del SDK | `9c48049b920514388952ea89cda13fc940ff2183` |
| Stubs | `target/lib/enhanced-stubs.zip` |
| Compilador | OpenJDK 8, `1.8.0_492` |
| Perfil de compilación | `-source 1.3 -target 1.3` |
| Formato | UDF 2.50 |
| Tamaño de ISO | 16 MiB |
| Volumen | `BDJHELLO` |

## Componentes y artefactos

El Xlet es `org.homebrew.MyXlet`. Su comportamiento se limita a crear una `HScene`, añadir un panel gráfico y pintar dos líneas de texto. No realiza llamadas de red, carga dinámica, reflexión, acceso privilegiado al sistema de archivos, uso de `Unsafe`, ejecución de procesos, carga de bibliotecas nativas, corrupción de memoria ni desactivación de controles de seguridad.

| Artefacto | SHA-256 | Descripción |
|---|---|---|
| `build/bdj-hello-world.iso` | `ad043fc4a1ac6ecd1a9a5cabb876e6daa849d52e5ec1afb3de29822dff148fdb` | Imagen BD-J UDF 2.50 |
| `build/discdir/BDMV/JAR/00000.jar` | `7cff985677ca0511afeaf35b89f0f7eb0e192708ddb39030734979269fcc7065` | JAR firmado del Xlet |
| `build/discdir/BDMV/BDJO/00000.bdjo` | `d32325af03d55c054fe7766cc96a8bb14cd10a0c5dc06a3a58938f04427cdea5` | Descriptor BDJO |
| `src/org/homebrew/MyXlet.java` | `3d8086a6faa09ff235f43d52e3e1984fa1f1ee68a0e8830f3624626d5de5c1fc` | Fuente del Xlet |

## Reproducción segura

La prueba debe realizarse sólo en una unidad autorizada y mediante un medio o método de carga permitido por el propietario del equipo. Antes de usar la imagen, debe verificarse su SHA-256. Después se debe registrar el modelo de PS4, la versión de firmware, el método de carga, la hora de la prueba, el resultado visible y cualquier mensaje de error.

El resultado esperado es que el reproductor reconozca la imagen y, si la implementación BD-J es compatible con esta authoring, muestre el mensaje del Xlet. No se deben cargar archivos adicionales, modificar el firmware ni ejecutar operaciones fuera del ciclo normal de BD-J.

## Interpretación de resultados

| Observación | Qué permite concluir | Clasificación |
|---|---|---|
| La imagen no se reconoce | Incompatibilidad del medio, formato o método de carga | `UNVERIFIED` |
| La imagen se reconoce | El medio o la imagen son legibles | `CONFIRMED_LOCAL`, sin impacto de seguridad |
| Aparece `Hello World` | Ejecución BD-J normal | `CONFIRMED_LOCAL`, no vulnerabilidad |
| Una API documentada funciona | Comportamiento esperado del runtime | `CONFIRMED_LOCAL`, no vulnerabilidad por sí solo |
| Una operación no permitida falla | El control observado está activo en esa prueba | Evidencia limitada al entorno probado |
| Aparece un permiso o comportamiento inesperado | Anomalía que requiere reproducción independiente | `UNVERIFIED` |
| Se cruza el sandbox o se ejecuta código no solicitado | Posible impacto de seguridad | Requiere reporte separado y evidencia fuerte |

## Qué no demuestra este artefacto

El disco no contiene una prueba de concepto de escape del sandbox ni una cadena de explotación. No demuestra que exista una vulnerabilidad en BD-J 13.52, que una vulnerabilidad histórica siga presente, que el WebKit de PS4 sea vulnerable, que exista ejecución native usermode o que sea posible alcanzar el kernel. La ejecución satisfactoria del Xlet sólo validaría el canal BD-J y el empaquetado de la imagen.

## Evidencia necesaria para un reporte de vulnerabilidad

Para presentar un reporte de seguridad sería necesario identificar una condición concreta, demostrar su impacto real en una versión específica y aportar una reproducción mínima, estable y autorizada. El informe tendría que incluir el componente afectado, la causa técnica, las precondiciones, los pasos de reproducción, los resultados observados, los logs o capturas, los hashes de los artefactos y una explicación de por qué el comportamiento excede las capacidades normales de BD-J.

No debe afirmarse una vulnerabilidad basándose únicamente en nombres históricos de clases, similitud con otro firmware, ejecución de un Xlet benigno o comentarios de terceros. Tampoco deben adjuntarse exploits operativos, payloads nativos, cadenas de jailbreak o material de otros investigadores.

## Estado actual y siguiente paso

El estado actual es **validación de authoring BD-J completada localmente**. La compatibilidad con una PS4 13.52 permanece `UNVERIFIED` hasta una prueba autorizada. Si la imagen carga, el siguiente paso seguro es registrar el resultado y, si fuera necesario, ampliar el diagnóstico con comprobaciones pasivas de APIs y permisos documentados, sin intentar eludir el sandbox.

Si sólo aparece el mensaje Hello World, no existe base para un reporte de vulnerabilidad. Si se observa una anomalía, debe conservarse la imagen como baseline limpio y preparar un informe separado centrado exclusivamente en esa anomalía, sin convertir el Xlet en un exploit.

## Referencias

[1]: https://github.com/john-tornblom/bdj-sdk "john-tornblom/bdj-sdk"
[2]: https://github.com/oliverlietz/bd-j "Herramientas BD-J y HD Cookbook mavenizadas"
[3]: https://www.oracle.com/technical-resources/articles/javabluray.html "Oracle: antecedentes de authoring Java Blu-ray"
[4]: ../README.md "README del proyecto BD-J Hello World"
[5]: validation.json "Validación estática reproducible del proyecto"
