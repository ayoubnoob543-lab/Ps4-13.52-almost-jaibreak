# Celsius / PS4 `ffs_mount`: investigación de procedencia y significado de “hasta 13.04”

**Fecha de corte:** 26 de agosto de 2026. **Método:** búsqueda pública en GitHub, Google, X, Reddit, PSDevWiki, noticias técnicas y fuentes de FreeBSD; análisis estático de artefactos locales. No se ejecutaron payloads ni corrupción de memoria contra hardware.

## Conclusión corta

La primera difusión pública que pude localizar es una publicación de **Dr.Yenyen (@calmboy2019) en X del 18 de julio de 2026 a las 18:37**, donde se presenta el nombre “Celsius” y se afirma “Up to 13.04 PS4 and 12.70 PS5”. La publicación contiene imágenes, no código ni PoC. Una de las imágenes atribuye el hallazgo a bollars y describe un bug descubierto mediante diffing de kernels en `ffs_mount`, pero utiliza lenguaje tentativo: “It might be exploitable but who knows” y “in theory”.

No se localizó una publicación original de **bollars**, un repositorio de bollars con Celsius, un gist, una PoC, un commit original o un log de hardware. El perfil público de bollars en GitHub sólo contiene `ddoslib`, no relacionado con PS4. Por tanto, la atribución “descubierto por bollars” y el alcance “hasta 13.04” son **SOURCE_ONLY**. El hecho de que 13.02 esté incluido en el intervalo numérico 1–13.04 es una inclusión nominal, no una prueba de funcionamiento.

## Cadena de procedencia

| Orden | Fuente | Fecha | Qué aporta | Independencia | Clasificación |
|---:|---|---|---|---|---|
| 1 | Dr.Yenyen en X | 18 jul. 2026 | Primera difusión localizada; nombre Celsius; PS4 13.04/PS5 12.70; imágenes que atribuyen bollars y `ffs_mount` | Primera fuente encontrada, pero no fuente primaria técnica de bollars | `SOURCE_ONLY` |
| 2 | GameGaz | 19 jul. 2026 | Repite bollars, `ffs_mount`, PS4 13.04, PS5 12.70, parche 13.50 y requisito HDD USB; advierte que aún no es práctico | Derivada del anuncio de X y comentarios de escena | `SOURCE_ONLY` |
| 3 | GAMERZ 56K en YouTube | julio 2026 | Repite integer overflow/heap overflow, hasta 13.04 incluyendo 13.02, parche 13.50 y USB | Derivada/recapitulación; no PoC | `SOURCE_ONLY` |
| 4 | `adri22235/ps4-suid-scanner` | 18 jul.–9 ago. 2026 | Añade análisis, atribución a bollars, estructura de `ffs_mountfs()` y afirmación “works up to 13.04” | Artefacto técnico secundario; no origen de bollars | `SOURCE_ONLY` para Celsius en PS4 |
| 5 | PSDevWiki | actualización 2026 | Registra `?<=13.04?`, fix desde 13.50, FFS y requisitos de disco/PFS | Wiki colaborativa que cita material de escena | `SOURCE_ONLY` con incertidumbre explícita |
| 6 | Wikova | 10 ago. 2026 | Resume Celsius y su rango | Fuente terciaria conectada a referencias anteriores | `SOURCE_ONLY` |
| 7 | X / Silent_Logic | 30–31 jul. 2026 | Rumor de baja tasa de éxito y requisitos difíciles; dice que podría ser inútil | Rumor comunitario sin evidencia técnica | `SOURCE_ONLY` |

La búsqueda de GitHub para `Celsius`, `ffs_mount` y `PS4` no localizó otro repositorio primario. La búsqueda de commits tampoco produjo un commit técnico de bollars. La cuenta `bollars` existe y tiene actividad pública, pero su único repositorio es `bollars/ddoslib`, creado en 2013 y actualizado en 2017.

## ¿Dónde aparece por primera vez “hasta 13.04”?

La primera aparición pública localizable es la publicación de Dr.Yenyen del **18 de julio de 2026**, no un documento técnico de bollars. El texto exacto visible es:

> “Here you go. You'll still have to be patient but this is what you might get. It's named ‘Celsius’ Posting it as of now so that you guys don't go crazy. Just wait and see how usable it is if at all. Up to 13.04 PS4 and 12.70 PS5.”

La imagen asociada atribuye el descubrimiento a bollars y describe `ffs_mount`, pero también dice que podría ser explotable “who knows” y que funciona hasta 13.04 “in theory”. Esto es importante: **la primera fuente ya contiene una reserva explícita sobre usabilidad y confirmación**.

## Comprobación técnica de FFS

CVE-2006-5679 documenta un integer overflow histórico en `ffs_mountfs()` de FreeBSD 6.1, relacionado con parámetros grandes o inválidos de tamaño al montar un filesystem UFS. NVD también conserva la nota de que el problema no necesariamente cruza privilegios en FreeBSD porque montar un filesystem normalmente requiere root.

