#pragma once
/* PS4 9.00 — kexec offsets: codedwrench */

#define kern_off_xfast_syscall             0x1C0

#define kern_off_prison0                   0x111F870
#define kern_off_rootvnode                 0x21EFF20
#define kern_off_allproc                   0x1B946E0

#define kern_off_vmspace_acquire_ref       0x7B9E0
#define kern_off_vmspace_free              0x7B810
#define kern_off_proc_rwmem                0x41EB00

#define kern_off_printf                    0xB7A30
#define kern_off_snprintf                  0xB7D30
#define kern_off_copyin                    0x2716A0
#define kern_off_copyout                   0x2715B0
#define kern_off_copyinstr                 0x271B50

#define kern_off_kmem_alloc                0x37BE70
#define kern_off_kmem_alloc_contig         0x270880
#define kern_off_kmem_free                 0x37C040

#define kern_off_kernel_map                0x2268D48
#define kern_off_kernel_pmap_store         0x1B904B0
#define kern_off_sysent                    0x1100310

#define kern_off_pmap_extract              0x12D050
#define kern_off_pmap_protect              0x12E1F0

#define kern_off_pml4pml4i                 0x1B904A0
#define kern_off_dmpml4i                   0x1B904A4
#define kern_off_dmpdpi                    0x1B904A8

#define kern_off_sched_pin                 0x1CD0D0
#define kern_off_sched_unpin               0x1CD0F0
#define kern_off_smp_rendezvous            0x432BF0
#define kern_off_smp_no_rendevous_barrier  0x432A00
#define kern_off_icc_query_nowait          0x2E1760

#define kern_off_gpu_devid_is_9924         0x4AC260
#define kern_off_gc_get_fw_info            0x4DF280
#define kern_off_set_gpu_freq              0x4DDDC0
#define kern_off_set_pstate                0x4D6FC0
#define kern_off_update_vddnp              0x4DE360
#define kern_off_set_cu_power_gate         0x4DE770
#define kern_off_set_nclk_mem_spd          0x0
#define kern_off_Starsha_UcodeInfo         0x0

#define kern_off_pstate_before_shutdown    0x29A970
#define kern_off_kern_reboot               0x29A380

#define kern_off_eap_hdd_key               0x26C4C90
#define kern_off_edid                      0x274C058
#define kern_off_wlanbt                    0x180860

#define kern_off_disable_aslr              0x5F824
#define kern_off_mmap_self_1               0x8BC90
#define kern_off_mmap_self_2               0x8BCB0
#define kern_off_mmap_self_3               0x168051
#define kern_off_reg_mgr_set_int           0x4E8B10
#define kern_off_set_time                  0x634450
#define kern_off_clear_time_diff           0x633930
#define kern_off_target_id                 0x221688D
#define kern_off_icc_nvs_write             0x10B150
#define kern_off_npdrm_open                0x64F160
#define kern_off_npdrm_close               0x64F180
#define kern_off_npdrm_ioctl               0x64F1D7
#define kern_off_no_bd_patch               0x53683
