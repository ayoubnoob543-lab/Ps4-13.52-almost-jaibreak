# Evidencia actual del runtime Java/BD-J de PS4 13.52

## Alcance

Esta investigación busca únicamente evidencia actual y verificable del runtime Java/BD-J de PS4 13.52 o de cambios inmediatamente adyacentes. No repite el inventario histórico de superficies, no busca PUPs, dumps privados ni runtime protegido, y no ejecuta exploits, payloads, JAR, ELF/BIN ni código contra hardware.

## Conclusión ejecutiva

No se encontró una diferencia actual verificable en `ObjectStreamClass`, `ReflectionFactory`, `ObjectInputStream`, `AccessController`, `ProtectionDomain`, `ClassLoader`, `defineClass`, `readObject`, `readResolve` o `UserPreferenceManagerImpl` para PS4 13.52.

La única evidencia primaria actual localizada es la página oficial de características de software de PlayStation. Para la versión 13.52 sólo declara:

> “We’ve made some security fixes to the system software.” [1]

La misma página describe 13.50 como una actualización de mensajes/usabilidad, y 13.02/13.04 como correcciones de seguridad, pero no identifica componentes Java, BD-J ni cambios de clases o métodos. Por tanto, la nota oficial confirma que hubo correcciones de seguridad, pero no permite atribuir ninguna a la JVM o al runtime BD-J.

## Matriz de evidencia actual

| Componente o ruta | Evidencia actual encontrada | Estado |
|---|---|---|
| `ObjectStreamClass` | No hay fuente, decompilación ni metadata actual de 13.52. Sólo existe el parche OpenJDK y análisis histórico. | `UNVERIFIED` |
| `ReflectionFactory` | No hay implementación PS4 13.52. El commit OpenJDK histórico es un precedente, no evidencia Sony. | `UNVERIFIED` |
| `ObjectInputStream` | No hay código BD-J/JVM actual de 13.52 ni log que muestre su flujo. | `UNVERIFIED` |
| `AccessController` | Sólo hay usos históricos en clientes/forks y documentación pública. No se conoce la semántica actual de 13.52. | `HISTORICAL_ONLY` para precedentes; `UNVERIFIED` para 13.52 |
| `ProtectionDomain` | No hay evidencia de `domains[]`, `getProtectionDomains`, `noPermissionsDomain` o `doIntersectionPrivilege` en PS4 13.52. | `UNVERIFIED` |
| `ClassLoader` | Los forks públicos contienen `URLClassLoader` y `Class.forName`, pero no son el runtime de la consola. | `HISTORICAL_ONLY`; `UNVERIFIED` para 13.52 |
| `defineClass` | No hay evidencia actual de overload, `CodeSource` o dominio asignado por la JVM PS4 13.52. | `UNVERIFIED` |
| `readObject` | No hay evidencia actual de filtros, contexto de seguridad o callbacks en 13.52. | `UNVERIFIED` |
| `readResolve` | No hay evidencia actual de contexto, filtros o restricciones independientes. | `UNVERIFIED` |
| `UserPreferenceManagerImpl` | Sólo existe el precedente histórico documentado; no hay clase, firma o flujo actual de 13.52. | `HISTORICAL_ONLY`; `UNVERIFIED` para 13.52 |

## Evidencia oficial de versiones adyacentes

La página oficial enumera las siguientes descripciones:

| Versión | Nota oficial | Valor para esta investigación |
|---|---|---|
| 13.52 | Correcciones de seguridad del sistema | Confirma una corrección genérica; no identifica Java/BD-J |
| 13.50 | Mejoras de mensajes/usabilidad | No aporta un cambio de runtime |
| 13.04 | Correcciones de seguridad | No identifica componentes |
| 13.02 | Correcciones de seguridad | No identifica componentes |
| 13.00 | Mejoras de mensajes/usabilidad | No aporta un cambio de runtime |

La información oficial no proporciona un diff, CVE, changelog de clases, nombre de módulo, firma, método ni descripción de mitigación. En consecuencia, no es posible distinguir si una corrección de 13.52 afecta `ObjectStreamClass`, `ReflectionFactory`, `ObjectInputStream`, policy, classloading, otro componente o una superficie no relacionada.

Clasificación de una diferencia Java 13.50→13.52: **UNVERIFIED**.

## Comparación con el corpus público local

El corpus local permite separar claramente los clientes/forks de la JVM efectiva:

| Archivo local | Qué demuestra | Qué no demuestra |
|---|---|---|
| `evidence/bd-jb-src/src/com/bdjb/api/API.java:27-40,92-124` | Uso histórico de clases internas, `ClassLoader$NativeLibrary`, reflection y diferencias `find`/`findEntry` | No demuestra que esas clases existan o tengan la misma semántica en 13.52 |
| `evidence/bd-jb-src/src/com/bdjb/exploit/sandbox/ExploitServiceProxyImpl.java:31-60` | Uso histórico de Ixc, `URLClassLoader`, `Class.forName`, `loadClass` y `newInstance` | No es una implementación de `ObjectInputStream`, `ObjectStreamClass` o `ReflectionFactory` |
| `evidence/bdjplus-src/src/com/sony/bdjstack/system/BDJModule.java:264-307,351,400,649-653` | Loader Java público con `URLClassLoader`, `Class.forName` y `newInstance` | No contiene el bootclasspath Sony ni prueba runtime 13.52 |
| `webkit-kit/runtime/BDJ_OBJECTSTREAM_FORK_COMPARISON_SESSION14.md` | Comparación del parche OpenJDK y límites de los forks | No contiene bytes de la JVM de PS4 |
| `webkit-kit/runtime/BDJ_OBJECTSTREAM_PROTECTIONDOMAIN_ANALYSIS_SESSION13.md` | Precedente del alcance de `domains[]` y `doIntersectionPrivilege` | No demuestra integración actual |

