# Reconstrucción del diff SUNJCE PS4 13.50→13.52

**Autor:** Manus AI  
**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** análisis estático y documental de la superficie SUNJCE. No se descargaron PUPs, dumps privados ni JAR retail; no se ejecutaron exploits, payloads, JAR/ELF/BIN ni hardware.

## Conclusión ejecutiva

La captura pública enlazada por Jose Coixao permite recuperar dos valores distintos de `sunjce_hash` dentro de un inicializador estático de `RootCertManager.java`:

| Contexto del diff | Valor visible |
|---|---|
| Panel izquierdo, versión anterior atribuida a 13.50 | `y8ehrm01Q64cek7k6/+CwpSDLsjfnCesSX0agGpM10g=` |
| Panel derecho, versión nueva atribuida a 13.52 | `At2dtIBsAdpxI/Gwtq2otASAkU5OVg3QG5ffUF+KBek=` |

La misma captura muestra que la asignación está próxima a `AccessController.doPrivileged(new 1())`. PSDevWiki atribuye el diff a una comparación de archivos BD-J decompilados 13.50/13.52 y declara la superficie parcheada desde 13.52. Esto eleva la evidencia del cambio de hash a **`INDIRECT_13.52` fuerte**.

No obstante, la captura no muestra el algoritmo que produjo el hash, el objeto exacto que se compara, el método que consume la constante, el caller, el valor de `RootCertManager` que se valida ni el diff completo del provider. La reconstrucción exacta del parche sigue incompleta.

> **Resultado:** SUNJCE puede considerarse documentalmente parcheado en 13.52, pero no existe todavía una cadena técnica completa y reproducible desde el cambio de hash hasta una vulnerabilidad concreta o su corrección por bytes.

## Evidencia visual y procedencia

La imagen pública es:

- URL: [captura pública de `RootCertManager.java`][1]
- Publicación: [Jose Coixao, 16 de junio de 2026][2]
- Archivo local: `rootcertmanager_hash_diff_1350_1352.webp`
- Dimensiones: `1673×158`
- SHA-256: `8de5f485cf45e00c8460a85bd915d5dca42086cbe8b8457dd97f0415f5af8b0c`

Recortes de lectura usados para evitar pérdida de caracteres:

| Archivo | SHA-256 |
|---|---|
| `hash-crops/left_hash_1350.png` | `b078d7b2013c598e6dd111c8f91cdb33b40791a057f76c0f36ea09b175f11ead` |
| `hash-crops/right_hash_1352.png` | `d198b842c52fba87b82b8bb698558bca80a07f2cc0ca45e23464144a65509156` |

La identificación de los paneles como 13.50 y 13.52 procede del contexto de la publicación y de la entrada de PSDevWiki; los paneles no contienen encabezados de versión visibles dentro del recorte.

## Qué muestra exactamente la captura

En ambos paneles aparece una estructura equivalente a:

```java
static {
    AccessController.doPrivileged(new 1());
    sunjce_hash = "...";
}
```

La línea `AccessController.doPrivileged(new 1())` y la asignación de `sunjce_hash` son legibles. La captura no contiene el cuerpo completo del método anónimo `new 1()`, ni el método que usa `sunjce_hash`, ni la operación que calcula el valor.

La presencia de `AccessController.doPrivileged` demuestra un contexto privilegiado de inicialización Java, pero no prueba que el hash se calcule dentro de ese bloque, ni que el bloque sea una primitiva de sandbox escape. Sólo fija el contexto estructural de la constante.

## Valores y posible representación

Los dos valores visibles tienen 44 caracteres y terminan en `=`. Esto es compatible con una representación Base64 de 32 bytes, pero esa observación no demuestra el algoritmo. Podría ser, por ejemplo, la codificación Base64 de un digest de 256 bits, una salida derivada o una constante serializada de longitud equivalente.

No se debe afirmar que sea SHA-256 sin ver el método de cálculo. Para confirmar el algoritmo y el objeto se necesita el cuerpo de `RootCertManager.java` o un diff que muestre una operación como `MessageDigest`, `Digest`, lectura de bytes del JAR o comparación contra un certificado/provider.

## RootCertManager y el cambio de hash

PSDevWiki declara en su sección SUNJCE:

> “The sunjce hash in RootCertManager.java was changed on PS4 13.52.”

