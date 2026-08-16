# PS4-13.52-Jailbreak-Research

**Investigación y reverse engineering del firmware PlayStation 4 13.52. Proyecto en desarrollo — no es un jailbreak.**

> **Estado crítico:** este repositorio no contiene un jailbreak ni un exploit confirmado. Los nombres de funciones y offsets documentados deben tratarse como hipótesis o resultados de análisis estático hasta que exista evidencia reproducible e independiente. No se deben ejecutar payloads ni usar estos datos contra hardware sin autorización.

## Alcance

El repositorio conserva tres chunks y un blob combinado atribuidos por la fuente original a una captura de `libkernel_sys.sprx`. La auditoría actual es estática: lee bytes, calcula hashes, comprueba la concatenación y desensambla el blob como x86-64 con `objdump`. No ejecuta el dump, exploits, payloads ni código recuperado, y no requiere hardware.

El dump binario se mantiene en el repositorio porque ya formaba parte del corpus de investigación. No se añaden otros dumps propietarios, eboots, secretos, claves, credenciales ni artefactos de hardware. Los nuevos análisis se guardan como texto/JSON y pueden regenerarse con los scripts de `tools/`.

## Integridad del corpus

| Artefacto | Tamaño | SHA-256 |
|---|---:|---|
| `libkernel_sys_13.52.bin` | 479232 bytes (`0x75000`) | `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c` |
| `lk_dump1.bin` | 159744 bytes (`0x27000`) | ver `analysis/hash_inventory.txt` |
| `lk_dump2.bin` | 159744 bytes (`0x27000`) | ver `analysis/hash_inventory.txt` |
| `lk_dump3.bin` | 159744 bytes (`0x27000`) | ver `analysis/hash_inventory.txt` |

La concatenación exacta es `lk_dump1.bin || lk_dump2.bin || lk_dump3.bin`; sus bases son `0x00000`, `0x27000` y `0x4e000`. El rango real del combinado es `0x00000–0x74fff`. El README histórico decía `0x75fff` y “468 KB”; esa descripción era incorrecta y se corrige aquí.

## Reproducción

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

## XREFs de versionado

La auditoría encontró estas referencias directas RIP-relative:

| Cadena | XREFs de archivo | Funciones probables |
|---|---|---|
| `kern.sdk_version` en `0x374a9` | `0x197a7`, `0x19903`, `0x19a6b` | `0x19790`, `0x198e0`, `0x19a40` |
| `%2x.%03x.%03x` en `0x374ba` | `0x197f4` | `0x19790` |
| `machdep.upd_version` en `0x378c0` | `0x1be37` | `0x1be10` |
| `machdep.lower_limit_upd_version` en `0x378d4` | `0x1be97` | `0x1be70` |
| `machdep.lower_limit_sysex_version` en `0x378f4` | `0x1bef9` | `0x1bed0` |
| `machdep.system_ex_version` en `0x37916` | `0x1bf78` | `0x1bf40` |

Las funciones de versión consultan nombres mediante el helper `0x10240`. La función alrededor de `0x19790` recupera un valor de cuatro bytes, extrae campos con `BEXTR`, `AND 0xfff` y `>> 0x18`, y usa el formato `%2x.%03x.%03x`. Esto demuestra un mecanismo de consulta/formateo, no el valor runtime de firmware. No se encontró la cadena literal inequívoca `13.52`, `13_52` o `1352` dentro del blob.

## GOT y versión exacta

La fuente original propone calcular la base mediante `EBOOT_GOT[0x0083d1c0] - 0x013b20`. El blob no contiene el eboot ni el valor runtime del slot GOT. Por ello:

| Proposición | Estado |
|---|---|
| Existe una función temporal en `0x13b20` | fuertemente soportado |
| `0x13b20` es compatible con `sceKernelUsleep` | fuertemente soportado |
| Es exactamente el export `sceKernelUsleep` | potencial; falta export/mapa |
| `0x0083d1c0` es el GOT slot indicado | desconocido sin el eboot |
| La resta produce la base correcta | condicional; no verificable con este corpus |
| El blob demuestra exactamente FW 13.52 | no verificable desde el blob aislado |

El artefacto mínimo siguiente es el eboot exacto de Okage v1.01, o un mapa de relocaciones/imports que identifique `0x0083d1c0`, además de un manifest/hash que relacione la imagen con FW 13.52.

## Documentación

`RESEARCH_STATUS.md` contiene el estado actual y las prioridades. `AUDIT_REPORT.md` contiene la auditoría completa: inventario, errores corregidos, XREFs, funciones, scanners, contradicciones, límites y próximos pasos. Los artefactos reproducibles están en `analysis/`.

## Referencias

[1]: https://github.com/Suchi96/mast1c0re-13_52-test "Contexto público mast1c0re 13.52"
[2]: https://cturt.github.io/mast1c0re.html "CTurt, mast1c0re y arquitectura del emulador PS2"
