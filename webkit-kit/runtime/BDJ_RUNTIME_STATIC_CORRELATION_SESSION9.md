# Correlación estática BD-J/JVM 13.52 — Sesión 9

## Objetivo y límite

Esta es una auditoría independiente de los artefactos que están realmente disponibles en el workspace y en el repositorio publicado. Se compara la hipótesis histórica de `bd-jb` con evidencia local vinculada a 13.52, pero no se ejecutan JAR, ELF/BIN, código nativo, payloads ni hardware.

La regla de esta auditoría es estricta: un nombre de clase, un método histórico o una captura pública no se considera evidencia de que el mismo componente exista en PS4 13.52.

## Resultado ejecutivo

No hay artefactos runtime PS4 13.52 verificables en el corpus actual. No aparecen `rt.jar`, `bdjstack.jar`, `sunjce_provider.jar`, `RootCertManager.class/.java`, `BdjPolicyImpl.class/.java`, un módulo JVM/BD-J ni metadata de símbolos nativos de esa build.

Por ello, la cadena no puede confirmarse en ningún punto específico de 13.52. El **primer punto no verificado es la existencia y el contrato exacto del runtime Java/JVM de 13.52**; todo análisis posterior de `Unsafe`, `NativeLibrary`, símbolos o compiler-agent permanece sin base directa.

## Cadena evaluada

```text
BD-J
  → permisos / sandbox escape
  → reflection
  → Unsafe o equivalente
  → ClassLoader$NativeLibrary.find/findEntry
  → resolución de símbolos nativos
  → compiler-agent/JIT
  → memoria/entrypoint nativo
```

| Etapa | Evidencia 13.52 disponible | Estado |
|---|---|---|
| Xlet/JAR BD-J y permisos iniciales | No hay runtime ni salida de consola 13.52 | **UNVERIFIED** |
| Sandbox escape | No hay artefacto ni log de reproducción | **UNVERIFIED** |
| Reflection sobre clases internas | Sólo cliente histórico; no runtime 13.52 | **UNVERIFIED** |
| `sun.misc.Unsafe` o equivalente | No hay `rt.jar`/clases bootstrap 13.52 | **UNVERIFIED** |
| `ClassLoader$NativeLibrary.find/findEntry` | Sólo código cliente histórico; no clase 13.52 | **UNVERIFIED** |
| Símbolos/API nativas referenciables | No hay módulo JVM/BD-J 13.52 ni tabla de exports | **UNVERIFIED** |
| Compiler-agent/JIT | Sólo implementación cliente histórica; no agente 13.52 | **UNVERIFIED** |
| Memoria/entrypoint nativo | No hay evidencia específica 13.52 | **UNVERIFIED** |

## Evidencia local disponible

### Código histórico de `bd-jb`

El checkout local de `TheOfficialFloW/bd-jb` tiene HEAD `8a31b642375f320681aebf5c1fbb00b06c321fb4`. El archivo `API.java` histórico contempla ramas JDK 8/JDK 11 y busca `ClassLoader$NativeLibrary.find(String)` o `findEntry(String)`. También adapta `Unsafe` y resuelve símbolos nativos mediante una interfaz específica del cliente.

SHA-256 local de `API.java`: `651a098aa26f9bb73225c9b1c584803ea1e5140dae535c427c4fb96cf9028925`.

Esto es evidencia **HISTORICAL/STRUCTURAL**. No demuestra que PS4 13.52 exporte esos métodos o símbolos.

### Implementación histórica del compiler-agent

`JitCompilerReceiverImpl` y `JitDefaultImpl` están conservados como notas extraídas del commit público `f480a063ab6bf4c79c065a48934458b7c5eb2154`.

`JitCompilerReceiverImpl` representa un cliente de un protocolo privado del runtime compiler-agent; `JitDefaultImpl` representa una ruta basada en APIs legítimas `sceKernelJit*`. Ninguno es el runtime de 13.52 ni contiene bytes de la JVM/BD-J Sony.

