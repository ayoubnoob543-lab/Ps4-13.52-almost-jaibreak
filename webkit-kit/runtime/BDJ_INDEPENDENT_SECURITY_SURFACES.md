# Superficies BD-J/OrbisOS independientes de Ixc, sunjce, nested-JAR y compiler-agent

## Alcance

Se revisaron fuentes públicas, advisories, HackerOne, PSDevWiki y documentación comunitaria. Se excluyeron deliberadamente Ixc, `sunjce`, nested-JAR y compiler-agent/JIT como superficies de esta sesión. No se descargaron PUPs/dumps privados ni se ejecutaron exploits, payloads, JAR/ELF/BIN o código contra hardware.

Las categorías son `DIRECT_13.52`, `INDIRECT_13.52`, `HISTORICAL_ONLY`, `HYPOTHESIS` y `DISCARDED`.

## Resultado ejecutivo

La búsqueda no encontró una vulnerabilidad pública nueva con código y evidencia independiente que pueda atribuirse a PS4 13.52. La única pista adicional que merece una investigación posterior es la pareja de entradas de PSDevWiki sobre `PSDescriptorFactory.handles()` y `PSDescriptorFactory.canWriteFile()`, ambas relacionadas con la ruta `userprefs`. El índice las presenta como superficies históricas separadas, pero las páginas enlazadas no pudieron recuperarse: sus títulos contienen caracteres inválidos para la extracción directa y no se dispone de código, rango exacto ni parche verificable.

Por tanto, estas entradas son **pistas editoriales**, no evidencia técnica de una vulnerabilidad ni de persistencia en 13.52.

## Candidatos

### 1. `PSDescriptorFactory.handles()` no comprueba la ruta de `userprefs`

El índice de PSDevWiki enumera una vulnerabilidad BD-J titulada aproximadamente “FW <= ?11.00? - `PSDescriptorFactory.handles()` does not check userprefs path”. El nombre sugiere una posible confusión entre una ruta controlada por BD-J y una ruta de preferencias usada por un descriptor/factory, lo que sería independiente de Ixc, nested-JAR y compiler-agent.

Sin embargo, no se pudo recuperar la página específica. No hay código, firma de método, flujo de llamada, excepción, primitive, hash, commit ni rango firmware confirmado. La interrogación del propio título indica incertidumbre editorial.

**Clasificación:** `HISTORICAL_ONLY / UNVERIFIED`.

**Dependencia necesaria:** conocer qué entrada controla `handles()`, qué ruta valida, qué consumidor abre el archivo y si el resultado alcanza permisos o sólo produce un error/lectura.

**Qué la descartaría:** una página fuente o diff que muestre que la ruta no es controlable, que la función sólo clasifica archivos sin efectos de seguridad o que el comportamiento fue corregido antes de los firmwares relevantes.

### 2. `PSDescriptorFactory.canWriteFile()` no comprueba la ruta de `userprefs`

El índice enumera una segunda entrada aproximadamente “FW <= ?9.00? - `PSDescriptorFactory.canWriteFile()` does not check userprefs path”. Podría representar una superficie de escritura de preferencias/configuración distinta de Ixc y de la deserialización `UserPreferenceManagerImpl` ya estudiada.

La página específica tampoco fue recuperable desde la URL del índice. No hay implementación, ruta, permiso requerido, llamada privilegiada ni evidencia de impacto.

**Clasificación:** `HISTORICAL_ONLY / UNVERIFIED`.

**Dependencia necesaria:** recuperar la implementación de `canWriteFile()`, el caller, el formato de ruta y la relación entre la decisión booleana y la escritura real.

**Qué la descartaría:** demostrar que `canWriteFile()` sólo valida una ruta interna fija, que el caller aplica una segunda canonicalización o que sólo controla UI/metadata sin operación de escritura.

### 3. BDJO/`/cdc/lib/`

PSDevWiki enumera una entrada histórica de path traversal vía BDJO y `/cdc/lib/`. Se excluye como candidato principal porque el propio índice la coloca en la familia de traversal/classloading y no se dispone de una demostración independiente que la separe de los mecanismos ya auditados. Sin una causa raíz y un flujo de privilegios distinto, no debe contarse como superficie nueva.

**Clasificación:** `DISCARDED` como hallazgo independiente; `HISTORICAL_ONLY` como referencia editorial.

### 4. Certificados, preferencias y configuración

`UserPreferenceManagerImpl`/`ObjectInputStream` y `RootCertManager` aparecen en HackerOne #1379975, pero ya forman parte de las cadenas históricas estudiadas. No se encontró otra vulnerabilidad pública independiente de parsing de certificados, preferencias o configuración que aporte una primitive nueva sin depender de esas rutas.

**Clasificación:** `HISTORICAL_ONLY`, sin hallazgo nuevo.

### 5. `XletClassLoader`, `URLClassLoader` y parsing ZIP/JAR

