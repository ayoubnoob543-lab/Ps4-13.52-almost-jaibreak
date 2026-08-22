# Investigación estática: SecurityManager, Unsafe y reflexión restringida

## Resumen

Las tres afirmaciones tienen significado de seguridad, pero no son equivalentes. Un `System.getSecurityManager()` nulo indica que las comprobaciones que siguen el patrón convencional `if (security != null)` no se ejecutan; por sí solo no demuestra que un código BD-J pueda obtener `Unsafe`, modificar memoria o alcanzar código nativo. La documentación de Java describe al `SecurityManager` como una política que permite o deniega operaciones sensibles mediante comprobaciones de permisos [1].

`sun.misc.Unsafe` es una API de bajo nivel. La documentación de OpenJDK señala que sus instancias están limitadas a código confiable y que no deben entregarse a código no confiable [2]. Por ello, demostrar que la clase existe no equivale a demostrar que un Xlet no confiable puede obtener una instancia funcional.

La reflexión restringida tampoco es una capacidad automática. En Java 7/8, `AccessibleObject.setAccessible(true)` suprime las comprobaciones lingüísticas sólo después de la comprobación de `ReflectPermission("suppressAccessChecks")` cuando existe un gestor de seguridad [3]. La ausencia del gestor puede cambiar ese control en implementaciones antiguas, pero todavía habría que demostrar que la clase, el miembro y el mecanismo de reflexión están disponibles en el runtime objetivo.

## Evidencia pública de PlayStation/BD-J

Los reportes públicos de HackerOne describen precedentes históricos relevantes:

| Fuente | Qué documenta | Relación con 13.52 |
|---|---|---|
| [4] #1379975 | Cadena histórica con deserialización, providers, Ixc, compiler receiver y UDF; el reporte indica prueba en PS4 9.00 y fue resuelto/recompensado | `HISTORICAL_ONLY` |
| [5] #3104356 | Problemas históricos de Ixc y callbacks privilegiados; el reporte describe una ruta hacia la desactivación del gestor y fue resuelto/recompensado | `DOCUMENTED_ONLY`, sin confirmación independiente de 13.52 |
| [6] #3452696 | Divergencia entre canonicalización de rutas y resolución de entradas de JAR; su resumen identifica PS4 13.00–13.02 | `HISTORICAL_ONLY` para 13.52 |
| [7] | Investigación general de escapes BD-J en otros reproductores; demuestra que las políticas varían por plataforma | `HISTORICAL_ONLY` |

Estos reportes son evidencia de que las superficies existieron y fueron consideradas vulnerabilidades por PlayStation en versiones concretas. No prueban que la misma cadena sobreviva en 13.52.

## Evaluación de cada afirmación

### 1. `System.getSecurityManager() == null`

**Qué significaría:** el valor global consultado por el código Java es nulo. En APIs que sólo llaman a `checkPermission` cuando el valor no es nulo, ese punto concreto no invocaría al gestor. La documentación oficial muestra precisamente ese patrón [1].

**Qué no demuestra:** no demuestra por sí mismo que se haya podido asignar el valor nulo desde un Xlet, que todas las APIs omitan controles independientes, que el runtime no tenga controles nativos adicionales o que se haya obtenido ejecución nativa.

**Estado:** la afirmación aparece en comentarios y demostraciones públicas atribuidas a terceros, pero no tenemos un log verificable y legible de 13.52 que permita clasificarla como `DIRECT_13.52`.

### 2. Acceso a `sun.misc.Unsafe`

**Qué significaría:** una clase confiable o una ruta de acceso devuelve una instancia utilizable de una API de bajo nivel. La fuente OpenJDK indica que `Unsafe` puede leer y escribir memoria y que la obtención de la instancia está limitada a código confiable [2].

**Qué no demuestra:** que el nombre de la clase exista; que `Class.forName` pueda resolverla; que `getUnsafe()` no aplique la comprobación del loader; que un Xlet pueda invocar métodos de memoria; ni que exista una primitive controlable o una ruta a código nativo.

