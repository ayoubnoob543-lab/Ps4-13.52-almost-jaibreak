# Reevaluación: ObjectStreamClass, ReflectionFactory y ProtectionDomain

**Autor:** Manus AI  
**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** análisis estático del corpus local, historial Git e informes públicos ya disponibles. No se obtuvieron PUPs, dumps, runtime propietario ni artefactos protegidos; no se ejecutaron exploits, payloads, JAR/ELF/BIN ni hardware.

## Resultado ejecutivo

La auditoría completa del repositorio no encuentra fuentes de runtime BD-J/JVM de Sony 13.52. El único código relevante conservado en el corpus local son informes y referencias históricas; las rutas de clientes históricos que Session13 citaba (`API.java`, `ExploitServiceProxyImpl.java` y `BDJModule.java`) no están actualmente presentes en el workspace, por lo que sus afirmaciones se tratan como documentación heredada, no como archivos locales reanalizados.

El parche OpenJDK `020204a972d9be8a3b2b9e75c2e8abea36d787e9` está suficientemente especificado para reconstruir su intención: `ObjectStreamClass` guarda dominios de protección, recorre la jerarquía entre la clase concreta y la clase que declara el constructor, crea un dominio sin permisos si la jerarquía es incoherente y usa `doIntersectionPrivilege` antes de `cons.newInstance()`. Esto es una mitigación concreta de la **construcción de objetos durante la deserialización**.

No existe evidencia local o pública en el corpus que demuestre que Sony integró ese cambio completo, una adaptación parcial o una ruta alternativa en PS4 13.52. El resultado es **`HISTORICAL_ONLY` para el parche y sus clientes; `UNVERIFIED` para 13.52**. No se encontró divergencia real atribuible a 13.52.

## 1. Auditoría del corpus local

La rama autorizada contiene el informe previo `BDJ_OBJECTSTREAM_PROTECTIONDOMAIN_ANALYSIS_SESSION13.md`, que resume el commit OpenJDK, HackerOne #1379975, HackerOne #3104356 y clientes históricos. No contiene las implementaciones Sony de `ObjectStreamClass`, `ReflectionFactory`, `ObjectInputStream`, `ClassLoader` o `UserPreferenceManagerImpl`.

La búsqueda de símbolos en `webkit-kit/runtime/` sólo produce informes Markdown. Las rutas históricas citadas por Session13 no existen actualmente:

| Ruta citada | Estado local |
|---|---|
| `/home/ubuntu/ps4-bdj-trust-audit/evidence/bd-jb-src/src/com/bdjb/api/API.java` | `ABSENT` |
| `/home/ubuntu/ps4-bdj-trust-audit/evidence/bd-jb-src/src/com/bdjb/exploit/sandbox/ExploitServiceProxyImpl.java` | `ABSENT` |
| `/home/ubuntu/ps4-bdj-trust-audit/evidence/bdjplus-src/src/com/sony/bdjstack/system/BDJModule.java` | `ABSENT` |

Por tanto, el corpus disponible permite verificar la documentación y los hashes de informes, pero no volver a calcular hashes de esos clientes históricos ausentes ni presentar sus rutas como evidencia directa actual.

## 2. Mitigación OpenJDK: cambio exacto

El commit público [1] modifica `ObjectStreamClass` y clases relacionadas para evitar que la construcción especial de un objeto serializable se ejecute con más permisos que la jerarquía de clases que interviene.

### 2.1 Estado del descriptor

El cambio añade `ProtectionDomain[] domains` al descriptor. Durante la inicialización, la implementación obtiene el constructor de serialización y calcula los dominios que separan la clase concreta de la clase que declara ese constructor.

### 2.2 `getProtectionDomains`

La función nueva sólo calcula dominios cuando hay constructor, el loader de la clase no es nulo y existe `SecurityManager`. Recorre las superclases hasta el `declaringClass` del constructor. Cada `ProtectionDomain` intermedio se agrega a un conjunto. Si la jerarquía no alcanza el declaring class esperado, se sustituye por un `ProtectionDomain` sin permisos.

