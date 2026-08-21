# Reconstrucción pública de `RootCertManager`: PS4 13.50 → 13.52

**Repositorio de trabajo:** `webkit-ps4-1352-kit`  
**Alcance:** análisis estático de código/bytecode público y fuentes documentales.  
**Restricciones:** no se obtuvieron JARs propietarios de PS4 13.52, no se descifró el PUP, no se ejecutaron clases, JAR, ELF, BIN, exploits ni hardware.

## Conclusión ejecutiva

Se localizó una fuente pública nueva y materialmente útil: `deepakmathi/BDJB`, commit `491852e8cdd66b54166271413371bc65d1b4da07`.[1] El repositorio conserva clases compiladas bajo `bdjstack.jar_out`, incluyendo:

```text
com/sony/bdjstack/security/cert/RootCertManager.class
com/sony/bdjstack/security/cert/RootCertManager$1.class
```

También conserva carpetas etiquetadas `1.xx`, `12.xx` y `13.xx`.

La clase `13.xx/RootCertManager.class` es un artefacto compilado real y descargable del repositorio público, con tamaño 7044 bytes, Git blob SHA `d29b447c645ab0afdcd5f7768b944c237a2531f2` y SHA-256 local `b2a8776617a85dfc0b4ef09b09ce0e1bea7a479298ae5b714105030d3d9c4977`. Sin embargo, el repositorio no demuestra que su etiqueta `13.xx` signifique PS4 13.52. Por ello, este artefacto es **`HISTORICAL_ONLY`/`PUBLIC_BDJ_CLASS`**, no `DIRECT_13.52`.

El flujo observable de esta clase pública es diferente de la hipótesis SUNJCE/`RSACipherAdaptor`: contiene referencias a `MessageDigest`, `getInstance`, `digest`, `SHA1withRSA`, `KeyStore`, `CertificateFactory`, certificados de disco y `AccessController`, pero no contiene en su constant pool visible `sunjce_hash`, `isSunJCEVerified`, `NONEwithRSA`, `RSACipherAdaptor`, `Provider` ni `Signature`.

Por tanto, la nueva evidencia **refuta como identificación de esta clase concreta** la hipótesis de que el `RootCertManager.class` público de `deepakmathi/BDJB` sea el mismo código mostrado en la captura de 13.50/13.52. No refuta que otra clase, otro JAR o una variante propietaria de 13.52 contenga `sunjce_hash`.

## 1. Fuente nueva y procedencia

| Propiedad | Valor |
|---|---|
| Repositorio | `deepakmathi/BDJB` |
| URL | `https://github.com/deepakmathi/BDJB` |
| Rama | `main` |
| Commit | `491852e8cdd66b54166271413371bc65d1b4da07` |
| Mensaje | `Initial commit` |
| Fecha del commit | 2026-03-28 08:31:35 UTC |
| Licencia declarada por API | Ninguna (`null`) |
| Tipo de material | Clases `.class` y manifests de hashes |
| Procedencia PS4 exacta | No indicada |

Las clases se recuperaron únicamente desde URLs públicas `raw.githubusercontent.com` del commit `main`. No se descargó un PUP ni material cifrado.

## 2. Artefactos `RootCertManager` disponibles

| Etiqueta pública | Ruta | Tamaño | Git blob SHA | SHA-256 descargado | Clasificación |
|---|---|---:|---|---|---|
| `1.xx` | `1.xx/bdjstack.jar_out/com/sony/bdjstack/security/cert/RootCertManager.class` | 6977 | `1910a65fcee69eaf504226d142f4aab32caa8ad6` | `a4b64e8bbb6ac68606634f562ff8c24b230d4c7eecf41660cb726314235d6da5` | `HISTORICAL_ONLY` |
| `12.xx` | `12.xx/bdjstack.jar_out/com/sony/bdjstack/security/cert/RootCertManager.class` | 7044 | `d29b447c645ab0afdcd5f7768b944c237a2531f2` | `b2a8776617a85dfc0b4ef09b09ce0e1bea7a479298ae5b714105030d3d9c4977` | `HISTORICAL_ONLY` |
| `13.xx` | `13.xx/bdjstack.jar_out/com/sony/bdjstack/security/cert/RootCertManager.class` | 7044 | `d29b447c645ab0afdcd5f7768b944c237a2531f2` | `b2a8776617a85dfc0b4ef09b09ce0e1bea7a479298ae5b714105030d3d9c4977` | `HISTORICAL_ONLY`; versión exacta `UNVERIFIED` |
| `13.xx` inner class | `13.xx/bdjstack.jar_out/com/sony/bdjstack/security/cert/RootCertManager$1.class` | 956 | `e6433b721913e8d16dfa78a01dc70736ef47d945` | `fbf98772a58c446d1a6df9c38915d65321dfc8134d2c6f4de1c1c8f82f448420` | `HISTORICAL_ONLY` |

