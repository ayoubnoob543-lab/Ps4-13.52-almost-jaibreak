# Comparación ObjectStreamClass/ReflectionFactory y forks BD-J

## Alcance

Este informe compara estáticamente el commit OpenJDK `020204a972d9be8a3b2b9e75c2e8abea36d787e9` con el corpus público de BD-J disponible localmente. El objetivo es precisar el alcance de `ProtectionDomain[] domains`, `doIntersectionPrivilege`, la construcción serializable, los callbacks de deserialización, los proxies, `ReflectionFactory` y `ClassLoader/defineClass`.

No se buscaron PUPs, dumps privados ni runtime protegido de PS4 13.52. No se ejecutaron exploits, payloads, JAR, ELF/BIN ni código contra hardware.

Las categorías son `DIRECT_13.52`, `INDIRECT_13.52`, `HISTORICAL_ONLY`, `HYPOTHESIS` y `DISCARDED`.

## Resultado ejecutivo

El parche OpenJDK no es un filtro general de toda deserialización. Endurece un punto concreto: **la invocación del constructor serializable o externalizable**. `ObjectStreamClass` calcula `ProtectionDomain[] domains`; `ReflectionFactory.newInstanceForSerialization` recibe esos dominios y, cuando hay `SecurityManager` y dominios no vacíos, ejecuta `Constructor.newInstance()` bajo la intersección del contexto actual y un `AccessControlContext(domains)`.

El parche no demuestra que `readObject`, `readObjectNoData`, `readResolve`, callbacks de aplicación ni `ClassLoader.defineClass` se ejecuten automáticamente dentro de esa misma intersección. En el código OpenJDK son fases y métodos distintos.

Los forks BD-J públicos disponibles no contienen `ObjectStreamClass`, `ReflectionFactory` ni `ObjectInputStream` del runtime Sony. Muestran `URLClassLoader`, `Class.forName`, `loadClass`, `newInstance`, reflection interna y `AccessController` en código cliente, pero no la integración del parche OpenJDK. Por tanto, no hay evidencia `DIRECT_13.52`.

## 1. Qué cambia exactamente `ProtectionDomain[] domains`

El commit añade a `ObjectStreamClass` un campo:

```java
private ProtectionDomain[] domains;
```

El campo se calcula durante la inicialización del descriptor, se copia en la inicialización de clases proxy y non-proxy, y se utiliza cuando se construye el objeto mediante el constructor serializable.

La función nueva `getProtectionDomains(Constructor cons, Class cl)` sólo actúa cuando:

```text
cons != null
AND cl.getClassLoader() != null
AND System.getSecurityManager() != null
```

Recorre la jerarquía desde `cl` hasta `cons.getDeclaringClass()`. Recoge los `ProtectionDomain` de las clases intermedias en un conjunto. Si la jerarquía no alcanza la clase que declara el constructor, borra el conjunto y añade un dominio sin permisos creado por `noPermissionsDomain()`.

La consecuencia es que el constructor no hereda simplemente el contexto privilegiado desde el cual se inició la deserialización. Debe ejecutarse con la intersección del contexto actual y de los dominios que separan la clase concreta de su ancestro constructor.

| Invariante | Protección que intenta proporcionar |
|---|---|
| La clase concreta y el constructor pertenecen a una jerarquía coherente | Evitar aceptar un constructor fuera de la cadena esperada |
| Cada clase intermedia aporta su dominio | Evitar perder restricciones de un loader o subclase |
| Una jerarquía incoherente produce dominio sin permisos | Fail closed frente a una estructura imposible |
| La intersección usa el contexto actual además de los dominios | Evitar ampliar permisos respecto al caller |

## 2. Dónde se aplica `doIntersectionPrivilege`

El parche añade a `ReflectionFactory`:

```java
public final Object newInstanceForSerialization(
        Constructor<?> cons, ProtectionDomain[] domains)
```

Su flujo es:

```text
SecurityManager ausente OR domains null/vacío
    → cons.newInstance()

SecurityManager presente AND domains no vacíos
    → PrivilegedAction que llama cons.newInstance()
    → AccessController.getContext()
    → new AccessControlContext(domains)
    → JavaSecurityAccess.doIntersectionPrivilege(...)
```

El fallback directo está expresamente diseñado para la ausencia de `SecurityManager` o de dominios. Eso no equivale por sí solo a una vulnerabilidad: aún se necesita una fuente controlable de clase/constructor y una operación privilegiada posterior.

La misma lógica aparece reflejada en el cambio de `ObjectStreamClass.newInstance()`, que conserva las excepciones reflectivas mediante `UndeclaredThrowableException`.

Clasificación: **HISTORICAL_ONLY**.

## 3. ¿Cubre `readObject`, `readResolve`, proxies y `ReflectionFactory`?

### 3.1 Constructor serializable y externalizable

Sí, dentro del alcance del parche. `ReflectionFactory.newInstanceForSerialization` documenta que recibe un constructor obtenido por `newConstructorForSerialization` o `newConstructorForExternalization` y aplica la intersección al llamar `Constructor.newInstance()`.

