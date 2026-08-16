# Auditoría profunda del repositorio PS4 13.52

## 1. Alcance y conclusión

Esta auditoría revisa el repositorio completo, su historial Git, el README original, los tres chunks, el blob combinado, los offsets documentados y los resultados/scripts de análisis disponibles. La revisión se ejecutó de forma estática. No se ejecutó el dump, ningún payload, exploit o código recuperado, y no se utilizó hardware.

> **Conclusión:** el corpus es reproducible e internamente coherente como blob x86-64 de la familia Sony/Orbis `libkernel`, pero la correspondencia exacta con FW 13.52 no queda demostrada por el blob aislado. Tampoco existe un jailbreak ni exploit confirmado en este repositorio.

## 2. Inventario del repositorio y Git

Al inicio del trabajo el repositorio tenía únicamente `README.md`, tres chunks y el combinado. La rama activa era `main`, limpia y alineada con `origin/main`. El historial contenía tres commits: inicialización, actualización del README y subida de los archivos binarios. No había tags ni submódulos. El repositorio no tenía `.gitignore` ni reglas LFS.

| Elemento | Resultado |
|---|---|
| Remoto original | `https://github.com/Suchi96/PS4_13_52_libkerneldump.git` |
| Rama auditada | `main` |
| Historia original | 3 commits |
| Código original | no había C/C++/Rust; sólo README y binarios |
| Submódulos/tags | no encontrados |
| Cambios de esta auditoría | documentación, scripts y análisis reproducible; no se modifica el contenido de los dumps |

El análisis histórico muestra que las afirmaciones fuertes del README fueron introducidas junto con el README y no están acompañadas en el repositorio por logs de captura, el eboot, un manifest de firmware, un mapa de símbolos o dumps comparativos.

## 3. Integridad de los binarios

El combinado tiene 479232 bytes (`0x75000`) y SHA-256:

```text
ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c
```

Los tres chunks tienen 159744 bytes (`0x27000`) cada uno. La concatenación exacta `lk_dump1.bin || lk_dump2.bin || lk_dump3.bin` produce el SHA-256 del combinado. Las bases correctas son `0x00000`, `0x27000` y `0x4e000`; el último byte real es `0x74fff`.

El README original indicaba `0x75fff` y “468 KB”. Esa descripción es incorrecta y se corrigió. La corrección no cambia los bytes ni la atribución de procedencia; sólo corrige el rango/tamaño reproducible.

## 4. Scanner de offsets

El scanner legacy comprobó que los offsets documentados que se presentan como funciones tienen prólogos estructuralmente compatibles con x86-64. Los stubs de syscall y la entrada de dispatch no tienen prólogo de función normal, lo cual es esperable para esos tipos de entrada.

| Nombre de fuente | Offset | Bytes iniciales | Resultado del scanner |
|---|---:|---|---|
| usleep | `0x13b20` | `55 48 89 e5 41 56 53 48` | prólogo sí |
| open | `0x148d0` | `55 48 89 e5 31 c0 e8 b5` | prólogo sí |
| close | `0x14900` | `55 48 89 e5 e8 07 80 ff` | prólogo sí |
| read | `0x14870` | `55 48 89 e5 e8 67 87 ff` | prólogo sí |
| write | `0x148a0` | `55 48 89 e5 e8 a7 8c ff` | prólogo sí |
| notify | `0x19320` | `55 48 89 e5 41 57 41 56` | prólogo sí |
| socket | `0x45f0` | `55 48 89 e5 41 57 41 56` | prólogo sí |
| connect | `0xc990` | `55 48 89 e5 41 57 41 56` | prólogo sí |
| stat | `0x15310` | `55 48 89 e5 e8 37 9a fe` | prólogo sí |
| pread | `0x15460` | `55 48 89 e5 e8 87 c0 ff` | prólogo sí |
| pwrite | `0x15490` | `55 48 89 e5 e8 67 c0 ff` | prólogo sí |
| lseek | `0x154f0` | `55 48 89 e5 e8 d7 bf ff` | prólogo sí |
| unlink | `0x14930` | `55 48 89 e5 e8 97 a1 fe` | prólogo sí |
| JITSHM create | `0x510` | `48 c7 c0 15 02 00 00 49` | stub, no prólogo |
| JITSHM alias | `0x530` | `48 c7 c0 16 02 00 00 49` | stub, no prólogo |
| dispatch candidate | `0x114e0` | `e9 eb 03 ff ff 90 90 90` | salto, no prólogo |
| error helper | `0x1bb0` | `55 48 89 e5 48 8b 05 15` | prólogo sí |

