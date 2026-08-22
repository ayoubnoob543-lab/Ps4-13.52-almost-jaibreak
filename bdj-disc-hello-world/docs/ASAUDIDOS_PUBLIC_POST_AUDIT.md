# Auditoría pública de publicaciones y herramientas relacionadas con ASaudidos

## Alcance

Se revisaron páginas públicas y referencias indexadas relacionadas con `@ASaudidos`, BD-J, PS4 13.52 y herramientas de investigación. No se descargaron ni ejecutaron payloads, binarios o exploits. Las afirmaciones de terceros se mantienen separadas de la evidencia directa.

## Publicación original revisada

La publicación `https://x.com/ASaudidos/status/2084139516877574245` muestra una solicitud de Jose Coixao para que `@ASaudidos` enviara una notificación Hello World con su BD-J en 13.52. La respuesta pública de `@ASaudidos` es `check it` junto con un vídeo. El texto visible no identifica el programa usado, no publica código, no proporciona hashes y no demuestra qué primitive o permisos se obtuvieron.

Clasificación: **DOCUMENTED_ONLY** para la existencia de una demostración pública; **UNVERIFIED** para la implementación, herramienta y mecanismo técnico.

Otra publicación pública de terceros, `https://x.com/Slient_Logic/status/2079535410599071931`, describe la demostración como sandbox escape/userland en 13.50 y posiblemente 13.52. La propia página indica que el post no está disponible. El autor del post se identifica además como comentarista y no como desarrollador o tester. Por ello, el texto es una afirmación de terceros, no evidencia directa de la primitive.

Clasificación: **DOCUMENTED_ONLY** y **UNVERIFIED_13.52**.

## Repositorio público relacionado encontrado

Se localizó `https://github.com/adri22235/ps4-suid-scanner`. Su README se presenta como investigación de PS4 13.04 y enumera un escáner BD-J, offsets parciales de 13.52 y una ISO preconstruida. También afirma que BD-JB funciona hasta ciertos firmwares y que algunas superficies están parcheadas en 13.50. El repositorio contiene archivos con nombres de payload, loader, llamadas nativas, offsets y binarios.

Este repositorio no demuestra que sea la herramienta utilizada por ASaudidos. Tampoco es apropiado incorporarlo al proyecto benigno: su propio README describe funciones de acceso nativo, escaneo del sistema y escritura de resultados en USB. No se descargó, compiló ni ejecutó.

Clasificación: **PUBLIC_REFERENCE_ONLY** para identificar vocabulario y procedencia; **OUT_OF_SCOPE** para el disco benigno; **UNVERIFIED** como herramienta de ASaudidos.

## Qué puede servir al proyecto benigno

La información útil y segura es únicamente documental:

| Elemento | Utilidad segura |
|---|---|
| Nombre `BD-JB` y demostración Hello World | Contexto histórico para distinguir carga BD-J de impacto de seguridad |
| Referencia a PS4 13.52 | Pista pública, no confirmación técnica |
| Estructura de una ISO BD-J | Comparación de authoring, sin copiar código de explotación |
| Mención de offsets o llamadas nativas | Sólo contexto; no debe incorporarse al Xlet |
| Escritura en USB | No se añade: requeriría acceso a dispositivos y permisos fuera del cascarón |

## Resultado

La búsqueda sí encontró material público que explica que existen demostraciones y repositorios relacionados con BD-J. No encontró una identificación verificable del programa exacto usado por ASaudidos ni evidencia suficiente para reconstruir una vulnerabilidad de PS4 13.52. El proyecto local debe mantener la ISO y el cascarón benigno separados de esos materiales.

El siguiente paso seguro es usar la publicación como referencia documental y probar únicamente el cascarón propio para confirmar carga BD-J. Una carga exitosa no demostraría que la herramienta pública o la vulnerabilidad histórica funcionen en 13.52.

## Referencias

[1]: https://x.com/ASaudidos/status/2084139516877574245 "Publicación de ASaudidos con respuesta a Jose Coixao"
[2]: https://x.com/Slient_Logic/status/2079535410599071931 "Comentario público de Silent_Logic sobre la demostración"
[3]: https://github.com/adri22235/ps4-suid-scanner "Repositorio público ps4-suid-scanner"
