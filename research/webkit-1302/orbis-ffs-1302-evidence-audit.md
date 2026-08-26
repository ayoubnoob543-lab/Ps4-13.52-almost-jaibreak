# Orbis PS4 13.02 y `ffs_mountfs()` — auditoría de evidencia pública

**Fecha de corte:** 26 de agosto de 2026. **Método:** inventario de artefactos públicos y locales, revisión estática de código FreeBSD y comparación de procedencia. No se ejecutaron payloads, corrupción de memoria ni pruebas contra hardware.

## Resumen ejecutivo

No encontré un kernel Orbis 13.02, un dump retail 13.02, símbolos de FFS 13.02, pseudocódigo de `ffs_mountfs()` en Orbis, una tabla de referencias de esa función, ni un diff 13.02→13.50 que permita confirmar que el código vulnerable de FreeBSD existe en PS4 13.02.

El repositorio sí contiene varios artefactos 13.02 —headers de offsets, tablas SLOPOS, offsets de kexec, documentación y fuentes de WebKit—, pero ninguno es una implementación del kernel FFS. También contiene comentarios en `webkit_gadgets_1304.js` que afirman que la cadena “Celsius” está presente en 13.04 y que una string de `ffs_mountfs` aparece en el mismo offset; el archivo binario al que esos comentarios dicen referirse no está en el repositorio y no hay script reproducible que genere esas cifras. Esos comentarios son **SOURCE_ONLY**, no evidencia binaria.

La evidencia técnica sólida sólo demuestra tres hechos más limitados: (1) FreeBSD histórico tuvo errores de cálculo de tamaño en `ffs_mountfs()`/`ffs_reload()`; (2) FreeBSD corrigió una familia de esos errores en el commit `r309172` de 2016; y (3) fuentes de la escena atribuyen a Celsius un overflow UFS/FFS con alcance nominal hasta PS4 13.04 y parche supuesto en 13.50. La correspondencia exacta con Orbis 13.02 sigue siendo **HYPOTHESIS / UNVERIFIED_13_02**.

## Artefactos Orbis 13.02 encontrados

| Artefacto | Qué contiene | Qué no demuestra | Estado |
|---|---|---|---|
| `kpayload/include/offsets/1302.h` y `kpayload/source/offsets/1302.c` | Offsets de kernel utilizados por payload/kexec | No contiene FFS, `ffs_mountfs()` ni código de montaje | `SOURCE_ONLY` para FFS |
| `research/results/slopos/1302.h` | Tabla de offsets SLOPOS | No contiene bytes de kernel ni correspondencia de funciones FFS | `SOURCE_ONLY` |
| `research/webkit-1302/upstream/riyon-kernel.ts` | Tablas de payload y mmap/RWX | La entrada 13.02 no contiene payload Netctrl completo ni FFS | `VERIFIED` como contenido del repo; `UNVERIFIED_13_02` como exploit |
| `webkit_gadgets_1304.js` | Offsets de gadgets WebKit y comentarios de comparación | No incluye `1304_libSceNKWebKit.sprx.decrypted`, hashes ni bytes FFS | `SOURCE_ONLY` |
| `libkernel_sys_13.52.bin` | Artefacto binario de otra versión | No permite confirmar FFS 13.02 | `SOURCE_ONLY` fuera de objetivo |
| `scanner_1304.iso` | ISO/artefacto de scanner local | No es un kernel retail ni muestra `ffs_mountfs()` | `SOURCE_ONLY` |
| `PS4_1304_ISO_STATIC_LIST_2026-08-20.json` | Manifest estático | Metadata, no implementación de kernel | `SOURCE_ONLY` |
| `jordy_stage2.js` | Esqueleto experimental de ROP con comentarios Celsius | El propio archivo marca dlsym, pivot y ejecución como `TODO`/`INCOMPLETE` | `HYPOTHESIS` |

La búsqueda de archivos muestra que no existe en el repositorio el artefacto referenciado por el comentario `// Source: 1304_libSceNKWebKit.sprx.decrypted (68 MB) from zecoxao`. Tampoco aparecen kernels retail 13.02/13.04/13.50 ni un dump de filesystem Orbis con símbolos FFS.

