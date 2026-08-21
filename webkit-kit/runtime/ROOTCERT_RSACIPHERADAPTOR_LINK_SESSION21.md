# RootCertManager → SUNJCE → RSACipherAdaptor: análisis del vínculo público

**Repositorio:** `webkit-ps4-1352-kit`  
**Ámbito:** análisis estático del corpus local y fuentes públicas verificables.  
**Restricciones:** no se ejecutaron exploits, payloads, JAR, ELF, BIN ni hardware; no se obtuvo ni descifró runtime propietario de PS4 13.52.

## Conclusión ejecutiva

La cadena completa solicitada no está demostrada. Se pueden separar dos subcadenas con evidencia distinta:

```text
OpenJDK SunJCE
  → Provider.Service("Signature", "NONEwithRSA",
                     "com.sun.crypto.provider.RSACipherAdaptor")
  → RSACipherAdaptor
  → RSACipher / RSA/ECB/PKCS1Padding
  → verificación mediante MessageDigest.isEqual
```

Esta subcadena es **DIRECTA para OpenJDK público**, no para PS4 13.52.[1] [2]

Por otro lado, PSDevWiki y publicaciones públicas atribuidas a investigadores afirman que `RootCertManager.java` cambió su `sunjce_hash` en 13.52 y que la ruta SUNJCE fue parcheada.[3] [4] Una respuesta pública afirma además que se añadió `RSACipherAdaptor` a `sunjce_provider.jar` de 13.52.[5] Esa afirmación es **DOCUMENTED_ONLY/INDIRECT_13.52**: no incluye paquete, bytecode, JAR hash, caller ni registro de provider.

No apareció ningún caller público que demuestre:

```text
RootCertManager
  → Signature.getInstance("NONEwithRSA")
  → Security.getProvider / Provider.Service
  → RSACipherAdaptor
  → validación del JAR, certificado o hash
```

El eslabón central `RootCertManager → RSACipherAdaptor` permanece **UNVERIFIED**. No es válido afirmar que el cambio de `sunjce_hash` fue causado por la incorporación del adaptor, ni que el adaptor implementa la corrección de la validación de JAR.

## 1. Evidencia local auditada

La auditoría de `webkit-ps4-1352-kit` encontró los siguientes materiales relevantes:

| Archivo | Contenido | Clasificación |
|---|---|---|
| `webkit-kit/runtime/BDJ_RSACIPHERADAPTOR_SUNJCE_1352.md` | Contrato OpenJDK, registro `NONEwithRSA` y límites de evidencia PS4 | `HISTORICAL_ONLY`/`INDIRECT_13.52` |
| `webkit-kit/runtime/ROOTCERTMANAGER_SUNJCE_DIFF_1350_1352_SESSION20.md` | Cambio público de `sunjce_hash`, captura y límites del pseudodiff | `INDIRECT_13.52` |
| `webkit-kit/runtime/ROOTCERT_PUBLIC_EVIDENCE_SESSION20.txt` | Texto capturado de PSDevWiki, X y OpenJDK | Evidencia auxiliar reproducible |
| `webkit-kit/runtime/BDJ_RUNTIME_PUBLIC_EVIDENCE_1352.md` | Ausencia de `rt.jar`, `bdjstack.jar` y runtime 13.52 | `UNVERIFIED` para contenido; ausencia local documentada |

La búsqueda textual local de `RootCertManager`, `sunjce_hash`, `isSunJCEVerified`, `RSACipherAdaptor`, `NONEwithRSA`, `Signature.getInstance`, `Security.getProvider` y `Provider` no produjo una implementación PS4 del caller. Las coincidencias corresponden a informes, referencias históricas, código estándar OpenJDK o capturas documentales.

No hay en el repositorio `sunjce_provider.jar`, `rt.jar`, `bdjstack.jar`, `RootCertManager.class`, `RootCertManager.java` completo ni `RSACipherAdaptor.class` de PS4 13.52.

## 2. Contrato estándar de OpenJDK

El commit OpenJDK `35dabb1a5f31d985f00de21badeeedb026a63b94`, cuyo mensaje es `8244336: Restrict algorithms at JCE layer`, añade `RSACipherAdaptor.java` y modifica el registro de `SunJCE`.[1]

