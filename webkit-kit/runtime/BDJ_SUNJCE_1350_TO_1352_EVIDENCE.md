# SUNJCE: evidencia pública de PS4 13.50→13.52

**Autor:** Manus AI  
**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** investigación estática y documental exclusivamente sobre la hipótesis `sunjce`. No se descargaron PUPs, dumps privados ni runtime propietario; no se ejecutaron exploits, payloads, JAR/ELF/BIN ni hardware.

## Conclusión ejecutiva

La investigación encontró evidencia pública nueva y más fuerte que el simple índice de PSDevWiki:

1. PSDevWiki atribuye a `zecoxao` el diff de archivos BD-J decompilados de PS4 13.50 y 13.52.
2. La sección identifica el archivo/clase `RootCertManager.java` y afirma que cambió el hash `sunjce` en PS4 13.52.
3. La misma sección declara editorialmente: parcheado desde 13.52, no parcheado en 13.50.
4. La publicación enlazada de Jose Coixao dice: “bdjb patched on 13.52. this code got removed” y “this also got changed (in RootCertManager.java)”.
5. Una respuesta pública de `@ps3120` afirma: “And added RSACipherAdaptor in sunjce_provider.jar 13.52”.

Esto permite clasificar la existencia de un cambio en la superficie `RootCertManager`/`sunjce_provider.jar` como **`INDIRECT_13.52` fuerte**. Todavía no es `DIRECT_13.52`: no se publican los archivos decompilados, el diff visual, los hashes, la firma exacta, la clase completa ni los bytes.

> **Conclusión:** se ha confirmado documentalmente que fuentes públicas atribuyen a 13.52 un cambio concreto en `RootCertManager.java` y en `sunjce_provider.jar`, pero no puede reconstruirse estáticamente el parche exacto ni demostrar por bytes qué validación se modificó.

## Fuentes primarias y evidencia

### PSDevWiki, sección 3.4

Fuente pública: [sección 3.4 en modo edición][1].

El wikitexto exacto contiene:

> `FW <= 13.50 - Path traversal sandbox escape via sunjce JAR signature (untested)`

> `zecoxao for diffing decompiled 13.50 and 13.52 PS4 BD-J files (2026-06-17)`

> `The sunjce hash in RootCertManager.java was changed on PS4 13.52`

> `Patched: Yes since PS4 FW 13.52. Not patched as of PS4 FW 13.50.`

La sección añade que el cambio probablemente deshabilita la inyección de JAR antiguos firmados, potencialmente vulnerables o falsamente firmados. El texto usa “probably” y marca la vulnerabilidad histórica como “untested”; por ello describe una afirmación de parche, no una demostración reproducible completa.

### Publicación de Jose Coixao

Fuente: [publicación enlazada por PSDevWiki][2].

El extractor público muestra dos mensajes del 16 de junio de 2026:

> `bdjb patched on 13.52. this code got removed`

> `this also got changed (in RootCertManager.java)`

La publicación corrobora la atribución temporal y el archivo señalado, pero no muestra el diff ni los hashes en el texto accesible.

### Respuesta sobre `RSACipherAdaptor`

En la misma página aparece una respuesta pública de `@ps3120`, fechada el 25 de junio de 2026:

> `And added RSACipherAdaptor in sunjce_provider.jar 13.52`

Esto introduce un nombre de clase adicional potencialmente relevante: `RSACipherAdaptor`. La respuesta es una corroboración textual independiente, pero no aporta método, paquete, firma, hash, bytecode ni prueba del comportamiento criptográfico o de permisos.

## Componentes y relación técnica

| Componente | Relación documentada | 13.50 | 13.52 | Evidencia | Clasificación |
|---|---|---|---|---|---|
| `RootCertManager.java` | Gestión/verificación de certificados raíz y decisión sobre confianza de JAR | El hash `sunjce` antiguo se atribuye a la ruta no parcheada | Se afirma que el hash cambió | PSDevWiki + Jose Coixao | `INDIRECT_13.52` fuerte |
| `sunjce_provider.jar` | JAR/provider criptográfico usado por la superficie SUNJCE | Asociado a grant de `AllPermission` y firmas históricas | Se afirma que cambió y que se añadió `RSACipherAdaptor` | PSDevWiki + respuesta pública | `INDIRECT_13.52` |
| Hash de `sunjce` | Elemento de comparación dentro de `RootCertManager` | Hash anterior no publicado | Hash nuevo no publicado | PSDevWiki | `INDIRECT_13.52` fuerte, contenido `UNVERIFIED` |
| `RSACipherAdaptor` | Clase que una fuente pública afirma añadida al provider | No documentada en las fuentes consultadas | Afirmada para 13.52 | Respuesta de `@ps3120` | `INDIRECT_13.52` débil |
| Código “removed” | Jose Coixao afirma que código BD-JB fue eliminado | Presente según la afirmación | Eliminado según la afirmación | X post | `INDIRECT_13.52` |

