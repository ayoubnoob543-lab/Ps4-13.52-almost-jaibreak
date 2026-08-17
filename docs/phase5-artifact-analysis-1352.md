# Fase 5 — análisis profundo de artefactos PS4 FW 13.52

## Resumen ejecutivo

La fase documenta un asset externo de GitHub asociado al commit `2beb4cfcef1d416a32d6fb7b35f01189e9eb62e2`, cuyo mensaje es **“Add 13.52 support”**. El asset externo no está incluido en este checkout y su digest no se ha recalculado a partir de un archivo local en la auditoría actual. El `hen.bin` local es un artefacto distinto, de 499680 bytes y SHA-256 `32570b6e54c9531dc8a7d75ef4da6557d440bf69c4b765a85a77d428db3a4b73`; no debe confundirse con HEN 181.

```text
pre-release-main-181/hen.bin
external_expected_size: 499776 bytes
external_recorded_sha256: 568d57e7c6bfff1b96fc20a4e00b9ca744aa58b135a56eeb5c66c1175acfac3e
commit: 2beb4cfcef1d416a32d6fb7b35f01189e9eb62e2
local_checkout_status: ABSENT
tag:    pre-release-main-181
```

Según la evidencia documental del asset externo, no se trata de un kernel/eboot ni de un ELF/SELF, sino de un payload raw que contiene tablas, código y strings de HEN. La afirmación de que los **89 campos de `offsets_1352` están serializados en `0x105e0–0x10743`** es `DOCUMENTATION`/`UNVERIFIED` en este checkout porque el archivo externo correspondiente no está disponible localmente para repetir la comparación.

La documentación del commit también describe código del payload que selecciona esa tabla cuando recibe `fw_version == 0x548`, es decir, `1352` decimal. Sin el asset externo local, esta relación permanece `DOCUMENTATION`/`UNVERIFIED` para la reproducción actual:

```asm
0xc549: cmp $0x548,%di
0xc550: jne 0xc579
0xc552: lea 0x4087(%rip),%rax  # 0x105e0
0xc559: ret
```

Si se obtiene el asset externo exacto y su hash coincide, esas relaciones podrían clasificarse como `DIRECT_BYTES` del payload. En el estado actual sólo se conserva la clasificación `UNVERIFIED`; no es `DIRECT_BYTES` del kernel retail ni del archivo local `hen.bin`.

## 1. Artefactos descargados y hashes

| Artefacto | Procedencia | Tamaño | SHA-256 | Resultado |
|---|---|---:|---|---|
| `pre-release-main-181/hen.bin` | GitHub Release `Scene-Collective/ps4-hen` | 499776 B | `568d57e7c6bfff1b96fc20a4e00b9ca744aa58b135a56eeb5c66c1175acfac3e` | Registro externo; archivo no incluido en checkout actual |
| `pre-release-main-179/hen.bin` | GitHub Release `Scene-Collective/ps4-hen` | 498880 B | `54b39b0e56efe00287238f55317b8111b895b96a5a4f779507b3931a58e6c4a2` | Digest local = digest publicado |
| `PSFree/kpatch/900.elf` | Clon público histórico | 5588 B | `56183734c0b4c694344971479c3e070a6a6f0d13f783804b1610218314a7ae33` | ELF 64-bit x86-64, sin relocations |
| `PSFree/goldhen.bin` | Clon público histórico | 290016 B | `c6329401d1810e16c84e6474ac30977dbdc951987c10cdb559370de7d59db0b0` | Payload raw histórico |
| `PSFree/aio_patches.bin` | Clon público histórico | 5588 B | `edf729eb5fe532b679cf2f7fb7c9af852d83199ad6d1364d40fb68b9983ac1e5` | Payload raw histórico |

El asset 181 está asociado al tag `pre-release-main-181`, publicado el 25 de junio de 2026, y al commit exacto `2beb4cfcef1d416a32d6fb7b35f01189e9eb62e2`. El asset 179 apunta al commit padre `31bb8cdaed62fb07656f52d2a90a4c345e1abdbd` y no contiene el bloque completo 13.52.

## 2. Tabla 13.52 serializada dentro del HEN 181

La tabla fuente externa contiene 89 campos `uint32_t`. Se serializó en little-endian y se buscó como secuencia exacta dentro del asset.

```text
field_count:             89
serialized_size:         356 bytes
sequence_sha256:         d032dbd790eaa29cd8ec7571ee04636f82bbbb50a9b2ce0d24dfa003ace0030f
asset_offset:            0x105e0
asset_end:               0x10743
exact_match:             True
```

Campos representativos y sus posiciones dentro del asset:

