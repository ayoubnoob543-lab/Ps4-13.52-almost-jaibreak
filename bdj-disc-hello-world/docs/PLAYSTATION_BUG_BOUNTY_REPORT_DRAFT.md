# Draft de reporte técnico para PlayStation Bug Bounty

**Estado del documento:** borrador de validación; no afirmar vulnerabilidad hasta obtener evidencia adicional.

## 1. Título provisional

**BD-J Hello World: validación de ejecución de un Xlet benigno en una imagen Blu-ray reproducible**

> Este título describe una prueba de funcionamiento. No debe presentarse como vulnerabilidad.

## 2. Resumen ejecutivo

Se construyó una imagen Blu-ray Disc Java (BD-J) benigna y reproducible a partir de un SDK público. La imagen contiene un Xlet que inicializa una escena gráfica y muestra el texto `Hello World — BD-J test`. El proceso usa stubs BD-J públicos, JDK8, un firmador público del SDK y `makefs` para crear una imagen UDF 2.50.

La evidencia disponible demuestra la generación de una imagen BD-J válida desde el punto de vista del proyecto y del empaquetado local. **No demuestra todavía que una PS4 13.52 acepte la imagen, ni que exista una vulnerabilidad, escape del sandbox, ejecución nativa o acceso al kernel.**

## 3. Producto, versión y entorno

- Producto a probar: PS4 de pruebas autorizada.
- Firmware objetivo: PS4 13.52; compatibilidad de esta ISO: **UNVERIFIED**.
- Entorno de authoring: Ubuntu 24.04.
- SDK: `john-tornblom/bdj-sdk`, commit `9c48049b920514388952ea89cda13fc940ff2183`.
- Stubs: `target/lib/enhanced-stubs.zip`.
- Compilador: OpenJDK 8 (`1.8.0_492`), con bytecode BD-J `-source 1.3 -target 1.3`.
- Formato de imagen: UDF 2.50, volumen `BDJHELLO`, tamaño 16 MiB.

## 4. Artefactos entregados

| Artefacto | SHA-256 | Función |
|---|---|---|
| `build/bdj-hello-world.iso` | `ad043fc4a1ac6ecd1a9a5cabb876e6daa849d52e5ec1afb3de29822dff148fdb` | Imagen BD-J de prueba |
| `build/discdir/BDMV/JAR/00000.jar` | `7cff985677ca0511afeaf35b89f0f7eb0e192708ddb39030734979269fcc7065` | JAR firmado del Xlet |
| `build/discdir/BDMV/BDJO/00000.bdjo` | `d32325af03d55c054fe7766cc96a8bb14cd10a0c5dc06a3a58938f04427cdea5` | Descriptor que referencia `org.homebrew.MyXlet` |
| `src/org/homebrew/MyXlet.java` | `3d8086a6faa09ff235f43d52e3e1984fa1f1ee68a0e8830f3624626d5de5c1fc` | Fuente del Xlet benigno |

## 5. Comportamiento previsto

Al cargar la imagen en un reproductor BD-J compatible, el Xlet debería inicializarse y mostrar un panel gráfico con el texto `Hello World — BD-J test` y `Benign authoring validation only`.

El Xlet no realiza llamadas de red, carga dinámica, acceso privilegiado al sistema de archivos, reflexión, uso de `Unsafe`, ejecución de procesos, carga de bibliotecas nativas, corrupción de memoria ni desactivación de controles de seguridad.

## 6. Procedimiento de reproducción segura

1. Verificar el SHA-256 de la ISO antes de grabarla o transferirla.
2. Utilizar únicamente una PS4 de pruebas autorizada y un medio/método de carga permitido por el propietario del equipo.
3. Observar si el reproductor reconoce el disco y si el Xlet muestra el mensaje esperado.
4. Registrar modelo, firmware, método de carga, hora, resultado, vídeo y mensajes visibles.
5. No modificar el firmware, no cargar archivos adicionales y no intentar operaciones fuera del comportamiento BD-J normal.

## 7. Resultados que deben distinguirse

| Observación | Interpretación | ¿Vulnerabilidad? |
|---|---|---|
| La imagen se reconoce | El medio o la imagen son legibles | No demostrado |
| Se muestra `Hello World` | Ejecución BD-J normal | No |
| El Xlet recibe un permiso documentado | Comportamiento esperado o dependiente de la plataforma | No por sí solo |
| Se observa un permiso inesperado | Anomalía que requiere reproducción y análisis independiente | Indeterminado |
| Se ejecuta código fuera del Xlet o se cruza el sandbox | Impacto de seguridad potencial | Requiere evidencia fuerte y reporte separado |

## 8. Afirmaciones que no deben hacerse

No debe afirmarse que la imagen contiene un exploit, que prueba una vulnerabilidad de PS4 13.52, que produce native usermode, que permite jailbreak, que alcanza el kernel o que reproduce una vulnerabilidad histórica de BD-J. Ninguna de esas afirmaciones está respaldada por los artefactos actuales.

## 9. Evidencia faltante para un reporte de vulnerabilidad

Para transformar este documento en un reporte de seguridad sería necesario disponer de una condición vulnerable concreta, un impacto demostrable, una reproducción mínima y evidencia específica de la versión afectada. La ejecución del Hello World sólo cubre la disponibilidad del canal BD-J.

## 10. Clasificación actual

| Elemento | Clasificación |
|---|---|
| ISO generada localmente | CONFIRMED_LOCAL |
| JAR firmado y BDJO empaquetados | CONFIRMED_LOCAL |
| Compatibilidad con PS4 13.52 | UNVERIFIED |
| Vulnerabilidad de BD-J | NOT DEMONSTRATED |
| Escape del sandbox | NOT DEMONSTRATED |
| Ejecución nativa | NOT DEMONSTRATED |
| Ejecución de kernel | OUT OF SCOPE |

## 11. Información de divulgación responsable

El informe final debe enviarse únicamente mediante el canal oficial de PlayStation Bug Bounty y debe seguir sus reglas actuales de alcance, formato y divulgación. No deben adjuntarse exploits operativos, payloads ni datos de otros investigadores. Si sólo existe esta evidencia, el asunto correcto es una **validación técnica**, no un reporte de vulnerabilidad.

## Referencias

[1]: https://github.com/john-tornblom/bdj-sdk "john-tornblom/bdj-sdk"
[2]: https://github.com/oliverlietz/bd-j "Mavenized BD-J and HD Cookbook tools"
[3]: https://www.oracle.com/technical-resources/articles/javabluray.html "Oracle: Java Blu-ray authoring background"
[4]: ../README.md "README del proyecto BD-J Hello World"
[5]: validation.json "Validación estática reproducible del proyecto"
