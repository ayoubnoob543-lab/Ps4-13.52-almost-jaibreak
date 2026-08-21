# Rutas BD-J posteriores al escape histórico — Prompt 2

## Alcance y criterio

Esta investigación se centra exclusivamente en mecanismos posteriores o alternativos a las cuatro líneas ya conocidas. No se usaron `rt.jar`, `bdjstack.jar`, PUPs, dumps ni runtime privado de 13.52. No se ejecutaron exploits, payloads, binarios ni código contra hardware.

Las categorías de confianza son **DIRECT_HISTORICAL**, **STRONG_INDIRECT**, **HYPOTHESIS**, **DISCARDED** y **UNVERIFIED_13.52**. Ninguna categoría histórica se convierte automáticamente en evidencia de PS4 13.52.

## Hallazgos nuevos

### 1. Deserialización privilegiada y construcción de clases

HackerOne #1379975 documenta que `com.sony.gemstack.org.dvb.user.UserPreferenceManagerImpl.ReadPreferenceAction.run()` deserializa `userprefs` mediante `ObjectInputStream.readObject()` dentro de `AccessController.doPrivileged`. El informe describe la posibilidad histórica de que un objeto serializable active la construcción de una subclase `ClassLoader`, use `defineClass` y asigne `AllPermission` a un `ProtectionDomain` propio.

Ésta es una ruta distinta de Ixc/sunjce: su primitiva sería **instanciación/construcción privilegiada**, no acceso directo a `Unsafe` ni al compiler-agent. Sin embargo, el mismo informe dice que un cambio de OpenJDK identificado como `020204a972d9be8a3b2b9e75c2e8abea36d787e9` mejoró la construcción de objetos durante deserialización. El diff de OpenJDK añade `ProtectionDomain[] domains`, un dominio sin permisos y construcción bajo una intersección de privilegios. Eso constituye una mitigación histórica concreta, pero no demuestra que Sony la incorporase en 13.52.

**Confianza:** `DIRECT_HISTORICAL` para el gadget y la mitigación OpenJDK; `UNVERIFIED_13.52` para su presencia actual.

**Descartaría la variante 13.52:** un diff del `ObjectStreamClass`/runtime BD-J o un error que muestre la construcción denegada. Sin ese dato, no se puede confirmar ni descartar de manera específica.

### 2. `Provider.Service.newInstance` y `ProviderAdapter`

HackerOne #1379975 documenta que `com.oracle.security.Service.newInstance` aceptaba un nombre de clase y usaba `Class.forName` para instanciar clases restringidas, y que `com.oracle.ProviderAdapter.setProviderAccessor` permitía saltar una validación de registro. La primitiva potencial es **instanciación reflexiva de una clase protegida con una firma de constructor compatible**.

La API pública Java SE confirma que `Provider.Service.newInstance(Object)` es una fábrica que instancia por reflexión la clase de implementación declarada por un servicio, aunque el gadget Sony y sus validaciones son propietarios. La diferencia importante es que esta superficie podría proporcionar una vía de construcción privilegiada aun si se modificaran Ixc o `BdjPolicyImpl`.

**Confianza:** `DIRECT_HISTORICAL` para el código reportado; `HYPOTHESIS` como variante posterior; `UNVERIFIED_13.52` para disponibilidad.

**Descartaría la variante 13.52:** ausencia de `com.oracle.security.Service`, cambios en `ProviderAdapter`, validación de proveedor no evadible o eliminación de constructores públicos compatibles.

### 3. Contrato del compiler receiver como interfaz de memoria

HackerOne #1379975 documenta un `CompilerAgentRequest` de `0x58` bytes con campos `runtime_data`, `compiler_data`, `data1`, `data2` y `unk`. El compiler receiver copia la estructura a `compiler_data + 0x28`; el informe describe que el puntero se convierte históricamente en una primitiva write-what-where sobre memoria JIT.

El hallazgo relevante no es repetir “JIT”, sino que el mecanismo depende de un **protocolo de IPC/estructura**, no necesariamente de métodos Java concretos. Una variante posterior podría conservar la capacidad conceptual cambiando el tamaño, offsets, validaciones o canal del receiver. Por eso los offsets históricos no deben reutilizarse sin una especificación o bytes equivalentes.

**Confianza:** `DIRECT_HISTORICAL` para el contrato 0x58; `HYPOTHESIS` para cualquier variante; `UNVERIFIED_13.52`.