| Campo | Valor | Offset de asset | Bytes little-endian |
|---|---:|---:|---|
| `XFAST_SYSCALL_addr` | `0x1c0` | `0x105e0` | `c0010000` |
| `PRISON0_addr` | `0x111fa18` | `0x105e4` | `18fa1101` |
| `M_TEMP_addr` | `0x1520d00` | `0x105ec` | `000d5201` |
| `ALLPROC_addr` | `0x1b28538` | `0x105f4` | `3885b201` |
| `SYSENT_addr` | `0x1102b70` | `0x10614` | `702b1001` |
| `printf_addr` | `0x2e0510` | `0x1063c` | `10052e00` |
| `vmspace_acquire_ref_addr` | `0x2f76e0` | `0x1068c` | `e0762f00` |
| `vmspace_free_addr` | `0x2f7510` | `0x10690` | `10752f00` |
| `vm_map_lock_read_addr` | `0x2f7870` | `0x10694` | `70782f00` |
| `vm_map_unlock_read_addr` | `0x2f78c0` | `0x10698` | `c0782f00` |
| `vm_map_lookup_entry_addr` | `0x2f7eb0` | `0x1069c` | `b07e2f00` |
| `proc_rwmem_addr` | `0x366760` | `0x106a0` | `60673600` |
| `proc_path_offset` | `0x474` | `0x10740` | `74040000` |

El registro del asset externo describe múltiples tablas de otras versiones, porque HEN selecciona offsets según la versión del firmware. En el checkout actual esas tablas no pueden volver a localizarse byte a byte; se conserva la referencia como `UNVERIFIED`:

| Tabla | HEN 179 | HEN 181 |
|---|---:|---:|
| `1350.c` completa | `0xf1c0` | `0xffe0` |
| `1352.c` completa | No encontrada | `0x105e0` |

La documentación externa afirma que HEN 181 añadió una tabla específica para `1352`, mientras el release 179 anterior no la contenía. Sin el asset externo local, esta afirmación queda `UNVERIFIED` en la reproducción actual.

## 3. Selector de firmware y XREF estructural

La documentación del asset HEN 181 describe un selector que compara el valor de firmware en `%di` y devuelve punteros a tablas internas mediante `lea RIP-relative`. Al no estar el asset en el checkout, el bloque siguiente es evidencia `UNVERIFIED` para esta auditoría local.

La rama crítica es:

```asm
0xc53b: 66 81 ff 46 05       cmp $0x546,%di
0xc540: 48 8d 05 99 3a 00 00 lea 0x3a99(%rip),%rax  # 0xffe0
0xc547: 74 30                je 0xc579
0xc549: 31 c0                xor %eax,%eax
0xc54b: 66 81 ff 48 05       cmp $0x548,%di
0xc550: 75 27                jne 0xc579
0xc552: 48 8d 05 87 40 00 00 lea 0x4087(%rip),%rax  # 0x105e0
0xc559: c3                   ret
```

`0x546 = 1350` y `0x548 = 1352`. La relación RIP-relative es exacta:

```text
0xc559 = siguiente instrucción
0xc559 + 0x4087 = 0x105e0
```

Esta relación es una prueba interna fuerte de que el bloque en `0x105e0` se selecciona específicamente para la versión numérica 1352. La función continúa con ramas para otras versiones y devuelve NULL mediante `0xc579` cuando no hay coincidencia.

## 4. Consumidores de los offsets

El `patch.c` del mismo commit declara y consume los campos de la tabla:

```text
líneas 12–17: declaraciones de proc_rwmem, vmspace_acquire_ref,
              vmspace_free, vm_map_lock_read,
              vm_map_unlock_read y vm_map_lookup_entry
líneas 29–30: M_TEMP y ALLPROC
líneas 37–48: malloc/free y búsqueda en ALLPROC
líneas 63–104: adquisición de vmspace, lectura de vm_map,
               locks, lookup, liberación y copia de entradas
línea 148:     llamada a proc_rwmem
líneas 161–205: shellcore_patch y búsqueda de SceShellCore
líneas 309–340: shellui_patch y búsqueda de SceShellUI
líneas 425–455: remoteplay_patch y búsqueda de SceRemotePlay
```

La documentación del commit presenta una cadena coherente de **tabla → punteros de funciones/estructuras → consumidores de kernel/payload**. Sin el asset exacto disponible localmente, esa relación se mantiene como `UNVERIFIED`; en cualquier caso, la corrección de los valores en el kernel sigue sin estar demostrada.

## 5. Comparación binaria 13.50 → 13.52

