# Frontera Ixc: `findMethod` → `Method` cacheado → `doPrivileged`

**Autor:** Manus AI  
**Alcance:** análisis estático de código/documentación pública e informes ya disponibles en el repositorio. No se buscaron PUPs, dumps privados ni runtime propietario; no se ejecutaron exploits, payloads, JAR/ELF/BIN ni acciones contra hardware.

## Conclusión ejecutiva

La evidencia histórica pública sí muestra una frontera semántica concreta: el stub generado recibe descriptores de método (`cName`, `mName`, tipos), delega su resolución en un callback `findMethod` y almacena el objeto `Method` que devuelve el callback. Más tarde, `WrappedRemote.com_sun_xlet_execute` invoca ese objeto cacheado dentro de `AccessController.doPrivileged`.

En el material público revisado no aparece una validación posterior que compruebe que el `Method` devuelto pertenece a la clase solicitada, conserva el mismo nombre y firma, procede del `ClassLoader` esperado, tiene el origen/`CodeSource` esperado, es compatible con el `target` o satisface los mismos permisos. Por ello, **históricamente existe una posible desalineación entre la solicitud simbólica y el objeto reflectivo ejecutado**. La fuente primaria no aporta, sin embargo, una implementación completa de `IxcProxyBuilder`, `IxcClassLoader` o `WrappedRemote` que permita convertir esa ausencia de validación publicada en una prueba formal de que ninguna comprobación existía.

No hay evidencia específica de PS4 13.52. El resultado correcto para 13.52 es `UNVERIFIED`; no se clasifica ningún elemento como `DIRECT_13.52`.

## 1. Cadena histórica reconstruida

### 1.1 `IxcProxy`

HackerOne #3104356 documenta que `com.sony.gemstack.org.dvb.io.ixc.IxcProxy` obtiene el call stack mediante `AccessController.doPrivileged`. La mitigación histórica busca una entrada cuyo nombre sea `com.sony.gemstack.org.dvb.io.ixc.IxcProxy` y permite el siguiente frame si comienza por `org.dvb.io.ixc.` o `com.sony.gemstack.org.dvb.io.ixc.`.

El informe afirma que esa mitigación no basta para los proxies reales generados por `IxcProxyBuilder`. Históricamente, la elegibilidad Ixc exige una interfaz que extienda `java.rmi.Remote` y métodos que declaren `java.rmi.RemoteException`.

La validación demostrada es, por tanto, principalmente una validación de **forma del proxy y del call stack**. No se demuestra en la fuente que esa validación se propague al `Method` que un stub generado cachea posteriormente.

### 1.2 `IxcProxyBuilder`

La fuente pública no contiene la implementación completa ni una firma detallada de `IxcProxyBuilder`. Sí afirma que un proxy generado por esta clase puede superar el control de call stack de `IxcProxy`. Esto establece un precedente histórico de separación entre:

```text
objeto/proxy aceptado por la capa Ixc
≠ necesariamente método semánticamente autorizado por el stub
```

La ausencia de código completo impide afirmar qué comprobaciones adicionales realiza el builder sobre clase, interfaces, modificadores, loader, origen o target.

### 1.3 `IxcClassLoader` y `WrappedRemote`

HackerOne #3104356 muestra un stub generado por `com.sun.xlet.ixc.IxcClassLoader` que hereda de `com.sun.xlet.WrappedRemote` e implementa una interfaz remota. El stub contiene métodos estáticos cacheados y dos callbacks de ciclo de vida:

```text
com_sun_xlet_init(Method findMethodMethod)
com_sun_xlet_destroy()
```

`com_sun_xlet_init` recibe una instancia reflectiva que representa `findMethod`. Para cada método del stub, invoca ese callback con descriptores simbólicos —nombre de interfaz, nombre de método y tipos— y convierte el resultado en `Method` para almacenarlo en la caché estática. `com_sun_xlet_destroy` limpia esa caché.

La fuente no muestra una segunda resolución independiente ni una comprobación explícita posterior al callback.

### 1.4 `findMethod` y la caché

El contrato visible es asimétrico:

| Entrada | Salida |
|---|---|
| `cName`, `mName`, matriz de tipos | Un objeto `Method` devuelto por el callback |

La entrada es una descripción simbólica; la salida es un objeto reflectivo concreto. La fuente primaria demuestra que el stub confía en ese retorno para poblar la caché. No demuestra una comparación posterior entre la descripción y propiedades del objeto retornado.

