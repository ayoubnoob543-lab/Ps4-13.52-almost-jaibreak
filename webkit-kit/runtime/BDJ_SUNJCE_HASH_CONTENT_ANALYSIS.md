# Qué representa `sunjce_hash` en `RootCertManager`

**Autor:** Manus AI  
**Fecha:** 2026-08-21  
**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** análisis estático y documental; no se ejecutaron exploits, payloads, JAR/ELF/BIN, PUPs ni hardware.

## Resumen ejecutivo

Con la evidencia pública disponible puede demostrarse que los dos valores atribuidos a `sunjce_hash` son cadenas **Base64 estándar de 44 caracteres** que decodifican a **32 bytes**. Esto es compatible con un digest de 256 bits, incluido SHA-256, pero **no identifica el algoritmo**: la longitud por sí sola también es compatible con SHA3-256, BLAKE2s-256, un valor aleatorio de 32 bytes o una salida truncada de otro mecanismo.

No puede demostrarse qué bytes se midieron. La captura pública sólo muestra la constante `sunjce_hash` dentro de un inicializador estático de `RootCertManager`, junto a `AccessController.doPrivileged`; no muestra la función de cálculo, el recurso de entrada, el consumidor ni la rama de error. PSDevWiki sí publica un fragmento histórico de `BdjPolicyImpl` que llama a `RootCertManager.isSunJCEVerified()` antes de conceder `AllPermission` al `sunjce_provider.jar` esperado, pero no publica el cuerpo de `isSunJCEVerified()` ni prueba que la misma implementación exista en 13.52.[1]

La conclusión obligatoria es, por tanto:

> **Algoritmo: no demostrado. Objeto hasheado: no demostrado. Consumidor nominal: `RootCertManager.isSunJCEVerified()` en el flujo histórico de `BdjPolicyImpl`; implementación y comportamiento 13.52: no demostrados. Efecto exacto de coincidencia/no coincidencia: no demostrado.**

El cambio matemáticamente observable entre 13.50 y 13.52 es un cambio de constante de 32 bytes, no una prueba de que se haya cambiado el JAR completo ni de que `RSACipherAdaptor` sea la causa.

## Evidencia local y pública

La captura conservada `rootcertmanager_hash_diff_1350_1352.webp` tiene SHA-256:

```text
8de5f485cf45e00c8460a85bd915d5dca42086cbe8b8457dd97f0415f5af8b0c
```

Visualmente sólo permite leer una asignación dentro de un inicializador estático:

```java
static {
    AccessController.doPrivileged(new 1());
    sunjce_hash = "...";
}
```

Los valores son:

| Atribución | Cadena visible | Longitud Base64 | Bytes decodificados | Hexadecimal decodificado |
|---|---|---:|---:|---|
| 13.50 | `y8ehrm01Q64cek7k6/+CwpSDLsjfnCesSX0agGpM10g=` | 44 | 32 | `cbc7a1ae6d3543ae1c7a4ee4ebff82c294832ec8df9c27ac497d1a806a4cd748` |
| 13.52 | `At2dtIBsAdpxI/Gwtq2otASAkU5OVg3QG5ffUF+KBek=` | 44 | 32 | `02dd9db4806c01da7123f1b0b6ada8b40480914e4e560dd01b97df505f8a05e9` |

La decodificación se realizó con el decodificador Base64 del entorno Linux; ambos resultados tienen exactamente 32 bytes. La documentación Java describe Base64 como una codificación de bytes y `MessageDigest` como una API que produce valores de longitud fija según el algoritmo, pero ninguna de esas propiedades permite invertir un digest ni deducir su entrada.[2] [3]

Las búsquedas exactas de ambas cadenas Base64 y de fragmentos distintivos no produjeron coincidencias públicas. El corpus local tampoco contiene el cuerpo de `RootCertManager`, una implementación de `isSunJCEVerified`, una llamada visible a `MessageDigest` asociada a este campo, ni bytes retail verificables de `sunjce_provider.jar`.

