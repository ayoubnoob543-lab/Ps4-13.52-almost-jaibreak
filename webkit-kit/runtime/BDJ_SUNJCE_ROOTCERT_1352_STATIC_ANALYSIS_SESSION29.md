# Investigación 29 — SUNJCE y RootCertManager en el supuesto snapshot 13.52

**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** verificar el snapshot de la Investigación 28 y analizar estáticamente sólo los artefactos realmente presentes.  
**Restricciones:** no se ejecutaron clases, JAR, ELF, BIN, exploits, payloads ni hardware; no se descifró material protegido.

## Resultado ejecutivo

El supuesto “snapshot BD-J 13.52” de la Investigación 28 **no está presente como snapshot de filesystem ni como conjunto de JARs/clases PS4 13.52** en el checkout o en la rama remota auditada. El commit remoto que documenta la Investigación 27 (`73876e6a8ac18fb3c72811be7083c99c39de7c87`) añade únicamente un informe Markdown, no `bdjstack.jar`, `rt.jar`, `sunjce_provider.jar`, `RootCertManager.class`, `BdjPolicyImpl.class`, `SunJCE.class` ni `RSACipherAdaptor.class`.

Por tanto, no es posible cumplir legítimamente una reconstrucción directa de `isSunJCEVerified()` a partir de bytes 13.52: el cuerpo, descriptor, algoritmo, objeto hasheado, comparación y ramas true/false siguen sin estar disponibles.

La discrepancia es importante:

```text
Solicitud: snapshot BD-J 13.52 obtenido y verificado
Estado local/remoto: sólo existe un informe que documenta que no se encontró tal snapshot
```

## 1. Verificación de procedencia y presencia local

Se comprobó el estado de la rama `webkit-ps4-1352-kit` y sus referencias remotas. La rama local estaba en `fe0559451afbee1ed2eb11eb08b3649ffe73d526`; el remoto contenía posteriormente el commit `73876e6a8ac18fb3c72811be7083c99c39de7c87` con el informe `BDJ_FILESYSTEM_SNAPSHOTS_1352_INVESTIGATION27.md`.

El árbol remoto no contiene un snapshot de runtime. El informe remoto afirma explícitamente que no se encontró un filesystem BD-J/JVM PS4 13.52 públicamente accesible y verificable, y enumera como ausentes `rt.jar`, `sunjce_provider.jar`, `BdjPolicyImpl.class`, `PSDescriptorFactory.class`, `XletClassLoader.class`, `BDJFactory.class`, `RSACipherAdaptor.class` y `SunJCE.class`.[1]

La búsqueda local de `/home/ubuntu` tampoco encontró archivos `bdjstack.jar`, `rt.jar`, `sunjce*.jar`, `RootCertManager*.class`, `BdjPolicyImpl*.class` ni un snapshot etiquetado como Investigación 28.

## 2. Artefactos solicitados

| Artefacto | ¿Existe como bytes 13.52? | Resultado |
|---|---|---|
| `RootCertManager.class` | No | Sólo snapshots históricos genéricos en `deepakmathi/BDJB` |
| `RootCertManager.java` | No | Sólo capturas públicas parciales |
| `RootCertManager$1.class` | No como 13.52 | Sólo snapshot histórico genérico |
| `BdjPolicyImpl.class` | No | Sólo captura/código histórico documental |
| `sunjce_provider.jar` | No | Sin bytes PS4 13.52 |
| `SunJCE.class` | No | `UNVERIFIED` |
| `RSACipherAdaptor.class` | No | `UNVERIFIED` |
| `bdjstack.jar` | No identificado como 13.52 | Sólo material histórico genérico |
| `rt.jar` | No | `UNVERIFIED` |
| Helper de `isSunJCEVerified()` | No | `UNVERIFIED` |

No se calculan hashes de artefactos inexistentes ni se inventan tamaños o rutas internas.

## 3. Lo que sí está disponible para comparación histórica

El repositorio público `deepakmathi/BDJB`, commit `491852e8cdd66b54166271413371bc65b1d4da07`, conserva clases compiladas bajo etiquetas amplias `1.xx`, `12.xx` y `13.xx`.[2]

La clase `13.xx/RootCertManager.class` tiene:

