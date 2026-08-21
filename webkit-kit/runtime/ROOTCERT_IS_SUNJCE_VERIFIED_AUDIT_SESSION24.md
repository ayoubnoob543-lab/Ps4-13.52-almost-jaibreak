# Investigación 24 — `RootCertManager.isSunJCEVerified()`

**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** búsqueda y análisis estático de implementaciones públicas, clases compiladas, decompilaciones, manifests y fuentes documentales.  
**Restricciones:** no se ejecutaron clases, JARs, exploits, payloads, ELF/BIN ni hardware; no se descifró el PUP ni se obtuvieron artefactos protegidos.

## Resultado obligatorio

| Requisito | Resultado | Clasificación |
|---|---|---|
| Cuerpo de `isSunJCEVerified()` | No localizado en una build PS4 identificable | `UNVERIFIED` |
| Descriptor JVM del método | No localizado | `UNVERIFIED` |
| Algoritmo de `sunjce_hash` | No demostrado | `UNVERIFIED` |
| Bytes exactos hasheados | No demostrados | `UNVERIFIED` |
| Recurso de entrada | No demostrado | `UNVERIFIED` |
| Comparación y ramas true/false | No publicadas | `UNVERIFIED` |
| Consumidor histórico | `BdjPolicyImpl` consulta el booleano antes de la rama histórica de `AllPermission` | `HISTORICAL_ONLY` |
| Cambio de hash entre 13.50 y 13.52 | Afirmado por PSDevWiki y visible en una captura pública | `INDIRECT_13.52` / `DIRECT_PUBLIC_SCREENSHOT` |

La investigación no encontró una implementación pública identificada explícitamente como PS4 13.50 o 13.52. Por tanto, el cuerpo del método debe considerarse **ausente de las fuentes públicas revisadas**, no reconstruido por inferencia.

## 1. Fuentes y artefactos auditados

Se revisaron el corpus local del repositorio, los informes previos de SUNJCE/RootCertManager, la sección raw de PSDevWiki, HackerOne #1379975, el índice de código público de GitHub y el repositorio público `deepakmathi/BDJB`.[1] [2] [3]

La fuente pública más cercana contiene clases compiladas bajo `bdjstack.jar_out` en carpetas amplias `1.xx`, `12.xx` y `13.xx`:

| Artefacto | Procedencia | Tamaño | Hash | Clasificación |
|---|---|---:|---|---|
| `1.xx/.../RootCertManager.class` | `deepakmathi/BDJB`, commit `491852e8cdd66b54166271413371bc65d1b4da07` | 6977 bytes | SHA-256 `a4b64e8bbb6ac68606634f562ff8c24b230d4c7eecf41660cb726314235d6da5` | `HISTORICAL_ONLY` |
| `12.xx/.../RootCertManager.class` | Mismo commit | 7044 bytes | SHA-256 `b2a8776617a85dfc0b4ef09b09ce0e1bea7a479298ae5b714105030d3d9c4977` | `HISTORICAL_ONLY` |
| `13.xx/.../RootCertManager.class` | Mismo commit | 7044 bytes | SHA-256 `b2a8776617a85dfc0b4ef09b09ce0e1bea7a479298ae5b714105030d3d9c4977` | `HISTORICAL_ONLY`; firmware exacto `UNVERIFIED` |
| `13.xx/.../RootCertManager$1.class` | Mismo commit | 956 bytes | SHA-256 `fbf98772a58c446d1a6df9c38915d65321dfc8134d2c6f4de1c1c8f82f448420` | `HISTORICAL_ONLY` |

Las clases `12.xx` y `13.xx` son byte-identical: mismo Git blob SHA `d29b447c645ab0afdcd5f7768b944c237a2531f2`, tamaño, SHA-256 y MD5 `6e801548989002ac02b75ba86d8e955c`. El repositorio no identifica `13.xx` como PS4 13.52.

## 2. Inspección de `RootCertManager.class`

El análisis pasivo del formato JVM y del constant pool de las clases públicas obtuvo métodos como:

```text
initRootCertificate
initPersistentRoot
getOriginalPersistentRoot
getOriginalBindingunitRoot
normalizePath
setCredentialCert
removeCredentialCert
getGrantorDigest
isCredentialPath
createNewPath
createNewBuPath
getRootDigestValue
getGranteeDigest
getDiscOID
loadIDFile
getGranteeDigestBytes
inKeyStore
loadKeyStore
```