Los manifests `6.xx-7.xx.txt` y `8.xx-11.xx.txt` contienen los siguientes MD5 para la clase equivalente:

```text
6e801548989002ac02b75ba86d8e955c  .../RootCertManager.class
c866b4bf9dd432c1f42606b3ccc6ba99  .../RootCertManager$1.class
```

El MD5 calculado localmente para la clase de 12.xx/13.xx coincide con `6e801548989002ac02b75ba86d8e955c`; el MD5 local de la clase 1.xx es `752318ed0b771606f97efb6b0ad8e7e6`.

## 3. Identidad de clase y métodos observables

El descriptor público permite establecer el paquete:

```text
com.sony.bdjstack.security.cert.RootCertManager
```

El parser estático del formato `.class` obtuvo, entre otros, estos métodos:

| Método | Descriptor |
|---|---|
| `<init>` | `()V` |
| `initRootCertificate` | `()V` |
| `initPersistentRoot` | `()V` |
| `getOriginalPersistentRoot` | `()Ljava/lang/String;` |
| `getOriginalBindingunitRoot` | `(Ljava/lang/String;)Ljava/lang/String;` |
| `normalizePath` | `(Ljava/lang/String;)Ljava/lang/String;` |
| `setCredentialCert` | `(Lcom/sony/gemstack/core/CoreAppId;Ljava/lang/String;Ljava/lang/String;)V` |
| `removeCredentialCert` | `(Lcom/sony/gemstack/core/CoreAppId;)V` |
| `getGrantorDigest` | `(Lcom/sony/gemstack/core/CoreAppId;Ljava/lang/String;)Ljava/lang/String;` |
| `isCredentialPath` | `(Ljava/lang/String;Ljava/lang/String;)Z` |
| `createNewPath` | `(Ljava/lang/String;)Ljava/lang/String;` |
| `createNewBuPath` | `(Ljava/lang/String;)Ljava/lang/String;` |
| `getRootDigestValue` | `()[B` |
| `getGranteeDigest` | `()Ljava/lang/String;` |
| `getDiscOID` | `()Ljava/lang/String;` |
| `loadIDFile` | `()V` |
| `getGranteeDigestBytes` | `()[B` |
| `inKeyStore` | `([Ljava/security/cert/Certificate;)Z` |
| `loadKeyStore` | `()V` |
| `<clinit>` | `()V` |

La clase también contiene métodos sintéticos `access$...` asociados a la clase interna `RootCertManager$1`.

## 4. Flujo observable de certificados, digest y persistencia

Las constantes y referencias del bytecode público incluyen:

```text
java/security/MessageDigest
MessageDigest.getInstance
MessageDigest.digest
SHA1withRSA
java/security/KeyStore
java/security/cert/CertificateFactory
generateCertificate
java/security/AccessController
dvb.persistent.root
sony.rootcert
bdrootcert
/CERTIFICATE/app.discroot.crt
/CERTIFICATE/id.bdmv
```

El flujo que puede reconstruirse sin inventar instrucciones completas es:

```text
initRootCertificate / loadIDFile
  → localizar /CERTIFICATE/id.bdmv y /CERTIFICATE/app.discroot.crt
  → CertificateFactory.generateCertificate
  → gestionar X509Certificate / KeyStore
  → obtener o comparar digests relacionados con credenciales/raíz
  → usar MessageDigest.getInstance(...).digest(...)
  → mantener rootDigest, disc_oid y grantee/grantor digests
```

La presencia de `SHA1withRSA` demuestra una referencia al algoritmo de firma/certificado dentro de esta clase pública. No demuestra que se use `Signature.getInstance("NONEwithRSA")`, ni que intervenga `RSACipherAdaptor`, ni que `sunjce_provider.jar` sea la entrada del digest.

La presencia de `AccessController` demuestra que existe al menos una operación privilegiada en el código histórico compilado. No permite reconstruir por sí sola el contexto, los permisos ni una decisión de `AllPermission`.

