# Reconstrucción de `BdjPolicyImpl → RootCertManager.isSunJCEVerified()`

**Autor:** Manus AI  
**Fecha:** 2026-08-21  
**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** análisis estático y documental exclusivamente; no se ejecutaron exploits, payloads, JAR/ELF/BIN ni hardware.

## Conclusión ejecutiva

La cadena puede reconstruirse de forma parcial y verificable:

```text
CodeSource
  → CodeSource.getLocation()
  → URL de protocolo file
  → extracción de URL.getFile()
  → comparación/canonicalización de ruta
  → identificación histórica de lib/ext/sunjce_provider.jar
  → RootCertManager.isSunJCEVerified()
  → Permissions.add(new AllPermission())
```

El método público de policy que puede fijarse por código es:

```java
public PermissionCollection getPermissions(CodeSource paramCodeSource)
```

En el caso nested-JAR documentado por HackerOne, `BdjPolicyImpl` extiende `Policy`, comprueba `paramCodeSource != null`, obtiene `URL url = paramCodeSource.getLocation()`, exige protocolo `file`, aplica `new File(url.getFile()).getCanonicalPath()` y concede `AllPermission` cuando la ruta canónica empieza por `javaHome + "lib" + File.separator + "ext"`. El reporte identifica PS4 13.00–13.02, no 13.50 ni 13.52.[1]

PSDevWiki publica otra variante histórica en la que, después de comparar la ruta con `javaHome/lib/ext/sunjce_provider.jar`, se llama a `RootCertManager.isSunJCEVerified()`. Si el método devuelve verdadero, se crea una colección de permisos, se añade `AllPermission` y se retorna.[2] El método no recibe argumento y su retorno documentado es, por la condición Java, `boolean`:

```java
RootCertManager.isSunJCEVerified() // boolean, sin argumentos
```

**No existe código público verificable del cuerpo de `isSunJCEVerified()`**, ni descriptor JVM/bytecode de la variante PS4 13.50/13.52. En particular, no puede demostrarse si compara `sunjce_hash` con el JAR completo, una clase, un certificado, una firma, un manifest u otro recurso; tampoco puede demostrarse la rama exacta cuando falla.

La clasificación final es:

> **`BdjPolicyImpl.getPermissions(CodeSource)`: DOCUMENTED_ONLY/HISTORICAL_ONLY. `RootCertManager.isSunJCEVerified()` como consumidor nominal: DOCUMENTED_ONLY/HISTORICAL_ONLY. Cambio de `sunjce_hash` entre 13.50 y 13.52: INDIRECT_13.52 fuerte para la existencia del cambio, UNVERIFIED para su semántica. Código actual 13.52: no demostrado.**

## Fuentes y procedencia

| Fuente | Material observable | Alcance de firmware | Clasificación |
|---|---|---|---|
| HackerOne #3452696 | Firma y cuerpo de un `BdjPolicyImpl.getPermissions(CodeSource)`; `CodeSource`, `URL`, canonicalización y `AllPermission` | PS4 13.00–13.02 según el reporte | `HISTORICAL_ONLY` |
| PSDevWiki, sección SUNJCE | Fragmento que compara la ruta del provider, llama a `RootCertManager.isSunJCEVerified()` y retorna `AllPermission` | Variante histórica; la propia página la relaciona con la familia ≤13.50 y marca el cambio desde 13.52 | `DOCUMENTED_ONLY` / `HISTORICAL_ONLY` |
| Captura pública de `RootCertManager.java` | Constante `sunjce_hash` distinta en los paneles atribuidos a 13.50 y 13.52 | 13.50/13.52 atribuidos por la fuente | `INDIRECT_13.52` para el cambio de constante; `UNVERIFIED` para el uso |
| `TheOfficialFloW/bd-jb` | Repositorio histórico de BD-JB; no contiene `RootCertManager` ni `BdjPolicyImpl` | Histórica | `HISTORICAL_ONLY` |
| `sleirsgoevy/bd-jb` | Código de adaptación pública; no contiene `RootCertManager` ni `isSunJCEVerified()` | Histórica | `HISTORICAL_ONLY` |
| Respuesta pública sobre `RSACipherAdaptor` | Afirmación textual de que fue añadido a `sunjce_provider.jar` en 13.52 | 13.52 atribuido | `INDIRECT_13.52`; contenido exacto `UNVERIFIED` |

