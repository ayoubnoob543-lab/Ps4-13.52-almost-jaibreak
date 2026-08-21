# Diferencial PS4 13.50 → 13.52 para BD-J/JVM

## Alcance

Este informe compara exclusivamente la evidencia pública disponible sobre PS4 13.50, una posible 13.51 y PS4 13.52 con respecto a BD-J/JVM, Ixc, deserialización, classloading, policy, `PSDescriptorFactory` y compiler-agent/JIT. No se buscaron PUPs, dumps privados ni runtime protegido, y no se ejecutaron exploits, payloads, JAR, ELF/BIN ni hardware.

La búsqueda se realizó sobre el historial y corpus de `webkit-ps4-1352-kit`, los informes ya publicados en `webkit-kit/runtime`, la documentación pública de PSDevWiki y las páginas oficiales de características de software de PlayStation.

## Resumen ejecutivo

No se encontró un cambio de implementación actual verificable entre 13.50 y 13.52 para ninguno de los componentes solicitados. La única diferencia pública concreta es editorial:

| Versión | Nota oficial |
|---|---|
| 13.50 | Mejora de mensajes/usabilidad en algunas pantallas |
| 13.52 | Correcciones de seguridad del sistema |

La lista oficial consultada no muestra una entrada 13.51. Esto demuestra que 13.51 no está documentada en esa lista pública, pero no demuestra que no existieran builds internas o no publicadas.

La frase de 13.52 no identifica módulo, clase, método, CVE, commit, firma ni subsistema. La nota de release es `INDIRECT_13.52` sólo como metadata de versión y contexto de seguridad, no como evidencia de un cambio Java. En consecuencia, no permite atribuir la corrección a Java, BD-J, Ixc, policy, classloading, JAR/ZIP, JIT o cualquier otra superficie.

## Matriz diferencial

| Componente | 13.50 | 13.51 | 13.52 | Diferencia verificable | Confianza |
|---|---|---|---|---|---|
| BD-J/JVM y módulos Java | Sin detalle técnico público | No documentada en la página oficial consultada | Sin detalle técnico; sólo “security fixes” | Ninguna implementación comparada | `UNVERIFIED` |
| `IxcProxy`/callbacks/stubs | No hay cuerpo o firma de 13.50 | No hay evidencia | No hay cuerpo o firma | Ninguna | `UNVERIFIED` |
| `ObjectStreamClass` | No hay runtime | No hay evidencia | No hay runtime | Ninguna | `UNVERIFIED` |
| `ReflectionFactory` | No hay runtime | No hay evidencia | No hay runtime | Ninguna | `UNVERIFIED` |
| `ObjectInputStream` | No hay runtime | No hay evidencia | No hay runtime | Ninguna | `UNVERIFIED` |
| `ClassLoader`/`defineClass` | Sólo clientes/forks históricos | No hay evidencia | Sólo clientes/forks históricos | Ninguna | `HISTORICAL_ONLY`; 13.52 `UNVERIFIED` |
| `ProtectionDomain` | No hay runtime | No hay evidencia | No hay runtime | Ninguna | `UNVERIFIED` |
| `PSDescriptorFactory` | Cuerpos editoriales de generaciones antiguas | No hay evidencia | No hay cuerpo 13.52 | La nota editorial de patch no es un diff de 13.50→13.52 | `HISTORICAL_ONLY`; 13.52 `UNVERIFIED` |
| `BdjPolicyImpl` | Referencias históricas | No hay evidencia | No hay cuerpo actual | Ninguna | `HISTORICAL_ONLY`; 13.52 `UNVERIFIED` |
| `XletClassLoader`/`BDJFactory` | Referencias históricas | No hay evidencia | No hay cuerpo actual | Ninguna | `HISTORICAL_ONLY`; 13.52 `UNVERIFIED` |
| `JarZipFile` | Variantes históricas anteriores | No hay evidencia | No hay cuerpo actual | No se reutiliza el nested-JAR descartado | `DISCARDED` para extrapolación |
| Compiler-agent/JIT | Contrato histórico del cliente | No hay evidencia | No hay implementación actual | Ninguna | `HISTORICAL_ONLY`; 13.52 `UNVERIFIED` |

## Evidencia pública de versiones

