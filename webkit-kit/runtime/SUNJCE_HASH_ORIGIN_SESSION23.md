# Origen de `sunjce_hash`: algoritmo, entrada y consecuencia

**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** análisis estático de clases públicas, informes locales, fuentes públicas verificables y búsquedas literales.  
**Restricciones:** no se ejecutaron exploits, payloads, JAR, ELF, BIN ni hardware; no se descargaron ni descifraron artefactos protegidos de PS4 13.52.

## Resultado obligatorio

| Pregunta | Resultado | Clasificación |
|---|---|---|
| Algoritmo que produce `sunjce_hash` | No demostrado | `UNVERIFIED` |
| Objeto exacto hasheado | No demostrado | `UNVERIFIED` |
| Método que lo calcula/compara | No disponible públicamente | `UNVERIFIED` |
| Consecuencia histórica de match/mismatch | `BdjPolicyImpl` consulta `RootCertManager.isSunJCEVerified()` antes de la ruta histórica que puede retornar `AllPermission` para un `CodeSource` SUNJCE concreto | `HISTORICAL_ONLY` |
| Cambio del valor entre la comparación pública 13.50/13.52 | Afirmado por PSDevWiki y visible en una captura pública | `INDIRECT_13.52` / `DIRECT_PUBLIC_SCREENSHOT` |
| Pieza faltante | `RootCertManager` de la build relevante y/o `bdjstack.jar`/provider con bytecode, procedencia, tamaño y SHA-256 | `UNVERIFIED` |

La conclusión estricta es que **sabemos que el valor cambió, pero no sabemos qué bytes causaron el cambio**.

## 1. Evidencia pública del cambio

PSDevWiki describe la entrada como “Path traversal sandbox escape via sunjce JAR signature”, la marca “untested” y afirma que el hash SUNJCE de `RootCertManager.java` cambió en PS4 13.52. También indica “Patched: Yes since PS4 FW 13.52” y “Not patched as of PS4 FW 13.50”.[1]

La sección raw es reproducible en:

```text
https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&action=raw&section=51
```

La captura pública enlazada muestra un bloque estático con `AccessController.doPrivileged(new 1())` y dos valores Base64 diferentes de 44 caracteres. Los valores fueron conservados como evidencia visual, no como bytes de runtime:

```text
y8ehrm0lQ64cek7k6/+CwpSDLsjfnCesSX0agGpM10g=
At2dtIBsAdpxI/GWtq2otASAkU5OVg3QG5fFUF+KBek=
```

La captura local `webkit-kit/runtime/rootcertmanager_followup.webp` tiene SHA-256 `ab98050e2cf3a4e62497e986043387722672460a914fcd51270c74e94ed3d820`.

Jose Coixao afirma públicamente que `RootCertManager.java` también cambió.[2] Ninguna de estas fuentes publica el cuerpo completo del método que consume el hash.

## 2. Cuerpos y bytecode públicos localizados

La fuente pública nueva `deepakmathi/BDJB`, commit `491852e8cdd66b54166271413371bc65d1b4da07`, conserva clases compiladas `RootCertManager.class` en carpetas `1.xx`, `12.xx` y `13.xx`.[3]

La clase `13.xx` tiene 7044 bytes, Git blob SHA `d29b447c645ab0afdcd5f7768b944c237a2531f2` y SHA-256 `b2a8776617a85dfc0b4ef09b09ce0e1bea7a479298ae5b714105030d3d9c4977`. La clase `12.xx` es byte-identical.

El análisis pasivo del constant pool y de la tabla de métodos encuentra:

```text
initRootCertificate
initPersistentRoot
getOriginalPersistentRoot
getOriginalBindingunitRoot
normalizePath
getGrantorDigest
isCredentialPath
getRootDigestValue
getGranteeDigest
getDiscOID
loadIDFile
getGranteeDigestBytes
inKeyStore
loadKeyStore
```

Y contiene referencias a:

```text
java/security/MessageDigest
MessageDigest.getInstance
digest
SHA1withRSA
java/security/KeyStore
java/security/cert/CertificateFactory
generateCertificate
java/security/AccessController
/CERTIFICATE/app.discroot.crt
/CERTIFICATE/id.bdmv
dvb.persistent.root
sony.rootcert
bdrootcert
```

Pero esa clase pública no contiene los siguientes literales o referencias:

| Símbolo | Resultado en `1.xx`, `12.xx`, `13.xx` |
|---|---|
| `sunjce_hash` | Ausente |
| `isSunJCEVerified` | Ausente |
| `sunjce_provider.jar` | Ausente |
| `NONEwithRSA` | Ausente |
| `RSACipherAdaptor` | Ausente |
| `Provider` | Ausente como constante relevante |
| `Signature` | Ausente como constante relevante |

Así, el snapshot público permite reconstruir un flujo histórico de certificados, `KeyStore`, `MessageDigest`, `SHA1withRSA` y persistencia, pero **no identifica el productor de `sunjce_hash`** de la comparación pública 13.50/13.52.[3]

## 3. Algoritmos observados y por qué no bastan

La presencia de `MessageDigest.getInstance` y `digest` en `RootCertManager.class` demuestra que esa variante realiza operaciones de digest. Sin embargo, el constant pool visible no permite atribuir la cadena Base64 de 32 bytes a una instancia concreta de `MessageDigest`.

La constante `SHA1withRSA` es el nombre de un esquema de firma que aparece en el flujo histórico de certificados. No equivale a SHA-256 y tampoco implica que la cadena de 44 caracteres sea producida por `Signature.getInstance("NONEwithRSA")`.

Los valores publicados decodifican superficialmente a 32 bytes, por lo que son compatibles con una codificación Base64 de un digest SHA-256, pero esa observación no prueba el algoritmo. También podría representar bytes de otro cálculo, una salida truncada o una cadena almacenada que no sea el resultado directo de `MessageDigest.digest()`.

| Candidato | Compatibilidad superficial | Evidencia del productor | Clasificación |
|---|---|---|---|
| SHA-256 sobre bytes | 32 bytes tras Base64 | Sólo longitud; no hay caller ni `getInstance("SHA-256")` público | `HYPOTHESIS` |
| SHA-1 sobre bytes | No compatible con 32 bytes salvo transformación adicional | `SHA1withRSA` aparece en clase histórica, pero no como productor de `sunjce_hash` | `HYPOTHESIS` débil |
| SHA-384/SHA-512 truncado | Posible sólo con truncamiento/transformación | Sin código | `HYPOTHESIS` |
| Digest de certificado/firma | Compatible si la entrada se normaliza | Sin método de lectura/comparación del hash | `HYPOTHESIS` |
| Hash de JAR completo | Compatible si se hashean exactamente sus bytes | Sin `JarFile`, `JarEntry`, stream ni path en la clase pública correspondiente | `HYPOTHESIS` |
| Hash de clase concreta | Compatible | Sin archivo objetivo ni caller | `HYPOTHESIS` |

No es correcto elevar SHA-256 a “algoritmo demostrado” sólo por la longitud Base64.

## 4. ¿Qué bytes podría medir?

Se evaluaron las entradas técnicamente plausibles solicitadas:

| Entrada candidata | Evidencia a favor | Evidencia en contra o ausente | Estado |
|---|---|---|---|
| `sunjce_provider.jar` completo | El nombre `sunjce_hash` y la descripción pública hablan de un SUNJCE JAR; añadir una clase cambiaría su digest | No hay `JarFile`, `JarEntry`, stream, path o método de hash público | `HYPOTHESIS` |
| `RSACipherAdaptor.class` | Una fuente afirma que se añadió al provider 13.52 | No hay prueba de que esa clase exista en el JAR PS4 ni de que sea la entrada medida | `HYPOTHESIS` |
| `SunJCE.class` u otra clase del provider | Un cambio de registro del provider podría cambiar un hash de clase/JAR | No existe referencia de archivo o clase en `RootCertManager` público | `HYPOTHESIS` |
| `MANIFEST.MF` o firma del JAR | La descripción editorial menciona JAR firmado | No hay lectura de manifest/certificado pública | `HYPOTHESIS` |
| Certificado o firma RSA | `RootCertManager` público procesa certificados y contiene `SHA1withRSA` | No conecta ese flujo con `sunjce_hash` ni con el valor Base64 de 32 bytes | `HYPOTHESIS` |
| Recurso externo/archivo de trust | Es posible en una implementación propietaria | No hay path, `CodeSource.getLocation()` ni `URL` público asociado | `HYPOTHESIS` |

