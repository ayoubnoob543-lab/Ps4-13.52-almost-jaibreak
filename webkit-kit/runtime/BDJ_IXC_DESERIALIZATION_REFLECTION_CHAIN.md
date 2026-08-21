# Cadena histórica Ixc → deserialización/reflection/provider

## Alcance

Este informe analiza exclusivamente la combinación histórica de tres superficies BD-J: Ixc/callbacks privilegiados, deserialización privilegiada y reflection/provider. No busca ni requiere `rt.jar`, `bdjstack.jar`, PUPs, dumps privados o hardware, y no ejecuta el código histórico.

La pregunta es si esas superficies forman una cadena histórica coherente y qué puede afirmarse para PS4 13.52 sin confundir código público antiguo con evidencia del firmware actual.

## Hallazgo central nuevo

El checkout público local de `TheOfficialFloW/bd-jb` muestra una composición concreta entre Ixc y reflection/provider que no depende de `sunjce` ni necesita la ruta de deserialización:

```text
IxcProxyImpl
  → super.invokeMethod(...)
  → ServiceImpl (subclase de com.oracle.security.Service)
  → ServiceInterface extends java.rmi.Remote
  → ProviderAccessorImpl.setProviderAccessor()
  → Service.newInstance(...)
  → URLClassLoader
  → carga del payload
```

Los archivos relevantes son:

- `IxcProxyImpl.java`: subclase de `com.sony.gemstack.org.dvb.io.ixc.IxcProxy`; conserva el objeto remoto y delega a `super.invokeMethod`.
- `ServiceInterface.java`: expone `newInstance(Object)` mediante `java.rmi.Remote` y `RemoteException`.
- `ServiceImpl.java`: subclase de `com.oracle.security.Service` que implementa esa interfaz remota.
- `ProviderAccessorImpl.java`: copia servicios y llama a `ProviderAdapter.setProviderAccessor(this)`.
- `ExploitServiceProxyImpl.java`: busca `com.oracle.security.Service`, registra un servicio cuyo nombre de clase es `URLClassLoader`, y llama a `newInstance` a través de Ixc.
- `Payload.java`: el cliente histórico carga una clase después y ejecuta `System.setSecurityManager(null)` desde una acción privilegiada.

Esta composición es **DIRECT/HISTORICAL** para el código público del cliente; sigue siendo **UNVERIFIED** para 13.52.

## Matriz completa de la cadena

| Eslabón | Evidencia histórica | Relación con los otros eslabones | Estado 13.52 |
|---|---|---|---|
| Xlet BD-J inicial | Los reportes describen el contexto BD-J y el cliente público implementa un Xlet/proyecto BD-J | Punto de entrada de toda la cadena | **STRONG_INDIRECT** |
| `IxcProxy`/callback privilegiado | #1379975 y #3104356 describen invocación de métodos bajo contexto privilegiado | Permite presentar un objeto `ServiceImpl` como superficie remota | **HISTORICAL_ONLY / UNVERIFIED** |
| `ServiceInterface extends Remote` | Código público exige `RemoteException` y expone `newInstance` | Hace elegible el método provider para el modelo Ixc histórico | **DIRECT/HISTORICAL / UNVERIFIED** |
| `ServiceImpl extends com.oracle.security.Service` | Código público crea una subclase concreta | Une la superficie Ixc con `Service.newInstance` | **DIRECT/HISTORICAL / UNVERIFIED** |
| `ProviderAdapter.setProviderAccessor` | Código público instala un accessor que devuelve servicios controlados | Hace que `Service.newInstance` acepte el servicio preparado | **DIRECT/HISTORICAL / UNVERIFIED** |
| `Service.newInstance`/`Class.forName` | #1379975 documenta instanciación de clase controlada; el cliente prepara `URLClassLoader` | Produce un classloader con el constructor seleccionado | **HISTORICAL_ONLY / UNVERIFIED** |
| Deserialización `readObject` privilegiada | #1379975 documenta `UserPreferenceManagerImpl` y `ObjectInputStream` bajo `doPrivileged` | Es una ruta alternativa para instanciar objetos/gadgets; no aparece como requisito en la composición provider del cliente | **HISTORICAL_ONLY / UNVERIFIED** |
| `URLClassLoader`/carga de clase | `ExploitServiceProxyImpl` prepara una URL y carga una clase mediante el loader | Puede llevar al código Java posterior, pero no es native usermode por sí mismo | **HISTORICAL_ONLY / UNVERIFIED** |
| Desactivación de `SecurityManager` | `Payload` histórico llama `System.setSecurityManager(null)` dentro de `doPrivileged` | Resultado histórico del cliente, no evidencia de 13.52 | **HISTORICAL_ONLY / UNVERIFIED** |
| Primitive adicional | El reporte #1379975 enlaza después compiler receiver/JIT; este informe no ejecuta ni valida esa fase | Requeriría otro componente y su contrato | **UNVERIFIED** |

## Ixc y provider: cadena coherente sin `sunjce`

La evidencia de código público demuestra una ruta histórica que no necesita `sunjce` como condición conceptual. `ExploitServiceProxyImpl` comprueba la clase `com.oracle.security.Service`, obtiene proveedores, crea `ServiceImpl`, registra el servicio mediante `ProviderAccessorImpl`, y llama al método `newInstance` a través de `IxcProxyImpl`.

La composición es coherente porque el método remoto está diseñado para satisfacer las restricciones históricas de Ixc: la interfaz extiende `Remote` y declara `RemoteException`; la implementación es una subclase de `Service`; y el accessor expone el servicio al adapter. Esto confirma una **composición histórica concreta**, no una vulnerabilidad actual.

La parte importante para la investigación es que `sunjce` no es necesario para esa ruta histórica de Ixc→provider. Sin embargo, eliminar `sunjce` o su permiso especial no demostraría que Ixc/provider esté corregido: son superficies separadas.

