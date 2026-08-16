# PS4-13.52-Jailbreak-Research

**Investigación y reverse engineering del firmware PlayStation 4 13.52. Proyecto en desarrollo — no es un jailbreak.**

> **Estado crítico:** este repositorio no contiene un jailbreak ni un exploit confirmado. Los nombres de funciones, offsets, puntos de entrada y vulnerabilidades deben tratarse según su clasificación de evidencia. Las afirmaciones de esta documentación no sustituyen una demostración reproducible e independiente.

Este README combina la documentación de la auditoría estática de `libkernel_sys` con el material histórico de investigación de firmware que existía en `origin/main`. Las dos líneas se conservaron mediante un merge no destructivo. Las secciones heredadas se mantienen como documentación de contexto y no convierten una afirmación histórica en una validación nueva.

## Alcance y metodología

El repositorio contiene herramientas y artefactos de investigación para PS4 FW 13.04/13.52, además de tres chunks y un blob combinado atribuidos por la fuente original a una captura de `libkernel_sys.sprx`. La auditoría del dump es estática: lee bytes, calcula hashes, comprueba concatenación y desensambla como x86-64 con `objdump`. No ejecuta el dump, exploits, payloads ni código recuperado, y no requiere hardware.

El dump binario ya formaba parte del corpus. No se añaden otros dumps propietarios, eboots, secretos, claves, credenciales ni artefactos de hardware. Los análisis nuevos se guardan como texto/JSON y pueden regenerarse con los scripts de `tools/`.

## Contenido del repositorio

| Área | Contenido |
|---|---|
| Dump de libkernel | `libkernel_sys_13.52.bin`, `lk_dump1.bin`, `lk_dump2.bin`, `lk_dump3.bin` |
| Auditoría reproducible | `tools/verify_offsets.py`, `tools/analyze_xref_versions.py`, `tools/run_static_audit.sh` |
| Resultados | `analysis/` con hashes, XREFs, consumidores de versión, fingerprints y JSON |
| Documentación | `AUDIT_REPORT.md`, `RESEARCH_STATUS.md`, `docs/` |
| Investigación de offsets | `1304.c`, `1304.h`, `1352_offsets.txt`, `kpayload/` |
| Scanner BD-J histórico | `src/org/bdj/SuidScanner.java`, `scanner_1304.iso` |
| Installer y payload SDK | `installer/`, `kpayload/`, `third_party/ps4-payload-sdk` |
| Investigación adicional | `cve_analysis.md`, auditorías de entrada y documentos de pmap/SYSENT |

Los artefactos generados por build y los archivos privados locales están excluidos mediante `.gitignore`. El ISO, los binarios y otros artefactos que ya estaban en la línea histórica remota se conservan por continuidad del corpus, pero su presencia no implica que sean una cadena de entrada FW 13.52.

## Integridad del corpus libkernel

| Artefacto | Tamaño | SHA-256 |
|---|---:|---|
| `libkernel_sys_13.52.bin` | 479232 bytes (`0x75000`) | `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c` |
| `lk_dump1.bin` | 159744 bytes (`0x27000`) | ver `analysis/hash_inventory.txt` |
| `lk_dump2.bin` | 159744 bytes (`0x27000`) | ver `analysis/hash_inventory.txt` |
| `lk_dump3.bin` | 159744 bytes (`0x27000`) | ver `analysis/hash_inventory.txt` |

La concatenación exacta es `lk_dump1.bin || lk_dump2.bin || lk_dump3.bin`; sus bases son `0x00000`, `0x27000` y `0x4e000`. El rango real del combinado es `0x00000–0x74fff`. La descripción histórica que indicaba `0x75fff` y “468 KB” era incorrecta y se corrige aquí.

## Reproducción del análisis estático

Desde la raíz del repositorio:

```bash
./tools/run_static_audit.sh
```

El comando genera `analysis/verify_offsets.json`, vuelve a generar `analysis/xref_version_analysis_13.52.txt` y `.json`, y actualiza los hashes locales. También puede ejecutarse cada herramienta por separado:

```bash
python3 tools/verify_offsets.py --repo . --json
python3 tools/analyze_xref_versions.py ./libkernel_sys_13.52.bin --out-dir ./analysis
```

El analizador de XREFs escanea el desensamblado completo y busca referencias RIP-relative cuyos destinos son explícitos en los comentarios de `objdump`. Las referencias indirectas, tablas sin relocaciones y símbolos externos se clasifican como `UNKNOWN`; no se convierten en nombres por coincidencia de prólogo.

## Estado reproducible de build

El submódulo `third_party/ps4-payload-sdk` está fijado e inicializado en `46efae910f3705e0171edea5b94e572d01bc00e8` (`Add 13.52 support`). Con GCC 13.3, GNU Make, `xxd`, `objcopy` y las herramientas presentes en Ubuntu, `make -C kpayload` y `make -C installer` terminaron correctamente en el entorno host. Esto demuestra compilabilidad host de las fuentes y no demuestra ABI, ejecución o compatibilidad funcional en una PS4.