La clase pública estándar tiene esta identidad:

| Propiedad | OpenJDK público |
|---|---|
| Paquete | `com.sun.crypto.provider` |
| Clase | `RSACipherAdaptor` |
| Superclase | `java.security.SignatureSpi` |
| Cipher interno | `RSACipher` |
| Servicio | `Signature`, algoritmo `NONEwithRSA` |
| Claves admitidas | `RSAPublicKey`, `RSAPrivateKey` |
| Verificación | Descifra con RSA/PKCS#1 v1.5 y compara con `MessageDigest.isEqual` |
| Registro | `SunJCE.putEntries()` mediante `Provider.Service` |

El registro público es conceptualmente:

```java
attrs.put("SupportedKeyClasses",
          "java.security.interfaces.RSAPublicKey"
        + "|java.security.interfaces.RSAPrivateKey");
ps("Signature", "NONEwithRSA",
   "com.sun.crypto.provider.RSACipherAdaptor", null, attrs);
```

El adaptador no conoce `RootCertManager`, BD-J, `CodeSource`, `AllPermission`, `BdjPolicyImpl`, JARs ni rutas de filesystem. Es un proveedor criptográfico estándar. Por sí solo no es una primitive de sandbox escape, carga de clases o ejecución nativa.

## 3. Flujo estándar `NONEwithRSA`

El flujo verificable en OpenJDK es:

```text
Signature.getInstance("NONEwithRSA", SunJCE)
  → Provider.Service del tipo Signature
  → instanciación de com.sun.crypto.provider.RSACipherAdaptor
  → engineInitVerify(RSAPublicKey)
  → engineUpdate(data)
  → engineVerify(signature)
  → RSACipher.engineDoFinal(signature)
  → MessageDigest.isEqual(decrypted, data)
```

La clase utiliza `SignatureSpi`; no llama a `RootCertManager`. El consumidor de `RootCertManager` tendría que invocar explícitamente `Signature`, `Security`, `Provider` o una clase de validación que, a su vez, seleccionase `NONEwithRSA`. No se encontró esa relación en ninguna fuente pública revisada.

## 4. RootCertManager y `sunjce_hash`

PSDevWiki afirma literalmente que el hash de SUNJCE en `RootCertManager.java` cambió en PS4 13.52 y marca la entrada como parcheada desde 13.52, no parcheada en 13.50.[3]

La captura pública enlazada en la publicación de Jose Coixao muestra un bloque estático con:

```java
AccessController.doPrivileged(new 1());
sunjce_hash = "<valor>";
```

en dos paneles con cadenas diferentes. Los valores visibles, conservados en el archivo auxiliar local, son:

```text
y8ehrm0lQ64cek7k6/+CwpSDLsjfnCesSX0agGpM10g=
At2dtIBsAdpxI/GWtq2otASAkU5OVg3QG5fFUF+KBek=
```

Estas cadenas son evidencia de una captura pública, no valores extraídos de un JAR retail. La imagen no revela el paquete completo, el método que calcula el digest, el objeto que se mide ni el caller.

La relación pública más fuerte es por nombre y contexto:

```text
RootCertManager
  → sunjce_hash / isSunJCEVerified
  → confianza en SUNJCE/JAR firmado
```

La relación con `RSACipherAdaptor` no aparece en el código visible de la captura.

## 5. Afirmación pública sobre PS4 13.52

La publicación de Jose Coixao del 16 de junio de 2026 afirma que `bdjb` fue parcheado en 13.52 y que también cambió `RootCertManager.java`.[4]

La respuesta pública de `@ps3120`, del 25 de junio de 2026, dice:

> “And added RSACipherAdaptor in sunjce_provider.jar 13.52”[5]

La frase demuestra que el autor de la respuesta hizo esa afirmación públicamente. No demuestra por sí sola:

| Pregunta | Estado |
|---|---|
| Package de la clase en PS4 | `UNVERIFIED` |
| Que sea idéntica a OpenJDK | `UNVERIFIED` |
| Que esté realmente en el JAR | `UNVERIFIED` como bytes |
| Que `SunJCE` registre `NONEwithRSA` | `UNVERIFIED` |
| Que exista un caller desde `RootCertManager` | `UNVERIFIED` |
| Que el hash mida el JAR completo | `UNVERIFIED` |
| Que el cambio sea la mitigación | `HYPOTHESIS` |

