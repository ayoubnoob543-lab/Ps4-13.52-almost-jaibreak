# Matriz de hipótesis sobre el cambio de seguridad de PS4 13.52

**Autor:** Manus AI  
**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** análisis estático y documental basado en el historial del repositorio y fuentes públicas. No se descargaron PUPs/dumps privados ni runtime propietario; no se ejecutaron exploits, payloads, JAR/ELF/BIN ni hardware.

## Respuesta ejecutiva

La nota oficial de PS4 13.52 sólo indica correcciones de seguridad. La evidencia pública disponible no identifica el componente corregido, el commit, la clase, el módulo ni el cambio de comportamiento.

La matriz permite ordenar hipótesis por **compatibilidad documental**, pero no atribuye el cambio a ninguna de ellas. El resultado correcto es:

> **Sin atribución posible.** No hay evidencia suficiente para afirmar que el cambio de 13.52 correspondiera a BD-J/Ixc, deserialización, ClassLoader, policy/JAR, PSDescriptorFactory, compiler-agent/JIT, `sunjce` u otra superficie concreta.

## Matriz principal

| Candidato | Vulnerabilidad/mitigación histórica | Rango documentado | Evidencia alrededor de 13.50/13.52 | Qué encaja | Qué contradice | Dato mínimo de confirmación | Estado |
|---|---|---|---|---|---|---|---|
| **BD-J/Ixc** | `IxcProxy`/call-stack, proxies generados, stubs `WrappedRemote`, callback `findMethod` y ejecución privilegiada. | PSDevWiki lista la vulnerabilidad Ixc como `FW <= 12.50`; HackerOne #3104356 es histórico. | No hay clase, firma, diff ni log 13.52. ConsoleMods limita BD-JB público a 12.52 o inferior. | La actualización 13.52 es posterior al rango histórico y la nota genérica podría incluir una mitigación. | El rango histórico termina en 12.50; no hay referencia 13.52 al método/callback actual. | Decompilación/metadata 13.52 de `IxcProxy`, `IxcClassLoader`, `WrappedRemote`, `findMethod` y validaciones. | `UNVERIFIED` |
| **Deserialización/ProtectionDomain** | `ObjectInputStream.readObject()` privilegiado; OpenJDK 8180024 añade dominios e intersección de privilegios antes de construir objetos. | Cadena histórica en firmwares antiguos; parche OpenJDK público, no rango Sony. | Ningún código Sony 13.52; no se sabe si la mitigación fue integrada o adaptada. | Es una mitigación de seguridad concreta que podría existir en una actualización. | No hay diff Sony ni indicio público que mencione `ObjectStreamClass`/`ReflectionFactory` en 13.52. | `ObjectStreamClass`/`ReflectionFactory` de 13.52 con `domains`, `getProtectionDomains` y `doIntersectionPrivilege`. | `UNVERIFIED` |
| **ClassLoader/defineClass** | Construcción/carga reflectiva histórica posterior a deserialización; riesgo depende de `ProtectionDomain` y policy. | Histórico; sin rango actual verificable. | Ninguna firma, símbolo o log 13.52. | Un cambio de loader podría ser una corrección de seguridad. | No hay evidencia independiente de `ClassLoader` en 13.52. | Código/decompilación 13.52 de `defineClass`, loader y dominio asignado. | `UNVERIFIED` |
| **Policy/CodeSource/JAR** | `BdjPolicyImpl` canoniza URL mientras `JarZipFile` interpreta literalmente la entrada nested-JAR. | HackerOne #3452696 declara 13.00–13.02; CVE-2025-64390. | Ninguna fuente fija un cambio en 13.52; el caso conocido ya está acotado antes. | La nota de seguridad podría cubrir una variante posterior de policy/loader. | La vulnerabilidad concreta publicada está parcheada/limitada antes de 13.52; no hay variante posterior demostrada. | Diff 13.50→13.52 de `BdjPolicyImpl`, `JarZipFile`, `BDJFactory` o `XletClassLoader`. | `HISTORICAL_ONLY / UNVERIFIED` |
| **PSDescriptorFactory** | Entradas históricas `handles()`/`canWriteFile()` asociadas editorialmente a `userprefs`. | El índice usa rangos inciertos `<= ?11.00?` y `<= ?9.00?`. | No hay cuerpo completo, caller ni evidencia 13.52. | Podría explicar una corrección de permisos/archivo. | Rangos editoriales inciertos y ausencia de implementación; no conecta con 13.52. | Código/diff verificable de la clase en 13.50/13.52 y caller de escritura. | `HISTORICAL_ONLY / UNVERIFIED` |
| **Compiler-agent/JIT** | Protocolo histórico de compiler receiver/JIT relacionado con ejecución usermode; depende de internals JVM. | Histórico; no se documenta rango 13.52. | Ningún símbolo, estructura, tamaño o mitigación 13.52. | Una actualización de seguridad podría alterar el protocolo privado. | La nota pública no menciona JIT; no hay artefactos o logs de compiler-agent. | Metadata/decompilación 13.52 del receiver, estructura y validaciones. | `UNVERIFIED` |
| **`sunjce`** | Ruta histórica de permisos/JAR y firma; PSDevWiki la lista como `FW <= 13.50` y “untested”. | `<=13.50` según PSDevWiki; no probado editorialmente. | Referencias públicas atribuidas a ASaudidos/GBAtemp dicen que la ruta fue eliminada/parcheada en 13.52, pero no aportan bytes, hash, clase o diff. | Es el candidato con relación temporal más directa: 13.50 está en el límite y 13.52 es posterior. | La afirmación no contiene evidencia de implementación; “eliminada” no identifica qué método cambió ni demuestra que la nota oficial se refiera a ella. | `sunjce_provider.jar` 13.50/13.52 o diff verificable de `RootCertManager`/policy con hashes. | `INDIRECT_13.52` débil / `UNVERIFIED` |
| **UAF userland no BD-J** | Publicación comunitaria afirma que un UAF de entradas userland fue parcheado en 13.50. | 13.50 según Reddit; sin CVE/clase/módulo. | No hay vínculo con BD-J/JVM; 13.52 sólo aparece como actualización posterior. | Explica por qué una nota de seguridad podría ser genérica. | Fuente comunitaria sin detalles técnicos ni corroboración primaria. | CVE/advisory, clase/módulo, diff 13.50/13.52. | `INDIRECT_13.52` débil |
| **Otra superficie BD-J** | PSDevWiki lista BDJO, archivos, certificados, preferencias y otras familias históricas. | Rangos diversos, mayoritariamente anteriores. | No existe referencia posterior con clase, método o cambio 13.52. | Es posible en abstracto. | La falta de nombre o evidencia no permite priorizarla responsablemente. | Advisory o diff que nombre componente y versión. | `UNVERIFIED` |