La página oficial de PlayStation identifica la versión 13.52 y declara que se realizaron correcciones de seguridad. También enumera 13.50 como una actualización de mensajes/usabilidad, y 13.04 y 13.02 como actualizaciones con correcciones de seguridad.[1]

La página no identifica 13.51. La documentación pública de PSDevWiki describe el formato de versión y el historial general del software, pero la información consultada no contiene un diff de módulos BD-J/JVM ni una descripción de cambios de esas clases.[2]

Estas fuentes permiten afirmar la existencia pública de 13.50 y 13.52 y sus notas genéricas. No permiten afirmar una relación causal entre la corrección de 13.52 y una superficie Java concreta.

## Revisión del historial Git local

La rama contiene informes sobre precedentes históricos de `ObjectStreamClass`, `ReflectionFactory`, `IxcProxy`, `PSDescriptorFactory`, `BdjPolicyImpl`, `XletClassLoader`, `BDJFactory`, `JarZipFile` y compiler-agent/JIT. Esos informes no contienen bytes ni implementaciones actuales atribuidas a 13.50–13.52.

La búsqueda del historial Git y del texto versionado no produjo una referencia independiente a 13.51 ni un commit que documente un cambio de esos componentes. La ausencia de una mención local no demuestra que no exista una build interna; sólo demuestra que no está preservada en este corpus.

## Cambios concretos que sí pueden afirmarse

| Diferencia | Evidencia | Clasificación |
|---|---|---|
| 13.50 está descrita oficialmente como mejora de mensajes/usabilidad | Página oficial de características | `DIRECT_13.52` no aplica; metadata pública de 13.50: `DIRECT` |
| 13.52 está descrita oficialmente como corrección genérica de seguridad | Página oficial de características | `DIRECT_13.52` para la nota de release, no para Java |
| No aparece 13.51 en la lista oficial consultada | Página oficial | `DOCUMENTED_ONLY`/`UNVERIFIED` respecto a builds no publicadas |
| No hay diff público actual de BD-J/JVM | Corpus local y fuentes consultadas | `UNVERIFIED` como ausencia de evidencia, no como afirmación de ausencia en consola |
| No hay cambio técnico verificable de `PSDescriptorFactory` entre 13.50 y 13.52 | No existe caller/cuerpo actual comparable | `UNVERIFIED` |

## Lo que no debe inferirse

No es válido inferir que “security fixes” de 13.52 significa que Sony integró el parche OpenJDK de `ProtectionDomain`, eliminó Ixc, cambió `findMethod`, corrigió `UserPreferenceManagerImpl`, modificó `BdjPolicyImpl`, cambió `PSDescriptorFactory`, eliminó compiler-agent/JIT o sustituyó `ClassLoader`.

Tampoco es válido usar la existencia pública de BD-J userland en 13.52 como evidencia de que las mismas clases históricas, la misma política o el mismo contrato JIT sigan presentes.

## Primer punto que continúa bloqueado

El primer punto bloqueado es la obtención de una fuente técnica versionada que compare al menos una clase o módulo BD-J/JVM entre 13.50 y 13.52. Sin esa fuente no puede distinguirse entre:

1. una corrección dentro del runtime Java;
2. un parche en el classloader/policy;
3. un cambio en BD-J nativo o IPC;
4. una corrección de una superficie no relacionada.

La ausencia de evidencia específica es `UNVERIFIED`, no una prueba de que los componentes no hayan cambiado.

## Conclusión

La prioridad de encontrar un cambio actual verificable no se pudo satisfacer con las fuentes públicas disponibles. El único diferencial confirmado es la descripción genérica de release: 13.50 documenta usabilidad y 13.52 documenta correcciones de seguridad. No existe evidencia pública actual que permita atribuir un cambio concreto a BD-J/JVM, Ixc, deserialización, classloading, policy, `PSDescriptorFactory`, JAR/ZIP o compiler-agent/JIT.

Por tanto, para todos esos componentes la clasificación específica de 13.52 permanece **UNVERIFIED**. El nested-JAR histórico no se reutiliza como hallazgo nuevo.

## Referencias

[1]: https://www.playstation.com/en-us/support/hardware/ps4/system-software-info/ "PlayStation 4 system software update features"
[2]: https://www.psdevwiki.com/ps4/System_Software "PS4 Developer Wiki: System Software"
[3]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer Wiki: Vulnerabilities"
[4]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 "OpenJDK protection-domain deserialization change"
