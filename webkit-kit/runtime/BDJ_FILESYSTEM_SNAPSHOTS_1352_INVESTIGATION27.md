# Investigación 27 — Snapshots públicos del filesystem BD-J/JVM PS4 13.52

**Autor:** Manus AI  
**Fecha:** 2026-08-21  
**Repositorio:** `webkit-ps4-1352-kit`  
**Alcance:** búsqueda y análisis estático de snapshots públicos; no se ejecutaron artefactos, exploits, payloads, JAR/ELF/BIN ni hardware.

## Conclusión ejecutiva

No se encontró ningún snapshot público derivado del filesystem BD-J/JVM que pueda atribuirse inequívocamente a PS4 13.52. En particular, no se encontró un `bdjstack.jar`, `rt.jar`, `sunjce_provider.jar` ni una clase `RootCertManager`, `BdjPolicyImpl`, `PSDescriptorFactory`, `XletClassLoader` o `BDJFactory` con procedencia demostrable de esa build.

Se localizaron dos clases de material cercano:

1. **Snapshots históricos/genéricos** de `bdjstack.jar` en `deepakmathi/BDJB`, etiquetados `12.xx` y `13.xx`, sin subversión PS4 ni vínculo 13.52.
2. **Herramientas públicas de adquisición**, especialmente BlueLoader `fsdump`, cuyo README explica cómo obtener `app0/bdjstack/bdjstack.jar` y `app0/bdjstack/lib/rt.jar` desde una ejecución en PS4. El repositorio y sus releases no contienen esos archivos ni un snapshot 13.52.

Por tanto, la respuesta final es:

> **No se ha pasado de “referencia pública” a “snapshot BD-J/JVM 13.52 analizable”. El primer punto sin evidencia sigue siendo la disponibilidad de un filesystem/runtime atribuido inequívocamente a PS4 13.52.**

## Artefactos encontrados

### `deepakmathi/BDJB`

Fuente: [repositorio `deepakmathi/BDJB`][1]  
Commit auditado: `491852e8cdd66b54166271413371bc65d1b4da07`.

| Artefacto | Tamaño | SHA-256 | Procedencia | Firmware aceptable |
|---|---:|---|---|---|
| `12.xx/bdjstack.jar` | 874.506 bytes | `96177957170728122b92ddf7f9a95a88314b55948dbab04886f75a9b308cd948` | Snapshot público del repositorio | Etiqueta genérica `12.xx`; no PS4 13.52 |
| `13.xx/bdjstack.jar` | 875.130 bytes | `96c0f1c001dfb90c33052ca2448f588a6d7f8f5cb43ab54152d9db4082172986` | Snapshot público del repositorio | Etiqueta genérica `13.xx`; no subversión ni PS4 13.52 demostrada |
| `13.xx/.../RootCertManager.class` | 7.044 bytes | `b2a8776617a85dfc0b4ef09b09ce0e1bea7a479298ae5b714105030d3d9c4977` | Entrada del snapshot `13.xx` | No atribuible a 13.52 |

Los JARs `12.xx` y `13.xx` tienen 987 clases, manifiestos equivalentes y la misma lista de nombres de entradas. Sus manifests contienen únicamente metadatos Java/Ant:

```text
Manifest-Version: 1.0
Ant-Version: Apache Ant 1.8.2
Created-By: 1.4.2_19-b04 (Sun Microsystems Inc.)
```

No aparecen `sunjce_provider.jar`, `RSACipherAdaptor`, `SunJCE`, `NONEwithRSA` ni una entrada separada de provider. La clase `RootCertManager.class` sí contiene referencias a `MessageDigest`, `digest`, `SHA1withRSA`, `KeyStore` y certificados, pero no contiene los literales `sunjce_hash` o `isSunJCEVerified`.

**Clasificación:** `HISTORICAL_ONLY` / `UNVERIFIED` para PS4 13.52. Estos archivos no deben usarse como sustitutos de runtime 13.52.

### BlueLoader y `fsdump`

Fuente: [kimariin/BlueLoader][2], commit auditado `5b7d73b67b52944d5dc61df0f7738d23f10bb7d3`.

El README documenta una aplicación BD-J y un payload `fsdump` que puede volcar por ZIP los archivos visibles al proceso JVM. El propio README indica que, después de obtener el ZIP, se pueden extraer:

```text
app0/bdjstack/bdjstack.jar
app0/bdjstack/lib/rt.jar
```

El repositorio contiene sólo `thirdparty/topsecret/README.txt`; no contiene `bdjstack.jar` ni `rt.jar`. El README identifica esos archivos como datos que deben recuperarse desde una PS4, o desde un paquete descifrado histórico 7.00. No afirma soporte 13.52 y no incluye snapshot del firmware.

Las releases públicas contienen ISO/payloads/fsdump, no runtime:

| Release | Assets | Hashes relevantes |
|---|---|---|
| v0.1 | `blueloader.iso`, `payload.jar` | ISO `7ddb0b10f2807fd6d2e73f12c85156731014c70d399589a662897f015a27292f`; payload `989de76c03d794bb9a24a92b6002b159649f21509f1ad4c268f7a39f0a2c7a85` |
| v0.2 | `blueloader.iso`, `fsdump.jar`, `lapse.jar` | ISO `9f1380cda553bf9a81c9f1e0801a68e871a87a51eb6e2c6e3da5dbf2bb8b3a34`; fsdump `b0a14d5055c58d750149e35f77e1097fdf8454759602017e9400268cd5d21325` |
| v0.3–v0.6 | ISO, `fsdump.jar`, `lapse.jar` | Sin `bdjstack.jar`, `rt.jar` o `sunjce_provider.jar` |

