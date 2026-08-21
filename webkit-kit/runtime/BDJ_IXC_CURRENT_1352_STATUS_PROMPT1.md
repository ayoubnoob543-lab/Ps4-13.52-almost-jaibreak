# Estado actual de Ixc en PS4 13.52

**Autor:** Manus AI  
**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** sólo el repositorio, su historial y fuentes públicas disponibles. No se buscaron PUPs, dumps privados ni runtime propietario; no se ejecutaron exploits, payloads, JAR/ELF/BIN ni hardware.

## Conclusión

No existe evidencia actual verificable de que las clases `IxcProxy`, `IxcProxyBuilder`, `IxcClassLoader`, `WrappedRemote`, `com_sun_xlet_init`, `com_sun_xlet_execute` o `findMethod` sigan presentes con la semántica histórica en PS4 13.52.

La única referencia pública actual que fija un rango de firmware es el índice de PSDevWiki: la vulnerabilidad Ixc histórica aparece como **“FW <= 12.50 - BD-JB3 - Sandbox escape via Inter-Xlet Communication (ixc)”** y su sección de parches está separada del material sobre 13.52.[1] Esto es evidencia de que la entrada histórica se documenta como afectada hasta 12.50, no evidencia de que Ixc siga vulnerable o siquiera expuesto igual en 13.52.

Por tanto, la conclusión es:

> **No se puede demostrar el estado actual de Ixc en 13.52. La persistencia de la cadena histórica es `UNVERIFIED`; no aparece ningún `DIRECT_13.52` ni `INDIRECT_13.52` fuerte.**

## Auditoría del repositorio

La rama local estaba limpia al inicio y en `HEAD` `2586dab4759ce1381da8bc7a3237dd2ef605c176`. La búsqueda de los nombres exactos sólo encontró informes Markdown, no fuentes Java, clases compiladas, símbolos o decompilaciones de Sony.

Los informes previos son útiles como corpus documental, pero no constituyen una segunda implementación actual. En particular, `BDJ_IXC_VALIDATION_DISCREPANCY_REASSESSMENT.md` documenta la separación histórica entre descriptores simbólicos y el `Method` retornado; sus líneas 1–118 clasifican explícitamente la persistencia en 13.52 como `UNVERIFIED`.

No se encontraron en el repositorio:

| Elemento actual | Resultado |
|---|---|
| Implementación de `IxcProxy` | No encontrada |
| Implementación de `IxcProxyBuilder` | No encontrada |
| Implementación de `IxcClassLoader` | No encontrada |
| Implementación de `WrappedRemote` | No encontrada |
| `com_sun_xlet_init`/`com_sun_xlet_execute` | No encontrados fuera de informes |
| Callback `findMethod` | No encontrado fuera de informes |
| Símbolos/firma de 13.52 | No encontrados |
| Diff 13.50→13.52 de Ixc | No encontrado |

## Evidencia pública específica de firmware

### PSDevWiki

La página pública de vulnerabilidades lista las siguientes entradas relevantes:

- `FW <= 12.50 - BD-JB3 - Sandbox escape via Inter-Xlet Communication (ixc)`.
- `FW <= 13.50 - Path traversal sandbox escape via sunjce JAR signature (untested)`.
- La demostración BD-J userland de 13.52 aparece fuera de la clasificación histórica de Ixc y no publica las clases de esta cadena.

El rango `<= 12.50` de la entrada Ixc es evidencia de un límite histórico documentado. No aporta código de 13.52, hash, firma ni diff posterior.[1]

### Fuentes de la cadena histórica

HackerOne #3104356 y los informes derivados muestran históricamente:

```text
IxcProxy / IxcProxyBuilder
  → IxcClassLoader
  → stub derivado de WrappedRemote
  → com_sun_xlet_init(findMethod)
  → Method cacheado
  → com_sun_xlet_execute
  → remoteMethod.invoke(targetNow,args) dentro de doPrivileged
```

El repositorio conserva esa reconstrucción documental en `BDJ_IXC_METHOD_CACHE_FRONTIER.md` y `BDJ_IXC_VALIDATION_DISCREPANCY_REASSESSMENT.md`. Ninguno de esos archivos contiene bytes o decompilación actual de 13.52.

## Preguntas técnicas solicitadas

### 1. ¿Siguen existiendo Ixc y los callbacks?

No demostrable. La referencia pública de firmware más concreta clasifica el bug histórico Ixc hasta 12.50, pero no ofrece una matriz de presencia de clases para 13.52. Clasificación: **`UNVERIFIED`**.

### 2. ¿Qué validaciones se realizan actualmente antes de aceptar un `Method`?

