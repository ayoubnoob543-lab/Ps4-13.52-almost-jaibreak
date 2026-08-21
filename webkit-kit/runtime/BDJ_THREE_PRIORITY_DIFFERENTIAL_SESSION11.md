# Diferencial independiente de tres mitigaciones BD-J/OpenJDK

## Alcance

Este informe cubre exclusivamente: (1) el diferencial `ObjectStreamClass`/`ReflectionFactory`/`AccessController`/`ClassLoader`; (2) las invariantes históricas de Ixc y stubs generados; y (3) la coherencia entre `BdjPolicyImpl`, `XletClassLoader`, `JarZipFile` y `BDJFactory`.

Se usan únicamente fuentes públicas y código histórico localmente conservado. No se descargan PUPs, dumps privados ni runtime de PS4 13.52; tampoco se ejecutan exploits, payloads, JAR, ELF/BIN o hardware.

Las categorías son `DIRECT_13.52`, `INDIRECT_13.52`, `HISTORICAL_ONLY`, `HYPOTHESIS` y `DISCARDED`.

## Conclusión ejecutiva

Ninguna de las tres líneas obtiene clasificación `DIRECT_13.52`. La evidencia más fuerte es histórica y permite establecer invariantes precisas, pero no su conservación posterior.

La línea con una mitigación pública más concreta es **deserialización/OpenJDK**: el commit `020204a972d9be8a3b2b9e75c2e8abea36d787e9` modifica `ObjectStreamClass` para calcular dominios de protección asociados al constructor y usar intersección de privilegios antes de construir objetos. El hueco relevante no es asumir que la corrección falla, sino comprobar si la implementación BD-J derivó completa, parcial o ninguna de esas modificaciones.

La línea Ixc muestra una mitigación explícitamente incompleta: el call stack y los prefijos de paquetes no equivalen a validar la identidad completa del proxy, su origen, el target y el `Method` final. Sin embargo, el informe que lo documenta no aporta una versión 13.52.

La línea policy/loader/JAR está históricamente acotada a PS4 13.00–13.02 por #3452696. Es útil como patrón de divergencia de representación, pero la variante nested-JAR no debe trasladarse a 13.52.

## 1. Diferencial OpenJDK/BD-J

### 1.1 Comportamiento histórico vulnerable

El reporte #1379975 describe una lectura de `userprefs` mediante `ObjectInputStream.readObject()` dentro de `AccessController.doPrivileged`. En firmwares antiguos sin el cambio OpenJDK indicado por el propio reporte, la construcción de una subclase de `ClassLoader` podía alcanzar `defineClass` con privilegios heredados y superar el sandbox.

La frontera relevante no era sólo `readObject()`. El problema residía en cómo la infraestructura de serialización elegía y llamaba al constructor de una clase serializable cuando la clase concreta y el constructor provenían de dominios de protección diferentes.

### 1.2 Qué hace el commit OpenJDK

El commit `020204a972d9be8a3b2b9e75c2e8abea36d787e9`, titulado `8180024: Improve construction of objects during deserialization`, modifica `ObjectStreamClass` y clases auxiliares. Añade, entre otros elementos:

| Elemento del cambio | Efecto de seguridad |
|---|---|
| `ProtectionDomain[] domains` | Conserva los dominios que separan la clase concreta de la clase que declara el constructor |
| `getProtectionDomains(cons, cl)` | Recorre la cadena de superclases y recoge dominios relevantes cuando hay `SecurityManager` |
| `noPermissionsDomain()` | Crea un dominio sin permisos si la relación esperada entre clase y constructor se rompe |
| `AccessControlContext(domains)` | Construye un contexto que representa la intersección de dominios |
| `JavaSecurityAccess.doIntersectionPrivilege` | Ejecuta la creación del objeto bajo la intersección del contexto actual y los dominios calculados |
| Cambios en `ObjectStreamClass.newInstance()` | Sustituye la llamada directa al constructor cuando existen dominios que deben comprobarse |

