# Celsius/ffs_mount frente a Netctrl/ucred — PS4 FW 13.02

**Fecha de corte:** 26 de agosto de 2026. **Método:** revisión estática y documental de fuentes públicas, repositorios, historiales, artefactos y writeups. No se ejecutaron payloads, corrupción de memoria ni pruebas de hardware.

## Resumen ejecutivo

Celsius y Netctrl no tienen el mismo nivel de evidencia. **Netctrl/ucred** dispone de código PS4 público y de una cadena histórica que llega funcionalmente hasta 13.00; su primitive está descrita y usada por una implementación real. **Celsius/ffs_mount** tiene una atribución pública a bollars, una descripción técnica coherente con un integer overflow de UFS/FFS y varias fuentes secundarias que sitúan el alcance hasta 13.04, pero no se ha localizado un repositorio primario de bollars, una PoC pública, un log de hardware o una demostración de kernel R/W.

En consecuencia, **13.02 queda incluido dentro del rango afirmado por las fuentes secundarias de Celsius, pero no dentro de un rango técnicamente demostrado**. Para Netctrl, la evidencia de funcionamiento en 13.02 es más débil todavía: el código publicado detiene la tabla de la primitive en 13.00. La comparación correcta no es “Celsius confirmado contra Netctrl descartado”, sino **Celsius como candidato de alcance nominal más amplio pero con menor transparencia técnica, frente a Netctrl como exploit real y trazable cuyo límite público está probado en 13.00**.

## Celsius: qué sabemos realmente

### Origen y procedencia

El nombre Celsius se atribuye a **bollars**. La búsqueda del perfil público de GitHub `bollars` encontró un único repositorio, `ddoslib`, sin código de Celsius, sin PoC FFS y sin historial del supuesto descubrimiento. La fuente pública más concreta es `adri22235/ps4-suid-scanner`, cuyos documentos atribuyen Celsius a bollars y describen `ffs_mountfs()`; sus commits se concentran entre el 18 de julio y el 9 de agosto de 2026. Esto verifica que la atribución fue publicada, pero no verifica que el repositorio sea la fuente original del descubrimiento.

Las noticias de GameGaz, la publicación de GAMERZ 56K en YouTube y el artículo terciario de Wikova repiten la misma historia: PS4 hasta 13.04, PS5 hasta 12.70, parcheado en PS4 13.50/PS5 13.00 y requisito de un HDD USB 3.0 de gran capacidad. Estas fuentes están relacionadas por contenido y no constituyen tres confirmaciones independientes.

**Clasificación de la atribución original:** `SOURCE_ONLY`.

### Firmware afirmado

| Fuente | Afirmación | Calidad |
|---|---|---|
| `adri22235/ps4-suid-scanner` | PS4 hasta 13.04; PS5 hasta 12.70; parche PS4 13.50 | `SOURCE_ONLY` |
| GameGaz, 19 jul. 2026 | PS4 hasta 13.04; PS5 hasta 12.70; USB 3.0 de 250 GB o más; aún no práctico | `SOURCE_ONLY`, con una advertencia explícita de falta de confirmación final |
| GAMERZ 56K, 2026 | PS4 hasta 13.04 incluyendo 13.02; parche 13.50+; USB 3.0 de 320/500 GB recomendado | `SOURCE_ONLY` |
| Wikova, actualizado ago. 2026 | Resume el mismo rango y atribución | `SOURCE_ONLY`/terciaria |
| PSDevWiki | `?<=13.04?`, corregido desde 13.50 | `SOURCE_ONLY` con incertidumbre explícita |

Por aritmética de rango, **13.02 está dentro de “hasta 13.04”**, pero eso sólo es una inclusión nominal. No demuestra que la implementación, la trigger o el post-exploitation funcionen en 13.02.

### Función y mecanismo descritos