## Comportamiento histórico conocido

La ruta histórica relaciona `sunjce_provider.jar` con la validación de firmas y policy de BD-J. PSDevWiki también documenta variantes de path traversal donde policy y loader interpretaban de forma distinta una ruta de JAR. Esas variantes tienen rangos separados:

- La sección nested-JAR/CVE-2025-64390 declara PS4 13.00–13.02.
- La sección BD-JB-13.04 declara rangos hasta 12.52 y 13.04.
- La sección `sunjce` no probada declara `<=13.50` y atribuye el cambio a 13.52.

No debe confundirse la existencia del cambio de hash en `RootCertManager` con la demostración de que el path traversal histórico siguiera siendo explotable en 13.50 ni con una prueba de ejecución nativa en 13.52.

## Firmas y métodos

La evidencia nueva identifica una clase Java (`RootCertManager.java`) y un nombre de clase adicional (`RSACipherAdaptor`), pero **no identifica firmas de métodos**. No se publican:

- método que calcula o compara el hash `sunjce`;
- algoritmo y representación del hash;
- nombre de campo o constante antigua/nueva;
- paquete de `RSACipherAdaptor`;
- constructores o interfaces implementadas;
- relación exacta entre el adaptor y la validación de firma;
- diff 13.50→13.52;
- SHA-256 de los JARs o clases.

Por tanto, no se inventan firmas ni se afirma que `RSACipherAdaptor` sea una mitigación por sí mismo.

## Qué está confirmado y qué sigue sin confirmar

| Afirmación | Estado |
|---|---|
| Existe una afirmación pública de cambio de `RootCertManager.java` en 13.52 | `INDIRECT_13.52` fuerte |
| PSDevWiki atribuye un diff decompilado 13.50/13.52 a `zecoxao` | `INDIRECT_13.52` fuerte |
| La entrada editorial marca la ruta como parcheada desde 13.52 | `INDIRECT_13.52` |
| `sunjce_provider.jar` cambió en 13.52 | `INDIRECT_13.52` |
| Se añadió `RSACipherAdaptor` en 13.52 | `INDIRECT_13.52` débil |
| Hash antiguo/nuevo disponible | `UNVERIFIED` |
| Diff de bytes o decompilación disponible | `UNVERIFIED` |
| Método exacto modificado identificado | `UNVERIFIED` |
| Mitigación reproducible ejecutable | `UNVERIFIED` |
| Vulnerabilidad `sunjce` demostrada en 13.52 | `DISCARDED` |
| Ejecución nativa derivada de este cambio | `UNVERIFIED` |

No existe evidencia `DIRECT_13.52`, porque ninguna fuente aporta bytes o un diff textual verificable de los artefactos de 13.52.

## Artefacto mínimo faltante

Para convertir la evidencia indirecta en `DIRECT_13.52` se necesita una de estas piezas legítimas y verificables:

1. El diff textual o imagen legible de `RootCertManager.java` 13.50→13.52, incluyendo los valores hash antiguos y nuevos.
2. `RootCertManager.class`/decompilación de ambas builds con SHA-256 y procedencia.
3. `sunjce_provider.jar` de ambas builds, o al menos sus manifests, inventarios de clases y hashes.
4. La clase `RSACipherAdaptor` con paquete, firma, interfaces y código decompilado.
5. Metadata de procedencia que vincule esos archivos con PS4 13.50 y PS4 13.52.

Sin una de esas piezas no puede determinarse si el cambio fue una sustitución de hash, eliminación de un certificado, incorporación de una clase adaptor, cambio de algoritmo o modificación de policy.

## Clasificación final

- **`DIRECT_13.52`:** ninguno.
- **`INDIRECT_13.52`:** cambio atribuido a `RootCertManager.java`; modificación de `sunjce_provider.jar`; afirmación de `RSACipherAdaptor`; código BD-JB eliminado.
- **`HISTORICAL_ONLY`:** comportamiento de path traversal, grant de `AllPermission` y variantes de firma/JAR descritas en PSDevWiki.
- **`HYPOTHESIS`:** que `RSACipherAdaptor` implemente o refuerce la mitigación del hash; que el cambio impida una variante concreta de JAR firmado.
- **`UNVERIFIED`:** hashes, bytes, métodos, firmas, diff reproducible y efecto exacto.

## Referencias

[1]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&section=51&action=edit — PSDevWiki, wikitexto público de la sección `sunjce`.

[2]: https://twitter.com/notnotzecoxao/status/2066944047944446366/photo/1 — Jose Coixao, publicación sobre BD-JB parcheado en 13.52 y cambio en `RootCertManager.java`.

[3]: https://twitter-thread.com/t/2081061116025692373 — Publicación atribuida a ASaudidos sobre la eliminación del grant original de `sunjce_provider.jar`.

[4]: https://www.psdevwiki.com/ps4/Vulnerabilities — Índice público de rangos y vulnerabilidades BD-J.
