# ObjectStreamClass → ReflectionFactory → ProtectionDomain → ClassLoader

## Alcance

Este informe analiza exclusivamente la segunda línea prioritaria solicitada: `ObjectStreamClass`, `ReflectionFactory`, `ObjectInputStream.readObject`, `readResolve`, `AccessController`, `ProtectionDomain`, `ClassLoader` y `defineClass`, comparando el commit OpenJDK público con el corpus BD-J histórico disponible.

No se descargaron PUPs, dumps privados ni runtime propietario de PS4 13.52. No se ejecutaron exploits, payloads, JAR, ELF/BIN ni hardware.

Las categorías son `DIRECT_13.52`, `INDIRECT_13.52`, `HISTORICAL_ONLY`, `HYPOTHESIS` y `DISCARDED`.

## Conclusión ejecutiva

El repositorio `webkit-ps4-1352-kit` no contiene una implementación de runtime BD-J/JVM ni fuentes de `ObjectStreamClass`, `ReflectionFactory` o `ObjectInputStream` de Sony. Sí contiene informes y clientes históricos. El checkout público de `bd-jb` muestra uso de reflection, `ClassLoader$NativeLibrary`, `URLClassLoader`, `Class.forName`, `loadClass`, `newInstance` y `AccessController`, pero no implementa la mitigación OpenJDK.

El commit OpenJDK `020204a972d9be8a3b2b9e75c2e8abea36d787e9` introduce una mitigación precisa para **la construcción de objetos deserializados**: recopila los `ProtectionDomain` que separan la clase concreta de la clase que declara el constructor y ejecuta la construcción bajo la intersección entre el contexto actual y esos dominios. Esto protege una frontera concreta; no demuestra filtros completos para `readObject`, `readResolve`, proxies, loaders alternativos o toda la reflexión.

No existe evidencia `DIRECT_13.52`.

## 1. Evidencia dentro del repositorio y corpus local

### 1.1 `webkit-ps4-1352-kit`

La búsqueda en la rama autorizada no encontró fuentes de runtime para los símbolos solicitados. Los únicos resultados relevantes son informes BD-J, documentación y `src/org/bdj/SuidScanner.java`, no implementaciones de `ObjectStreamClass`, `ReflectionFactory`, `ObjectInputStream` o `ClassLoader` de PS4.

Clasificación: **HISTORICAL_ONLY** para los informes; **UNVERIFIED** para cualquier afirmación sobre 13.52.

### 1.2 Cliente histórico `bd-jb`

El archivo `/home/ubuntu/ps4-bdj-trust-audit/evidence/bd-jb-src/src/com/bdjb/api/API.java` contiene las siguientes referencias de cliente:

| Ruta/líneas | Observación | Clasificación |
|---|---|---|
| `API.java:27-40` | Nombres de símbolos y `ClassLoader$NativeLibrary.find/findEntry` | **HISTORICAL_ONLY** |
| `API.java:92-100` | Selecciona una implementación `Unsafe` y distingue JDK 8/JDK 11 | **HISTORICAL_ONLY** |
| `API.java:102-124` | Obtiene `ClassLoader$NativeLibrary`, busca método y campo mediante reflection, habilita acceso y crea la instancia | **HISTORICAL_ONLY** |
| `API.java:127-145` | Resuelve símbolos mediante una capa nativa del cliente histórico | **HISTORICAL_ONLY** |

El archivo `/home/ubuntu/ps4-bdj-trust-audit/evidence/bd-jb-src/src/com/bdjb/exploit/sandbox/ExploitServiceProxyImpl.java:31-60` usa `Class.forName`, `URLClassLoader`, `loadClass` y `newInstance` después de la llamada histórica al servicio/provider. Es evidencia del cliente, no del runtime de 13.52.

El archivo `/home/ubuntu/ps4-bdj-trust-audit/evidence/bd-jb-src/src/com/bdjb/exploit/sandbox/Payload.java:10-17` contiene `AccessController.doPrivileged(this)`. No contiene `ObjectStreamClass`, `ReflectionFactory` ni una implementación de `ProtectionDomain`.