El scanner sólo demuestra una forma binaria compatible. No demuestra nombres, exportaciones ni firmware.

## 5. JITSHM y syscall stubs

En `0x510` se observa:

```asm
mov rax, 0x215
mov r10, rcx
syscall
jb  error_path
ret
```

En `0x530` se observa la misma estructura con `rax = 0x216`. Las referencias directas previamente encontradas son `0x16c69 → call 0x510` y `0x16ca9 → call 0x530`. Esto confirma los números de syscall y la relación caller/stub. No demuestra por sí solo que los nombres de export sean `jitshm_create` y `jitshm_alias`; esa asignación es compatible con el README y el contexto JIT-SHM, pero requiere una tabla de símbolos/export o una referencia independiente.

## 6. Helper de error/TLS en `0x1bb0`

El helper comienza con un prólogo normal y accede a memoria global y a `fs:0x10`. Tiene un patrón compatible con obtención de estado TLS/error. El análisis anterior encontró un número elevado de llamadas internas, aproximadamente 586 en el desensamblado utilizado. La identidad como helper común está fuertemente soportada; el nombre exacto `__error` no está demostrado por una tabla de exports presente en el repo.

## 7. Función temporal `0x13b20`

`0x13b20` contiene una función con aritmética temporal y llamadas internas que pasan por `0xcc40` y alcanzan `0x1670`; `0x1670` carga `rax = 0xf0`, mueve `rcx` a `r10`, ejecuta `syscall`, comprueba error y retorna. Los callers analizados usan constantes y transformaciones compatibles con conversión a unidades temporales. Por eso la función es fuertemente compatible con una operación tipo sleep/usleep.

El nombre exacto `sceKernelUsleep` sigue siendo potencial porque el blob no contiene una tabla de símbolos ni el eboot que supuestamente contiene el GOT anchor.

## 8. Dispatch `0x114d0–0x11520` y wrappers I/O

`0x114e0` es una entrada de salto relativa a `0x18d0` y tiene múltiples callers. Las entradas vecinas forman una familia de dispatch. Los wrappers `0x15460`, `0x15490` y `0x154f0` llaman a entradas hermanas de esta familia, lo que hace compatible la relación con I/O posicionado `pread`, `pwrite` y `lseek`.

La estructura es evidencia de organización interna, no un símbolo. La identidad semántica de cada entrada requiere exports, comparación con una imagen conocida o seguimiento de argumentos hasta un syscall con número identificable.

## 9. XREFs de versionado

El analizador automático encontró estas XREF RIP-relative directas:

| String | Offset de datos | XREF | Bytes | Instrucción | Función probable |
|---|---:|---:|---|---|---:|
| `kern.sdk_version` | `0x374a9` | `0x197a7` | `48 8d 3d fb dc 01 00` | `lea rdi,[rip+0x1dcfb]` | `0x19790` |
| `kern.sdk_version` | `0x374a9` | `0x19903` | `48 8d 3d 9f db 01 00` | `lea rdi,[rip+0x1db9f]` | `0x198e0` |
| `kern.sdk_version` | `0x374a9` | `0x19a6b` | `48 8d 3d 37 da 01 00` | `lea rdi,[rip+0x1da37]` | `0x19a40` |
| `%2x.%03x.%03x` | `0x374ba` | `0x197f4` | `48 8d 15 bf dc 01 00` | `lea rdx,[rip+0x1dcbf]` | `0x19790` |
| `machdep.upd_version` | `0x378c0` | `0x1be37` | `48 8d 3d 82 ba 01 00` | `lea rdi,[rip+0x1ba82]` | `0x1be10` |
| `machdep.lower_limit_upd_version` | `0x378d4` | `0x1be97` | `48 8d 3d 36 ba 01 00` | `lea rdi,[rip+0x1ba36]` | `0x1be70` |
| `machdep.lower_limit_sysex_version` | `0x378f4` | `0x1bef9` | `48 8d 3d f4 b9 01 00` | `lea rdi,[rip+0x1b9f4]` | `0x1bed0` |
| `machdep.system_ex_version` | `0x37916` | `0x1bf78` | `48 8d 3d 97 b9 01 00` | `lea rdi,[rip+0x1b997]` | `0x1bf40` |