El commit oficial de FreeBSD `r309172`, de Kirk McKusick, fue enviado el 26 de noviembre de 2016 a stable/11. Su mensaje dice: “Avoid possible overflow when calculating malloc size for auxiliary data structure sizes when mounting and reloading UFS/FFS filesystems”. El diff cambia tamaños de `int` a `u_long` y elimina conversiones que podían truncar cálculos en `ffs_reload()` y `ffs_mountfs()`.

Estos dos artefactos verifican que la **familia de error de cálculo de tamaño en FFS mount/reload existe históricamente en FreeBSD**. No verifican que el código de Orbis PS4 13.02 sea idéntico ni que el supuesto Celsius sea una reaplicación funcional de CVE-2006-5679.

El análisis local de `adri22235/ps4-suid-scanner` describe un patrón donde `fs_ncg`, `fs_cssize`, `fs_contigsumsize`, `fs_bsize` y `fs_fsize` controlan el tamaño de estructuras auxiliares; una envoltura entera podría causar una reserva menor seguida de una escritura iterativa sobre grupos de cilindros. El documento es una descripción secundaria, no un diff de Orbis ni una PoC.

| Afirmación técnica | Estado |
|---|---|
| Existió un overflow de tamaño relacionado con FFS mount en FreeBSD histórico | `VERIFIED` |
| FreeBSD corrigió cálculos de tamaño en r309172 | `VERIFIED` |
| Orbis conserva código suficientemente equivalente | `HYPOTHESIS` |
| El supuesto Celsius usa exactamente la misma ruta | `SOURCE_ONLY`/`HYPOTHESIS` |
| El overflow produce sólo crash/DoS o puede producir R/W | `UNVERIFIED_13_02` |

## Requisitos que se atribuyen a Celsius

GameGaz y la publicación de GAMERZ afirman que se necesita un HDD USB 3.0 de al menos 250 GB —algunas publicaciones recomiendan 320 o 500 GB— con una imagen o partición FFS/UFS malformada. También se menciona un entrypoint userland Vue o BD-J y una dependencia del timing de inserción del USB.

PSDevWiki añade que el FFS de PS4 está protegido por PFS, por lo que preparar una partición FFS malformada podría requerir claves por consola o una etapa adicional. Esto vuelve esencial distinguir entre “puede colocarse un archivo o disco malformado” y “el kernel Orbis llega a montar esa estructura bajo los privilegios accesibles desde BD-J/Vue”.

Ningún artefacto público localizado demuestra: la imagen exacta, el formato de partición usado, cómo se obtiene el acceso al mount/reload, qué privilegios tiene el proceso, qué objeto queda adyacente en heap, cómo se controla el overwrite o cómo se obtiene kernel R/W. Por tanto, los requisitos son `SOURCE_ONLY` y la transición overflow → R/W es `HYPOTHESIS`.

## Evidencia de 13.02 y 13.04

No hay evidencia real localizada de que Celsius haya sido ejecutado con éxito en PS4 13.02. El único argumento a favor es que 13.02 cae dentro de la frase “hasta 13.04”, pero esa frase procede de un anuncio con lenguaje tentativo y no va acompañada de PoC, log ni video técnico reproducible.

Tampoco hay evidencia real localizada de ejecución en PS4 13.04. Las fuentes secundarias usan “up to 13.04”, pero no muestran consola, versión leída de forma verificable, trigger, resultado del overflow ni kernel R/W. La clasificación correcta para ambas versiones es `UNVERIFIED_13_02`/`UNVERIFIED_13_04`, con la afirmación de alcance nominal en `SOURCE_ONLY`.

## Evidencia del supuesto parche 13.50

La evidencia a favor consiste en una coincidencia temporal y repetición de fuentes: PS4 13.50 se publicó en marzo de 2026 y varias fuentes de la escena dicen que Celsius fue corregido allí. GameGaz interpreta que una actualización con notas genéricas de estabilidad habría incluido una corrección silenciosa.

No se localizó un diff de kernel Sony, un advisory de Sony, una función o string identificada, un hash pre/post, una referencia HackerOne vinculada, ni una PoC que funcione en 13.04 y falle en 13.50. X/Silent_Logic sólo aporta rumor sobre baja tasa de éxito; no prueba un parche.

**Clasificación del parche 13.50:** `SOURCE_ONLY`. El parche es plausible, pero no técnicamente probado con las fuentes públicas disponibles.

## Respuestas solicitadas

### 1. ¿Quién publicó originalmente Celsius?

La primera difusión pública localizada fue de **Dr.Yenyen en X el 18 de julio de 2026**. La publicación atribuye el hallazgo técnico a **bollars**, pero no es una publicación de bollars ni contiene la PoC original. Por tanto, la respuesta precisa es: **Dr.Yenyen publicó la primera difusión pública localizada; bollars es el descubridor atribuido, todavía sin fuente primaria pública localizada**.

