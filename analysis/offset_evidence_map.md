# 13.52 Offset Evidence Map

This map records existing values without changing them. A payload embedding or consuming a value is not classified as retail-kernel validation.

| Offset/field | Value | Module/target | Consumer or location | Source/provenance | Evidence type | Status |
|---|---:|---|---|---|---|---|
| `XFAST_SYSCALL_addr` | `0x1c0` | Kernel target | 13.52 offsets table/HEN table | `kpayload/source/offsets/1352.c`; HEN 181 table | `OFFSET_REFERENCE` + payload bytes | Not validated against kernel bytes |
| `PRISON0_addr` | `0x111FA18` | Kernel target | 13.52 offsets table/HEN table | Same as above | `OFFSET_REFERENCE` + payload bytes | Not validated against kernel bytes |
| `ROOTVNODE_addr` | `0x2136E90` | Kernel target | 13.52 offsets table/HEN table | Same as above | `OFFSET_REFERENCE` + payload bytes | Not validated against kernel bytes |
| `M_TEMP_addr` | `0x1520D00` | Kernel target | Allocator consumers in payload | Same as above | `STRONG_STRUCTURAL` for payload; no kernel bytes | Unverified retail target |
| `ALLPROC_addr` | `0x1B28538` | Kernel target | Process-list consumers in payload | Same as above | `STRONG_STRUCTURAL` for payload; no kernel bytes | Unverified retail target |
| `SYSENT_addr` | `0x1102B70` | Kernel target | Syscall-table field in payload | Same as above | `STRONG_STRUCTURAL` for payload; no kernel bytes | Favored candidate; not retail-verified |
| `SYSENT_addr` alternative | `0x110A760` | Kernel target | Historical/partial table | Existing research corpus | `UNVERIFIED` | No consumer or target bytes |
| `pmap_protect` candidate A | `0x58570` | Kernel target | Patch/pmap research | Existing external tables | `DOCUMENTATION`/`OFFSET_REFERENCE` | Conflict unresolved |
| `pmap_protect` candidate B | `0x59DF0` | Kernel target | Patch/pmap research | Existing external tables | `DOCUMENTATION`/`OFFSET_REFERENCE` | Conflict unresolved |
| `pmap` patch site | `0x59E37` | Kernel target | Candidate patch site | Existing research corpus | `INDIRECT_STRUCTURAL` | No target bytes |
| `kernel_pmap_store` | `0x1B2C3A0` | Kernel target | Kernel mapping research | Existing table | `OFFSET_REFERENCE` | No target bytes |
| `vmspace_acquire_ref` | `0x2F76E0` | Kernel target | `proc_get_vm_map` payload consumer | 13.52 HEN table | `STRONG_STRUCTURAL` for payload | No target bytes |
| `vmspace_free` | `0x2F7510` | Kernel target | `proc_get_vm_map` payload consumer | 13.52 HEN table | `STRONG_STRUCTURAL` for payload | No target bytes |
| `vm_map_lock_read` | `0x2F7870` | Kernel target | VM-map lock consumer | 13.52 HEN table | `STRONG_STRUCTURAL` for payload | No target bytes |
| `vm_map_unlock_read` | `0x2F78C0` | Kernel target | VM-map unlock consumer | 13.52 HEN table | `STRONG_STRUCTURAL` for payload | No target bytes |
| `vm_map_lookup_entry` | `0x2F7EB0` | Kernel target | VM-map lookup consumer | 13.52 HEN table | `STRONG_STRUCTURAL` for payload | No target bytes |
| `proc_rwmem` | `0x366760` | Kernel target | Process memory read/write consumer | 13.52 HEN table | `STRONG_STRUCTURAL` for payload | No target bytes |
| `unknown1` | `0x4D6D0` | Unknown kernel target | No demonstrated consumer | Existing 1352 table | `UNVERIFIED` | Meaning unknown |
| `unknown2` | `0xE6C60` | Unknown kernel target | No demonstrated consumer | Existing 1352 table | `UNVERIFIED` | Meaning unknown |
| `check_disc_root_param_patch` | `0xDEADC0DE` | 13.04 ShellCore target | Historical patch field | Canonical `1304.c` | `UNVERIFIED` placeholder | Must remain placeholder |

## Required evidence to raise status

A `VERIFIED_INTERNAL` classification requires bytes or relocations from the same target image, a known file-to-address mapping, and a demonstrated semantic relationship such as a prologue, table entry, caller/callee chain or structure reference. HEN table inclusion alone is `STRONG_STRUCTURAL` for the payload and cannot raise a retail-kernel field to verified.
