# SUNJCE público PS4 13.50→13.52 — sesión final 31

**Autor:** Manus AI  
**Método:** búsqueda y análisis estático de fuentes públicas; no se usó hardware, no se ejecutaron exploits ni artefactos de consola.

## Conclusión ejecutiva

La búsqueda final no encontró ningún archivo `.class`, `.jar`, manifest, listado de filesystem o snapshot con bytes públicamente verificables que pueda atribuirse inequívocamente a PS4 13.50 o 13.52 y que permita reconstruir `RootCertManager.isSunJCEVerified()`, el origen de `sunjce_hash` o la presencia de `RSACipherAdaptor` en el provider retail.

Aparecieron dos fuentes públicas adicionales, pero ninguna aporta bytes retail 13.52:

1. `deepakmathi/BDJB/diff8.txt`, un diff histórico de listados MD5 de `bdjstack.jar` y clases extraídas para rangos antiguos `6.xx–7.xx` y `8.xx–11.xx`. El archivo no contiene `sunjce_provider.jar`, `RSACipherAdaptor`, `SunJCE`, `NONEwithRSA`, `sunjce_hash` ni etiquetas 13.50/13.52.
2. `oliverlietz/bd-j`, un proyecto genérico de herramientas de certificados y firma BD-J. No contiene runtime PS4 ni clases SUNJCE.

La línea queda cerrada como **bloqueada por ausencia de bytes retail verificables**.

## Artefactos nuevos auditados

| Fuente | Ruta/artefacto | Tamaño | SHA-256 | Firmware/procedencia | Clasificación |
|---|---|---:|---|---|---|
| [`deepakmathi/BDJB`][1] | `diff8.txt` en commit `491852e8cdd66b54166271413371bc65d1b4da07` | 221.217 bytes | `8c06c1149165d181af153038775c8a717d088cb5544550284b7f4d977a57ed6c` | Diff documental de listados históricos `6.xx–7.xx` y `8.xx–11.xx`; no 13.50/13.52 | `HISTORICAL_ONLY` |
| [`oliverlietz/bd-j`][2] | `DiscCreationTools/net.java.bd.tools.security/README.md` | Documento público; no runtime | No aplica | Herramientas genéricas BD-J para certificados, firmas JAR y `app.discroot.crt` | `DOCUMENTED_ONLY` |
| [`ajaysenr/HackerOne-Disclosed-Reports`][3] | `reports/3452696.md` | Documento público | No aplica | Mirror de reporte histórico BD-J 13.00–13.02; ya conocido y no evidencia 13.52 | `HISTORICAL_ONLY` |
| [`zecoxao/zecoxao.github.io`][4] | Repositorio público y directorios PS4/WebKit/JSC | Varios | No se identificó runtime SUNJCE | Repositorio de proyectos; no aparecen los JAR/classes objetivo | `DOCUMENTED_ONLY` |

## Análisis de `diff8.txt`

El archivo público tiene SHA-256 `8c06c1149165d181af153038775c8a717d088cb5544550284b7f4d977a57ed6c` y 221.217 bytes. Su contenido es un diff textual entre listados históricos de clases y hashes MD5, con rutas como:

```text
6.xx-7.xx/bdjstack.jar_out/...
8.xx-11.xx/bdjstack.jar_out/...
```

El archivo contiene referencias nominales a `RootCertManager` en el contexto histórico del listado, pero no contiene `isSunJCEVerified()`, `sunjce_hash`, `sunjce_provider.jar`, `RSACipherAdaptor`, `SunJCE`, `NONEwithRSA` ni un cuerpo de clase/bytecode. Las búsquedas exactas produjeron cero coincidencias de SUNJCE y cero coincidencias de las cadenas `13.50` y `13.52`.

Por tanto, `diff8.txt` permite confirmar que algunos snapshots históricos de `bdjstack.jar` fueron catalogados por clase y MD5, pero no permite identificar el provider SUNJCE ni extrapolar sus hashes a 13.50/13.52.

## Análisis de fuentes genéricas y mirrors

El README de `oliverlietz/bd-j` documenta `BDCertGenerator`, `BDSigner` y `BDCredentialSigner`, así como la creación de `app.discroot.crt`, cadenas de certificados y firmas BD-J. Es material útil para el formato y la seguridad estándar de discos Blu-ray, pero no describe las clases propietarias de PS4 ni proporciona archivos runtime.

El mirror `ajaysenr/HackerOne-Disclosed-Reports/reports/3452696.md` reproduce el reporte histórico de BD-J nested-JAR y el flujo `BdjPolicyImpl → AllPermission`, pero no es un snapshot nuevo: no contiene JARs ni `.class` de 13.52 y su firmware declarado es 13.00–13.02.

El repositorio de zecoxao contiene proyectos públicos de PS4/PS5, WebKit y JSC, pero el índice del repositorio no muestra `sunjce_provider.jar`, `RootCertManager.class`, `BdjPolicyImpl.class`, `bdjstack.jar` ni `rt.jar`. La existencia de directorios WebKit/JSC no constituye evidencia de runtime BD-J 13.52.

