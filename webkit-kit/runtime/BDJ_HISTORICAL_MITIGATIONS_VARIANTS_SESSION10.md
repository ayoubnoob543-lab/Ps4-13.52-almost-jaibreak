# Mitigaciones históricas de BD-J/OpenJDK y variantes residuales

## Alcance

Este informe estudia de forma estática mitigaciones públicas de las superficies BD-J relacionadas con permisos, `AccessController`, reflection, classloading, deserialización, providers, rutas/JAR y callbacks/IPC. No utiliza PUPs, dumps privados, `rt.jar`, `bdjstack.jar` ni runtime retail 13.52, y no ejecuta exploits, payloads o binarios.

La columna «Evidencia 13.52» no convierte una similitud histórica en confirmación. Las variantes propuestas sólo se marcan `HYPOTHESIS` cuando no existe un artefacto 13.52 que las demuestre.

## Matriz principal

| Superficie | Vulnerabilidad histórica | Mitigación pública | Versión del parche o rango | Posible variante residual | Evidencia 13.52 | Confianza |
|---|---|---|---|---|---|---|
| `IxcProxy` / callbacks privilegiados | `invokeMethod` podía invocar métodos bajo contexto privilegiado; una primera defensa inspeccionaba el call stack buscando `IxcProxy`, pero el informe #3104356 afirma que proxies reales generados por `IxcProxyBuilder` seguían siendo aceptados | Comprobación del call stack y prefijos de clases Ixc; segunda implementación `WrappedRemote` seguía usando `doPrivileged` | Reporte publicado en 2025; el reporte no publica un diff posterior de firmware | Validación que confíe en la presencia de una clase/proxy autorizada en vez de validar identidad, origen y target; otra ruta generada por `IxcClassLoader` | Ninguna evidencia directa; el informe ASaudidos no muestra Ixc | **HISTORICAL_ONLY; variante HYPOTHESIS** |
| `WrappedRemote` / `AccessController` / `SecurityManager` | `com_sun_xlet_execute` invocaba `remoteMethod.invoke` dentro de `doPrivileged` con contexto suministrado por el mecanismo Ixc; la cadena histórica podía terminar afectando al `SecurityManager` | Restricciones de registro, generación de stubs y validaciones de call stack podrían limitar el acceso; no se publica una corrección completa | Reporte #3104356; sin versión de firmware identificada en el texto extraído | Stub válido pero método o `Method` seleccionado desde un loader/controlador inesperado; requiere que la selección siga siendo controlable | Ninguna | **HISTORICAL_ONLY; variante HYPOTHESIS** |
| Deserialización de `userprefs` | `UserPreferenceManagerImpl` ejecutaba `ObjectInputStream.readObject()` dentro de `AccessController.doPrivileged`, permitiendo construir objetos en contexto privilegiado en firmwares antiguos | OpenJDK `020204a972d9be8a3b2b9e75c2e8abea36d787e9` incorpora dominios de protección de constructores y `doIntersectionPrivilege` al crear objetos deserializados | El reporte #1379975 señala que el commit no estaba presente en firmwares antiguos como 5.05; no demuestra la integración exacta en PS4 | Filtros aplicados a constructores pero no a `readObject`, `readResolve`, proxies o clases con rutas de deserialización distintas; sólo posibilidad teórica | Ninguna; no hay bytecode 13.52 | **HISTORICAL_ONLY; variante HYPOTHESIS** |
| `ObjectStreamClass` / dominios de protección | La construcción de una subclase serializable podía cruzar dominios de protección hasta un constructor privilegiado | El commit OpenJDK agrega `ProtectionDomain[]`, dominio sin permisos y la intersección con el contexto actual antes de `cons.newInstance()` | Commit OpenJDK público; no es prueba de que Sony lo incorporara en la build BD-J 13.52 | Implementación BD-J parcialmente derivada que conserve `ObjectInputStream` o `ReflectionFactory` anterior | Ninguna | **HISTORICAL_ONLY; variante HYPOTHESIS** |
| `com.oracle.security.Service.newInstance` | `Class.forName` aceptaba nombres de clase arbitrarios y podía instanciar clases restringidas con constructores públicos de un argumento; `ProviderAdapter.setProviderAccessor` permitía sortear la comprobación de registro según #1379975 | Comprobación de que el servicio esté registrado y corresponda al provider; posibilidad de endurecer el accessor o restringir clases/constructores | Reporte #1379975; no identifica parche de firmware | Otro factory/provider con validación de registro débil o accessor sustituible; no se debe asumir que existe | Ninguna; tampoco aparece en el vídeo público de 13.52 | **HISTORICAL_ONLY; variante HYPOTHESIS** |
| Reflection / clases internas | Acceso a `sun.*` y métodos internos mediante `Class.forName`, reflection y objetos de proveedor | Checks de provider, visibilidad, constructores y contexto de permisos; en OpenJDK moderno hay encapsulación adicional, pero no equivale automáticamente a la implementación BD-J | Evidencia genérica OpenJDK y reportes históricos | Paquetes internos aún expuestos por compatibilidad BD-J o proxies que invocan un `Method` ya obtenido | Ninguna | **HISTORICAL_ONLY; variante HYPOTHESIS** |
| `ClassLoader` / `defineClass` | En firmwares sin el cambio OpenJDK, una subclase de `ClassLoader` podía alcanzar `defineClass` con permisos heredados y ayudar a eludir el sandbox | El cambio de construcción de objetos intersecta dominios de protección; controles adicionales de loader y permisos pueden impedir la herencia privilegiada | Referencia al commit OpenJDK en #1379975; rango exacto de integración Sony desconocido | Loader alternativo, proxy o `defineClass` alcanzado por una ruta de provider/reflection distinta | Ninguna | **HISTORICAL_ONLY; variante HYPOTHESIS** |
| `XletClassLoader` / JAR firmado | El loader y la política podían interpretar de forma divergente la procedencia de un JAR | Verificación de firma, `RootCertManager`, rango de `applicationId` y cambios de normalización podrían cerrar la discrepancia | #3452696 limita explícitamente el bug de JAR anidado a PS4 13.00–13.02 | Divergencia distinta entre URL, canonicalización, entrada ZIP, URL encoding o JAR anidado; no hay evidencia de que sobreviva | #3452696 no prueba 13.52; su rango anterior contradice una extrapolación automática | **HISTORICAL_ONLY; variante HYPOTHESIS** |
| `BdjPolicyImpl` / canonicalización | La política canonicalizaba con `File.getCanonicalPath`, mientras `JarZipFile` trataba `..` como caracteres de una entrada anidada, concediendo `AllPermission` a contenido no confiable | Corrección de la discrepancia de resolución/validación o cambios en loader, firma y policy; el diff exacto no está publicado en la fuente consultada | PS4 13.00–13.02 según #3452696 | Otra divergencia entre la ruta usada por `CodeSource` y la ruta real del loader, pero requiere una nueva inconsistencia demostrable | Ninguna | **HISTORICAL_ONLY; variante HYPOTHESIS** |
| Parsing ZIP/JAR y rutas | `JarZipFile` separaba un JAR exterior y una entrada literal, creando un contexto de carga distinto al de la policy | Normalización común de rutas, rechazo de entradas ascendentes, validación de firmas y coincidencia entre `CodeSource` y origen físico | Rango 13.00–13.02 documentado; parche exacto desconocido | ZIP con nombres codificados, separadores alternativos o múltiples capas de JAR; sólo una categoría de prueba estática futura | Ninguna | **HISTORICAL_ONLY; variante HYPOTHESIS** |
| Callbacks/IPC no Ixc: compiler receiver | El receiver histórico aceptaba una request de `0x58` bytes, ACK `0xAA` y copia a `compiler_data + 0x28` | La divulgación pública indica que el conjunto `bd-jb` fue corregido en PS4 9.50, pero no identifica qué parte del receiver cambió | Probado en 9.00; corregido como conjunto en 9.50 según referencias públicas | Validación de punteros, autenticación del descriptor, cambio de ABI o eliminación del receiver | Ninguna; no hay metadata 13.52 | **HISTORICAL_ONLY; mitigación temporal INDIRECT_13.52; variante HYPOTHESIS** |