## Qué documenta PSDevWiki y qué no documenta

La sección pública de SUNJCE afirma que el hash de `RootCertManager.java` cambió en PS4 13.52 y que esto probablemente deshabilita la inyección de JAR antiguos firmados.[1] El verbo “probablemente” es importante: la página no publica una demostración del algoritmo, del recurso hasheado ni del resultado operacional de la comparación.

En la sección histórica de BD-JB-13.04, PSDevWiki publica este flujo simplificado:

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

Este fragmento permite identificar un **consumidor nominal histórico**: `BdjPolicyImpl` usa el resultado booleano de `RootCertManager.isSunJCEVerified()` como condición previa a conceder `AllPermission` cuando `CodeSource.getLocation()` coincide literalmente con la ruta esperada del provider. No permite saber cómo se calcula el booleano. Tampoco permite concluir que la comparación se haga contra el JAR completo: el método podría medir el JAR, una clase, un certificado, una firma, un recurso interno o cualquier otra representación estable.

## Hipótesis sobre el objeto hasheado

| Hipótesis | Evidencia a favor | Evidencia en contra o ausente | Estado |
|---|---|---|---|
| JAR completo `sunjce_provider.jar` | El nombre `sunjce` y el uso histórico de `CodeSource`/ruta del provider son compatibles; el cambio podría invalidar un JAR antiguo. | No existe cuerpo de `isSunJCEVerified()`, lectura de bytes, orden de entradas, normalización ni hash publicado. Un hash del JAR completo cambiaría por cualquier diferencia de bytes, firmas, timestamps o compresión. | `HYPOTHESIS` |
| Clase concreta dentro del provider | Un componente de confianza puede validar sólo una clase o recurso crítico. | No hay nombre de clase, `getResourceAsStream`, extracción ni digest visible. | `UNVERIFIED` |
| Certificado o firma del JAR | El flujo se relaciona históricamente con JAR firmado y confianza; un digest de 32 bytes podría representar material de firma o certificado. | No se muestra `Certificate`, `CodeSigner`, `JarEntry`, `Signature` ni una API de verificación. El hash no tiene formato de certificado o firma estructurada, pero una huella binaria sí podría ser Base64. | `HYPOTHESIS` |
| Manifest o entrada concreta del JAR | Es posible fijar una entrada estable, evitando variaciones del contenedor completo. | No aparece `Manifest`, `JarFile`, nombre de entrada ni canonicalización. | `UNVERIFIED` |
| Cadena textual, ruta o metadata | Una constante de 32 bytes podría ser digest de una representación textual o metadata. | No hay entrada ni encoding documentados; el nombre por sí solo no lo respalda. | `UNVERIFIED` |
| Digest de un recurso obtenido por `CodeSource`, classloader o filesystem | El contexto de policy hace plausibles esas fuentes. | No hay llamada a `CodeSource`, `URL`, `ClassLoader`, `FileInputStream` o stream visible en la captura. | `HYPOTHESIS` |
| Valor no criptográfico de 32 bytes | La longitud Base64 sólo demuestra 32 bytes tras decodificación. | El nombre `_hash` y la documentación pública lo presentan como hash. | `WEAK_INDIRECT` |

## Algoritmo: qué puede y qué no puede inferirse

La cadena Base64 tiene la forma esperada para 32 bytes: 32 bytes producen 43 caracteres significativos más un carácter `=` de padding, es decir, 44 caracteres. Esto descarta como representación directa completa los digest estándar de SHA-1/160 bits, SHA-384/384 bits y SHA-512/512 bits, salvo que hubieran sido truncados o transformados. No descarta SHA-256, SHA3-256, BLAKE2s-256 ni un valor arbitrario de 256 bits.

