# BD-J: análisis profundo de Ixc/stubs, Java deserialización y policy/loader

**Autor:** Manus AI  
**Alcance:** análisis estático de fuentes públicas. No se ejecutaron exploits, payloads, JAR/ELF/BIN ni código contra hardware. El nested-JAR 13.00–13.02 se trata sólo como caso excluido, no como variante nueva.

## Resumen ejecutivo

La evidencia pública permite reconstruir con bastante precisión dos puntos históricos: la mitigación Ixc basada en call-stack era incompleta frente a proxies generados y callbacks de método; y la cadena de deserialización dependía de construir objetos bajo privilegios mediante `ObjectStreamClass`/`ReflectionFactory`. El commit OpenJDK `020204a...` introdujo dominios de protección e intersección de privilegios para cerrar precisamente esa elevación durante la construcción del objeto.

No existe evidencia pública específica de PS4 13.52 que demuestre la presencia o ausencia de esas clases, la integración del commit OpenJDK, los filtros actuales de `CodeSource`/policy o el comportamiento de `BdjPolicyImpl`/`XletClassLoader`. Por ello, ninguna hipótesis se clasifica como `DIRECT_13.52`.

Las tres hipótesis técnicamente más fuertes son:

1. **Ixc callback/cache residual:** la validación de `IxcProxy` inspecciona el stack, pero la selección efectiva del `Method` se delega a `findMethod` y se cachea en el stub; una divergencia entre la identidad del método solicitado y el método devuelto podría conservar una invocación privilegiada. `HISTORICAL_ONLY / HYPOTHESIS`.
2. **Deserialización con dominios incompletos:** si una implementación Sony anterior o adaptada calcula incorrectamente los `ProtectionDomain` de una subclase serializable frente al constructor de su ancestro no serializable, `ReflectionFactory` podría conservar privilegios indebidos. El commit OpenJDK demuestra la clase de mitigación, no su integración en OrbisOS. `HISTORICAL_ONLY / HYPOTHESIS`.
3. **Desacuerdo policy/loader por representación de `CodeSource`:** si `BdjPolicyImpl` autoriza una representación de URL/ruta y `XletClassLoader` carga otra tras normalización distinta, podría existir una frontera de autorización inconsistente. No hay código público suficiente para afirmar que esa discrepancia exista en 13.52. `HYPOTHESIS`.

## 1. Ixc/stubs

### Contrato histórico

HackerOne #3104356 documenta dos implementaciones: `org.dvb.io.ixc` y `com.sun.xlet.ixc`. En la primera, `com.sony.gemstack.org.dvb.io.ixc.IxcProxy.invokeMethod` obtiene el stack mediante `AccessController.doPrivileged` y busca una entrada cuyo nombre sea `com.sony.gemstack.org.dvb.io.ixc.IxcProxy`. La mitigación permite el siguiente frame si pertenece a `org.dvb.io.ixc.*` o `com.sony.gemstack.org.dvb.io.ixc.*`.

El mismo informe afirma que esa condición no cubre todos los proxies generados por `IxcProxyBuilder`. Históricamente, la elegibilidad requiere una interfaz que extienda `java.rmi.Remote` y métodos que declaren `java.rmi.RemoteException`. Un objeto bootstrap elegible puede así atravesar la comprobación del método privilegiado, aunque los métodos internos realicen `SecurityManager.checkPermission`.

En la segunda implementación, `IxcClassLoader` genera una clase stub que hereda de `WrappedRemote`. El stub conserva métodos estáticos `com_sun_xlet_methodN`; `com_sun_xlet_init(Method findMethodMethod)` llama reflectivamente a un callback para resolver y cachear `Method`; `com_sun_xlet_destroy()` limpia la caché. Los métodos públicos del stub delegan en `WrappedRemote.com_sun_xlet_execute`, que invoca el método cacheado dentro de `AccessController.doPrivileged`.

