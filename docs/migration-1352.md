# PS4 13.52 migration framework

This document describes the static, artifact-first migration base now present in this repository.

## Verified libkernel anchor

The repository includes `libkernel_sys_13.52.bin` and three chunks. The validation command is:

```bash
python3 tools/validate_libkernel_1352.py --json
```

The validator checks the full SHA-256, each chunk SHA-256 and size, concatenates `lk_dump1.bin`, `lk_dump2.bin`, `lk_dump3.bin`, and checks byte equality with the combined artifact.

Verified anchor:

```text
size:   479232 bytes
sha256: ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c
format: raw x86-64 blob; not ELF/SELF
```

Direct byte evidence exists for:

```text
jitshm_create: offset 0x510, syscall 0x215
jitshm_alias:  offset 0x530, syscall 0x216
```

The remaining published libkernel names are recorded as `STRUCTURAL`: their offsets contain coherent x86-64 function entries, but a runtime base, export table, relocation table, GOT or PLT is not present in this raw blob. No `DIRECT_RUNTIME` claim is made.

## WebKit parameterization

`tools/webkit_1352_migration.json` is intentionally incomplete. It has no guessed WebKit addresses. The target artifact, module bases, `.text`, `PT_SCE_RELRO`, vtable bytes and import patterns remain empty until a real 13.52 WebKit image is supplied.

`tools/scan_webkit_patterns.py` accepts a raw or extracted image and searches exact or masked byte patterns from the configuration:

```bash
python3 tools/scan_webkit_patterns.py \
  --image /path/to/libSceNKWebKit_13.52.bin \
  --config tools/webkit_1352_migration.json \
  --json
```

A match is only a byte-level candidate. The tool explicitly does not infer a runtime base, GOT/PLT, semantic function identity or firmware portability from a match.

## Jordy Stage 2 parameterization

`tools/jordy_1352_migration.json` separates portable logic from firmware-dependent data:

```text
portable dispatch and argument handling: enabled
WebKit base:                           pending
WebKit vtable:                         pending
libkernel_web/libc bases:              pending
GOT/PLT:                               pending
gadgets/pivot/ROP:                    pending
```

The libkernel wrapper references in this configuration point only to the verified 13.52 anchor. No WebKit gadget or kernel offset is filled from 13.04, 13.50, 9.00, PS5 or another firmware.

## Kernel analyzer

`tools/scan_kernel_structures.py` is a conservative scanner for a future kernel artifact. It accepts byte patterns supplied in a separate JSON file and reports candidates for:

```text
sysent
pmap_protect
allproc
rootvnode
kernel_map
```

It never computes a firmware delta and never labels a candidate as confirmed. Each result requires same-build bytes, function boundaries, XREFs and structural validation. Running it on `libkernel_sys_13.52.bin` correctly returns no kernel candidates because libkernel is not the kernel.

## Current boundary

The repository now has a real 13.52 libkernel anchor and executable static validation, but the chain is still incomplete:

```text
WebKit 13.52:       absent
libkernel_sys 13.52: verified
kernel 13.52:       absent
```

The next artifact with the highest expected value is a 13.52 `libSceNKWebKit.sprx` or equivalent `.text` plus `PT_SCE_RELRO` dump. Until that exists, WebKit imports, vtables, GOT/PLT, gadgets and ROP pivots remain `REQUIRES_REANALYSIS` or `UNVERIFIED`.