Las fuentes atribuyen el bug a `ffs_mountfs()` en `sys/ufs/ffs/ffs_vfsops.c`, durante el montaje o reload de un filesystem UFS/FFS. El patrón técnico descrito utiliza valores derivados del superbloque, entre ellos `fs_cssize`, `fs_ncg`, `fs_contigsumsize`, `fs_bsize` y `fs_fsize`, para calcular el tamaño de estructuras auxiliares antes de `malloc`. Si el cálculo entero envuelve, la asignación puede ser menor que la cantidad que después se escribe al recorrer `fs_ncg` grupos de cilindros.

El cambio histórico de FreeBSD r309172, de Kirk McKusick, confirma que existía una familia real de errores de cálculo de tamaños en montaje/reload UFS/FFS: cambió `size` de `int` a `u_long` y eliminó conversiones que podían ocultar el tamaño calculado. El correo de commit de FreeBSD de 26 de noviembre de 2016 muestra cambios en `ffs_reload()` y `ffs_mountfs()`.

Sin embargo, esa confirmación es de **FreeBSD stable/11**, y CVE-2006-5679 describe originalmente FreeBSD 6.1. Ninguno de esos artefactos prueba que el código de Orbis PS4 13.02 sea idéntico. La presencia de un patrón equivalente en una copia de FreeBSD 9 es una evidencia de heredabilidad potencial, no una validación de Celsius en PS4.

**Clasificación del mecanismo genérico UFS/FFS:** `CORROBORATED` como familia histórica de bug en FreeBSD; `HYPOTHESIS` para la traducción exacta a Orbis 13.02.

### Requisitos afirmados para PS4

Las fuentes secundarias señalan un **HDD USB 3.0 de al menos 250 GB** —algunas recomiendan 320/500 GB— con una imagen o partición UFS/FFS especialmente construida. También señalan que hace falta una entrada userland como Vue o BD-J para preparar o activar la operación. El requisito de disco y el timing de inserción aparecen en fuentes comunitarias, pero no hay PoC pública que permita verificar el flujo exacto.

Quedan sin demostrar los puntos críticos: si el usuario sandbox puede provocar el montaje de una imagen arbitraria; si el dispositivo debe estar preparado con claves o formato específico; si el kernel Orbis expone la ruta FFS relevante; si `fs_ncg` y los demás campos llegan sin normalización; qué objeto de heap queda adyacente; y cómo se transforma el overflow en una primitive de lectura/escritura.

**Clasificación de requisitos:** `SOURCE_ONLY`; la posibilidad de convertir el overflow en kernel R/W es `HYPOTHESIS`.

### Afirmación de parche en 13.50

GameGaz, GAMERZ 56K, Wikova y PSDevWiki repiten que Celsius fue corregido en PS4 13.50. GameGaz relaciona esa conclusión con el cambio de firmware de marzo de 2026 y con un anuncio de seguridad genérico. No se localizó un diff de kernel Sony, advisory de Sony, símbolo, hash de función o commit público que identifique la corrección.

La afirmación es compatible temporalmente con una corrección silenciosa, pero no prueba causalidad. También es posible que el rango “hasta 13.04” sea una observación de disponibilidad de offsets o una inferencia de diffing, no una demostración completa.

**Clasificación del parche:** `SOURCE_ONLY`; no `VERIFIED`.

## Netctrl/ucred: qué sabemos realmente

Netctrl/Poopsploit dispone de una fuente primaria más sólida: el gist de TheOfficialFloW y la implementación pública de Riyon/Vue. La cadena usa una vulnerabilidad en la ruta NetControl/ucred para provocar una condición de liberación múltiple o triple-free, obtener un leak asociado a objetos `kqueue`/descriptores y construir primitivas de lectura y escritura del kernel mediante estructuras reclamadas.

Los componentes dependientes de offsets incluyen la identificación de objetos, los layouts de `ucred`, `file`, `filedesc`, `kqueue`, `uio`/`iov`, referencias a procesos y offsets de funciones o datos usados después para el jailbreak. El trigger y el reclaim dependen más de layouts, tamaños y comportamiento del kernel que de una sola dirección; el post-exploitation sí depende fuertemente de offsets por firmware.