| Algoritmo o familia | Longitud binaria natural | Compatibilidad con la cadena | Conclusión |
|---|---:|---|---|
| SHA-1 | 20 bytes | Sólo con padding/truncamiento adicional no evidenciado | `NO MATCH` como digest natural |
| SHA-256 | 32 bytes | Sí | `CANDIDATO`, no demostrado |
| SHA-384 | 48 bytes | No como salida natural completa | `NO MATCH` |
| SHA-512 | 64 bytes | No como salida natural completa | `NO MATCH` |
| SHA3-256 | 32 bytes | Sí | `CANDIDATO`, no demostrado |
| BLAKE2s-256 | 32 bytes | Sí | `CANDIDATO`, no demostrado |
| Digest truncado o KDF/huella propietaria | Variable | Sí | `UNVERIFIED` |

Por tanto, no es correcto convertir la compatibilidad de tamaño en una afirmación “`sunjce_hash` es SHA-256”. Para elevarla a `DIRECT`, sería necesario observar el algoritmo en bytecode/decompilación o reproducir el valor contra una entrada conocida.

## Consumidor y efecto de coincidencia

El consumidor históricamente identificable es `RootCertManager.isSunJCEVerified()`, invocado desde `BdjPolicyImpl` dentro de la rama que concede `AllPermission` al `CodeSource` cuya URL coincide con `javaHome/lib/ext/sunjce_provider.jar`.[1] La evidencia disponible no permite distinguir si:

1. la coincidencia devuelve `true` y permite `AllPermission`;
2. la no coincidencia devuelve `false` y deja la policy normal;
3. existe una excepción que aborta la inicialización;
4. el método realiza además validaciones de firma, certificado o ubicación;
5. el método compara el digest con `sunjce_hash` o usa la constante en otra ruta.

La interpretación funcional más fuerte, pero todavía histórica, es: **el hash actúa como una condición de confianza para impedir que un archivo que sólo imita la ruta del provider sea tratado como el provider autorizado**. La frase “probablemente deshabilita inyectar JARs antiguos firmados” procede de PSDevWiki y no sustituye al cuerpo del método ni a una prueba de ejecución.[1]

## ¿Puede explicarse el cambio por `RSACipherAdaptor`?

No puede demostrarse. Una incorporación de `RSACipherAdaptor` al provider puede cambiar el hash del JAR completo, de una clase, del manifest o de una estructura de firma; por tanto, **es matemáticamente compatible** con un cambio de 32 bytes en `sunjce_hash`. Pero la implicación inversa no es válida: un cambio de hash no demuestra que el objeto medido sea el JAR completo ni que el adaptor sea la causa.

Además, la implementación pública de OpenJDK de `RSACipherAdaptor` sólo demuestra que existe un patrón de adaptación de `SignatureSpi` sobre RSA en una rama/versión de OpenJDK. No demuestra identidad de bytes, package, caller ni integración en el provider BD-J de PS4. La relación correcta es `INFERRED`/`UNVERIFIED`, no `DIRECT_13.52`.

## Disponibilidad de un `sunjce_provider.jar` público comparable

Existen artefactos públicos con el nombre `sunjce_provider` en repositorios Java, incluido un paquete indexado en Maven con versión `5.0.20.29`.[4] También existe código fuente histórico de OpenJDK para construir `sunjce_provider.jar`.[5] Estos materiales son **implementaciones Java genéricas**, no el provider retail de PS4 13.50/13.52. Su hash no puede confirmar ni refutar el valor de `RootCertManager`, porque no se conoce que sean la entrada medida ni que compartan código, compilador, empaquetado, firma o layout con el runtime de Sony.

En consecuencia, un hash calculado sobre uno de esos JARs sería sólo una comparación negativa/no concluyente. No se debe publicar como “hash SUNJCE 13.52”.

## Resultado por requisito

