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