### Variante histórica no cubierta

La primera variante que merece atención no es el prefijo del stack por sí solo, sino la **desalineación entre la identidad solicitada y la identidad devuelta por `findMethod`**. El contrato visible del stub pasa un nombre de interfaz, un nombre de método y tipos; el callback devuelve un `Method`. El material público demuestra que la resolución es reflectiva y que el valor devuelto se cachea, pero no publica una validación posterior que compare `Method.getDeclaringClass()`, nombre, firma, modificadores, loader u origen frente a la solicitud.

| Aspecto | Evidencia |
|---|---|
| Precondición | Stub generado, callback `findMethod` alcanzable y método cacheable. |
| Validación que debería impedirlo | Comparar nombre, firma, clase declarada, loader, `public`/`static`, origen y permisos antes de cachear. |
| Evidencia histórica | HackerOne #3104356 muestra `findMethod` y `doPrivileged`; no muestra todas esas comparaciones. |
| Rango conocido | Cadena histórica probada por el informe; el propio reporte de 2025 no aporta PS4 13.52. |
| Por qué podría sobrevivir | El control principal está en el proxy/call-stack, mientras la selección final se produce en el stub/cache. Una mitigación en una capa no implica validación en la otra. |
| Evidencia 13.52 | Ninguna. |
| Dato faltante | Código/decompilación de `IxcProxyBuilder`, `IxcClassLoader`, `WrappedRemote` y callback de 13.52. |
| Clasificación | `HISTORICAL_ONLY / HYPOTHESIS`. |

Esta hipótesis no afirma que el callback sea arbitrario en 13.52 ni describe una forma operativa de abusarlo; identifica una condición de consistencia que el código retail tendría que demostrar o refutar.

### Mitigación de #3104356 y límite

La mitigación observada en `IxcProxy` comprueba una propiedad del call-stack, no la legitimidad semántica del `Method` finalmente invocado. El informe público muestra además que `WrappedRemote` usa `doPrivileged` al invocar el método. Por tanto, históricamente quedan dos fronteras separadas: autorización del proxy y resolución/cache del método.

**Clasificación 13.52:** `UNVERIFIED`; no hay bytes ni diff de esa build.

## 2. Java: `ObjectStreamClass`, `ReflectionFactory` y `AccessController`

### Cambio exacto de OpenJDK

El commit `020204a972d9be8a3b2b9e75c2e8abea36d787e9` (“8180024: Improve construction of objects during deserialization”) modifica `java.io.ObjectStreamClass` y clases relacionadas. Añade un campo `ProtectionDomain[] domains`, calcula los dominios que separan la clase concreta serializable de la clase que declara el constructor de inicialización y crea un dominio sin permisos si la jerarquía es anómala.

Antes del cambio, `ObjectStreamClass.newInstance()` podía terminar en `cons.newInstance()` directamente. Después, cuando existen dominios, el constructor se ejecuta con `JavaSecurityAccess.doIntersectionPrivilege`, combinando el contexto actual con un `AccessControlContext` creado a partir de esos dominios. El commit no elimina `readObject` ni `readResolve`; modifica el contexto de privilegios con el que se construye el objeto.

### Rutas relevantes

`ObjectInputStream.readObject()` obtiene el descriptor y sigue las rutas de deserialización; `ObjectStreamClass` identifica métodos de la clase como `readObject`, `readObjectNoData`, `writeReplace` y `readResolve`, y determina el constructor de serialización. `ReflectionFactory` crea el constructor especial para una clase serializable y, en implementaciones históricas, puede suprimir comprobaciones de acceso y generar bytecode de construcción.

La documentación actual de OpenJDK advierte que `ReflectionFactory` puede leer/escribir datos privados, invocar métodos privados y cargar bytecode no verificado, por lo que el objeto factory debe estar cuidadosamente protegido. JDK-8315810 documenta una reimplementación posterior con method handles en JDK 22 para retirar el hack de verificación de VM. Esto es evidencia del diseño OpenJDK, no de Sony.

