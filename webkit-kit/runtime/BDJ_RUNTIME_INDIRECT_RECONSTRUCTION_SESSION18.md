# Reconstrucción indirecta del runtime BD-J/JVM de PS4 13.52

## Alcance

Esta investigación parte de que la búsqueda pública directa de bytes, JARs y bootclasspath de PS4 13.52 está agotada. No repite esa búsqueda. Utiliza únicamente el corpus ya conservado en `webkit-ps4-1352-kit`: informes, código histórico, manifests, tablas, hashes, referencias versionadas y documentación pública ya registrada.

No se ejecutaron exploits, payloads, JAR, ELF/BIN ni hardware. El objetivo es obtener correlaciones útiles sin convertirlas en hechos de 13.52.

## Conclusión ejecutiva

El corpus permite construir un **mapa de interfaces históricas y una cadena de comprobación**, pero no reconstruir el runtime 13.52 de forma suficientemente determinada. La correlación más fuerte es arquitectónica:

```text
BD-J cliente
  → CoreIxcClassLoader / IxcProxy / URLClassLoader
  → reflection y carga de clases
  → APIs internas o nativas históricas
  → policy / deserialización / JIT según la ruta
```

Esta arquitectura explica qué nombres y contratos deberían comprobarse primero, pero no demuestra que las mismas clases, firmas, filtros o semántica existan en 13.52.

El manifest público/local del PUP sólo contiene metadata verificable del contenedor SLB2. Las referencias a `bdjstack.jar`, `rt.jar` y `BdjPolicyImpl` en el corpus son nombres documentales o históricos, no artefactos actuales de 13.52. Declara firmware 13.52, hashes del contenedor y de sus dos entradas internas, pero marca los contenidos como `ABSENT_UNTIL_DECRYPTED` y registra explícitamente que no confirma `libSceNKWebKit`, `libkernel_web`, libc ni artefactos retail.[1]

El inventario `analysis/webkit_13.52.json` clasifica el artefacto WebKit como `ABSENT`, con `artifact: null`, `sha256: null`, sin segmentos ni patrones.[2] Esto impide usar WebKit como sustituto indirecto del runtime BD-J.

## Evidencia versionada y fuerza de inferencia

| Evidencia conservada | Qué permite inferir | Qué no permite inferir | Clasificación |
|---|---|---|---|
| `analysis/pup_13.52_manifest.json:1-54` | Procedencia oficial declarada, firmware 13.52, formato SLB2, hashes de contenedor/entradas y ausencia de extracción interna | Clases, módulos o cambios de runtime | `DIRECT_13.52` para metadata; `UNVERIFIED` para contenido |
| `analysis/webkit_13.52.json:2-24` | No hay imagen WebKit retail verificable en el corpus | Estado del runtime BD-J/JVM | `DIRECT_13.52` para ausencia documentada del artefacto WebKit; no evidencia Java |
| `evidence/bd-jb-src/src/com/bdjb/exploit/sandbox/IxcProxyImpl.java:15-49` | Cliente histórico usa `CoreIxcClassLoader`, guarda `remote` y delega en `super.invokeMethod` | Implementación de `IxcProxy`, cache, `findMethod` o validaciones 13.52 | `HISTORICAL_ONLY` |
| `evidence/bd-jb-src/src/com/bdjb/exploit/sandbox/ExploitServiceProxyImpl.java:31-60` | Cliente histórico conecta Ixc con `URLClassLoader`, `Class.forName`, `loadClass` y `newInstance` | Que esa cadena siga disponible o sea alcanzable en 13.52 | `HISTORICAL_ONLY` |
| `evidence/bdjplus-src/src/com/sony/bdjstack/system/BDJModule.java:264-307,351,400,649-653` | Loader Java público y nombres de componentes `bdjstack` | Bootclasspath, filtros y runtime Sony actuales | `HISTORICAL_ONLY` |
| `BDJ_OBJECTSTREAM_FORK_COMPARISON_SESSION14.md` | El parche OpenJDK usa `domains[]` y una intersección de privilegios en construcción serializable | Integración en BD-J 13.52 | `HISTORICAL_ONLY` |
| `BDJ_COMPILER_AGENT_CONTRACT_INDEPENDENT.md` | Contrato histórico de `CompilerAgentRequest`, ACK, `compiler_data` y separación de `JitDefaultImpl` | Existencia o layout actual del compiler-agent | `HISTORICAL_ONLY` |
| `BDJ_PSDESCRIPTORFACTORY_CALLER_ANALYSIS_SESSION12.md` | Cuerpos editoriales históricos de `handles()`/`canWriteFile()` y sus rangos documentados | Caller actual y comportamiento 13.52 | `HISTORICAL_ONLY`; 13.52 `UNVERIFIED` |
| Nota oficial de 13.52 | La release declara correcciones genéricas de seguridad | Componente o método cambiado | `INDIRECT_13.52` |