El único flujo de archivo observable en la clase pública BDJB está relacionado con certificados de disco (`/CERTIFICATE/app.discroot.crt`, `/CERTIFICATE/id.bdmv`) y persistencia. No demuestra lectura de `sunjce_provider.jar`.

## 5. `isSunJCEVerified()` y efecto del resultado

No se localizó un cuerpo público de `isSunJCEVerified()` ni una clase pública que lo contenga. La única consecuencia observable está en el código histórico publicado de `BdjPolicyImpl`: para un `CodeSource` y ruta que coinciden con `lib/ext/sunjce_provider.jar`, se consulta `RootCertManager.isSunJCEVerified()` y, si el resultado es verdadero, se construye `Permissions`, se añade `AllPermission` y se retorna esa política.[1]

El flujo histórico puede expresarse así:

```text
CodeSource.getLocation()
  → URL con protocolo file:
  → path esperado javaHome/lib/ext/sunjce_provider.jar
  → RootCertManager.isSunJCEVerified()
  → true
  → Permissions + AllPermission
```

No puede expresarse legítimamente como:

```text
sunjce_hash
  → SHA-256 confirmado
  → hash de JAR completo confirmado
  → isSunJCEVerified() confirmado
  → AllPermission en 13.52 confirmado
```

La consecuencia `AllPermission` es **HISTORICAL_ONLY**. La etiqueta “patched” de PSDevWiki es `DOCUMENTED_ONLY` y la entrada está marcada como no probada.[1]

## 6. `RSACipherAdaptor` y posible explicación del cambio

OpenJDK público registra `com.sun.crypto.provider.RSACipherAdaptor` como implementación de `Signature.NONEwithRSA` dentro de `SunJCE`.[4] Esa clase envuelve `RSACipher` y compara el resultado descifrado con los datos mediante `MessageDigest.isEqual`.

Una respuesta pública de `@ps3120` afirma que `RSACipherAdaptor` se añadió al `sunjce_provider.jar` de PS4 13.52.[5] No se publica el JAR, el package de PS4, su manifest, un hash ni un caller desde `RootCertManager`.

La explicación “añadir `RSACipherAdaptor` cambió `sunjce_hash`” requiere que el objeto hasheado incluya el archivo o clase modificada. Esa condición no está demostrada. También es posible que Sony haya cambiado sólo la constante permitida, el certificado, otra clase del provider o el consumidor de la policy.

| Afirmación | Clasificación |
|---|---|
| OpenJDK define el contrato `RSACipherAdaptor`/`NONEwithRSA` | `DIRECT_OPENJDK` |
| PS4 13.52 añadió una clase con ese nombre | `DOCUMENTED_ONLY` / `INDIRECT_13.52` débil |
| Esa clase está incluida en los bytes medidos por `sunjce_hash` | `UNVERIFIED` |
| `RootCertManager` llama a `Signature.getInstance("NONEwithRSA")` | `UNVERIFIED` |
| El cambio de hash fue causado por el adaptor | `HYPOTHESIS` |

## 7. Búsqueda literal de los hashes

Se buscaron ambos valores Base64 completos en el índice público de código de GitHub. No se encontraron coincidencias:

```text
y8ehrm0lQ64cek7k6/+CwpSDLsjfnCesSX0agGpM10g=
At2dtIBsAdpxI/GWtq2otASAkU5OVg3QG5fFUF+KBek=
```

La ausencia en el índice no prueba que no existan en imágenes, repositorios no indexados, artefactos binarios o fuentes privadas. Sólo demuestra que no se localizó una copia textual pública indexada mediante esa búsqueda.