También aparecen referencias a certificados, persistencia y digest:

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

No aparecen en las tres clases auditadas:

```text
isSunJCEVerified
sunjce_hash
sunjce_provider.jar
NONEwithRSA
RSACipherAdaptor
CodeSource
JarFile
JarEntry
Base64
```

Esto permite reconstruir un flujo histórico de certificados, `KeyStore`, `MessageDigest` y persistencia, pero no el método solicitado. La ausencia de estos literales no prueba que ninguna otra variante de RootCertManager los contenga; sí demuestra que los snapshots públicos auditados no son una implementación verificable del método SUNJCE mostrado en la captura.

## 3. Búsqueda específica de `isSunJCEVerified()`

La búsqueda exacta en el corpus local y en el índice público de código de GitHub no localizó un cuerpo Java, bytecode, descriptor o helper con ese nombre. Los resultados públicos relevantes sólo contienen referencias documentales o el fragmento histórico de `BdjPolicyImpl` que llama al método.[1]

La búsqueda también resultó negativa para una combinación pública que conecte:

```text
RootCertManager
→ MessageDigest.getInstance(...)
→ sunjce_hash
→ isSunJCEVerified()
```

No se encontraron llamadas verificables a:

```text
Signature.getInstance("NONEwithRSA")
Security.getProvider("SunJCE")
new RSACipherAdaptor()
new JarFile(...)
CodeSource.getLocation()
```

desde una implementación pública de `RootCertManager` identificada con PS4 13.50 o 13.52.

## 4. Algoritmo y entrada hasheada

Los valores públicos atribuidos a `sunjce_hash` son cadenas Base64 de 44 caracteres que decodifican a 32 bytes. Esto es compatible con SHA-256, SHA3-256, BLAKE2s-256 u otro valor de 256 bits, pero no identifica el algoritmo. No se localizó ninguna instrucción, literal `"SHA-256"`, `"SHA3-256"`, constructor de digest o función de normalización asociada al campo.

Las entradas posibles no pueden discriminarse:

| Candidato | Estado |
|---|---|
| `sunjce_provider.jar` completo | `HYPOTHESIS` |
| `RSACipherAdaptor.class` o `SunJCE.class` | `HYPOTHESIS` |
| Manifest o entrada concreta del JAR | `UNVERIFIED` |
| Certificado, firma o `CodeSigner` | `HYPOTHESIS` |
| Recurso obtenido mediante `CodeSource`, URL o filesystem | `HYPOTHESIS` |
| Certificados de disco del flujo público BDJB | `HISTORICAL_ONLY`, no conectados a `sunjce_hash` |

El nombre `sunjce_hash` y la relación histórica con un JAR SUNJCE hacen plausible el hash del provider, pero no lo demuestran. No existe un `sunjce_provider.jar` retail PS4 13.50/13.52 público con el que probar:

```text
Base64(digest(candidate_bytes)) == published_sunjce_hash
```

## 5. Comparación, ramas y relación con `BdjPolicyImpl`

PSDevWiki publica un fragmento histórico de policy con esta estructura conceptual:[1]

```java
if (codeSource != null) {
    URL url = codeSource.getLocation();
    if ("file".equals(url.getProtocol())) {
        String path = url.getFile();
        String jceJar = javaHome + "lib" + separator + "ext"
                      + separator + "sunjce_provider.jar";
        if (path.equals(jceJar)) {
            if (RootCertManager.isSunJCEVerified()) {
                Permissions p = new Permissions();
                p.add(new AllPermission());
                return p;
            }
        }
    }
}
```

Esto prueba históricamente que el método actuaba como condición previa nominal para una rama de policy. No publica el cuerpo del método ni permite observar el caso `false`. Las posibilidades —policy normal, excepción, rechazo del provider u otra ruta— permanecen abiertas.

La relación más fuerte que puede afirmarse es:

```text
BdjPolicyImpl histórico
→ RootCertManager.isSunJCEVerified()
→ si true, rama histórica Permissions + AllPermission
```

No puede afirmarse para 13.52 que el resultado `true` siga produciendo `AllPermission`, ni que el método compare el digest del JAR completo.

