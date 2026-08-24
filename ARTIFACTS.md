# Artifact Inventory and Provenance

This file records the artifacts used by the static audit and host build. Hashes are copied from the existing audit records; no new firmware value or offset is inferred here.

## Core repository artifacts

| Artifact | Repository path | Size | SHA-256 | Provenance and status | Reproducible output |
|---|---|---:|---|---|---|
| Combined libkernel dump | `libkernel_sys_13.52.bin` | 479232 B (`0x75000`) | `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c` | Existing research corpus; raw libkernel artifact; not a kernel/eboot image | `analysis/verify_offsets.json`, XREF reports |
| Dump chunk 1 | `lk_dump1.bin` | 159744 B (`0x27000`) | `d4a9a642f85446785469750532d9353c9010ebec4373b8e9c4c06d594536da57` | Existing chunk; concatenation base `0x00000` | `analysis/concatenation_sha256.txt` |
| Dump chunk 2 | `lk_dump2.bin` | 159744 B (`0x27000`) | `e044d0e5303596df94f86190d34bee6dda8e87f9a51578d067e8d1650ca15e8d` | Existing chunk; concatenation base `0x27000` | `analysis/concatenation_sha256.txt` |
| Dump chunk 3 | `lk_dump3.bin` | 159744 B (`0x27000`) | `e31dd16ddc488851c98bc1782cfe919ece1cab2c141bd0ef7c8a9ef82fb9fdf2` | Existing chunk; concatenation base `0x4e000` | `analysis/concatenation_sha256.txt` |
| Historical BD-J ISO | `scanner_1304.iso` | See local file | See existing inventory | Historical 13.04 artifact; not a confirmed 13.52 entry path | Scanner documentation only |
| Historical HEN payload | `hen.bin` | See local file | `32570b6e54c9531dc8a7d75ef4da6557d440bf69c4b765a85a77d428db3a4b73` | Existing historical corpus artifact; not proof of retail kernel validation | Build outputs only |
| GoldHEN payload (public release) | `goldhen/goldhen.bin` | 260160 B | `eb9fee5e9e3618c0a144a6fc6b8fc1ec7e89cf06483ad64ae7c1085efc9525a3` | Official GitHub release `2.4b18` by SiSTR0; supports FW 5.05–11.00 only; reference infrastructure, not 13.52 evidence | `goldhen/MANIFEST.json`, `docs/goldhen.md` |
| GoldHEN original archive | `goldhen/archive/GoldHEN_v2.4b18.7z` | 258065 B | `d0c84c79f65df5afc79a00c578f33ab1aa70aeb9c205f1e789895dc7d4fca38d` | Verbatim official asset from `GoldHEN/GoldHEN` release `2.4b18`; provenance anchor for the extracted files | `goldhen/MANIFEST.json` |
| GoldHEN PPPwn stage2 set v1.03 | `goldhen/pppnw_stage2/` | 8 × 2705 B bins + inner 7z | Per-file hashes in manifest | Included in the official asset; identical builds across minor FW revisions (see `docs/goldhen.md`) | `goldhen/MANIFEST.json` |
| HenLoader BD-J disc image | `goldhen/henloader.iso` | 16777216 B | `23236fa7c820a7e1b3fc1e4c556f0be6e793fbfcd6c5093346937afc62f399f5` | Built locally from pinned submodule `third_party/henloader_lp` (Lapse/Poops entry, AIO fix embedded); loads GoldHEN as USB `payload.bin`; supported FWs only, not a 13.52 path | `goldhen/MANIFEST.json`, `docs/goldhen.md` |

## External or generated artifacts not redistributed here

| Artifact | Expected source | Recorded identity | Inclusion policy |
|---|---|---|---|
| HEN 181 payload | Scene-Collective/ps4-hen release `pre-release-main-181`, commit `2beb4cfcef1d416a32d6fb7b35f01189e9eb62e2` | 499776 B; SHA-256 `568d57e7c6bfff1b96fc20a4e00b9ca744aa58b135a56eeb5c66c1175acfac3e` | Not included; use only where legally permitted; payload-table evidence is not kernel-byte validation |
| Serialized 13.52 table | HEN 181 offset `0x105e0–0x10743` | 356 B; SHA-256 `d032dbd790eaa29cd8ec7571ee04636f82bbbb50a9b2ce0d24dfa003ace0030f` | Derived evidence; not a firmware image |
| Plugin archive | `https://github.com/Scene-Collective/ps4-hen-plugins/releases/latest/download/plugins.zip` | SHA-256 `196e3f8d854ccbc9654c9836f9e73784c39c0e4b88af64dee8bc85087f08e7bc` | Build input documented in `installer/GENERATED_ASSETS.md`; do not commit downloaded archive |
| Newer GoldHEN builds (e.g. `2.4b18.7`) | Ko-fi distribution by SiSTR0 only, no GitHub release | No local hash | Not included; no verifiable public provenance for this corpus |
| Local HEN payload rebuild (`hen.rebuilt-local.bin`, not committed) | Regenerated in-place by `./build.sh` on aarch64 host via the portability-adapted pipeline (`docs/build-portability.md`), 2026-08-24 | 514784 B; SHA-256 `38bf58bb22abcb3a431de6a3b05613f19b74432de6cad5870fb87b4979c32eb1`; clang 21.1.8 cross x86_64 + current upstream PRX set | Not canonical; differs from the historical artifact by compiler and plugin-set drift; regenerate with `bash build.sh` |
| Exact Okage eboot/GOT artifact | External, not present | No local hash | Required to validate the documented GOT anchor; do not fabricate or substitute |
| Retail kernel/eboot 13.52 | External, not present | No local hash | Critical missing artifact for direct validation of kernel offsets |
| Shell module images | External, not present | No local hash | Required separately for ShellCore/ShellUI/RemotePlay patch-site validation |

## SDK and generated build inputs

The submodule `third_party/ps4-payload-sdk` is pinned to commit `46efae910f3705e0171edea5b94e572d01bc00e8` from `Scene-Collective/ps4-payload-sdk`. Generated plugin include files are described in `installer/GENERATED_ASSETS.md`; the downloaded plugin ZIP is not committed by this inventory.

The submodule `third_party/henloader_lp` tracks `GoldHEN/henloader_lp` (Lapse 9.00–12.02 / Poops 9.00–13.00 loader). It is source-level reference infrastructure for payload loading on supported firmwares; it contains no 13.52 bytes and validates no kernel offset.

## Legal and reproducibility policy

This repository records hashes and analytical results for reproducibility. It does not grant redistribution rights for Sony firmware, proprietary dumps, external payloads, downloaded plugin archives or console images. A missing external artifact must be reported as missing; it must not be replaced by a guessed value, a different firmware, or a similarly named module.

Hash equality proves byte identity of the named artifact only. It does not prove firmware identity, module identity, runtime loading address, exploitability or hardware compatibility.