El mecanismo `fsdump` es, por tanto, una **ruta pública documentada de adquisición**, no un snapshot público ya disponible. La obtención requiere ejecución en hardware, que queda fuera del alcance de esta investigación.

**Clasificación:** `DOCUMENTED_ONLY`; no evidencia directa de 13.52.

### BD-JB-1250 y repositorios relacionados

Se revisaron [dptug/BD-JB-1250-lapse][3] y [mbcrump/PS4900Linux][4]. El primero redirige además a un repositorio `ayasns/BD-JB-1250` y su README declara soporte de hasta PS4 12.50. Contiene dependencias esperadas de `bdjstack.jar` y `rt.jar` en el classpath, pero no incluye esos runtime. No contiene referencias verificables a PS4 13.52.

`PS4900Linux` contiene material histórico de PS4/Linux y BD-J, pero no un snapshot BD-J/JVM 13.52 ni los archivos objetivo con procedencia de esa build.

**Clasificación:** `HISTORICAL_ONLY` / `DOCUMENTED_ONLY`.

## Clases y métodos solicitados

| Elemento | Encontrado | Firmware atribuible | Resultado estático |
|---|---|---|---|
| `bdjstack.jar` | Sí, `deepakmathi/BDJB` | `12.xx`/`13.xx` genérico | No es 13.52 inequívoco |
| `rt.jar` | No | Ninguno | Falta runtime |
| `sunjce_provider.jar` | No | Ninguno | Falta provider |
| `RootCertManager.class` | Sí, snapshot `13.xx` | No PS4 13.52 demostrado | Sin `sunjce_hash`/`isSunJCEVerified` |
| `BdjPolicyImpl.class` | No snapshot 13.52 | Ninguno | No disponible |
| `PSDescriptorFactory.class` | No snapshot 13.52 | Ninguno | No disponible |
| `XletClassLoader.class` | No snapshot 13.52 inequívoco | Ninguno | No disponible |
| `BDJFactory.class` | No snapshot 13.52 inequívoco | Ninguno | No disponible |
| `com.sony.bdjstack.security.*` | Parcial en snapshots históricos | No 13.52 | Sólo precedente histórico |
| `RSACipherAdaptor.class` | No | Ninguno | `UNVERIFIED` para PS4 13.52 |
| `SunJCE.class` | No | Ninguno | `UNVERIFIED` para PS4 13.52 |

## Comparación 13.50→13.52

No puede realizarse una comparación real 13.50→13.52 porque no existe ningún par de snapshots con esas procedencias. Sólo se dispone de la afirmación pública y captura que muestran un cambio de la constante `sunjce_hash` en `RootCertManager.java`.

La evidencia no permite reconstruir:

```text
RootCertManager
  → isSunJCEVerified()
  → algoritmo y bytes hasheados
  → sunjce_hash
  → sunjce_provider.jar
```

Tampoco permite demostrar que `RSACipherAdaptor` exista en el provider 13.52 o que no existiera en 13.50. Una afirmación comunitaria sobre su adición queda clasificada como `INDIRECT_13.52` débil hasta disponer de la clase, manifest, inventario o bytecode de la build correspondiente.

## Primer punto sin evidencia

El primer punto no verificable no es el nombre de una clase concreta, sino la **cadena de procedencia del filesystem**:

```text
PS4 13.52 retail
  → filesystem BD-J/JVM identificado
  → bdjstack.jar / rt.jar / sunjce_provider.jar
  → clases y bytecode verificables
```

BlueLoader demuestra que una herramienta puede producir un ZIP de archivos visibles al JVM, pero el repositorio no contiene un resultado 13.52. `deepakmathi/BDJB` demuestra que existen snapshots históricos públicos, pero sus etiquetas no vinculan la carpeta `13.xx` con PS4 13.52.

## Resultado obligatorio

- **Artefactos encontrados:** snapshots genéricos `bdjstack.jar` 12.xx/13.xx, clases históricas `RootCertManager`, herramientas BlueLoader/fsdump y repositorios BD-JB históricos.
- **Procedencia exacta:** commits y URLs documentados arriba; ninguna procedencia identifica PS4 13.52.
- **Firmware:** 12.xx/13.xx genérico, BD-JB hasta 12.50, BlueLoader sin soporte 13.52 demostrado.
- **Hashes:** incluidos para los JARs públicos y releases de BlueLoader.
- **Clases/métodos relevantes:** `RootCertManager` histórico contiene digest/certificados, pero no `sunjce_hash` ni `isSunJCEVerified`.
- **Diferencias 13.50→13.52:** no comparables por ausencia de snapshots; sólo cambio de constante documentado indirectamente.
- **Objeto hasheado:** no identificable.
- **`RSACipherAdaptor`:** no demostrable en PS4 13.52.
- **Primer punto sin evidencia:** snapshot/runtime BD-J/JVM con procedencia inequívoca de PS4 13.52.

## Conclusión

La investigación no encontró un filesystem BD-J/JVM PS4 13.52 públicamente accesible y verificable. Encontró únicamente **material histórico y herramientas de adquisición**. En consecuencia, no se puede analizar de forma válida `isSunJCEVerified()`, el provider SUNJCE, `RSACipherAdaptor` ni el objeto que produce `sunjce_hash` para 13.52.

## Referencias

[1]: https://github.com/deepakmathi/BDJB/tree/491852e8cdd66b54166271413371bc65d1b4da07 "deepakmathi/BDJB, commit auditado"
[2]: https://github.com/kimariin/BlueLoader "kimariin/BlueLoader — BlueLoader y fsdump"
[3]: https://github.com/dptug/BD-JB-1250-lapse "dptug/BD-JB-1250-lapse"
[4]: https://github.com/mbcrump/PS4900Linux "mbcrump/PS4900Linux"
[5]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer Wiki — Vulnerabilities"