## Deserialización: ruta alternativa, no eslabón demostrado de la composición

El reporte #1379975 describe una segunda familia histórica: `UserPreferenceManagerImpl` lee `userprefs` mediante `ObjectInputStream.readObject()` dentro de `AccessController.doPrivileged`. El informe relaciona esa ruta con instanciación de objetos y, en firmwares antiguos, con `ClassLoader`/`defineClass`.

No aparece en el cliente público local una composición que use simultáneamente `readObject()` y `ProviderAdapter`. Por ello, la afirmación más precisa es:

> **Ixc→provider/reflection y deserialización privilegiada son dos rutas históricas que pueden converger conceptualmente en acceso a clases, pero no hay evidencia de que fueran una única cadena obligatoria.**

La deserialización sólo sería combinable si un objeto/gadget producido por `readObject` pudiera alcanzar el callback provider o una clase interna bajo el mismo contexto. Esa conexión es **HYPOTHESIS**, no está demostrada por el código público revisado.

## Mitigaciones que podrían romper la cadena

| Mitigación | Eslabón afectado | Efecto si existe en 13.52 |
|---|---|---|
| Validación estricta del llamador y del origen de proxies | Ixc | Impide que `IxcProxy` acepte el wrapper `ServiceImpl` |
| Eliminación de `doPrivileged` alrededor de la invocación remota | Ixc/WrappedRemote | El método conserva el contexto restringido del Xlet |
| Sellado de `ProviderAccessor` y validación de identidad del servicio | Provider | Impide instalar un accessor o servicio controlado |
| Restricción de `Class.forName`/constructores y paquetes internos | Reflection | Impide instanciar `URLClassLoader` o clases `sun.*` |
| Filtros estrictos de deserialización | `readObject` | Impide gadgets y subclases de `ClassLoader` |
| Integridad/autenticación del archivo `userprefs` | Deserialización | Elimina el control de entrada necesario |
| Prohibición de `System.setSecurityManager(null)` | Resultado Java | Evita desactivar la sandbox aunque se cargue la clase |
| Eliminación o validación del compiler-agent | Primitive posterior | Rompe el salto de Java privilegiado a JIT/native |

No hay un diff público específico de 13.52 que confirme qué mitigaciones están implementadas. La matriz anterior son criterios de confirmación/falsación, no afirmaciones sobre el firmware.

## Evidencia específica de 13.52

No se encontró evidencia directa específica de 13.52 para `IxcProxy`, `WrappedRemote`, `UserPreferenceManagerImpl`, `Service`, `ProviderAdapter` ni sus filtros. La demo pública de BD-J 13.52 no muestra nombres de esas clases, logs, excepciones o una primitive identificable.

Por tanto:

- `CONFIRMED_13.52`: **ningún eslabón**.
- `STRONG_INDIRECT`: sólo el contexto público de una demostración BD-J/userland, sin mecanismo.
- `HISTORICAL_ONLY`: la composición Ixc→provider y la ruta de deserialización descritas en #1379975/#3104356 y el checkout público.
- `HYPOTHESIS`: que una de esas composiciones sobreviva en 13.52 o se combine con otra ruta.

## Primer eslabón no demostrado

El primer eslabón no demostrado en una cadena específica de 13.52 es la **disponibilidad y semántica actual de Ixc/callbacks privilegiados**. Sin demostrar que 13.52 permite el callback con el contexto requerido, no se puede afirmar que `Service.newInstance`, `ProviderAdapter` o `readObject` sean alcanzables desde un Xlet.

Incluso si Ixc estuviera disponible, el siguiente bloqueo sería la validación actual de `ProviderAccessor`/`Service.newInstance` y la posibilidad de desactivar el `SecurityManager`. La deserialización no debe introducirse como requisito sin evidencia de control sobre `userprefs`.

## Evidencia mínima para resolverlo

La evidencia mínima sería una fuente pública verificable de 13.52 que muestre:

1. el contrato o decompilación de `IxcProxy`, `IxcProxyBuilder` y `WrappedRemote`;
2. el comportamiento de `ProviderAdapter.setProviderAccessor` y `Service.newInstance`;
3. las restricciones de reflection y de paquetes/clases internas;
4. si `UserPreferenceManagerImpl.readObject` sigue existiendo y qué filtro aplica;
5. una salida de prueba que conecte el callback con la siguiente primitive, sin necesidad de ejecutar un payload.

## Conclusión

Sí existe una **cadena histórica coherente** entre Ixc y reflection/provider, y puede evitar depender de `sunjce`:

```text
IxcProxy → ServiceImpl/Remote → ProviderAccessor → Service.newInstance → URLClassLoader
```

La deserialización privilegiada es una **ruta histórica alternativa** y podría converger conceptualmente, pero no está demostrada como parte obligatoria de la misma cadena. Ningún eslabón está confirmado específicamente en 13.52. El primer punto no verificado es Ixc/callbacks privilegiados en ese firmware; el segundo es la semántica actual de `ProviderAdapter`/`Service.newInstance`.

## Referencias

[1]: https://hackerone.com/reports/1379975 "PlayStation report #1379975: bd-j exploit chain"

[2]: https://hackerone.com/reports/3104356 "PlayStation report #3104356: Blu-ray Disc Java Sandbox Escape via two vulnerabilities"

[3]: https://github.com/TheOfficialFloW/bd-jb "TheOfficialFloW/bd-jb"

[4]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 "OpenJDK commit referenced by report #1379975"

[5]: https://www.nccgroup.com/research/abusing-blu-ray-players-part-1-sandbox-escapes/ "NCC Group: Abusing Blu-ray Players Part 1 – Sandbox Escapes"