## Qué mitigaciones están realmente demostradas

### OpenJDK: deserialización y dominios de protección

El commit `020204a972d9be8a3b2b9e75c2e8abea36d787e9`, titulado «8180024: Improve construction of objects during deserialization», modifica `ObjectStreamClass`. La corrección calcula los dominios de protección que separan la clase concreta de la clase que declara el constructor, crea un dominio sin permisos cuando la cadena es inconsistente y usa `doIntersectionPrivilege` con un `AccessControlContext` compuesto antes de invocar el constructor.

Esto es una mitigación concreta de la herencia de privilegios durante construcción. No demuestra que el runtime BD-J de PS4 13.52 contenga esa revisión, porque el commit es de OpenJDK y no existe una cadena pública de integración Sony que llegue a ese firmware.

### Ixc: mitigación incompleta documentada

El reporte #3104356 proporciona evidencia directa de una defensa que buscaba `com.sony.gemstack.org.dvb.io.ixc.IxcProxy` en el call stack y exigía prefijos de paquetes Ixc. El mismo informe explica que el diseño podía seguir aceptando proxies reales generados por `IxcProxyBuilder`. Por tanto, la mitigación demostrada era una restricción de contexto, no una validación completa de la identidad del target o del flujo de generación.

La existencia de esta defensa histórica permite estudiar patrones residuales públicamente, pero no permite afirmar que la misma implementación esté en 13.52.

