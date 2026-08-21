# `RSACipherAdaptor` y `sunjce_provider.jar` en PS4 13.52

**Autor:** Manus AI  
**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** investigación estática y documental. No se descargaron PUPs, dumps privados ni runtime propietario; no se ejecutaron exploits, payloads, JAR/ELF/BIN ni hardware.

## Conclusión ejecutiva

La evidencia pública permite identificar con precisión qué es `RSACipherAdaptor` en OpenJDK moderno: una clase `com.sun.crypto.provider.RSACipherAdaptor` que extiende `java.security.SignatureSpi` y adapta el cifrado `RSA/ECB/PKCS1Padding` de SunJCE para ofrecer el servicio `Signature.NONEwithRSA`.

El commit OpenJDK `35dabb1a5f31d985f00de21badeeedb026a63b94` (`8244336: Restrict algorithms at JCE layer`) añade la clase y registra el servicio en `SunJCE`. El historial público de GitHub fija esa aparición en **12 de septiembre de 2025**.

Una respuesta pública de `@ps3120` afirma que `RSACipherAdaptor` fue añadido en `sunjce_provider.jar` de PS4 13.52. Esa afirmación es nominalmente compatible con la clase OpenJDK, pero no aporta package, diff, bytecode, hash, caller ni procedencia del JAR PS4. Por tanto, el resultado para PS4 13.52 es **`INDIRECT_13.52`**, no `DIRECT_13.52`.

No existe evidencia pública que conecte `RSACipherAdaptor` con `RootCertManager`, con el grant `AllPermission`, con la selección de JARs BD-J o con el parche de la vulnerabilidad SUNJCE. La cadena causal completa sigue sin demostrarse.

## Identidad y contrato de la clase en OpenJDK

El commit público de OpenJDK muestra la siguiente identidad:

| Propiedad | Evidencia pública |
|---|---|
| Package | `com.sun.crypto.provider` |
| Clase | `public final class RSACipherAdaptor` |
| Superclase | `java.security.SignatureSpi` |
| Campo principal | `private final RSACipher c` |
| Estado de verificación | `private ByteArrayOutputStream verifyBuf` |
| Constructor | `public RSACipherAdaptor()`; crea `new RSACipher()` |
| Servicio JCE | `Signature`, algoritmo `NONEwithRSA` |
| Clases de clave | `RSAPublicKey` y `RSAPrivateKey` |
| Cipher subyacente | `RSA/ECB/PKCS1Padding` mediante `RSACipher` |

Los métodos protegidos que aparecen en el diff son `engineInitVerify`, dos variantes de `engineInitSign`, dos variantes de `engineUpdate`, `engineSign`, `engineVerify`, dos variantes de `engineSetParameter` y `engineGetParameter`. Los métodos de parámetros rechazan parámetros no soportados.

En modo de verificación, el adaptador acumula los datos en `verifyBuf`, descifra la firma mediante `RSACipher.engineDoFinal` y compara el resultado con `MessageDigest.isEqual`. En modo de firma, inicializa el cipher con la clave privada y devuelve el resultado de `engineDoFinal`. Esta semántica corresponde a un adaptador criptográfico JCE; no es una API de carga de clases, permisos o ejecución nativa.

## Cadena técnica solicitada

La cadena que sí puede demostrarse para OpenJDK es:

```text
SunJCE.putEntries()
  → Provider.Service("Signature", "NONEwithRSA",
                    "com.sun.crypto.provider.RSACipherAdaptor")
  → Signature.getInstance("NONEwithRSA", SunJCE)
  → instanciación del SignatureSpi
  → RSACipherAdaptor
  → RSACipher
  → RSA/ECB/PKCS1Padding
```

La cadena que se ha afirmado para PS4, pero que no está demostrada por bytes, sería:

```text
RootCertManager
  → decisión sobre confianza/firma de JAR
  → sunjce_provider.jar
  → RSACipherAdaptor
  → API JCE / Signature NONEwithRSA
  → validación de firma o certificado
```

