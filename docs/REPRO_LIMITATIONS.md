# Reproducibility and Validation Limitations

## What the repository reproduces

The repository reproduces static checks over the checked-in libkernel corpus. `tools/verify_offsets.py` verifies the combined dump hash, the three-chunk concatenation, expected file ranges and structural byte windows. `tools/analyze_xref_versions.py` regenerates disassembly-derived reports and version-string XREF reports. The host build validates compilation of the available sources with the pinned payload SDK; it does not execute Orbis code.

The Phase 5 analysis records a separate documented claim: an external public HEN payload is described as containing a serialized 89-field 13.52 table and a selector that maps `0x548` to the table at `0x105e0`. The exact external asset is not present in the current checkout, so this is not locally reproduced binary evidence. Even if obtained, payload inclusion would not prove the values against retail kernel bytes.

## What is not available

A complete retail PS4 FW 13.52 kernel or eboot with a verified hash, build identity, load base and bytes around the critical addresses is not present. Consequently, the repository cannot directly validate `SYSENT`, `pmap_protect`, `ALLPROC`, `M_TEMP`, `kernel_pmap_store`, `vmspace_*`, `vm_map_*` or `proc_rwmem` against the kernel image.

The eboot/GOT artifact needed to establish the documented `sceKernelUsleep` anchor is also missing. The existing libkernel dump does not contain the runtime value of the eboot GOT slot and cannot independently prove the proposed base calculation.

Exact WebKit 13.52 and matching `SceShellCore`, `SceShellUI` and `SceRemotePlay` images are not present. `webkit_gadgets_1304.js` and `webkit_gadgets_1350.js` are historical/reference tables, and `jordy_stage2.js` is an incomplete integration prototype. External projects can document historical techniques, but their offsets must not be imported as 13.52 values without target bytes.

There is no reproducible hardware log proving the entry path, JIT behavior, payload loading, kernel transition or console compatibility. No exploit, payload, HEN, ISO or recovered code is executed by the static audit.

## Evidence boundaries

| Observation | What it proves | What it does not prove |
|---|---|---|
| SHA-256 matches | The local artifact matches the recorded bytes | Firmware identity or runtime validity |
| Chunks concatenate exactly | The local dump reconstruction is byte-identical | That the dump is a kernel image |
| XREF/prologue pattern | A structural relation in the raw file | Symbol identity or export name |
| Offset appears in HEN bytes | The payload embeds the value | Correctness against retail kernel |
| Host build succeeds | Sources compile in the host toolchain | Orbis ABI, console execution or jailbreak |
| Public table repeats a value | Documentation lineage or reuse | Independent binary corroboration |

## Artifact and legal policy

Missing proprietary or externally hosted artifacts are recorded by name, provenance and hash when known. They must not be replaced with guessed values, another firmware, a different module or a generated placeholder. Sony firmware, proprietary dumps, console images and external payloads may have redistribution restrictions; the repository should prefer hashes and reproducible instructions over unauthorized copies.

## Minimum artifacts for complete validation

The minimum next artifact is a kernel or eboot image from the same PS4 FW 13.52 build with a verifiable hash and load-base/segment information. It must contain bytes or relocations sufficient to inspect `0x58570`, `0x59DF0`, `0x59E37`, `0x1102B70`, `0x110A760`, `0x1B28538`, `0x1B2C3A0`, `0x1520D00`, the `vmspace`/`vm_map` range and `0x366760`.

Separate versioned images of `SceShellCore`, `SceShellUI` and `SceRemotePlay` are required for patch-site validation. A matching eboot or import/relocation map is required for the GOT anchor. A matching WebKit binary/build ID and JIT/entry-path logs would be required for a complete WebKit-to-libkernel chain. None of these requirements authorizes execution; they are static-evidence requirements only.