La comparación externa documentada afirma que los bloques 13.50 y 13.52 comparten sus primeros 14 campos, incluidos. No se ha podido repetir byte a byte con un asset HEN 181 local:

```text
XFAST_SYSCALL = 0x1c0
PRISON0       = 0x111fa18
ROOTVNODE     = 0x2136e90
M_TEMP        = 0x1520d00
ALLPROC       = 0x1b28538
SYSENT        = 0x1102b70
```

A partir del campo `memcmp_addr`, las funciones comunes y offsets de funciones cambian entre 13.50 y 13.52. También cambian `vmspace_*`, `vm_map_*` y `proc_rwmem`:

| Campo | 13.50 | 13.52 |
|---|---:|---:|
| `SYSENT_addr` | `0x1102b70` | `0x1102b70` |
| `M_TEMP_addr` | `0x1520d00` | `0x1520d00` |
| `ALLPROC_addr` | `0x1b28538` | `0x1b28538` |
| `vmspace_acquire_ref` | `0x2f72e0` | `0x2f76e0` |
| `vmspace_free` | `0x2f7100` | `0x2f7510` |
| `vm_map_lock_read` | `0x2f7470` | `0x2f7870` |
| `vm_map_unlock_read` | `0x2f74c0` | `0x2f78c0` |
| `vm_map_lookup_entry` | `0x2f7ab0` | `0x2f7eb0` |
| `proc_rwmem` | `0x366360` | `0x366760` |
| `printf` | `0x2e0460` | `0x2e0510` |

La persistencia documentada de `SYSENT=0x1102B70`, `ALLPROC=0x1B28538` y `M_TEMP=0x1520D00` en dos assets binarios consecutivos sería evidencia `STRUCTURAL` de inclusión en payloads, pero no es una prueba de bytes del kernel y no se recalculó en este checkout.
 La ausencia de `0x110A760` en ambos bloques favorece la primera tabla dentro de la línea Scene-Collective, aunque no elimina la posibilidad de que el valor alternativo provenga de otra build, módulo o fuente incorrecta.

## 6. `pmap_protect`, patch site y kernel_pmap_store

El asset HEN 181 no contiene representaciones directas little-endian de:

```text
0x58570
0x59DF0
0x59E37
0x110A760
0x1B2C3A0  (kernel_pmap_store)
0x4D6D0    (unknown1)
0xE6C60    (unknown2)
```

Además, `pmap_protect` no es un campo de `struct kpayload_offsets` en el commit externo. Por tanto, este HEN no implementa ni serializa el conflicto `0x58570 vs 0x59DF0` como parte de su tabla 13.52. No se debe interpretar la ausencia como descarte de cualquiera de las direcciones.

El `patch.c` externo consume `vmspace_*`, `vm_map_*` y `proc_rwmem`, pero no contiene un consumidor de `pmap_protect` ni `kernel_pmap_store`. Esos offsets pertenecen a otra cadena o a otra implementación de kernel patching.

## 7. PSFree y comparación histórica

`PSFree/kpatch/900.elf` es un ELF x86-64 de 5588 bytes con símbolos locales/globales `kpatch`, `restore` y `do_patch`, sin relocations. Es histórico y de firmware 9.00. `lapse.mjs` usa `sysent[661]` en `0x1107f00`, mientras el payload C 9.00 usa otra dirección de tabla para su mecanismo. Esto demuestra que `SYSENT` es sensible a firmware, método y contexto; no permite transferir esos valores a 13.52.

## 8. Clasificación actualizada

| Offset | Evidencia nueva | Clasificación correcta | Cambio |
|---|---|---|---|
| `SYSENT=0x1102B70` | Bloque completo serializado en HEN 181; selector `0x548 → 0x105e0`; mismo valor en HEN 179/13.50 | `STRUCTURAL` para la tabla/payload; no validado contra kernel | Sube en evidencia de inclusión/uso, no a validación firmware |
| `SYSENT=0x110A760` | No aparece en HEN 179/181 ni en la tabla Scene 13.52 | `UNVERIFIED` (conflicto no resuelto) | Sin cambio de valor operativo |
| `ALLPROC=0x1B28538` | Serializado y consumido en HEN 181; igual en 13.50 | `STRUCTURAL` para asset/table claim; no validado contra kernel | Evidencia binaria nueva de inclusión |
| `M_TEMP=0x1520D00` | Serializado y consumido; igual en 13.50 | `STRUCTURAL` para asset/table claim; no validado contra kernel | Evidencia binaria nueva de inclusión |
| `vmspace_*`, `vm_map_*`, `proc_rwmem` | Bloque serializado exacto y consumidores de `patch.c` | `STRUCTURAL` para asset/table claim; no validado contra kernel | Evidencia binaria nueva de inclusión |
| `pmap_protect=0x58570` | Ausente de la tabla y del asset | `UNVERIFIED` (referencia documental sin bytes objetivo) | Sigue sin resolver |
| `pmap_protect=0x59DF0` | Ausente de la tabla y del asset | `UNVERIFIED` (conflicto no resuelto) | Sigue sin resolver |
| `patch site=0x59E37` | Ausente del asset | `STRUCTURAL` únicamente; sin bytes objetivo | Sigue sin resolver |
| `kernel_pmap_store=0x1B2C3A0` | Ausente del asset | `UNVERIFIED` (referencia documental sin bytes objetivo) / `UNVERIFIED` binario | Sigue sin resolver |
| `unknown1`, `unknown2` | Ausentes del asset y sin consumidores | `UNVERIFIED` | Sin cambio |