## 8. Qué se ha demostrado y qué no

| Pregunta | Resultado estricto |
|---|---|
| ¿El hash cambió entre la comparación pública? | Sí, como evidencia editorial/captura pública; `INDIRECT_13.52` |
| ¿El valor es Base64 de 32 bytes? | Sí, por decodificación/longitud del texto publicado; no identifica productor |
| ¿El algoritmo es SHA-256? | No demostrado; `HYPOTHESIS` |
| ¿La entrada es `sunjce_provider.jar` completo? | No demostrado; `HYPOTHESIS` |
| ¿La entrada es `RSACipherAdaptor.class`? | No demostrado; `HYPOTHESIS` |
| ¿Existe `isSunJCEVerified()` público? | No localizado en el corpus ni índice público consultado |
| ¿Se publica su caller? | Sólo la consulta histórica desde `BdjPolicyImpl`; cuerpo del verificador ausente |
| ¿Hay `CodeSource`/`JarFile`/`JarEntry` en RootCertManager público? | No en los snapshots RootCertManager auditados |
| ¿El match otorga `AllPermission` en una implementación histórica? | Sí, según código histórico de `BdjPolicyImpl`; no 13.52 |
| ¿El mismatch bloquea exactamente BD-JB en 13.52? | Sólo afirmado documentalmente; no probado por bytes |

## Pieza concreta que sigue faltando

Para resolver la incógnita se necesita una implementación de la build PS4 relevante que contenga al menos:

```text
com/sony/bdjstack/security/cert/RootCertManager.class
```

y una de las siguientes evidencias de bytecode o fuente:

```text
MessageDigest.getInstance("SHA-256" | "SHA-1" | ...)
InputStream.read(...) / Files.readAllBytes(...)
JarFile / JarEntry / Manifest
CodeSource.getLocation() / URL
Base64 encoder
MessageDigest.digest(...)
ConstantValue: sunjce_hash
isSunJCEVerified() caller/body
```

Además, para decidir entre JAR completo y clase concreta se necesita el `sunjce_provider.jar` de la misma build, su manifest, tamaño y SHA-256. Sin ambos lados, no puede hacerse una prueba de igualdad:

```text
encodeBase64(digest(candidate_bytes)) == published_sunjce_hash
```

## Conclusión

**El algoritmo y el objeto exactos siguen `UNVERIFIED`.** El dato sólido es el cambio público del valor y la consecuencia histórica de consultar un booleano de confianza desde `BdjPolicyImpl`. El `RootCertManager.class` público localizado demuestra operaciones históricas de certificados y digest, pero no contiene `sunjce_hash` ni referencias SUNJCE y, por ello, no resuelve la incógnita.

El siguiente paso mínimo no es otro análisis histórico general: es obtener una clase `RootCertManager` de firmware identificado o un bytecode equivalente que exponga el cuerpo de `isSunJCEVerified()` y la entrada concreta del digest.

## Referencias

[1]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&action=raw&section=51 — PSDevWiki, sección SUNJCE/RootCertManager; afirma el cambio y marca la entrada como no probada.
[2]: https://x.com/notnotzecoxao/status/2066944047944446366 — Publicación pública de Jose Coixao y captura de `RootCertManager.java`.
[3]: https://github.com/deepakmathi/BDJB/tree/491852e8cdd66b54166271413371bc65d1b4da07 — Repositorio público con clases compiladas BD-J y snapshots etiquetados.
[4]: https://github.com/openjdk/jdk/commit/35dabb1a5f31d985f00de21badeeedb026a63b94 — OpenJDK `8244336`, `RSACipherAdaptor` y registro `NONEwithRSA`.
[5]: https://x.com/ps3120/status/2070144817233789048 — Afirmación pública sobre `RSACipherAdaptor` en `sunjce_provider.jar` 13.52.
[6]: https://hackerone.com/reports/1379975 — Código histórico de `BdjPolicyImpl`, `RootCertManager.getOriginalPersistentRoot()` y `userprefs`.