### Classloader/JAR: rango históricamente acotado

El reporte #3452696 es importante porque limita el bug de canonicalización y JAR anidado a PS4 13.00–13.02. La evidencia no autoriza a extenderlo a 13.52. Sólo deja como hipótesis metodológica que futuras variantes deberían buscar otra divergencia entre la identidad usada por la policy y el origen real del loader.

## Tres mejores líneas para continuar sin runtime privado

### 1. Diferencial de mitigación OpenJDK aplicado a forks BD-J públicos

Comparar las versiones públicas de `ObjectStreamClass`, `ReflectionFactory`, `AccessController` y `ClassLoader` usadas por forks BD-J disponibles, buscando si el cambio de dominios de protección fue incorporado completo, parcial o reemplazado. El resultado útil sería un commit/blob verificable, no una inferencia por nombre.

### 2. Análisis de invariantes de Ixc y stubs generados

Construir una tabla estática de todas las condiciones documentadas en #3104356: origen del call stack, clase real del proxy, interfaz `Remote`, métodos no estáticos, visibilidad, constructor y selección de `Method`. La pregunta es si la mitigación valida identidad completa o sólo patrones superficiales. Esto puede hacerse con código público sin ejecutar la cadena.

### 3. Comparación de parsers de JAR/ZIP y policy en fuentes públicas

Buscar implementaciones públicas de `BdjPolicyImpl`, `XletClassLoader`, `JarZipFile` y `BDJFactory` para comprobar si comparten una normalización única. Debe priorizarse la búsqueda de inconsistencias de representación —canonical path frente a entry name, separadores y anidamiento— sin probarlas como explotación.

## Conclusión

Las mitigaciones públicas no forman una única corrección global. Cada una protege una frontera diferente: construcción de objetos y dominios de protección, autorización de callbacks Ixc, validación de providers/reflection, coherencia de policy/loader y, por separado, el receiver/JIT.

La mejor posibilidad de una variante residual no es un supuesto “bug intacto” en 13.52, sino una **mitigación parcial con representaciones o contextos divergentes**. Esa formulación sigue siendo `HYPOTHESIS` hasta hallar un diff o código de la versión objetivo. No existe evidencia `DIRECT_13.52` en las fuentes examinadas.

## Referencias

[1]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 "OpenJDK 8180024: Improve construction of objects during deserialization"

[2]: https://hackerone.com/reports/3104356 "PlayStation #3104356: Blu-ray Disc Java Sandbox Escape via two vulnerabilities"

[3]: https://hackerone.com/reports/1379975 "PlayStation #1379975: bd-j exploit chain"

[4]: https://hackerone.com/reports/3452696 "PlayStation #3452696: PS4 BD-J privilege escalation using nested JAR"

[5]: https://habr.com/ru/articles/671088/ "Public reproduction of the BD-J exploit chain"

[6]: https://www.psx-place.com/threads/update-2-thefl0w-discloses-blu-ray-disc-java-sandbox-escape-vulnerabilities-ps3-ps4-ps5.37554/ "Public reproduction and timeline of the BD-J disclosure"