## 1. `BdjPolicyImpl`: firma y flujo verificable

### 1.1 Firma

HackerOne #3452696 publica la siguiente forma de clase y método:

```java
public class BdjPolicyImpl extends Policy {
    private static String javaHome = System.getProperty("java.home");

    public PermissionCollection getPermissions(CodeSource paramCodeSource) {
        // ...
    }
}
```

La firma relevante es, por tanto, `getPermissions(CodeSource): PermissionCollection`. La clase base es `java.security.Policy`, y el argumento es un `java.security.CodeSource`. Esta evidencia es código incluido en un reporte público, pero corresponde al caso nested-JAR de PS4 13.00–13.02; no es bytecode de 13.52.[1]

### 1.2 Obtención de la ubicación

El flujo publicado es:

```java
if (paramCodeSource != null) {
    URL url = paramCodeSource.getLocation();
    if (url.getProtocol().equals("file")) {
        String path = new File(url.getFile()).getCanonicalPath();
        // comparación de la ruta y decisión de permisos
    }
}
```

La entrada de policy es, por tanto, el `CodeSource` que acompaña a la clase/código cuya colección de permisos se solicita. `CodeSource.getLocation()` suministra una `URL`; la variante documentada exige `file`, extrae `URL.getFile()` y transforma la ruta mediante `File.getCanonicalPath()`.

En el caso de nested-JAR, HackerOne documenta la ruta de policy como:

```text
file:/dsm/00000.jar/../../app0/bdjstack/lib/ext/00000.jar
```

La policy la canonicaliza a:

```text
/app0/bdjstack/lib/ext/00000.jar
```

Mientras tanto, el loader conserva la representación no canónica y la interpreta como una entrada literal de JAR anidado. Esa divergencia es el caso CVE-2025-64390/GHSA-87pc-67c4-x49 documentado para 13.00–13.02, no una prueba de que exista igual en 13.52.[1]

### 1.3 Condición de `AllPermission` en el caso publicado por HackerOne

El cuerpo publicado contiene la condición conceptual siguiente:

```java
if (path.startsWith(javaHome + "lib" + File.separator + "ext")) {
    Permissions permissions = new Permissions();
    permissions.add(new AllPermission());
    return permissions;
}
```

Esto demuestra que, en esa variante, la condición suficiente para la rama de permisos completos era que la ruta canónica empezara por el prefijo confiable de `javaHome/lib/ext`. El reporte muestra después un retorno de permisos normales para las rutas que no satisfacen la condición, aunque el extracto resumido no reproduce el cuerpo completo del retorno por defecto.[1]

### 1.4 Variante SUNJCE publicada por PSDevWiki

PSDevWiki publica una condición más específica, con esta estructura:

```java
if (path.equals(jceJar)) {
    if (RootCertManager.isSunJCEVerified()) {
        Permissions p = new Permissions();
        p.add(new AllPermission());
        return p;
    }
}
```

La variable `jceJar` se construye con la forma:

```java
javaHome + "lib" + separator + "ext"
        + separator + "sunjce_provider.jar"
```

El flujo verificable de esta variante es, por tanto:

1. Existe un `CodeSource`.
2. Se obtiene su `URL`.
3. Se exige el protocolo `file`.
4. Se obtiene una representación de ruta.
5. La representación se compara con la ruta esperada de `sunjce_provider.jar`.
6. Se llama a `RootCertManager.isSunJCEVerified()` sin argumentos.
7. Sólo si devuelve `true`, se añade `AllPermission` y se retorna la colección.

El fragmento no muestra el cuerpo de `isSunJCEVerified()`, ni el retorno posterior cuando devuelve `false`. La interpretación más conservadora es que la ejecución cae al mecanismo normal de permisos de `Policy`, pero esa parte no debe marcarse como código demostrado de 13.52.

