# Evidencia pública del runtime BD-J/JVM de PS4 13.52

**Autor:** Manus AI  
**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** búsqueda documental y estática de fuentes públicas, repositorios, informes y metadata. No se descargaron PUPs, dumps privados ni runtime propietario; no se ejecutaron exploits, payloads, JAR/ELF/BIN ni hardware.

## Conclusión ejecutiva

La investigación no localizó bytes, símbolos, manifest interno, bootclasspath, decompilación ni diff de implementación que permita identificar directamente el runtime BD-J/JVM de PS4 13.52.

Sí se verificaron tres piezas de evidencia indirecta:

1. La página oficial de PlayStation enlaza la actualización oficial de PS4, pero sólo publica instrucciones generales y no expone componentes BD-J/JVM.
2. ConsoleMods documenta que BD-JB llega hasta firmware 12.52 y no ofrece soporte 13.52.
3. HackerOne #3452696 publica una implementación detallada de `BdjPolicyImpl`, `JarZipFile`, `XletClassLoader`, `BDJFactory` y `CoreAppId.isSigned()`, pero declara afectación 13.00–13.02, no 13.52.

La conclusión estricta es:

> **No existe evidencia `DIRECT_13.52` del runtime BD-J/JVM ni de las clases objetivo. El estado actual es `UNVERIFIED`; las referencias de 13.52 disponibles sólo demuestran que existe una versión de firmware y que hay demostraciones públicas de BD-J userland, no qué implementación contienen.**

## Auditoría local

La rama autorizada estaba limpia y sincronizada antes de esta sesión. La búsqueda exhaustiva en `webkit-kit/runtime/` sólo encontró informes Markdown; no encontró `rt.jar`, `bdjstack.jar`, `sunjce_provider.jar`, bootclasspath, módulos JVM, clases compiladas, símbolos o diffs de 13.52.

Los únicos binarios presentes en el workspace general son artefactos PS4 ya inventariados (`hen.bin`, `libkernel_sys_13.52.bin`, `lk_dump1.bin`, `lk_dump2.bin` y `lk_dump3.bin`). No son artefactos BD-J/JVM y no se usan como evidencia del runtime.

## Fuentes públicas verificadas

| Fuente | Archivo/sección relevante | Qué demuestra | Clasificación |
|---|---|---|---|
| PlayStation Support [1] | Enlace oficial `PS4UPDATE.PUP` y página de actualización | Existe una fuente oficial de actualización PS4; no publica bootclasspath, clases, símbolos ni hashes internos | `INDIRECT_13.52` |
| ConsoleMods Wiki [2] | “The BD-J exploit requires ... 12.52 or lower”; sección “Henloader (9.00–12.52)” | El BD-JB público documentado no cubre 13.52; 12.50/12.52 tienen rutas distintas | `INDIRECT_13.52` |
| HackerOne #3452696 [3] | Summary, “Affected PS4 system software: version 13.00 to latest (13.02)” | Código/flujo histórico de `BdjPolicyImpl`, `JarZipFile`, `XletClassLoader`, `BDJFactory` y `CoreAppId.isSigned()` para 13.00–13.02 | `HISTORICAL_ONLY` |
| BlueLoader [4] | README y Makefile/documentación de rutas | Herramienta histórica que espera extraer `app0/bdjstack/bdjstack.jar` y `app0/bdjstack/lib/rt.jar` desde un dump; no contiene esos JARs ni soporte 13.52 | `HISTORICAL_ONLY` |
| PSDevWiki [5] | Índice BD-J | Ixc histórico aparece como `FW <= 12.50`; `sunjce` aparece como `FW <= 13.50` no probado | `HISTORICAL_ONLY` |
| GitHub exact-match search | Consultas `13.52 + bdjstack`, `13.52 + rt.jar`, `13.52 + IxcProxy` | No devolvió repositorios, manifests ni hashes públicos de esos componentes | `UNVERIFIED` |

## Componentes solicitados

### Runtime BD-J/JVM y bootclasspath

No apareció ningún archivo o manifest público verificable que exponga el bootclasspath de 13.52. Las rutas `app0/bdjstack/bdjstack.jar` y `app0/bdjstack/lib/rt.jar` están documentadas por BlueLoader como insumos obtenidos desde un dump, pero el proyecto no contiene los bytes.

Clasificación: `HISTORICAL_ONLY`; estado 13.52: `UNVERIFIED`.

### `ObjectStreamClass`, `ReflectionFactory`, `ObjectInputStream`, `ProtectionDomain`

El corpus local contiene el análisis del parche OpenJDK `020204a972d9be8a3b2b9e75c2e8abea36d787e9` y reportes históricos de `ObjectInputStream.readObject()`. No contiene la implementación Sony de esas clases ni un diff 13.52.

