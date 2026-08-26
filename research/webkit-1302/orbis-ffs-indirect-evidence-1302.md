# Evidencia indirecta de Celsius/FFS en artefactos PS4 13.02

**Fecha de corte:** 26 de agosto de 2026.
**Alcance:** análisis documental y estático exclusivamente. No se ejecutaron exploits ni corrupción de memoria.

## Conclusión

La nueva búsqueda encuentra **más evidencia de infraestructura de kernel y de procedencia de offsets**, pero no encuentra una correspondencia verificable con `ffs_mountfs()`, `ffs_reload()`, `ffs_vget()` o `ffs_alloc()` en Orbis 13.02. Las coincidencias FFS directas se concentran en dos clases: código/documentación FreeBSD upstream y documentación de Celsius en el repositorio de investigación `adri22235/ps4-suid-scanner`. No aparece un cuerpo de función Orbis, un string de kernel Orbis, pseudocódigo, cross-reference ni offset atribuido explícitamente a una función FFS.

La evidencia indirecta más fuerte es que los artefactos 13.02 exponen funciones generales de kernel relacionadas con VFS/memoria y un parche llamado `patch_mount`, y que el SDK incluye headers FreeBSD UFS/FFS. También apareció un segundo repositorio relevante, OSM-Made/PS4-Kernel-SDK, cuyo YAML `firmware-1302.yaml` reproduce prácticamente toda la tabla de Fusion. Eso demuestra una línea pública de tablas de símbolos VFS y mecanismos de montaje/payload, pero no una nueva fuente binaria. **No demuestra que `patch_mount` sea `ffs_mountfs`, ni que Orbis conserve el código vulnerable, ni que Celsius proporcione R/W.**

El repositorio OSM-Made es importante para la procedencia, pero no cambia la categoría probatoria: su commit inicial de 13.02 (`093808e`, 22 de enero de 2026) llega después del commit/PR 13.02 de Fusion (20 de enero de 2026), añade únicamente `offsets/firmware-1302.yaml` y no menciona FFS, Celsius, bollars ni un dump. La comparación reproducible encontró 163 nombres comunes, 162 offsets idénticos y una única diferencia (`trap_fatalHook`: `0` frente a `0x0014AA90`). Los objetivos `patch_mount`, `M_MOUNT`, `getnewvnode`, `vn_fullpath`, `kern_open`, `malloc`, `free`, `kmem_alloc` y `kmem_free` son idénticos. Esto respalda **DERIVED/same-lineage**, no independencia.

## 1. `Shared/Offsets-1302.h` de AetherPS/Fusion