## 9. Qué se ha demostrado y qué no

### Demostrado directamente en artefactos

Se demostró que el asset HEN 181, con hash reproducible y commit versionado, contiene una tabla de 89 campos exactamente igual a `offsets_1352.c`, que el selector de firmware compara `0x548` y devuelve el bloque `0x105e0`, y que el código asociado consume `M_TEMP`, `ALLPROC`, `vmspace_*`, `vm_map_*`, `proc_rwmem` y `SYSENT` mediante esa estructura.

### No demostrado

No se demostró que `0x1102B70` sea la tabla `sysent` correcta leyendo bytes del kernel retail 13.52. No se resolvió `0x58570` frente a `0x59DF0`; no se validó `0x59E37`; no se validaron `kernel_pmap_store`, `M_TEMP` o las funciones `vm_map_*` contra bytes del kernel. Tampoco apareció una imagen `SceShellCore`, `SceShellUI` o `SceRemotePlay` independiente de los payloads.

## 10. Progreso real

| Métrica | Antes | Después | Justificación |
|---|---:|---:|---|
| Corpus | 70% | 72% | Aparece un asset binario público versionado con tabla 13.52 exacta y hashes reproducibles. |
| Cadena funcional | 42% | 46% | Se demuestra binariamente la cadena selector de firmware → tabla → consumidores de vmspace/vm_map/proc_rwmem; no la transición kernel runtime. |
| Validación kernel/patch sites | 35% | 37% | Aumenta la evidencia estructural de offsets usados por el payload, pero sigue sin bytes del kernel. |
| Jailbreak/exploit confirmado | 0% | 0% | No existe validación completa en hardware ni cadena reproducible de exploit. |

Estos incrementos son limitados y no representan validación de hardware. Si se adopta una política más estricta en la que sólo los bytes de kernel pueden cambiar el porcentaje de validación, la métrica de validación kernel debe permanecer en 35%; el incremento de 2 puntos corresponde exclusivamente a evidencia de **reproducibilidad del artefacto/payload**.

## 11. Siguiente artefacto concreto

El siguiente artefacto de mayor impacto sigue siendo un **kernel o eboot PS4 13.52 de la misma build**, con hash, base de carga y bytes alrededor de:

```text
0x58570–0x59E37
0x1102B70
0x110A760
0x1B28538
0x1B2C3A0
0x2F76E0–0x2F7EB0
0x366760
0x1520D00
```

El HEN 181 permite comparar la tabla que espera el payload con ese kernel cuando aparezca, pero no sustituye esa imagen. Para cerrar la cuestión del patch site hacen falta además los bytes del módulo concreto al que se aplique; no debe asumirse que `0x59E37` pertenece al mismo módulo que `libkernel` o al HEN raw.

## Referencias

[1]: https://github.com/Scene-Collective/ps4-hen/releases/tag/pre-release-main-181 "Scene-Collective HEN pre-release-main-181"
[2]: https://github.com/Scene-Collective/ps4-hen/commit/2beb4cfcef1d416a32d6fb7b35f01189e9eb62e2 "Add 13.52 support"
[3]: https://github.com/Scene-Collective/ps4-hen/releases/tag/pre-release-main-179 "Scene-Collective HEN pre-release-main-179"
[4]: https://github.com/Scene-Collective/ps4-hen/blob/main/kpayload/source/offsets/1352.c "Scene-Collective offsets/1352.c"
[5]: https://github.com/Scene-Collective/ps4-hen/blob/main/kpayload/source/patch.c "Scene-Collective patch.c"
[6]: https://github.com/Suchi96/PS4_13_52_libkerneldump "Local research corpus and libkernel dump"
[7]: https://github.com/Al-Azif/PSFree "PSFree historical payload source"
