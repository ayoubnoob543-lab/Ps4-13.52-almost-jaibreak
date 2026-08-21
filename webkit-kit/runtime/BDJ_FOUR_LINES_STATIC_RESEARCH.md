# Investigación estática independiente: cuatro líneas BD-J hacia 13.52

## Alcance y clasificación

Este informe no busca PUPs, dumps ni runtime privado y no ejecuta código. Revisa fuentes públicas verificables y distingue precedentes históricos de evidencia específica de PS4 13.52.

Las categorías usadas son:

- **CONFIRMED**: demostrado directamente para el firmware indicado por una fuente primaria o artefacto verificable.
- **DIRECT/HISTORICAL**: mecanismo demostrado históricamente, pero no atribuido a 13.52.
- **STRONG_INDIRECT**: evidencia pública próxima al comportamiento, sin bytes o prueba directa de 13.52.
- **DOCUMENTED_ONLY**: descrito por una fuente, sin reproducción independiente suficiente.
- **HYPOTHESIS**: posibilidad técnica que requiere una condición no demostrada.
- **UNVERIFIED**: no hay evidencia suficiente para afirmar presencia o ausencia en 13.52.

## Resumen priorizado

| Prioridad | Línea | Mecanismo histórico | Estado para 13.52 |
|---:|---|---|---|
| 1 | Ixc/callbacks privilegiados | `IxcProxy`/`WrappedRemote` invocan métodos bajo `doPrivileged`; proxies y clases bootstrap permiten alcanzar métodos protegidos | **HYPOTHESIS / UNVERIFIED** |
| 2 | Reflection/acceso interno | `com.oracle.security.Service.newInstance` y `ProviderAdapter.setProviderAccessor` permiten instanciación/reflection sobre clases restringidas | **DIRECT/HISTORICAL; UNVERIFIED** |
| 3 | Deserialización privilegiada | `UserPreferenceManagerImpl` hace `readObject()` dentro de acción privilegiada y puede instanciar objetos controlados | **DIRECT/HISTORICAL; UNVERIFIED** |
| 4 | ClassLoader/canonicalización/JAR anidado | `BdjPolicyImpl` canoniza, mientras `JarZipFile` interpreta literalmente la entrada anidada | **DIRECT para 13.00–13.02; REFUTED para ese rango concreto posterior; UNVERIFIED para variantes 13.52** |

## I. Ixc y callbacks privilegiados

### Mecanismo histórico

El reporte público #1379975 describe una vulnerabilidad en `com.sony.gemstack.org.dvb.io.ixc.IxcProxy.invokeMethod`: un método público, no estático, perteneciente a una clase pública y extensible podía ser llamado mediante una interfaz `java.rmi.Remote`, haciendo que controles de permisos del método objetivo se ejecutaran en un contexto privilegiado. El reporte usa como ejemplo `File.list()` y afirma que la primitiva permite inspeccionar o extraer archivos.

El reporte público posterior #3104356 documenta dos implementaciones de Ixc: `org.dvb.io.ixc` y `com.sun.xlet.ixc`. La primera tenía una comprobación de call stack para permitir sólo llamadas desde `IxcProxy`, pero el propio informe afirma que la comprobación seguía admitiendo proxies reales creados por `IxcProxyBuilder`. La segunda contiene `WrappedRemote.com_sun_xlet_execute`, que invoca `remoteMethod` dentro de `AccessController.doPrivileged`; una clase stub generada puede controlar el `Method` que se ejecuta.

### Controles y mitigaciones conocidas

Los controles históricos incluyen comprobación del call stack, `SecurityManager.checkPermission`, restricciones de interfaces `Remote`, requisitos de `RemoteException` y validación de métodos/proxies. La evidencia pública demuestra que la primera mitigación de Ixc no era suficiente en el contexto del reporte #3104356.

No existe en estas fuentes un diff público que demuestre cómo quedaron ambas implementaciones en 13.52. Por eso no puede afirmarse que el fallo siga presente ni que haya sido eliminado.

### Qué podría sobrevivir

Una variante sólo podría sobrevivir si 13.52 conservara una ruta que combine un proxy permitido, un callback ejecutado con `doPrivileged` y un método cuya comprobación se haga después de perder el contexto del llamador. Esta es una **HYPOTHESIS**; no se debe confundir con la existencia histórica de las clases.

### Evidencia que confirmaría o descartaría

