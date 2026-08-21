# Investigación 26 — Recuperación del diff BD-J PS4 13.50→13.52

**Repositorio:** `webkit-ps4-1352-kit`  
**Objeto:** origen del diff atribuido a zecoxao/Jose Coixao y citado por PSDevWiki.  
**Método:** recuperación pasiva de páginas, wikitexto, URLs multimedia, imágenes y referencias públicas; análisis visual y hash local.  
**Restricciones:** no se ejecutaron exploits, payloads, PUPs descifrados, JAR/ELF/BIN ni hardware.

## Resumen ejecutivo

Se recuperó el origen público que PSDevWiki cita para la afirmación sobre `RootCertManager.java`: la sección raw de PSDevWiki enlaza a la publicación de Jose Coixao `2066944047944446366`, cuya imagen multimedia original/medium se pudo descargar. La imagen es una **captura de código** de 1200×113 píxeles, no un archivo Java, `.class`, JAR ni diff textual.

También se recuperó la imagen del post anterior del hilo, que muestra el fragmento histórico de `BdjPolicyImpl` relacionado con `CodeSource`, la ruta `sunjce_provider.jar`, `RootCertManager.isSunJCEVerified()` y `AllPermission`. Tampoco es un archivo fuente ni bytecode.

No se recuperó el artefacto original que supuestamente produjo el diff: no apareció un `bdjstack.jar`, `rt.jar`, `sunjce_provider.jar`, un árbol de filesystem, una decompilación completa, un commit con los archivos, ni un listado con firmware, tamaños y hashes de los JARs 13.50/13.52.

La cadena se rompe exactamente después de las capturas:

```text
PSDevWiki
→ post/imagen pública de Jose Coixao
→ captura parcial de RootCertManager.java
→ [FALTA] fuente/bytecode/JAR original identificable por firmware
→ [FALTA] diff reproducible de archivos completos
```

## 1. Página exacta de PSDevWiki

La entrada exacta es la sección SUNJCE de [PS4 Developer Wiki — Vulnerabilities].[1] El wikitexto raw reproducible es:

```text
https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&action=raw&section=51
```

La sección se titula:

```text
FW <= 13.50 - Path traversal sandbox escape via sunjce JAR signature (untested)
```

Y contiene, en esencia, estas afirmaciones:

> The sunjce hash in RootCertManager.java was changed on PS4 13.52.
>
> This probably disables injecting old signed JAR files, which could possibly contain vulnerabilities or even be fake signed.
>
> Patched: Yes since PS4 FW 13.52. Not patched as of PS4 FW 13.50.

La misma sección atribuye el diff a:

```text
zecoxao for diffing decompiled 13.50 and 13.52 PS4 BD-J files (2026-06-17)
```

La propia entrada marca el hallazgo como **untested** y utiliza lenguaje probabilístico (“probably”). Por tanto, PSDevWiki es evidencia documental de la afirmación, no un repositorio de los artefactos que fueron comparados.

## 2. Publicación original de Jose Coixao

La publicación original es:

```text
https://x.com/notnotzecoxao/status/2066944047944446366
```

| Campo | Valor |
|---|---|
| Autor | Jose Coixao, `@notnotzecoxao` |
| Fecha visible | 2026-06-16 18:00:37 UTC |
| Texto | `this also got changed (in RootCertManager.java)` |
| Imagen multimedia | `https://pbs.twimg.com/media/HK9CpsiXYAAmMb?format=webp&name=medium` |
| Tipo | Captura de código, no fuente ni bytecode |
| Dimensiones | 1200×113 píxeles |
| Tamaño local | 10568 bytes |
| SHA-256 | `ab98050e2cf3a4e62497e986043387722672460a914fcd51270c74e94ed3d820` |
| Archivo local | `webkit-kit/runtime/rootcertmanager_diff_original_public.webp` |
| Clasificación | `INDIRECT_13.52` / `DIRECT_PUBLIC_SCREENSHOT` |

La imagen muestra dos paneles laterales. En ambos se ve un bloque `static` con:

```java
AccessController.doPrivileged(new 1());
sunjce_hash = "...";
```

Los dos valores visibles son distintos y tienen forma Base64 de 44 caracteres:

```text
y8ehrm0lQ64cek7k6/+CwpSDLsjfnCesSX0agGpM10g=
At2dtIBsAdpxI/GWtq2otASAkU5OVg3QG5fFUF+KBek=
```