La desalineación histórica potencial aparece aquí:

```text
solicitud simbólica
→ callback findMethod
→ Method retornado
→ cache estática
→ remoteMethod.invoke(targetNow,args)
```

La cuestión técnica no es sólo si el callback puede devolver cualquier objeto, sino si el consumidor verifica que `Method` cumple invariantes equivalentes a la solicitud antes de almacenarlo.

### 1.5 `com_sun_xlet_execute`

La fuente publica el flujo de `WrappedRemote.com_sun_xlet_execute`: el objeto `Method` cacheado se invoca con `remoteMethod.invoke(targetNow, args)` dentro de `AccessController.doPrivileged`. Esto hace que la frontera de autorización quede separada de la frontera de ejecución:

1. `IxcProxy` controla una propiedad del call stack.
2. El stub selecciona/cacha un objeto `Method` mediante `findMethod`.
3. `WrappedRemote` ejecuta ese objeto bajo privilegios.

La fuente no publica una comprobación entre los pasos 2 y 3 de `getDeclaringClass`, firma, loader, `CodeSource`, modificadores, target o permisos.

## 2. Invariantes que deberían existir

Una implementación robusta debería mantener, como mínimo, estas invariantes antes de cachear y antes de ejecutar el método:

| Invariante | Pregunta que debe responder |
|---|---|
| Clase declarada | ¿`Method.getDeclaringClass()` coincide con la interfaz/clase solicitada? |
| Nombre | ¿`Method.getName()` coincide con `mName`? |
| Firma | ¿Los tipos de parámetros coinciden exactamente y en el mismo orden? |
| Modificadores | ¿Es público, no estático y permitido por el contrato Ixc? |
| Loader | ¿La clase/método procede del `ClassLoader` de la interfaz remota esperada? |
| Origen | ¿El `CodeSource`/ProtectionDomain coincide con el origen autorizado? |
| Target | ¿El objeto `targetNow` es instancia compatible con la clase declarada? |
| Call stack | ¿La llamada procede de un proxy y callback autorizados? |
| Ciclo de vida | ¿`destroy` invalida toda referencia cacheada y no sólo campos visibles? |
| Privilegios | ¿La invocación conserva sólo el contexto necesario y no un `doPrivileged` excesivo? |

La evidencia pública sólo demuestra explícitamente partes del contrato `Remote`/`RemoteException`, el control histórico de call stack y la invocación privilegiada. No demuestra el conjunto de invariantes anterior.

## 3. Primer punto exacto donde podría romperse la cadena

El primer punto con mayor valor discriminante es **después del retorno de `findMethod` y antes de asignar el `Method` a la caché**. En ese punto una mitigación puede:

- volver a resolver el método desde la clase autorizada;
- comparar nombre y firma;
- comprobar la clase declarada y el loader;
- comprobar el origen/ProtectionDomain;
- rechazar métodos estáticos, privados o incompatibles;
- ignorar callbacks suministrados por código no confiable;
- asociar la caché a un único `ClassLoader`/target;
- invalidarla durante `destroy` de forma completa.

Si la implementación valida todas esas propiedades, la hipótesis de desalineación queda descartada para esa variante. Si sólo conserva el chequeo del call stack y el resultado simbólico no se compara con el `Method` retornado, la debilidad histórica permanece conceptualmente.

## 4. Qué demuestra y qué no demuestra la fuente primaria

### Demostrado históricamente

HackerOne #3104356 demuestra que:

- existen dos implementaciones históricas de Ixc;
- `IxcProxy` usa un control de call stack bajo `doPrivileged`;
- proxies generados por `IxcProxyBuilder` son relevantes para la insuficiencia de esa mitigación;
- `IxcClassLoader` genera stubs derivados de `WrappedRemote`;
- `com_sun_xlet_init` recibe un callback `findMethod`;
- el callback devuelve `Method` que se almacena;
- `com_sun_xlet_execute` usa `remoteMethod.invoke(targetNow,args)` dentro de `doPrivileged`.

### No demostrado históricamente con el material disponible

No se publica el cuerpo completo de `IxcProxyBuilder`, `IxcClassLoader`, `WrappedRemote` ni el callback interno de resolución. No puede afirmarse que no existiera ninguna validación privada entre retorno, caché e invocación; sólo puede afirmarse que el informe público no la muestra y que el exploit histórico dependía de que la cadena aceptara el método sustituido.