Confirmaría la hipótesis un diff o decompilación 13.52 de `IxcProxy`, `IxcProxyBuilder`, `WrappedRemote`, `IxcClassLoader` y las rutas de generación de stubs, mostrando la comprobación y el contexto de invocación. La descartaría una implementación 13.52 que elimine la invocación privilegiada, valide el origen completo del proxy y aplique el permiso al llamador original.

**Prioridad: 1.** Es la línea histórica más directamente conectada con callbacks privilegiados y con la desactivación de controles Java, pero sigue **UNVERIFIED** para 13.52.

## II. Deserialización y objetos Java privilegiados

### Mecanismo histórico

El reporte #1379975 describe `com.sony.gemstack.org.dvb.user.UserPreferenceManagerImpl`. Su método de inicialización lee `userprefs` dentro de `AccessController.doPrivileged`, usando `ObjectInputStream.readObject()` y una ruta persistente obtenida mediante `RootCertManager.getOriginalPersistentRoot()`.

El informe afirma que un objeto serializado malicioso podía causar instanciación de clases bajo contexto privilegiado. Para firmwares antiguos como 5.05, el reporte relaciona la explotación con la posibilidad de instanciar un `ClassLoader` y usar `defineClass` con permisos elevados. También cita el commit OpenJDK `020204a972d9be8a3b2b9e75c2e8abea36d787e9` como una diferencia relevante en versiones antiguas.

### Controles y mitigaciones conocidas

El control principal es impedir deserialización de clases no permitidas o evitar que datos controlables alcancen `readObject()` privilegiado. La propia referencia al commit OpenJDK indica que el comportamiento de deserialización cambió entre generaciones, pero no demuestra cómo Sony integró o adaptó ese cambio.

No hay un diff público específico de `UserPreferenceManagerImpl`, de la lista de clases permitidas o del filtro de deserialización en PS4 13.52.

### Qué podría sobrevivir

Una variante podría sobrevivir si el archivo persistente siguiera siendo manipulable por una etapa anterior y el filtro aceptara una clase con `readObject`, `readResolve`, proxy o callback que reintrodujera una acción privilegiada. Esto es una **HYPOTHESIS** y depende de dos condiciones no demostradas: control del archivo y disponibilidad del gadget.

### Evidencia que confirmaría o descartaría

Confirmaría la hipótesis una versión 13.52 de `UserPreferenceManagerImpl`, su `ObjectInputStream`, filtros de clase y la procedencia del archivo. La descartaría un filtro estricto con tipos permitidos, una sustitución de `ObjectInputStream`, integridad autenticada del archivo o ausencia de una ruta controlable desde BD-J.

**Prioridad: 3.** Es históricamente potente, pero la dependencia en un archivo persistente y en gadgets concretos hace que la extrapolación a 13.52 sea débil sin una comparación del runtime.

## III. ClassLoader, canonicalización y JAR anidado

### Variante histórica

El reporte #3452696 describe dos interpretaciones distintas de una URL como:

```text
file:/dsm/00000.jar/../../app0/bdjstack/lib/ext/00000.jar
```

`BdjPolicyImpl` aplica `File.getCanonicalPath()`, resolviendo `..` y comparando el resultado con `javaHome/lib/ext`, mientras `JarZipFile` transforma `/dsm/` a una ruta virtual de disco y trata `../../app0/...` como nombre literal de entrada en un JAR anidado. El informe describe una discrepancia entre el archivo que recibe la política y el archivo que realmente abre el classloader, con concesión de `AllPermission`.

La fuente pública asigna explícitamente el reporte a PS4 13.00–13.02. El advisory CVE-2025-64390/GHSA-87pc-67c4-x49w también limita la descripción a 13.00–13.02.

### Mitigaciones conocidas

La mitigación lógica necesaria es hacer que la identidad usada por la política sea la misma que la identidad usada por el loader, rechazar rutas con componentes ambiguos y verificar la firma del contenido después de resolver el JAR real. También debe evitarse conceder permisos por un prefijo canónico sin comprobar límites de componente y origen físico.

### Qué podría sobrevivir

El bug exacto documentado no debe trasladarse a 13.52: la evidencia pública no lo extiende a esa versión. Sólo podría existir una variante distinta si alguna nueva ruta de nested JAR, copia temporal, `URLClassLoader` o fallback conserva la separación entre `CodeSource` y objeto cargado. No se encontró evidencia pública nueva que demuestre esa variante.