Clasificación: **HISTORICAL_ONLY**.

### 3.2 `readObject`

No hay evidencia de que el método de clase `readObject(ObjectInputStream)` sea ejecutado por `doIntersectionPrivilege` como consecuencia automática del parche. `ObjectInputStream` conserva la lógica de invocar los métodos especiales de deserialización después de crear el objeto y restaurar su estado. La mitigación analizada se centra en el constructor, no en toda llamada posterior de método de aplicación.

Si un `readObject` obtiene un contexto privilegiado por otra ruta, el commit no demuestra que esa ruta quede neutralizada. La implementación concreta de BD-J podría añadir controles propios, pero no está disponible.

Clasificación: **HISTORICAL_ONLY** para el alcance negativo del parche; estado 13.52 **UNVERIFIED**.

### 3.3 `readResolve`

`readResolve` es una fase distinta de la construcción. El descriptor almacena `readResolveMethod`, pero el parche no muestra que ese método sea llamado dentro de `ReflectionFactory.newInstanceForSerialization`. Por ello, una hipótesis de callback posterior con diferente contexto no queda resuelta por este commit.

Eso es una posibilidad de comparación, no una vulnerabilidad demostrada.

Clasificación: **HYPOTHESIS**.

### 3.4 Proxies

El parche copia `domains` durante la inicialización de descriptores proxy y non-proxy. Esto indica que el autor consideró explícitamente la propagación a proxies. Sin embargo, la eficacia completa depende de que todas las rutas de proxy usen el mismo descriptor y terminen en la construcción intersecada.

Una implementación BD-J divergente podría omitir esa copia, crear el proxy por otra API o ejecutar callbacks del proxy fuera de la ruta protegida. No hay evidencia de que ocurra en 13.52.

Clasificación: propagación en OpenJDK **HISTORICAL_ONLY**; variante BD-J **HYPOTHESIS**.

### 3.5 `ReflectionFactory`

Sí, el commit modifica directamente `sun.reflect.ReflectionFactory` mediante `newInstanceForSerialization(cons, domains)`. Esto significa que la mitigación no es sólo una comprobación en `ObjectStreamClass`; existe un punto centralizado para la invocación del constructor serializable.

No obstante, no todas las operaciones de `ReflectionFactory` son necesariamente construcciones serializables. Un uso alternativo de reflection, `Method.invoke`, `defineClass` o un loader propio no queda automáticamente cubierto.

Clasificación: integración en OpenJDK **HISTORICAL_ONLY**; integración en BD-J 13.52 **UNVERIFIED**.

## 4. `ClassLoader` y `defineClass`

La mitigación no asigna un `ProtectionDomain` nuevo a todas las clases definidas por un loader. Los dominios que calcula se obtienen de clases ya cargadas mediante `Class.getProtectionDomain()`. Por tanto, el parche usa dominios existentes para limitar la construcción del objeto; no demuestra por sí mismo cómo un `ClassLoader.defineClass` posterior asigna su dominio.

La asignación de dominio en `defineClass` depende del overload usado, del loader, del `CodeSource` y de las reglas de la JVM/port. Si un loader alternativo puede definir una clase con un dominio privilegiado o si usa otra API interna, esa operación está fuera del método añadido salvo que el propio loader aplique controles equivalentes.

El cliente histórico `bd-jb` demuestra únicamente que un proyecto público intentaba usar `URLClassLoader`, `Class.forName`, `loadClass` y reflection interna. En concreto:

| Archivo | Líneas | Evidencia |
|---|---:|---|
| `bd-jb-src/src/com/bdjb/api/API.java` | 92–124 | Selección de `Unsafe`, `ClassLoader$NativeLibrary`, `find/findEntry`, `setAccessible` y constructor interno |
| `bd-jb-src/src/com/bdjb/exploit/sandbox/ExploitServiceProxyImpl.java` | 31–60 | `Class.forName`, `URLClassLoader`, `loadClass`, `newInstance` |
| `bd-jb-src/src/com/bdjb/Loader.java` | 74–76 | `DVBClassLoader.newInstance` y `loadClass` |
| `bdjplus-src/src/com/sony/bdjstack/system/BDJModule.java` | 264–307, 351, 400, 649–653 | `URLClassLoader`, `Class.forName`, `loadClass` y `newInstance` |

Ninguno de esos archivos define `ProtectionDomain`, `ObjectStreamClass` o `ReflectionFactory`. Son clientes/forks, no pruebas del runtime BD-J 13.52.

Clasificación: existencia de loaders en clientes **HISTORICAL_ONLY**; integración con `defineClass` en 13.52 **UNVERIFIED**.

## 5. Comparación con forks BD-J públicos

