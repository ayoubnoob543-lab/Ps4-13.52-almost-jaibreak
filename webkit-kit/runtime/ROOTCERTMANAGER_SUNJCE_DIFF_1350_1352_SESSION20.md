# Diferencial público de `RootCertManager.java` y SUNJCE: PS4 13.50 → 13.52

**Repositorio:** `webkit-ps4-1352-kit`  
**Ámbito:** reconstrucción estática a partir de fuentes públicas, capturas públicas y corpus local.  
**Restricciones:** no se obtuvieron JAR/SELF/ELF protegidos, no se descifró el PUP, no se ejecutaron JAR, ELF, BIN, exploits ni hardware.

## Resumen ejecutivo

La evidencia pública permite afirmar que entre PS4 13.50 y 13.52 se publicó un **cambio de la constante `sunjce_hash` dentro de `RootCertManager.java`**. La fuente editorial primaria consultada, PSDevWiki, identifica el rango como “FW <= 13.50”, atribuye la comparación decompilada a zecoxao y afirma que el problema está parcheado desde 13.52, pero etiqueta la vulnerabilidad como **untested**.[1]

Además, una publicación pública de Jose Coixao enlaza una captura de código y afirma que `bdjb` fue parcheado en 13.52 y que otro cambio ocurrió en `RootCertManager.java`.[2] La captura pública descargada muestra dos paneles con el mismo bloque de inicialización estática y valores distintos de `sunjce_hash`. Esto es evidencia directa de una **captura pública**, no de los bytes retail 13.52 ni de un diff textual verificable.

La reconstrucción más fuerte permitida por las fuentes es:

```diff
 static {
     AccessController.doPrivileged(new 1());
-    sunjce_hash = "<valor anterior visible en captura>";
+    sunjce_hash = "<valor nuevo visible en captura>";
 }
```

No existe evidencia pública suficiente para reconstruir la clase completa, el paquete, el algoritmo de digest, el archivo exacto que se mide, el cuerpo de `isSunJCEVerified()`, `getOriginalPersistentRoot()`, ni el comportamiento 13.52 de `PSDescriptorFactory`, `BdjPolicyImpl`, `CodeSource` o los classloaders.

## 1. Evidencia pública comprobada

| Fuente | Observación | Clasificación |
|---|---|---|
| PSDevWiki, sección raw 51 | Declara que el hash SUNJCE de `RootCertManager.java` cambió en PS4 13.52; atribuye la comparación a zecoxao; afirma “Patched: Yes since PS4 FW 13.52” y “Not patched as of PS4 FW 13.50” | `INDIRECT_13.52` / `DOCUMENTED_ONLY` |
| Publicación de Jose Coixao, 16-jun-2026 | Texto: “bdjb patched on 13.52. this code got removed” y, en publicación relacionada, “this also got changed (in RootCertManager.java)” | `DOCUMENTED_ONLY` |
| Captura pública HK9CpsiXYAAmMbv | Dos paneles de código; ambos muestran el bloque estático y cadenas `sunjce_hash` distintas | `DIRECT_PUBLIC_SCREENSHOT`; procedencia retail exacta `UNVERIFIED` |
| Respuesta pública de @ps3120, 25-jun-2026 | Afirma: “And added RSACipherAdaptor in sunjce_provider.jar 13.52” | `DOCUMENTED_ONLY`; sin corroboración independiente |
| PUP metadata local | Identifica el PUP 13.52 y sus hashes exteriores | `DIRECT_13.52` para el contenedor; no demuestra el contenido Java |

La sección raw exacta de PSDevWiki es reproducible mediante:

```text
https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&action=raw&section=51
```

La publicación primaria y la imagen son:

```text
https://x.com/notnotzecoxao/status/2066944047944446366
https://pbs.twimg.com/media/HK9CpsiXYAAmMbv?format=webp&name=medium
```