### 1.3 Fork/loader público BDJPlus

`/home/ubuntu/ps4-bdj-trust-audit/evidence/bdjplus-src/src/com/sony/bdjstack/system/BDJModule.java:264-307,351,400,649-653` contiene `URLClassLoader`, `Class.forName`, `loadClass` y `newInstance`. La implementación funciona como loader Java de un fork público, pero no contiene `ObjectStreamClass`, `ReflectionFactory`, `ObjectInputStream` ni una integración demostrada de la mitigación OpenJDK.

La existencia de estas referencias confirma que los proyectos públicos usan classloading y reflection como interfaces de cliente. No confirma qué clases bootstrap o filtros existen en PS4 13.52.

## 2. Cadena histórica completa

La cadena histórica descrita por el código y los reportes públicos puede representarse así:

```text
userprefs / flujo de deserialización
  → ObjectInputStream.readObject()
  → ObjectStreamClass descubre la clase y el constructor
  → ReflectionFactory / constructor de serialización
  → AccessController.doPrivileged o contexto privilegiado
  → construcción de objeto bajo ProtectionDomain
  → posible objeto ClassLoader / defineClass
  → carga de clases Java posteriores
```

El cliente `bd-jb` añade otra ruta de reflection posterior:

```text
objeto obtenido mediante BD-J/provider
  → Class.forName / URLClassLoader
  → loadClass
  → newInstance
```

Estas dos secuencias no deben fusionarse automáticamente. La primera depende de la implementación de serialización del runtime. La segunda es código cliente histórico que presupone que ya existe una primitive de acceso/reflection.

## 3. Mitigación exacta de OpenJDK

El commit público [1] modifica cuatro archivos y declara el objetivo `8180024: Improve construction of objects during deserialization`.

### 3.1 Estado almacenado

`ObjectStreamClass` añade:

```java
private ProtectionDomain[] domains;
```

El descriptor calcula este campo durante su inicialización y lo copia en las rutas de proxy y non-proxy. El objetivo es conservar los dominios que deben aplicarse cuando se invoque el constructor de serialización.

### 3.2 `getProtectionDomains`

La función nueva sólo recoge dominios cuando se cumplen estas condiciones:

```text
constructor != null
AND class.getClassLoader() != null
AND System.getSecurityManager() != null
```

Después recorre la jerarquía desde la clase concreta hasta la clase que declara el constructor. Para cada clase intermedia obtiene `getProtectionDomain()` y añade el dominio a un conjunto. Si la jerarquía no llega al declaring class esperado, reemplaza el conjunto por un dominio creado por `noPermissionsDomain()`.

La mitigación pretende proteger estas invariantes:

| Invariante | Propósito |
|---|---|
| El constructor real pertenece a la jerarquía esperada | Evitar usar un constructor privilegiado fuera de la cadena de clases |
| Cada clase intermedia aporta su `ProtectionDomain` | No perder permisos de una subclase serializable o loader intermedio |
| Una jerarquía incoherente produce dominio sin permisos | Fail closed en vez de heredar el contexto privilegiado |
| La comprobación sólo aplica con SecurityManager activo | Mantener el coste/semántica de la plataforma protegida |

### 3.3 `newInstance`

La ruta anterior hacía directamente:

```java
return cons.newInstance();
```

La ruta nueva mantiene la llamada directa si `domains == null` o está vacía. Si hay dominios, crea una acción privilegiada y llama:

```java
jsa.doIntersectionPrivilege(
    pea,
    AccessController.getContext(),
    new AccessControlContext(domains));
```

La acción ejecuta `cons.newInstance()` y traduce las excepciones reflectivas a través de `UndeclaredThrowableException` para recuperarlas después.

La operación importante no es conceder todos los permisos del constructor: es calcular la **intersección** del contexto actual con los dominios que separan la clase concreta de su constructor.

### 3.4 `ReflectionFactory` y CORBA