La captura no contiene una etiqueta interna que identifique de forma independiente qué panel es 13.50 o 13.52; esa atribución proviene del contexto del post y de PSDevWiki. Tampoco muestra el package, imports, cuerpo completo, descriptor JVM, helpers, ruta del archivo, JAR de origen, tamaño, hash del artefacto ni build ID.

## 3. Post anterior del hilo y `BdjPolicyImpl`

El post anterior es:

```text
https://x.com/notnotzecoxao/status/2066838388976517585
```

| Campo | Valor |
|---|---|
| Autor | Jose Coixao, `@notnotzecoxao` |
| Texto | `bdjb patched on 13.52. this code got removed` |
| Imagen multimedia | `https://pbs.twimg.com/media/HK7ieV2XwAA3gQc?format=webp&name=medium` |
| Tipo | Captura de código, no fuente ni bytecode |
| Dimensiones | 451×370 píxeles |
| Tamaño local | 19958 bytes |
| SHA-256 | `713f2e92ead82f069160de801231988fdeb884b8ec12c7ddd89182acc43fbf23` |
| Archivo local | `webkit-kit/runtime/bdjpolicy_public_screenshot.webp` |
| Clasificación | `HISTORICAL_ONLY` / `DOCUMENTED_ONLY` |

El texto visible de la captura permite leer este flujo histórico simplificado:

```java
if (codeSource != null) {
    URL url = codeSource.getLocation();
    if ("file".equals(url.getProtocol())) {
        String path = url.getFile();
        String jceJar = javaHome + "lib" + separator
                      + "ext" + separator
                      + "sunjce_provider.jar";
        if (path.equals(jceJar)) {
            if (RootCertManager.isSunJCEVerified()) {
                Permissions p = new Permissions();
                p.add(new AllPermission());
                return p;
            }
        }
    }
}
```

La captura demuestra un **caller histórico/documental** y la relación nominal entre policy y `isSunJCEVerified()`. No demuestra el cuerpo del verificador, el algoritmo del hash, la entrada que se hashea ni el comportamiento de la rama `false`.

## 4. Comentario sobre `RSACipherAdaptor`

En el hilo aparece una respuesta pública de `@ps3120`:

```text
And added RSACipherAdaptor in sunjce_provider.jar 13.52
```

La publicación es:

```text
https://x.com/ps3120/status/2070144817233789048
```

| Campo | Valor |
|---|---|
| Autor | `@ps3120` |
| Fecha | 2026-06-25 13:59:20 UTC |
| Tipo | Comentario textual |
| Artefacto adjunto | Ninguno |
| Clasificación | `DOCUMENTED_ONLY` / `UNVERIFIED` |

La frase no proporciona el JAR, la clase, el package, tamaño, SHA-256, commit, firmware de origen ni una referencia al método que calcule `sunjce_hash`. Por ello no convierte la incorporación de `RSACipherAdaptor` en un hecho byte-verificable de PS4 13.52.

## 5. Artefactos originales buscados y resultado

| Artefacto | Resultado | Clasificación |
|---|---|---|
| `RootCertManager.java` completo 13.50 | No recuperado | `UNVERIFIED` |
| `RootCertManager.java` completo 13.52 | No recuperado | `UNVERIFIED` |
| `RootCertManager.class` PS4 13.50 | No recuperado | `UNVERIFIED` |
| `RootCertManager.class` PS4 13.52 | No recuperado | `UNVERIFIED` |
| `bdjstack.jar` 13.50/13.52 | No recuperado | `UNVERIFIED` |
| `rt.jar` 13.50/13.52 | No recuperado | `UNVERIFIED` |
| `sunjce_provider.jar` 13.50/13.52 | No recuperado | `UNVERIFIED` |
| Diff textual de archivos BD-J | No recuperado | `UNVERIFIED` |
| Manifest/listado con tamaños y hashes | No recuperado | `UNVERIFIED` |
| Captura `RootCertManager.java` | Recuperada | `INDIRECT_13.52` |
| Captura `BdjPolicyImpl` | Recuperada | `HISTORICAL_ONLY` |
| Página y wikitexto PSDevWiki | Recuperados | `DOCUMENTED_ONLY` |

El repositorio público `deepakmathi/BDJB` fue revisado como mirror/fork relacionado. Conserva clases históricas `RootCertManager.class` en carpetas `1.xx`, `12.xx` y `13.xx`, pero no identifica estas carpetas con PS4 13.50/13.52 ni contiene la clase SUNJCE mostrada en la captura: sus snapshots `12.xx`/`13.xx` son byte-identical y no exponen `sunjce_hash`, `isSunJCEVerified`, `NONEwithRSA` ni `RSACipherAdaptor`.[2]