La copia local de la captura es `webkit-kit/runtime/rootcertmanager_followup.webp`, con SHA-256:

```text
ab98050e2cf3a4e62497e986043387722672460a914fcd51270c74e94ed3d820
```

## 2. Hashes visibles en la captura

La captura se inspeccionó a resolución original de `1200 × 113` píxeles y mediante recortes ampliados. Las cadenas visualmente legibles son:

| Panel | Cadena visible | Estado |
|---|---|---|
| Izquierdo, presumiblemente versión anterior | `y8ehrm0lQ64cek7k6/+CwpSDLsjfnCesSX0agGpM10g=` | `DIRECT_PUBLIC_SCREENSHOT`; `UNVERIFIED_AS_SOURCE_BYTES` |
| Derecho, presumiblemente versión nueva | `At2dtIBsAdpxI/GWtq2otASAkU5OVg3QG5fFUF+KBek=` | `DIRECT_PUBLIC_SCREENSHOT`; `UNVERIFIED_AS_SOURCE_BYTES` |

La asignación izquierda = versión anterior y derecha = versión nueva es una **inferencia de comparación visual**, apoyada por la afirmación pública de que se compararon 13.50 y 13.52. La imagen no contiene una etiqueta explícita “13.50” y “13.52” junto a cada panel. Por ello no se debe presentar la tabla como dos hashes recuperados de JARs retail.

El archivo auxiliar `webkit-kit/runtime/ROOTCERT_PUBLIC_EVIDENCE_SESSION20.txt` conserva el texto de las fuentes, las URLs, la clasificación y los límites de transcripción.

## 3. Pseudodiff verificable y límites

La parte que sí aparece en la captura es estructuralmente equivalente a:

```java
static {
    AccessController.doPrivileged(new 1());
    sunjce_hash = "<cadena base64-like>";
}
```

El pseudodiff mínimo es, por tanto, un cambio de **valor constante** dentro de un bloque que llama a `AccessController.doPrivileged`. La captura no permite demostrar que se modificara el control de acceso, que se añadiera una validación nueva o que se eliminara una rama de código.

No es reproducible como diff de fuente porque no se dispone de:

| Elemento no disponible | Consecuencia |
|---|---|
| Archivo completo `RootCertManager.java` | No se conoce paquete, campos, métodos ni imports completos |
| `rt.jar`/`bdjstack.jar` 13.50 y 13.52 | No se puede calcular ni verificar SHA-256 del JAR |
| Bytes de `sunjce_provider.jar` | No se puede comprobar qué archivo se hashea ni su contenido |
| Algoritmo de digest y normalización | No se puede reproducir la comparación a partir de los valores visibles |
| Etiquetas de versión en los paneles | La correspondencia izquierda/derecha con 13.50/13.52 es inferida |
| Diff textual o commit Sony | No se puede identificar línea añadida/eliminada más allá de la constante visible |

## 4. Relación con el parche BD-JB

PSDevWiki describe una ruta histórica en `BdjPolicyImpl` donde, si el `CodeSource` es un `file:` URL cuyo path coincide con `$JAVA_HOME/lib/ext/sunjce_provider.jar`, y `RootCertManager.isSunJCEVerified()` devuelve verdadero, se construye un objeto `Permissions`, se añade `AllPermission` y se retorna esa política.[1]

La captura pública separada de `BdjPolicyImpl` muestra visualmente estas operaciones:

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

Este bloque es evidencia histórica/publicada de la relación **CodeSource → path SUNJCE → `isSunJCEVerified()` → `AllPermission`**. No demuestra que el mismo cuerpo siga en 13.52. Tampoco demuestra por sí mismo un bypass: la vulnerabilidad descrita por PSDevWiki está expresamente marcada como no probada.[1]

La afirmación pública de que cambiar `sunjce_hash` “probablemente deshabilita la inyección de JARs firmados antiguos” es una explicación editorial plausible, no una prueba de la condición exacta de aceptación ni del flujo de carga real en 13.52.[1]

