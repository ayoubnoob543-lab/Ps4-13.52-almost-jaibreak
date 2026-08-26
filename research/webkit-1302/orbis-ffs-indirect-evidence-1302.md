# Auditoría final de evidencia indirecta sobre Celsius/FFS en PS4 FW 13.02

**Fecha de corte:** 26 de agosto de 2026.
**Alcance:** investigación pública, documental y estática. No se ejecutaron exploits, cadenas de corrupción ni payloads en hardware real.

## Conclusión ejecutiva

La investigación no ha encontrado un artefacto público que permita identificar directamente `ffs_mountfs()`/`ffs_reload()` en el kernel Orbis de PS4 FW 13.02. Los artefactos disponibles contienen headers de offsets, loaders, runtimes, herramientas de volcado, código userland y documentación secundaria. Ninguno aporta conjuntamente bytes de kernel Orbis 13.02, dirección verificable de `ffs_mountfs()`, disassembly, pseudocódigo obtenido del binario, hash de kernel, log de prueba o PoC reproducible que transforme Celsius en kernel R/W.

La primera aparición pública observada de la tabla completa de offsets 13.02 es el commit de ArabPixel en Fusion del 18 de enero de 2026. La tabla de OSM de 21/22 de enero es posterior y deriva prácticamente toda su información de esa línea: se observaron 162 coincidencias de 163 valores comunes. Las copias de Fusion, OSM, SLOPOS y otros headers no constituyen fuentes independientes mientras no exista una medición o artefacto primario separado.

El offset `patch_mount = 0x001512A7` tampoco identifica `ffs_mountfs()`. El análisis estático de Fusion muestra que el concepto “mount” se usa para parches genéricos de autorización/FUSE, históricamente documentados como “Enable mount for unprivileged user” y “Mount Fuse filesystem as root”. No aparecen bytes, cross-references, strings UFS/FFS ni una firma que conecte ese offset con Celsius.

La documentación de `adri22235/ps4-suid-scanner` es la descripción pública más explícita de Celsius, pero sigue siendo una fuente secundaria o del propio proyecto: afirma “hasta 13.04”, “parcheado en 13.50”, atribuye el descubrimiento a bollars y reproduce un patrón de código FreeBSD. Su código `stage2_jordy.js`/`jordy_stage2.js` no demuestra una cadena completa: deja como TODO la base WebKit, la base de libkernel, `dlsym`, el montaje de la imagen UFS, el pivote ROP y la ejecución. Por tanto, Celsius permanece como **SOURCE_ONLY / HYPOTHESIS / UNVERIFIED_13_02**, no como ruta reproducible de kernel R/W.

| Pregunta | Resultado | Clasificación |
|---|---|---|
| ¿Existe una tabla pública de offsets 13.02? | Sí, Fusion/ArabPixel y derivados. | **VERIFIED** |
| ¿La tabla prueba un dump de kernel? | No; no contiene bytes ni hash de kernel. | **INVALID** |
| ¿OSM identifica el dump de origen? | No; su README sólo da orientación general. | **SOURCE_ONLY** |
| ¿`patch_mount` es `ffs_mountfs()`? | No hay bytes, símbolo ni cross-reference. | **HYPOTHESIS / INVALID como identificación** |
| ¿El código FreeBSD vulnerable existe en Orbis 13.02? | No demostrado; sólo existe la referencia upstream. | **VERIFIED upstream; UNVERIFIED_13_02 Orbis** |
| ¿Celsius está probado en hardware 13.02? | No se encontró log, PoC reproducible ni dump de crash. | **UNVERIFIED_13_02** |
| ¿Está probado el parche de 13.50? | Sólo por anuncios y reportes secundarios; Sony no publica el diff. | **SOURCE_ONLY** |
| ¿Hay ruta pública reproducible userland → kernel R/W en 13.02? | No. | **NO DEMOSTRADA** |

## Actualización: qué piezas externas existen alrededor de Jordy

La inspección de los 80 forks públicos de `ntfargo/CSSFontFace-Exploit` encontró principalmente propagación de la cadena histórica `lapse.js`/`netctrl.js`/`ps4/kernel.js` y, en algunos casos, sólo `offsets.mjs`. No apareció ningún `jordy_stage2.js`, archivo Celsius, `ffs_mountfs` ni extensión 13.02/13.04. El fork `hejran7` añade `pl_KernelDumper.bin` y `pl_KernelClock.bin`, pero su menú los identifica como payloads de dumper. Ambos son binarios pequeños con prólogos x86-64 y strings de APIs PS4/libkernel; no son una imagen de kernel. Su `kernel_patches()` declara explícitamente que sólo se usa “after kernel arw”, por lo que consume una primitive existente y no la obtiene.

