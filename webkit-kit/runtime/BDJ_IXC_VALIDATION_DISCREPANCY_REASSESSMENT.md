# Revisión focalizada de la frontera Ixc `findMethod` → `Method`

**Autor:** Manus AI  
**Corpus:** informes y fuentes públicas ya incorporados al repositorio.  
**Restricciones:** no se buscaron PUPs, dumps, runtime privado ni artefactos protegidos; no se ejecutaron exploits, payloads, JAR/ELF/BIN ni hardware.

## Conclusión

El corpus público demuestra una **asimetría histórica de validación**: los descriptores que recibe `findMethod` son datos simbólicos —clase/interfaz, nombre y tipos—, mientras que el objeto que el stub almacena es un `java.lang.reflect.Method` retornado por el callback. La fuente pública muestra el almacenamiento y posterior uso privilegiado de ese objeto, pero no publica una comprobación posterior que fuerce la igualdad entre ambas representaciones.

Eso permite formular una **debilidad histórica de validación** como hipótesis: si el callback devuelve un `Method` distinto del descrito y el consumidor lo acepta sin volver a verificarlo, la identidad efectiva del método ejecutado no está fijada por la solicitud original. La evidencia pública del informe HackerOne #3104356 incluso muestra un callback que devuelve un método distinto del nombre solicitado en el stub de ejemplo. Sin embargo, el corpus no incluye las implementaciones completas de `IxcProxyBuilder`, `IxcClassLoader` o `WrappedRemote`, por lo que no permite probar que no hubiera validaciones privadas adicionales.

No existe evidencia específica de PS4 13.52. El resultado para esa versión es **`UNVERIFIED`** y no `DIRECT_13.52`.

## Cadena y puntos de control

| Etapa | Operación observable en el corpus | Validación demostrada | Validación no demostrada |
|---|---|---|---|
| `IxcProxy` | Obtiene el call stack bajo `AccessController.doPrivileged`. | Busca el frame `IxcProxy` y acepta prefijos concretos en el siguiente frame. | Clase declarada del método, `CodeSource`, loader y relación con el target. |
| `IxcProxyBuilder` | Produce proxies reales considerados elegibles por Ixc. | Interfaz `Remote` y métodos con `RemoteException` aparecen como requisitos históricos. | Firma completa del proxy, origen, loader y validación del método que resolverá el stub. |
| `IxcClassLoader` | Genera un stub derivado de `WrappedRemote`. | La relación de herencia y generación se muestra en el informe público. | Restricciones de definición, `ProtectionDomain`, `CodeSource` y verificaciones post-generación. |
| `com_sun_xlet_init` | Invoca `findMethod` con descriptores simbólicos y guarda el retorno como `Method`. | El retorno se convierte en `Method` y se cachea. | Comparación posterior de clase, nombre, firma, loader u origen. |
| `com_sun_xlet_execute` | Usa `remoteMethod.invoke(targetNow,args)` dentro de `doPrivileged`. | Invocación reflectiva privilegiada del objeto cacheado. | Revalidación del `Method`, target o permisos justo antes de `invoke`. |
| `destroy` | Limpia las referencias de método mostradas. | Se observa la puesta a `null` de la caché de ejemplo. | Invalidación de copias, concurrencia y referencias retenidas por otros objetos. |

## Validaciones históricas demostradas

### Interfaz y firma remota

El informe #3104356 indica que la elegibilidad histórica para registrar un objeto en Ixc requiere una interfaz que extienda `java.rmi.Remote`. También indica que los métodos invocables deben declarar `java.rmi.RemoteException`. Estas condiciones limitan la superficie de proxies e interfaces, pero no prueban que el `Method` que devuelve el callback pertenezca a esa interfaz.

### Call stack

La mitigación de `IxcProxy` inspecciona el stack y permite la llamada si encuentra su propio nombre y un siguiente frame con prefijo `org.dvb.io.ixc.` o `com.sony.gemstack.org.dvb.io.ixc.`. Es una validación del **camino de llamada**, no una validación de la identidad semántica del `Method` que queda en la caché.

El mismo informe afirma que los proxies generados por `IxcProxyBuilder` aún pueden superar esa mitigación. Esto demuestra una insuficiencia histórica de la frontera de call stack, pero no proporciona el cuerpo completo de la implementación para enumerar todos sus invariantes.

### Método, clase declarada y modificadores

El ejemplo público de `findMethod` devuelve un método real distinto de los descriptores simbólicos recibidos. El corpus no muestra una comprobación posterior de:

| Propiedad | ¿Aparece una validación post-callback en el corpus? |
|---|---|
| `Method.getDeclaringClass()` | No demostrada. |
| `Method.getName()` | No demostrada. |
| `Method.getParameterTypes()` | No demostrada. |
| `public`/`static`/`final` | Sólo aparecen restricciones de la interfaz/método remoto en la descripción histórica; no una revalidación del objeto retornado. |
| `ClassLoader` | No demostrada. |
| `ProtectionDomain`/`CodeSource` | No demostrada. |
| Compatibilidad de `targetNow` | No demostrada antes de `invoke`. |
| Permisos del método | La ejecución ocurre dentro de `doPrivileged`, pero no se publica una comprobación semántica posterior. |