```text
size: 7044 bytes
Git blob SHA: d29b447c645ab0afdcd5f7768b944c237a2531f2
SHA-256: b2a8776617a85dfc0b4ef09b09ce0e1bea7a479298ae5b714105030d3d9c4977
MD5: 6e801548989002ac02b75ba86d8e955c
```

Ese material es un artefacto público histórico, no una prueba de PS4 13.52. Las clases `12.xx` y `13.xx` son byte-identical dentro de ese repositorio.

El constant pool y la tabla de métodos de esa clase muestran operaciones históricas de certificados y persistencia:

```text
initRootCertificate
initPersistentRoot
getOriginalPersistentRoot
normalizePath
getGrantorDigest
getRootDigestValue
getGranteeDigest
getDiscOID
loadIDFile
inKeyStore
loadKeyStore
java/security/MessageDigest
MessageDigest.getInstance
digest
SHA1withRSA
java/security/KeyStore
CertificateFactory.generateCertificate
java/security/AccessController
```

No muestran:

```text
isSunJCEVerified
sunjce_hash
sunjce_provider.jar
NONEwithRSA
RSACipherAdaptor
CodeSource
JarFile
JarEntry
```

La clasificación correcta es `HISTORICAL_ONLY`, no `DIRECT_13.52`.

## 4. `RootCertManager.isSunJCEVerified()`

### Cuerpo y descriptor

No se encontró el cuerpo del método ni su descriptor JVM en el snapshot local/remoto, en el repositorio BDJB ni en las fuentes públicas consultadas. El descriptor hipotético no se completa por nombre; no se afirma una firma que no esté observada.

**Resultado:** `UNVERIFIED`.

### Algoritmo

Los valores públicos de `sunjce_hash` son Base64 de 44 caracteres y decodifican a 32 bytes. Esto es compatible con un digest de 256 bits, pero no demuestra SHA-256 ni ningún otro algoritmo. No se encontró una instrucción `MessageDigest.getInstance("SHA-256")` asociada al campo.

**Resultado:** `UNVERIFIED`.

### Entrada hasheada

No existe implementación disponible que permita decidir entre:

```text
sunjce_provider.jar completo
RSACipherAdaptor.class / SunJCE.class
MANIFEST.MF o JarEntry
certificado/firma
recurso obtenido por CodeSource, URL o filesystem
otra representación normalizada
```

**Resultado:** `UNVERIFIED`.

### Obtención, cálculo y comparación

No se observó en una clase 13.52:

```text
InputStream.read / Files.readAllBytes
JarFile / JarEntry / Manifest
CodeSource.getLocation
Base64 decoder/encoder
MessageDigest.digest asociado a sunjce_hash
```

En consecuencia, no puede reconstruirse la comparación ni determinarse si el método devuelve `false`, lanza una excepción, rechaza el provider o sigue otra rama cuando los bytes no coinciden.

**Resultado:** `UNVERIFIED`.

## 5. `BdjPolicyImpl`

La captura pública del post de Jose Coixao muestra un fragmento histórico que realiza:

```text
codeSource.getLocation()
→ comprobar protocolo file
→ url.getFile()
→ construir javaHome/lib/ext/sunjce_provider.jar
→ comparar path
→ RootCertManager.isSunJCEVerified()
→ Permissions + AllPermission cuando la condición es verdadera
```

La imagen recuperada tiene SHA-256 `713f2e92ead82f069160de801231988fdeb884b8ec12c7ddd89182acc43fbf23` y no es un `.class` ni fuente completa.

Esto establece un consumidor histórico/documental, pero no prueba que el mismo código exista en 13.52 ni publica la rama `false`.

**Clasificación:** `HISTORICAL_ONLY` / `DOCUMENTED_ONLY`.

## 6. `sunjce_provider.jar`, `SunJCE` y `RSACipherAdaptor`

No hay un `sunjce_provider.jar` 13.52 presente localmente, en la rama remota o en el snapshot documentado por la Investigación 28. En consecuencia no pueden calcularse SHA-256, tamaño, lista de clases, presencia de `RSACipherAdaptor`, descriptor, métodos ni registro de `Signature.NONEwithRSA` para PS4.

OpenJDK público demuestra que existe un contrato genérico de `RSACipherAdaptor`/`NONEwithRSA`, pero no sustituye los bytes de Sony y no aporta procedencia PS4.[3]

Una publicación de `@ps3120` afirma que se añadió `RSACipherAdaptor` a `sunjce_provider.jar` 13.52, pero no adjunta el JAR, clase, hash, commit ni decompilación.[4]