## 5. ¿Cambió `getOriginalPersistentRoot()`?

No se encontró evidencia pública verificable de que `getOriginalPersistentRoot()` haya cambiado en la misma modificación.

La referencia histórica de HackerOne #1379975 muestra que `UserPreferenceManagerImpl` usaba:

```java
new FileInputStream(
    RootCertManager.getOriginalPersistentRoot() + "/userprefs"
)
```

y que la lectura se hacía mediante `ObjectInputStream.readObject()` dentro de `AccessController.doPrivileged`.[3] Esta es evidencia histórica del consumidor del método, no evidencia de su implementación 13.52.

El material disponible no demuestra ninguno de los siguientes puntos:

| Pregunta | Estado |
|---|---|
| ¿Cambió la firma de `getOriginalPersistentRoot()`? | `UNVERIFIED` |
| ¿Cambió la ruta devuelta? | `UNVERIFIED` |
| ¿Cambió su canonicalización o encoding? | `UNVERIFIED` |
| ¿Cambió la relación con `PSDescriptorFactory`? | `UNVERIFIED` |
| ¿Se eliminó la ruta `userprefs`? | `UNVERIFIED` |

## 6. ¿Afecta carga de clases, `CodeSource`, permisos o policy?

La evidencia disponible permite separar tres niveles:

| Nivel | Conclusión | Clasificación |
|---|---|---|
| Constante de confianza | El valor de `sunjce_hash` cambió en la comparación pública | `STRONG_INDIRECT` / captura pública directa |
| Validación | Es razonable inferir que `isSunJCEVerified()` compara o usa ese valor, por su nombre y por el código publicado | `INFERRED` |
| Política | Existe una ruta histórica publicada donde un `CodeSource` concreto puede devolver `AllPermission` si la verificación es verdadera | `HISTORICAL_ONLY` |
| Carga de clases | No hay prueba de cómo 13.52 construye o valida el `CodeSource` antes de invocar la policy | `UNVERIFIED` |
| Permisos 13.52 | No hay prueba de que 13.52 conceda `AllPermission` a ningún JAR | `UNVERIFIED` |
| `getOriginalPersistentRoot()` | No hay diff ni cuerpo 13.52 | `UNVERIFIED` |

Por tanto, el cambio de hash puede cerrar la aceptación de un JAR firmado antiguo, pero no se puede afirmar si lo hace cambiando sólo la cadena de confianza, sustituyendo el archivo esperado, modificando el consumidor o alterando el classloader.

## 7. `RSACipherAdaptor` y SUNJCE 13.52

La respuesta pública de @ps3120 afirma que `RSACipherAdaptor` fue añadido en `sunjce_provider.jar` 13.52. La observación es relevante porque sugiere un cambio adicional en el proveedor criptográfico, pero no incluye código, hash del JAR, clase completa, firma del método ni una referencia independiente de filesystem.

Clasificación:

```text
DOCUMENTED_ONLY
```

No debe convertirse en `DIRECT_13.52` ni usarse para reconstruir una API exacta hasta disponer del JAR, bytecode, decompilación reproducible o una segunda fuente técnica independiente.

## 8. Referencias a métodos y consumidores

| Método/componente | Evidencia pública encontrada | Estado 13.52 |
|---|---|---|
| `RootCertManager.isSunJCEVerified()` | Referenciado por el bloque histórico de `BdjPolicyImpl` y por la captura pública | `UNVERIFIED` en 13.52 |
| `RootCertManager.getOriginalPersistentRoot()` | Referenciado por `UserPreferenceManagerImpl` en HackerOne #1379975 | `UNVERIFIED` en 13.52 |
| `BdjPolicyImpl` | Código histórico publicado en PSDevWiki/HackerOne | `HISTORICAL_ONLY` |
| `PSDescriptorFactory` | Informes históricos locales y PSDevWiki | `HISTORICAL_ONLY`; relación actual `UNVERIFIED` |
| `sunjce_hash` | Constante visible en captura pública | `STRONG_INDIRECT` para el cambio; hash fuente `UNVERIFIED` |
| `RSACipherAdaptor` | Comentario público de @ps3120 | `DOCUMENTED_ONLY` |