## 5. Diferencia entre snapshots públicos

La clase `12.xx` y la clase `13.xx` son byte-identical:

```text
size:      7044 bytes en ambas
Git blob:  d29b447c645ab0afdcd5f7768b944c237a2531f2 en ambas
SHA-256:   b2a8776617a85dfc0b4ef09b09ce0e1bea7a479298ae5b714105030d3d9c4977 en ambas
MD5:       6e801548989002ac02b75ba86d8e955c en ambas
```

La comparación estática de métodos y constantes relevantes no encontró diferencia entre `12.xx` y `13.xx`. Tampoco encontró `sunjce_hash` en ninguna de las dos.

La comparación `1.xx` frente a `12.xx` tampoco mostró diferencias en el conjunto de métodos/constantes relevantes enumerado por el parser, aunque los archivos sí tienen distinto tamaño y hash. La diferencia exacta de bytecode no se interpreta aquí como cambio funcional sin un disassembler completo.

Este resultado es importante pero limitado: el repositorio usa etiquetas amplias (`12.xx`, `13.xx`) y no identifica sus clases con PS4 13.50 o 13.52. No puede utilizarse para afirmar que Sony mantuvo RootCertManager sin cambios en 13.52.

## 6. Ausencia de la ruta SUNJCE en esta clase pública

La búsqueda de constant-pool y strings de `RootCertManager.class` 1.xx, 12.xx y 13.xx no encontró:

| Símbolo o literal | Resultado |
|---|---|
| `sunjce_hash` | Ausente |
| `isSunJCEVerified` | Ausente |
| `RSACipherAdaptor` | Ausente |
| `NONEwithRSA` | Ausente |
| `Provider` | Ausente como constante UTF-8 relevante |
| `Signature` | Ausente como constante UTF-8 relevante |
| `sunjce_provider.jar` | Ausente |

Esto no invalida la captura pública de RootCertManager: demuestra que **la clase capturada o la variante 13.52 relevante no puede identificarse con estos snapshots públicos**. Puede tratarse de una clase distinta, una revisión posterior, otra ubicación/JAR o una build propietaria no representada por `deepakmathi/BDJB`.

## 7. Relación con `getOriginalPersistentRoot()`

La nueva clase pública confirma históricamente la existencia de:

```java
public static String getOriginalPersistentRoot()
```

El caller público de HackerOne #1379975 usa ese método para construir la ruta `.../userprefs` antes de `ObjectInputStream.readObject()`.[2] Esta relación es `HISTORICAL_ONLY`.

No se puede establecer a partir de la clase pública:

- si el método cambia entre 13.50 y 13.52;
- si la ruta se normaliza o canoniza de la misma forma;
- si el método sigue siendo llamado por el mismo componente;
- si la entrada `userprefs` continúa existiendo;
- si el método está conectado con `sunjce_hash`.

## 8. Relación con `RSACipherAdaptor` y `NONEwithRSA`

El contrato estándar OpenJDK de `RSACipherAdaptor` registra `Signature.NONEwithRSA` dentro de `SunJCE`.[3] La nueva clase pública RootCertManager no contiene ninguno de esos nombres ni referencias en su constant pool.

Por tanto, no existe caller observable que conecte:

```text
RootCertManager
→ Signature.getInstance("NONEwithRSA")
→ SunJCE Provider.Service
→ RSACipherAdaptor
```

La afirmación pública de que `RSACipherAdaptor` fue añadido a `sunjce_provider.jar` en 13.52 continúa siendo `DOCUMENTED_ONLY`.[4] El nuevo repositorio aporta una clase RootCertManager pública, pero su contenido no coincide nominalmente con la ruta SUNJCE de la captura.

## 9. Reconstrucción funcional máxima

La reconstrucción más fuerte que permite el material público es la siguiente:

```text
BD-J / BDJ stack histórico
  → RootCertManager
  → raíz de disco y archivos CERTIFICATE
  → X509Certificate / CertificateFactory
  → KeyStore y credenciales
  → MessageDigest / SHA1withRSA / digest de estructuras
  → rootDigest, grantee/grantor digest y disc_oid
  → rutas persistentes mediante dvb.persistent.root
```

Esta reconstrucción **no** puede ampliarse legítimamente a:

```text
RootCertManager
  → sunjce_provider.jar
  → sunjce_hash
  → Signature.NONEwithRSA
  → RSACipherAdaptor
```