**Clasificación para PS4 13.52:** `DOCUMENTED_ONLY`/`UNVERIFIED`; no `DIRECT_13.52`.

## 7. Verificación reproducible del hash

No se intentó probar combinaciones arbitrarias ni crear entradas ficticias. No existe en el snapshot un candidato autorizado con bytes y procedencia que permita ejecutar una prueba de igualdad:

```text
Base64(digest(candidate_bytes)) == published_sunjce_hash
```

Por ello:

| Resultado | Estado |
|---|---|
| Algoritmo exacto | No verificable |
| Objeto exacto | No verificable |
| Valor 13.52 | Sólo visible en captura pública; no como constante de una clase 13.52 recuperada |
| Reproducción del hash | No realizada porque faltan bytes fuente y método |
| `RSACipherAdaptor` PS4 | No verificable |
| Caller | Histórico/documental desde `BdjPolicyImpl` |
| Efecto de validación | Histórico: rama `true` hacia `AllPermission`; rama `false` desconocida |

## 8. Clasificación final

| Hallazgo | Clasificación |
|---|---|
| Existe un snapshot BD-J 13.52 local verificable | `DISCARDED` por ausencia de archivos; sólo existe documentación de disponibilidad investigada |
| `RootCertManager.class` público histórico | `HISTORICAL_ONLY` |
| `RootCertManager.class` público es PS4 13.52 | `UNVERIFIED` |
| `BdjPolicyImpl` llama al verificador en código histórico | `HISTORICAL_ONLY` |
| La rama histórica `true` añade `AllPermission` | `HISTORICAL_ONLY` |
| El cambio de `sunjce_hash` fue observado públicamente | `INDIRECT_13.52` / `DOCUMENTED_ONLY` |
| Algoritmo del hash | `UNVERIFIED` |
| Bytes medidos | `UNVERIFIED` |
| `sunjce_provider.jar` PS4 13.52 | `UNVERIFIED` |
| `SunJCE.class` PS4 13.52 | `UNVERIFIED` |
| `RSACipherAdaptor.class` PS4 13.52 | `UNVERIFIED` |
| Cambio funcional completo 13.50→13.52 | `UNVERIFIED` |

## Conclusión

El “snapshot BD-J 13.52” que debía ser la base de esta investigación **no está disponible como bytes verificables**. La evidencia local/remota demuestra lo contrario: el commit de la Investigación 27 documenta la búsqueda y enumera como ausentes los artefactos necesarios.

Por tanto, no puede producirse honestamente el resultado solicitado de algoritmo, objeto hasheado, comparación ni ramas de `isSunJCEVerified()`. El caller histórico de `BdjPolicyImpl` sí está documentado mediante una captura, pero no permite confirmar el comportamiento de 13.52.

La pieza mínima que falta es un conjunto de artefactos de la misma build PS4 13.52 con procedencia verificable:

```text
RootCertManager.class o RootCertManager.java
BdjPolicyImpl.class
sunjce_provider.jar
SunJCE.class
RSACipherAdaptor.class si existe
manifest/ruta/tamaño/SHA-256 del snapshot
```

Sin ese conjunto, cualquier cuerpo o pseudodiff adicional sería inventado.

## Referencias

[1]: https://github.com/ayoubnoob543-lab/firmware-lab/blob/73876e6a8ac18fb3c72811be7083c99c39de7c87/webkit-kit/runtime/BDJ_FILESYSTEM_SNAPSHOTS_1352_INVESTIGATION27.md — Informe remoto de disponibilidad de snapshots BD-J 13.52.
[2]: https://github.com/deepakmathi/BDJB/tree/491852e8cdd66b54166271413371bc65d1b4da07 — Clases históricas públicas BDJB.
[3]: https://github.com/openjdk/jdk/commit/35dabb1a5f31d985f00de21badeeedb026a63b94 — OpenJDK `RSACipherAdaptor`/`NONEwithRSA`.
[4]: https://x.com/ps3120/status/2070144817233789048 — Afirmación pública sobre `RSACipherAdaptor` en 13.52.
[5]: https://x.com/notnotzecoxao/status/2066838388976517585 — Captura pública de `BdjPolicyImpl`.
[6]: https://x.com/notnotzecoxao/status/2066944047944446366 — Captura pública de `RootCertManager.java`.
