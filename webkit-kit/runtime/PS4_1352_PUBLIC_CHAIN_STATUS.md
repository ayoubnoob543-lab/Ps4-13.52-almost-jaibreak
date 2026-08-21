# Estado público verificable de la cadena PS4 13.52

**Autor:** Manus AI  
**Ámbito:** fuentes públicas y análisis estático. No se utilizó hardware, no se ejecutaron exploits, payloads, JAR/ELF/BIN ni artefactos de consola.

## Resumen

La investigación confirma que la entrada BD-J histórica y la frontera Java→native usermode son conceptualmente distintas. Existe código público histórico donde una API BD-J resuelve símbolos nativos con `dlsym` y los invoca mediante `call`, pero ese código está identificado como firmware 13.04. También existen afirmaciones y metadatos parciales recientes para 13.50/13.52, pero no una implementación pública reproducible que conecte BD-J 13.52 con WebKit userland, escape de sandbox, kernel RCE y HEN.

La cadena pública queda así:

```text
BD-R / Blu-ray Player
        ↓
BD-J Java userland                         DOCUMENTED_ONLY para 13.52
        ↓
API histórica Java → dlsym/call             DIRECT_13.04
        ↓
WebKit/JSC userland 13.52                  DOCUMENTED_ONLY / UNVERIFIED
        ↓
Primitive de memoria                       UNVERIFIED
        ↓
Escape de sandbox                          UNVERIFIED
        ↓
Kernel exploit 13.52                       UNVERIFIED
        ↓
HEN / Linux Loader v25                     UNVERIFIED como cadena pública completa
```

## Evidencia BD-J

El repositorio [`adri22235/ps4-suid-scanner`][1] incluye `SuidScanner.java`, un scanner que el propio proyecto identifica como BD-JB para FW 13.04. El código contiene la siguiente interfaz histórica:

```java
api = API.getInstance();
openAddr = api.dlsym(API.LIBC_MODULE_HANDLE, "open");
closeAddr = api.dlsym(API.LIBC_MODULE_HANDLE, "close");
getdentsAddr = api.dlsym(API.LIBC_MODULE_HANDLE, "getdents");
statAddr = api.dlsym(API.LIBC_MODULE_HANDLE, "stat");
writeAddr = api.dlsym(API.LIBC_MODULE_HANDLE, "write");
long fd = api.call(openAddr, pathBuf, O_RDONLY);
long nread = api.call(getdentsAddr, fd, dentsBuf, DENTS_BUF_SIZE);
```

Esto demuestra que, en el entorno histórico 13.04, la frontera Java→native usermode podía expresarse como resolución de símbolos y llamadas nativas. No demuestra que `org.bdj.api.API`, `dlsym`, `call`, `LIBC_MODULE_HANDLE` ni la misma validación sobrevivan en 13.52. La clasificación correcta es `DIRECT_13.04` y `UNVERIFIED` para 13.52.

El mismo repositorio contiene `scanner_1304.iso`, offsets completos 13.04 y un archivo `1352_offsets.txt` parcial. El ISO no es 13.52 y no se ejecutó.

## Evidencia reciente 13.50/13.52

El archivo público [`1352_offsets.txt`][2] declara cinco valores parciales: `PRISON0=0x111FA18`, `ROOTVNODE=0x2136E90`, `SYSENT=0x110A760`, `unknown1=0x4D6D0` y `unknown2=0xE6C60`. El propio archivo dice “PARTIAL”, atribuye el origen a un desarrollador anónimo vía Shunsui y exige verificación adicional. No incluye dump, build ID, módulo WebKit, método de extracción ni exploit. Es `STRONG_INDIRECT_13.52` como metadata declarada, no `DIRECT_13.52`.

El archivo [`webkit_gadgets_1350.js`][1] contiene dos gadgets marcados como `partial match` y comentarios que mencionan una supuesta `libSceNKWebKit.sprx.decrypted (68 MB)`. La librería no está incluida en el repositorio. Por ello no existen bytes que permitan validar los gadgets, ni una base para extrapolar 13.52. Clasificación: `DOCUMENTED_ONLY`/`UNVERIFIED`.

El README del repositorio atribuye a MasterMaind/ASaudidos una confirmación de BD-J sandbox escape hasta 13.50/13.52, pero no adjunta ISO final, código del puente, hashes, offsets completos ni artefacto reproducible. Clasificación: `DOCUMENTED_ONLY`.

El vídeo titulado “PS4 13.52 BD-J USERLAND BUG PROOF OF CONCEPT” muestra una afirmación pública de POC, pero la página no expone código, ISO, build ID, hashes, primitivas ni cadena kernel. Clasificación: `DOCUMENTED_ONLY`, no `DIRECT_13.52`.