El corpus no contiene una implementación pública actual de `ObjectStreamClass`, `ReflectionFactory`, `ObjectInputStream` o `ClassLoader` que pueda atribuirse a PS4 13.52.

## ¿Está integrada la mitigación de `ProtectionDomain`?

No puede determinarse. La ausencia de `domains[]` en los forks cliente no indica que la mitigación falte en la JVM de la consola; esos proyectos no versionan el bootclasspath. Del mismo modo, la nota oficial de “security fixes” no permite afirmar que la mitigación esté integrada.

Las tres posibilidades siguen abiertas:

| Posibilidad | Estado |
|---|---|
| Mitigación OpenJDK integrada sin cambios | `UNVERIFIED` |
| Mitigación integrada parcialmente o adaptada por Sony | `UNVERIFIED` |
| Mitigación ausente o sustituida por controles propios | `UNVERIFIED` |

## ¿Qué rutas reciben realmente el contexto de seguridad?

No hay evidencia actual que permita resolverlo. El parche OpenJDK histórico demuestra una intersección específica en la construcción de constructores serializables, pero no prueba que `readObject`, `readResolve`, proxies, `ReflectionFactory` alterna o `ClassLoader.defineClass` reciban automáticamente el mismo contexto.

En PS4 13.52 no se puede afirmar si:

- `readObject` se ejecuta bajo el dominio del constructor, bajo el contexto del stream o bajo otro contexto;
- `readResolve` tiene un control independiente;
- los proxies propagan todos los dominios;
- `ReflectionFactory` expone una ruta alternativa;
- `defineClass` asigna un `ProtectionDomain` derivado del `CodeSource` o uno específico del loader;
- `UserPreferenceManagerImpl` aplica filtros antes de `readObject`.

Todos esos puntos son **UNVERIFIED**, no vulnerabilidades afirmadas.

## Diferencias actuales realmente verificables

No apareció ninguna diferencia de implementación actual atribuible a PS4 13.52. La única diferencia verificable es editorial: la nota de release de 13.52 declara correcciones genéricas de seguridad mientras que 13.50 declara cambios de usabilidad. Esa diferencia no identifica el runtime Java y se clasifica **INDIRECT_13.52** únicamente como contexto de versión, no como evidencia de una mitigación concreta.

No se encontraron:

- firmas o nombres de métodos de 13.52;
- `ProtectionDomain[] domains` atribuido a Sony;
- `doIntersectionPrivilege` atribuido a BD-J 13.52;
- filtros actuales de `ObjectInputStream`;
- cambios de `readObject`/`readResolve`;
- overloads actuales de `defineClass`;
- una implementación actual de `UserPreferenceManagerImpl`;
- un commit público Sony que describa alguno de estos cambios.

## Evidencia mínima faltante

Para confirmar o descartar la mitigación en 13.52 se necesita una fuente pública verificable y específica de esa build o de una build inmediatamente adyacente que exponga al menos una implementación, decompilación o inventario de símbolos de:

1. `ObjectStreamClass`, con `domains`, cálculo de dominios y ruta `newInstance`;
2. `ReflectionFactory`, con `newInstanceForSerialization` o su sustituto;
3. `ObjectInputStream`, incluyendo `readObject` y tratamiento de `readResolve`;
4. `ClassLoader`, incluyendo `defineClass`, `CodeSource` y `ProtectionDomain`;
5. `UserPreferenceManagerImpl`, incluyendo fuente, filtros y deserialización;
6. un changelog o diff que vincule el cambio con 13.52.

Una demo BD-J, una salida `Hello World` o la frase genérica de correcciones de seguridad no satisfacen este requisito.

## Conclusión final

La prioridad de encontrar una diferencia actual verificable en 13.52 no se pudo satisfacer con las fuentes públicas disponibles. La evidencia oficial confirma correcciones de seguridad, pero no identifica una sola clase o método del runtime Java/BD-J. El corpus público local contiene sólo clientes, stubs y precedentes históricos.

Por tanto:

> **No hay evidencia actual suficiente para afirmar que la mitigación de `ProtectionDomain` esté integrada, modificada o ausente en PS4 13.52. Todos los controles específicos de deserialización, reflexión y classloading permanecen `UNVERIFIED`.**

## Referencias

[1]: https://www.playstation.com/en-us/support/hardware/ps4/system-software-info/ "PlayStation 4 system software update features; version 13.52"
[2]: https://www.playstation.com/en-us/support/hardware/ps4/system-software/ "Official PlayStation 4 system software support"
[3]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 "OpenJDK protection-domain deserialization change"
[4]: https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/io/ObjectInputStream.java "OpenJDK ObjectInputStream"
[5]: https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/io/ObjectStreamClass.java "OpenJDK ObjectStreamClass"
[6]: https://github.com/TheOfficialFloW/bd-jb "Public bd-jb client repository"
[7]: https://github.com/john-tornblom/bdj-sdk "Public BDJ SDK"
