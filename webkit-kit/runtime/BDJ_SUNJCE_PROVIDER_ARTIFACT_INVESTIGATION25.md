# Investigación 25 — Artefactos públicos de `sunjce_provider.jar` para PS4 13.50/13.52

**Autor:** Manus AI  
**Fecha:** 2026-08-21  
**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** búsqueda, validación y comparación estática de artefactos públicos. No se descargaron PUPs, dumps privados ni material protegido; no se ejecutaron exploits, payloads, JAR/ELF/BIN ni hardware.

## Resultado ejecutivo

No se encontró un `sunjce_provider.jar` retail PS4 verificable de 13.50 ni de 13.52. Tampoco se encontró un snapshot inequívoco que contenga `RSACipherAdaptor.class`, `SunJCE.class` o un provider PS4 etiquetado con esas versiones.

Sí se encontró y validó un repositorio público con snapshots de `bdjstack.jar` y clases `RootCertManager`, pero sus etiquetas son amplias (`12.xx`, `13.xx`) y no prueban una build PS4 13.50/13.52. Esos JARs no contienen `RSACipherAdaptor`, `SunJCE`, `sunjce_provider.jar` ni registros `Signature.NONEwithRSA`.

| Resultado obligatorio | Estado | Clasificación |
|---|---|---|
| Artefacto `sunjce_provider.jar` PS4 13.50 | No encontrado | `UNVERIFIED` |
| Artefacto `sunjce_provider.jar` PS4 13.52 | No encontrado | `UNVERIFIED` |
| Snapshot equivalente inequívoco 13.50 | No encontrado | `UNVERIFIED` |
| Snapshot equivalente inequívoco 13.52 | No encontrado | `UNVERIFIED` |
| `RSACipherAdaptor.class` PS4 13.52 | No encontrado | `UNVERIFIED` |
| `RSACipherAdaptor.class` PS4 13.50 | No encontrado | `UNVERIFIED` |
| Cambio de `sunjce_hash` | Visible en captura/documentado públicamente | `INDIRECT_13.52` |
| Relación causal con `RSACipherAdaptor` | No demostrada | `HYPOTHESIS` |

## Fuentes y auditoría realizada

Se revisaron los workspaces locales, informes previos, repositorios públicos históricos de BD-JB y el repositorio público `deepakmathi/BDJB`. También se ejecutaron búsquedas exactas en el índice de código público de GitHub:

| Consulta | Resultado del índice de código |
|---|---:|
| `RSACipherAdaptor.class` | 0 coincidencias |
| `sunjce_hash` | 0 coincidencias |
| `isSunJCEVerified` | 0 coincidencias |
| `sunjce_provider.jar` | 13.472 coincidencias genéricas, sin artefacto PS4 verificable identificado |

El resultado masivo para `sunjce_provider.jar` corresponde principalmente a JDKs y documentación Java genérica. No constituye evidencia de un provider PS4. Las búsquedas exactas de los hashes Base64 publicados tampoco identificaron un repositorio o archivo público.

## Artefactos públicos encontrados

### `deepakmathi/BDJB`

Repositorio: [github.com/deepakmathi/BDJB][1]  
Commit auditado: `491852e8cdd66b54166271413371bc65d1b4da07`.

El repositorio contiene snapshots de `bdjstack.jar` y clases extraídas con etiquetas amplias. Los artefactos relevantes son:

| Archivo | Tamaño | SHA-256 | Metadata observable | Firmware demostrable |
|---|---:|---|---|---|
| `12.xx/bdjstack.jar` | 874.506 bytes | `96177957170728122b92ddf7f9a95a88314b55948dbab04886f75a9b308cd948` | 987 clases; manifest Java/Ant; `RootCertManager.class` | Sólo etiqueta `12.xx`; no PS4 13.50/13.52 |
| `13.xx/bdjstack.jar` | 875.130 bytes | `96c0f1c001dfb90c33052ca2448f588a6d7f8f5cb43ab54152d9db4082172986` | 987 clases; manifest Java/Ant; `RootCertManager.class` | Sólo etiqueta `13.xx`; no subversión ni PS4 retail demostrada |
| `13.xx/.../RootCertManager.class` | 7.044 bytes | `b2a8776617a85dfc0b4ef09b09ce0e1bea7a479298ae5b714105030d3d9c4977` | Java class version 47.0; constant pool con `MessageDigest`, `SHA1withRSA`, `KeyStore` y certificados | Snapshot histórico/genérico, no 13.50/13.52 |

