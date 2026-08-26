#pragma once
/* PS4 13.52 — kexec offsets: ArabPixel */

#define kern_off_xfast_syscall             0x1C0

#define kern_off_prison0                   0x111FA18
#define kern_off_rootvnode                 0x2136E90

/* kern_off_vmspace_acquire_ref TODO — help wanted */
/* kern_off_vmspace_free TODO — help wanted */
/* kern_off_proc_rwmem TODO — help wanted */

#define kern_off_printf                    0x2E0510
#define kern_off_snprintf                  0x2E0810
#define kern_off_copyin                    0x2BD790
#define kern_off_copyout                   0x2BD6A0
#define kern_off_copyinstr                 0x2BDC40

#define kern_off_kmem_alloc                0x466290
#define kern_off_kmem_alloc_contig         0x24D4F0
#define kern_off_kmem_free                 0x466460

#define kern_off_kernel_map                0x22D1D50
#define kern_off_kernel_pmap_store         0x1B2C3A0
#define kern_off_sysent                    0x1102B70

#define kern_off_pmap_extract              0x573D0
#define kern_off_pmap_protect              0x58570

#define kern_off_pml4pml4i                 0x1B2C390
#define kern_off_dmpml4i                   0x1B2C394
#define kern_off_dmpdpi                    0x1B2C398

#define kern_off_sched_pin                 0x231720
#define kern_off_sched_unpin               0x231740
#define kern_off_smp_rendezvous            0x1AD5E0
#define kern_off_smp_no_rendevous_barrier  0x1AD3F0
#define kern_off_icc_query_nowait          0x448380

#define kern_off_gpu_devid_is_9924         0x4ACDF0
#define kern_off_gc_get_fw_info            0x4BB7A0
#define kern_off_set_gpu_freq              0x4BA2E0
#define kern_off_set_pstate                0x4BC6B0
#define kern_off_update_vddnp              0x4BA880
#define kern_off_set_cu_power_gate         0x4BAC90
#define kern_off_set_nclk_mem_spd          0x437140
#define kern_off_Starsha_UcodeInfo         0x0

#define kern_off_pstate_before_shutdown    0x3A2B90
#define kern_off_kern_reboot               0x3A25A0

#define kern_off_eap_hdd_key               0x26C4CF0
#define kern_off_edid                      0x275E148
#define kern_off_wlanbt                    0x4792A0

#define kern_off_disable_aslr              0x478504
#define kern_off_mmap_self_1               0x3B35F0
#define kern_off_mmap_self_2               0x3B3610
#define kern_off_mmap_self_3               0x1FC561
#define kern_off_reg_mgr_set_int           0x4E8CC0
#define kern_off_set_time                  0x635220
#define kern_off_clear_time_diff           0x634700
#define kern_off_target_id                 0x21CC60D
#define kern_off_icc_nvs_write             0xA5A10
#define kern_off_npdrm_open                0x64DF00
#define kern_off_npdrm_close               0x64DF20
#define kern_off_npdrm_ioctl               0x64DF77
#define kern_off_no_bd_patch               0x1D5EA3