## 6. ¿El hash mide el JAR completo, una clase o algo distinto?

No se encontró un cuerpo público de `RootCertManager` que responda esta pregunta. Las posibilidades no son equivalentes:

| Hipótesis | Qué exigiría | Estado |
|---|---|---|
| Hash del JAR completo | Abrir/leer `sunjce_provider.jar`, normalizar bytes y comparar contra constante | `HYPOTHESIS` |
| Hash de una clase concreta | Localizar una entrada `.class`, leer sus bytes y comparar | `HYPOTHESIS` |
| Hash de una firma/certificado | Leer certificado, cadena o firma y comparar digest/base64 | `HYPOTHESIS` |
| Hash de otro recurso SUNJCE | Identificar path y bytes consumidos por el método | `HYPOTHESIS` |

El nombre `sunjce_hash` sólo identifica semánticamente el valor, no su entrada. Tampoco es válido concluir que la diferencia de hash se explica por añadir `RSACipherAdaptor`: para probarlo habría que conocer el objeto hasheado y comparar el provider completo antes/después.

## 7. ¿Podría explicar el cambio de hash la incorporación del adaptor?

Hay una hipótesis de dependencia débil: si `RootCertManager` mide bytes completos de `sunjce_provider.jar`, entonces añadir una clase o modificar `SunJCE` cambiaría el digest. Esa hipótesis requiere simultáneamente tres condiciones no demostradas:

1. `RootCertManager` mide el JAR completo o una región que incluye el adaptor.
2. El adaptor fue realmente añadido o modificado en la build 13.52.
3. El valor nuevo de `sunjce_hash` corresponde al resultado de ese nuevo contenido.

También existen explicaciones independientes: Sony pudo cambiar únicamente el hash permitido, sustituir un certificado, modificar otra clase SUNJCE, cambiar el archivo validado o corregir el consumidor de la policy. La evidencia pública no discrimina entre ellas.

| Relación propuesta | Clasificación |
|---|---|
| `RSACipherAdaptor` estándar implementa `NONEwithRSA` | `HISTORICAL_ONLY`/`STANDARD_JAVA` |
| PS4 13.52 añadió una clase con ese nombre | `DOCUMENTED_ONLY`/`INDIRECT_13.52` débil |
| El nuevo adaptor cambió el hash medido | `HYPOTHESIS` |
| `RootCertManager` invoca `Signature.getInstance("NONEwithRSA")` | `UNVERIFIED` |
| El adaptor corrige la concesión de `AllPermission` | `HYPOTHESIS`, sin caller |
| El adaptor es el parche de la ruta SUNJCE | `UNVERIFIED` |

## 8. Relación con la validación BD-J

La ruta histórica publicada de policy contiene una llamada a `RootCertManager.isSunJCEVerified()` dentro de una condición que, para un `CodeSource` y path concretos, puede retornar `AllPermission`.[3] Esa evidencia es histórica y no incluye `RSACipherAdaptor`.

La cadena correcta que puede escribirse sin inventar callers es:

```text
BdjPolicyImpl histórico
  → RootCertManager.isSunJCEVerified()
  → resultado booleano de confianza
  → posible Permissions/AllPermission
```

La cadena que no está demostrada es:

```text
RootCertManager
  → Signature.getInstance("NONEwithRSA")
  → SunJCE Provider.Service
  → RSACipherAdaptor
  → validación de firma/hash
  → decisión de policy
```

`NONEwithRSA` puede ser útil para verificar una firma RSA sin digest integrado, pero el hecho de que el algoritmo exista en OpenJDK no demuestra que el runtime BD-J lo use para validar `sunjce_provider.jar`. Un sistema puede comprobar un digest almacenado, una firma de JAR mediante otro API, un certificado o bytes directos sin pasar por `NONEwithRSA`.

## 9. Cambios posteriores y vulnerabilidad corregida

La fuente pública más concreta atribuye a 13.52 dos hechos documentales: el cambio de hash y el estado “patched” de la ruta SUNJCE.[3] La respuesta sobre `RSACipherAdaptor` añade una afirmación nominal sobre el contenido de `sunjce_provider.jar`.[5]