## Resultado de búsqueda de código

La API de búsqueda de código de GitHub devolvió:

| Consulta | Resultado relevante |
|---|---|
| `isSunJCEVerified` | 0 coincidencias |
| `sunjce_hash` | 0 coincidencias |
| `sunjce_provider.jar` | Muchas coincidencias genéricas; ninguna identificada como provider retail PS4 |
| `RSACipherAdaptor` | Coincidencias en OpenJDK y forks de JDK; ninguna identificada como PS4 |
| `RootCertManager` | Coincidencias genéricas y mirrors del reporte 3452696; ninguna clase retail 13.52 |

Las coincidencias de `RSACipherAdaptor` corresponden al código estándar OpenJDK o derivados de JDK. No son evidencia de que el mismo archivo exista en `sunjce_provider.jar` de PS4 13.52.

## Cadena SUNJCE: estado final

| Eslabón | Estado | Evidencia disponible |
|---|---|---|
| `BdjPolicyImpl` llama a `RootCertManager.isSunJCEVerified()` | Documentado históricamente | Fragmentos públicos de PSDevWiki y reporte BD-J histórico |
| `isSunJCEVerified()` es estático y booleano | Inferencia del uso en un `if` | Fragmento documental; no descriptor ni bytecode |
| `sunjce_hash` cambia entre 13.50 y 13.52 | Evidencia pública indirecta fuerte | Captura pública de `RootCertManager.java` |
| Algoritmo del digest | No resuelto | No hay cuerpo público del método |
| Bytes de entrada | No resuelto | No hay `MessageDigest`/stream/caller retail |
| Provider retail 13.50 | No encontrado | No hay JAR verificable |
| Provider retail 13.52 | No encontrado | No hay JAR verificable |
| `RSACipherAdaptor` en provider 13.52 | No demostrado | Sólo afirmación comunitaria y referencia OpenJDK |
| Caller que conecte `RootCertManager` con `RSACipherAdaptor` | No encontrado | Sin bytecode ni diff textual |
| Cadena causal completa | No demostrada | Falta el runtime retail |

## Pieza mínima restante

Para pasar de `UNVERIFIED` a una comparación real se necesita al menos uno de los siguientes artefactos con procedencia inequívoca de 13.50 y/o 13.52:

- `sunjce_provider.jar` completo, con tamaño y SHA-256;
- `RootCertManager.class` o decompilación completa que incluya `isSunJCEVerified()`;
- `bdjstack.jar` con la variante exacta de `BdjPolicyImpl` y sus callers;
- manifest/listado de filesystem que vincule esos archivos con la build 13.50/13.52;
- diff textual o bytecode que muestre el algoritmo, bytes de entrada y comparación contra `sunjce_hash`.

Sin uno de estos artefactos, no es posible distinguir si `sunjce_hash` mide el JAR completo, una clase, una firma, un certificado, un manifest o cualquier otro recurso; tampoco es posible demostrar que `RSACipherAdaptor` esté presente en la build PS4.

## Cierre

No se encontró ningún artefacto nuevo `DIRECT_13.52` ni `STRONG_INDIRECT_13.52` que permita reconstruir la implementación de SUNJCE. La afirmación sobre `RSACipherAdaptor` permanece `DOCUMENTED_ONLY`/`UNVERIFIED` para PS4, y el cambio de `sunjce_hash` permanece evidencia de modificación, no evidencia del mecanismo causal.

Esta línea de investigación debe cerrarse como **BLOCKED: ausencia de bytes retail públicos y verificables**. Repetir búsquedas de nombres, repositorios genéricos o código OpenJDK no reduciría la incertidumbre actual.

## Referencias

[1]: https://github.com/deepakmathi/BDJB/blob/491852e8cdd66b54166271413371bc65d1b4da07/diff8.txt "deepakmathi/BDJB — diff8.txt"

[2]: https://github.com/oliverlietz/bd-j/blob/master/DiscCreationTools/net.java.bd.tools.security/README.md "oliverlietz/bd-j — BD-J security tools"

[3]: https://github.com/ajaysenr/HackerOne-Disclosed-Reports/blob/17ff7c9eb72a33429d04269c2a35285d0a67eace/reports/3452696.md "Mirror del reporte HackerOne 3452696"

[4]: https://github.com/zecoxao/zecoxao.github.io "zecoxao/zecoxao.github.io"

[5]: https://github.com/openjdk/jdk/commit/35dabb1a5f31d985f00de21badeeedb026a63b94 "OpenJDK 8244336 — RSACipherAdaptor"

[6]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&action=raw&section=51 "PSDevWiki — SUNJCE/RootCertManager"

[7]: https://x.com/notnotzecoxao/status/2066944047944446366 "Jose Coixao — captura pública de RootCertManager"

[8]: https://x.com/ps3120/status/2070144817233789048 "@ps3120 — afirmación sobre RSACipherAdaptor"