Fuente primaria del archivo: [`AetherPS/Fusion/Shared/Offsets-1302.h`](https://github.com/AetherPS/Fusion/blob/1d7c0314ade52858496195e53bcc85de274def51/Shared/Offsets-1302.h), dentro del commit [`1d7c0314ade52858496195e53bcc85de274def51`](https://github.com/AetherPS/Fusion/commit/1d7c0314ade52858496195e53bcc85de274def51). El PR asociado es [`#13`](https://github.com/AetherPS/Fusion/pull/13), titulado “13.02 Kernel offsets”, creado por ArabPixel y fusionado por OSM-Made.

El archivo tiene 203 líneas y define `InitKernel1302(uint64_t kernelBase, KernelAddrs* addrs)`. Todas las direcciones son expresiones `kernelBase + constante`; no hay bytes de instrucciones ni formato de imagen. La extracción local del archivo tiene SHA-256 `34a206ffa48a406f6d15879b40e941de5e9d0db094bfd2d0932a6cf58961066a` para la copia normalizada utilizada en el expediente local; el identificador de contenido Git queda determinado por el commit y blob de GitHub, no por ese SHA-256 local.

### Offsets extraídos por grupo

| Grupo | Símbolos disponibles |
|---|---|
| Util/VFS general | `Xfast_syscall=0x1C0`, `sysvec=0x1A7CFE8`, `prison0=0x111FA18`, `rootvnode=0x2136E90`, `copyin=0x2BD6E0`, `copyout=0x2BD5F0`, `copyinstr=0x2BDB90`, `kern_open=0x3435E0`, `kern_mkdir=0x348720`, `kernel_map=0x22D1D60`, `kmem_alloc=0x465A50`, `kmem_free=0x465C20`, `vn_fullpath=0x308CE0`, `getnewvnode=0x36E2F0` |
| VFS/memoria auxiliar | `M_TEMP=0x1520D00`, `M_MOUNT=0x1A40250`, `malloc=0x9520`, `free=0x96E0`, `memcpy=0x2BD4D0`, `memset=0x1FA1B0` |
| Procesos | `allproc=0x1B28538`, `allproc_lock=0x1B284D8`, `pfind=0xEA40`, `proc_rwmem=0x366010`, `create_thread=0x4C6C0` |
| Memoria virtual | `vm_map_lock=0x2F6FD0`, `vm_map_unlock=0x2F7040`, `vm_map_findspace=0x2FA1E0`, `vm_map_delete=0x2F9C20`, `vm_map_insert=0x2F8320`, `vm_map_protect=0x2FBF80` |
| Sincronización | `mtx_lock_flags=0x378330`, `mtx_unlock_flags=0x3785E0`, `sx_xlock=0xA3840`, `sx_xunlock=0xA3A00`, `sx_slock=0xA3660`, `sx_sunlock=0xA3950` |
| Driver/DevFS | `make_dev_p=0x38A980`, `destroy_dev=0x38AEA0`, `devfs_rule_applyde_recursive=0x2DEB70` |
| NVS | `icc_nvs_read=0xA5BD0`, `icc_nvs_write=0xA5A10` |
| Sysctl | `sysctl__children=0x22CC600`, `sysctl_ctx_init=0x3F95C0`, `sysctl_ctx_free=0x3F95E0`, `sysctl_add_oid=0x3F9C20`, `sysctl_handle_int=0x3FA0A0`, `sysctl_handle_string=0x3FA340` |
| SBL/FSelf | funciones `sceSblAuthMgr*`, `sbl_drv_msg_mtx`, `gpu_va_page_list`, mailbox y hooks SBL |
| PFS/crypto | `sbl_pfs_sx=0x265C080`, `sceSblPfsSetKeys=0x626770`, funciones Keymgr/PFS, AES, RSA y HMAC |
| TTY | `cloneuio=0x36CCF0`, `console_write=0x46FA00`, `deci_tty_write=0x48C550`, `M_IOV=0x1A4A230`, `console_cdev=0x22D1F30` |
| Parches | `patch_memcpy=0x2BD4FD`, parches `copyin/copyout/copyinstr`, `patch_mount=0x1512A7`, `patch_mprotect=0x2FC15C`, `patch_fuseLoader=0x4953FE`, parches de VM/panic y depuración |

### Interpretación de `patch_mount`

`patch_mount = kernelBase + 0x001512A7` es el único nombre del header que contiene `mount`. Su contexto es el grupo genérico “Kernel Patches” y no aporta nombre de función, bytes, comentario, string ni referencia a FFS/UFS. No se puede convertir en `ffs_mountfs()` por proximidad semántica. Se clasifica como **SOURCE_ONLY** para la existencia de un punto de parche llamado `patch_mount` y **INVALID** como identificación de Celsius/FFS.

`M_MOUNT`, `getnewvnode`, `vn_fullpath`, `kern_open` y `kern_mkdir` son indicios razonables de componentes VFS, pero son símbolos generales. No identifican una rutina FFS concreta. Clasificación: **CORROBORATED** como infraestructura VFS-like publicada; **HYPOTHESIS** para cualquier relación con Celsius.

## 2. Procedencia cruzada de las tablas 13.02

| Artefacto | Fecha/commit | Contenido real | Relación con `patch_mount` | Clasificación |
|---|---|---|---|---|
| Fusion `Shared/Offsets-1302.h` | 20-ene-2026, `1d7c031` | Header C generado/manual con asignaciones `kernelBase + offset` | Define `patch_mount=0x001512A7` | `SOURCE_ONLY` para offset |
| OSM `offsets/firmware-1302.yaml` | 22-ene-2026, `093808e` | YAML de offsets, 853 líneas nuevas | Reproduce el mismo offset y casi toda la tabla | `DERIVED` / `SOURCE_ONLY` |
| kpayload 13.02 | árbol de firmware del payload | Struct de offsets para R/W, PFS, VM y SceShellCore | No contiene `patch_mount` | `CORROBORATED` para sus propios símbolos; sin FFS |
| SDK PR #6 | 5-oct-2025, `66d5a096` | Cambios de runtime en `crt/kernel.c` | No añade `patch_mount` ni FFS | `CORROBORATED` como soporte 13.02; `INVALID` para Celsius |

La evidencia de OSM no es un dump ni una fuente primaria del kernel. El README indica como guía que los offsets deberían actualizarse desde un dump conocido y probarse en hardware, pero esa recomendación no prueba el origen concreto de `firmware-1302.yaml`. No hay comentario, hash de kernel, build number ni artefacto adjunto que permita auditar la medición.

## 3. Búsqueda de referencias FFS/UFS

Se buscaron `ffs_mountfs`, `ffs_reload`, `ffs_vget`, `ffs_alloc`, `mountfs`, `fs_ncg`, `fs_cssize`, `fs_contigsumsize`, `fs_bsize`, `fs_fsize`, `UFS`, `FFS`, `superblock`, además de `Celsius`, `bollars`, `Dr.Yenyen`, `Pharaoh2k` y `13.04`.

| Ubicación | Coincidencia | Naturaleza | Clasificación |
|---|---|---|---|
| `research/webkit-1302/upstream/freebsd-9.1-ffs_vfsops.c` | cuerpos y declaraciones de `ffs_mountfs()`/`ffs_reload()` | Código FreeBSD histórico recopilado como referencia | **VERIFIED** para FreeBSD; **INVALID** como Orbis |
| `research/webkit-1302/upstream/freebsd-9.1-ffs-comparison.txt` | cálculos con `fs_cssize`, `fs_ncg`, `fs_contigsumsize`, `fs_bsize`, `fs_fsize` | Comparación/documentación upstream | **VERIFIED** para la fuente comparada |
| `cve_analysis.md` y `adri-cve_analysis.md` | explicación de Celsius y pseudocódigo | Documentación secundaria del repositorio de scanner | **SOURCE_ONLY** |
| `jordy_stage2.js` | comentarios “mount → triggers ffs_mountfs → Celsius” | Comentario de una cadena no completada | **HYPOTHESIS/UNVERIFIED** |
| `webkit_gadgets_1304.js` | comentario sobre string `ffs_mountfs` y supuesto offset | Afirmación sin binario ni hash adjunto | **SOURCE_ONLY**, no corroborada |
| `AetherPS/Fusion/Shared/Offsets-1302.h` | `M_MOUNT`, `getnewvnode`, `patch_mount` | Tabla de offsets, sin FFS explícito | **CORROBORATED** como offsets; **INVALID** como identificación FFS |
| SLOPOS `ps4/1302.h` | offsets generales kexec/jailbreak | Header de offsets | **DERIVED/SOURCE_ONLY** |
| `ps4-linux-loader` | headers UFS/FFS FreeBSD y kexec | Código/headers de SDK y loader | **SOURCE_ONLY** como antecedente; no Orbis |
| `ps4-payload-dev/sdk` | `include/freebsd-9.3/ufs/ffs/*` y `crt/kernel.c` | Headers FreeBSD y runtime de payload | **SOURCE_ONLY**; no Orbis |
| `Al-Azif/vue-after-free/src/download0/kernel.ts` | exploit WebKit/userland | Código de entrada userland | **INVALID** para FFS kernel |

No aparecieron strings extraídas de un binario de kernel Orbis. Las únicas coincidencias de campos de superbloque (`fs_*`) provienen del código FreeBSD y de documentación que lo reproduce.

## 4. Código FreeBSD frente a los artefactos 13.02

El código FreeBSD upstream sí contiene la ruta histórica en la que `fs_cssize`, `fs_contigsumsize` y `fs_ncg` participan en cálculos de tamaño y asignación, seguida por bucles que consumen `fs_ncg`. Esa relación es **VERIFIED para el código FreeBSD de referencia**.

Los artefactos 13.02 no contienen `struct fs` de Orbis asociada a una función, no muestran los tipos usados por Sony, no contienen instrucciones equivalentes y no incluyen un diff de 13.02→13.50. Por tanto, no hay base para afirmar que la implementación Orbis tenga el mismo overflow ni que el bug sea explotable.

## 5. Cadena de procedencia de Celsius

La cadena pública reconstruible es la siguiente:

> **Celsius (atribución a bollars) → documentación de `adri22235/ps4-suid-scanner` → afirmación “works up to 13.04 / patched in 13.50” → tablas 13.04 basadas en 13.02 y atribuidas a verificación de Pharaoh2k → headers de offsets de Fusion/SLOPOS/SDK.**

Esta cadena tiene una ruptura crítica: entre la documentación de Celsius y los headers 13.02/13.04 no existe un artefacto que contenga la función FFS, su dirección, sus bytes o una prueba de ejecución. La presencia de `patch_mount` en Fusion tampoco repara esa ruptura.

El PR de SDK que añadió soporte 13.02, [`66d5a096`](https://github.com/ps4-payload-dev/sdk/commit/66d5a096e1c301c17b826f0759e6b843b881bcd2), sólo modifica `crt/kernel.c` para añadir el caso de firmware y tres direcciones generales: base inferida desde `LSTAR`, `targetid`, `copyin` y `copyout`. No añade FFS, Celsius, un dump ni pseudocódigo. Clasificación: **CORROBORATED** como cambio de soporte del SDK; **INVALID** como evidencia de Celsius.

## 6. ¿Puede asociarse algún offset a FFS?

No de forma razonable y verificable. La asociación más cercana sería:

| Offset/nombre | Por qué podría parecer relevante | Por qué no identifica FFS | Clasificación |
|---|---|---|---|
| `patch_mount = 0x1512A7` | Nombre `mount` y grupo de parches | Sin bytes, firma, referencia o nombre `ffs_*`; podría ser otra ruta de montaje | **HYPOTHESIS**, no evidencia FFS |
| `M_MOUNT = 0x1A40250` | Zona/estructura de asignación relacionada con mounts | Es un símbolo de allocator/zone, no `ffs_mountfs` | **CORROBORATED** como símbolo publicado; **INVALID** como Celsius |
| `getnewvnode = 0x36E2F0` | VFS/vnode | Función general de vnode; no específica de FFS | **CORROBORATED**, no FFS |
| `vn_fullpath = 0x308CE0` | VFS pathname | No participa necesariamente en mount de FFS | **CORROBORATED**, no FFS |
| `kern_open/kern_mkdir` | Operaciones de filesystem | No son funciones UFS específicas | **CORROBORATED**, no FFS |
| `malloc/free` | Primitivas que Celsius necesitaría | Presentes en cualquier kernel y no localizan la función | **INVALID** como evidencia de vulnerabilidad |

## 7. Respuestas finales

**¿Qué evidencia nueva aparece?** Aparece un historial más claro de soporte 13.02 en Fusion y SDK, y se confirma que los artefactos exponen infraestructura VFS genérica (`M_MOUNT`, `getnewvnode`, `vn_fullpath`, `patch_mount`) junto con primitivas de memoria. No aparece evidencia nueva directa de Celsius.

**¿Qué funciones FFS podemos identificar indirectamente?** Ninguna función FFS de Orbis. Sólo se pueden identificar las funciones FreeBSD upstream y las referencias documentales que las nombran.

**¿Algún offset puede asociarse razonablemente a FFS?** No. `patch_mount` es un candidato nominal débil, pero no puede etiquetarse como `ffs_mountfs`; todos los demás son símbolos VFS o memoria genéricos.

**¿Aparece evidencia adicional de Celsius en 13.02?** Sólo evidencia documental derivada: la documentación afirma cobertura hasta 13.04 y otras tablas reutilizan offsets 13.02. No hay código, bytes, dirección de `ffs_mountfs`, prueba de hardware ni prueba de kernel R/W. La clasificación permanece **SOURCE_ONLY / HYPOTHESIS / UNVERIFIED**.

**¿Cuál es el siguiente paso más informativo?** Obtener una tabla de símbolos o disassembly parcial de un kernel Orbis 13.02 legítimamente disponible, aunque sólo contenga una ventana alrededor de `patch_mount`, `M_MOUNT` o cualquier string `ffs_*`. Si eso no aparece, la segunda mejor pieza sería un commit o log primario de bollars que publique el offset, la firma de la función y el artefacto UFS usado. Sin una de esas piezas, seguir comparando offsets no resolverá la cuestión.

## Referencias

[1]: https://github.com/AetherPS/Fusion/blob/1d7c0314ade52858496195e53bcc85de274def51/Shared/Offsets-1302.h "Fusion Shared/Offsets-1302.h"
[2]: https://github.com/AetherPS/Fusion/commit/1d7c0314ade52858496195e53bcc85de274def51 "Fusion commit 1d7c031"
[3]: https://github.com/AetherPS/Fusion/pull/13 "Fusion PR #13"
[4]: https://github.com/alferdoss/SLOPOS-offsets/blob/master/ps4/1302.h "SLOPOS 13.02 header"
[5]: https://github.com/ps4-payload-dev/sdk/commit/66d5a096e1c301c17b826f0759e6b843b881bcd2 "SDK commit adding 13.02 support"
[6]: https://github.com/ps4-linux/ps4-linux-loader "PS4 Linux loader"
[7]: https://github.com/ps4-payload-dev/sdk "PS4 payload SDK"
[8]: https://github.com/Al-Azif/vue-after-free "Vue After Free repository"
[9]: https://github.com/adri22235/ps4-suid-scanner "PS4 SUID scanner and Celsius documentation"
[10]: https://github.com/Al-Azif/ps4-re-utilities "PS4 reverse-engineering utilities"
[11]: https://github.com/Al-Azif/dumper-testing "Dumper testing repository"
[12]: https://www.psdevwiki.com/ps4/Kernel "PS4 Developer Wiki: Kernel"
[13]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer Wiki: Vulnerabilities"
[14]: https://github.com/TheOfficialFloW/PPPwn "PPPwn"
[15]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain "OpenOrbis PS4 Toolchain"
[16]: https://github.com/OpenOrbis/mira-project "OpenOrbis Mira project"

## 8. Actualización de procedencia: ArabPixel → Fusion → OSM

La auditoría histórica localiza una primera aparición pública concreta de la tabla completa 13.02 en el commit de ArabPixel [`77a16b7f236df46f14bb2c744a24540e57245214`](https://github.com/ArabPixel/Fusion/commit/77a16b7f236df46f14bb2c744a24540e57245214), fechado el 18 de enero de 2026. El commit añade únicamente `Shared/Offsets-1302.h` (203 líneas) y modifica `Shared/Offsets.h`; no añade dump, ELF, kernel hash, proyecto IDA/Ghidra, strings FFS, comentarios sobre Celsius ni herramienta de extracción. Clasificación: **VERIFIED** como primera fuente pública observada del header; **INVALID** como dump o evidencia de FFS.

El PR [`AetherPS/Fusion#13`](https://github.com/AetherPS/Fusion/pull/13) fue abierto por ArabPixel el mismo día y describe el cambio como “only kernel offsets and the implementation in Offsets.h :)”. Su único comentario público conservado no identifica un dump ni un método de obtención. La copia fusionada en `AetherPS/Fusion` (`1d7c031`) es byte a byte idéntica al archivo de ArabPixel; ambas descargas tienen SHA-256 `7b034c3b933ddbee560ae9dc18cf02cbcd7aa4d8cef6e5ab48154cd972268f7d`. Clasificación: **VERIFIED** como copia, **DERIVED** como procedencia, no independiente.

El commit inicial de OSM [`093808ee1563dfdb735b69ba2bfc925a9439ff54`](https://github.com/OSM-Made/PS4-Kernel-SDK/commit/093808ee1563dfdb735b69ba2bfc925a9439ff54), del 21 de enero de 2026, añade sólo `offsets/firmware-1302.yaml` con 853 líneas. No menciona la fuente, un dump, LSTAR, IDA/Ghidra, una build de Orbis o pruebas en hardware. El YAML tiene SHA-256 `2774f464e642b2419ddb7939707f262c87b268a5794c291d79a2edcc9eefe769`. Su relación pública con Fusion es **DERIVED/same-lineage**: 162 de 163 offsets comunes coinciden; la excepción comparada es `trap_fatalHook` (`0` frente a `0x0014AA90`).

El submódulo [`AetherPS/FusionShared`](https://github.com/AetherPS/FusionShared) fue creado el 9 de enero de 2025 y su historial público contiene tablas 9.00, 11.00 y 12.02, pero ninguna 13.02 o 13.04. Sus commits de actualización de offsets (`6e351d8`, `0fc5b2b`, `f233cd0`) no contienen `patch_mount` 13.02 ni FFS. Por tanto, no es la fuente anterior identificable de la tabla 13.02.

## 9. Evidencia histórica relacionada con mount

El commit [`a486e87`](https://github.com/cualquiercosa327/Fusion/commit/a486e87fb6026d8b64178ee27f00a3558fc9b2ac), “Add fuse root mount”, modifica sólo `Kernel/source/Patches.cpp` y contiene parches antiguos de Fusion para `SOFTWARE_VERSION_900` y `SOFTWARE_VERSION_1100`. Los comentarios distinguen “Enable mount for unprivileged user” y “Mount Fuse filesystem as root”; el código parchea comprobaciones de privilegios y una ruta FUSE. No contiene `ffs_mountfs`, UFS, `struct fs` ni Celsius y no es evidencia 13.02. Clasificación: **VERIFIED** como código histórico FUSE/privilegios; **INVALID** como identificación de FFS.

La búsqueda `git log -S` en los historiales de AetherPS/Fusion, ArabPixel/Fusion, RetroGenPS/Fusion y cualquiercosa327/Fusion muestra que `patch_mount` y el valor `0x001512A7` aparecen por primera vez en la línea del commit de ArabPixel `77a16b7`/PR #13. No se encontró una aparición anterior pública en esos historiales. Esto fija el primer origen público observable, pero no demuestra que ArabPixel sea la fuente primaria material de los offsets: el origen de sus mediciones sigue sin estar documentado.

## 10. Grafo de procedencia actualizado

```text
[Origen material no identificado: posible análisis privado o fuente no publicada]
                  |
                  v
ArabPixel/Fusion 77a16b7 (18-ene-2026)
                  |
                  v
AetherPS/Fusion PR #13 / 1d7c031 (20-ene-2026; copia byte-identica)
                  |
                  v
OSM-Made/PS4-Kernel-SDK 093808e (21-ene-2026; YAML transformado)
                  |
          +-------+--------+
          v                v
   OSM forks/SDKs      tablas derivadas de escena
```

El README de OSM que recomienda partir de un “known-good kernel dump” es **SOURCE_ONLY** como orientación general. No identifica el dump utilizado para `firmware-1302.yaml`, no aporta hash ni enlaza un artefacto acompañante. Por tanto, el “dump conocido” no ha sido localizado y no puede darse por existente para esta tabla.

## 11. Respuesta a los objetivos de procedencia

La primera fuente pública observable de los offsets 13.02 es el commit de ArabPixel en Fusion, no OSM. El primer artefacto público acompañante es un header C de offsets; no aparece un dump, ELF, disassembly o pseudocódigo asociado. `patch_mount` ya está presente en ese header, pero sólo como asignación `kernelBase + 0x001512A7`, sin bytes o cross-reference. No aparece evidencia adicional de que corresponda a UFS/FFS ni una ruta reproducible desde esos offsets hasta Celsius.

La conclusión probatoria permanece: **VERIFIED** para la existencia y propagación pública de la tabla; **DERIVED** para OSM respecto de Fusion; **SOURCE_ONLY** para cualquier afirmación sobre un dump de origen; **HYPOTHESIS/UNVERIFIED** para `patch_mount → ffs_mountfs → Celsius`; e **INVALID** para tratar la tabla como evidencia de una vulnerabilidad funcional.

## Referencias adicionales

[16]: https://github.com/ArabPixel/Fusion/commit/77a16b7f236df46f14bb2c744a24540e57245214 "ArabPixel: first observed public 13.02 offsets commit"
[17]: https://github.com/AetherPS/Fusion/pull/13 "Fusion PR #13"
[18]: https://github.com/OSM-Made/PS4-Kernel-SDK/commit/093808ee1563dfdb735b69ba2bfc925a9439ff54 "OSM initial 13.02 YAML commit"
[19]: https://github.com/AetherPS/FusionShared "FusionShared repository"
[20]: https://github.com/cualquiercosa327/Fusion/commit/a486e87fb6026d8b64178ee27f00a3558fc9b2ac "Historical Fuse root mount commit"

## 12. Hallazgo nuevo: el SDK de ArabPixel ya tenía infraestructura de kdump antes de Fusion

La auditoría de `ArabPixel/sdk` descubre un antecedente técnicamente relevante, aunque insuficiente para identificar el origen material de la tabla. El repositorio es un fork de [`ps4-payload-dev/sdk`](https://github.com/ps4-payload-dev/sdk). Antes de la publicación de `Shared/Offsets-1302.h`, su historial ya contenía un sample `samples/kdump/main.c`, una función `kernel_find_pattern()` y una función `kernel_get_image_size()`.

El commit [`4323a2d`](https://github.com/ArabPixel/sdk/commit/4323a2d9d8e2646e7488c5c5147709b5824eef7d), del 10 de julio de 2025, añade búsqueda de patrones en memoria del kernel y cálculo del tamaño de la imagen. El sample `kdump` copia rangos desde `KERNEL_ADDRESS_IMAGE_BASE` mediante `kernel_copyout()` y los escribe por stdout. El commit [`7ca86e9`](https://github.com/ArabPixel/sdk/commit/7ca86e9b871b60311c2ce87f4a6be06478751026), del 30 de agosto de 2025, corrige el sample para usar `KERNEL_IMAGE_SIZE`. El commit [`546bb1c`](https://github.com/ArabPixel/sdk/commit/546bb1c513a75885def8ba2598b58fb69a44226b), del 5 de octubre de 2025, añade el caso `0x13020000` a `crt/kernel.c`, con `KERNEL_ADDRESS_IMAGE_BASE = lstar - 0x1C0`, `KERNEL_ADDRESS_COPYIN = base + 0x2BD6E0` y `KERNEL_ADDRESS_COPYOUT = base + 0x2BD5F0`. Fue authored por Al-Azif y committed por John Törnblom.

Esto establece una **capacidad pública de obtener un kdump del kernel** si el entorno ya dispone de una primitiva funcional de kernel R/W. No demuestra que ArabPixel utilizase el sample para generar los offsets de Fusion. El commit del 13.02 sólo añade cuatro constantes de inicialización y no contiene la tabla completa, `patch_mount`, `M_MOUNT`, funciones FFS, hashes de kernel, archivos dump ni logs de ejecución.

| Hallazgo | Clasificación | Alcance real |
|---|---|---|
| `kernel_find_pattern()` en SDK | `VERIFIED` | Puede escanear un rango de memoria accesible; no incluye patrones FFS ni offsets 13.02 completos |
| `samples/kdump/main.c` | `VERIFIED` | Puede volcar la imagen cuyo tamaño se calcula; no es un dump publicado |
| Caso de firmware `0x13020000` | `VERIFIED` | Permite inicializar base/copyin/copyout para 13.02; no demuestra origen de la tabla Fusion |
| SDK fork de ArabPixel antes de Fusion | `VERIFIED` | Proximidad técnica y temporal, no prueba causalidad |
| ArabPixel usó `kdump` para obtener `77a16b7` | `HYPOTHESIS` | No hay commit, log, hash ni archivo que lo confirme |
| `kdump` contiene o localiza `ffs_mountfs()` | `INVALID` | El sample sólo copia memoria; no aporta una dirección FFS concreta |

La hipótesis material mejorada es que los offsets de ArabPixel pudieron haberse obtenido mediante un flujo privado o local basado en kernel R/W, `kernel_copyout`, `kdump` y/o pattern scanning, antes de ser publicados como header. La evidencia pública sólo demuestra que esas herramientas estaban disponibles, no que fueran utilizadas para esos valores ni que el dump resultante exista.

## 13. Actualización sobre Celsius y `patch_mount`

El nuevo linaje del SDK no introduce ninguna conexión con Celsius. Las únicas constantes 13.02 que expone son base derivada de `LSTAR`, `targetid`, `copyin` y `copyout`; no aparece `patch_mount` ni ninguna rutina `ffs_*`. El sample podría producir un archivo de bytes si se ejecutara en un sistema con R/W, pero no hay un archivo resultante, hash, salida, patrón de `ffs_mountfs()` o análisis de IDA/Ghidra publicado.

En consecuencia, `patch_mount = 0x001512A7` permanece **SOURCE_ONLY** como offset etiquetado y **HYPOTHESIS/UNVERIFIED** respecto de `ffs_mountfs()`. La disponibilidad previa de `kdump` eleva la plausibilidad de un origen privado basado en un volcado, pero no eleva la identificación de Celsius a `CORROBORATED`.

## Referencias del SDK de kdump

[21]: https://github.com/ArabPixel/sdk "ArabPixel SDK fork"
[22]: https://github.com/ArabPixel/sdk/commit/4323a2d9d8e2646e7488c5c5147709b5824eef7d "kernel_find_pattern and kernel_get_image_size"
[23]: https://github.com/ArabPixel/sdk/commit/7ca86e9b871b60311c2ce87f4a6be06478751026 "kdump sample fix"
[24]: https://github.com/ArabPixel/sdk/commit/546bb1c513a75885def8ba2598b58fb69a44226b "ArabPixel SDK: add 13.02 support"
[25]: https://github.com/ps4-payload-dev/sdk "Upstream payload SDK"

## 14. Pista material anterior a Fusion: ArabPixel/sdk y kdump

La revisión ampliada encontró que `ArabPixel/sdk` contiene una infraestructura pública de extracción de memoria anterior a la tabla `Shared/Offsets-1302.h`. El fork procede de `ps4-payload-dev/sdk`. El 10-jul-2025, `4323a2d` añadió `kernel_find_pattern()` y `kernel_get_image_size()`; el 30-ago-2025, `7ca86e9` corrigió `samples/kdump/main.c`; el 5-oct-2025, `546bb1c` añadió el caso `0x13020000` en `crt/kernel.c`. En este último commit, Al-Azif fue el autor y John Törnblom el committer.

El caso 13.02 configura `KERNEL_ADDRESS_IMAGE_BASE` desde `LSTAR` y fija `copyin`, `copyout` y `targetid`; el sample `kdump` copia `KERNEL_IMAGE_SIZE` desde `KERNEL_ADDRESS_IMAGE_BASE` con `kernel_copyout()` y lo emite por stdout. Esto demuestra una ruta pública de tooling que podría producir un dump si ya existe una primitive de kernel R/W. No se encontró el output de esa herramienta, un hash de dump, un patrón FFS, un registro de ejecución ni una declaración de que ArabPixel la usara para producir la tabla de Fusion. Clasificación: tooling `VERIFIED`; uso causal para los offsets `HYPOTHESIS`.

La coincidencia entre los offsets de Fusion y las constantes del SDK es parcial y esperable: `copyin` y `copyout` 13.02 aparecen como `0x2BD6E0` y `0x2BD5F0` en ambos contextos. Esto demuestra coherencia de la inicialización publicada, no el origen independiente de `patch_mount` ni de los demás símbolos.

## 15. Asset de Fusion 1.4 anterior a la tabla 13.02

La release pública [Fusion 1.4](https://github.com/AetherPS/Fusion/releases/tag/1.4), publicada el 17-ene-2026, contiene `Fusion.bin` de 214672 bytes, SHA-256 `aff12b6cddc352e598ea263e1f901cdc525da5e9c0b53467bf5768ec58032af4`. Su descripción anuncia soporte para 12.50 y 13.00, no 13.02. La inspección pasiva muestra un payload raw con strings `Installing Kernel ELF`, `Failed to decompress Kernel.elf` y `Starting Kernel. (Entry: %llX, ELFBase: %llX, Size: %i)`.

El asset contiene varias secuencias `ELF`, pero la secuencia localizada al offset 213555 no forma un ELF válido al extraerse hasta el final: la cabecera tiene clase y campos corruptos. Esto es compatible con datos comprimidos/embebidos del propio payload de Fusion, no con un kernel Orbis retail. No aparecen strings `patch_mount`, `ffs`, `ufs`, `1302` o `1304`. Clasificación: `VERIFIED` como payload compilado de Fusion; `INVALID` como dump Orbis o artefacto Celsius.

## 16. Issues y validación pública

El PR de Fusion [#13](https://github.com/AetherPS/Fusion/pull/13) se describe literalmente como “only kernel offsets and the implementation in Offsets.h”; no menciona dump, kernel, IDA/Ghidra, FFS o Celsius. Su único comentario del autor indica que quizá añadiría más offsets. Los issues #11 y #12 documentan problemas de módulos, firmware, filesystem dumps y offsets al ejecutar Fusion, pero no identifican el origen de `patch_mount` ni aportan un disassembly FFS. La frase “filesystem dump” en comentarios de soporte es contexto operativo del testkit/retail y no un dump de kernel 13.02 publicado.

El origen material más plausible ahora es un proceso privado que combinó una primitive previa de kernel R/W con el SDK `kdump`/pattern scan y produjo una tabla manual. La evidencia disponible no permite atribuir ese proceso a ArabPixel, Pharaoh2k, bollars o Dr.Yenyen. El primer archivo público de offsets sigue siendo el header de ArabPixel/Fusion del 18-ene-2026, pero el mecanismo de medición continúa sin documentarse.

[26]: https://github.com/ArabPixel/sdk "ArabPixel SDK fork"
[27]: https://github.com/ArabPixel/sdk/commit/4323a2d9d8e2646e7488c5c5147709b5824eef7d "kernel_find_pattern and kernel_get_image_size"
[28]: https://github.com/ArabPixel/sdk/commit/7ca86e9b871b60311c2ce87f4a6be06478751026 "kdump sample fix"
[29]: https://github.com/ArabPixel/sdk/commit/546bb1c513a75885def8ba2598b58fb69a44226b "ArabPixel SDK 13.02 support"
[30]: https://github.com/AetherPS/Fusion/releases/tag/1.4 "Fusion 1.4 release"
[31]: https://github.com/AetherPS/Fusion/pull/13 "Fusion PR 13: 13.02 Kernel offsets"
[32]: https://github.com/AetherPS/Fusion/issues/12 "Fusion offset initialization issue"
[33]: https://github.com/AetherPS/Fusion/issues/11 "Fusion game compatibility issue"

## 17. Resultado de la búsqueda ampliada de artefactos ocultos

La búsqueda de releases, tags, issues y PRs no descubrió un dump oculto ni un artefacto FFS asociado a los offsets. El PR [AetherPS/Fusion #13](https://github.com/AetherPS/Fusion/pull/13) tiene como descripción “only kernel offsets and the implementation in Offsets.h”. Su diff no incluye código de extracción, hash de kernel, dump, proyecto de análisis, patrones de bytes ni referencias UFS/FFS. El comentario de ArabPixel sólo indica que podría añadir más offsets.

La inspección de `ArabPixel/sdk` aporta la única pista técnica nueva: el soporte 13.02 se añadió el 5-oct-2025, antes de la publicación de Fusion 13.02, y el mismo fork ya disponía desde julio/agosto de 2025 de `kernel_find_pattern()` y `samples/kdump/main.c`. La combinación hace plausible que los offsets pudieran medirse con tooling de dump/pattern scan en un entorno privado. Sin embargo, no hay evidencia del archivo de salida, de quién lo produjo, de qué kernel se usó ni de que el proceso se aplicara a `patch_mount` o a Celsius.

La release Fusion 1.4 es un asset compilado de 214672 bytes (`aff12b6cddc352e598ea263e1f901cdc525da5e9c0b53467bf5768ec58032af4`) con payload comprimido propio. Su descripción sólo anuncia 12.50/13.00. La presencia de cadenas `Kernel.elf` y `ELF` embebidas no convierte el asset en kernel Orbis; la extracción ingenua no produce un ELF válido y no aparecen FFS/UFS/13.02. Se clasifica como payload Fusion `VERIFIED` y como supuesto dump Orbis `INVALID`.

La hipótesis más fuerte actual es, por tanto, **“offsets derivados de una sesión privada de kernel R/W y tooling de kdump/pattern scan, publicados después como tablas”**, pero sigue siendo `HYPOTHESIS`. La fuente material primaria, si existió, no está en las ramas, tags, releases, issues o PRs públicos auditados.

## 18. PSFree Enhanced: payload de dumper real, pero sin output 13.02

La búsqueda de la referencia pública de ArabPixel en Reddit localizó la discusión [“is there a kernel dumper for 13.00?”](https://www.reddit.com/r/PS4Mods/comments/1tvjftl/is_there_a_kernel_dumper_for_1300/). ArabPixel respondió que existe un dumper, recomendó compilar el payload de Scene-Collective y mencionó que PSFree Enhanced tenía payloads actualizados.

Se inspeccionó `ArabPixel/old-PSFree-Enhanced/payloads/Bins/Dumper/kerneldumper.bin`. El archivo es un payload raw de 15380 bytes, SHA-256 `61eaf5122a83aec55ac22045f7ac19f86ad663ea78eea3fa9e0d2a63fb5355a9`. Sus strings indican que escribe un archivo en `%s/PS4/%s/kernel.bin`, usa una marca `%s/kernel.complete`, espera un dispositivo USB, calcula tamaño y chunks, y anuncia “Kernel dumped successfully!”. Esto confirma un dumper compilado funcional como artefacto público de tooling.

No aparecen strings `13.02`, `1302`, `13.04`, `ffs_mountfs`, `ffs_reload`, `UFS` o `Celsius`; el repositorio no contiene una variante `kerneldumper-1302.bin`, un kernel.bin resultante, log de ejecución ni hash de un dump. El historial relevante de PSFree Enhanced sólo muestra actualizaciones generales de payloads entre mayo y julio de 2025. Clasificación: `VERIFIED` como payload dumper; `SOURCE_ONLY` para la afirmación de que pudiera estar actualizado; `INVALID` como dump Orbis 13.02.

El dato eleva la plausibilidad de que investigadores con kernel R/W pudieran obtener imágenes de kernel, pero no establece que el dumper de PSFree Enhanced haya sido ejecutado en 13.02 ni que generase la tabla de ArabPixel/Fusion. Tampoco proporciona una dirección o patrón para `patch_mount`/`ffs_mountfs`.

La guía pública de [reversing.codes](https://reversing.codes/posts/ps4-kernel-patching-guide/) confirma conceptualmente que el dumper de Scene-Collective se usa para adquirir un kernel y que los offsets se obtienen restando la base KASLR a direcciones observadas en el dump. Es evidencia metodológica general, no evidencia específica de Orbis 13.02 ni de Celsius.

## 19. Scene-Collective kernel dumper y soporte de firmware

`Scene-Collective/ps4-kernel-dumper` es un proyecto público de 2019 cuyo README dice que descarga el kernel a un dispositivo USB y que soporta cualquier firmware admitido por su SDK. Su historial visible llega hasta revisiones de 7.0X; el CHANGELOG documenta el traslado de offsets específicos al SDK, pero no aparece una revisión 13.02/13.04 ni un dump producido para esas versiones.

El repositorio `Scene-Collective/ps4-payload-repo` es un generador de payloads y sus commits relevantes visibles son antiguos (5.03/6.72); su árbol actual no ofrece una variante identificable `kernel-dumper-1302` o `kernel-dumper-1304`. El resultado de Reddit que recomienda compilar este dumper no constituye evidencia de ejecución 13.02.

El payload `ArabPixel/old-PSFree-Enhanced/payloads/Bins/Dumper/kerneldumper.bin` sí es un binario dumper real y guarda `kernel.bin` en USB, pero no contiene marcador de firmware 13.02/13.04, FFS, Celsius ni output de dump. Clasificación: `VERIFIED` como dumper; `UNVERIFIED` para 13.02; `INVALID` como evidencia de `ffs_mountfs`.

[34]: https://github.com/Scene-Collective/ps4-kernel-dumper "Scene-Collective PS4 Kernel Dumper"
[35]: https://github.com/Scene-Collective/ps4-payload-repo "Scene-Collective payload repository"
[36]: https://github.com/ArabPixel/old-PSFree-Enhanced "ArabPixel PSFree Enhanced"

## 20. Identidad pública de `bollars`

La búsqueda de GitHub identifica una cuenta pública `bollars` creada en 2013, con un único repositorio visible, `bollars/ddoslib`, creado en 2013 y actualizado por última vez en 2017. No contiene material PS4, kernel, FFS, UFS, offsets, Celsius ni herramientas de reverse engineering. No se localizaron gists públicos en esa cuenta ni eventos públicos actuales.

La búsqueda web de `bollars` combinada con PS4/Celsius/`ffs_mountfs` sólo devuelve publicaciones secundarias de julio de 2026 que atribuyen Celsius a ese alias. No aparece una cuenta técnica primaria, repositorio, commit, dump, disassembly, captura de IDA/Ghidra o publicación del propio bollars. Esta ausencia no prueba que el alias de escena y la cuenta GitHub sean la misma persona, ni que no exista material privado; sólo limita la procedencia pública observable. Clasificación: identidad GitHub `VERIFIED`; conexión con Celsius `UNVERIFIED`; publicaciones secundarias `SOURCE_ONLY`.

[37]: https://github.com/bollars "Public GitHub profile for bollars"
[38]: https://github.com/bollars/ddoslib "Only visible repository under bollars"