Los artefactos de build son regenerables y están excluidos por `.gitignore`. No se ejecutaron payloads, HEN, ISO ni código destinado a modificar una consola. El workflow de CI fija las acciones principales y el SDK al commit exacto del submódulo, pero aún requiere una ejecución real en GitHub para validar el runner.

## Resultados estáticos principales

| Offset | Atribución de la fuente | Resultado estático actual |
|---|---|---|
| `0x510` | `jitshm_create` | stub que carga syscall `0x215`; nombre semántico no demostrado por símbolos |
| `0x530` | `jitshm_alias` | stub que carga syscall `0x216`; nombre semántico no demostrado por símbolos |
| `0x1bb0` | `error` / `__error` | helper con acceso TLS/global y numerosas llamadas; identidad exacta de export pendiente |
| `0x13b20` | `usleep` | función temporal compatible con espera; el nombre exacto depende del anchor/artefactos externos |
| `0x114e0` | `mmap` | entrada de dispatch con múltiples callers; nombre `mmap` no probado sólo por el salto |
| `0x15460` | `pread` | wrapper de lectura posicionada compatible con la tabla de dispatch |
| `0x15490` | `pwrite` | wrapper de escritura posicionada compatible con la tabla de dispatch |
| `0x154f0` | `lseek` | wrapper de posicionamiento compatible con la tabla de dispatch |
| `0x14870`, `0x148a0`, `0x148d0`, `0x14900` | `read`, `write`, `open`, `close` | prólogos y wrappers estructuralmente compatibles; semántica exacta pendiente |
| `0x15310`, `0x19320`, `0x45f0`, `0xc990` | `stat`, `notify`, `socket`, `connect` | patrones compatibles, sin tabla de símbolos independiente |

En `0x510` y `0x530` se observan respectivamente `rax = 0x215` y `rax = 0x216`, traslado de `rcx` a `r10`, `syscall`, rama de error y retorno. Los callers estáticos `0x16c69` y `0x16ca9` llaman a esos stubs. Esto confirma los números syscall y la relación caller/stub, pero no demuestra por sí solo los nombres de export.

`0x13b20` es compatible con una operación temporal por su aritmética, helpers y cadena que alcanza `0x1670`, donde se observa `rax = 0xf0`. El nombre exacto `sceKernelUsleep` sigue siendo potencial sin eboot, exports o GOT.

## XREFs de versionado

| Cadena | XREFs de archivo | Funciones probables |
|---|---|---|
| `kern.sdk_version` en `0x374a9` | `0x197a7`, `0x19903`, `0x19a6b` | `0x19790`, `0x198e0`, `0x19a40` |
| `%2x.%03x.%03x` en `0x374ba` | `0x197f4` | `0x19790` |
| `machdep.upd_version` en `0x378c0` | `0x1be37` | `0x1be10` |
| `machdep.lower_limit_upd_version` en `0x378d4` | `0x1be97` | `0x1be70` |
| `machdep.lower_limit_sysex_version` en `0x378f4` | `0x1bef9` | `0x1bed0` |
| `machdep.system_ex_version` en `0x37916` | `0x1bf78` | `0x1bf40` |

Las funciones de versión consultan nombres mediante `0x10240`. La función alrededor de `0x19790` recupera un valor de cuatro bytes, extrae campos con `BEXTR`, `AND 0xfff` y `>> 0x18`, y usa `%2x.%03x.%03x`. Esto demuestra un mecanismo de consulta/formateo, no el valor runtime de firmware. No se encontró la cadena literal inequívoca `13.52`, `13_52` o `1352` dentro del blob.

## GOT y versión exacta

La fuente original propone calcular la base mediante `EBOOT_GOT[0x0083d1c0] - 0x013b20`. El blob no contiene el eboot ni el valor runtime del slot GOT.

| Proposición | Estado |
|---|---|
| Existe una función temporal en `0x13b20` | fuertemente soportado |
| `0x13b20` es compatible con `sceKernelUsleep` | fuertemente soportado |
| Es exactamente el export `sceKernelUsleep` | potencial; falta export/mapa |
| `0x0083d1c0` es el GOT slot indicado | desconocido sin el eboot |
| La resta produce la base correcta | condicional; no verificable con este corpus |
| El blob demuestra exactamente FW 13.52 | no verificable desde el blob aislado |

El artefacto mínimo siguiente es el eboot exacto de Okage v1.01, o un mapa de relocaciones/imports que identifique `0x0083d1c0`, además de un manifest/hash que relacione la imagen con FW 13.52.

## Investigación histórica de firmware 13.04/13.52

La siguiente información se conserva de la línea histórica de `firmware-lab`. Sus afirmaciones mantienen la clasificación indicada y no deben interpretarse como una confirmación nueva derivada del dump libkernel.

### Entry points y estado histórico

La documentación histórica identifica BD-JB como un punto de entrada investigado para 13.04 y registra análisis de WebKit DOM, getters y LLInt OOB. También menciona PlayStation Vue como posible punto de entrada Celsius. Estas referencias pertenecen a la investigación de 13.04 y a documentación externa; no constituyen una cadena 13.52 reproducible dentro de este repositorio.

