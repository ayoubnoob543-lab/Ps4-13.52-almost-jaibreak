# Cadena BD-J histórica: Ixc → callback privilegiado → ProviderAdapter → Service.newInstance → reflection

## Alcance

Este informe usa únicamente documentación y código público. No usa PUPs, dumps, firmware privado ni artefactos retail no autorizados. No ejecuta exploits, payloads, JAR/ELF/BIN ni código contra hardware.

Las clasificaciones son `DIRECT_13.52`, `INDIRECT_13.52`, `HISTORICAL_ONLY`, `HYPOTHESIS` y `DISCARDED`. Cuando no existe evidencia de 13.52 se indica explícitamente `UNVERIFIED`.

## 1. `IxcProxy`, `IxcProxyImpl` y `IxcProxyBuilder`

El informe público HackerOne #3104356 documenta dos implementaciones de Ixc: `org.dvb.io.ixc` y `com.sun.xlet.ixc`. Para la primera, `com.sony.gemstack.org.dvb.io.ixc.IxcProxy` ejecuta la comprobación de call-stack bajo `AccessController.doPrivileged`. La mitigación histórica busca el nombre de `IxcProxy` en el stack y exige que la clase siguiente comience por `org.dvb.io.ixc.` o `com.sony.gemstack.org.dvb.io.ixc.`.

El mismo informe afirma que la comprobación no bloquea los proxies generados por `com.sony.gemstack.org.dvb.io.ixc.IxcProxyBuilder`. La condición histórica para registrar un objeto en Ixc es que su clase implemente una interfaz que extienda `java.rmi.Remote`; los métodos invocables deben declarar `java.rmi.RemoteException`.

`IxcProxyImpl` no aparece como una implementación pública separada en las fuentes consultadas. El nombre verificable es `IxcProxy` y la referencia a `IxcProxyBuilder`; no se deben inventar firmas adicionales para `IxcProxyImpl`.

| Elemento | Qué demuestra históricamente | Estado 13.52 |
|---|---|---|
| `IxcProxy` | Callback/invocación bajo contexto privilegiado y validación de stack. | `HISTORICAL_ONLY / UNVERIFIED` |
| `IxcProxyBuilder` | Proxy generado que pasa la mitigación basada en prefijo de clase. | `HISTORICAL_ONLY / UNVERIFIED` |
| Interfaces `Remote` | Criterio de elegibilidad Ixc. | `HISTORICAL_ONLY / UNVERIFIED` |
| `RemoteException` | Criterio histórico para métodos invocables. | `HISTORICAL_ONLY / UNVERIFIED` |
| `IxcRegistryImpl` | Clase bootstrap con checks de `IxcPermission`. | `HISTORICAL_ONLY / UNVERIFIED` |

## 2. `WrappedRemote`, callbacks y control de call-stack

En la implementación `com.sun.xlet.ixc`, `WrappedRemote.com_sun_xlet_execute` invoca un `Method` cacheado mediante `remoteMethod.invoke(targetNow, args)` dentro de `AccessController.doPrivileged`. El stub generado por `com.sun.xlet.ixc.IxcClassLoader` hereda de `WrappedRemote`, implementa la interfaz remota y almacena métodos estáticos obtenidos mediante un callback `findMethod`.

El ciclo histórico publicado contiene:

```text
com_sun_xlet_init(Method findMethodMethod)
    → invocación reflectiva del callback
    → cache de Method
com_sun_xlet_execute(Method, args)
    → remoteMethod.invoke(targetNow, args) dentro de doPrivileged
com_sun_xlet_destroy()
    → limpia la cache
```

La vulnerabilidad histórica aparece porque el callback `findMethod` puede devolver un método distinto del que el stub pretendía resolver. El informe muestra una sustitución conceptual por `System.setSecurityManager`, seguida de una llamada remota que lo ejecuta con argumento `null`.