## 6. Relación con `RSACipherAdaptor`

OpenJDK público registra `com.sun.crypto.provider.RSACipherAdaptor` como servicio `Signature.NONEwithRSA` en `SunJCE`.[4] Una respuesta pública afirma que se añadió `RSACipherAdaptor` a `sunjce_provider.jar` de PS4 13.52.[5]

No se encontró una clase PS4 pública con:

```text
RSACipherAdaptor
NONEwithRSA
```

ni un caller desde `RootCertManager`. La incorporación del adaptor puede ser compatible con un cambio del hash si el objeto medido incluye bytes del provider, pero esa condición no está demostrada.

Clasificación de la relación:

```text
RootCertManager → RSACipherAdaptor: UNVERIFIED
RSACipherAdaptor → cambio de sunjce_hash: HYPOTHESIS
RSACipherAdaptor → corrección de policy: HYPOTHESIS
```

## 7. Clasificación final

| Hallazgo | Clasificación |
|---|---|
| Cambio público del valor `sunjce_hash` entre la comparación 13.50/13.52 | `INDIRECT_13.52` |
| Captura pública de la asignación del campo | `DIRECT_PUBLIC_SCREENSHOT` |
| Cuerpo de `isSunJCEVerified()` en PS4 13.52 | `UNVERIFIED` por ausencia demostrada en fuentes revisadas |
| Descriptor JVM del método | `UNVERIFIED` |
| Algoritmo | `UNVERIFIED` |
| Objeto hasheado | `UNVERIFIED` |
| Forma de obtener el objeto | `UNVERIFIED` |
| Comparación y rama `false` | `UNVERIFIED` |
| Consulta histórica desde `BdjPolicyImpl` | `HISTORICAL_ONLY` |
| Concesión histórica de `AllPermission` cuando la condición es verdadera | `HISTORICAL_ONLY` |
| Implementación pública BDJB de `RootCertManager` | `HISTORICAL_ONLY`; no contiene SUNJCE hash |
| Equivalencia del snapshot `13.xx` con PS4 13.52 | `UNVERIFIED` |
| Relación con `RSACipherAdaptor` | `UNVERIFIED`/`HYPOTHESIS` |

## Pieza mínima faltante

El artefacto mínimo que resolvería la investigación es `RootCertManager.class` de una build PS4 identificada como 13.50 o 13.52, con su ruta, tamaño, SHA-256 y bytecode. Como alternativa válida serviría un `bdjstack.jar` de esa build con el mismo metadata.

Para resolver si la entrada es el JAR completo o una clase/manifest/certificado concreto, también se necesita `sunjce_provider.jar` de la misma build, su manifest, entradas ZIP, certificados/firma y SHA-256.

Sin esos artefactos, el cuerpo, descriptor, algoritmo, entrada, comparación y rama `false` no pueden reconstruirse sin inventar código.

## Conclusión

**Cuerpo/descriptor encontrado:** no.  
**Algoritmo:** no demostrado.  
**Entrada hasheada:** no demostrada.  
**Comparación y ramas:** no publicadas.  
**Relación con `BdjPolicyImpl`:** histórica y documental; no confirmada para 13.52.  
**Estado:** `UNVERIFIED` para la implementación PS4 solicitada.

La búsqueda produjo una ausencia reproducible, no una implementación nueva. El próximo punto de evidencia debe ser una clase/JAR de firmware identificado, no otra extrapolación desde el snapshot público BDJB.

## Referencias

[1]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&action=raw&section=51 — PSDevWiki, sección SUNJCE/RootCertManager.
[2]: https://hackerone.com/reports/1379975 — HackerOne #1379975, código histórico de policy y callers de `RootCertManager`.
[3]: https://github.com/deepakmathi/BDJB/tree/491852e8cdd66b54166271413371bc65b1d4da07 — Snapshot público BDJB con clases compiladas históricas.
[4]: https://github.com/openjdk/jdk/commit/35dabb1a5f31d985f00de21badeeedb026a63b94 — OpenJDK `RSACipherAdaptor` y `NONEwithRSA`.
[5]: https://x.com/ps3120/status/2070144817233789048 — Afirmación pública sobre `RSACipherAdaptor` en `sunjce_provider.jar` 13.52.
