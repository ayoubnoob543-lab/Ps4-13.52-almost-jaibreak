# WebKit and libkernel Reproducibility

## Local artifacts

| Artifact | Current status | Reproducibility boundary |
|---|---|---|
| `webkit_gadgets_1304.js` | Historical 13.04 gadget/reference table | Not an exact 13.52 WebKit image or build ID |
| `webkit_gadgets_1350.js` | Historical 13.50 reference table | Not proof of 13.52 offsets |
| `jordy_stage2.js` | Incomplete integration/prototype; base discovery and pivot remain explicit dependencies | Does not provide a complete entry path or executable exploit |
| `libkernel_sys_13.52.bin` | Raw libkernel corpus with exact chunk/hash audit | Not kernel, eboot or Shell image; no runtime base |
| `full_objdump_intel.txt` | Locally generated disassembly artifact | File-relative analysis only; no ELF symbols or runtime relocations |

The static workflow can reproduce hashes, chunk concatenation, raw x86-64 disassembly and documented XREFs. It cannot reconstruct a runtime GOT, import table or load base that is absent from the corpus.

## External references used only as documentation

The following projects are useful for historical context and methodology but are not sources from which 13.52 offsets should be copied:

- [ntfargo/CSSFontFace-Exploit](https://github.com/ntfargo/CSSFontFace-Exploit) documents CSSFontFace layouts and a supported chain through older firmware; its code table does not contain a 13.52 implementation.
- [Al-Azif/psfree-lapse](https://github.com/Al-Azif/psfree-lapse) contains historical WebKit and kernel material for older firmware, including `sysent[661]` values that are not `SYSENT_addr` for 13.52.
- [kmeps4/PSFree](https://github.com/kmeps4/PSFree) contains historical 9.00 material, not a 13.52 kernel image.
- [ConsoleMods Exploit Chart](https://consolemods.org/wiki/PS4:Exploit_Chart) is documentation of public exploit status and does not provide 13.52 bytes or offsets.

## Missing artifacts

Complete static reproducibility of a WebKit-to-libkernel-to-kernel chain would require an exact WebKit 13.52 binary or dump with build ID, an exact matching libkernel import/export or relocation map, the eboot/GOT artifact used for any base anchor, and versioned Shell module images where patch sites are involved.

For the kernel side, a same-build 13.52 kernel/eboot with hash, segment/base information and bytes around `SYSENT`, `pmap_protect`, `ALLPROC`, `kernel_pmap_store`, `M_TEMP`, `vmspace_*`, `vm_map_*` and `proc_rwmem` is required. For the entry path, a matching WebKit build, documented JIT evidence and non-hardware static logs would be needed. Hardware logs would still be required for claims about runtime compatibility.

## Classification policy

A gadget or structure copied from a different firmware is historical documentation, not 13.52 validation. A value embedded in a payload is evidence of payload/table inclusion. A `VERIFIED_INTERNAL` classification requires bytes from the same target image plus a defensible address mapping and semantic cross-reference. No file in the current repository meets that standard for the pending retail-kernel offsets.