Clasificación: primera difusión `VERIFIED` como hecho de publicación; atribución a bollars `SOURCE_ONLY`.

### 2. ¿Dónde aparece por primera vez “hasta 13.04”?

En el tuit de Dr.Yenyen del **18 de julio de 2026 a las 18:37**. La frase es “Up to 13.04 PS4 and 12.70 PS5”, y la imagen asociada añade “13.04 PS4 in theory”. GameGaz lo repite al día siguiente.

Clasificación: `SOURCE_ONLY`.

### 3. ¿Existe evidencia real de que funcionara en 13.02?

No. Existe inclusión nominal de 13.02 dentro de “hasta 13.04”, pero no hay PoC, video técnico, log, hash de firmware, lectura/escritura observable ni prueba de hardware PS4 13.02 localizada.

Clasificación: `UNVERIFIED_13_02`.

### 4. ¿Existe evidencia real de que funcionara en 13.04?

No se encontró evidencia de ejecución funcional en 13.04. Sólo existe la afirmación de alcance en X, noticias, wiki y repositorios secundarios.

Clasificación: `UNVERIFIED_13_04`.

### 5. ¿Qué prueba existe de que fue parcheado en 13.50?

Sólo la convergencia temporal y la repetición de fuentes secundarias. Falta una comparación técnica de kernel o una PoC pre/post que atribuya causalmente el cambio a 13.50.

Clasificación: `SOURCE_ONLY`; no `VERIFIED`.

### 6. ¿Qué falta para considerar Celsius una ruta reproducible de kernel R/W en 13.02?

Falta un paquete de evidencia con: (a) fuente o PoC original; (b) imagen FFS/UFS exacta; (c) artefacto de kernel Orbis 13.02 con procedencia y hash; (d) explicación estática de la función equivalente a `ffs_mountfs()`; (e) log o video de PS4 13.02 que muestre la trigger; (f) prueba de que la corrupción es controlable y no sólo un panic; y (g) demostración de kernel R/W y de una operación post-exploitation observable.

## Clasificación final

| Hallazgo | Clasificación |
|---|---|
| Primera difusión pública de Celsius fue el tuit de Dr.Yenyen del 18 jul. 2026 | `VERIFIED` |
| bollars es el descubridor atribuido | `SOURCE_ONLY` |
| Existe un bug histórico de overflow en FFS mount/reload de FreeBSD | `VERIFIED` |
| Orbis contiene una ruta equivalente utilizable por Celsius | `HYPOTHESIS` |
| Celsius cubre nominalmente PS4 hasta 13.04 | `SOURCE_ONLY` |
| Celsius funcionó en PS4 13.02 | `UNVERIFIED_13_02` |
| Celsius funcionó en PS4 13.04 | `UNVERIFIED_13_04` |
| Celsius fue parcheado en PS4 13.50 | `SOURCE_ONLY` |
| Celsius proporciona kernel R/W | `UNVERIFIED_13_02` |
| Rumor de baja tasa de éxito/inutilidad | `SOURCE_ONLY` |
| Netctrl tiene PoC PS4 hasta 13.00 | `VERIFIED` |

## Referencias

[1]: https://x.com/calmboy2019/status/2078549759460094065 "Primera difusión localizada de Celsius por Dr.Yenyen"
[2]: https://github.com/bollars/ddoslib "Único repositorio público localizado del usuario bollars"
[3]: https://github.com/adri22235/ps4-suid-scanner "Repositorio secundario con la atribución y análisis Celsius"
[4]: https://gamegaz.com/2026071945823/ "GameGaz: Celsius by bollars"
[5]: https://www.youtube.com/post/UgkxE2BPYs9Rf7TJgkq8GqnZlTh-kOpDU15F "GAMERZ 56K: resumen del rumor Celsius"
[6]: https://www.psdevwiki.com/ps4/Bugs "PSDevWiki Bugs"
[7]: https://www.psdevwiki.com/ps4/Vulnerabilities "PSDevWiki Vulnerabilities"
[8]: https://mail-archive.freebsd.org/cgi/mid.cgi?201611260043.uAQ0hcWs008737 "FreeBSD r309172: fix FFS mount/reload overflow"
[9]: https://nvd.nist.gov/vuln/detail/CVE-2006-5679 "NVD CVE-2006-5679"
[10]: https://x.com/Slient_Logic/status/2082855345844797681 "Rumor de Silent_Logic sobre Celsius 13.02"
[11]: https://wikova.com/wiki/DQm4J1HU "Wikova: resumen de PS4 Jailbreak"

> **Conclusión:** la afirmación “hasta 13.04” nació públicamente como una afirmación de alcance teórico en una difusión de X, no como una PoC publicada por bollars. No existe actualmente evidencia pública suficiente de ejecución Celsius en 13.02 o 13.04 ni de kernel R/W reproducible. El origen primario real y el artefacto que demostraría el parche 13.50 siguen faltando.
