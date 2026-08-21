# PSDescriptorFactory: `handles()` y `canWriteFile()`

## Alcance

Investigación estática de las dos entradas de PSDevWiki. No se descargaron PUPs/dumps privados ni se ejecutaron JAR/ELF/BIN, exploits o código contra hardware.

Las conclusiones distinguen `DIRECT_13.52`, `INDIRECT_13.52`, `HISTORICAL_ONLY`, `HYPOTHESIS` y `DISCARDED`.

## 1. `PSDescriptorFactory.handles(int, String)`

### Fuente y procedencia

La sección pública de PSDevWiki se recuperó mediante su editor de fuente:

`https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&section=39&action=edit`

Los créditos atribuyen el diff a `zecoxao`, comparando archivos BD-J PS5 12.00/13.00 compartidos por una fuente anónima, con fecha indicada de 2026-03-19. La sección compara además código de PS4 11.00 y PS3 4.92.

### Firma y código previo al parche

La fuente publica esta firma y flujo para `java/com/sony/gemstack/io/factories/ps/PSDescriptorFactory.java` en PS4 11.00 y PS3 4.92:

```java
public boolean handles(int i, String path) {
    if (tempDir != null && path.startsWith(tempDir)) {
        return false;
    }
    persistentRoot = (String) AccessController.doPrivileged(new PrivilegedAction(this) {
        private final PSDescriptorFactory this$0;
        {
            this.this$0 = this;
        }
        public Object run() {
            return System.getProperty("dvb.persistent.root", "/OS/persistent");
        }
    });
    if (path != null) {
        return path.startsWith(persistentRoot);
    }
    return false;
}
```

La variante PS5 12.70 publicada conserva la misma lógica, expresada como clase anónima compilada (`new 1(this)`). La operación relevante es una comparación de prefijo (`startsWith`) contra una raíz obtenida bajo `AccessController.doPrivileged`, con fallback a `"/OS/persistent"`.

### Cambio documentado

La variante posterior publicada para PS5 13.00 cambia la comparación final a:

```java
return var2 != null
    ? path.startsWith(RootCertManager.getOriginalPersistentRoot())
    : false;
```

La diferencia concreta es que deja de confiar directamente en la propiedad `dvb.persistent.root` y usa `RootCertManager.getOriginalPersistentRoot()`.

La sección declara editorialmente:

> Patched: Yes since PS4 FW ?13.50? and PS5 FW 13.00. Not patched as of PS4 FW 11.00, PS5 FW 12.70 and PS3 FW 4.92.

El signo de interrogación es parte esencial de la evidencia: el texto no aporta bytes PS4 13.50/13.52 ni una versión PS4 exacta del método parcheado.

### Caller y flujo demostrables

La fuente recuperada sólo publica el método `handles`; no publica caller, método de escritura posterior, formato de `userprefs` ni la relación exacta entre el valor booleano y una operación privilegiada. Por ello sólo puede afirmarse este flujo:

```text
caller desconocido
→ PSDescriptorFactory.handles(i, path)
→ exclusión si path empieza por tempDir
→ lectura privilegiada de dvb.persistent.root
→ comparación de prefijo con persistentRoot
→ booleano
```

No es válido completar el flujo como escritura o carga de clases sin una fuente adicional.

### Evaluación

| Propiedad | Resultado |
|---|---|
| Clase | `com.sony.gemstack.io.factories.ps.PSDescriptorFactory` |
| Método | `boolean handles(int i, String path)` |
| Ruta controlada | `path`, comparada con `tempDir` y `persistentRoot` |
| Validación histórica | Exclusión `tempDir` y prefijo de raíz configurable |
| Privilegio | Lectura de `dvb.persistent.root` bajo `AccessController.doPrivileged` |
| Firmware previo | PS4 11.00 y PS3 4.92; PS5 12.70 también aparece en la comparación |
| Mitigación documentada | Sustituir `persistentRoot` por `RootCertManager.getOriginalPersistentRoot()` |
| PS4 13.52 | No hay bytes ni diff; sólo rango editorial `?13.50?` |
| Clasificación | `HISTORICAL_ONLY`; `INDIRECT_13.52` débil sólo por la nota editorial |

La causa raíz histórica que sí puede demostrarse es **confianza en una raíz derivada de una propiedad configurable y comparación de prefijo**, no una vulnerabilidad completa de escritura o sandbox escape. La existencia de un caller que use un resultado `true` para una operación sensible no está publicada en esta sección.

## 2. `PSDescriptorFactory.canWriteFile()`

### Fuente y contenido disponible

La sección pública se recuperó mediante:

`https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&section=40&action=edit`

El contenido contiene únicamente los créditos:

```text
=== Credits ===
* zecoxao for diffing decompiled 12.00 and 13.00 PS5 BD-J files shared to him by an anonymous (2026-03-19)
```

También enlaza el tweet público:

`https://twitter.com/notnotzecoxao/status/2034585816186454272`

No contiene secciones `Analysis`, `Bug Description`, `Implementation` ni `Patched`.

### Lo que no puede determinarse

No hay fuente pública recuperada que establezca:

- la firma exacta de `canWriteFile()`;
- el caller;
- la ruta que recibe;
- si la ruta es `userprefs` u otro recurso;
- la validación ausente;
- el efecto de retorno `true`/`false`;
- la versión PS4/PS5/PS3 afectada;
- la mitigación;
- una variante posterior.

El índice de PSDevWiki sólo muestra el título `FW <= ?9.00? - PSDescriptorFactory.canWriteFile() does not check userprefs path`. Ese título es una pista editorial, no evidencia suficiente para reconstruir el método.

**Clasificación:** `HISTORICAL_ONLY / UNVERIFIED`. No existe base para `DIRECT_13.52` ni `INDIRECT_13.52`.

## 3. Comparación y relación con `userprefs`

`handles()` sí contiene una referencia explícita a la propiedad `dvb.persistent.root` y al fallback `/OS/persistent`; el texto no demuestra por sí solo que la operación sea `userprefs`. La asociación con `userprefs` procede del título de la sección, no del cuerpo del código.

`canWriteFile()` sólo se relaciona con `userprefs` por el título del índice. No hay código que permita confirmar o refutar esa relación.

## 4. ¿Existe una variante posterior documentada?

Para `handles()`, existe una variante posterior documentada en PS5 13.00 que usa `RootCertManager.getOriginalPersistentRoot()`. PSDevWiki atribuye editorialmente el parche a PS4 desde aproximadamente 13.50, pero no aporta el diff PS4 ni un hash de clase. Esto permite clasificar el cambio como **evidencia estructural/indirecta**, no como confirmación retail de PS4 13.52.

Para `canWriteFile()`, no existe variante posterior documentada en el contenido recuperado.

## 5. Tabla final

| Método | Firma/clase | Caller/flujo | Ruta/validación | Firmware histórico | Mitigación | Evidencia 13.52 | Clasificación |
|---|---|---|---|---|---|---|---|
| `handles` | `PSDescriptorFactory.handles(int, String)` | Sólo el método; caller no publicado | `tempDir`; `dvb.persistent.root`; comparación de prefijo | PS4 11.00, PS3 4.92; comparación PS5 12.70/13.00 | `RootCertManager.getOriginalPersistentRoot()` en PS5 13.00; PS4 `?13.50?` editorial | Ningún byte/diff PS4 13.52 | `HISTORICAL_ONLY`, con `INDIRECT_13.52` débil |
| `canWriteFile` | Firma no publicada | No recuperable | Ruta y validación no recuperables | Título `<= ?9.00?` | No documentada | Ninguna | `HISTORICAL_ONLY / UNVERIFIED` |

## 6. Conclusión

`PSDescriptorFactory.handles()` sí merece una investigación adicional limitada: hay una firma exacta, código histórico y un cambio concreto de implementación que sustituye una raíz configurable por `RootCertManager.getOriginalPersistentRoot()`. Sin embargo, la evidencia específica de PS4 13.52 sigue siendo insuficiente: la nota `?13.50?` no sustituye un diff, bytes, hash o manifest.

`PSDescriptorFactory.canWriteFile()` no merece aún una hipótesis técnica: la fuente pública actual sólo conserva el título y los créditos. El siguiente dato de mayor valor sería el wikitexto histórico de esa sección o el diff/decompilación PS5 12.00→13.00 al que alude el crédito.

Resultado final:

- **`handles()`**: superficie histórica real de validación de rutas; posible parche aplicado antes de 13.52 según nota editorial, pero `UNVERIFIED` para PS4 13.52.
- **`canWriteFile()`**: pista editorial sin cuerpo técnico; `HISTORICAL_ONLY / UNVERIFIED`.
- **No se demuestra** una variante PS4 13.52 que produzca escritura privilegiada, sandbox escape o carga de clases.

## Referencias

[1]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&section=39&action=edit — Wikitexto público de la sección `PSDescriptorFactory.handles()`.

[2]: https://www.psdevwiki.com/ps4/index.php?title=Vulnerabilities&section=40&action=edit — Wikitexto público de la sección `PSDescriptorFactory.canWriteFile()`.

[3]: https://www.psdevwiki.com/ps4/Vulnerabilities — Índice de vulnerabilidades PS4 BD-J.

[4]: https://twitter.com/notnotzecoxao/status/2034585816186454272 — Referencia pública de procedencia citada por PSDevWiki.