## Correlaciones de nombres y firmas

### Correlación Ixc/classloading

El cliente histórico de `bd-jb` contiene una relación verificable entre `CoreIxcClassLoader`, `IxcProxy`, `URLClassLoader`, `Class.forName`, `loadClass` y `newInstance`. Esto permite inferir que la interfaz histórica de cliente necesitaba un loader Ixc y una capacidad de cargar clases Java. No permite inferir que `IxcClassLoader`, `WrappedRemote`, `com_sun_xlet_init`, `com_sun_xlet_execute` o `findMethod` conservaran la misma firma en 13.52.

La correlación útil es un **puente de comprobación**: si en el futuro aparece metadata versionada, hay que buscar primero la correspondencia entre loader, proxy, método cacheado, `CodeSource`, `ProtectionDomain` y target. Sin esos elementos, un nombre de clase aislado sería sólo `INFERRED` o `UNVERIFIED`.

### Correlación deserialización/policy

El parche OpenJDK y los informes locales describen una mitigación que introduce `ProtectionDomain[] domains`, calcula dominios de la jerarquía serializable y aplica una intersección de privilegios en la construcción. Los forks públicos no contienen `ObjectStreamClass`, `ReflectionFactory` ni `ObjectInputStream` de la JVM Sony. La inferencia válida es que el cambio OpenJDK define un **invariante de comparación** —el contexto de construcción no debe superar la intersección de los dominios de la jerarquía—, no que Sony lo haya incorporado en 13.52.

Para una comprobación posterior, las señales mínimas serían `domains`, `getProtectionDomains`, un dominio sin permisos, `doIntersectionPrivilege`, la ruta de `newInstanceForSerialization` y el tratamiento separado de `readObject`/`readResolve`.

### Correlación compiler-agent/JIT

`BDJ_COMPILER_AGENT_CONTRACT_INDEPENDENT.md` conserva el layout histórico de `CompilerAgentRequest` de 0x58 bytes, el ACK `0xAA`, `compiler_data`, la copia a `compiler_data + 0x28` y la ruta alternativa `JitDefaultImpl` con APIs `sceKernelJit*`. Esto permite distinguir dos familias de interfaz: un protocolo privado del receiver y una API JIT legítima.

La inferencia útil es negativa: la existencia histórica de `JitDefaultImpl` no confirma compiler-agent; la existencia histórica de un `CompilerAgentRequest` no confirma que el descriptor, framing, validaciones o memoria JIT sobrevivan en 13.52.

### Correlación policy/JAR

`BDJ_PSDESCRIPTORFACTORY_CALLER_ANALYSIS_SESSION12.md` conserva cuerpos históricos de `handles(int,String)` y `canWriteFile()`. El primero muestra comparaciones textuales de raíz persistente; el segundo muestra comprobaciones de atributos y el rechazo histórico de `userprefs` bajo una raíz persistente original. No hay callers públicos que conecten los booleanos con escritura real, carga de clases o cambio de permisos.

La inferencia correcta es que esas funciones son **gates de policy/almacenamiento**, no una cadena demostrada hacia classloading. El nested-JAR histórico no se reutiliza como evidencia nueva.

## Relaciones de versión

La documentación oficial conservada distingue 13.50 y 13.52 sólo por notas de alto nivel: 13.50 describe usabilidad y 13.52 correcciones de seguridad. La lista pública no muestra 13.51. PSDevWiki proporciona formato y metadata general de software, pero no un diff Java versionado.[3]

A partir de ello sólo pueden formularse estas inferencias:

| Inferencia | Evidencia | Clasificación |
|---|---|---|
| 13.52 tuvo al menos una corrección de seguridad de sistema | Nota oficial de release | `DIRECT_13.52` como metadata; no como componente |
| Alguna superficie histórica pudo ser modificada | Nota genérica de seguridad + contexto de vulnerabilidades públicas | `INDIRECT_13.52` |
| La modificación afectó BD-J/JVM | Ninguna fuente técnica | `UNVERIFIED` |
| La modificación afectó Ixc, policy o JIT | Ninguna fuente técnica | `UNVERIFIED` |
| El runtime 13.52 comparte todas las firmas históricas | Código cliente/forks históricos | `HISTORICAL_ONLY`; no inferencia válida |

## Puente práctico de “no tenemos runtime” a “sabemos qué comprobar”

El material existente no permite saber qué componente cambió, pero sí permite definir una secuencia de comprobación determinista para cualquier metadata futura:

| Orden | Señal a comprobar | Por qué es discriminante |
|---:|---|---|
| 1 | Identidad de `bdjstack`/`rt` y versión de clases bootstrap | Distingue cliente histórico de runtime efectivo |
| 2 | `IxcProxy`/`IxcClassLoader`/`WrappedRemote` y `findMethod` | Determina si el canal y el cacheo histórico existen |
| 3 | `ClassLoader$NativeLibrary`, `find`/`findEntry` y `CodeSource` | Determina la frontera interna/native histórica |
| 4 | `ObjectStreamClass`/`ReflectionFactory` y `domains[]` | Determina integración de la mitigación OpenJDK |
| 5 | `ObjectInputStream`, `readObject`, `readResolve`, `defineClass` | Determina callbacks y loaders fuera de la construcción |
| 6 | `PSDescriptorFactory`/policy/JAR | Determina gates de persistencia y representación de rutas |
| 7 | `CompilerAgentRequest`/receiver frente a `sceKernelJit*` | Distingue protocolo privado de API JIT legítima |

Este puente no requiere asumir una vulnerabilidad. Convierte la incertidumbre en una lista de firmas y relaciones que pueden comprobarse cuando aparezca una fuente técnica autorizada.

## Clasificación final

| Categoría | Alcance |
|---|---|
| `DIRECT_13.52` | Metadata del manifest PUP y existencia/documentación de la versión; no clases Java |
| `INDIRECT_13.52` | Contexto de correcciones de seguridad y posibles áreas afectadas, sin componente identificado |
| `HISTORICAL_ONLY` | Código `bd-jb`, BDJPlus, contratos Ixc, ObjectStream, PSDescriptorFactory y compiler-agent |
| `INFERRED` | Relaciones arquitectónicas y señales que deben comprobarse, nunca equivalencias binarias |
| `UNVERIFIED` | Estado actual de todas las clases, firmas, filtros, loaders, policy y JIT en 13.52 |

## Conclusión

La reconstrucción indirecta no produce un componente cambiado identificado. Sí produce tres resultados útiles y verificables:

1. El manifest de 13.52 demuestra procedencia y metadata del contenedor, pero declara que el contenido interno no está disponible para análisis.
2. Los clientes y forks históricos revelan qué contratos y nombres deben comprobarse, especialmente la frontera Ixc/classloading, la intersección de dominios serializables y la separación compiler-agent/API JIT.
3. Las notas de release de 13.52 prueban correcciones genéricas de seguridad, pero no permiten asignarlas a BD-J/JVM.

La afirmación máxima defendible es:

> **Sabemos qué relaciones y firmas buscar, pero no sabemos qué componente cambió en 13.52. Todas las equivalencias de comportamiento actual permanecen `UNVERIFIED`.**

## Referencias

[1]: https://www.playstation.com/en-us/support/hardware/ps4/system-software-info/ "PlayStation 4 system software update features"
[2]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 "OpenJDK protection-domain deserialization change"
[3]: https://www.psdevwiki.com/ps4/System_Software "PS4 Developer Wiki: System Software"
[4]: https://github.com/TheOfficialFloW/bd-jb "Public bd-jb repository"
[5]: https://github.com/john-tornblom/bdj-sdk "Public BDJ SDK"
[6]: https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/io/ObjectInputStream.java "OpenJDK ObjectInputStream"