No hay implementación actual disponible. Históricamente se documentan requisitos `Remote`/`RemoteException` y un control de call stack en `IxcProxy`; no se demuestra una validación post-callback de la clase declarada, nombre, firma, loader, `CodeSource`, `ProtectionDomain`, target o permisos. Para 13.52: **`UNVERIFIED`**.

### 3. ¿Se comprueban clase, nombre, firma, loader, origen, target y permisos?

Para la implementación histórica completa no puede afirmarse un conjunto negativo absoluto, porque el corpus público son fragmentos y writeups. Para 13.52 no existe ninguna evidencia que permita contestar afirmativamente o negativamente. Clasificación: **`UNVERIFIED`**.

### 4. ¿Existe caché y revalidación antes de `invoke`?

El caché y el `invoke` privilegiado están documentados históricamente. No se publica una revalidación posterior visible en el corpus; tampoco hay evidencia de que la misma estructura exista en 13.52. Clasificación: **`HISTORICAL_ONLY`** para la cadena antigua; **`UNVERIFIED`** para 13.52.

### 5. ¿Qué cambió respecto al histórico?

El único cambio públicamente acotado es indirecto: la entrada Ixc aparece con rango histórico `<=12.50`, mientras las referencias posteriores de BD-J 13.52 no nombran Ixc ni sus callbacks. Esto no identifica qué clase, firma o validación cambió. Clasificación: **`INDIRECT_13.52` débil como ausencia de atribución pública**, no como prueba de una modificación concreta.

### 6. ¿Existe una inconsistencia actual demostrable?

No. La inconsistencia método solicitado/`Method` retornado es una hipótesis histórica delimitada, no una inconsistencia actual de 13.52. Clasificación: **`DISCARDED` como afirmación actual demostrada**.

## Matriz de evidencia

| Componente/pregunta | Evidencia 13.52 | Evidencia histórica | Clasificación |
|---|---|---|---|
| `IxcProxy` presente | Ninguna | HackerOne/PSDevWiki; bug listado hasta 12.50 | `HISTORICAL_ONLY / UNVERIFIED` |
| `IxcProxyBuilder` presente | Ninguna | Proxy generado relevante para el bypass histórico | `HISTORICAL_ONLY / UNVERIFIED` |
| `IxcClassLoader` y `WrappedRemote` | Ninguna | Stub y ciclo `init/destroy` documentados | `HISTORICAL_ONLY / UNVERIFIED` |
| `findMethod` | Ninguna | Callback que devuelve y cachea `Method` | `HISTORICAL_ONLY / UNVERIFIED` |
| `com_sun_xlet_execute` | Ninguna | `Method.invoke` dentro de `doPrivileged` | `HISTORICAL_ONLY / UNVERIFIED` |
| Validación de clase/firma/loader/origen | Ninguna | No visible en los fragmentos públicos | `HYPOTHESIS / UNVERIFIED` |
| Cambio 13.50→13.52 | Ningún diff o símbolo | Sólo rangos editoriales y textos de demos | `UNVERIFIED` |
| Inconsistencia actual | Ninguna | Posible asimetría histórica | `DISCARDED` como actual |

## Dato mínimo faltante

Para obtener una respuesta actual A/B se necesita una fuente verificable de 13.52 que revele al menos uno de estos elementos: inventario de clases BD-J, decompilación de `IxcProxy`/`IxcClassLoader`/`WrappedRemote`, firmas de `com_sun_xlet_init` y `com_sun_xlet_execute`, implementación del callback `findMethod`, o logs técnicos con sus nombres y validaciones.

Una demo “Hello World”, el arranque de un Xlet o el rango histórico de una vulnerabilidad no permiten demostrar la presencia o ausencia de esta cadena.

## Conclusión final

La investigación no encontró una diferencia real específica de PS4 13.52. El estado actual más sólido es:

- **Histórico:** Ixc y la cadena callback/cache/invocación están documentados.
- **Rango público:** la vulnerabilidad Ixc histórica se lista hasta 12.50.
- **13.52:** presencia, validaciones, caché y cambios concretos son `UNVERIFIED`.
- **Inconsistencia actual:** no demostrada; se descarta como afirmación actual.

## Referencias

[1]: https://www.psdevwiki.com/ps4/Vulnerabilities — PS4 Developer Wiki, índice público de vulnerabilidades BD-J; la entrada Ixc aparece como `FW <= 12.50`.

[2]: https://hackerone.com/reports/3104356 — HackerOne #3104356, “Blu-ray Disc Java Sandbox Escape via two vulnerabilities”.

[3]: https://hackerone.com/reports/1379975 — HackerOne #1379975, “bd-j exploit chain”.

[4]: https://www.psx-place.com/threads/update-2-thefl0w-discloses%22blu-ray-disc-java-sandbox-escape-vulnerabilities-ps3-ps4-ps5.37554/ — Discusión pública histórica de la cadena BD-J.
