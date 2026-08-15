# Auditoría de offsets PS4 13.52

## Alcance

Esta auditoría compara `kpayload/source/offsets/1352.c` con el commit público `2beb4cfcef1d416a32d6fb7b35f01189e9eb62e2` de `Scene-Collective/ps4-hen`, titulado **Add 13.52 support**. La comparación se hizo campo por campo y encontró **89 campos en cada tabla**.

La procedencia pública demuestra que la tabla local sigue la estructura y los nombres del proyecto de referencia. No demuestra por sí misma que los valores funcionen en una PS4 física con firmware 13.52.

## Divergencia encontrada

Sólo un valor difería entre el archivo público y el local:

| Campo | Commit público | Tabla independiente SLOPOS 13.52 | Valor local anterior | Decisión |
|---|---:|---:|---:|---|
| `SYSENT_addr` | `0x01102B70` | `0x01102B70` | `0x0110A760` | Cambiado a `0x01102B70`; hardware aún **UNVERIFIED** |

La tabla independiente `SLOPOS-offsets/ps4/1352.h` está explícitamente etiquetada `PS4 13.52 — kexec offsets: ArabPixel` y también define `kern_off_sysent = 0x1102B70`. La coincidencia independiente con el commit público resuelve la discrepancia de procedencia pública a favor de `0x01102B70`. El cambio no equivale a una prueba de ejecución en hardware.

## Clasificación individual

Los 89 campos se clasifican así:

| Campos | Nivel de evidencia |
|---|---|
| `PRISON0_addr`, `ROOTVNODE_addr` | **Parcialmente corroborados**: aparecen en la tabla pública parcial de 13.52 y coinciden con el commit público y el árbol local. Sigue faltando validación en hardware 13.52. |
| `SYSENT_addr` | **Públicamente cross-checkeado para 13.52**, porque Scene-Collective y SLOPOS coinciden en `0x01102B70`. La tabla de `remote_lua_loader` usa `0x110A760` para 11.50–12.02, no para 13.52. La ejecución en hardware sigue **UNVERIFIED**. |
| `XFAST_SYSCALL_addr`, `M_TEMP_addr`, `MINI_SYSCORE_SELF_BINARY_addr`, `ALLPROC_addr`, `SBL_DRIVER_MAPPED_PAGES_addr`, `SBL_PFS_SX_addr`, `SBL_KEYMGR_KEY_SLOTS_addr`, `SBL_KEYMGR_KEY_RBTREE_addr`, `SBL_KEYMGR_BUF_VA_addr`, `SBL_KEYMGR_BUF_GVA_addr`, `FPU_CTX_addr`, `memcmp_addr`, `_sx_xlock_addr`, `_sx_xunlock_addr`, `malloc_addr`, `free_addr`, `strstr_addr`, `fpu_kern_enter_addr`, `fpu_kern_leave_addr`, `memcpy_addr`, `memset_addr`, `strlen_addr`, `printf_addr`, `eventhandler_register_addr` | **Public implementation only; no verificación independiente localizada**. Coinciden con el commit público, pero no se ha demostrado que sean correctos en 13.52 real. |
| `sceSblACMgrGetPathId_addr`, `sceSblServiceMailbox_addr`, `sceSblAuthMgrSmIsLoadable2_addr`, `_sceSblAuthMgrGetSelfInfo_addr`, `_sceSblAuthMgrSmStart_addr`, `sceSblAuthMgrVerifyHeader_addr`, `RsaesPkcs1v15Dec2048CRT_addr`, `Sha256Hmac_addr`, `AesCbcCfb128Encrypt_addr`, `AesCbcCfb128Decrypt_addr`, `sceSblDriverSendMsg_0_addr`, `sceSblPfsSetKeys_addr`, `sceSblKeymgrSetKeyStorage_addr`, `sceSblKeymgrSetKeyForPfs_addr`, `sceSblKeymgrCleartKey_addr`, `sceSblKeymgrSmCallfunc_addr` | **Public implementation only; no verificación independiente localizada**. |
| `vmspace_acquire_ref_addr`, `vmspace_free_addr`, `vm_map_lock_read_addr`, `vm_map_unlock_read_addr`, `vm_map_lookup_entry_addr`, `proc_rwmem_addr` | **Public implementation only; no verificación independiente localizada**. |
| `sceSblAuthMgrIsLoadable__sceSblACMgrGetPathId_hook`, `sceSblAuthMgrIsLoadable2_hook`, `sceSblAuthMgrVerifyHeader_hook1`, `sceSblAuthMgrVerifyHeader_hook2`, `sceSblAuthMgrSmLoadSelfSegment__sceSblServiceMailbox_hook`, `sceSblAuthMgrSmLoadSelfBlock__sceSblServiceMailbox_hook` | **Public implementation only; no verificación independiente localizada**. |
| `sceSblKeymgrSetKeyStorage__sceSblDriverSendMsg_hook`, `sceSblKeymgrInvalidateKey__sx_xlock_hook`, `sceSblKeymgrSmCallfunc_npdrm_decrypt_isolated_rif_hook`, `sceSblKeymgrSmCallfunc_npdrm_decrypt_rif_new_hook`, `mountpfs__sceSblPfsSetKeys_hook1`, `mountpfs__sceSblPfsSetKeys_hook2` | **Public implementation only; no verificación independiente localizada**. |
| `sceSblRcMgrIsAllowDebugMenuForSettings_patch`, `sceSblRcMgrIsStoreMode_patch`, `CreateUserForIDU_patch`, `remote_play_menu_patch`, `SceRemotePlay_patch1`, `SceRemotePlay_patch2` | **Public implementation only; no verificación independiente localizada**. |
| `sceKernelIsGenuineCEX_patch1`, `sceKernelIsGenuineCEX_patch2`, `sceKernelIsGenuineCEX_patch3`, `sceKernelIsGenuineCEX_patch4`, `nidf_libSceDipsw_patch1`, `nidf_libSceDipsw_patch2`, `nidf_libSceDipsw_patch3`, `nidf_libSceDipsw_patch4` | **Public implementation only; no verificación independiente localizada**. |
| `check_disc_root_param_patch`, `app_installer_patch`, `check_system_version`, `check_title_system_update_patch`, `enable_data_mount_patch`, `enable_psvr_patch`, `enable_fpkg_patch`, `fake_free_patch`, `pkg_installer_patch`, `ext_hdd_patch`, `debug_trophies_patch`, `disable_screenshot_patch` | **Public implementation only; no verificación independiente localizada**. `check_disc_root_param_patch = 0xDEADC0DE` es un sentinel, no una dirección utilizable. |
| `proc_p_comm_offset`, `proc_path_offset` | **Public implementation only; no verificación independiente localizada**. |