## 2. `RootCertManager.isSunJCEVerified()`

### 2.1 Firma y retorno

La llamada publicada es exactamente:

```java
RootCertManager.isSunJCEVerified()
```

Al usarse como operando de `if`, la firma observable debe ser compatible con un método estático sin argumentos que devuelva `boolean` o un valor booleano equivalente en el lenguaje decompilado. No se publica el descriptor JVM (`()Z`) ni el bytecode; por ello la clasificación de la firma exacta es `DOCUMENTED_ONLY`, no `DIRECT_13.52`.

### 2.2 Ausencia del cuerpo

Las búsquedas locales y públicas realizadas no encontraron:

- cuerpo fuente completo de `RootCertManager` con `isSunJCEVerified()`;
- descriptor de método o listado `javap` del runtime PS4 13.50/13.52;
- bytecode o decompilación que muestre `MessageDigest`, `DigestInputStream`, `JarFile`, `JarEntry`, `Certificate`, `CodeSigner`, `CodeSource`, `ClassLoader` o streams dentro del método;
- helper separado identificado como calculador de `sunjce_hash`;
- JAR retail de `bdjstack` o `sunjce_provider.jar` de ambas versiones con procedencia verificable.

Los repositorios públicos históricos `TheOfficialFloW/bd-jb` y `sleirsgoevy/bd-jb` tampoco contienen `RootCertManager`, `isSunJCEVerified`, `BdjPolicyImpl` ni `sunjce_hash` en los commits auditados. El segundo repositorio sí contiene `FakeProvider` con uso de `ProviderAdapter` y `MessageDigest` para SHA/SHA-1, pero ese código no implementa la verificación de SUNJCE y no identifica el algoritmo del hash de `RootCertManager`.[3] [4]

### 2.3 Argumento de entrada

El método publicado no recibe argumento. La entrada que puede utilizar internamente sólo puede derivarse de estado global, configuración, rutas conocidas, classloader, filesystem o recursos del runtime; no puede atribuirse una fuente concreta sin el cuerpo del método. La ruta del `CodeSource` se usa en `BdjPolicyImpl` antes de la llamada, pero no demuestra que `RootCertManager` la vuelva a obtener ni que mida el objeto ubicado allí.

### 2.4 Algoritmo y comparación

La captura pública muestra una constante `String` llamada `sunjce_hash`, distinta entre las versiones atribuidas a 13.50 y 13.52. Ambos valores son Base64 de 32 bytes. Eso es compatible con SHA-256, pero no demuestra SHA-256 ni demuestra que el valor sea el digest del JAR completo.

No hay evidencia pública de una llamada a:

```java
MessageDigest.getInstance("SHA-256")
```

ni a SHA-1, SHA-384, SHA-512, SHA3-256, un algoritmo propietario o una API de firma. Tampoco puede saberse si el valor se compara mediante `String.equals`, `MessageDigest.isEqual`, una comparación de certificados, una validación de firma o un helper propietario.

## 3. ¿Qué recurso podría validarse?

| Posible entrada | Qué la haría plausible | Evidencia publicada | Clasificación |
|---|---|---|---|
| JAR completo `sunjce_provider.jar` | El nombre del campo y la ruta confiable se refieren al provider; cambiar una clase podría cambiar el digest del contenedor | No hay lectura del JAR ni hash reproducible | `HYPOTHESIS` |
| Clase o recurso dentro del provider | Permite validar sólo contenido funcional estable | No hay nombre de clase/recurso ni stream | `UNVERIFIED` |
| Manifest o entrada ZIP | Permite una huella estable del contenido relevante | No hay `JarFile`, `JarEntry` ni `Manifest` visible | `UNVERIFIED` |
| Certificado o firma | El flujo histórico trata con JARs firmados y keystores | No hay `Certificate`, `CodeSigner` ni verificador visible | `HYPOTHESIS` |
| Ruta, metadata o bytes normalizados | Puede evitar diferencias de empaquetado | No hay transformación publicada | `UNVERIFIED` |