### Variante de dominios incompletos

La hipótesis relevante es una **implementación parcial o anterior del cálculo de dominios**. Si sólo se valida el dominio de la clase concreta, pero no todos los ancestros entre ella y el constructor no serializable, el constructor podría ejecutarse con un conjunto de permisos más amplio que el previsto. El commit OpenJDK muestra exactamente por qué se necesita recorrer la jerarquía y aplicar la intersección.

| Aspecto | Evidencia |
|---|---|
| Precondición | Entrada controlada a `ObjectInputStream.readObject()` y clase serializable con jerarquía relevante. |
| Validación que debería impedirlo | Calcular todos los `ProtectionDomain` intermedios y aplicar intersección antes de `cons.newInstance()`. |
| Evidencia histórica | Commit OpenJDK añade `domains`, `getProtectionDomains`, dominio vacío y `doIntersectionPrivilege`. |
| Rango conocido | OpenJDK; no se identifica versión OrbisOS/Sony. |
| Por qué podría sobrevivir | Sony podría usar una rama Java antigua, una implementación adaptada o haber aplicado sólo parte del cambio. |
| Evidencia 13.52 | Ninguna. |
| Dato faltante | Clase `ObjectStreamClass`/`ReflectionFactory` de 13.52, número de build o diff Sony. |
| Clasificación | `HISTORICAL_ONLY / HYPOTHESIS`. |

No se debe asumir que `readResolve` o `ReflectionFactory` son vulnerables por su mera existencia. La condición depende del contexto, los filtros, el constructor elegido y los dominios reales.

## 3. Policy/loader: `BdjPolicyImpl`, `XletClassLoader`, `BDJFactory`, `JarZipFile`, `CodeSource`

### Discrepancia de representación

Una frontera independiente potencial es que policy y loader no comparen la misma representación de origen. `BdjPolicyImpl` puede razonar sobre `CodeSource`/URL y permisos; `XletClassLoader` puede resolver una URL, una ruta local o una entrada JAR; `BDJFactory` puede elegir el descriptor y `JarZipFile` puede convertir el nombre de entrada en un recurso. Si una capa normaliza `%2e`, separadores, symlinks, `file:` o componentes `..` de forma distinta, policy y loader podrían referirse a objetos diferentes.

El nested-JAR 13.00–13.02 queda excluido. La hipótesis aquí sólo sería válida si se demuestra una discrepancia de representación que no dependa de la inserción `.jar` ya documentada.

| Aspecto | Evidencia |
|---|---|
| Precondición | Un recurso con dos representaciones aceptadas por policy y loader. |
| Validación que debería impedirlo | Canonicalizar una única vez, comparar el mismo `CodeSource` y aplicar la política después de resolver el recurso final. |
| Evidencia histórica | Las fuentes públicas identifican `BdjPolicyImpl`, `XletClassLoader`, `BDJFactory` y `JarZipFile` en cadenas BD-J, pero los detalles disponibles están dominados por traversal/nested-JAR. |
| Rango conocido | Históricos; no rango 13.52 verificable. |
| Por qué podría sobrevivir | Un parche puede bloquear una forma concreta de traversal sin unificar todas las representaciones URL/ruta/JAR. |
| Evidencia 13.52 | Ninguna. |
| Dato faltante | Código de los cinco componentes en una build posterior, con entradas y salidas de normalización. |
| Clasificación | `HYPOTHESIS`; cualquier variante nested-JAR es `DISCARDED`. |

### `CodeSource` y permisos

La presencia de un `CodeSource` no implica `AllPermission`. La política debe asociar el origen a un `ProtectionDomain`, y el loader debe definir la clase con ese origen. Un bug necesitaría demostrar que la clase se define con un origen más confiable que el recurso realmente leído o que la policy consulta una URL distinta. No existe esa demostración pública para 13.52.