La documentación histórica describe Celsius (`ffs_mount`) como un integer overflow en `ffs_mountfs()` que se considera funcional hasta 13.04 y parcheado en 13.50. También conserva el análisis de CVE-2026-49415 como candidato bajo investigación. La presencia de estos documentos no convierte el resultado en un exploit confirmado para 13.52.

### Scanner SUID/SGID

`src/org/bdj/SuidScanner.java` y `scanner_1304.iso` pertenecen al scanner histórico. El scanner busca binarios SUID/SGID mediante una entrada BD-JB de usuario, usa operaciones FreeBSD (`open`, `getdents`, `stat`) a través de la API Java y guarda resultados en `/mnt/usb0/suid_scan.txt` según la documentación histórica.

El uso documentado del scanner requiere grabar `scanner_1304.iso` en BD-R, insertar el disco y un USB. Estas instrucciones son históricas y específicas del artefacto 13.04. El ISO no debe presentarse como una entrada 13.52.

### Offsets de kernel 13.04 y 13.52

La tabla completa histórica de 13.04 se conserva en `1304.c`/`1304.h`. La tabla parcial de 13.52 conserva estos valores:

```text
PRISON0    = 0x111FA18
ROOTVNODE  = 0x2136E90
SYSENT     = 0x1102B70
unknown1   = 0x4D6D0
unknown2   = 0xE6C60
```

La documentación asociada indica que los offsets de 13.52 fueron contrastados con tablas públicas, pero permanecen sin verificar en hardware. `docs/1352-offset-audit.md` documenta especialmente la divergencia y resolución del valor `SYSENT_addr = 0x01102B70`. La tabla debe tratarse como parcial y de confianza limitada.

### Entrada 13.52 y límites

La documentación histórica declara expresamente que el repositorio no contiene una cadena pública completa de entrada, loader y kernel para 13.52. `scanner_1304.iso` es un artefacto BD-J de 13.04 y no debe presentarse como entry point 13.52. Esta limitación es coherente con la auditoría del dump.

### MP4 y CVE históricos

La documentación histórica conserva el análisis de un MP4 malformado que provoca crashes reportados en FW 11.00 y posiblemente 13.04, con una estructura `moov.udta.meta` y offsets de inyección documentados. Su estado es “under investigation” y no demuestra un exploit 13.52.

También conserva estas clasificaciones históricas: CVE-2026-7270 descartada por incompatibilidad con FreeBSD 9; CVE-2026-49415 como candidata; y Celsius como confirmado para 13.04. Deben mantenerse separadas de cualquier conclusión sobre 13.52.

## Estado de evidencia

| Categoría | Resultado |
|---|---|
| **CONFIRMADO** | hash del combinado; concatenación de chunks; offsets de archivo; instrucciones syscall `0x215`, `0x216` y `0xf0`; XREFs RIP-relative enumeradas; existencia de strings y código de consulta de versión |
| **FUERTEMENTE SOPORTADO** | pertenencia a la familia libkernel/Orbis; helper TLS/error alrededor de `0x1bb0`; función temporal alrededor de `0x13b20`; dispatch alrededor de `0x114d0–0x11520`; consultas de versión mediante `0x10240` |
| **POTENCIAL** | nombres semánticos `usleep`, `jitshm_create`, `jitshm_alias`, `mmap`, `connect` y wrappers POSIX, a falta de exports/relocations |
| **NO VERIFICABLE** | versión exacta 13.52 desde el blob solo; GOT del eboot; validación de hardware; deltas entre firmwares sin imágenes comparables |
| **CONTRADICHO** | rango/tamaño histórico del README libkernel: el archivo real termina en `0x74fff` y mide `0x75000` bytes |

## Documentación y resultados

`RESEARCH_STATUS.md` contiene el estado resumido y las prioridades. `AUDIT_REPORT.md` contiene la auditoría profunda: inventario, errores corregidos, XREFs, funciones, scanners, contradicciones, límites y próximos pasos. Los artefactos reproducibles están en `analysis/`.

## Referencias históricas

- [BD-JB-1250](https://github.com/ps3120/BD-JB-1250) por ps3120/Gezine.
- [Scene-Collective/ps4-hen](https://github.com/Scene-Collective/ps4-hen) para el formato de offsets.
- [PPPwn](https://github.com/TheOfficialFloW/PPPwn) como referencia de arquitectura de exploit.
- [mast1c0re 13.52 research](https://github.com/Suchi96/mast1c0re-13_52-test) como contexto público relacionado.
- [CTurt mast1c0re writeup](https://cturt.github.io/mast1c0re.html) como contexto histórico.

## Créditos heredados

La línea histórica reconoce a ps3120, Gezine, Scene-Collective, Pharaoh2k, bollars, MasterMaind, Shunsui y Victor por los artefactos y análisis referenciados. La atribución no equivale a validación independiente de todas las afirmaciones.

## Licencia y seguridad

Esta investigación es para fines educativos y de seguridad autorizada. No se debe ejecutar ningún payload, modificar hardware ni probar una cadena de explotación sin autorización explícita. El proyecto no es un jailbreak y no afirma que exista uno confirmado.