La hipótesis “JAR completo” es razonable, pero no se puede demostrar matemáticamente a partir de una sola salida de 32 bytes. Incluso si `RSACipherAdaptor` fue añadido al provider en 13.52, el cambio de digest sólo sería compatible con esa hipótesis; no probaría que el objeto medido sea el JAR completo ni que el adaptor sea el motivo del cambio.

## 4. Variantes y firmware

| Variante | Evidencia | Firmware atribuible | Clasificación |
|---|---|---|---|
| `BdjPolicyImpl` con prefijo canónico `javaHome/lib/ext` | Código completo de HackerOne nested-JAR | PS4 13.00–13.02 | `HISTORICAL_ONLY` |
| `BdjPolicyImpl` con igualdad a `sunjce_provider.jar` y llamada a `isSunJCEVerified()` | Fragmento publicado por PSDevWiki | Variante histórica asociada a la familia SUNJCE; la página afirma cambio/parche desde 13.52 | `DOCUMENTED_ONLY` / `HISTORICAL_ONLY` |
| `RootCertManager.sunjce_hash` antiguo | Captura pública | Atribuido a 13.50 | `INDIRECT_13.52` sólo en comparación con el panel nuevo |
| `RootCertManager.sunjce_hash` nuevo | Captura pública | Atribuido a 13.52 | `INDIRECT_13.52` para el cambio de constante |
| `RSACipherAdaptor` añadido al provider | Afirmación textual pública | Atribuido a 13.52 | `INDIRECT_13.52`; clase/caller/bytes `UNVERIFIED` |
| Implementación completa del método en 13.52 | No localizada | 13.52 | `UNVERIFIED` |

Debe señalarse una ambigüedad editorial en PSDevWiki: el bloque describe código “removido en PS4 13.50 comparado con PS4 13.04”, mientras que la propia página presenta la rama SUNJCE y la llamada de verificación en el contexto del parche desde 13.52. Sin los archivos decompilados originales no es posible resolver si el fragmento corresponde a 13.04, a una variante 13.50 o a una reconstrucción editorial que mezcla revisiones. Esta ambigüedad impide elevar el flujo a `DIRECT_13.52`.

## 5. Qué ocurre si la verificación falla

Lo que se demuestra por el fragmento es sólo la rama positiva:

```java
isSunJCEVerified() == true
    → Permissions
    → add(AllPermission)
    → return
```

No se publica la rama negativa. Las posibilidades compatibles con la evidencia son:

| Resultado de fallo posible | Evidencia | Clasificación |
|---|---|---|
| Caída a permisos normales | Patrón usual de `Policy.getPermissions`; el extracto menciona retorno normal | `DOCUMENTED_ONLY`/`HISTORICAL_ONLY` |
| `SecurityException` | Posible en verificadores de confianza | `HYPOTHESIS` |
| Error de inicialización o excepción envuelta | Posible si se usa filesystem/crypto bajo inicialización privilegiada | `HYPOTHESIS` |
| Rechazo específico del loader antes de policy | No aparece en el fragmento | `UNVERIFIED` |

No debe afirmarse que la no coincidencia “deshabilita exactamente” una ruta concreta sin el cuerpo del método y el retorno completo de policy.

## 6. Relación con `sunjce_hash` y `RSACipherAdaptor`

La relación verificable es temporal y nominal:

```text
RootCertManager.java cambia su constante sunjce_hash
+ una fuente afirma que aparece RSACipherAdaptor en sunjce_provider.jar 13.52
```

No se ha publicado una cadena de callers:

```text
RootCertManager → cálculo de digest → comparación → isSunJCEVerified
```

Por ello no puede afirmarse que `RSACipherAdaptor` sea leído, hasheado, validado o invocado por `RootCertManager`. El método podría validar un JAR, un certificado, una firma, un recurso o metadata independiente. La ausencia de `RootCertManager` en BD-JB público es consistente con que el proyecto distribuya sólo el exploit/cliente y no el runtime propietario, pero no aporta evidencia del comportamiento 13.52.