## Evaluación de la evidencia posterior

### `sunjce`

Es el candidato con mejor **coincidencia temporal**, no con mejor demostración técnica. PSDevWiki sitúa la ruta histórica en `<=13.50`, mientras referencias públicas atribuidas a ASaudidos/GBAtemp describen su eliminación o parche en 13.52. Sin embargo, ninguna de esas referencias proporciona una clase, método, hash o diff que permita comprobar qué cambió. Por eso sólo merece `INDIRECT_13.52` débil y permanece `UNVERIFIED` como atribución del cambio de seguridad.

### BD-JB público y el límite 12.52

ConsoleMods afirma que BD-JB público llega hasta 12.52 y que Lapse está parcheado en 12.50/12.52. Esto demuestra que las rutas históricas públicas no se transfieren automáticamente a 13.52, pero no identifica el cambio de 13.52 ni prueba que afecte al runtime BD-J/JVM.

### UAF de 13.50

Una publicación comunitaria afirma que un UAF usado por entradas userland fue parcheado en 13.50. La afirmación no identifica módulo, clase, CVE o commit. No permite vincularlo a BD-J ni usarlo como explicación del cambio de 13.52.

### Nota oficial de Sony

La página oficial de soporte de PlayStation proporciona la actualización oficial y sólo información general. La nota “security fixes” no contiene una lista de CVEs, clases, módulos o componentes BD-J. Es metadata de existencia de firmware, no atribución técnica.

## Contradicciones y límites

La principal contradicción es temporal: varias superficies BD-J históricas ya están documentadas como parcheadas antes de 13.52 o limitadas a 12.50/12.52. Eso hace razonable que 13.52 contenga otra mitigación, pero no permite escoger una familia concreta.