## WebKit/JSC userland

La guía Synacktiv sobre el PS4 6.xx documenta un WebKit UAF en `WebCore::ValidationMessage::buildBubbleTree`, su conversión a read/write y la necesidad posterior de un sandbox bypass y kernel exploit [3]. Es una demostración histórica directa de la arquitectura de una cadena WebKit, no una prueba de 13.52.

Los repositorios públicos de POCs de FreeType o WebKit, como [`The-Maxu/PS4-FreeType-WebKit-Poc`][4], aportan código o documentos históricos para otros rangos. El POC de FreeType declara que PS4 12.00 parecía usar FreeType 2.9.0, pero no demuestra 13.52 ni una cadena de ejecución.

La evidencia upstream de JSC —incluidos CVE-2020-9802, CVE-2022-42856, CVE-2023-32439 y `toReversed()`— permite reconstruir bugs y fixes en WebKit/JSC portable, pero no identifica la revisión retail PS4 13.52. La revisión pública `WebKit-601-1300` sólo está documentada para PS4 13.00–13.04. El árbol comunitario `WebKit-616-1300` es parcial y no contiene un árbol JSC completo ni metadata 13.52.

## Kernel y jailbreak

El reporte público de HackerOne #1340942 describe el bug exFAT de truncamiento `size_t`→`int` y su impacto en PS4/PS5 [5]. El repositorio [`pOOBs4`][6] implementa la cadena para PS4 9.00 y afirma que el bug fue corregido en 9.03. No es una ruta 13.52.

La guía pública BD-JB de ConsoleMods documenta Henloader hasta 12.52 y Lapse hasta 12.02 [7]. Un issue de `ps4-hen` para FW 13.50 aclara que la inyección de payload y el entrypoint no sustituyen un kernel exploit [8]. Esto corrobora la separación conceptual entre userland y kernel, pero no proporciona una cadena kernel pública 13.52.

PSDevWiki lista candidatos recientes etiquetados `<=13.50`/`<=13.52`, pero varias páginas individuales no pudieron verificarse de manera reproducible por falta de extracción o desafíos anti-bot. La página índice no basta para clasificar esos candidatos como explotables o confirmados.

## Matriz de estado

| Etapa | Evidencia pública | Resultado |
|---|---|---|
| Entrada BD-J en firmware reciente | Afirmaciones, POC visuales y herramientas históricas | `DOCUMENTED_ONLY` para 13.52 |
| Java userland | Código BD-J histórico y API pública 13.04 | `DIRECT_13.04`; `UNVERIFIED` 13.52 |
| Java→native usermode | `API.dlsym` + `API.call` en `SuidScanner.java` | `DIRECT_13.04`; `UNVERIFIED` 13.52 |
| WebKit/JSC userland 13.52 | Noticias, vídeos y referencias sin bytes | `DOCUMENTED_ONLY`/`UNVERIFIED` |
| WebKit primitive de memoria 13.52 | Ninguna implementación o testcase verificable | `UNVERIFIED` |
| Sandbox escape 13.52 | Afirmaciones comunitarias, sin artefacto reproducible | `DOCUMENTED_ONLY` |
| Kernel exploit 13.52 | Offsets parciales y candidatos no validados | `UNVERIFIED` |
| HEN completo 13.52 | No hay cadena pública reproducible | `UNVERIFIED` |
| Linux Loader v25 | Loader y kernel/initramfs conocidos; falta entrada nativa fiable | `INCOMPLETE` |

## Bloqueos exactos

El primer bloqueo técnico reproducible no es la existencia conceptual de BD-J ni la existencia histórica de `dlsym`/`call`. Es demostrar que el runtime y los límites de seguridad de PS4 13.52 permiten la misma interfaz, o una primitiva equivalente, y conectar esa primitiva con bytes WebKit/JSC o con una API nativa.

Para pasar de evidencia documental a una cadena 13.52 evaluable se necesita al menos uno de los siguientes artefactos legítimos y verificables: un ISO/loader BD-J 13.52 con hashes y código; un snapshot runtime BD-J 13.52; `libSceNKWebKit.sprx` 13.52 con build ID y hash; una implementación WebKit/JSC 13.52 con testcase y commit; o un writeup técnico que publique la primitiva, los límites de sandbox y la interfaz exacta que entrega native usermode.

No se debe usar `hen.bin`, offsets parciales o comentarios de gadgets como sustitutos de esos artefactos. Tampoco se debe confundir la evidencia histórica de exFAT 9.00 con 13.52.

## Conclusión actual

La parte BD-R→BD-J→Java userland parece públicamente avanzada, pero no existe una cadena pública reproducible completa desde una PS4 13.52 limpia hasta el Linux Loader v25. La evidencia pública más fuerte disponible para la pieza intermedia es la interfaz histórica `API.dlsym`/`API.call` en BD-J 13.04 y la metadata parcial de offsets 13.52. Ninguna de las dos demuestra la transición 13.52.