En todos los casos las referencias son offsets relativos al archivo porque el blob se analiza con VMA cero. No deben transformarse automáticamente en direcciones virtuales.

## 10. Consumidores de `kern.sdk_version`

La zona `0x19790` consulta `kern.sdk_version` mediante `0x10240` con buffer de 4 bytes. Si la consulta es correcta, usa el formato `%2x.%03x.%03x`; se observan `BEXTR` con control `0xc0c`, máscara `0xfff` y desplazamiento de `0x18`. El valor se obtiene en runtime; no aparece como literal `13.52`.

Las zonas `0x198e0` y `0x19a40` vuelven a consultar `kern.sdk_version` para realizar conversiones/comprobaciones adicionales. Se observan rutas de error que pasan por `0x1bb0` y, en determinados caminos, `0x13d90`.

## 11. Consumidores de `machdep.*`

Las funciones `0x1be10`, `0x1be70`, `0x1bed0` y `0x1bf40` pasan las cuatro strings `machdep.*` a `0x10240`. Usan buffers pequeños, checks de punteros y rutas de error. `0x1bfd0` y `0x1c030` continúan la familia de wrappers de consulta. El código demuestra consultas diferenciadas, pero no la semántica C exacta de cada buffer ni que el resultado sea una versión de firmware.

## 12. Búsqueda global de versiones

No se encontró dentro del blob la cadena literal inequívoca `13.52`, `13_52` o `1352`. Sí aparecen los nombres de variables, el formato de versión y constantes de extracción. Esto favorece que la imagen contenga infraestructura de consulta de versión, pero no fija el resultado runtime.

`J02697906` aparece en rutas internas de build relacionadas con pthread/libkernel. Es una huella de procedencia de build interno, no una prueba suficiente de FW 13.52.

## 13. Auditoría del README original

| Afirmación | Resultado de auditoría |
|---|---|
| Los chunks se concatenan en el orden indicado | confirmado |
| El combinado cubre `0x00000–0x75fff` | contradicho: cubre hasta `0x74fff` |
| El combinado mide 468 KB | contradicho en la convención usada: mide 479232 bytes |
| La captura procede de retail PS4 13.52 | no verificable desde el corpus; sólo afirmación de procedencia |
| El GOT `0x0083d1c0` contiene `sceKernelUsleep` | no verificable sin eboot |
| `0x13b20` es `usleep` | fuertemente soportado como función temporal; nombre exacto potencial |
| Todos los offsets fueron probados en hardware | no verificable en esta auditoría estática |
| Las deltas de 9.00/11.02 son reproducibles | no verificable: faltan dumps comparables |
| `0xc7e0` es `accept` y no `connect` | **NO VERIFICABLE** como nombre: el flujo llama al helper interno `0x15b0`, pero sin tabla de símbolos/syscall sólo queda parcialmente soportado que no es una llamada directa observable a `connect` |
| bind/listen/setsockopt no tienen wrappers | no verificable sólo por ausencia o búsqueda parcial |
| BSD raw syscall implica validación de RSP | no verificable desde este blob |

## 14. Errores encontrados y corregidos

Se corrigió el rango/tamaño del README. También se identificó una limitación del scanner original: el match de prólogo es sólo una prueba de forma y no debe presentarse como confirmación de identidad. La documentación nueva lo etiqueta como sanity check.

Se corrigió el alcance de la documentación para no presentar como confirmado el firmware exacto, el GOT, los nombres de export ni la validación por hardware. Se añadió un analizador portable de XREFs que acepta la ruta del dump y genera los resultados dentro de `analysis/`.

La auditoría no encontró corrupción en los chunks ni discrepancia de hash con el SHA-256 facilitado. Tampoco encontró un valor literal de firmware que contradiga 13.52. La inspección adicional de `0xc7e0` mostró un wrapper con TLS que llama a `0x15b0`; `0xc970` llama a `0x271a0` con constantes, mientras `0xc990` llama a `0x1610` y realiza bookkeeping TLS. Esta estructura no permite etiquetar `0xc7e0` como `accept` ni `0xc970`/`0xc990` como `connect` sin una tabla semántica externa.