La invariante central es que una clase serializable no pueda beneficiarse de permisos que pertenecen a un tramo de la jerarquía que la construcción no debería atravesar.

### 2.3 `newInstance`

Antes del commit, la ruta podía terminar en `cons.newInstance()` directamente. Después, si `domains` no es nulo ni vacío, se crea una acción privilegiada que llama al constructor y se ejecuta con:

```java
jsa.doIntersectionPrivilege(
    pea,
    AccessController.getContext(),
    new AccessControlContext(domains));
```

El cambio no elimina `readObject`, `readResolve`, `ReflectionFactory` ni `ClassLoader`. Endurece específicamente el contexto de permisos de la construcción del objeto.

### 2.4 `ReflectionFactory`

La referencia OpenJDK actual [2] describe `ReflectionFactory` como una interfaz interna capaz de crear objetos reflectivos, acceder a datos privados, invocar métodos privados y cargar bytecode no verificado; por diseño debe estar protegida. JDK-8315810 [3] documenta una evolución posterior que reimplementa la construcción de serialización con method handles en JDK 22. Ninguna de estas referencias demuestra que Sony trasladara esos cambios a OrbisOS.

## 3. Cadena histórica BD-J

HackerOne #1379975 [4] describe históricamente:

```text
UserPreferenceManagerImpl
  → FileInputStream(RootCertManager.getOriginalPersistentRoot() + "/userprefs")
  → ObjectInputStream.readObject()
  → ObjectStreamClass / constructor de serialización
  → contexto privilegiado
  → posible construcción de un ClassLoader
  → defineClass / carga posterior
```

Esta cadena es evidencia histórica del cliente y del flujo descrito por el informe. No prueba que PS4 13.52 conserve `UserPreferenceManagerImpl`, que el archivo se lea igual, que exista el mismo filtro de deserialización o que la mitigación OpenJDK esté ausente/presente.

La existencia de `readResolve` tampoco basta para formular una vulnerabilidad. Habría que demostrar su contexto de ejecución, la controlabilidad de la clase y la relación con el `ProtectionDomain` ya aplicado durante la construcción.

## 4. Variantes y primer punto no verificable

| Variante | Condición necesaria | Qué la impediría | Estado |
|---|---|---|---|
| Mitigación OpenJDK no integrada | `ObjectStreamClass` no contiene `domains` o usa `cons.newInstance()` sin intersección | Presencia de `getProtectionDomains` y `doIntersectionPrivilege` | `HYPOTHESIS`, no 13.52 |
| Integración parcial | Se protege la construcción normal, pero no una ruta proxy/CORBA/alternativa | Todas las rutas de descriptor/proxy reutilizan el mismo contexto | `HYPOTHESIS` |
| `readResolve` con contexto distinto | Callback posterior a la construcción recibe privilegios adicionales | Contexto intersecado y callback no controlable | `HYPOTHESIS` |
| `ReflectionFactory` alternativa | Constructor serializable generado fuera de la ruta endurecida | Todas las construcciones pasan por la API protegida | `HYPOTHESIS` |
| `ClassLoader.defineClass` fuera de la intersección | Loader controlable asigna un dominio independiente | Loader, origen y dominio quedan limitados por policy | `HYPOTHESIS` |
| Ausencia de `SecurityManager` | `getProtectionDomains` no calcula dominios y se usa la ruta directa | No existe además un contexto privilegiado controlable | `HYPOTHESIS`, no evidencia de bug por sí sola |
| Filtro de deserialización divergente | `ObjectInputStream` Sony usa filtros o clases permitidas distintos | Filtro completo y validación de origen antes de `readObject` | `HYPOTHESIS` |