El árbol público de Riyon declara y sirve la cadena hasta **13.00**. En `kernel.ts`, las tablas Netctrl se agrupan para `12.50`, `12.52` y `13.00`; la entrada `13.02` encontrada en el mismo ecosistema corresponde a mmap/RWX u otros datos auxiliares, no a una adaptación demostrada de la primitive Netctrl. Los forks de Vue After Free comparten ascendencia y no son fuentes independientes por el mero hecho de tener hashes distintos.

**Clasificación del exploit funcional publicado:** `VERIFIED` para el rango documentado por el código —hasta 13.00—. **Clasificación para 13.02:** `UNVERIFIED_13_02`.

## Comparación directa

| Dimensión | Celsius/ffs_mount | Netctrl/ucred |
|---|---|---|
| Fuente primaria pública del descubrimiento | No localizada; atribución indirecta a bollars | Sí: TheOfficialFloW y adaptación pública de Riyon |
| Firmware nominal | Hasta 13.04 según fuentes secundarias | Hasta 13.00 en implementación pública |
| Firmware 13.02 | Incluido nominalmente, sin PoC pública | Sin entrada funcional específica; `UNVERIFIED_13_02` |
| Bug base | Integer overflow durante montaje/reload UFS/FFS | Triple-free/corrupción de `ucred` en NetControl |
| Primitive inicial | Heap overflow/corrupción potencial | Leak y `kread/kwrite` en cadena publicada |
| R/W directo demostrado | No | Sí en firmware publicado hasta 13.00 |
| PoC PS4 pública | No localizada | Sí, para el rango histórico publicado |
| Evidencia hardware 13.02 | No | No |
| Evidencia de parche | Afirmación secundaria: 13.50 | No hay diff de parche específico 13.02 localizado |
| Requisitos especiales | HDD USB 3.0, imagen/partición FFS, trigger userland | Userland y condiciones de heap/objetos NetControl |
| Independencia de fuentes | Mayormente artículos que repiten una atribución | Varias copias/forks de una línea común; fuente primaria sí identificable |
| Estado global 13.02 | `HYPOTHESIS / UNVERIFIED_13_02` | `UNVERIFIED_13_02` |

## Candidato más prometedor para 13.02

Si “prometedor” significa **alcance nominal**, Celsius es el candidato más cercano: las fuentes lo sitúan hasta 13.04, por lo que 13.02 queda dentro del rango afirmado. Pero si “prometedor” significa **evidencia técnica reutilizable**, Netctrl es superior: tiene código PS4, una primitive de R/W ya demostrada en firmwares cercanos y una ruta post-exploitation conocida.

Mi conclusión ponderada es que **Celsius es el candidato de mayor interés para una investigación estática de 13.02**, porque podría evitar el límite 13.00 de Netctrl, pero **Netctrl tiene la evidencia más fuerte de que el concepto de kernel R/W funciona en PS4**. Ninguno puede clasificarse como `VERIFIED` para 13.02.

## Evidencia concreta que falta

Para Celsius, hace falta el anuncio o commit original de bollars, el artefacto exacto de la imagen FFS/USB, una PoC o pseudocódigo completo, un log de ejecución que demuestre el overflow en PS4 13.02 y un análisis del target de heap que convierta la corrupción en R/W. Para validar el parche 13.50, hacen falta dumps o funciones comparables de 13.04 y 13.50 con hashes y un diff que señale el cambio.

Para Netctrl, hace falta una ejecución documentada en 13.02 que muestre, en orden, el trigger ucred, el leak, la reclamación de objetos y una lectura/escritura controlada; alternativamente, kernels legítimos 13.00 y 13.02 con hashes que permitan comparar la ruta NetControl y sus estructuras.

## Otras líneas surgidas

La comparación abre cuatro líneas, todas estáticas inicialmente:

1. **Comparación Orbis FFS:** identificar la implementación de `ffs_mountfs()` en un artefacto legítimo de Orbis y contrastarla con FreeBSD 9.1 y el fix de FreeBSD r309172, sin extrapolar automáticamente el commit de FreeBSD 11.
2. **Proveniencia de Celsius:** buscar mensajes originales de bollars, anuncios fechados del 18 de julio de 2026 y artefactos atribuidos a Pharaoh2k, separando archivos derivados de una tabla de offsets de una PoC independiente.
3. **Diferencias de pre/post 13.50:** localizar cambios de funciones, strings, tamaños y checks relacionados con FFS en artefactos públicos de 13.04/13.50; una nota de firmware genérica no basta.
4. **Compatibilidad de trigger:** documentar si BD-J/Vue puede llegar a una operación de montaje de FFS bajo las restricciones reales del sandbox y si el disco requerido es un requisito técnico o sólo una recomendación comunitaria.

## Clasificación final

| Afirmación | Clasificación |
|---|---|
| Existe una familia real de integer overflow en FFS mount/reload en FreeBSD histórico | `VERIFIED` |
| El patrón genérico puede existir en una base derivada de FreeBSD 9 | `CORROBORATED`/`HYPOTHESIS` |
| bollars descubrió Celsius | `SOURCE_ONLY` |
| Celsius funciona hasta PS4 13.04 | `SOURCE_ONLY` |
| Celsius funciona específicamente en PS4 13.02 | `UNVERIFIED_13_02` |
| Celsius fue parcheado específicamente en PS4 13.50 | `SOURCE_ONLY` |
| Netctrl/ucred tiene implementación PS4 funcional hasta 13.00 | `VERIFIED` |
| Netctrl/ucred funciona en PS4 13.02 | `UNVERIFIED_13_02` |
| Las tablas 13.02 de offsets demuestran Celsius o Netctrl | `DISPROVEN` como inferencia; las tablas mismas son `SOURCE_ONLY` |
| Existe actualmente una ruta pública reproducible a kernel R/W en 13.02 | `DISPROVEN` por ausencia de evidencia reproducible pública, no por prueba de que sea imposible |

## Referencias

[1]: https://github.com/adri22235/ps4-suid-scanner "adri22235/ps4-suid-scanner"
[2]: https://github.com/RiyonAbib07/ps-vue-jb-2.5 "RiyonAbib07/ps-vue-jb-2.5"
[3]: https://gist.github.com/TheOfficialFloW/7174351201b5260d7780780f4059bebf "TheOfficialFloW NetControl gist"
[4]: https://gamegaz.com/2026071945823/ "GameGaz: Celsius by bollars"
[5]: https://www.youtube.com/post/UgkxE2BPYs9Rf7TJgKq8GqnZlTh-kOpDU15F "GAMERZ 56K: Celsius rumor summary"
[6]: https://wikova.com/wiki/DQm4J1HU "Wikova: PlayStation 4 Jailbreak"
[7]: https://mail-archive.freebsd.org/cgi/mid.cgi?201611260043.uAQ0hcWs008737 "FreeBSD r309172 UFS/FFS overflow fix"
[8]: https://nvd.nist.gov/vuln/detail/CVE-2006-5679 "NVD CVE-2006-5679"
[9]: https://www.psdevwiki.com/ps4/Bugs "PSDevWiki Bugs"
[10]: https://www.psdevwiki.com/ps4/Vulnerabilities "PSDevWiki Vulnerabilities"
[11]: https://github.com/bollars/ddoslib "The only public bollars GitHub repository located"

> **Conclusión:** Celsius tiene el rango nominal más atractivo para 13.02, pero Netctrl tiene la evidencia técnica más fuerte de una primitive real en PS4. La afirmación “Celsius funciona en 13.02” sigue siendo `UNVERIFIED_13_02`; la afirmación “Netctrl sobrevivió a 13.02” también. El artefacto decisivo para ambos sería una comparación verificable de kernel Orbis 13.00/13.02, complementada —para Celsius— por la PoC y la imagen FFS originales.