### Evidencia que confirmaría o descartaría

Confirmaría una variante una comparación 13.52 de `BdjPolicyImpl`, `XletClassLoader`, `JarZipFile`, `BDJFactory` y la verificación de certificados, con una misma entrada evaluada por política y loader. La descartaría una ruta única de resolución que preserve el objeto físico y el `CodeSource`, junto con verificación de firma sobre el JAR anidado real.

**Prioridad: 4.** El bug histórico está documentado de forma directa para 13.00–13.02, pero no es evidencia de 13.52.

## IV. Reflection y acceso a clases internas

### Mecanismo histórico

El reporte #1379975 describe `com.oracle.security.Service.newInstance`, que invoca `Class.forName` sobre un nombre de clase controlable y permite instanciar clases restringidas, incluidas clases en paquetes `sun.`, cuando tienen un constructor público compatible. El informe indica que la comprobación de registro podía ser sorteada mediante `com.oracle.ProviderAdapter.setProviderAccessor` con un `ProviderAccessor` personalizado.

La relevancia de esta línea no es que `Class.forName` sea por sí mismo una escalada, sino que un proveedor o servicio de seguridad puede convertirse en un mecanismo de acceso a clases internas si no valida de forma estricta el origen del servicio, el nombre de clase y el contexto de llamada.

### Controles y mitigaciones conocidas

El control histórico incluía comprobar que el servicio estaba registrado y que `ProviderAdapter.getService(...)` devolvía el mismo objeto. El reporte afirma que ese control era evitable mediante un accessor personalizado. Las mitigaciones posibles son sellar el proveedor, comprobar identidad y origen del accessor, restringir paquetes internos y validar los tipos/constructores antes de instanciar.

No hay evidencia pública específica de que las clases `com.oracle.security.Service` y `com.oracle.ProviderAdapter` mantengan las mismas firmas o comportamiento en 13.52.

### Qué podría sobrevivir

Podría sobrevivir una variante si otra API de seguridad, provider, proxy o classloader siguiera permitiendo elegir un nombre de clase interno y ejecutar un constructor bajo permisos ampliados. Eso es una **HYPOTHESIS**, no una confirmación.

### Evidencia que confirmaría o descartaría

Confirmaría la línea una decompilación 13.52 de `Service.newInstance`, `ProviderAdapter`, las comprobaciones de registro y los filtros de paquetes, además de una ruta de llamada desde BD-J. La descartaría una implementación que elimine `Class.forName` sobre entradas controlables, selle el accessor y aplique restricciones de módulos/clases antes de resolver el nombre.

**Prioridad: 2.** Históricamente conecta de forma más directa con el acceso a clases internas que podría preceder a `Unsafe` o APIs nativas, aunque no produce native usermode por sí misma.

## Conclusión

La evidencia nueva y verificable permite reforzar cuatro precedentes históricos, pero no confirma ninguna vulnerabilidad en PS4 13.52. La prioridad técnica queda en:

1. verificar las implementaciones de Ixc y sus callbacks privilegiados;
2. verificar reflection/provider/classloader como ruta de acceso a clases internas;
3. comprobar deserialización sólo si existe una fuente controlable y un gadget aceptado;
4. tratar la canonicalización/JAR anidado como un bug histórico limitado a 13.00–13.02, no como una explicación automática para 13.52.

El dato que permitiría avanzar no es otro resumen histórico, sino un diff o decompilación 13.52 de las clases y métodos concretos enumerados en cada sección. Sin esa evidencia, la clasificación correcta es **UNVERIFIED** para 13.52.

## Referencias

[1]: https://hackerone.com/reports/3104356 "Blu-ray Disc Java Sandbox Escape via two vulnerabilities"

[2]: https://hackerone.com/reports/1379975 "bd-j exploit chain"

[3]: https://hackerone.com/reports/3452696 "PS4 BD-J privilege escalation using nested JAR"

[4]: https://github.com/advisories/GHSA-87pc-67c4-x49w "CVE-2025-64390 / GHSA-87pc-67c4-x49w"

[5]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 "OpenJDK commit referenced by report #1379975"

[6]: https://www.nccgroup.com/research/abusing-blu-ray-players-part-1-sandbox-escapes/ "NCC Group: Abusing Blu-ray Players Part 1 – Sandbox Escapes"

[7]: https://github.com/dptug/BD-JB-1250-lapse "BD-JB-1250-lapse public repository"