Tampoco se publica una variante posterior con cambios de firma, loader, `CodeSource`, target o cache.

## 5. Comparación con mitigaciones conocidas

La mitigación de `IxcProxy` corrige una propiedad del **origen de la llamada**: busca frames y prefijos. El problema que queda como hipótesis pertenece a la **identidad del método ejecutado**. Son dimensiones diferentes.

| Mitigación | Frontera que cubre | ¿Cubre automáticamente método/cache? |
|---|---|---|
| Prefijo de call stack en `IxcProxy` | Origen estructural de la invocación | No demostrado; la fuente afirma que proxies generados aún pasan. |
| Requisito `Remote`/`RemoteException` | Elegibilidad del proxy/interfaz | No garantiza que el callback retorne el método esperado. |
| Limpieza de `com_sun_xlet_destroy` | Estado de ciclo de vida | No demuestra invalidación de todas las referencias/closures. |
| Comprobación de clase/firma/loader tras `findMethod` | Identidad semántica del método | Sería la mitigación directa; no publicada. |
| Eliminación de `doPrivileged` en `execute` | Contexto de privilegios | Detendría la elevación, pero no hay diff público. |

## 6. Evidencia específica de 13.52

No se encontró evidencia `DIRECT_13.52`. Las referencias documentales a BD-J userland 13.52 no exponen nombres de estas clases, firmas, stack traces, campos de caché ni resultados de validaciones. El hecho de que una demo BD-J produzca salida Java no permite inferir que la frontera Ixc sobreviva.

| Hallazgo | Clasificación |
|---|---|
| Implementación histórica de `IxcProxy` y call-stack check | `HISTORICAL_ONLY` |
| Proxy generado aceptado por la mitigación histórica | `HISTORICAL_ONLY` |
| `findMethod` devuelve/cachea un `Method` y `execute` lo invoca bajo privilegios | `HISTORICAL_ONLY` |
| Ausencia de validación semántica posterior en el código público | `HISTORICAL_ONLY / HYPOTHESIS` |
| Persistencia de la misma frontera en PS4 13.52 | `UNVERIFIED` |
| Cambio concreto de Sony entre 13.50 y 13.52 | `UNVERIFIED` |

## 7. Dato mínimo faltante

Para confirmar o descartar la hipótesis en PS4 13.52 hace falta una fuente de una sola build 13.52 que revele, mediante código, decompilación, inventario de métodos o log técnico:

1. la firma y el cuerpo de `IxcProxyBuilder`/`IxcClassLoader`;
2. la implementación de `com_sun_xlet_init` y `com_sun_xlet_execute`;
3. el callback `findMethod` usado por el runtime;
4. cualquier comparación posterior sobre clase declarada, firma, loader, origen, target y permisos;
5. el comportamiento de `destroy` sobre la caché.

Sin esos datos, el estado correcto es `HISTORICAL_ONLY / HYPOTHESIS`, no `DIRECT_13.52`.

## Conclusión

Históricamente sí existe una **desalineación potencial** entre la solicitud simbólica de `findMethod` y el objeto `Method` que termina en la caché y se ejecuta bajo `doPrivileged`. El primer punto exacto donde la cadena puede romperse es la validación posterior al callback y anterior a la cache; la mitigación de call stack por sí sola no demuestra que cubra esa frontera.

La conclusión no puede trasladarse a PS4 13.52. No se ha encontrado código público que pruebe que el `Method` retornado siga sin validarse, ni código que pruebe la mitigación concreta en esa build. La investigación histórica queda cerrada en **HISTORICAL_ONLY / HYPOTHESIS** y la compatibilidad 13.52 permanece **UNVERIFIED**.

## Referencias

[1]: https://hackerone.com/reports/3104356 — HackerOne #3104356, “Blu-ray Disc Java Sandbox Escape via two vulnerabilities”.

[2]: https://hackerone.com/reports/1379975 — HackerOne #1379975, “bd-j exploit chain”.

[3]: https://www.psdevwiki.com/ps4/Vulnerabilities — PS4 Developer Wiki, resumen de vulnerabilidades BD-J.

[4]: https://www.psx-place.com/threads/update-2-thefl0w-discloses%22blu-ray-disc-java-sandbox-escape-vulnerabilities-ps3-ps4-ps5.37554/ — discusión pública histórica sobre la cadena BD-J.
