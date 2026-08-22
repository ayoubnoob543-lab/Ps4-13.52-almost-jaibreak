# Informe técnico para PlayStation Bug Bounty

**Estado:** validación técnica de authoring BD-J; **no se afirma una vulnerabilidad**.

## Situación exacta (checklist)

| Punto | Estado |
|---|---|
| ¿Carga en la PS4? | **No sabemos** |
| Validación de la ISO | Solo Linux, estructura UDF/BDMV. No se ha probado en el reproductor BD-J propietario de PS4. |
| Hello World = vulnerabilidad | **No.** Sólo demuestra que un Xlet benigno puede inicializarse y dibujar una interfaz *si* la consola lo acepta. Comportamiento normal de BD-J. |
| Primitive de seguridad | **No.** No hay corrupción de memoria, confusión de tipos, UAF, lectura/escritura arbitraria ni ejecución de código demostrada. |
| Escape del sandbox | **No.** El Xlet no intenta ni demuestra acceso a permisos elevados, rutas protegidas, USB arbitrario, procesos o bibliotecas nativas. |
| Ejecución nativa | **No.** Sin ELF, payload, carga dinámica ni llamada a código nativo. |
| Acceso al kernel | **No.** El proyecto no contiene ni prueba una cadena hacia kernel execution. |
| Evidencia específica PS4 13.52 | **No.** El SDK y la plantilla son públicos y genéricos; no equivalen al runtime propietario de PS4 13.52. |
| Impacto para Bug Bounty | **No.** Sin condición vulnerable e impacto reproducible, Sony no tendría base para aceptar un reporte como vulnerabilidad. |

## Cadena de vulnerabilidad — estado actual

| # | Etapa | Descripción | Estado en este proyecto |
|---|-------|-------------|-------------------------|
| 1 | **Trigger del fallo** | Provoca la condición vulnerable concreta del runtime BD-J/WebKit | **No existe**; el cascarón sólo inicia y muestra texto |
| 2 | **Primitive** | Convierte el fallo en una capacidad controlable (violación de memoria o de permisos) | **No existe** |
| 3 | **Puente de privilegios** | Usa esa capacidad para cruzar la frontera del sandbox | **No existe** |
| 4 | **Ejecución / efecto** | Demuestra el resultado posterior (invocar función permitida o cargar acción controlada) | **No existe** |
| 5 | **Entrega opcional** | Mecanismo para transportar datos (archivo local, USB, etc.) | Solo transporte; **no es la vulnerabilidad** |

Sin las etapas 1–4 no hay vulnerabilidad demostrable ni impacto de seguridad.

### Qué sí tenemos

ISO BD-J reproducible, JAR firmado, BDJO coherente, código fuente, Makefile, hashes, documentación y paquete textual para revisión. Eso prueba que el disco está **bien construido**, no que contenga un exploit.

## Resumen ejecutivo

Se construyó una imagen Blu-ray Disc Java (BD-J) benigna y reproducible para validar el flujo de authoring. La imagen contiene un Xlet que inicializa una escena gráfica y muestra `Hello World — BD-J test`. El proyecto utiliza un SDK BD-J público fijado a una revisión concreta, stubs públicos, JDK8, un firmador del SDK y `makefs` para producir una imagen UDF 2.50 [1] [2].

La evidencia actual demuestra que la imagen puede generarse de forma reproducible en el entorno de authoring. **No demuestra que una PS4 13.52 acepte la imagen ni demuestra una vulnerabilidad, un escape del sandbox, ejecución nativa, jailbreak o acceso al kernel.**

## Producto y entorno

| Campo | Valor |
|---|---|
| Producto objetivo | PS4 de pruebas autorizada |
| Firmware objetivo | PS4 13.52; compatibilidad de esta imagen: `UNVERIFIED` |
| Entorno de authoring | Ubuntu 24.04 |
| SDK | `john-tornblom/bdj-sdk` |
| Revisión del SDK | `9c48049b920514388952ea89cda13fc940ff2183` |
| Stubs | `target/lib/enhanced-stubs.zip` |
| Compilador | OpenJDK 8 |
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

## Reproducción segura (si se prueba en hardware)

