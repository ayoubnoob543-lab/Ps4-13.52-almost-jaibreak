# Commit 6cacb243 provenance audit

Source: `adri22235/ps4-suid-scanner`, commit `6cacb2432f9940a5710a8d13895d4c799342cca6`, dated 2026-07-18.

Commit message: “Add complete PS4 13.04 kernel offsets (verified via Pharaoh2k + 1302 base)”. The commit adds only `1304.c` and `1304.h`: a C offset structure and its declaration. The visible patch contains no kernel image, dump, IDA/Ghidra project, bytes, hash, FFS symbol, `ffs_mountfs` reference, test log, or signed statement from Pharaoh2k. The 13.04 table includes ordinary kernel/VFS-related entries such as `memcpy`, `proc_rwmem`, and various patch hooks, but naming an offset does not identify the underlying function's implementation or prove Celsius.

Classification: commit and table existence `VERIFIED`; “verified via Pharaoh2k” is `SOURCE_ONLY`; 13.02/13.04 byte identity `UNVERIFIED`; FFS/Celsius relationship `HYPOTHESIS`/`INVALID` without disassembly; hardware validation `UNVERIFIED`.