La segunda contradicción es probatoria: las fuentes que mencionan “patched” o “removed” no publican los bytes ni el diff. No se puede convertir la coincidencia de firmware en evidencia directa.

La tercera es de alcance: un cambio de seguridad de firmware puede pertenecer a kernel, sistema, red, DRM, WebKit, BD-J u otra parte no cubierta por el corpus. La lista de candidatos no es exhaustiva a nivel del sistema completo.

## Puntuación cualitativa

La siguiente puntuación sólo ordena el valor de investigación documental; no estima probabilidad real de que Sony corrigiera esa superficie:

| Candidato | Valor temporal | Evidencia técnica | Contradicción | Prioridad documental |
|---|---:|---:|---:|---:|
| `sunjce` | Alta | Baja | Alta | 1 |
| BD-J/Ixc | Media | Baja | Alta | 2 |
| Deserialización/ProtectionDomain | Baja | Media histórica | Alta | 3 |
| Policy/CodeSource/JAR variante no nested | Baja | Media para 13.00–13.02 | Alta | 4 |
| ClassLoader/defineClass | Baja | Media histórica | Alta | 5 |
| UAF userland no BD-J | Media | Baja | Media | 6 |
| Compiler-agent/JIT | Baja | Media histórica | Alta | 7 |
| PSDescriptorFactory | Muy baja | Baja | Muy alta | 8 |

## Dato mínimo para confirmar o descartar cada hipótesis

No se necesita otro informe general. Hace falta una pieza primaria con procedencia:

- Para `sunjce`: diff/hash de `sunjce_provider.jar`, `RootCertManager` o policy entre 13.50 y 13.52.
- Para Ixc: firma/cuerpo de `IxcProxy`/`IxcClassLoader` y validación de `findMethod` en 13.52.
- Para deserialización: `ObjectStreamClass`/`ReflectionFactory` 13.52 y presencia de `domains`/`doIntersectionPrivilege`.
- Para policy/JAR: diff 13.50→13.52 de `BdjPolicyImpl`/`JarZipFile`/`XletClassLoader`.
- Para PSDescriptorFactory: cuerpo de `handles()`/`canWriteFile()` y caller de `userprefs` en una build identificada.
- Para JIT: metadata/decompilación del compiler receiver y sus validaciones en 13.52.
- Para UAF: advisory/CVE y módulo/clase exactos.

## Conclusión

La hipótesis que mejor encaja temporalmente es **`sunjce`**, pero sólo como indicio débil. La evidencia no permite afirmar que la nota de seguridad de PS4 13.52 se refiera a `sunjce`, Ixc, ProtectionDomain, ClassLoader, policy/JAR, PSDescriptorFactory, compiler-agent/JIT ni a otra superficie BD-J.

> **Resultado final: sin atribución posible.**

No se encontró una matriz de cambios posterior a 13.52 que identifique una clase, módulo o mitigación concreta. La única conclusión responsable es mantener todas las superficies como históricas o no verificadas hasta disponer de una fuente primaria que nombre el componente corregido.

## Referencias

[1]: https://www.playstation.com/en-us/support/hardware/ps4/system-software/ — Sony PlayStation, página oficial de actualización PS4.

[2]: https://www.psdevwiki.com/ps4/Vulnerabilities — PS4 Developer Wiki, rangos y resúmenes BD-J.

[3]: https://hackerone.com/reports/3104356 — HackerOne #3104356, cadena Ixc histórica.

[4]: https://hackerone.com/reports/1379975 — HackerOne #1379975, deserialización/reflection histórica.

[5]: https://hackerone.com/reports/3452696 — HackerOne #3452696, nested-JAR; PS4 13.00–13.02.

[6]: https://consolemods.org/wiki/PS4:BD-JB — ConsoleMods Wiki, BD-JB hasta 12.52.

[7]: https://github.com/kimariin/BlueLoader — BlueLoader, rutas históricas de `bdjstack.jar`/`rt.jar`.

[8]: https://www.reddit.com/r/ps4homebrew/comments/1rwjnxw/warning_do_not_update_to_1350_userland_exploit/ — publicación comunitaria sobre un UAF presuntamente parcheado en 13.50.

[9]: https://x.com/ASaudidos/status/2068786051041108378 — referencia pública atribuida a ASaudidos sobre la ruta `sunjce`; se usa como indicio documental, no como prueba de bytes.