El **primer punto no verificable** es la implementación efectiva de `ObjectStreamClass` y `ReflectionFactory` dentro del runtime BD-J usado en 13.52. No es posible decidir entre mitigación completa, integración parcial, sustitución interna o eliminación de la ruta sin esas clases o metadata equivalente.

## 5. Clasificación de evidencia

| Elemento | Evidencia disponible | Clasificación |
|---|---|---|
| Código del commit OpenJDK 8180024 | Commit público con diff de `ObjectStreamClass`, `ProtectionDomain` y `doIntersectionPrivilege` | `HISTORICAL_ONLY` |
| `ReflectionFactory` como API interna privilegiada | Fuente OpenJDK y JDK-8315810 | `HISTORICAL_ONLY` |
| `UserPreferenceManagerImpl` + `readObject` privilegiado | HackerOne #1379975 | `HISTORICAL_ONLY` |
| Uso histórico de ClassLoader/defineClass | Descrito en HackerOne y reportes del corpus | `HISTORICAL_ONLY` |
| Presencia de `domains` en Sony 13.52 | Ninguna | `UNVERIFIED` |
| Ausencia de `domains` en Sony 13.52 | Ninguna | `UNVERIFIED` |
| Integración parcial en 13.52 | Sólo hipótesis de comparación | `HYPOTHESIS` |
| Cambio concreto de 13.50→13.52 | Ninguno encontrado | `DISCARDED` como afirmación no sustentada |
| `DIRECT_13.52` | Sin código, hash o metadata runtime | No presente |

## 6. Evidencia mínima necesaria

Para pasar de `UNVERIFIED` a una conclusión A/B se necesita un artefacto verificable de la implementación efectiva, no otro informe histórico. El mínimo técnico es uno de los siguientes conjuntos:

| Componente | Evidencia mínima |
|---|---|
| `ObjectStreamClass` | Código/decompilación que revele `domains`, recorrido de superclases y ruta `newInstance`. |
| `ReflectionFactory` | Implementación de `newConstructorForSerialization` y relación con `ObjectStreamClass`. |
| `ObjectInputStream` | Llamadas reales a `ObjectStreamClass.newInstance`, filtros y tratamiento de `readObject`/`readResolve`. |
| `ClassLoader` | Firma/visibilidad de `defineClass`, `ProtectionDomain` asignado y loader de origen. |
| `UserPreferenceManagerImpl` | Fuente/metadata que muestre ruta, validación y contexto de `userprefs`. |
| Procedencia | Hash, versión/build y relación verificable con PS4 13.52. |

## Conclusión final

La mitigación OpenJDK es verificable y precisa, pero el corpus `webkit-ps4-1352-kit` no contiene el runtime BD-J que permitiría comprobar su integración. Los clientes históricos y las referencias a `UserPreferenceManagerImpl`, `ReflectionFactory`, `ObjectStreamClass` y `ClassLoader` no son sustitutos del código Sony 13.52.

No se encontró una divergencia real específica de 13.52. La clasificación conservadora es:

> **Mitigación y cadena histórica: `HISTORICAL_ONLY`. Integración, modificación o ausencia en PS4 13.52: `UNVERIFIED`. Variantes de integración parcial: `HYPOTHESIS`.**

## Referencias

[1]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 — OpenJDK 8180024, “Improve construction of objects during deserialization”.

[2]: https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/jdk/internal/reflect/ReflectionFactory.java — OpenJDK `ReflectionFactory`.

[3]: https://bugs.openjdk.org/browse/JDK-8315810 — Reimplementación de `ReflectionFactory::newConstructorForSerialization` con method handles.

[4]: https://hackerone.com/reports/1379975 — PlayStation #1379975, “bd-j exploit chain”.

[5]: https://hackerone.com/reports/3104356 — PlayStation #3104356, “Blu-ray Disc Java Sandbox Escape via two vulnerabilities”.

[6]: https://www.psdevwiki.com/ps4/Vulnerabilities — PS4 Developer Wiki, vulnerabilidades BD-J históricas.
