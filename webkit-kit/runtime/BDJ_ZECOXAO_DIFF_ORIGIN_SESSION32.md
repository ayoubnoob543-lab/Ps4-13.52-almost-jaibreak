# Procedencia pública del diff BD-J atribuido a zecoxao/Jose Coixao

## Alcance y conclusión

Esta investigación rastreó el origen público de los materiales que Jose Coixao mostró en diffs de `bdjstack`, priorizando repositorios, posts, enlaces y archivos descargables. No se ejecutaron exploits, payloads, JARs, binarios ni código contra hardware.

Se recuperó un artefacto público nuevo y reproducible: el archivo MediaFire `files_diff_bdjstack_jar_ps5.7z`, enlazado desde una publicación de Jose Coixao del 19 de marzo de 2026. El archivo contiene **fuentes Java descompiladas o reconstruidas para PS5 `bdjstack` 12.00/13.00**, no un conjunto identificado como PS4 13.50/13.52. Su existencia explica una ruta pública de trabajo para producir diffs BD-J, pero no demuestra que sea el origen de las capturas de `RootCertManager.java` de PS4 13.50→13.52.

La reconstrucción más precisa es, por tanto:

```text
Jose Coixao publica capturas de diffs de bdjstack
→ enlaza un archivo público MediaFire de PS5 12.00/13.00
→ el archivo contiene fuentes Java por versión
→ el material permite comparar clases BD-J y rutas de policy/persistencia
→ [bloqueo] no hay asignación a PS4 13.50/13.52 ni RootCertManager/SUNJCE
```

## Artefacto público recuperado

| Campo | Valor |
|---|---|
| Autor/editorial | Jose Coixao, `@notnotzecoxao` |
| Post que anuncia el archivo | https://x.com/notnotzecoxao/status/2034586729684910541 |
| Post contextual de los diffs | https://x.com/notnotzecoxao/status/2034585765137576040 |
| Enlace acortado | https://t.co/TEVzzvY624 |
| URL expandida | https://www.mediafire.com/file/ilf5yaw13frv2w7/files_diff_bdjstack_jar_ps5.7z/file |
| Nombre | `files_diff_bdjstack_jar_ps5.7z` |
| Tipo | Archivo 7Z |
| Tamaño publicado | 10.04 KB |
| Fecha publicada en MediaFire | 2026-03-19 06:03:59 |
| Región indicada por MediaFire | Portugal |
| SHA-256 del archivo descargado | `4f815045a9fe4419085a7f32007794e1201dca01a839645274745ab4ffd76c99` |
| Firmware indicado por el nombre/contenido | PS5 12.00/13.00 |
| Relación con PS4 13.50/13.52 | `UNVERIFIED`; no atribuida por el archivo |
| Clasificación | `DOCUMENTED_ONLY` para su existencia; `HISTORICAL_ONLY`/`UNVERIFIED` para PS4 |

La página MediaFire fue usada sólo para recuperar metadata y el archivo público. La mención de un análisis antivirus `0/28` no aporta evidencia de firmware, procedencia técnica o integridad del contenido.

## Índice del archivo

El archivo contiene un directorio `files_diff_bdjstack jar ps5` y doce fuentes Java:

| Grupo | Archivos |
|---|---|
| PS5 12.00 | `1200_PlaybackControlEngine.java`, `1200_PrimaryAudioControl.java`, `1200_PSDescriptorFactory.java`, `1200_SysProfile.java`, `1200_UserPreferenceManagerImpl.java`, `1200_UserPreferenceManagerImpl$ReadPreferenceAction.java` |
| PS5 13.00 | `1300_PlaybackControlEngine.java`, `1300_PrimaryAudioControl.java`, `1300_PSDescriptorFactory.java`, `1300_SysProfile.java`, `1300_UserPreferenceManagerImpl.java`, `1300_UserPreferenceManagerImpl$ReadPreferenceAction.java` |