Los manifiestos de `12.xx/bdjstack.jar` y `13.xx/bdjstack.jar` son iguales en contenido relevante:

```text
Manifest-Version: 1.0
Ant-Version: Apache Ant 1.8.2
Created-By: 1.4.2_19-b04 (Sun Microsystems Inc.)
```

Ambos JARs contienen 987 clases y la misma lista de nombres de entradas. La diferencia de 624 bytes en el tamaño del contenedor no se traduce en clases nuevas visibles; los timestamps y el empaquetado difieren. Las entradas relevantes incluyen `RootCertManager.class`, `RootCertManager$1.class`, `BDASignatureFile.class` y `CredentialSignature.class`.

La inspección estática de `RootCertManager.class` encontró referencias a `MessageDigest`, `MessageDigest.getInstance`, `digest`, `SHA1withRSA`, `KeyStore` y certificados. No encontró los literales o referencias siguientes:

```text
sunjce_hash
isSunJCEVerified
sunjce_provider.jar
NONEwithRSA
RSACipherAdaptor
SunJCE
```

Por tanto, estos snapshots permiten estudiar una variante histórica de gestión de certificados, pero **no proporcionan el provider SUNJCE de PS4 ni resuelven el cambio 13.50→13.52**.

### Repositorios históricos BD-JB

Se auditaron también:

- [TheOfficialFloW/bd-jb][2], commit local `8a31b642375f320681aebf5c1fbb00b06c321fb4`.
- [sleirsgoevy/bd-jb][3], commit local `28238490805f5026122daadb2ed73579818eae63`.

No contienen `sunjce_provider.jar`, `RSACipherAdaptor.class`, `SunJCE.class`, `sunjce_hash` ni `isSunJCEVerified`. El repositorio de sleirsgoevy sí contiene adaptadores y llamadas históricas relacionadas con `ProviderAdapter`, `MessageDigest`, `ClassLoader$NativeLibrary` y `sceKernelDlsym`, pero no son el provider retail y no pueden utilizarse como evidencia directa de 13.50/13.52.

## Comparación estática de snapshots `bdjstack.jar`

| Propiedad | `12.xx` | `13.xx` | Diferencia observable |
|---|---|---|---|
| Tamaño del JAR | 874.506 bytes | 875.130 bytes | +624 bytes |
| SHA-256 | `96177957170728122b92ddf7f9a95a88314b55948dbab04886f75a9b308cd948` | `96c0f1c001dfb90c33052ca2448f588a6d7f8f5cb43ab54152d9db4082172986` | Distinto contenedor |
| Clases | 987 | 987 | Sin diferencia de conteo |
| Manifest | Java 1.4.2 / Ant 1.8.2 | Igual | Ninguna diferencia textual relevante |
| `RootCertManager.class` | 7.044 bytes | 7.044 bytes | Byte-identical según SHA-256 |
| `RSACipherAdaptor.class` | Ausente | Ausente | No encontrado |
| `SunJCE.class` | Ausente | Ausente | No encontrado |
| `Signature.NONEwithRSA` | Ausente | Ausente | No encontrado |
| `sunjce_hash` | Ausente | Ausente | No encontrado |

La diferencia entre ambos snapshots no debe confundirse con un diff PS4 13.50→13.52: las carpetas no identifican esas subversiones y no contienen `sunjce_provider.jar`.

## `RSACipherAdaptor`, `SunJCE` y `NONEwithRSA`

La única implementación verificable localizada es la de OpenJDK moderno. El commit [OpenJDK 8244336][4] añade `com.sun.crypto.provider.RSACipherAdaptor` como un adaptador de `SignatureSpi` para `Signature.NONEwithRSA`, usando `RSACipher`. La implementación estándar demuestra el contrato Java/OpenJDK, no el contenido del provider PS4.

Una respuesta pública de `@ps3120` afirma que `RSACipherAdaptor` fue añadido al `sunjce_provider.jar` de PS4 13.52.[5] No proporciona el JAR, hash, package confirmado, manifest, blob, decompilación ni caller. Por ello:

| Afirmación | Clasificación |
|---|---|
| `RSACipherAdaptor` existe en OpenJDK moderno | `HISTORICAL_ONLY` / estándar público |
| OpenJDK lo registra para `Signature.NONEwithRSA` | `HISTORICAL_ONLY` / estándar público |
| PS4 13.52 contiene una clase con ese nombre | `INDIRECT_13.52` débil / afirmación textual |
| PS4 13.50 contiene o no contiene esa clase | `UNVERIFIED` |
| La clase PS4 es byte-identical a OpenJDK | `UNVERIFIED` |
| El provider PS4 13.52 registra `NONEwithRSA` | `UNVERIFIED` |
| `RootCertManager` usa el adaptor | `UNVERIFIED` |