Hashes de las notas históricas:

- `historical_JitCompilerReceiverImpl.java`: `4c4c557d488c7339960fd842c789798e04ad4a1eacfc66275b9238c1a1a4c5da`.
- `historical_JitDefaultImpl.java`: `9fd12a93c6424c10dfa3d721292e79a10c3e7f15ed5d4cf84b6b9ad9216d54ee`.

Clasificación: **HISTORICAL**, no específica de 13.52.

### Capturas de cambios de política/hash

Las capturas públicas previamente conservadas muestran un cambio de literal en `RootCertManager` y la eliminación de un bloque de política histórico relacionado con `CodeSource`/`AllPermission`. No son archivos fuente ni bytes de 13.52 y no permiten analizar `Unsafe`, `NativeLibrary`, compiler-agent o JIT.

Hashes:

- `rootcertmanager_changed.webp`: `667cca7f00a5a404fea741535415537280d984315c9044131d5e1e03db13062f`.
- `rootcertmanager_hash_left.png`: `2903d56a6724cd47d3f5de44c6e933531418c0adf222022642a88ff3996dbd13`.
- `rootcertmanager_hash_right.png`: `89467d3074739f2f5006e8f706c3c834ce0bb17aed610a27c97fc18fb973ff61`.

Clasificación: **DOCUMENTED_ONLY / STRUCTURAL** respecto a la comparación pública; no evidencia directa suficiente para el runtime completo 13.52.

## ¿Existe una mitigación 13.52 demostrable?

No puede demostrarse una mitigación específica de la cadena JVM/JIT porque no están disponibles los componentes que habría que comparar. El cambio público de política/hash no prueba por sí mismo que se hayan eliminado `Unsafe`, `NativeLibrary`, el compiler-agent o las APIs legítimas `sceKernelJit*`.

La única conclusión firme es negativa: **el corpus actual no contiene el material necesario para distinguir entre conservación, modificación o eliminación de esas interfaces en 13.52**.

## Ruta alternativa identificable

No aparece una ruta alternativa específica de 13.52. La existencia histórica de APIs legítimas de JIT no equivale a una primitive arbitraria; la existencia histórica de `Unsafe`/reflection no equivale a accesibilidad actual. Sin metadata 13.52 no se puede elegir entre:

1. una cadena histórica aún compatible;
2. una variante adaptada a nuevos layouts/símbolos;
3. una ruta Java distinta;
4. una mitigación completa de la frontera nativa.

Todas permanecen **UNVERIFIED**.

## Primer punto no verificado y artefacto faltante

El primer punto no verificado es:

> **¿Qué clases bootstrap y qué contrato JVM/BD-J existen realmente en PS4 13.52?**

El artefacto mínimo para resolverlo sería una copia autorizada y hasheada de `rt.jar` y/o `bdjstack.jar` de 13.52, con su procedencia. Para continuar hasta native usermode harían falta además:

- bytecode de `ClassLoader$NativeLibrary` y `Unsafe`;
- lista de métodos/signaturas y restricciones de acceso;
- tabla de símbolos del módulo JVM/BD-J;
- evidencia estática del compiler-agent y su protocolo, si existe;
- metadata de `sceKernelJit*` si se evalúa la ruta legítima.

## Conclusión

La cadena histórica queda completamente **HISTORICAL/STRUCTURAL** y no puede promoverse a `CONFIRMED_13.52`. El primer bloqueo no está en un símbolo concreto, sino en la ausencia del propio runtime Java/JVM de 13.52. No hay evidencia suficiente para afirmar vulnerabilidad, compatibilidad, mitigación ni ruta alternativa.

## Referencias

[1]: https://github.com/TheOfficialFloW/bd-jb "TheOfficialFloW/bd-jb"

[2]: https://github.com/kimariin/BlueLoader "BlueLoader"

[3]: https://github.com/ayasns/BD-JB-1250 "BD-JB-1250"

[4]: https://github.com/john-tornblom/bdj-sdk "BDJ-SDK"
