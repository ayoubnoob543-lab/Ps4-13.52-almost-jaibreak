#pragma once
/* PS4 11.02 — kexec offsets: BestPig */
/* PS4 11.02 allproc, vmspace, proc_rwmem: MSI_Ins_Dir (kernel dump) */

#define kern_off_xfast_syscall             0x1C0

#define kern_off_prison0                   0x111F830
#define kern_off_rootvnode                 0x2116640

#define kern_off_allproc                   0x22D0A98
#define kern_off_vmspace_acquire_ref       0x357740
#define kern_off_vmspace_free              0x357570
#define kern_off_proc_rwmem                0x3838C0

#define kern_off_printf                    0x2FCBF0
#define kern_off_snprintf                  0x2FCEF0
#define kern_off_copyin                    0x2DE000
#define kern_off_copyout                   0x2DDF10
#define kern_off_copyinstr                 0x2DE4B0

#define kern_off_kmem_alloc                0x245E30
#define kern_off_kmem_alloc_contig         0x22F8F0
#define kern_off_kmem_free                 0x246000

#define kern_off_kernel_map                0x21FF130
#define kern_off_kernel_pmap_store         0x2162A88
#define kern_off_sysent                    0x1101760

#define kern_off_pmap_extract              0x1142B0
#define kern_off_pmap_protect              0x115450

#define kern_off_pml4pml4i                 0x2162A78
#define kern_off_dmpml4i                   0x2162A7C
#define kern_off_dmpdpi                    0x2162A80

#define kern_off_sched_pin                 0x2BB9D0
#define kern_off_sched_unpin               0x2BB9F0
#define kern_off_smp_rendezvous            0x1342E0
#define kern_off_smp_no_rendevous_barrier  0x1340F0
#define kern_off_icc_query_nowait          0x39F410

#define kern_off_gpu_devid_is_9924         0x4B4A00
#define kern_off_gc_get_fw_info            0x4B1F50
#define kern_off_set_gpu_freq              0x4B0A90
#define kern_off_set_pstate                0x4C8C70
#define kern_off_update_vddnp              0x4B1030
#define kern_off_set_cu_power_gate         0x4B1440
#define kern_off_set_nclk_mem_spd          0x2F56C0
#define kern_off_Starsha_UcodeInfo         0x0

#define kern_off_pstate_before_shutdown    0x198670
#define kern_off_kern_reboot               0x198080

#define kern_off_eap_hdd_key               0x26C4CD0
#define kern_off_edid                      0x2749E58
#define kern_off_wlanbt                    0x1D1590

#define kern_off_disable_aslr              0x3B11C4
#define kern_off_mmap_self_1               0x3D0E70
#define kern_off_mmap_self_2               0x3D0E90
#define kern_off_mmap_self_3               0x157FB1
#define kern_off_reg_mgr_set_int           0x4EDF80
#define kern_off_set_time                  0x633280
#define kern_off_clear_time_diff           0x632760
#define kern_off_target_id                 0x221C60D
#define kern_off_icc_nvs_write             0x2D4150
#define kern_off_npdrm_open                0x64E2C0
#define kern_off_npdrm_close               0x64E2E0
#define kern_off_npdrm_ioctl               0x64E337
#define kern_off_no_bd_patch               0x33E833