**Descartaría una variante:** evidencia de validación de rangos, eliminación del receiver, cambio de transporte o ausencia de memoria JIT escribible/controlable.

### 4. Generación de stubs Ixc y reflexión `findMethod`

HackerOne #3104356 muestra que `com.sun.xlet.ixc.IxcClassLoader` genera stubs con `com_sun_xlet_init`, `com_sun_xlet_destroy` y `com_sun_xlet_execute`. Los stubs guardan métodos obtenidos mediante un `findMethod` reflejado y ejecutan el objetivo desde `AccessController.doPrivileged`.

Esto revela una superficie auxiliar: **generación de código de stub + cache de objetos `Method` + reflexión en un classloader especial**. Si el fabricante hubiera cambiado Ixc, un error independiente en inicialización/destrucción, cache o resolución de métodos podría generar una primitiva distinta. El informe público, sin embargo, sólo demuestra que la cadena histórica acaba desactivando el SecurityManager.

**Confianza:** `DIRECT_HISTORICAL` para la arquitectura; `HYPOTHESIS` para una variante independiente; `UNVERIFIED_13.52`.

**Descartaría una variante:** stubs que no sean generables desde BD-J, `findMethod` con lista cerrada de clases/métodos o eliminación de la llamada privilegiada.

### 5. Nested JAR y discrepancia de canonicalización

HackerOne #3452696 describe una discrepancia entre `BdjPolicyImpl.getPermissions()` y `JarZipFile`: la política canonicaliza `..` y puede clasificar el origen como `lib/ext`, mientras el cargador interpreta la ruta como una entrada literal de un nested JAR. También intervienen `CoreApp.loadXlet`, `BDJFactory`, `JarDescriptorFactory`, `JarZipFile`, `JarInputStream`, `XletClassLoader` y `CoreAppId.isSigned()`.

El advisory público GHSA-87pc-67c4-x49w / CVE-2025-64390 limita esta vulnerabilidad a PS4 13.00–13.02. Por tanto, es evidencia de una superficie de policy/classloading, pero **no** una candidata viable para atribuir a 13.52 sin un nuevo diff o bytes.

**Confianza:** `DIRECT_HISTORICAL` para 13.00–13.02; `DISCARDED` como explicación directa de 13.52 salvo evidencia nueva.

## APIs Java→native alternativas

`Runtime.exec`, `System.loadLibrary` y JNI siguen siendo sólo posibilidades abstractas. La documentación Java SE demuestra que `doPrivileged` puede encapsular una llamada como `System.loadLibrary`, y que `Provider.Service` puede construir una implementación, pero no demuestra que el perfil BD-J de Sony exponga esas APIs, que exista una biblioteca aceptada o que una llamada produzca un entrypoint ejecutable.

La evidencia histórica más concreta para Java→native sigue siendo `ClassLoader$NativeLibrary.findEntry` y el compiler receiver. No apareció una interfaz propietaria pública alternativa que pueda clasificarse por encima de `HYPOTHESIS`.

## Tabla final ordenada por probabilidad

| Orden | Mecanismo | Evidencia histórica | Mitigación/cambio conocido | Relevancia potencial para 13.52 | Qué lo descartaría | Confianza |
|---:|---|---|---|---|---|---|
| 1 | Compiler receiver/JIT como protocolo de memoria | `CompilerAgentRequest` 0x58 y copia mediante `compiler_data` en #1379975 | Se desconoce cambio de ABI/validación | Podría sobrevivir con estructura o validaciones modificadas aunque cambien clases Java | Manifest/símbolos que eliminen receiver o validen punteros | `DIRECT_HISTORICAL` / `UNVERIFIED_13.52` |
| 2 | Deserialización privilegiada → constructor `ClassLoader`/`defineClass` | `UserPreferenceManagerImpl`, `ReadPreferenceAction`, `ObjectInputStream.readObject` en #1379975 | OpenJDK `020204a…` introduce dominios de protección e intersección de privilegios | Variante residual posible si Sony no incorporó el backport o lo adaptó parcialmente | `ObjectStreamClass` mitigado o `userprefs` no controlable | `DIRECT_HISTORICAL` / `UNVERIFIED_13.52` |
| 3 | `Provider.Service.newInstance` + `ProviderAdapter` | #1379975, `com.oracle.security.Service` y `setProviderAccessor` | Validaciones de registro y cambios de proveedor desconocidos | Podría ofrecer construcción reflexiva independiente de Ixc | Clase ausente, accessor sellado o constructor inaccesible | `DIRECT_HISTORICAL` / `HYPOTHESIS` |
| 4 | Stubs Ixc/cache `findMethod` | #3104356, `IxcClassLoader`, `WrappedRemote`, `com_sun_xlet_*` | Validaciones de stack y cambios de Ixc documentados históricamente | Posible superficie residual en generación/reflexión, sin asumir que sea la ruta usada | Stub generator cerrado o métodos cacheados no sustituibles | `DIRECT_HISTORICAL` / `HYPOTHESIS` |
| 5 | JNI/`loadLibrary`/callback propietario | Sólo contratos Java SE y precedentes generales | Perfil BD-J y políticas propietarias no verificadas | Alternativa si existe una biblioteca autorizada y un callback expuesto | Ausencia de JNI exportado o política que bloquee carga | `HYPOTHESIS` |
| 6 | Nested JAR `BdjPolicyImpl`/`JarZipFile` | #3452696 y CVE-2025-64390 | Afectación pública limitada a 13.00–13.02 | Útil como patrón de discrepancia policy/loader, no como candidato 13.52 | Rango CVE y parche temprano | `DIRECT_HISTORICAL` / `DISCARDED_13.52` |