También atribuye a `zecoxao` el “diffing decompiled 13.50 and 13.52 PS4 BD-J files” y marca la entrada como parcheada desde 13.52, no parcheada en 13.50. Jose Coixao publica además:

> “bdjb patched on 13.52. this code got removed”

> “this also got changed (in RootCertManager.java)”

Estas fuentes corroboran la existencia documental de un cambio de superficie, pero no permiten distinguir entre sustitución de hash, eliminación de código, cambio de provider, cambio de certificado o modificación de la lógica de comparación.

## `RSACipherAdaptor` y `sunjce_provider.jar`

Una respuesta pública de `@ps3120` afirma:

> “And added RSACipherAdaptor in sunjce_provider.jar 13.52”

El nombre coincide con una clase pública moderna de OpenJDK:

```text
com.sun.crypto.provider.RSACipherAdaptor
```

El commit OpenJDK `35dabb1a5f31d985f00de21badeeedb026a63b94` (`8244336: Restrict algorithms at JCE layer`, 12 de septiembre de 2025) añade la clase y registra:

```java
Signature / NONEwithRSA
→ com.sun.crypto.provider.RSACipherAdaptor
```

El adaptor extiende `SignatureSpi`, encapsula `RSACipher`, verifica mediante `MessageDigest.isEqual` y usa RSA/ECB/PKCS1Padding. El commit OpenJDK no contiene referencias a `RootCertManager`, BD-J, `AllPermission`, `CodeSource` o policy.

Por tanto, la coincidencia permite una hipótesis de trabajo, no una equivalencia de implementación:

```text
sunjce_provider.jar 13.52
→ posible RSACipherAdaptor
→ posible servicio Signature/NONEwithRSA
```

El caller PS4 que conectaría esto con `RootCertManager` no está publicado. La relación temporal tampoco demuestra que `RSACipherAdaptor` sea la causa del parche; podría ser un cambio independiente de compatibilidad o de registro criptográfico.

## Reconstrucción máxima permitida por la evidencia

La reconstrucción más precisa que puede sostenerse es:

```text
PS4 13.50:
RootCertManager.java
  → sunjce_hash = y8ehrm01Q64cek7k6/+CwpSDLsjfnCesSX0agGpM10g=
  → lógica de confianza de JAR/provider no mostrada

PS4 13.52:
RootCertManager.java
  → sunjce_hash = At2dtIBsAdpxI/Gwtq2otASAkU5OVg3QG5ffUF+KBek=
  → código BD-J relacionado afirmado como eliminado/cambiado
  → sunjce_provider.jar afirmado como modificado
  → RSACipherAdaptor afirmado como añadido
```

No se puede rellenar el tramo central con una llamada o algoritmo no visible:

```text
sunjce_hash
  → ¿qué bytes se digieren?
  → ¿qué algoritmo se usa?
  → ¿qué resultado se compara?
  → ¿qué decisión toma RootCertManager?
  → ¿qué caller selecciona o autoriza el JAR?
```

## Clases y cambios: estado de evidencia

| Elemento | 13.50 | 13.52 | Evidencia | Clasificación |
|---|---|---|---|---|
| `RootCertManager.java` | Hash anterior visible | Hash nuevo visible | Captura pública + PSDevWiki | `INDIRECT_13.52` fuerte |
| `sunjce_hash` | `y8ehrm01Q64cek7k6/+CwpSDLsjfnCesSX0agGpM10g=` | `At2dtIBsAdpxI/Gwtq2otASAkU5OVg3QG5ffUF+KBek=` | Captura pública | `INDIRECT_13.52` fuerte |
| Algoritmo del hash | No visible | No visible | Ninguna | `UNVERIFIED` |
| Objeto hasheado | No visible | No visible | Ninguna | `UNVERIFIED` |
| `sunjce_provider.jar` | Existencia histórica asociada | Cambio afirmado | PSDevWiki/X | `INDIRECT_13.52` |
| `RSACipherAdaptor` | No evidencia PS4 13.50 | Adición afirmada | Respuesta de `@ps3120` | `INDIRECT_13.52` débil |
| Package de adaptor en PS4 | No visible | No visible | Sólo OpenJDK estándar | `UNVERIFIED` |
| Caller del adaptor | No visible | No visible | Ninguna | `UNVERIFIED` |
| Clases eliminadas | Afirmadas como presentes | Afirmadas como eliminadas | Jose Coixao | `INDIRECT_13.52` |
| Diff textual completo | Ausente | Ausente | Ninguna | `UNVERIFIED` |