| Corpus | `ObjectStreamClass` propio | `ReflectionFactory` propia | `ObjectInputStream` propio | `ProtectionDomain[] domains` | Resultado |
|---|---:|---:|---:|---:|---|
| `TheOfficialFloW/bd-jb` | No | No | No | No | Cliente histórico; no integra el parche |
| BDJPlus | No en el corpus revisado | No | No | No | Loader/módulos Java; no integra el parche |
| BDJ-SDK público | Stubs/API, no runtime Sony | No | No | No | Interfaces de compilación; no prueba ejecución |
| `webkit-ps4-1352-kit` | No runtime | No runtime | No runtime | No | Informes y referencias; sin integración 13.52 |

El resultado correcto es **ninguna integración verificable** en los forks públicos disponibles. La ausencia de una clase en el cliente no prueba que el runtime no la tenga; simplemente muestra que la clase pertenece a la JVM/bootclasspath y no está versionada por esos proyectos.

Clasificación: **HISTORICAL_ONLY**.

## 6. Variantes residuales técnicamente plausibles

| Variante | Condición necesaria | Primer punto de ruptura | Clasificación |
|---|---|---|---|
| `readObject` fuera de la intersección | La clase ejecuta un callback de deserialización con contexto más privilegiado que el constructor | Si el runtime interseca también el callback o no hay fuente privilegiada | **HYPOTHESIS** |
| `readResolve` posterior privilegiado | `readResolve` recibe/recupera un contexto que no pasa por `ReflectionFactory.newInstanceForSerialization` | Si el callback se ejecuta con el contexto restringido o no es controlable | **HYPOTHESIS** |
| Proxy con propagación incompleta | Una ruta proxy no copia `domains` o no usa el descriptor endurecido | Si todas las rutas proxy conservan `domains` y usan la construcción intersecada | **HYPOTHESIS** |
| `ReflectionFactory` alternativo | BD-J expone una construcción que no usa `newInstanceForSerialization` | Si todos los constructores serializables pasan por la API nueva | **HYPOTHESIS** |
| Loader/`defineClass` alternativo | Una clase obtenida por reflexión obtiene `defineClass` con un dominio no restringido | Si el loader asigna un dominio limitado y no expone el método | **HYPOTHESIS** |
| `SecurityManager` ausente | La implementación toma el fallback directo de `cons.newInstance()` | No basta sin clase/constructor y operación posterior controlables | **HYPOTHESIS** |

Todas estas variantes se refieren a rutas técnicamente posibles en una comparación de implementaciones. Ninguna es `DIRECT_13.52` ni `INDIRECT_13.52`.

## 7. Primer punto no verificado y evidencia mínima

El primer punto no verificado es si el runtime BD-J de PS4 13.52 integra el cambio de OpenJDK en `ObjectStreamClass` y `ReflectionFactory`.

Para resolverlo se necesita una fuente pública verificable de 13.52 que muestre, como mínimo:

| Componente | Evidencia mínima |
|---|---|
| `ObjectStreamClass` | Campo `domains`, cálculo de dominios, propagación a proxy/non-proxy y uso en `newInstance` |
| `ReflectionFactory` | Presencia/ausencia de `newInstanceForSerialization` y su fallback/intersección |
| `ObjectInputStream` | Flujo de `readObject`, `readObjectNoData`, restauración y `readResolve` |
| `ClassLoader` | Overload de `defineClass`, `CodeSource`, loader y `ProtectionDomain` asignado |
| BD-J userprefs | Integración de `UserPreferenceManagerImpl`, filtros y callback posterior |

La evidencia pública del cliente `bd-jb` no satisface estos requisitos. La similitud de nombres no se eleva a evidencia de 13.52.

## Conclusión

El parche OpenJDK endurece de forma real y precisa la construcción serializable: conserva `ProtectionDomain[] domains`, calcula dominios de la jerarquía de clases y utiliza `doIntersectionPrivilege` tanto en `ObjectStreamClass` como en `ReflectionFactory.newInstanceForSerialization`.

El parche cubre directamente la invocación del constructor serializable/externalizable. No demuestra cobertura automática de `readObject`, `readResolve`, callbacks de aplicación, loaders alternativos o `ClassLoader.defineClass`. Los forks BD-J públicos revisados no integran las clases de la JVM ni muestran `domains`; sólo contienen loaders y clientes de reflection.

Resultado para PS4 13.52:

> **No hay evidencia DIRECT_13.52 ni INDIRECT_13.52. La integración de la mitigación, su eventual ausencia o una variante residual permanecen UNVERIFIED/HYPOTHESIS.**

## Referencias

[1]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 "OpenJDK 8180024: Improve construction of objects during deserialization"

[2]: https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/io/ObjectInputStream.java "OpenJDK ObjectInputStream"

[3]: https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/io/ObjectStreamClass.java "OpenJDK ObjectStreamClass"

[4]: https://github.com/TheOfficialFloW/bd-jb "TheOfficialFloW bd-jb public client"

[5]: https://github.com/john-tornblom/bdj-sdk "Public BDJ SDK"

[6]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9.patch "OpenJDK 020204a patch"