## La afirmación local de `webkit_gadgets_1304.js`

El archivo contiene los comentarios:

> “Kernel comparison: 13.00 vs 13.04”
>
> “Same size: 20,080,104 bytes”
>
> “ffs_mountfs string at 0x7d021f in BOTH (Celsius NOT patched)”
>
> “CONFIRMED: Celsius (ffs_mount) is present in 13.04 kernel”

No hay, junto a esos comentarios, el par de archivos comparados, sus SHA-256, un script de extracción, un log de `readelf`/disassembler, una lista de referencias cruzadas ni una captura de pseudocódigo. Por ello, la frase “CONFIRMED” no puede aceptarse como `VERIFIED`. La única conclusión segura es que alguien escribió esa afirmación en un archivo local.

`jordy_stage2.js` es aún más explícito: la función `buildRopChain()` contiene comentarios “call mount → triggers ffs_mountfs → Celsius”, pero la resolución de `dlsym`, la dirección de la llamada y el pivot de ejecución están incompletos. El mismo archivo devuelve `false` y registra que la ejecución no está implementada. Esto clasifica la cadena como `HYPOTHESIS`, no como prueba de que Orbis 13.02 alcance FFS.

## Código histórico de FreeBSD

El archivo público de FreeBSD 9.1 revisado contiene `ffs_mountfs()` y `ffs_reload()` con el patrón relevante. En `ffs_mountfs()` se leen el superbloque y campos como `fs_bsize`, `fs_fsize`, `fs_cssize`, `fs_ncg` y `fs_contigsumsize`. El cálculo observado es conceptualmente:

```c
size = fs->fs_cssize;
blks = howmany(size, fs->fs_fsize);
if (fs->fs_contigsumsize > 0)
    size += fs->fs_ncg * sizeof(int32_t);
size += fs->fs_ncg * sizeof(u_int8_t);
space = malloc((u_long)size, M_UFSMNT, M_WAITOK);
```

Después se copia información de grupos de cilindros y, cuando `fs_contigsumsize > 0`, se ejecuta un bucle que escribe `fs->fs_ncg` entradas en `fs_maxcluster`. Estos hechos están **VERIFIED para la fuente FreeBSD 9.1 consultada**, no para Orbis.

El commit FreeBSD `r309172`, enviado por Kirk McKusick el 26 de noviembre de 2016, documenta una corrección de posibles overflows al calcular tamaños auxiliares durante el montaje y reload. El diff cambia variables de `int` a `u_long`, elimina conversiones en llamadas a `malloc`, y separa `len` de `size` para atributos de GEOM. El commit está confirmado para stable/11. NVD registra además el antecedente CVE-2006-5679 para FreeBSD 6.1.

La existencia de un fix en stable/11 no demuestra que el fix esté o no esté en Orbis. Sony podría haber portado el fix, haber modificado el código, haber eliminado UFS/FFS de la ruta accesible o haber conservado el patrón con diferencias relevantes.

## Comparación solicitada de tipos y cálculos

| Elemento | FreeBSD 9.1 público | Orbis 13.02 | Conclusión |
|---|---|---|---|
| `fs_cssize` | Consumido como tamaño inicial | No hay bytes/símbolos Orbis públicos | `UNVERIFIED_13_02` |
| `fs_contigsumsize` | Condiciona sumas y bucle `fs_maxcluster` | No identificado en Orbis | `UNVERIFIED_13_02` |
| `fs_ncg` | Participa en multiplicaciones y controla iteraciones | No identificado en Orbis | `UNVERIFIED_13_02` |
| `fs_bsize` | Validación y tamaño de bloques | No identificado en Orbis | `UNVERIFIED_13_02` |
| `fs_fsize` | Usado por `howmany` y tamaño de copias | No identificado en Orbis | `UNVERIFIED_13_02` |
| `size` | `int` en el código antiguo revisado, con cast a `u_long` en `malloc` | Sin implementación Orbis | `UNVERIFIED_13_02` |
| Sumas antes de `malloc` | Sí, en FreeBSD 9.1 histórico | Sin bytes Orbis | `HYPOTHESIS` |
| Bucle posterior que consume `fs_ncg` | Sí, en FreeBSD 9.1 | Sin bytes Orbis | `HYPOTHESIS` |
| Fix `int`→`u_long` de r309172 | Confirmado en stable/11 | No comparable | `VERIFIED` sólo para FreeBSD |