## ¿Corrige una vulnerabilidad concreta?

La evidencia histórica conecta SUNJCE con validación de firmas/JAR y con una decisión de confianza que podía otorgar privilegios a un JAR seleccionado mediante una ruta manipulada. La sustitución del hash y la eliminación de código son coherentes con una mitigación de confianza en un provider antiguo o en JARs firmados antiguos.

Pero no existe una cadena técnica verificable completa. No se ha demostrado si el parche:

- rechaza un provider por hash;
- cambia el hash esperado para invalidar un JAR antiguo;
- elimina un grant de `AllPermission`;
- añade una clase criptográfica estándar;
- cambia `Signature.NONEwithRSA`;
- elimina una ruta de carga;
- o aplica varias correcciones simultáneas.

Por ello, SUNJCE 13.52 puede describirse como **parcheado según fuentes públicas**, pero no como una corrección técnicamente reproducible de una vulnerabilidad concreta.

## Piezas que siguen faltando

| Pieza | Pregunta que resolvería |
|---|---|
| `RootCertManager.java` decompilado 13.50 y 13.52 | Qué algoritmo, bytes y comparación producen `sunjce_hash`. |
| Hashes exactos en formato legible y contexto de versión | Confirmar la transcripción y asociación de paneles. |
| `sunjce_provider.jar` 13.50 y 13.52 | Qué clases fueron añadidas/eliminadas/modificadas. |
| `RSACipherAdaptor.class` 13.52 | Package, superclase, métodos e implementación real. |
| Registro `Provider.Service` 13.52 | Si existe `Signature.NONEwithRSA` y qué clase instancia. |
| Caller de `RootCertManager` | Qué decisión de confianza depende del hash. |
| Diff de `AccessController.doPrivileged(new 1())` | Qué código se ejecuta bajo privilegio y qué cambió. |
| Manifest/procedencia de ambos JARs | Vincular todo con PS4 13.50 y 13.52 de forma reproducible. |

## Clasificación final

- **`DIRECT_13.52`:** ninguno; la captura es evidencia visual pública, no bytes de runtime verificables.
- **`INDIRECT_13.52`:** valores distintos de `sunjce_hash`, cambio de `RootCertManager.java`, cambio de `sunjce_provider.jar`, código BD-JB eliminado y afirmación de `RSACipherAdaptor` añadido.
- **`HISTORICAL_ONLY`:** semántica OpenJDK de `RSACipherAdaptor` y vulnerabilidades históricas de selección/firma de JAR.
- **`INFERRED`:** posible relación funcional entre el cambio de hash y la invalidación de JAR/provider antiguo.
- **`UNVERIFIED`:** algoritmo, objeto, caller, clases modificadas, package PS4, diff textual, hashes de JAR y cadena causal completa.

## Conclusión final

La evidencia permite reconstruir **un cambio real de constante/hash en `RootCertManager.java` entre las versiones que la fuente atribuye a 13.50 y 13.52**, además de afirmaciones independientes de cambios en `sunjce_provider.jar` y la adición de `RSACipherAdaptor`.

No permite reconstruir todavía el diff funcional completo. La conclusión responsable es:

> **SUNJCE 13.52 está documentado como parcheado, pero no existe una cadena técnica verificable que identifique exactamente la vulnerabilidad corregida ni que conecte `RSACipherAdaptor` con `RootCertManager`.**

## Referencias

[1]: https://pbs.twimg.com/media/HK9CpsiXYAAmMbv?format=webp&name=large — Captura pública de la comparación `RootCertManager.java`.

[2]: https://twitter.com/notnotzecoxao/status/2066944047944446366/photo/1 — Jose Coixao, cambio de `RootCertManager.java` y BD-JB parcheado en 13.52.

[3]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&section=51&action=edit — PSDevWiki, sección SUNJCE con rango y crédito del diff.

[4]: https://github.com/openjdk/jdk/commit/35dabb1a5f31d985f00de21badeeedb026a63b94 — OpenJDK `8244336`, adición de `RSACipherAdaptor`.

[5]: https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/com/sun/crypto/provider/SunJCE.java — Registro `Signature NONEwithRSA` en SunJCE.

[6]: https://twitter-thread.com/t/2081061116025692373 — Publicación atribuida a ASaudidos sobre el grant original de `sunjce_provider.jar`.