**Estado:** `sun.misc.Unsafe` está documentada públicamente como API de OpenJDK, y reportes históricos de BD-J mencionan rutas de acceso privilegiado, pero no hay bytes ni salida de 13.52 que demuestren una instancia funcional. Clasificación: `HISTORICAL_ONLY` / `UNVERIFIED_13.52`.

### 3. Campos restringidos de `System`

**Qué significaría:** un objeto `Field` o `Method` puede usarse con acceso suprimido para manipular un miembro que normalmente no es accesible. La documentación de `AccessibleObject` describe que `setAccessible` afecta a campos, métodos y constructores y que requiere `ReflectPermission` cuando existe `SecurityManager` [3].

**Qué no demuestra:** que el miembro concreto sea accesible; que se haya cambiado el flag; que el campo sea mutable; que el runtime acepte la operación; o que modificarlo produzca una escalada posterior.

**Estado:** el acceso reflectivo restringido aparece como parte de cadenas históricas públicas, pero no hay una captura o traza completa atribuida verificablemente a PS4 13.52. Clasificación: `HISTORICAL_ONLY` / `UNVERIFIED_13.52`.

## Relación con nuestro disco

El Xlet `org.homebrew.MyXlet` actual no usa `SecurityManager`, `AccessController`, `Unsafe`, reflexión, `ClassLoader`, `NativeLibrary`, USB, sockets, procesos o código nativo. El cascarón sólo muestra estados estáticos de compatibilidad y termina limpiamente.

Por ello, incluso si la pantalla se muestra, el resultado sólo sería **carga BD-J normal**. No sería una comprobación de ninguna de las tres afirmaciones.

## Qué evidencia mínima resolvería cada punto

| Punto | Evidencia mínima no operativa |
|---|---|
| Gestor nulo | Log o captura legible de la consulta en una build/firmware identificable, con contexto suficiente para descartar una simulación |
| `Unsafe` | Identidad de clase, descriptor y resultado de una comprobación controlada de disponibilidad; no basta el nombre en una fuente histórica |
| Campos restringidos | Nombre del miembro, resultado de la operación reflectiva y excepción/permisión observada, sin modificar estado sensible |
| Aplicabilidad 13.52 | Artefacto o prueba autorizada específica de 13.52 que conecte la capacidad con el runtime real |

## Conclusión

La información pública permite explicar para qué servirían esas capacidades y por qué juntas podrían representar una salida del modelo de sandbox. También demuestra que hubo cadenas BD-J históricas aceptadas por PlayStation. **No demuestra que ASaudidos haya obtenido exactamente esas capacidades en PS4 13.52**, ni que nuestro disco benigno pueda producirlas. La clasificación correcta es `DOCUMENTED_ONLY`, `HISTORICAL_ONLY` y `UNVERIFIED_13.52`; no `CONFIRMED_13.52`.

## Referencias

[1]: https://docs.oracle.com/javase/8/docs/api/java/lang/SecurityManager.html "Oracle Java SE 8 SecurityManager"
[2]: https://github.com/openjdk/jdk/blob/master/src/jdk.unsupported/share/classes/sun/misc/Unsafe.java "OpenJDK sun.misc.Unsafe"
[3]: https://docs.oracle.com/javase/7/docs/api/java/lang/reflect/AccessibleObject.html "Oracle Java SE 7 AccessibleObject"
[4]: https://hackerone.com/reports/1379975 "HackerOne #1379975 — bd-j exploit chain"
[5]: https://hackerone.com/reports/3104356 "HackerOne #3104356 — Blu-ray Disc Java Sandbox Escape via two vulnerabilities"
[6]: https://hackerone.com/reports/3452696 "HackerOne #3452696 — PS4 BD-J privilege escalation using nested JAR"
[7]: https://www.fox-it.com/nl-en/abusing-blu-ray-players-part-1-sandbox-escapes/ "Fox-IT — Abusing Blu-ray Players Part 1"