El repositorio `ddaaccdd/CSSFontFace-Exploit-1302research` aporta el contraste más informativo: contiene un scaffold real de derivación de bases WebKit/libc/libkernel, pivot, syscalls y dlsym, pero su README afirma que el vector CSSFontFace probado no funciona en 13.02 por razones arquitectónicas. No contiene Netctrl, `KernelView`, kernel R/W, UFS/FFS ni Celsius implementados. Así, las piezas históricas permiten reconstruir qué tendría que aportar una cadena completa, pero ninguna llena las lagunas de `jordy_stage2.js` para 13.02.

El commit 1089382 sí existe y es auditable, pero su `jordy_stage2.js` continúa siendo un scaffold: devuelve `0` para las bases WebKit/libkernel, deja dlsym sin resolver, comenta el flujo `mount → ffs_mountfs → Celsius` y termina el pivot con `TODO`. La matriz de componentes muestra que `KernelView`, `kread/kwrite`, `p_ucred` y `pktopts` sólo aparecen en la cadena histórica PS4, no en Jordy.

## 1. Procedencia de los offsets 13.02

El primer artefacto público completo localizado es `ArabPixel/Fusion/Shared/Offsets-1302.h`, añadido por el commit [`77a16b7f236df46f14bb2c744a24540e57245214`](https://github.com/ArabPixel/Fusion/commit/77a16b7f236df46f14bb2c744a24540e57245214), fechado el 18 de enero de 2026. El PR correspondiente de AetherPS/Fusion es [`#13`](https://github.com/AetherPS/Fusion/pull/13), descrito como “only kernel offsets and the implementation in Offsets.h”. El cambio contiene asignaciones del tipo `kernelBase + constante`; no contiene dump, ELF, bytes de instrucciones, hash de kernel, proyecto IDA/Ghidra, método de extracción ni prueba de hardware.

La copia fusionada de AetherPS/Fusion (`1d7c0314ade52858496195e53bcc85de274def51`) es byte a byte idéntica a la cabecera de ArabPixel; ambas copias tienen el mismo SHA-256 descargado, `7b034c3b933ddbee560ae9dc18cf02cbcd7aa4d8cef6e5ab48154cd972268f7d`. Esto es propagación, no corroboración independiente.

El commit inicial de OSM-Made [`093808ee1563dfdb735b69ba2bfc925a9439ff54`](https://github.com/OSM-Made/PS4-Kernel-SDK/commit/093808ee1563dfdb735b69ba2bfc925a9439ff54) añade `offsets/firmware-1302.yaml` con 853 líneas. La comparación realizada encontró 162 de 163 offsets comunes idénticos frente a Fusion; la diferencia observada es `trap_fatalHook` (`0` frente a `0x0014AA90`). El YAML tiene SHA-256 `2774f464e642b2419ddb7939707f262c87b268a5794c291d79a2edcc9eefe769`. El commit no identifica dump, build, LSTAR, IDA/Ghidra, autor de la medición, hash de kernel ni prueba de hardware.

El README de OSM indica como práctica general que los offsets deben proceder de un “known-good kernel dump” y probarse en hardware. Esa frase no demuestra que el YAML concreto proceda de un dump conocido ni identifica cuál sería. El grafo público mínimo es:

```text
Origen material no identificado
        ↓
ArabPixel/Fusion 77a16b7 — primera tabla pública completa observada
        ↓
AetherPS/Fusion PR #13 / 1d7c031 — copia byte a byte
        ↓
OSM-Made/PS4-Kernel-SDK 093808e — YAML transformado
        ↓
SLOPOS, kpayload, SDKs y tablas derivadas
```

**Clasificación:** Fusion/ArabPixel como primera aparición pública, **VERIFIED**; OSM respecto de Fusion, **DERIVED**; “dump conocido” de OSM, **SOURCE_ONLY**; fuente material anterior, **UNVERIFIED**.

## 2. Qué contiene realmente la tabla 13.02

La tabla expone infraestructura general de kernel: `prison0`, `rootvnode`, `allproc`, `sysent`, `copyin`, `copyout`, `kern_open`, `kern_mkdir`, `getnewvnode`, `vn_fullpath`, `M_MOUNT`, `malloc`, `free`, `kmem_alloc`, `kmem_free`, funciones de VM, sysctl, TTY, PFS/SBL y varios parches. Estos nombres son compatibles con infraestructura de payload y VFS, pero no identifican la implementación interna de UFS/FFS.

| Entrada | Interpretación segura | Lo que no demuestra |
|---|---|---|
| `patch_mount = 0x001512A7` | Punto de parche etiquetado por el proyecto. | No demuestra `ffs_mountfs()`. |
| `M_MOUNT = 0x01A40250` | Símbolo/zona de asignación asociada a mounts. | No es la función vulnerable. |
| `getnewvnode = 0x0036E2F0` | Función VFS general. | No identifica FFS. |
| `vn_fullpath = 0x00308CE0` | Función VFS de resolución de rutas. | No identifica la ruta de montaje UFS. |
| `kern_open`, `kern_mkdir` | Wrappers de operaciones de filesystem. | No son `ffs_mountfs()`. |
| `malloc`, `free`, `kmem_alloc`, `kmem_free` | Primitivas generales de memoria. | No prueban un overflow. |

El historial de Fusion anterior a la tabla 13.02 contiene parches FUSE/root y de autorización para firmwares antiguos. Los comentarios “Enable mount for unprivileged user” y “Mount Fuse filesystem as root” explican el contexto del nombre `patch_mount`: un bypass genérico de autorización para montar, no una identificación de la función FFS vulnerable. Esta conexión es **VERIFIED** para el código histórico de Fusion y **INVALID** como prueba de Celsius.

## 3. Búsqueda específica de FFS/UFS

Se buscaron `ffs_mountfs`, `ffs_reload`, `ffs_vget`, `ffs_alloc`, `mountfs`, `fs_ncg`, `fs_cssize`, `fs_contigsumsize`, `fs_bsize`, `fs_fsize`, `struct fs`, `superblock`, `UFS`, `FFS`, `Celsius`, `bollars`, `Dr.Yenyen`, `Pharaoh2k` y `13.04` en el repositorio y en artefactos relacionados.

Las coincidencias de cuerpos de función, cálculos de `size`, tipos e iteraciones sobre `fs_ncg` proceden del código FreeBSD upstream recopilado para comparación, o de documentación secundaria que lo reproduce. No se encontró la misma función extraída de un kernel Orbis 13.02. En particular, no se obtuvo una prueba de que Orbis conserve los tipos, validaciones, orden de cálculos o bucles del código FreeBSD de referencia.

| Fuente | Naturaleza | Clasificación para Orbis 13.02 |
|---|---|---|
| FreeBSD 9.1 `ffs_vfsops.c` | Código upstream histórico. | **VERIFIED upstream; INVALID como Orbis** |
| `adri22235/ps4-suid-scanner/cve_analysis.md` | Explicación y pseudocódigo de Celsius. | **SOURCE_ONLY** |
| `jordy_stage2.js` / `stage2_jordy.js` | Código de integración incompleto. | **HYPOTHESIS / UNVERIFIED** |
| `webkit_gadgets_1304.js` | Comentarios sobre gadgets y FFS sin binario. | **SOURCE_ONLY** |
| Fusion/SLOPOS/kpayload | Headers de offsets. | **CORROBORATED como tablas; INVALID como FFS** |
| SDKs y `ps4-linux-loader` | Headers, loaders y runtime. | **SOURCE_ONLY como antecedente; no Orbis FFS** |

La conclusión técnica es limitada pero firme: podemos demostrar la ruta histórica FreeBSD de referencia; no podemos demostrar que el kernel Orbis 13.02 tenga esa implementación sin un artefacto de código Orbis.

## 4. Auditoría de la narrativa Celsius

La fuente pública de mayor detalle es el repositorio [`adri22235/ps4-suid-scanner`](https://github.com/adri22235/ps4-suid-scanner). Su README y `cve_analysis.md` afirman que Celsius es un integer overflow en `ffs_mountfs()`, que funciona hasta PS4 13.04, que fue parcheado en 13.50, que requiere una imagen UFS malformada y un HDD USB 3.0 de al menos 250 GB, y que puede encadenarse con Vue o BD-J. También atribuyen el descubrimiento a bollars.

Estas afirmaciones son evidencia de lo que el repositorio dice, no prueba material de que el código Orbis sea igual. El supuesto código vulnerable se presenta con estilo FreeBSD upstream: `fs_cssize`, `fs_contigsumsize`, `fs_ncg`, cálculos de tamaño, `malloc` y un bucle posterior sobre `fs_ncg`. No se acompaña de dirección de función en Orbis, bytes, disassembly, dump, hash, crash log o PoC pública reproducible.

El commit [`6cacb2432f9940a5710a8d13895d4c799342cca6`](https://github.com/adri22235/ps4-suid-scanner/commit/6cacb2432f9940a5710a8d13895d4c799342cca6), con mensaje “Add complete PS4 13.04 kernel offsets (verified via Pharaoh2k + 1302 base)”, añade sólo `1304.c` y `1304.h`. No contiene dump, disassembly, firma de Pharaoh2k, log, bytes de FFS ni prueba de hardware. “Verified via Pharaoh2k” es por ello **SOURCE_ONLY**.

El commit [`96a79482d249fdbc6101bc641241488de66c313d`](https://github.com/adri22235/ps4-suid-scanner/commit/96a79482d249fdbc6101bc641241488de66c313d) añade un `stage2_jordy.js` descrito como “Jordy r/w → ROP → Celsius for 13.04”. La inspección estática encuentra TODOs para `read32`, `write32`, disposición de objetos, base WebKit, base libkernel, `dlsym`, imagen UFS, pivote ROP y parcheo. El archivo es un esqueleto de diseño, no una cadena funcional.

El historial enumera después `1089382ec1e0000e9557b7748d39b57952bbc4f3` con el mensaje “Replace skeleton with full stage 2: persistent r/w + ROP for 13.04”. La recuperación posterior confirmó que el SHA **sí existe**, tiene como padre `96a7948` y añade el `jordy_stage2.js` que también aparece en el árbol público/forks auditados. Sin embargo, su contenido no es funcionalmente completo: `findWebkitBase()` retorna `0`, `findLibkernelBase()` retorna `0`, faltan las direcciones exactas de `dlsym`, el montaje UFS sólo está comentado y `executeRop()` registra “TODO: Implement execution pivot”. Por tanto, el commit es un artefacto público auditable de diseño, pero no demuestra una cadena ejecutable ni una primitive de kernel R/W.

**Clasificación:** existencia del commit 1089382 y de su archivo, **VERIFIED**; que sea una implementación completa, **DISPROVEN por inspección estática**; alcance “hasta 13.04”, **SOURCE_ONLY**; correspondencia exacta con Orbis, **HYPOTHESIS / UNVERIFIED_13_02**; kernel R/W, **UNVERIFIED**; parche 13.50, **SOURCE_ONLY**.

## 5. Fuentes secundarias y supuesta corrección en 13.50

La publicación de Dr.Yenyen del 18 de julio de 2026 y los artículos de GameGaz y Wikova repiten la afirmación “Up to 13.04 PS4 and 12.70 PS5”, la atribución a bollars y el requisito de almacenamiento USB. GameGaz dice expresamente que Celsius todavía no era práctico y que no localizó un informe HackerOne público correspondiente. Wikova es una síntesis secundaria y no aporta bytes ni PoC.

La página oficial de soporte de Sony para el software de PS4 ofrece instrucciones generales de actualización y un enlace al firmware actual, pero no publica un diff de kernel ni menciona UFS, FFS, `ffs_mountfs`, Celsius o el parche concreto. Las notas de usuario, por sí solas, no permiten convertir la afirmación “parcheado en 13.50” en evidencia técnica.

La cronología de releases de `ps4-payload-dev/elfldr` registra offsets 13.02, offsets 13.04 y parches 13.50. `Scene-Collective/ps4-hen` registra releases firmados con soporte 13.00, 13.02, 13.04 y 13.50. Estos son artefactos válidos de soporte de loaders/HEN, no evidencia de que Celsius exista ni de que se haya parcheado. El soporte de un payload sólo prueba que un proyecto conoce o utiliza determinados offsets y rutas de carga.

Un hilo de Reddit afirma que Gezine tendría un exploit hasta 13.50, pero no aporta código, offsets, dump, log, primitive ni relación con Celsius. Se clasifica como **SOURCE_ONLY / UNVERIFIED** y no modifica la conclusión.

## 6. Tooling de dump y la hipótesis de un origen privado

`ArabPixel/sdk`, fork de `ps4-payload-dev/sdk`, ya disponía antes de Fusion de `kernel_find_pattern()`, `kernel_get_image_size()` y `samples/kdump/main.c`. El commit de julio de 2025 añadió infraestructura de búsqueda de patrones; otro de agosto corrigió el sample `kdump`; y el commit de octubre de 2025 añadió inicialización para firmware 13.02 basada en `LSTAR`, `copyin`, `copyout` y `targetid`. El sample puede copiar una imagen del kernel si ya existe una primitive funcional de kernel R/W.

Esta proximidad temporal hace plausible que alguien pudiera haber utilizado un flujo privado de kernel R/W → `kernel_copyout()` → kdump → pattern scanning para obtener offsets. Pero no se encontró el archivo de salida, hash de dump, patrón FFS, log, proyecto de reverse engineering ni declaración de ArabPixel que conecte ese tooling con `Shared/Offsets-1302.h`. La hipótesis mejor respaldada es, por tanto, **posible análisis privado o fuente no publicada**, no una atribución demostrada.

Los artículos históricos de fail0verflow muestran qué aspecto tiene una evidencia primaria real: para PS4 1.01 documentan un dump obtenido mediante hardware/PCIe y publican pseudocódigo de crashdump y explotación. Ese material es **VERIFIED** para 1.01, pero **INVALID** como evidencia 13.02/Celsius. La comparación es útil porque demuestra que un dump real normalmente deja bytes, método, hash, símbolos o pseudocódigo reproducible; nada equivalente apareció para 13.02.

## 7. Diferencia entre userland, primitive intermedia y kernel R/W

Debe mantenerse una separación estricta entre niveles. Vue, CSS/WebKit, BD-J y los gadgets ROP proporcionan entradas userland o capacidades de ejecución dentro de un proceso. Un header con `copyin`, `copyout`, `proc_rwmem`, `prison0` o `rootvnode` documenta direcciones que un payload podría usar después de obtener control kernel; no demuestra por sí mismo que exista la vulnerabilidad que entrega ese control.

Del mismo modo, un comentario que diga “Jordy arbitrary R/W” puede referirse a una primitive de memoria dentro del proceso WebKit, no a lectura/escritura arbitraria del kernel. La transición crítica userland → kernel R/W requiere un bug de kernel demostrado, una primitive de corrupción o lectura/escritura fuera del proceso, una cadena de estabilización y una prueba de que las direcciones de destino funcionan en el firmware concreto. Esa transición no aparece implementada públicamente para 13.02.

## 8. Respuestas finales

**1. ¿Quién publicó originalmente Celsius?** La primera fuente pública localizada es el anuncio de Dr.Yenyen que atribuye el descubrimiento a bollars; GameGaz lo reproduce. No se encontró una publicación técnica primaria, PoC original o commit original de bollars. Clasificación: **SOURCE_ONLY**.

**2. ¿Dónde aparece primero “hasta 13.04”?** En la cadena pública localizada, aparece en el anuncio de Dr.Yenyen del 18 de julio de 2026 y sus primeras referencias secundarias. No se ha encontrado una fuente técnica anterior que acompañe la frase con bytes o prueba.

**3. ¿Existe evidencia real de que funcionara en 13.02?** No en el sentido exigente de esta auditoría. Existe una afirmación de cobertura hasta 13.04 y tablas de offsets 13.02/13.04, pero no hay log, PoC reproducible, dump de crash, dirección de `ffs_mountfs()` ni prueba de kernel R/W. Clasificación: **UNVERIFIED_13_02**.

**4. ¿Existe evidencia real de que funcionara en 13.04?** Existe documentación y una tabla etiquetada como verificada por Pharaoh2k, pero no el artefacto de verificación ni una cadena completa públicamente inspeccionable. Clasificación: **SOURCE_ONLY**, no **VERIFIED**.

**5. ¿Qué prueba existe de que fue parcheado en 13.50?** Existen anuncios y reportes secundarios que lo afirman, además de la coincidencia temporal con un firmware posterior. No existe un diff de `ffs_mountfs()`, un binario comparado, un símbolo, un crash diferencial o una confirmación técnica de Sony. Clasificación: **SOURCE_ONLY**.

**6. ¿Celsius pasa de hipótesis a candidato respaldado para 13.02?** Sí como candidato narrativo y técnico plausible basado en FreeBSD y en afirmaciones de terceros; no como exploit respaldado por evidencia material de Orbis 13.02. La categoría correcta permanece **SOURCE_ONLY / HYPOTHESIS / UNVERIFIED_13_02**.

**7. ¿Existe hoy una ruta reproducible userland → kernel R/W en 13.02?** No. La primera etapa userland está documentada para ciertos rangos y existen tablas/tooling de payload, pero el salto a kernel R/W no está demostrado con evidencia pública reproducible.

## 9. Artefacto que resolvería la incertidumbre

El siguiente objetivo más informativo es un artefacto legítimamente disponible que contenga bytes de un kernel Orbis 13.02 o un disassembly/pseudocódigo verificable de la región de montaje. Idealmente debería incluir hash, firmware/build, procedencia, dirección base y una ventana que permita localizar `ffs_mountfs()` o una referencia desde `vfs_mount`/`mount` hacia UFS.

Si no aparece un dump completo, el mínimo suficiente sería un fragmento de código o tabla de símbolos con la dirección y bytes de `ffs_mountfs()`, más una comparación 13.02→13.50 de la misma función. Alternativamente, un commit primario de bollars que publique la función, el offset, la imagen UFS y un log de hardware permitiría elevar Celsius de **SOURCE_ONLY** a candidato técnicamente respaldado. Sin uno de esos artefactos, seguir comparando nombres de offsets no resolverá la cuestión.

## Referencias

[1]: https://github.com/ArabPixel/Fusion/commit/77a16b7f236df46f14bb2c744a24540e57245214 "Primera aparición pública observada de los offsets 13.02"

[2]: https://github.com/AetherPS/Fusion/pull/13 "Fusion PR #13"

[3]: https://github.com/AetherPS/Fusion/blob/1d7c0314ade52858496195e53bcc85de274def51/Shared/Offsets-1302.h "Header Fusion 13.02"

[4]: https://github.com/OSM-Made/PS4-Kernel-SDK/commit/093808ee1563dfdb735b69ba2bfc925a9439ff54 "Commit inicial YAML OSM 13.02"

[5]: https://github.com/Al-Azif/sdk "SDK de ArabPixel"

[6]: https://github.com/ArabPixel/sdk/commit/4323a2d9d8e2646e7488c5c5147709b5824eef7d "kernel_find_pattern y kernel_get_image_size"

[7]: https://github.com/ArabPixel/sdk/commit/7ca86e9b871b60311c2ce87f4a6be06478751026 "Corrección del sample kdump"

[8]: https://github.com/ArabPixel/sdk/commit/546bb1c513a75885def8ba2598b58fb69a44226b "Soporte 13.02 en crt/kernel.c"

[9]: https://github.com/adri22235/ps4-suid-scanner "Repositorio de documentación Celsius"

[10]: https://github.com/adri22235/ps4-suid-scanner/commit/6cacb2432f9940a5710a8d13895d4c799342cca6 "Tabla 13.04 atribuida a Pharaoh2k"

[11]: https://github.com/adri22235/ps4-suid-scanner/commit/96a79482d249fdbc6101bc641241488de66c313d "Esqueleto stage2 Jordy/Celsius"

[12]: https://raw.githubusercontent.com/adri22235/ps4-suid-scanner/main/jordy_stage2.js "Fuente actual jordy_stage2.js"

[13]: https://github.com/ps4-payload-dev/elfldr/releases "Releases elfldr 13.02/13.04/13.50"

[14]: https://github.com/Scene-Collective/ps4-hen/releases "Releases ps4-hen"

[15]: https://x.com/calmboy2019/status/2078549759460094065 "Anuncio público de Dr.Yenyen sobre Celsius"

[16]: https://gamegaz.com/2026071945823/ "GameGaz: Celsius hasta 13.04"

[17]: https://wikova.com/wiki/DQm4J1HU "Síntesis Wikova sobre jailbreak PS4"

[18]: https://www.playstation.com/en-us/support/hardware/ps4/system-software/ "Página oficial de software PS4 de Sony"

[19]: https://fail0verflow.com/blog/2017/ps4-crashdump-dump/ "Ejemplo histórico de dump de kernel PS4 1.01"

[20]: https://fail0verflow.com/blog/2017/ps4-namedobj-exploit/ "Ejemplo histórico de reverse engineering de kernel PS4 1.01"

[21]: https://github.com/sleirsgoevy/ps4-hamachi/issues/22 "Reverse engineering de dump propio 10.50"

[22]: https://www.reddit.com/r/ps4homebrew/comments/1sm5z56/ "Rumor secundario sobre exploit Gezine 13.50"