No se puede declarar “presente en PS4 13.52” sin el blob de clase o un inventario de JAR cuya procedencia identifique inequívocamente la build.

## Manifests, firmas y certificados

No se encontró un manifest de `sunjce_provider.jar` PS4 13.50/13.52. Los manifests de `bdjstack.jar` públicos sólo contienen metadatos de construcción Java/Ant y no enumeran provider JCE, `RSACipherAdaptor`, `SunJCE` ni `NONEwithRSA`.

No se encontró un certificado, firma JAR, `CodeSigner`, `JarEntry`, lista de entradas ZIP ni hash de provider atribuible a PS4 13.50/13.52. El hecho de que PSDevWiki describa históricamente una validación SUNJCE y que `RootCertManager.java` cambie de constante no sustituye estos artefactos.

## Relación con `sunjce_hash`

La captura pública permite observar dos constantes Base64 distintas de 44 caracteres, que decodifican a 32 bytes. No se encontró el objeto medido ni el algoritmo. Por ello no puede probarse que:

```text
sunjce_hash = digest(sunjce_provider.jar)
```

ni que la incorporación de `RSACipherAdaptor` haya causado el cambio. La hipótesis sólo sería comprobable con el provider de ambas builds y el cuerpo de `RootCertManager.isSunJCEVerified()`:

```text
Base64(digest(candidate_bytes)) == published_sunjce_hash
```

Sin conocer `candidate_bytes`, el algoritmo y la normalización de entrada, no existe comparación causal reproducible.

## Relación con `RootCertManager`

Los snapshots públicos contienen una clase histórica `RootCertManager` con operaciones de certificados y digest, pero no `sunjce_hash` ni `isSunJCEVerified`. El fragmento de policy publicado por PSDevWiki conecta nominalmente `RootCertManager.isSunJCEVerified()` con una rama que puede conceder `AllPermission`; no hay implementación pública del método ni referencia pública que conecte `RootCertManager` con `RSACipherAdaptor`.

La cadena permanece incompleta:

```text
RootCertManager
  → ¿qué bytes/algoritmo?
  → ¿qué provider/clase?
  → sunjce_hash
  → isSunJCEVerified()
  → BdjPolicyImpl
  → AllPermission
```

## Conclusión final

El artefacto PS4 `sunjce_provider.jar` de 13.50 **no fue encontrado**. El artefacto PS4 `sunjce_provider.jar` de 13.52 **no fue encontrado**. No se localizó un snapshot inequívoco que permita comparar ambas builds.

La única evidencia concreta adicional es negativa pero reproducible: los snapshots públicos `deepakmathi/BDJB` `12.xx`/`13.xx` contienen `bdjstack.jar` y `RootCertManager.class`, pero no contienen el provider SUNJCE ni ninguna de las clases objetivo; además, sus etiquetas no permiten atribuirlos a PS4 13.50/13.52.

Por tanto, no puede determinarse si `RSACipherAdaptor` existe realmente en el provider PS4 13.52 ni si ya existía en 13.50. La relación con el cambio de `sunjce_hash` y `RootCertManager` queda en `HYPOTHESIS`/`UNVERIFIED`.

La pieza mínima restante para cerrar la cadena causal es:

> **Un `sunjce_provider.jar` o snapshot de clases del provider para PS4 13.50 y 13.52, cada uno con procedencia de firmware inequívoca, tamaño y SHA-256, acompañado del bytecode de `RootCertManager.isSunJCEVerified()` o de un diff que muestre el algoritmo, los bytes de entrada y la comparación.**

## Referencias

[1]: https://github.com/deepakmathi/BDJB/tree/491852e8cdd66b54166271413371bc65d1b4da07 "deepakmathi/BDJB, commit auditado"
[2]: https://github.com/TheOfficialFloW/bd-jb "TheOfficialFloW/bd-jb"
[3]: https://github.com/sleirsgoevy/bd-jb "sleirsgoevy/bd-jb"
[4]: https://github.com/openjdk/jdk/commit/35dabb1a5f31d985f00de21badeeedb026a63b94 "OpenJDK 8244336 — Restrict algorithms at JCE layer"
[5]: https://x.com/ps3120/status/2070144817233789048 "Afirmación pública sobre RSACipherAdaptor en sunjce_provider.jar 13.52"
[6]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer Wiki — Vulnerabilities"