La prueba debe realizarse **sólo** en una unidad autorizada y mediante un medio o método de carga permitido por el propietario del equipo. Antes de usar la imagen, verificar su SHA-256. Registrar: modelo de PS4, versión de firmware, método de carga, hora, resultado visible y cualquier mensaje de error.

Resultado esperado: el reproductor reconoce la imagen y, **si** la implementación BD-J es compatible con esta authoring, muestra el mensaje del Xlet. No cargar archivos adicionales, no modificar el firmware, no ejecutar operaciones fuera del ciclo normal de BD-J.

## Interpretación de resultados

| Observación | Qué permite concluir | Clasificación |
|---|---|---|
| La imagen no se reconoce | Incompatibilidad del medio, formato o método de carga | `UNVERIFIED` |
| La imagen se reconoce | El medio o la imagen son legibles | `CONFIRMED_LOCAL`, sin impacto de seguridad |
| Aparece `Hello World` | Ejecución BD-J **normal** | `CONFIRMED_LOCAL`, **no vulnerabilidad** |
| Una API documentada funciona | Comportamiento esperado del runtime | `CONFIRMED_LOCAL`, no vulnerabilidad por sí solo |
| Una operación no permitida falla | El control observado está activo en esa prueba | Evidencia limitada al entorno probado |
| Aparece un permiso o comportamiento inesperado | Anomalía que requiere reproducción independiente | `UNVERIFIED` |
| Se cruza el sandbox o se ejecuta código no solicitado | Posible impacto de seguridad | Requiere reporte **separado** y evidencia fuerte |

## Qué no demuestra este artefacto

El disco **no** contiene una prueba de concepto de escape del sandbox ni una cadena de explotación. **No** demuestra que exista una vulnerabilidad en BD-J 13.52, que una vulnerabilidad histórica siga presente, que el WebKit de PS4 sea vulnerable, que exista ejecución native usermode o que sea posible alcanzar el kernel.

La ejecución satisfactoria del Xlet (si ocurre) **sólo** validaría el canal BD-J y el empaquetado de la imagen.

## Evidencia necesaria para un reporte de vulnerabilidad

Para presentar un reporte de seguridad sería necesario:

1. Identificar una **condición vulnerable concreta** (Trigger)
2. Demostrar una **primitive** controlable
3. Demostrar **cruzar el sandbox** (Puente de privilegios)
4. Demostrar **impacto real** en una versión específica (Ejecución/efecto)
5. Aportar una reproducción mínima, estable y autorizada

El informe tendría que incluir: componente afectado, causa técnica, precondiciones, pasos de reproducción, resultados observados, logs/capturas, hashes de artefactos, y por qué el comportamiento **excede** las capacidades normales de BD-J.

**No** debe afirmarse una vulnerabilidad basándose únicamente en:
- nombres históricos de clases
- similitud con otro firmware
- ejecución de un Xlet benigno
- comentarios de terceros

Tampoco deben adjuntarse exploits operativos, payloads nativos, cadenas de jailbreak o material de otros investigadores.

## Estado actual y siguiente paso

| Campo | Valor |
|---|---|
| Estado | Validación de authoring BD-J completada **localmente** (Linux, estático) |
| PS4 13.52 | `UNVERIFIED` — pendiente prueba autorizada en hardware |
| Impacto Bug Bounty | **Ninguno** con la evidencia actual |

Si la imagen carga y solo aparece Hello World → **no hay base** para un reporte de vulnerabilidad.

Si se observa una anomalía real → conservar esta imagen como baseline limpio y preparar un informe **separado** centrado exclusivamente en esa anomalía, sin convertir el Xlet en un exploit.

## Referencias

[1]: https://github.com/john-tornblom/bdj-sdk — john-tornblom/bdj-sdk  
[2]: https://github.com/oliverlietz/bd-j — Herramientas BD-J / HD Cookbook  
[3]: https://www.oracle.com/technical-resources/articles/javabluray.html — Oracle BD-J  
[4]: ../README.md — README del proyecto  
[5]: BUILD_STATUS.md — Estado exacto del build  
[6]: validation.json — Validación estática  