## Matriz de clasificación

| Superficie | Evidencia histórica | Mitigación conocida | Evidencia específica 13.52 | Clasificación |
|---|---|---|---|---|
| Ixc call-stack check | #3104356 muestra búsqueda de `IxcProxy` y prefijos permitidos. | Restricción de frames; insuficiente ante proxy generado según el reporte. | Ninguna. | `HISTORICAL_ONLY` |
| Stub `findMethod`/cache | #3104356 muestra callback, cache y `WrappedRemote.doPrivileged`. | No se documenta comparación completa de método/origen. | Ninguna. | `HISTORICAL_ONLY / HYPOTHESIS` |
| `ObjectStreamClass` domains | OpenJDK 8180024 añade recorrido de dominios e intersección. | `doIntersectionPrivilege`, dominio sin permisos y posterior evolución de ReflectionFactory. | Ninguna integración Sony. | `HISTORICAL_ONLY / HYPOTHESIS` |
| `ReflectionFactory` | OpenJDK la considera altamente privilegiada; JDK 22 cambia constructor de serialización. | Protección del factory y method handles posteriores. | Ninguna. | `HISTORICAL_ONLY` |
| Policy/loader representation | Riesgo estructural de URLs/rutas/CodeSource distintos. | No hay parche público independiente del nested-JAR. | Ninguna. | `HYPOTHESIS` |
| Nested-JAR | CVE/PSDevWiki 13.00–13.02. | Ya documentada y excluida. | No es variante nueva. | `DISCARDED` |

## Conclusión y siguiente comprobación segura

La hipótesis Ixc de mayor fuerza es la falta de validación semántica entre la solicitud de `findMethod` y el `Method` cacheado, porque la fuente pública demuestra ambos lados del límite: el callback recibe descriptores simbólicos y devuelve un `Method`, mientras la ejecución posterior ocurre en `doPrivileged`. Esto sigue siendo histórico; no hay evidencia 13.52.

La hipótesis Java de mayor fuerza es una implementación incompleta del cálculo de `ProtectionDomain` en la rama Java usada por OrbisOS. El commit OpenJDK proporciona un criterio claro de comparación: recorrido completo de ancestros, dominio sin permisos para jerarquías anómalas e intersección antes de construir. Sin el código Sony no se puede afirmar integración ni ausencia.

La hipótesis policy/loader es la más débil pero independiente: una divergencia de representación de `CodeSource` entre policy y loader. Debe mantenerse separada del nested-JAR y no merece exploración adicional hasta disponer de código público concreto que muestre dos normalizadores distintos.

La siguiente comprobación segura de mayor valor es documental: localizar una revisión pública de las clases Ixc o Java de Sony que revele si el método cacheado se valida contra su solicitud y si `ObjectStreamClass` contiene `domains`/`doIntersectionPrivilege`. No se debe convertir ninguna de estas hipótesis en un harness o exploit sin esa evidencia.

## Referencias

[1]: https://hackerone.com/reports/3104356 — HackerOne #3104356, “Blu-ray Disc Java Sandbox Escape via two vulnerabilities”.

[2]: https://hackerone.com/reports/1379975 — HackerOne #1379975, “bd-j exploit chain”.

[3]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 — OpenJDK 8180024, “Improve construction of objects during deserialization”.

[4]: https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/jdk/internal/reflect/ReflectionFactory.java — OpenJDK `ReflectionFactory` actual.

[5]: https://bugs.openjdk.org/browse/JDK-8315810 — JDK-8315810, reimplementación de `ReflectionFactory` con method handles.

[6]: https://www.psdevwiki.com/ps4/Vulnerabilities — PS4 Developer Wiki, índice y análisis histórico de vulnerabilidades BD-J.

[7]: https://cve.org/CVERecord?id=CVE-2025-64390 — CVE-2025-64390, nested-JAR; citado sólo para delimitar la superficie excluida.