El primer eslabón potencialmente roto en 13.52 es **la relación entre el stub generado, el callback `findMethod` y la aceptación del método devuelto**. Si Sony selló el callback, verificó que el `Method` pertenece a la clase/interfaz solicitada, invalidó la cache o eliminó la ruta privilegiada, la cadena se detiene antes de `ProviderAdapter` y `Service.newInstance`.

Clasificación: `HISTORICAL_ONLY`; no hay evidencia pública específica 13.52.

## 3. `ProviderAdapter.setProviderAccessor`

HackerOne #1379975 documenta que `com.oracle.security.Service.newInstance` llama `Class.forName` sobre un nombre de clase arbitrario. La validación de servicio registrado consulta `ProviderAdapter.getService(provider, type, algorithm)`. El informe afirma que la comprobación puede eludirse usando `ProviderAdapter.setProviderAccessor` con una implementación personalizada de `ProviderAccessor`.

El contrato histórico puede resumirse como:

```text
ProviderAdapter.setProviderAccessor(customAccessor)
    → ProviderAdapter.getService(...) usa el accessor instalado
    → Service considera registrado el objeto/proveedor
    → Service.newInstance(argument)
    → Class.forName(className)
    → constructor público de un argumento
```

La documentación pública no proporciona una matriz completa de quién puede invocar `setProviderAccessor`, si existe un singleton, si la instalación es única, qué sincronización usa ni qué filtros posteriores se ejecutan. Por tanto, no es válido afirmar que cualquier Xlet pueda instalarlo, ni que la misma API exista en 13.52.

Clasificación: `HISTORICAL_ONLY / UNVERIFIED`.

## 4. `Service.newInstance`, `ServiceImpl` y `ServiceInterface`

El nombre verificable en el informe es `com.oracle.security.Service`. No apareció una implementación pública independiente con los nombres exactos `ServiceImpl` o `ServiceInterface` que permita atribuirles firmas concretas.

La primitiva histórica es instanciación reflectiva de clases restringidas que tengan un constructor público compatible. Esto puede alcanzar clases internas Java, pero no proporciona por sí mismo un entrypoint nativo. Requiere primero superar la validación de registro y disponer de una clase/cargador que pueda resolver el nombre.

| Componente | Evidencia | Clasificación |
|---|---|---|
| `com.oracle.security.Service.newInstance` | Publicado en #1379975; usa `Class.forName` sobre el nombre de clase. | `HISTORICAL_ONLY` |
| `ProviderAdapter.setProviderAccessor` | Publicado como forma de sustituir el accessor de validación. | `HISTORICAL_ONLY` |
| `ServiceImpl` | No encontrado como fuente pública verificable. | `UNVERIFIED` |
| `ServiceInterface` | No encontrado como fuente pública verificable. | `UNVERIFIED` |
| Reflection/`Class.forName` | Flujo histórico explícito. | `HISTORICAL_ONLY` |

## 5. Reflection, URLClassLoader y XletClassLoader

La reflexión histórica interviene en dos lugares: el callback Ixc que resuelve `Method`, y `Service.newInstance` que resuelve una clase mediante `Class.forName`. `IxcClassLoader` genera stubs y `XletClassLoader` aparece como componente de classloading en el ecosistema BD-J, pero las fuentes públicas consultadas no demuestran una ruta 13.52 ni publican un diff de sus validaciones.

`URLClassLoader` es una abstracción Java histórica, no evidencia de que BD-J 13.52 permita cargar URLs arbitrarias. El hecho de que exista una clase en Java SE no demuestra que esté presente, accesible o autorizada en el runtime Sony.

## 6. Mitigaciones conocidas y comparación pública

La mitigación histórica de `IxcProxy` añade un control de call-stack, pero el propio informe #3104356 afirma que no valida suficientemente los proxies generados por `IxcProxyBuilder`. El segundo fallo explota el callback `findMethod` y la ejecución privilegiada de `WrappedRemote`.

Las fuentes públicas no aportan un parche posterior que indique cómo PS4 13.52 cambió:

- los prefijos aceptados en el call-stack;
- la generación de proxies;
- la firma o visibilidad de `WrappedRemote.com_sun_xlet_execute`;
- la validación del `Method` devuelto por `findMethod`;
- el ciclo `init/destroy` y la cache estática;
- `ProviderAdapter.setProviderAccessor`;
- el estado de registro exigido por `Service.newInstance`.

Las páginas secundarias consultadas corroboran el texto público de HackerOne, pero no aportan una implementación independiente ni un diff 13.52. Por ello se clasifican como corroboración documental, no como evidencia directa de firmware.

## 7. Primer eslabón potencialmente roto

El primer eslabón con mayor probabilidad de diferir o romperse en 13.52 es el **callback de resolución de métodos dentro del stub Ixc**, antes de `ProviderAdapter`:

```text
stub generado
→ findMethod callback
→ Method cacheado
→ WrappedRemote.com_sun_xlet_execute
→ doPrivileged
```

La razón es estructural: la cadena depende de que un callback externo pueda devolver un `Method` cuyo propietario/firma no coincida con la búsqueda solicitada. Una mitigación mínima podría verificar la clase declarada, la firma, el origen del callback o el stack; también podría eliminar el callback sustituible. Si ese punto está corregido, `ProviderAdapter` y `Service.newInstance` dejan de ser relevantes para esta cadena concreta.

La segunda frontera es `ProviderAdapter.setProviderAccessor`: aunque Ixc funcione, la cadena requiere que el accessor global siga siendo instalable o sustituible y que `Service` confíe en él. No hay evidencia pública de 13.52 para ninguna de las dos condiciones.

## Tabla final de clasificación

| Hallazgo | Clasificación |
|---|---|
| `IxcProxy` y callback privilegiado | `HISTORICAL_ONLY` |
| Call-stack check y bypass mediante proxy generado | `HISTORICAL_ONLY` |
| `WrappedRemote` + `findMethod` + `doPrivileged` | `HISTORICAL_ONLY` |
| `ProviderAdapter.setProviderAccessor` como bypass de registro | `HISTORICAL_ONLY` |
| `Service.newInstance` + `Class.forName` | `HISTORICAL_ONLY` |
| `ServiceImpl`/`ServiceInterface` concretos | `UNVERIFIED` |
| Persistencia de cualquier elemento en 13.52 | `UNVERIFIED` |
| Primer eslabón potencialmente roto: callback/stub Ixc | `HYPOTHESIS` |

## Conclusión

La cadena histórica no demuestra que PS4 13.52 conserve ninguna de estas clases o semánticas. El punto de mayor valor para discriminar una variante posterior, sin estudiar aún native/JIT/kernel, es la frontera **stub generado → `findMethod` → `WrappedRemote.com_sun_xlet_execute`**. Si la implementación 13.52 valida el `Method`, bloquea callbacks externos o cambia la generación de stubs, la cadena se rompe allí. Si ese punto sobrevive, la siguiente frontera a comprobar es la instalación global de `ProviderAccessor` y la validación de registro de `Service`.

El artefacto mínimo que falta para pasar de `HISTORICAL_ONLY` a `DIRECT_13.52` es código, decompilación, inventario de firmas o log del runtime 13.52 que revele esos métodos y sus validaciones. Sin ello, el resultado correcto es **UNVERIFIED**, no compatibilidad inferida.

## Referencias

[1]: https://hackerone.com/reports/3104356 — PlayStation report #3104356, Blu-ray Disc Java Sandbox Escape via two vulnerabilities.

[2]: https://hackerone.com/reports/1379975 — PlayStation report #1379975, bd-j exploit chain.

[3]: https://www.psdevwiki.com/ps4/Vulnerabilities — PS4 Developer Wiki, vulnerability summaries and patch ranges.

[4]: https://habr.com/ru/articles/671088/ — Independent translation/reproduction of the 2022 BD-J chain.

[5]: https://www.psx-place.com/threads/update-2-thefl0w-discloses%22blu-ray-disc-java-sandbox-escape-vulnerabilities-ps3-ps4-ps5.37554/ — Public discussion and reproduction of the disclosed chain.