## Fuentes comparadas

La fuente principal es el commit público de Scene-Collective:

<https://github.com/Scene-Collective/ps4-hen/commit/2beb4cfcef1d416a32d6fb7b35f01189e9eb62e2>

La tabla parcial del proyecto de investigación enumera `PRISON0`, `ROOTVNODE`, `SYSENT`, `unknown1` y `unknown2`, pero declara expresamente que está incompleta:

<https://github.com/adri22235/ps4-suid-scanner/blob/main/1352_offsets.txt>

`remote_lua_loader` publica `0x110A760` como `SYSENT_661_OFFSET` para 11.50–11.52 y 12.00–12.02, pero no contiene una entrada 13.52:

<https://raw.githubusercontent.com/shahrilnet/remote_lua_loader/main/savedata/kernel_offset.lua>

La tabla independiente que resolvió la discrepancia es `SLOPOS-offsets/ps4/1352.h`, commit `42273e2180cae9aa0c1a67332994d75e1baa713c`, con `kern_off_sysent = 0x1102B70` y la cabecera explícitamente etiquetada para PS4 13.52:

<https://github.com/alferdoss/SLOPOS-offsets/blob/master/ps4/1352.h>

## Conflicto adicional fuera de `1352.c`

La tabla independiente SLOPOS define `kern_off_pmap_protect = 0x58570`, mientras que las macros públicas de Scene-Collective y el installer local definen `K1352_PMAP_PROTECT = 0x00059DF0`. El código del installer usa esa macro como dirección de la función `pmap_protect`, por lo que ambos nombres parecen semánticamente comparables, pero la diferencia no puede resolverse sólo con texto: SLOPOS deriva su bloque de `ps4-linux/ps4-linux-loader` y Scene-Collective usa otra tabla de HEN. Se deja documentado como **conflicto pendiente**, sin cambiarlo, porque no existe una tercera fuente independiente ni una comprobación de bytes/kernel que permita decidir con seguridad.

Los offsets `copyin`, `copyout` y `copyinstr` de SLOPOS son entradas de funciones, mientras que las macros `K1352_COPYIN_PATCH_*`, `K1352_COPYOUT_PATCH_*` y `K1352_COPYINSTR_PATCH_*` del installer son sitios de parche; no son comparaciones uno a uno y no se sustituyen.

## Conclusión

La evidencia pública independiente permite resolver la discrepancia de `SYSENT_addr` a favor de `0x01102B70`; se actualizó el código y la nota PPPwn para usar ese valor. No existe base suficiente para elevar ningún campo a **verificado por ejecución en hardware 13.52**. Los restantes 88 campos siguen clasificados según las categorías anteriores y el bloqueo operativo restante es una prueba real con una PS4 13.52 y una fuente de lectura/validación de kernel que permita comprobar la tabla completa y los parches dependientes.