## ¿Existe realmente `ffs_mountfs()` vulnerable en 13.02?

No hay evidencia pública suficiente para responder afirmativamente. La respuesta estricta es **“no demostrado”**, no “demostrado ausente”. La atribución de Celsius a `ffs_mountfs()` y el comentario local sobre un string en 13.04 son indicios, pero no identifican una función con bytes verificables, referencias, tipos ni flujo de control.

La clasificación correcta es `UNVERIFIED_13_02` para la existencia de la variante vulnerable en Orbis 13.02. La familia histórica de FFS es `VERIFIED` en FreeBSD; la correspondencia Orbis es `HYPOTHESIS`.

## ¿Qué partes de Orbis 13.02 podemos identificar?

Podemos identificar de forma limitada offsets y tablas de otras etapas, incluidos `sysent`, `prison0`, `kernel_map`, `rootvnode`, `pmap_extract`, `pmap_protect` y offsets de mmap/RWX. Esos datos permiten estudiar la organización de payloads y kexec, pero no prueban la presencia de FFS ni de Celsius.

No podemos identificar públicamente la dirección de `ffs_mountfs()`, `ffs_reload()`, sus referencias, la estructura `struct fs` efectiva de Orbis 13.02, los tipos compilados, la ruta de montaje expuesta al sandbox ni los consumidores de `fs_ncg`.

## ¿Qué diferencias hay frente a FreeBSD?

No existe un diff binario o de código Orbis que permita enumerarlas. Las diferencias confirmables son sólo de corpus: FreeBSD 9.1 tiene el código fuente disponible y Orbis 13.02 no. La base FreeBSD de PS4 está fuertemente modificada por Sony, y el nombre de una función o la herencia general de UFS no prueban identidad de implementación.

Por tanto, cualquier afirmación de que 13.02 conserva `int size`, las mismas sumas, el mismo cast a `u_long` o el mismo bucle `fs_ncg` debe clasificarse `HYPOTHESIS` hasta obtener bytes o pseudocódigo de Orbis.

## ¿Existe evidencia técnica del parche 13.50?

No. Hay afirmaciones secundarias de que Celsius fue parcheado en PS4 13.50 y comentarios locales que dicen “Celsius NOT patched” en una comparación 13.00/13.04, pero no hay artefactos verificables de 13.50 FFS. No se encontró un diff de función, hash pre/post, advisory de Sony, mensaje de HackerOne, cambio de string o pseudocódigo que vincule causalmente 13.50 con el supuesto parche.

La afirmación “parcheado en 13.50” es `SOURCE_ONLY`. La afirmación local “no parcheado en 13.04” también es `SOURCE_ONLY`; no convierte la presencia de una string en prueba de que el comportamiento vulnerable sobreviva.

## Clasificación consolidada

| Hallazgo | Clasificación |
|---|---|
| `ffs_mountfs()` vulnerable como familia histórica de FreeBSD | `VERIFIED` |
| Fix de tamaños UFS/FFS en FreeBSD r309172 | `VERIFIED` |
| Código equivalente presente en Orbis 13.02 | `HYPOTHESIS` |
| Variante vulnerable de Celsius presente en Orbis 13.02 | `UNVERIFIED_13_02` |
| Comentario local identifica string FFS en 13.04 | `SOURCE_ONLY` |
| Celsius cubre nominalmente 13.04 | `SOURCE_ONLY` |
| Celsius funciona en PS4 13.02 o 13.04 | `UNVERIFIED_13_02` |
| Patch específico de Celsius en 13.50 | `SOURCE_ONLY` |
| Offsets 13.02 demuestran FFS/Celsius | `DISPROVEN` como inferencia |
| `jordy_stage2.js` demuestra una ruta funcional | `DISPROVEN` como inferencia; el archivo marca TODO/INCOMPLETE |