La investigación debe permanecer abierta si aparece un artefacto nuevo, pero el siguiente avance de alto valor no es buscar otra afirmación: es obtener un artefacto público verificable que muestre el runtime, la primitive nativa o la revisión WebKit/JSC específica de 13.52.

## Referencias

[1]: https://github.com/adri22235/ps4-suid-scanner "adri22235/ps4-suid-scanner"

[2]: https://github.com/adri22235/ps4-suid-scanner/blob/main/1352_offsets.txt "PS4 13.52 partial offsets"

[3]: https://synacktiv.com/publications/this-is-for-the-pwners-exploiting-a-webkit-0-day-in-playstation-4 "Synacktiv — Exploiting a WebKit 0-day in PlayStation 4"

[4]: https://github.com/The-Maxu/PS4-FreeType-WebKit-Poc "The-Maxu — PS4 FreeType WebKit POC"

[5]: https://hackerone.com/reports/1340942 "HackerOne #1340942 — exFAT size_t-to-int vulnerability"

[6]: https://github.com/ChendoChap/pOOBs4 "ChendoChap/pOOBs4"

[7]: https://consolemods.org/wiki/PS4:BD-JB "ConsoleMods — PS4 BD-JB"

[8]: https://github.com/Scene-Collective/ps4-hen/issues/66 "Scene-Collective/ps4-hen issue #66"


## Actualización: RemoteJarLoader y APIs nativas públicas

La auditoría de [`Gezine/BD-JB5`][9] permite separar tres mecanismos que a menudo se confunden. `RemoteJarLoader` escucha en TCP/9025, recibe un JAR, lo guarda en `/download0/received.jar`, lee `Main-Class` y lo ejecuta mediante `URLClassLoader` y reflexión. `InternalJarLoader` carga `/disc/payload.jar` de forma local. Ninguno de estos dos componentes constituye por sí mismo un escape de sandbox.

El mismo repositorio publica `NativeInvoke`, que resuelve `sceKernelSendNotificationRequest` mediante `API.dlsym` y lo llama con `API.call`, y `UnsafeInterface`, que expone lecturas/escrituras por dirección, asignación de memoria y `copyMemory`. El README exige una PS5 ya jailbroken para desparchear BD-J en firmwares superiores a 13.42. Esto confirma que el transporte remoto de JAR, el acceso Unsafe y la invocación nativa son eslabones distintos, y que el loader remoto no reemplaza el privilegio previo.

La clasificación es `DIRECT_PS5_13.42` para el diseño publicado; `UNVERIFIED` para PS4 13.52. No se debe convertir el código BD-JB5 en evidencia de una API disponible en Orbis PS4 13.52.

## Actualización: calidad de la metadata kernel 13.52

Los offsets públicos `1352_offsets.txt` se mantienen como metadata parcial: su propio texto indica origen anónimo, necesidad de verificación y ausencia de offsets adicionales. La tabla pública `remote_lua_loader` no contiene una entrada 13.50/13.52, y la mención comunitaria de 4PDA no aporta bytes ni procedencia independiente. La clasificación adecuada es `STRONG_INDIRECT_13.52` como indicio de metadata, no `DIRECT_13.52` como exploit o código kernel.

[9]: https://github.com/Gezine/BD-JB5 "Gezine — BD-JB5 para PS5"


## Hallazgo adicional: adaptación pública de BD-UN-JB para 13.52

El repositorio público [`Gezine/BD-UN-JB`][10] contiene el commit `fef9084ef18435cc451f2fb5039d88957ddc8f85`, fechado el 18 de junio de 2026, con el mensaje `Improve success rate of poops, Add PS4 13.52 offsets`. En `payloads/poops/src/org/bdj/external/PS4_KernelOffset.java` añade una entrada `13.52` distinta de `13.50` y un bloque `ShellcodeData` separado para esa versión. Un segundo commit relacionado es `40276274a7fe3419e03354f6d65ba1fa20c696bd`.

Esto cambia la evaluación de la etapa kernel: existe un artefacto de software público etiquetado 13.52 con offsets y código de soporte. La clasificación es `DIRECT_13.52` para la presencia del bloque en el repositorio; la reproducibilidad efectiva, la procedencia interna de cada valor y la ejecución en hardware siguen `UNVERIFIED`. El commit no demuestra por sí mismo la entrada BD-J 13.52, el escape de sandbox, WebKit 13.52 ni la entrega al Linux Loader.

[10]: https://github.com/Gezine/BD-UN-JB/commit/fef9084ef18435cc451f2fb5039d88957ddc8f85 "Gezine/BD-UN-JB — Add PS4 13.52 offsets"