La mitigación protege la **construcción** del objeto. No demuestra por sí sola filtros completos de `readObject`, `readResolve`, proxies, `ReflectionFactory` o clases cargadas por mecanismos distintos.

### 1.3 `ReflectionFactory`, `ClassLoader` y `AccessController`

La cadena histórica depende de varias capas con responsabilidades diferentes:

| Capa | Papel | Qué tendría que demostrar una variante residual |
|---|---|---|
| `ObjectStreamClass` | Descubrir constructor y metadatos de serialización | Que la construcción aún se ejecute con un dominio incorrecto |
| `ReflectionFactory` | Suprimir o adaptar checks de construcción/reflection | Que el runtime BD-J conserve una ruta equivalente no cubierta por la intersección |
| `AccessController` | Ejecutar una acción privilegiada | Que el contexto privilegiado abarque el constructor o callback controlado |
| `ClassLoader`/`defineClass` | Definir bytecode en un loader | Que una clase controlable alcance `defineClass` con permisos suficientes |

La presencia de un nombre de clase histórico no basta. La variante sólo sería plausible si se demuestra la combinación de implementación, visibilidad, permisos y flujo de llamada.

### 1.4 Clasificación

| Hallazgo | Clasificación |
|---|---|
| El commit OpenJDK introduce dominios de protección en la construcción deserializada | **HISTORICAL_ONLY** |
| El cambio fue integrado exactamente en el runtime BD-J 13.52 | **UNVERIFIED; no DIRECT_13.52** |
| Una implementación BD-J parcial podría conservar rutas no cubiertas | **HYPOTHESIS** |
| Cualquier deserialización posterior sigue siendo vulnerable | **DISCARDED** como afirmación general |

El dato mínimo faltante es una comparación de las implementaciones efectivas de `ObjectStreamClass`, `ReflectionFactory` y `ClassLoader` del runtime objetivo, o un commit/fork BD-J público que demuestre qué parte del cambio se incorporó.

## 2. Invariantes Ixc y stubs generados

### 2.1 `IxcProxy` y primera mitigación

El reporte #3104356 describe dos implementaciones Ixc: `org.dvb.io.ixc` y `com.sun.xlet.ixc`. Para la primera, una mitigación histórica obtenía el call stack bajo `doPrivileged`, buscaba `com.sony.gemstack.org.dvb.io.ixc.IxcProxy` y exigía que la clase siguiente empezara por `org.dvb.io.ixc.` o `com.sony.gemstack.org.dvb.io.ixc.`.

La invariante real de esa defensa era, por tanto:

```text
existe IxcProxy en la pila
AND el siguiente frame tiene un prefijo permitido
```

No equivalía a comprobar de forma completa:

```text
proxy concreto autorizado
AND origen del proxy
AND loader del proxy
AND target remoto autorizado
AND método/Method esperado
AND argumentos y contexto coherentes
```

El mismo informe afirma que los proxies reales creados por `IxcProxyBuilder` seguían siendo aceptados. Eso es evidencia de una mitigación basada en patrones, no de una validación de identidad completa.

### 2.2 `WrappedRemote` y stubs

La segunda implementación expuesta en #3104356 contiene `com_sun_xlet_execute`, que invoca `remoteMethod.invoke(targetNow, args)` dentro de `AccessController.doPrivileged`. El stub generado por `IxcClassLoader` mantiene métodos estáticos del tipo `com_sun_xlet_method0`, inicializados por una función `findMethod` que recibe el nombre de clase, nombre de método y tipos.

Las invariantes históricas del stub son:

| Invariante | Estado histórico |
|---|---|
| El stub extiende `WrappedRemote` | Publicado |
| El método remoto se representa mediante un objeto `Method` estático | Publicado |
| `com_sun_xlet_init` obtiene el `Method` mediante `findMethod` | Publicado |
| `com_sun_xlet_execute` ejecuta bajo `doPrivileged` | Publicado |
| El target implementa una interfaz `Remote` y el método declara `RemoteException` | Publicado como condición Ixc |
| La identidad del `Method` se valida contra un catálogo fijo | No demostrado |
| El loader/origen del stub se valida criptográficamente | No demostrado |
| El target y los argumentos se validan antes de la invocación | No demostrado en el informe |