| Pregunta | Resultado | Confianza |
|---|---|---|
| ¿Es Base64 estándar? | Sí, por sintaxis y padding; decodifica a 32 bytes en ambos casos. | `DIRECT` sobre los valores observados |
| ¿Es SHA-256? | Compatible, pero no demostrado. | `UNVERIFIED` |
| ¿Qué formato de entrada usa? | No determinable. | `UNVERIFIED` |
| ¿Qué archivo/recurso mide? | No determinable; JAR completo es sólo hipótesis. | `UNVERIFIED` |
| ¿Cómo obtiene la entrada? | No determinable; `CodeSource`/ruta sólo aparecen en el caller histórico de policy. | `HISTORICAL_ONLY` para el contexto; `UNVERIFIED` para el cálculo |
| ¿Qué método consume el resultado? | `RootCertManager.isSunJCEVerified()` aparece en el flujo histórico de `BdjPolicyImpl`. | `HISTORICAL_ONLY` |
| ¿Qué ocurre si coincide? | Históricamente, la rama mostrada concede `AllPermission` tras coincidir ruta y verificación. | `HISTORICAL_ONLY` |
| ¿Qué ocurre si no coincide? | No publicado. | `UNVERIFIED` |
| ¿Explica `RSACipherAdaptor` el cambio? | Es compatible temporalmente, pero no causalmente demostrable. | `INFERRED` |
| ¿Existe JAR público comparable? | Sí, genérico; no retail PS4 y no utilizable para confirmar el hash. | `DIRECT` sobre disponibilidad; `NO MATCH` como evidencia PS4 |

## Pieza exacta que falta

La pieza mínima que resolvería la pregunta es una de las siguientes, idealmente ambas versiones para comparación:

| Artefacto mínimo | Pregunta que resolvería |
|---|---|
| Cuerpo de `RootCertManager.isSunJCEVerified()` y cualquier helper invocado | Algoritmo, entrada, encoding, comparación y ramas de éxito/error |
| `RootCertManager.java` decompilado completo de 13.50 y 13.52 | Contexto de inicialización, imports, nombres de recursos y cambios de flujo |
| Bytecode de `RootCertManager` o una traza estática equivalente | Confirmación independiente del algoritmo y callers |
| `sunjce_provider.jar` retail de ambas versiones con metadata de procedencia | Prueba de si los valores son digest del JAR completo, una clase o un recurso; además permite probar la hipótesis `RSACipherAdaptor` |
| Manifest, certificado/firma y entradas ZIP de ambos provider | Permite discriminar JAR completo, manifest, firma o entrada específica |

## Conclusión

La única conclusión positiva firme es estructural: ambos valores son **Base64 estándar de 32 bytes**, y la captura demuestra que se asignan como constantes distintas de `RootCertManager` en las versiones atribuidas a 13.50 y 13.52. La fuente pública relaciona históricamente `isSunJCEVerified()` con la decisión de conceder `AllPermission` al provider situado en una ruta concreta.

No puede determinarse de forma verificable el algoritmo, el formato de entrada, el archivo/recurso medido, la implementación de la comparación ni el efecto de fallo. Por ello, el cambio de hash **no puede explicarse matemáticamente como prueba de que se incorporó `RSACipherAdaptor`**. La investigación queda correctamente en `UNVERIFIED` para el contenido semántico del hash y en `HISTORICAL_ONLY` para su consumidor y efecto de policy.

## Referencias

[1]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer Wiki — Vulnerabilities"
[2]: https://docs.oracle.com/javase/8/docs/api/java/util/Base64.html "Oracle Java SE 8 — Base64"
[3]: https://docs.oracle.com/javase/8/docs/api/java/security/MessageDigest.html "Oracle Java SE 8 — MessageDigest"
[4]: https://mvnrepository.com/artifact/com.thunderhead/sunjce_provider "Maven Repository — com.thunderhead:sunjce_provider"
[5]: https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/make/com/sun/crypto/provider/Makefile "OpenJDK mirror — sunjce_provider.jar build Makefile"