## Candidato WebKit más fuerte: CSSFontFace UAF

El repositorio público [`ntfargo/CSSFontFace-Exploit`][11] y su writeup técnico [12] ofrecen la cadena estática más completa encontrada para WebKit: causa raíz en referencias no propietarias de `CSSFontFace`, reentrada durante la resolución de promesas, corrección mediante `Ref<CSSFontFace>` y una primitive de memoria documentada en versiones concretas.

La evidencia debe dividirse cuidadosamente. El README declara `Vulnerability Scope: PS4 6.00–13.52`, pero también declara `Exploitable In This Repository: PS4 6.00–11.02` y explica que desde 11.5x se rediseñó el layout CSSFontFace, incluyendo `m_propertiesOrCSSConnection`, por lo que la primitive `m_featureSettings` ya no funciona sobre esas versiones. El writeup describe el UAF y la transición hacia disclosure/read-write, pero no publica una primitive operativa para 13.52.

| Pregunta | Resultado |
|---|---|
| ¿Existe bug WebKit con alcance declarado hasta 13.52? | Sí, según el README del repositorio; `STRONG_INDIRECT_13.52` |
| ¿Existe primitive reproducible publicada para 13.52? | No; `UNVERIFIED` |
| ¿Se conoce la causa raíz y el fix de ownership? | Sí, en código/documentación upstream; `DOCUMENTED_ONLY` |
| ¿Se demuestra que Sony dejó intacta la condición en 13.52? | No |
| ¿Se demuestra RCE, sandbox escape o native usermode en 13.52? | No |

El caso CSSFontFace no permite cerrar la cadena solicitada, pero sí reduce el espacio de búsqueda: el mismo bug puede abarcar versiones nuevas sin que sobreviva la primitive histórica. Para PS4 13.52 faltan la revisión WebKit retail, el layout exacto de `CSSFontFace`, una demostración de la condición de vida útil y una primitive segura y reproducible; no se desarrollará ni adaptará una explotación.

## Estado revisado de WebKit-616-1300

La colección OSS `FreeBSDKernel9-0/PS4OSSCode` contiene un directorio `WebKit-616-1300`, pero la navegación directa sólo muestra `LayoutTests`, `WebKit.xcworkspace`, `WebKitLibraries` y `resources`; no contiene `Source/JavaScriptCore`, `Source/WebCore` ni `JSArray.cpp`. Su nombre no permite identificarlo como WebKit/JSC de PS4 13.52.

[11]: https://github.com/ntfargo/CSSFontFace-Exploit "ntfargo/CSSFontFace-Exploit"
[12]: https://linearfox.com/blog/cssfontface-uaf-playstation "From CSSFontFace to ARW: A PlayStation Webkit Exploit Writeup"


## Actualización: fork ps3120 y estado de la primitive CSSFontFace

El fork público [`ps3120/CSSFontFace-Exploit`][13] fue creado el 28 de junio de 2026 y contiene commits posteriores hasta el 4 de julio de 2026, entre ellos `Update offsets.mjs` (`7a0b599064c84ae78aef84913aee0082bfab5272`), `Update userland.mjs` (`dfa2e2fc5a3b58da07092dfa3e8ec3df2167c9a6`) y `Update lapse.mjs` (`33650b33984188cf76229251caea7d1f450c1455`).

El fork conserva la misma matriz probatoria que el repositorio original: `Vulnerability Scope` PS4 6.00–13.52, pero `Exploitable In` PS4 6.00–11.02; el soporte real del repositorio se declara para PS4 9.00. Sus actualizaciones públicas no añaden un testcase, layout, offsets de WebKit o primitive para 13.52. Logic-Sunrise reproduce la misma limitación y el hilo público sobre un supuesto workaround para firmwares altos afirma que todavía no está publicado [14] [15].

Por tanto, la mejor evidencia actual no es una primitive 13.52, sino una **demostración pública de que la primitive histórica deja de ser utilizable después del rediseño 11.5x**. Esto convierte el siguiente objetivo seguro en identificar una implementación o documentación pública del nuevo layout, no en adaptar una explotación.

[13]: https://github.com/ps3120/CSSFontFace-Exploit "ps3120/CSSFontFace-Exploit"
[14]: https://www.logic-sunrise.com/news-1221608-ps4ps55-cssfontface-exploit-un-nouvel-exploit-webkit-ps4-et-ps5-par-ntfargo.html "Logic-Sunrise — CSSFontFace Exploit"
[15]: https://www.reddit.com/r/ps4homebrew/comments/1vsm1de/webkit_for_above_11.02_meaning_11.5x_and_12.xx_and/ "Public discussion of an unpublished high-firmware workaround"