## Comprobaciones seguras priorizadas

La comprobación de mayor valor no requiere ejecutar un exploit: obtener un diff o inventario de clases de `ObjectStreamClass`, `com.oracle.security.Service`, `ProviderAdapter`, `IxcClassLoader`, `WrappedRemote` y `JarZipFile` entre dos runtimes autorizados. Si sólo se dispone de código histórico, el siguiente paso seguro es comparar revisiones públicas de esos componentes y registrar firmas, validaciones y llamadas `doPrivileged`, sin construir payloads.

En segundo lugar, debe reconstruirse documentalmente el contrato del compiler receiver: nombre del canal, tamaño de estructura, campos, validaciones y política de memoria. Los offsets 0x38/0x58 del precedente no deben reutilizarse como offsets de 13.52.

## Conclusión

La evidencia nueva más prometedora es que hay **dos rutas históricas posteriores o alternativas** que no dependen literalmente de `sunjce`: deserialización privilegiada con construcción de `ClassLoader`, y `Provider.Service`/`ProviderAdapter` para instanciación reflexiva restringida. Ambas pueden explicar una variante si Sony parcheó Ixc pero dejó otro gadget Java; ninguna está demostrada en 13.52.

El contrato JIT/compiler-agent sigue siendo la ruta con mayor probabilidad histórica hacia native usermode, pero depende de una interfaz nativa y de validaciones no disponibles sin runtime. El nested-JAR queda descartado como explicación directa de 13.52 por su rango público 13.00–13.02.

No se ha demostrado ninguna primitive nueva de PS4 13.52. El siguiente experimento seguro es estático: conseguir un inventario autorizado de clases/firmas o un diff de runtime que permita comprobar las dos familias nuevas (`ObjectStreamClass`/deserialización y `com.oracle.security.Service`/ProviderAdapter) antes de considerar cualquier transición Java→native.

## Referencias

[1]: https://hackerone.com/reports/1379975 — PlayStation report #1379975, bd-j exploit chain.

[2]: https://hackerone.com/reports/3104356 — PlayStation report #3104356, BD-J sandbox escape via Ixc.

[3]: https://hackerone.com/reports/3452696 — PlayStation report #3452696, nested-JAR privilege escalation.

[4]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 — OpenJDK commit 8180024, construction during deserialization.

[5]: https://docs.oracle.com/javase/8/docs/api/java/security/Provider.Service.html — Java SE 8 `Provider.Service`.

[6]: https://docs.oracle.com/javase/8/docs/api/java/io/ObjectInputStream.html — Java SE 8 `ObjectInputStream`.

[7]: https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/security/AccessController.html — Java SE `AccessController` semantics.

[8]: https://github.com/advisories/GHSA-87pc-67c4-x49w — CVE-2025-64390/GHSA-87pc-67c4-x49w.

[9]: https://consolemods.org/wiki/PS4:BD-JB — ConsoleMods BD-JB status and public firmware range.

[10]: https://elhacker.info/Books/BOOKS%20PART%206/hardwear_io_bd_jb-.pdf — Public BD-JB presentation by TheFlow.
