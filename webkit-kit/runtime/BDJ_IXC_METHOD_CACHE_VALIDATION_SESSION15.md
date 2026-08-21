# Auditoría independiente: Ixc → `findMethod` → `Method` cacheado

## Alcance y conclusión

Esta auditoría se centra exclusivamente en la frontera entre los descriptores simbólicos recibidos por `findMethod`, el objeto `java.lang.reflect.Method` que devuelve el callback y el método que queda cacheado y se ejecuta posteriormente. Se utilizó el historial de `webkit-ps4-1352-kit` y el checkout público local de `TheOfficialFloW/bd-jb`.

No se ejecutaron exploits, payloads, JAR, ELF/BIN ni código contra hardware. No se buscaron runtime privado, PUPs ni dumps.

La conclusión estricta es:

> El corpus público demuestra una **asimetría histórica potencial** entre la solicitud simbólica y el objeto `Method` retornado, almacenado y ejecutado bajo `doPrivileged`. No demuestra que la implementación histórica completa careciera de validaciones privadas adicionales y no aporta evidencia de que la misma frontera exista en PS4 13.52.

Estado final específico 13.52: **UNVERIFIED**. No hay evidencia `DIRECT_13.52` ni `INDIRECT_13.52` suficiente.

## Fuentes locales y rutas verificables

| Archivo | Evidencia observable | Clasificación |
|---|---|---|
| `evidence/bd-jb-src/src/com/bdjb/exploit/sandbox/IxcProxyImpl.java:15-49` | Subclase de `IxcProxy`; obtiene `CoreIxcClassLoader`; guarda `remote`; llama `super.invokeMethod(args, name, signature)` | `HISTORICAL_ONLY` |
| `evidence/bd-jb-src/src/com/bdjb/exploit/sandbox/ExploitServiceProxyImpl.java:31-60` | Construye un servicio, invoca `proxy.invokeMethod(service, NEW_INSTANCE_METHOD_NAME, NEW_INSTANCE_METHOD_SIGNATURE, ...)`, recibe un `URLClassLoader`, carga una clase y la instancia | `HISTORICAL_ONLY` |
| `webkit-kit/runtime/BDJ_IXC_VALIDATION_DISCREPANCY_REASSESSMENT.md:17-24` | Resume el callback `findMethod`, el almacenamiento del retorno y la invocación posterior desde `com_sun_xlet_execute` | `HISTORICAL_ONLY` |
| `webkit-kit/runtime/BDJ_IXC_VALIDATION_DISCREPANCY_REASSESSMENT.md:63-75` | Identifica los dos puntos de control: retorno antes de la caché e invocación antes de `Method.invoke` | `HISTORICAL_ONLY / HYPOTHESIS` |

El cliente local no contiene el cuerpo de `IxcProxy`, `IxcProxyBuilder`, `IxcClassLoader`, `WrappedRemote` ni el callback interno del runtime. La presencia de nombres y wrappers no prueba su implementación en 13.52.

## Flujo histórico reconstruido

```text
Xlet / objeto Remote
  → IxcProxyBuilder produce o registra proxy
  → IxcClassLoader genera/selecciona stub
  → WrappedRemote recibe descriptores simbólicos
  → com_sun_xlet_init invoca findMethod
  → callback devuelve java.lang.reflect.Method
  → el stub almacena el retorno en una caché
  → com_sun_xlet_execute recupera el Method
  → remoteMethod.invoke(targetNow, args) dentro de doPrivileged
```

La superficie relevante no es solamente la existencia de `findMethod`. La propiedad crítica es si el método retornado se vincula semánticamente con la solicitud antes de almacenarse y, de nuevo, antes de ejecutarse.

## Invariantes que una mitigación completa debería comprobar

| Propiedad del resultado | Comprobación necesaria antes de cachear/ejecutar |
|---|---|
| Clase declarada | `Method.getDeclaringClass()` pertenece a la clase/interfaz solicitada o a una relación autorizada explícita |
| Nombre | `Method.getName()` coincide con el nombre pedido |
| Firma | `getParameterTypes()` y tipo de retorno coinciden con el descriptor solicitado |
| Modificadores | `public`, instancia/estático, finalidad y demás restricciones son compatibles |
| Loader | El `ClassLoader` pertenece al contexto autorizado y no a un loader inesperado |
| Origen | `CodeSource`/`ProtectionDomain` son compatibles con la política del proxy |
| Target | `targetNow` es instancia compatible con `getDeclaringClass()` |
| Permisos | La invocación privilegiada no amplía el contexto respecto al método validado |
| Ciclo de vida | `destroy` invalida todas las referencias cacheadas y no sólo un campo visible |
| Concurrencia | No existe sustitución entre validación, almacenamiento e invocación |

El corpus público histórico documenta requisitos de elegibilidad Ixc, como interfaces `Remote`, métodos que declaran `RemoteException` y checks de call stack/prefijos. Estos requisitos validan el canal y su origen estructural; no demuestran por sí solos la igualdad entre descriptor simbólico y `Method` retornado.

## Qué demuestra el corpus y qué no

El ejemplo público muestra que `findMethod` recibe descriptores de búsqueda y puede devolver un `Method` distinto del nombre solicitado en el stub ilustrativo. Después, ese objeto es el que se almacena y se utiliza. La evidencia permite formular una hipótesis de desalineación:

```text
request(class, name, signature)
  ≠ returned Method
  → cache(returned Method)
  → privileged invoke(returned Method)
```

La formulación correcta es limitada: el callback es la fuente del objeto ejecutado y el corpus no muestra una comparación post-callback. Esto no prueba que no exista una comprobación privada en el runtime histórico completo.

El cliente `IxcProxyImpl` local tampoco es una prueba de ausencia de validación. Su función es construir una subclase cliente y delegar en `super.invokeMethod`; la lógica de `findMethod`, la caché y `WrappedRemote` están en clases externas no incluidas.

## Mitigaciones históricas conocidas

| Mitigación | Frontera cubierta | Limitación observable | Clasificación |
|---|---|---|---|
| Check de call stack en `IxcProxy` | Origen estructural de la llamada | No fija la identidad semántica del `Method` | `HISTORICAL_ONLY` |
| Prefijos de paquetes Ixc | Elegibilidad del caller/proxy | Un proxy generado puede cumplir el patrón | `HISTORICAL_ONLY` |
| `Remote`/`RemoteException` | Forma de la interfaz remota | No demuestra validación del resultado de `findMethod` | `HISTORICAL_ONLY` |
| Limpieza de referencias en `destroy` | Parte del ciclo de vida | No demuestra invalidación de copias, closures o carreras | `HISTORICAL_ONLY` |
| Revalidación de clase, firma, loader, origen y target | Identidad efectiva del método | No aparece publicada en el corpus consultado | `HYPOTHESIS` como requisito; existencia 13.52 `UNVERIFIED` |

No se encontró una implementación pública posterior que documente específicamente una comparación completa entre el `Method` retornado y los descriptores solicitados. Tampoco se encontró un diff público que vincule ese cambio con PS4 13.50 o 13.52.

## Evidencia 13.50–13.52

No se encontró evidencia específica de una revisión de `IxcProxy`, `IxcProxyBuilder`, `IxcClassLoader`, `WrappedRemote`, `com_sun_xlet_init`, `com_sun_xlet_execute` o `findMethod` para 13.50–13.52.

| Afirmación | Clasificación |
|---|---|
| Ixc histórico tuvo una frontera de call stack/proxy insuficiente | `HISTORICAL_ONLY` |
| El `Method` retornado por el callback podía terminar en la caché y ser invocado privilegiadamente | `HISTORICAL_ONLY` |
| Existe una validación completa post-callback en 13.52 | `UNVERIFIED` |
| No existe ninguna validación post-callback en 13.52 | `UNVERIFIED` |
| Sony cambió la caché o la semántica de `findMethod` entre 13.50 y 13.52 | `UNVERIFIED` |
| La demo BD-J pública de 13.52 usa esta superficie | `DISCARDED` como afirmación no demostrada |

## Primer punto no verificado

El primer punto no verificado es inmediatamente después de que el runtime invoque el callback `findMethod` y antes de asignar el resultado a la caché:

```java
Method m = (Method) findMethodCallback(...);
// ¿validación semántica completa?
cachedMethod = m;
```

El segundo punto es justo antes de `remoteMethod.invoke(targetNow, args)`. Una revalidación allí también rompería la hipótesis de desalineación. El corpus no demuestra ninguna de las dos en 13.52.

## Dato mínimo faltante

Para confirmar o descartar la mitigación en 13.52 se necesita una fuente de esa build —código público, decompilación autorizada, inventario de firmas o log técnico— que revele:

1. el cuerpo de `IxcProxyBuilder` e `IxcClassLoader`;
2. `WrappedRemote` y los campos de caché;
3. `com_sun_xlet_init` y `com_sun_xlet_execute`;
4. el callback real `findMethod`;
5. cualquier comparación de clase, nombre, firma, modificadores, loader, `CodeSource`, `ProtectionDomain`, target y permisos;
6. invalidación de la caché durante `destroy` y sincronización entre validación e invocación.

Un nombre de clase, una demo “Hello World” o la mera existencia histórica de Ixc no bastan.

## Conclusión

La evidencia estática independiente confirma sólo una **hipótesis histórica de desalineación**: los descriptores simbólicos y el `Method` ejecutado son representaciones distintas, y la documentación pública no expone una revalidación que las vincule. El cliente local `bd-jb` prueba el uso histórico del proxy y la delegación, pero no implementa ni demuestra la lógica completa del runtime.

Para PS4 13.52, la conclusión correcta es **UNVERIFIED**. No se encontró ninguna diferencia real atribuible a 13.52 ni evidencia `DIRECT_13.52`/`INDIRECT_13.52`.

## Referencias

[1]: https://hackerone.com/reports/3104356 "HackerOne #3104356, Blu-ray Disc Java Sandbox Escape via two vulnerabilities"
[2]: https://hackerone.com/reports/1379975 "HackerOne #1379975, bd-j exploit chain"
[3]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer Wiki, vulnerabilities"
[4]: https://github.com/TheOfficialFloW/bd-jb "TheOfficialFloW bd-jb public repository"
[5]: https://www.psx-place.com/threads/update-2-thefl0w-discloses-blu-ray-disc-java-sandbox-escape-vulnerabilities-ps3-ps4-ps5.37554/ "Public discussion of BD-J disclosures"