## Respuestas finales

### 1. ¿Hay evidencia de que `ffs_mountfs()` vulnerable exista realmente en 13.02?

**No.** Hay una familia histórica real de errores FFS y afirmaciones de terceros sobre Celsius, pero no hay bytes, símbolos o pseudocódigo Orbis 13.02 que permitan confirmarlo. Estado: `UNVERIFIED_13_02`.

### 2. ¿Qué partes del código Orbis 13.02 podemos identificar?

Sólo offsets y tablas de otras superficies —payload/kexec, mmap/RWX, `sysent`, `prison0`, pagetables—. No se puede identificar de manera pública la implementación de `ffs_mountfs()`, `ffs_reload()` o la `struct fs` compilada de Orbis 13.02.

### 3. ¿Qué diferencias hay frente al código vulnerable de FreeBSD?

No se puede establecer ninguna diferencia funcional porque falta el objeto de comparación Orbis. Sí sabemos que el código FreeBSD 9.1 histórico usa los campos y cálculos indicados, mientras que Orbis 13.02 sólo está representado por afirmaciones y offsets no relacionados. Cualquier diferencia adicional sería hipótesis.

### 4. ¿Existe evidencia técnica del supuesto parche de 13.50?

**No.** Sólo existe repetición de fuentes secundarias y coincidencia temporal. Estado: `SOURCE_ONLY`.

### 5. ¿Celsius pasa de “hipótesis” a “candidato respaldado” para 13.02?

Pasa a ser un **candidato documental plausible**, porque la familia FFS es real y el rango 13.04 se repite en varias fuentes; no pasa a `VERIFIED` ni a `CORROBORATED` para Orbis 13.02. La clasificación correcta sigue siendo `HYPOTHESIS / UNVERIFIED_13_02`.

### 6. ¿Qué artefacto exacto falta?

Falta un **kernel Orbis retail 13.02 legítimo, con procedencia y SHA-256 verificables**, o un dump/pseudocódigo equivalente que incluya la implementación efectiva de `ffs_mountfs()`/`ffs_reload()`, referencias a `fs_cssize`, `fs_contigsumsize`, `fs_ncg`, `fs_bsize` y `fs_fsize`, tipos compilados, cálculos antes de `malloc` y bucles posteriores. Para confirmar el parche también hace falta el mismo artefacto de 13.50 y un diff reproducible de la función.

## Referencias

[1]: https://mail-archive.freebsd.org/cgi/mid.cgi?201611260043.uAQ0hcWs008737 "FreeBSD r309172, fix de tamaños UFS/FFS"
[2]: https://nvd.nist.gov/vuln/detail/CVE-2006-5679 "NVD CVE-2006-5679"
[3]: https://www.psdevwiki.com/ps4/Vulnerabilities "PSDevWiki Vulnerabilities"
[4]: https://www.psdevwiki.com/ps4/Bugs "PSDevWiki Bugs"
[5]: https://github.com/adri22235/ps4-suid-scanner "Repositorio secundario de Celsius"
[6]: https://x.com/calmboy2019/status/2078549759460094065 "Primera difusión localizada de Celsius"
[7]: https://gamegaz.com/2026071945823/ "GameGaz: Celsius by bollars"
[8]: https://consolemods.org/wiki/PS4:Exploit_Chart "ConsoleMods Exploit Chart"

> **Conclusión:** hoy no puede demostrarse que Orbis PS4 13.02 conserve el código vulnerable de `ffs_mountfs()` asociado a Celsius. Lo que existe es una combinación de código histórico FreeBSD, afirmaciones públicas de alcance hasta 13.04 y comentarios locales no reproducibles. El artefacto decisivo sigue siendo un kernel Orbis 13.02 legítimo con código/pseudocódigo FFS verificable, acompañado por su equivalente 13.50 para probar o refutar el parche.