No se encontró un advisory técnico posterior, diff textual, commit Sony, manifest de clases, hash de JAR o decompilación que establezca:

- qué vulnerabilidad exacta se corrigió;
- si la corrección fue de canonicalización, firma, policy, classloader o provider;
- si `NONEwithRSA` se usó como mecanismo de validación;
- si `RootCertManager` llama directa o indirectamente al adaptor;
- si el cambio de hash fue causa o consecuencia del cambio del provider.

La etiqueta pública “patched” debe interpretarse como una afirmación documental del estado de la investigación, no como una prueba del mecanismo interno.

## 10. Clasificación final

| Hallazgo | Clasificación |
|---|---|
| `RSACipherAdaptor` existe en OpenJDK moderno | `HISTORICAL_ONLY` / `STANDARD_JAVA` |
| OpenJDK registra `Signature.NONEwithRSA` en SunJCE usando el adaptor | `HISTORICAL_ONLY` / `DIRECT_OPENJDK` |
| `RSACipherAdaptor` usa `RSACipher` y `MessageDigest.isEqual` | `HISTORICAL_ONLY` / `DIRECT_OPENJDK` |
| `RootCertManager.java` cambia `sunjce_hash` en la comparación pública | `INDIRECT_13.52` fuerte; captura `DIRECT_PUBLIC_SCREENSHOT` |
| PSDevWiki marca SUNJCE parcheado desde 13.52 | `DOCUMENTED_ONLY` / `INDIRECT_13.52` |
| Una fuente pública afirma que se añadió `RSACipherAdaptor` al provider 13.52 | `DOCUMENTED_ONLY` / `INDIRECT_13.52` débil |
| PS4 usa el package estándar `com.sun.crypto.provider` | `UNVERIFIED` |
| PS4 registra `NONEwithRSA` en `SunJCE` | `UNVERIFIED` |
| `RootCertManager` llama a `Signature.getInstance("NONEwithRSA")` | `UNVERIFIED` |
| `RootCertManager` usa `RSACipherAdaptor` | `UNVERIFIED` |
| El adaptor explica el cambio de `sunjce_hash` | `HYPOTHESIS` |
| El adaptor concede o revoca `AllPermission` | `DISCARDED` como atribución directa; policy separada |

## Resultado

**Ruta parcialmente identificada.** Está identificado el contrato criptográfico estándar de `RSACipherAdaptor` y existe una afirmación pública de su incorporación al `sunjce_provider.jar` de 13.52. Sin embargo, no existe un caller público verificable que conecte `RootCertManager` con `RSACipherAdaptor`, `NONEwithRSA` o una API de validación concreta.

El siguiente dato mínimo es un inventario o bytecode verificable de `sunjce_provider.jar` 13.52 junto con el cuerpo de `RootCertManager` o sus referencias de bytecode. En particular, se necesita encontrar una de estas evidencias:

```text
Signature.getInstance("NONEwithRSA")
Security.getProvider("SunJCE")
Provider.Service("Signature", "NONEwithRSA", ...)
new RSACipherAdaptor()
invokestatic RootCertManager.isSunJCEVerified
```

Sin esa evidencia, la relación causal entre el cambio de hash, el adaptor y el parche SUNJCE permanece `UNVERIFIED`.

## Referencias

[1]: https://github.com/openjdk/jdk/commit/35dabb1a5f31d985f00de21badeeedb026a63b94 — OpenJDK `8244336`, adición de `RSACipherAdaptor`.
[2]: https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/com/sun/crypto/provider/SunJCE.java — registro público de `Signature.NONEwithRSA`.
[3]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&action=raw&section=51 — PSDevWiki, sección SUNJCE/RootCertManager.
[4]: https://x.com/notnotzecoxao/status/2066944047944446366 — publicación pública de Jose Coixao y captura de RootCertManager.
[5]: https://x.com/ps3120/status/2070144817233789048 — afirmación pública sobre `RSACipherAdaptor` en `sunjce_provider.jar` 13.52.
[6]: https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/com/sun/crypto/provider/RSACipherAdaptor.java — implementación estándar pública.
[7]: https://hackerone.com/reports/1379975 — referencias históricas a `RootCertManager.getOriginalPersistentRoot()` y deserialización privilegiada.