porque los símbolos de esa segunda ruta no están presentes en la clase pública examinada y no existe una implementación pública de 13.52 que la conecte.

## 10. Clasificación final

| Hallazgo | Clasificación |
|---|---|
| Existe una clase pública compilada `com.sony.bdjstack.security.cert.RootCertManager` | `HISTORICAL_ONLY` |
| El repositorio tiene una carpeta etiquetada `13.xx` | `DOCUMENTED_ONLY`; firmware exacto `UNVERIFIED` |
| `12.xx` y `13.xx` son byte-identical en ese repositorio | `DIRECT_PUBLIC_ARTIFACT` |
| La clase contiene `getOriginalPersistentRoot()` | `HISTORICAL_ONLY` |
| La clase referencia `MessageDigest`, `digest`, `SHA1withRSA`, KeyStore y certificados | `DIRECT_PUBLIC_ARTIFACT` |
| La clase referencia `AccessController` | `DIRECT_PUBLIC_ARTIFACT` |
| La clase contiene `sunjce_hash` | `DISCARDED` para estos snapshots |
| La clase contiene `NONEwithRSA`/`RSACipherAdaptor` | `DISCARDED` para estos snapshots |
| El snapshot `13.xx` representa PS4 13.52 | `UNVERIFIED` |
| El cambio de hash público 13.50→13.52 está en esta clase | `DISCARDED` como identificación; la captura sigue siendo evidencia separada |
| `RootCertManager` usa `RSACipherAdaptor` | `UNVERIFIED` |
| El cambio de hash explica la eliminación de BD-JB | `HYPOTHESIS`/`DOCUMENTED_ONLY`, no probado por este artefacto |

## Conclusión

**Se encontró evidencia pública nueva, pero no bytes 13.52 identificados.** El repositorio BDJB aporta un `RootCertManager.class` real, métodos y referencias que permiten reconstruir el flujo histórico de certificados, persistencia, `MessageDigest`, `SHA1withRSA` y `KeyStore`. Sin embargo, sus snapshots `12.xx` y `13.xx` son idénticos y no contienen `sunjce_hash`, `NONEwithRSA`, `RSACipherAdaptor` ni `sunjce_provider.jar`.

El resultado más preciso es:

> **La ruta pública de RootCertManager queda parcialmente reconstruida para certificados/KeyStore/digest y persistencia, pero la ruta SUNJCE asociada a la captura 13.50→13.52 no puede atribuirse a estas clases. El primer punto no verificado sigue siendo identificar la variante exacta de `RootCertManager` y su bytecode correspondiente a 13.50/13.52.**

La pieza mínima siguiente es un `RootCertManager.class`/`RootCertManager.java` de una build PS4 identificada por firmware, o el `bdjstack.jar` correspondiente con manifest, tamaño y SHA-256. El snapshot público `13.xx` no es suficiente para promover ninguna conclusión a `DIRECT_13.52`.

## Referencias

[1]: https://github.com/deepakmathi/BDJB/tree/491852e8cdd66b54166271413371bc65d1b4da07 — Repositorio público BDJB y commit auditado.
[2]: https://hackerone.com/reports/1379975 — HackerOne #1379975, caller histórico de `getOriginalPersistentRoot()` y `userprefs`.
[3]: https://github.com/openjdk/jdk/commit/35dabb1a5f31d985f00de21badeeedb026a63b94 — OpenJDK `8244336`, `RSACipherAdaptor` y registro `NONEwithRSA`.
[4]: https://x.com/ps3120/status/2070144817233789048 — Afirmación pública sobre `RSACipherAdaptor` en `sunjce_provider.jar` 13.52.
[5]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&action=raw&section=51 — PSDevWiki, evidencia editorial de cambio de `sunjce_hash` y estado de parcheo.
[6]: https://raw.githubusercontent.com/deepakmathi/BDJB/main/13.xx/bdjstack.jar_out/com/sony/bdjstack/security/cert/RootCertManager.class — Clase pública `13.xx` auditada.
[7]: https://raw.githubusercontent.com/deepakmathi/BDJB/main/12.xx/bdjstack.jar_out/com/sony/bdjstack/security/cert/RootCertManager.class — Clase pública `12.xx` byte-identical.
[8]: https://raw.githubusercontent.com/deepakmathi/BDJB/main/13.xx/bdjstack.jar_out/com/sony/bdjstack/security/cert/RootCertManager%241.class — Clase interna pública `RootCertManager$1`.