El checkout histórico local de `bd-jb` confirma el lado cliente: `IxcProxyImpl` hereda de `IxcProxy`, obtiene `CoreIxcClassLoader` desde `CoreAppContext`, almacena el objeto remoto y delega a `super.invokeMethod`. `ExploitServiceProxyImpl` usa ese proxy para invocar `Service.newInstance`; el cliente no implementa la mitigación y depende de que el runtime acepte la combinación.

### 2.3 ¿Valida identidad completa o sólo patrones?

La evidencia pública permite responder históricamente: la primera defensa descrita valida principalmente **patrones de call stack y prefijos**, mientras la segunda superficie deja que la selección de `Method` pase por `findMethod` y posteriormente por `doPrivileged`. No hay evidencia pública de una validación completa de identidad, origen, target y método en esa revisión.

Eso no demuestra una variante 13.52. Sólo define el punto exacto que una futura comparación deberá comprobar.

### 2.4 Clasificación

| Hallazgo | Clasificación |
|---|---|
| La mitigación del primer Ixc usaba call stack y prefijos | **HISTORICAL_ONLY** |
| `IxcProxyBuilder` dejaba pasar proxies reales según #3104356 | **HISTORICAL_ONLY** |
| `WrappedRemote` invocaba `Method` bajo `doPrivileged` | **HISTORICAL_ONLY** |
| El stub validaba identidad completa del `Method` | **DISCARDED** como afirmación: no está demostrado |
| Un loader/proxy alternativo podría satisfacer los patrones superficiales | **HYPOTHESIS** |
| Estas invariantes siguen en 13.52 | **UNVERIFIED** |

El dato mínimo faltante es una decompilación o diff público de `IxcProxy`, `IxcProxyBuilder`, `WrappedRemote`, `IxcClassLoader` y la utilidad `findMethod` en una revisión posterior, con atención a identidad de loader, target y método.

## 3. Coherencia policy/loader/JAR/ZIP

### 3.1 Bug histórico acotado

#3452696 atribuye a PS4 13.00–13.02 una divergencia entre:

1. `BdjPolicyImpl`, que aplicaba `File.getCanonicalPath()` a la URL de `CodeSource` y podía verla bajo `app0/bdjstack/lib/ext`; y
2. `JarZipFile`/`BDJFactory`, que transformaban la ruta `/dsm/` y trataban el segmento `..` como parte literal del nombre de entrada de un JAR anidado.

`XletClassLoader` registraba la URL y usaba el resultado del loader, mientras la policy decidía permisos sobre la ruta canonicalizada. La vulnerabilidad era una divergencia de representación: la policy y el loader no estaban evaluando el mismo objeto lógico.

### 3.2 Invariantes de coherencia

| Frontera | Representación histórica | Riesgo si diverge |
|---|---|---|
| URL → `CodeSource` | URL `file:` con path textual | Permiso calculado sobre una identidad distinta |
| `CodeSource` → policy | `getCanonicalPath()` | Resolución de `..`, separadores y symlinks |
| `BDJFactory.needProxy` | Prefijo/ruta `/dsm/` | Selección de backend diferente |
| `getAbsPath` | `/dsm/` → `/VP/BDMV/JAR/` | Cambio de namespace/path raíz |
| `JarZipFile` | Primer `.jar/` separa exterior y entrada | Entrada ZIP literal distinta de path canonicalizado |
| `XletClassLoader` | URL y `isSigned`/permisos | Firma y origen pueden no coincidir con bytes cargados |
| ZIP/JAR entry | Nombre textual dentro del JAR | `..`, encoding o separadores pueden tener semántica distinta |

### 3.3 Variantes distintas del nested-JAR