## 9. Clasificación final de afirmaciones

| Afirmación | Clasificación |
|---|---|
| PSDevWiki afirma que el hash cambió en 13.52 | `DIRECT_13.52` como afirmación documental, no como bytes |
| La captura muestra valores distintos de `sunjce_hash` | `DIRECT_PUBLIC_SCREENSHOT` |
| La cadena anterior y posterior pertenece exactamente a 13.50 y 13.52 | `INDIRECT_13.52` / asignación de paneles `INFERRED` |
| El hash anterior exacto es el valor del runtime 13.50 | `UNVERIFIED_AS_SOURCE_BYTES` |
| El hash nuevo exacto es el valor del runtime 13.52 | `UNVERIFIED_AS_SOURCE_BYTES` |
| El cambio bloquea JARs firmados antiguos | `INFERRED` según PSDevWiki; no probado en la fuente |
| El cambio modifica `getOriginalPersistentRoot()` | `UNVERIFIED` |
| El cambio modifica `PSDescriptorFactory` | `UNVERIFIED` |
| 13.52 concede `AllPermission` al JAR SUNJCE | `UNVERIFIED` |
| `RSACipherAdaptor` fue añadido en SUNJCE 13.52 | `DOCUMENTED_ONLY` |

## 10. Conclusión

### Qué se puede afirmar

Existe una diferencia pública concreta asociada a PS4 13.52: el valor de `sunjce_hash` mostrado en la comparación de `RootCertManager.java` cambió respecto al panel anterior. PSDevWiki afirma que el cambio corresponde al parche de la ruta SUNJCE en 13.52, mientras que 13.50 se marca como no parcheado.[1] La captura pública preserva suficiente estructura para observar que el cambio está dentro de un inicializador estático que llama a `AccessController.doPrivileged`.

### Qué no se puede afirmar

No se puede reconstruir una clase completa ni un diff textual 13.50→13.52. No se puede demostrar que cambiasen `getOriginalPersistentRoot()`, `BdjPolicyImpl`, `PSDescriptorFactory`, el classloader, la canonicalización de `CodeSource` o los permisos efectivos. Tampoco se puede confirmar que la vulnerabilidad descrita como “path traversal via sunjce JAR signature” haya sido probada, sólo que la fuente pública la describe y marca 13.52 como parcheado.

### Pieza mínima que falta

La pieza mínima para convertir la reconstrucción en una comparación técnica es una copia autorizada y versionada de **ambas implementaciones comparables** —preferentemente `RootCertManager.class`/`RootCertManager.java` y `sunjce_provider.jar` de 13.50 y 13.52— con rutas, tamaños, hashes y procedencia. Para resolver la parte de policy se necesita además `BdjPolicyImpl` de las mismas builds. Sin ello, el resultado correcto continúa siendo `STRONG_INDIRECT` para el cambio público de hash y `UNVERIFIED` para la semántica interna y la explotabilidad.

## Referencias

[1]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&action=raw&section=51 "PSDevWiki, sección raw de SUNJCE/RootCertManager"
[2]: https://x.com/notnotzecoxao/status/2066944047944446366 "Jose Coixao, publicación pública con captura de RootCertManager"
[3]: https://hackerone.com/reports/1379975 "HackerOne #1379975, bd-j exploit chain"
[4]: https://pbs.twimg.com/media/HK9CpsiXYAAmMbv?format=webp&name=medium "Captura pública enlazada en la publicación"
[5]: https://www.playstation.com/en-us/support/hardware/ps4/system-software-info/ "PlayStation, información de software del sistema PS4"