La ausencia aquí significa “no aparece en la evidencia pública consultada”, no “se ha probado que no exista en la implementación histórica completa”.

## ¿Puede `findMethod` devolver otro método?

**Históricamente, sí existe evidencia pública de esa posibilidad en el material del informe.** El callback recibe los descriptores de una búsqueda y el ejemplo publicado muestra que puede retornar otro `Method`; luego ese retorno es el que se almacena y se utiliza. La condición necesaria para que esto constituya una debilidad es que el runtime confíe en el retorno sin comparar sus propiedades con la solicitud.

La afirmación precisa y limitada es:

> El corpus demuestra una ruta de datos donde la solicitud y el objeto ejecutado son valores distintos y donde el objeto ejecutado procede del callback. No demuestra que las implementaciones completas carezcan de toda comprobación adicional.

## Primer punto de ruptura

El primer punto de ruptura de la hipótesis está entre estas dos operaciones:

```text
Method m = (Method) findMethodMethod.invoke(...);
// validación requerida aquí
cachedMethod = m;
```

Una validación que compruebe clase declarada, nombre, firma, loader, origen, modificadores, target y contexto de permisos descartaría la variante de desalineación. Si sólo existe el filtro de call stack y los requisitos `Remote`/`RemoteException`, esos filtros no fijan por sí solos la identidad del método cacheado.

El segundo punto de ruptura está inmediatamente antes de `remoteMethod.invoke(targetNow,args)`. Una revalidación allí también impediría que una caché incorrecta alcance la invocación privilegiada. El corpus no muestra ninguna.

## Diferencias entre variantes públicas

No apareció una implementación pública completa alternativa de estos nombres exactos. El corpus público disponible se compone principalmente de los fragmentos de HackerOne #3104356 y sus reproducciones/documentación secundaria. Por tanto, no existe una comparación fiable de versiones que permita afirmar un cambio de `IxcProxyBuilder`, `IxcClassLoader`, `WrappedRemote` o `findMethod`.

Las mitigaciones conocidas afectan principalmente al call stack y a la elegibilidad Ixc. No se encontró una mitigación pública posterior que documente explícitamente la comparación `Method`-solicitud, el sellado del callback o una asociación obligatoria entre caché, loader y target.

## Evidencia específica de 13.52

No se encontró evidencia `DIRECT_13.52` ni `INDIRECT_13.52` suficientemente fuerte. Las demostraciones públicas de BD-J userland en 13.52 no publican estas clases, el callback, los campos de caché ni las comprobaciones de método. Una salida Java observable no demuestra que esta frontera Ixc exista o conserve su semántica.

| Hallazgo | Clasificación |
|---|---|
| Requisitos históricos `Remote`/`RemoteException` | `HISTORICAL_ONLY` |
| Call-stack check en `IxcProxy` | `HISTORICAL_ONLY` |
| Proxies generados que superan la mitigación histórica | `HISTORICAL_ONLY` |
| Callback `findMethod` como fuente del `Method` cacheado | `HISTORICAL_ONLY` |
| Revalidación post-callback no mostrada en el corpus | `HISTORICAL_ONLY / HYPOTHESIS` |
| Desalineación persistente en 13.52 | `UNVERIFIED` |
| Cambio concreto de 13.50→13.52 | `UNVERIFIED` |
| Atribución `DIRECT_13.52` | `DISCARDED` por falta de evidencia |

## Dato mínimo para confirmar o descartar la variante en 13.52

Se necesita, para una misma build 13.52, una decompilación, código, inventario de firmas o log técnico que revele: el cuerpo de `IxcProxyBuilder` e `IxcClassLoader`; el código de `com_sun_xlet_init` y `com_sun_xlet_execute`; la implementación real de `findMethod`; y cualquier comparación post-callback de clase, firma, loader, origen, target y permisos.

Un simple nombre de clase, una demo “Hello World”, el hecho de que BD-J arranque o la existencia histórica de Ixc no serían suficientes.

## Conclusión final

La hipótesis histórica está bien delimitada: **la solicitud simbólica de `findMethod` y el `Method` que se cachea/ejecuta son objetos distintos, y el corpus público no muestra una revalidación que los vincule**. La primera frontera relevante es el retorno del callback antes de la caché; la segunda es la invocación desde `WrappedRemote` antes de `Method.invoke`.

Esto constituye una **hipótesis histórica de debilidad de validación**, no una demostración de PS4 13.52. La clasificación final para 13.52 permanece **`UNVERIFIED`**.

## Referencias

[1]: https://hackerone.com/reports/3104356 — HackerOne #3104356, “Blu-ray Disc Java Sandbox Escape via two vulnerabilities”.

[2]: https://hackerone.com/reports/1379975 — HackerOne #1379975, “bd-j exploit chain”.

[3]: https://www.psdevwiki.com/ps4/Vulnerabilities — PS4 Developer Wiki, índice y resúmenes históricos de BD-J.

[4]: https://www.psx-place.com/threads/update-2-thefl0w-discloses%22blu-ray-disc-java-sandbox-escape-vulnerabilities-ps3-ps4-ps5.37554/ — discusión pública histórica de la cadena BD-J.