Las fuentes extraídas se conservaron fuera del commit como material auxiliar de análisis. Sus tamaños observados son:

| Archivo | Tamaño |
|---|---:|
| `1200_PlaybackControlEngine.java` | 39060 bytes |
| `1200_PrimaryAudioControl.java` | 2952 bytes |
| `1200_PSDescriptorFactory.java` | 7881 bytes |
| `1200_SysProfile.java` | 4374 bytes |
| `1200_UserPreferenceManagerImpl.java` | 6144 bytes |
| `1200_UserPreferenceManagerImpl$ReadPreferenceAction.java` | 1058 bytes |
| `1300_PlaybackControlEngine.java` | 39031 bytes |
| `1300_PrimaryAudioControl.java` | 3257 bytes |
| `1300_PSDescriptorFactory.java` | 7910 bytes |
| `1300_SysProfile.java` | 4480 bytes |
| `1300_UserPreferenceManagerImpl.java` | 8127 bytes |
| `1300_UserPreferenceManagerImpl$ReadPreferenceAction.java` | 1299 bytes |

## Diff funcional observable

### `PSDescriptorFactory`

La diferencia más relevante para esta investigación está en `handles(int, String)`:

```diff
- return var2 != null ? var2.startsWith(persistentRoot) : false;
+ return var2 != null ? var2.startsWith(RootCertManager.getOriginalPersistentRoot()) : false;
```

La versión 13.00 también conserva referencias a `RootCertManager` en `getCredentialPath()` y usa:

```java
RootCertManager.getOriginalPersistentRoot()
RootCertManager.getGrantorDigest(...)
RootCertManager.createNewPath(...)
```

El mismo archivo contiene `canWriteFile()` y bloquea explícitamente:

```java
if (var0.equals(RootCertManager.getOriginalPersistentRoot() + "/userprefs")) {
    return false;
}
```

También contiene la comprobación de `AllPermission` en `isPrivilegedContext()` y la selección entre rutas credentialed y acceso normal.

Estos cuerpos son material real dentro del archivo público, pero su etiqueta es **PS5 12.00/13.00**, no PS4 13.50/13.52. Por eso no se pueden usar como implementación retail PS4.

### `UserPreferenceManagerImpl`

La fuente 13.00 añade `DataInputStream` y validaciones estructurales de un archivo serializado de preferencias mediante `checkClassDesc()` y `checkUserPrefFile()`. Comprueba magic/version, class descriptor `[[Ljava.lang.String;`, flags y strings. `ReadPreferenceAction` usa:

```java
RootCertManager.getOriginalPersistentRoot() + "/userprefs"
```

y el manager ejecuta las lecturas/escrituras mediante `AccessController.doPrivileged(...)`.

Esto demuestra que el archivo público incluye una comparación de cambios BD-J con componentes de persistencia, serialización y policy. No demuestra que el diff original de PS4 usara exactamente el mismo archivo ni que alguna de estas clases sea 13.52.

## Lo que el archivo no contiene

La enumeración y el análisis pasivo no encontraron:

```text
RootCertManager.java
RootCertManager.class
BdjPolicyImpl.java
BdjPolicyImpl.class
sunjce_provider.jar
rt.jar
bdjstack.jar completo
sunjce_hash
isSunJCEVerified
RSACipherAdaptor
NONEwithRSA
```

Tampoco contiene nombres `13.50` o `13.52`; las etiquetas internas son `1200` y `1300`, coherentes con PS5 por el nombre del archivo y la publicación de origen.

## ¿De dónde proceden las capturas de PS4?

La evidencia permite identificar con seguridad un **método público de difusión** de diffs BD-J: capturas en X más un archivo MediaFire con fuentes de dos versiones. No permite identificar que ese archivo concreto sea la fuente de las capturas de `RootCertManager.java` de PS4 13.50/13.52, porque:

1. el archivo dice PS5;
2. no contiene `RootCertManager` ni `sunjce_hash`;
3. no contiene `sunjce_provider.jar` ni `BdjPolicyImpl`;
4. no incluye manifest de PS4, PUP, filesystem o build ID;
5. no contiene una fecha/commit que lo vincule al post de junio de 2026 sobre PS4.

Las alternativas restantes —filesystem dump, extracción directa de una consola, snapshot privado, otro archivo no enlazado o trabajo propio del investigador— son posibles, pero no aparecen demostradas en la evidencia pública revisada. `BlueLoader` u otra herramienta no se pueden atribuir como usadas sin una referencia técnica o log explícito del autor.

## Clasificación de hallazgos

| Hallazgo | Clasificación |
|---|---|
| Jose Coixao publicó diffs públicos de `bdjstack` | `DOCUMENTED_ONLY` |
| Existe un archivo MediaFire reproducible enlazado por él | `DOCUMENTED_ONLY` |
| El archivo contiene fuentes 12.00/13.00 de PS5 | `DIRECT_PUBLIC_ARTIFACT` / `HISTORICAL_ONLY` frente a PS4 |
| `PSDescriptorFactory` cambia entre 1200 y 1300 | `DIRECT_PUBLIC_ARTIFACT` |
| `UserPreferenceManagerImpl` añade validación de preferencias en 1300 | `DIRECT_PUBLIC_ARTIFACT` |
| El archivo contiene material usado para el diff PS4 13.50→13.52 | `UNVERIFIED` |
| El archivo es el origen de las capturas de RootCertManager PS4 | `UNVERIFIED` |
| zecoxao obtuvo los archivos PS4 mediante filesystem dump | `HYPOTHESIS` |
| zecoxao usó BlueLoader | `HYPOTHESIS` |
| Existe una ruta pública reproducible a los archivos PS4 exactos | `UNVERIFIED` |

## ¿Permite continuar sin PUP completo?

Sí, pero sólo parcialmente. El archivo permite estudiar cómo se presentan y comparan snapshots BD-J, verificar cambios en `PSDescriptorFactory` y `UserPreferenceManagerImpl`, y construir una referencia pública de nomenclatura y estructura. No permite cerrar la cadena PS4 13.50→13.52 ni recuperar `RootCertManager.isSunJCEVerified()` o `sunjce_provider.jar` de esas versiones.

El artefacto mínimo que falta sigue siendo un conjunto identificado de archivos PS4:

```text
RootCertManager.class o RootCertManager.java de PS4 13.50/13.52
BdjPolicyImpl.class o fuente equivalente
sunjce_provider.jar
manifest/ruta/tamaño/SHA-256
```

Si sólo aparece `RootCertManager.class`, ya se podrían extraer descriptor, constant pool e instrucciones. Para resolver qué bytes producen `sunjce_hash`, se necesita además el `sunjce_provider.jar` correspondiente o un manifest que identifique exactamente el recurso medido.

## Reproducibilidad

El archivo puede localizarse mediante el post de Jose Coixao y la URL MediaFire indicada arriba. La inspección realizada fue pasiva: descarga, `file`, SHA-256, enumeración de entradas 7Z y lectura de fuentes Java extraídas. No se ejecutó ninguna clase, JAR, binario ni herramienta procedente del archivo.

## Referencias

[1]: https://x.com/notnotzecoxao/status/2034585765137576040 "Jose Coixao: some diffs from ps5 bdjstack 12.00 and 13.00"
[2]: https://x.com/notnotzecoxao/status/2034586729684910541 "Jose Coixao: files_diff_bdjstack jar ps5"
[3]: https://t.co/TEVzzvY624 "Enlace acortado al archivo público"
[4]: https://www.mediafire.com/file/ilf5yaw13frv2w7/files_diff_bdjstack_jar_ps5.7z/file "MediaFire: files_diff_bdjstack jar ps5"
[5]: https://x.com/notnotzecoxao/status/2066944047944446366 "Jose Coixao: captura pública de RootCertManager"
[6]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&action=raw&section=51 "PSDevWiki: sección SUNJCE"