No se encontró evidencia pública de una variante posterior concreta. Como líneas estáticas de falsación, podrían compararse:

- canonicalización de separadores `/` y `\\`;
- percent-encoding antes y después de `URL.getFile()`;
- diferencia entre `URI.normalize()` y `File.getCanonicalPath()`;
- nombres ZIP codificados o duplicados;
- primer versus último separador `.jar/`;
- coincidencia entre `CodeSource`, `JarFile` exterior, `JarEntry` interior y certificados;
- rutas temporales o fallback cuando no existe una entrada literal.

Todas son **HYPOTHESIS**, no vulnerabilidades existentes. La variante nested-JAR original no debe tratarse como presente en 13.52 porque el reporte limita su alcance a 13.00–13.02.

### 3.4 Clasificación

| Hallazgo | Clasificación |
|---|---|
| Divergencia canonical path vs entrada literal en 13.00–13.02 | **HISTORICAL_ONLY** |
| Policy y loader histórico evaluaban representaciones distintas | **HISTORICAL_ONLY** |
| Una variante de encoding/separadores existe en 13.52 | **UNVERIFIED** |
| El nested-JAR documentado funciona en 13.52 | **DISCARDED** como extrapolación |
| Una futura variante requeriría que policy y loader vuelvan a divergir | **HYPOTHESIS** |

El dato mínimo faltante es código o decompilación posterior de `BdjPolicyImpl`, `XletClassLoader`, `BDJFactory` y `JarZipFile` con ejemplos de transformación de rutas y validación de certificados.

## Matriz final de prioridades

| Línea | Mejor resultado sin artefactos privados | Evidencia 13.52 | Primer punto bloqueado | Prioridad |
|---|---|---|---|---:|
| OpenJDK/BD-J | Comparar integración parcial/completa de dominios de protección y construcción por reflection | Ninguna directa | Implementación efectiva de `ObjectStreamClass`/`ReflectionFactory` | 1 |
| Ixc/stubs | Modelar identidad de proxy, loader, target, `Method` y contexto, frente a checks de call stack/prefijos | Ninguna directa | Implementación posterior de `IxcProxyBuilder`/`WrappedRemote` | 2 |
| Policy/loader/JAR | Buscar divergencias de representación sin repetir nested-JAR | Ninguna directa | Implementaciones posteriores y reglas de normalización | 3 |

## Conclusión

Las tres líneas sobreviven como **programas de análisis estático**, no como vulnerabilidades confirmadas. La evidencia histórica más accionable es:

1. OpenJDK sí introdujo una mitigación concreta de dominios de protección durante deserialización.
2. Ixc sí tuvo una mitigación basada en call stack/prefijos que el propio reporte consideró insuficiente frente a proxies reales y stubs generados.
3. La policy/loader sí sufrió una divergencia de representación en 13.00–13.02, pero esa vulnerabilidad concreta no debe extrapolarse a 13.52.

No se encontró evidencia `DIRECT_13.52`. La siguiente investigación útil debe localizar diffs públicos de forks BD-J posteriores, no buscar nombres aislados ni convertir interfaces históricas en afirmaciones de compatibilidad.

## Referencias

[1]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 "OpenJDK 8180024: Improve construction of objects during deserialization"

[2]: https://hackerone.com/reports/1379975 "PlayStation #1379975: bd-j exploit chain"

[3]: https://hackerone.com/reports/3104356 "PlayStation #3104356: Blu-ray Disc Java Sandbox Escape via two vulnerabilities"

[4]: https://hackerone.com/reports/3452696 "PlayStation #3452696: PS4 BD-J privilege escalation using nested JAR"

[5]: https://habr.com/ru/articles/671088/ "Public reproduction of the BD-J exploit chain"

[6]: https://www.psx-place.com/threads/update-2-thefl0w-discloses-blu-ray-disc-java-sandbox-escape-vulnerabilities-ps3-ps4-ps5.37554/ "Public reproduction and timeline of the BD-J disclosure"