## 15. Pistas nuevas

La pista más interesante es la cadena completa de `kern.sdk_version`: string, tres consumidores, helper común `0x10240`, buffer de 4 bytes, extracción de campos y formato `%2x.%03x.%03x`. Es evidencia más fuerte que la mera presencia de una etiqueta, pero todavía no contiene el valor runtime.

La segunda pista es la estructura de la familia dispatch `0x114d0–0x11520` y su relación con wrappers I/O posicionados. La tercera es la coincidencia entre los stubs `0x510/0x530`, los callers `0x16c69/0x16ca9` y los números syscall `0x215/0x216`. La inspección de conectividad añadió una corrección importante: los destinos internos `0x15b0`, `0x1610` y `0x271a0` siguen sin nombre demostrado; no se debe repetir la atribución `accept(#30)` sin el contexto de syscall/export.

## 16. Pistas prioritarias

La primera prioridad es conseguir el eboot exacto de Okage Shadow King v1.01 con su tabla GOT/relocations y comprobar `0x0083d1c0`. La segunda es obtener un `libkernel_sys` de firmware conocido para comparación byte a byte. La tercera es conseguir un manifest o hash de build que relacione `J02697906` con 13.52. La cuarta es reconstruir `0x10240` con imports/exports o una imagen con símbolos.

## 17. Qué falta analizar

Faltan el eboot, exports, relocaciones, un log de captura, una lectura runtime de `kern.sdk_version`, imágenes comparativas de 9.00/11.02/12.52/13.04, y evidencia independiente de la semántica de cada syscall/wrapper. No se debe cubrir esa ausencia con nombres derivados del README.

## 18. Archivos incorporados

| Ruta | Propósito |
|---|---|
| `tools/verify_offsets.py` | hashes, tamaños, concatenación y sanity checks |
| `tools/analyze_xref_versions.py` | XREFs RIP-relative, funciones y constantes de versionado |
| `tools/run_static_audit.sh` | ejecución reproducible de ambos análisis |
| `analysis/verify_offsets.json` | salida estructurada de integridad |
| `analysis/xref_version_analysis_13.52.txt` | informe automático de XREFs y funciones |
| `analysis/xref_version_analysis_13.52.json` | datos estructurados del análisis |
| `analysis/hash_inventory.txt` | hashes de chunks y combinado |
| `analysis/scanner_offsets_output.txt` | salida del scanner de offsets |
| `analysis/scanner_xrefs_output.txt` | salida del scanner legacy de XREFs |
| `analysis/phase14_*.txt` | consumidores de variables de versión |
| `analysis/phase16_binary_fingerprints.md` | huellas binarias por offset |
| `RESEARCH_STATUS.md` | estado resumido y prioridades |

No se añadieron desensamblados masivos ni archivos propietarios externos. Los artefactos grandes existentes son los binarios originales del corpus.

## 19. Confirmado, pendiente y no confirmado

**Confirmado:** hash del combinado, concatenación, tamaños, rangos reales, XREFs directas enumeradas, bytes de stubs `0x215/0x216/0xf0`, existencia de consultas de strings mediante funciones internas y presencia de patrones Orbis/libkernel.

**Fuertemente soportado:** familia libkernel/Orbis, helper TLS/error, función temporal, dispatch y wrappers I/O compatibles.

**Pendiente:** nombres semánticos exactos, GOT, versión exacta, comparación entre firmwares y validación externa.

**No confirmado:** jailbreak, exploit, kernel escape, ejecución nativa o cualquier impacto de seguridad.

## 20. Reproducibilidad y límites

Los scripts son herramientas de análisis de datos binarios; no ejecutan instrucciones del dump. El analizador usa `objdump -D -b binary -m i386:x86-64 -M intel` con VMA cero. En consecuencia, `0x197a7` significa offset dentro del archivo, no dirección virtual. Las XREF indirectas y los destinos sin relocaciones no se etiquetan como hechos.

## 21. Referencias

[1]: https://github.com/Suchi96/PS4_13_52_libkerneldump "Repositorio original auditado"
[2]: https://github.com/Suchi96/mast1c0re-13_52-test "Repositorio público relacionado de mast1c0re 13.52"
[3]: https://cturt.github.io/mast1c0re.html "Contexto histórico de mast1c0re y el emulador PS2"