`XletClassLoader`, `JarZipFile`, `BDJFactory` y `CoreAppId.isSigned()` aparecen en HackerOne #3452696, pero el informe es explícitamente nested-JAR. `URLClassLoader` sólo es una abstracción Java; su existencia en Java SE no prueba que esté expuesto o autorizado en el perfil BD-J de PS4.

**Clasificación:** `DISCARDED` para esta sesión por dependencia de nested-JAR o ausencia de evidencia Sony independiente.

### 6. IPC/callbacks Java distintos de Ixc

No se encontró en las fuentes revisadas una interfaz pública de IPC/callback BD-J diferente de Ixc que otorgue privilegios o acceda a recursos protegidos. La presencia de `Remote`, sockets o callbacks Java estándar no demuestra que exista un endpoint privilegiado en OrbisOS.

**Clasificación:** `HYPOTHESIS`, sin candidato concreto.

## Tabla de evaluación

| Candidato | Versión afectada históricamente | Causa raíz conocida | Mitigación conocida | Dependencia necesaria | Evidencia pública hasta 13.52 | Clasificación |
|---|---|---|---|---|---|---|
| `PSDescriptorFactory.handles()` / `userprefs` | Título incierto: `<= ?11.00?` | No recuperable; el índice sólo afirma falta de comprobación de ruta. | No recuperable. | Código del método y caller de descriptor. | Ninguna específica de 13.52. | `HISTORICAL_ONLY / UNVERIFIED` |
| `PSDescriptorFactory.canWriteFile()` / `userprefs` | Título incierto: `<= ?9.00?` | No recuperable; el índice sólo afirma falta de comprobación de ruta. | No recuperable. | Código de validación y escritura. | Ninguna específica de 13.52. | `HISTORICAL_ONLY / UNVERIFIED` |
| BDJO `/cdc/lib/` traversal | Histórico, rango indicado por PSDevWiki | Path traversal editorial; no se separa de familias ya estudiadas. | No evaluable con la página no recuperada. | Flujo completo de classloading/policy. | Ninguna. | `DISCARDED` como superficie independiente |
| `UserPreferenceManagerImpl`/deserialización | Histórico, documentado en #1379975 | `ObjectInputStream.readObject()` privilegiado. | Mitigaciones OpenJDK y posibles filtros. | Archivo controlable y gadget. | Ninguna 13.52. | `HISTORICAL_ONLY` |
| `Provider`/`Service` | Histórico, documentado en #1379975 | `Class.forName` y validación de accessor. | Cambios de registro/proveedor desconocidos. | Clases propietarias y accessor. | Ninguna 13.52. | `HISTORICAL_ONLY` |
| Certificados/configuración alternativa | Sin candidato concreto | No demostrada. | No demostrada. | Implementación de parser/caller. | Ninguna. | `HYPOTHESIS` |
| IPC distinto de Ixc | Sin interfaz concreta | No demostrada. | No demostrada. | Endpoint privilegiado. | Ninguna. | `HYPOTHESIS` |

## Mejor superficie para investigación adicional

La mejor pista nueva es **`PSDescriptorFactory.handles()` / `canWriteFile()`**, no porque exista una vulnerabilidad confirmada, sino porque es la única referencia del índice público que parece tratar directamente una ruta de `userprefs` fuera de las cadenas ya revisadas. Antes de formular hipótesis, hay que recuperar el contenido exacto de esas páginas o una copia histórica válida de PSDevWiki.

El siguiente paso seguro es documental: localizar el título canónico/ID correcto de las dos páginas, consultar revisiones históricas o dumps de documentación pública y extraer únicamente firmas, callers, rutas y rangos. No se debe crear un probe ni ejecutar un Xlet hasta conocer ese flujo.

## Conclusión

No apareció una superficie independiente confirmada que merezca atribución a PS4 13.52. La investigación reduce el espacio de búsqueda a dos referencias `PSDescriptorFactory` históricas cuyo contenido técnico falta. Todo lo demás encontrado pertenece a familias ya auditadas o son APIs Java genéricas sin evidencia Sony.

El estado correcto es:

- **DIRECT_13.52:** ninguno.
- **INDIRECT_13.52:** ninguno.
- **HISTORICAL_ONLY:** `PSDescriptorFactory` según el índice, deserialización/Provider y referencias auxiliares ya conocidas.
- **HYPOTHESIS:** IPC distinto de Ixc y parsing de configuración/certificados sin candidato concreto.
- **DISCARDED:** nested-JAR/`XletClassLoader` de #3452696 y BDJO traversal como supuesto hallazgo independiente.

## Referencias

[1]: https://www.psdevwiki.com/ps4/Vulnerabilities — PS4 Developer Wiki, índice de vulnerabilidades BD-J y rangos editoriales.

[2]: https://hackerone.com/reports/1379975 — PlayStation report #1379975, deserialización y Provider históricos.

[3]: https://hackerone.com/reports/3452696 — PlayStation report #3452696, nested-JAR y componentes XletClassLoader/JarZipFile.

[4]: https://consolemods.org/wiki/PS4:BD-JB — ConsoleMods, rango de las implementaciones públicas BD-JB.