El diff también cambia `src/java.corba/share/classes/com/sun/corba/se/impl/io/ObjectStreamClass.java` y `src/jdk.unsupported/share/classes/sun/reflect/ReflectionFactory.java`. El resumen de Git indica cuatro archivos modificados. La mitigación, por tanto, no está limitada a un único método de `ObjectStreamClass`; también ajusta rutas relacionadas con construcción serializable y reflection interna.

La evidencia pública no demuestra que una implementación BD-J de Sony incluya estos cambios completos, ni que todos los caminos propietarios de deserialización utilicen el mismo `ObjectStreamClass`.

## 4. Variantes residuales posibles

Las variantes siguientes son hipótesis de análisis, no vulnerabilidades afirmadas.

| Variante | Condición necesaria | Primer punto donde se rompe | Clasificación |
|---|---|---|---|
| Protección incompleta de jerarquía | El descriptor no recorre todos los loaders/superclases o usa un declaring class distinto | Si `getProtectionDomains` alcanza todas las clases y el declaring class coincide, la variante desaparece | **HYPOTHESIS** |
| `readObject` fuera de la ruta protegida | Un `readObject` o callback se invoca con privilegios antes/después de `ObjectStreamClass.newInstance` | Si toda construcción y callback pasan por el contexto intersecado, la variante no alcanza permisos adicionales | **HYPOTHESIS** |
| `readResolve` posterior | El objeto ya construido ejecuta `readResolve` en un contexto diferente al de la construcción | Si `readResolve` conserva el contexto correcto o no es controlable, se rompe | **HYPOTHESIS** |
| Proxy serializable | `initProxy` copia metadatos pero una ruta proxy distinta evita el cálculo o cambia la clase concreta | Si el proxy reutiliza `domains` y el constructor real se valida igual, se rompe | **HYPOTHESIS** |
| `ReflectionFactory` alternativo | BD-J conserva una API de construcción que no pasa por la ruta endurecida de `ObjectStreamClass.newInstance` | Si todas las rutas llaman la construcción intersecada, se rompe | **HYPOTHESIS** |
| Loader alternativo / `defineClass` | Un `ClassLoader` cargado por otra ruta obtiene `defineClass` con permisos independientes de la deserialización | Si el loader y su `ProtectionDomain` quedan dentro de la intersección, se rompe | **HYPOTHESIS** |
| SecurityManager ausente | `getProtectionDomains` devuelve `null` y se usa la ruta directa por diseño | Esto no es automáticamente una vulnerabilidad; requiere además una fuente de privilegios y una operación controlable | **HYPOTHESIS** |
| Callback privilegiado externo | `doPrivileged` ajeno a la construcción reintroduce permisos antes de `readObject` o después de `readResolve` | Si no hay callback controlable o el contexto se intersecta correctamente, se rompe | **HYPOTHESIS** |

Ninguna variante es `DIRECT_13.52`.

## 5. Relación con `UserPreferenceManagerImpl`

El reporte histórico #1379975 describe `UserPreferenceManagerImpl` leyendo `userprefs` mediante `ObjectInputStream.readObject()` dentro de un contexto privilegiado. El mismo material relaciona la construcción con objetos y loaders en firmwares antiguos.

La relación técnicamente válida es:

```text
UserPreferenceManagerImpl
  → fuente de datos userprefs
  → ObjectInputStream.readObject
  → ObjectStreamClass / constructor de serialización
  → ProtectionDomain/AccessController
  → posible objeto ClassLoader
```

Lo que no puede afirmarse es que el runtime 13.52 conserve esta secuencia, que el commit OpenJDK esté integrado, o que `readResolve`, `ReflectionFactory` y `defineClass` sean alcanzables de la misma forma.

Clasificación: **HISTORICAL_ONLY**.

## 6. Evidencia posterior y estado 13.52

La evidencia pública posterior disponible es editorial y de reportes históricos. No se encontró un commit Sony, fork BD-J público o decompilación identificada de 13.52 que permita afirmar:

- si `ObjectStreamClass` incluye `domains`;
- si `getProtectionDomains` recorre la jerarquía de igual manera;
- si `newInstance` usa `doIntersectionPrivilege`;
- si `ReflectionFactory` fue sustituida o eliminada;
- si `UserPreferenceManagerImpl` filtra `userprefs` antes de deserializar;
- si `readResolve` o proxies tienen un contexto separado;
- si `ClassLoader/defineClass` está expuesto o restringido.

La ausencia de esos datos no es una evidencia de que la mitigación falte. Por eso el estado correcto es `UNVERIFIED`, no `HYPOTHESIS` de vulnerabilidad.

## 7. Ranking de variantes

| Prioridad | Variante | Motivo | Estado |
|---:|---|---|---|
| 1 | Integración parcial de la mitigación en `ObjectStreamClass`/`ReflectionFactory` | Es la única forma de que el cambio OpenJDK proteja una ruta pero deje otra construcción privilegiada | **HYPOTHESIS** |
| 2 | `readResolve` o callback posterior con contexto diferente | La mitigación descrita se centra en la construcción; el flujo posterior debe comprobarse por separado | **HYPOTHESIS** |
| 3 | Loader alternativo/`defineClass` fuera del contexto intersecado | Conecta directamente con la cadena histórica, pero requiere una API/loader accesible | **HYPOTHESIS** |
| 4 | Proxy serializable con propagación incorrecta de `domains` | El commit copia `domains` en `initProxy`; una implementación divergente podría omitirlo | **HYPOTHESIS** |
| 5 | Ausencia de SecurityManager | El commit no calcula dominios si no hay SecurityManager, pero eso no basta para crear una primitive | **HYPOTHESIS**, baja solidez |

## 8. Evidencia mínima para confirmar o descartar en 13.52

El mínimo requerido es una fuente pública verificable de los componentes efectivos de 13.52 que permita comparar:

| Componente | Dato mínimo |
|---|---|
| `ObjectStreamClass` | presencia de `domains`, `getProtectionDomains`, `noPermissionsDomain` y ruta `newInstance` |
| `ReflectionFactory` | implementación de constructores serializables y cualquier bypass de la ruta intersecada |
| `ObjectInputStream` | llamadas a `ObjectStreamClass.newInstance`, filtros y tratamiento de `readObject`/`readResolve` |
| `AccessController` | contexto activo alrededor de userprefs y callbacks |
| `ClassLoader` | exposición de `defineClass`, loader y `ProtectionDomain` asignado |
| `UserPreferenceManagerImpl` | fuente, validación y deserialización de `userprefs` |
| Proxies | propagación de `domains` en proxy/non-proxy y loader real |

Sin esa evidencia, el primer punto no verificado es la **implementación efectiva de `ObjectStreamClass` y la integración de la mitigación en el runtime BD-J 13.52**.

## Conclusión final

La mitigación OpenJDK es real y específica: protege la construcción de objetos serializables calculando los dominios de protección que separan la clase concreta de su constructor y ejecutando el constructor bajo una intersección de permisos.

El corpus local confirma los clientes históricos de reflection y classloading, pero no contiene el runtime BD-J ni una implementación de la mitigación para 13.52. Las variantes residuales —jerarquías incompletas, proxies, `readObject`, `readResolve`, `ReflectionFactory` alternativo, loaders y callbacks— son hipótesis de comparación, no vulnerabilidades confirmadas.

El resultado específico es:

> **No hay evidencia `DIRECT_13.52`; la cadena histórica sólo puede clasificarse `HISTORICAL_ONLY` y su compatibilidad actual permanece `UNVERIFIED`.**

## Referencias

[1]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 "OpenJDK 8180024: Improve construction of objects during deserialization"

[2]: https://hackerone.com/reports/1379975 "PlayStation #1379975: bd-j exploit chain"

[3]: https://hackerone.com/reports/3104356 "PlayStation #3104356: Blu-ray Disc Java Sandbox Escape via two vulnerabilities"

[4]: https://github.com/TheOfficialFloW/bd-jb "TheOfficialFloW bd-jb public client"

[5]: https://github.com/john-tornblom/bdj-sdk "Public BDJ SDK"