Clasificación: `HISTORICAL_ONLY`; integración 13.52: `UNVERIFIED`.

### Ixc: `IxcProxy`, `IxcProxyBuilder`, `IxcClassLoader`, `WrappedRemote`

HackerOne #3104356 documenta históricamente la cadena de proxies, stubs, `findMethod`, caché y `doPrivileged`. PSDevWiki limita la entrada de vulnerabilidad Ixc a `FW <= 12.50`. No existe firma, símbolo o decompilación pública de 13.52.

Clasificación: `HISTORICAL_ONLY`; presencia y semántica en 13.52: `UNVERIFIED`.

### Policy/loader: `PSDescriptorFactory`, `BdjPolicyImpl`, `XletClassLoader`, `BDJFactory`, `JarZipFile`

HackerOne #3452696 sí publica código y flujo de `BdjPolicyImpl`, `JarZipFile`, `XletClassLoader`, `BDJFactory` y `CoreAppId.isSigned()`, pero el propio informe fija el rango en 13.00–13.02. La entrada de `PSDescriptorFactory` en PSDevWiki es editorial e histórica, sin implementación retail 13.52.

Clasificación: `HISTORICAL_ONLY`; persistencia 13.52: `UNVERIFIED`.

## Qué se puede afirmar sobre 13.52

| Pregunta | Resultado | Clasificación |
|---|---|---|
| ¿Existe públicamente PS4 13.52? | Sí, la página oficial enlaza la actualización correspondiente | `INDIRECT_13.52` |
| ¿Existe un runtime BD-J/JVM 13.52 público con hashes? | No localizado | `UNVERIFIED` |
| ¿Existe `rt.jar` 13.52 público verificable? | No localizado | `UNVERIFIED` |
| ¿Existe `bdjstack.jar` 13.52 público verificable? | No localizado | `UNVERIFIED` |
| ¿Existe bootclasspath/manifest 13.52? | No localizado | `UNVERIFIED` |
| ¿Hay código Sony 13.52 de `ObjectStreamClass`/Ixc? | No localizado | `UNVERIFIED` |
| ¿HackerOne #3452696 representa 13.52? | No; declara 13.00–13.02 | `HISTORICAL_ONLY` |
| ¿BlueLoader proporciona runtime 13.52? | No; proporciona tooling y espera un dump | `HISTORICAL_ONLY` |
| ¿Se encontró una diferencia de implementación 13.50→13.52? | No | `UNVERIFIED` |

## Artefactos y hashes

No se encontró ningún artefacto runtime 13.52 al que calcular SHA-256. Por tanto, no se inventan hashes de `rt.jar`, `bdjstack.jar`, módulos JVM ni clases Sony.

El registro local de fuentes generado durante la investigación sí queda preservado en:

`/home/ubuntu/ps4-bdj-bridge-research/current-runtime-public-findings.md`

Su SHA-256 es:

`5fc847a7908230de0202abae1e3595a34a9879df295f61f4346c8941b3a458e0`

El hash corresponde a las notas de fuentes, no a un runtime 13.52.

## Artefacto mínimo faltante

El primer artefacto externo necesario para pasar de `UNVERIFIED` a comparación real es un conjunto procedente de una misma build 13.52 que contenga, como mínimo, `app0/bdjstack/bdjstack.jar`, `app0/bdjstack/lib/rt.jar` y un manifest con firmware, ruta, tamaño y SHA-256. Para evaluar la frontera ProtectionDomain/Ixc también sería necesario el componente JVM/BD-J nativo o metadata de símbolos/decompilación equivalente.

Las referencias públicas actuales no proporcionan esos bytes ni permiten deducir sus firmas.

## Referencias

[1]: https://www.playstation.com/en-us/support/hardware/ps4/system-software/ — Sony PlayStation, página oficial de actualización de PS4.

[2]: https://consolemods.org/wiki/PS4:BD-JB — ConsoleMods Wiki, límite documentado de BD-JB hasta 12.52.

[3]: https://hackerone.com/reports/3452696 — HackerOne #3452696, nested-JAR; declara PS4 13.00–13.02.

[4]: https://github.com/kimariin/BlueLoader — BlueLoader; tooling histórico y rutas de extracción de `bdjstack.jar`/`rt.jar`.

[5]: https://www.psdevwiki.com/ps4/Vulnerabilities — PS4 Developer Wiki, índice de vulnerabilidades BD-J.

[6]: https://hackerone.com/reports/3104356 — HackerOne #3104356, cadena Ixc histórica.

[7]: https://hackerone.com/reports/1379975 — HackerOne #1379975, cadena histórica de deserialización y reflection.