El enlace `RootCertManager → sunjce_provider.jar` está documentado de forma histórica y el cambio de `RootCertManager.java` en 13.52 está afirmado públicamente. El eslabón `sunjce_provider.jar → RSACipherAdaptor` sólo aparece en una respuesta pública de `@ps3120`; no existe caller verificable ni prueba de que `RootCertManager` lo instancie o lo consulte.

## Evidencia específica de PS4 13.52

| Hallazgo | Fuente | Qué demuestra | Clasificación |
|---|---|---|---|
| Cambio de `RootCertManager.java` en 13.52 | PSDevWiki, sección SUNJCE | El wikitexto afirma que cambió el hash de SUNJCE y marca la ruta como parcheada desde 13.52 | `INDIRECT_13.52` fuerte |
| Cambio de `sunjce_provider.jar` | Jose Coixao y PSDevWiki | Se afirma que cambió/eliminó código en BD-J y que `RootCertManager.java` también cambió | `INDIRECT_13.52` |
| Adición de `RSACipherAdaptor` en 13.52 | Respuesta pública de `@ps3120` | Afirmación textual de que se añadió al provider | `INDIRECT_13.52` débil |
| Package y métodos de `RSACipherAdaptor` | OpenJDK 2025 / API OpenJDK 26 | Define una clase estándar con package, superclase y contrato concretos | `HISTORICAL_ONLY` / `STANDARD_JAVA` |
| Identidad de la clase PS4 | Ninguna fuente con bytes o decompilación PS4 | No permite comprobar equivalencia | `UNVERIFIED` |
| Caller PS4 | Ninguna fuente | No permite enlazar `RootCertManager` con el adaptor | `UNVERIFIED` |

## Relación con `RootCertManager`

`RootCertManager.java` aparece en las fuentes públicas como componente cuyo hash de SUNJCE cambió en 13.52. La descripción histórica relaciona esa validación con la confianza en JARs firmados, pero no publica el cuerpo de la clase ni el método que calcula o compara el hash.

El commit OpenJDK de `RSACipherAdaptor` no contiene referencias a `RootCertManager`, BD-J, `AllPermission`, `CodeSource`, `JarFile` ni policy. Su propósito explícito es restringir/registrar algoritmos en la capa JCE y proporcionar `NONEwithRSA` mediante el cipher RSA existente. Por tanto, no puede establecerse causalidad entre la clase estándar y el cambio de la política de confianza de JAR en PS4.

## Relación con la vulnerabilidad histórica SUNJCE

La superficie histórica SUNJCE se describe como una combinación de selección de JAR, firma/hash y policy de BD-J. Las fuentes separan esa superficie de la implementación criptográfica concreta. Que un provider contenga una clase RSA no implica que:

1. el provider sea el componente que concede `AllPermission`;
2. `RootCertManager` instancie `RSACipherAdaptor`;
3. el adaptor modifique la decisión de confianza;
4. el cambio de 13.52 sea una corrección de `Signature.NONEwithRSA`;
5. el cambio permita o impida cargar JARs antiguos.

La relación causal debe permanecer como **`UNVERIFIED`**.

## Qué comportamiento podría introducir o sustituir

En OpenJDK, la clase introduce un servicio `Signature.NONEwithRSA` construido sobre `RSACipher`. El comportamiento nuevo es una implementación de firma/verificación RSA en la capa JCE y una restricción/registro explícito del algoritmo en `SunJCE`.

No puede afirmarse que el provider PS4 13.52 tenga exactamente esa implementación. Tampoco se sabe si la respuesta de `@ps3120` usa el mismo package `com.sun.crypto.provider`, una adaptación Sony, una clase interna de otro provider o simplemente el nombre visible en una decompilación parcial.

## Hashes y procedencia

No hay hash público de `sunjce_provider.jar` PS4 13.50 o 13.52, ni de `RootCertManager.class`, ni de `RSACipherAdaptor.class` PS4. El único identificador reproducible relacionado es el commit OpenJDK:

- Commit: `35dabb1a5f31d985f00de21badeeedb026a63b94`.
- Mensaje: `8244336: Restrict algorithms at JCE layer`.
- Fecha: 2025-09-12.
- Archivo añadido: `src/java.base/share/classes/com/sun/crypto/provider/RSACipherAdaptor.java`.

Ese commit es evidencia del origen público moderno de la clase, no evidencia del contenido del JAR PS4.

## Qué faltaría para confirmar la cadena PS4

La confirmación requiere al menos una de estas piezas:

1. `RSACipherAdaptor.class` de `sunjce_provider.jar` 13.52 con SHA-256 y procedencia.
2. Manifest o inventario de clases de `sunjce_provider.jar` 13.52 que indique el package completo.
3. Decompilación de `RSACipherAdaptor` 13.52 con superclase, métodos y referencias a `RSACipher`.
4. Caller o referencia desde `RootCertManager.java`, `Signature`, `Cipher` o provider registration.
5. Diff 13.50→13.52 de `RootCertManager.java` y del provider.
6. Hash antiguo/nuevo usado por `RootCertManager` y explicación de qué artefacto se valida.

## Clasificación final

| Conclusión | Clasificación |
|---|---|
| `RSACipherAdaptor` existe en OpenJDK moderno como `com.sun.crypto.provider.RSACipherAdaptor` | `HISTORICAL_ONLY` / `STANDARD_JAVA` |
| La clase se añadió en OpenJDK mediante `8244336` | `HISTORICAL_ONLY` |
| Una fuente pública afirma que se añadió a `sunjce_provider.jar` 13.52 | `INDIRECT_13.52` débil |
| El provider PS4 13.52 contiene exactamente la clase OpenJDK | `UNVERIFIED` |
| `RootCertManager` instancia o usa el adaptor | `UNVERIFIED` |
| La equivalencia nominal con OpenJDK sugiere una posible relación funcional, sin demostrarla en PS4 | `INFERRED` |
| El adaptor implementa el parche de confianza de JAR | `HYPOTHESIS` |
| `RSACipherAdaptor` es una primitive de sandbox escape/native code | `DISCARDED` |

## Conclusión

La explicación técnicamente más prudente es que `RSACipherAdaptor` es, en el precedente público de OpenJDK, un adaptador criptográfico para `Signature.NONEwithRSA`. La evidencia específica de 13.52 sólo permite afirmar que una fuente pública dice que una clase con ese nombre fue añadida a `sunjce_provider.jar`; no permite identificar su package, código, caller ni relación causal con `RootCertManager` o el parche SUNJCE.

> **Resultado:** `RSACipherAdaptor` queda como `INDIRECT_13.52` débil y la cadena `RootCertManager → SUNJCE/provider → RSACipherAdaptor → API/caller → validación/parche` permanece incompleta y `UNVERIFIED` en su tramo central.

## Referencias

[1]: https://github.com/openjdk/jdk/commit/35dabb1a5f31d985f00de21badeeedb026a63b94 — OpenJDK commit `8244336`, “Restrict algorithms at JCE layer”.

[2]: https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/com/sun/crypto/provider/SunJCE.java — Registro de `Signature NONEwithRSA` en `SunJCE`.

[3]: https://apidia.net/java/OpenJDK/26/com.sun.crypto.provider.RSACipherAdaptor.html — API pública de `RSACipherAdaptor` en OpenJDK 26.

[4]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&section=51&action=edit — PSDevWiki, wikitexto público de la sección SUNJCE.

[5]: https://twitter.com/notnotzecoxao/status/2066944047944446366/photo/1 — Jose Coixao, publicaciones sobre BD-JB/`RootCertManager` en 13.52.

[6]: https://twitter-thread.com/t/2081061116025692373 — Publicación atribuida a ASaudidos sobre el grant original de `sunjce_provider.jar`.