## 7. Respuesta por requisito

| Requisito | Resultado | Clasificación |
|---|---|---|
| Cuerpo público de `BdjPolicyImpl` | Sí, para nested-JAR; no necesariamente la variante SUNJCE exacta | `HISTORICAL_ONLY` |
| Firma de `getPermissions` | `getPermissions(CodeSource): PermissionCollection` | `DOCUMENTED_ONLY`/`HISTORICAL_ONLY` |
| Firma de `isSunJCEVerified` | Sin argumentos; retorno booleano por uso en `if`; descriptor no publicado | `DOCUMENTED_ONLY` |
| Ruta del provider | `javaHome + lib + separator + ext + separator + sunjce_provider.jar` | `DOCUMENTED_ONLY`/`HISTORICAL_ONLY` |
| Condición de `AllPermission` | Igualdad de ruta y resultado verdadero del verificador | `DOCUMENTED_ONLY` |
| Efecto de fallo | No publicado con precisión | `UNVERIFIED` |
| Algoritmo/digest | No localizado | `UNVERIFIED` |
| Clase calculadora separada | No localizada | `UNVERIFIED` |
| Variante específica 13.50 | Cambio de constante atribuido; implementación ausente | `INDIRECT_13.52`/`UNVERIFIED` |
| Variante específica 13.52 | No hay cuerpo, descriptor ni bytes | `UNVERIFIED` |

## Pieza exacta que falta

Para cerrar la cadena se necesita al menos uno de los siguientes artefactos legítimamente verificables:

1. Bytecode o decompilación completa de `RootCertManager` para 13.50 y 13.52, incluyendo el descriptor de `isSunJCEVerified()` y helpers privados.
2. Bytecode/decompilación de la variante exacta de `BdjPolicyImpl` usada en 13.50 y 13.52, incluyendo el retorno de permisos cuando la verificación falla.
3. `sunjce_provider.jar` de ambas versiones con hash y procedencia retail verificables, junto con manifest, certificados y entradas ZIP.
4. Una traza estática o diff que muestre la llamada a `MessageDigest`, la fuente de bytes y la comparación contra `sunjce_hash`.
5. Evidencia de caller que conecte `RSACipherAdaptor` con `RootCertManager` o con el objeto validado.

## Conclusión final

La cadena histórica de confianza está demostrada sólo hasta el nivel de policy y documentación:

```text
CodeSource.getLocation()
→ ruta file del provider
→ RootCertManager.isSunJCEVerified()
→ si true: AllPermission
```

El cuerpo de `BdjPolicyImpl` del caso nested-JAR demuestra cómo una discrepancia de representación de rutas podía producir `AllPermission` en PS4 13.00–13.02. El fragmento SUNJCE demuestra documentalmente una validación adicional, pero no su implementación. Ninguna fuente pública localizada demuestra que el mismo método, algoritmo, objeto hasheado o rama de fallo estén presentes en PS4 13.52.

Por tanto, **no es posible reconstruir completamente `BdjPolicyImpl → isSunJCEVerified` para 13.52**. El resultado correcto es `UNVERIFIED` para la implementación actual y `HISTORICAL_ONLY`/`DOCUMENTED_ONLY` para la cadena publicada. El cambio de `sunjce_hash` es una evidencia indirecta fuerte de modificación entre 13.50 y 13.52, pero no permite atribuir el algoritmo ni demostrar la causa o el efecto exacto del parche.

## Referencias

[1]: https://hackerone.com/reports/3452696 "HackerOne #3452696 — PS4 BD-J privilege escalation using nested JAR"
[2]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer Wiki — Vulnerabilities"
[3]: https://github.com/TheOfficialFloW/bd-jb/tree/master "TheOfficialFloW/bd-jb"
[4]: https://github.com/sleirsgoevy/bd-jb/tree/master "sleirsgoevy/bd-jb"
[5]: https://newnegna.blogspot.com/2026/06/17-PS4-13.52-firmware-update.html "Secondary reproduction of the BdjPolicyImpl fragment"