## 6. ¿Se puede reproducir el diff con lo recuperado?

No. Las capturas permiten verificar visualmente una diferencia de constantes y un fragmento de policy, pero no permiten calcular un diff de archivos completo ni atribuirlo criptográficamente a una build exacta.

La reproducción completa requeriría dos conjuntos de entradas:

```text
RootCertManager/BD-J 13.50
RootCertManager/BD-J 13.52
```

con al menos:

```text
ruta interna
firmware exacto
archivo original o bytecode
tamaño
SHA-256
```

Para resolver el objeto de `sunjce_hash` sería necesario además:

```text
sunjce_provider.jar 13.50
sunjce_provider.jar 13.52
manifest y entradas ZIP
certificados/firma
RootCertManager.class de ambas builds
```

Sin esas entradas no se puede comprobar si el valor es el digest del JAR completo, una clase, una entrada, el manifest, un certificado, una firma o una representación normalizada.

## 7. Clasificación de la cadena de evidencia

| Eslabón | Evidencia | Clasificación |
|---|---|---|
| PSDevWiki atribuye un diff BD-J a zecoxao | Wikitexto raw y créditos | `DOCUMENTED_ONLY` |
| Jose Coixao publicó una captura de `RootCertManager.java` | Imagen pública recuperada y hasheada | `INDIRECT_13.52` |
| Los dos valores visibles son distintos | Inspección visual de la captura | `DIRECT_PUBLIC_SCREENSHOT` |
| La comparación es de 13.50 y 13.52 | Contexto de post/wiki; no etiqueta interna en la imagen | `INDIRECT_13.52` |
| Existe el archivo fuente completo | No publicado | `UNVERIFIED` |
| Existe bytecode PS4 identificable | No publicado | `UNVERIFIED` |
| SUNJCE está parcheado en 13.52 | Afirmación de PSDevWiki, marcada untested | `DOCUMENTED_ONLY` |
| `RSACipherAdaptor` fue añadido al provider PS4 | Comentario de tercero sin artefacto | `DOCUMENTED_ONLY` |
| El cambio de hash fue causado por `RSACipherAdaptor` | No hay diff ni bytes | `HYPOTHESIS` |

## Conclusión

**Se recuperó el origen público de la afirmación, pero no el diff real ni los archivos que lo produjeron.** La evidencia más fuerte disponible son dos capturas públicas: una de `RootCertManager.java` con dos constantes `sunjce_hash` diferentes y otra de `BdjPolicyImpl` con la llamada histórica a `isSunJCEVerified()` antes de `AllPermission`.

La cadena se rompe al intentar pasar de la captura a los artefactos comparados. Siguen faltando los archivos `RootCertManager.java`/`.class` completos de 13.50 y 13.52, o el `bdjstack.jar` correspondiente con procedencia verificable. Para resolver el hash también falta `sunjce_provider.jar` de las mismas builds.

El siguiente artefacto concreto necesario es:

> **Un `RootCertManager.class` o `bdjstack.jar` extraído de PS4 13.50 y/o 13.52, identificado por ruta, firmware, tamaño y SHA-256; idealmente acompañado por el `sunjce_provider.jar` de la misma build.**

Hasta entonces, el cambio de `sunjce_hash` permanece `INDIRECT_13.52`, el cuerpo del método permanece `UNVERIFIED` y no es válido presentar la captura como un diff reproducible de bytes retail.

## Referencias

[1]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&action=raw&section=51 — PSDevWiki, sección SUNJCE/RootCertManager.
[2]: https://github.com/deepakmathi/BDJB/tree/491852e8cdd66b54166271413371bc65b1d4da07 — Snapshot público BDJB con clases históricas compiladas.
[3]: https://x.com/notnotzecoxao/status/2066838388976517585 — Post anterior de Jose Coixao con la captura de `BdjPolicyImpl`.
[4]: https://x.com/notnotzecoxao/status/2066944047944446366 — Post de Jose Coixao con la captura de `RootCertManager.java`.
[5]: https://x.com/ps3120/status/2070144817233789048 — Comentario público sobre `RSACipherAdaptor`.
[6]: https://hackerone.com/reports/1379975 — Caller histórico relacionado con `getOriginalPersistentRoot()` y policy BD-J.
