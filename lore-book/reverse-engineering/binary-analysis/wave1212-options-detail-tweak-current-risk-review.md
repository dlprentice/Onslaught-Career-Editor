# Wave1212 Options Detail/Tweak Current-Risk Review

Status: complete static current-risk read-only review; later validation passed by current-risk closeout gates
Date: 2026-06-07
Tag: `wave1212-options-detail-tweak-current-risk-review`

Wave1212 re-read `9 options/detail/tweak current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This is a read-only review with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt. Active current-risk progress is `1119/1179 = 94.91%`; remaining active focused work: 60. The legacy additive counter is deprecated (`1150/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1127; live regenerated current focused candidates: 1127; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction.

## Targets

| Address | Function | Static evidence |
| --- | --- | --- |
| `0x004ceef0` | `LandscapeDetail_SetLevel` | COMPUTED_CALL xref `0x004cead0`; writes landscape detail globals `0x009c7c54` and `0x009c7c56` from selected detail level. |
| `0x004cef30` | `LandscapeDetail_GetLevel` | COMPUTED_CALL xref `0x004ceac6`; returns level `2` when high-detail global is set, otherwise returns low-detail boolean global. |
| `0x004cef50` | `CTreeDetail__SetQualityLevel` | COMPUTED_CALL xref `0x004ceb06`; forwards selected quality to `CRTMesh__SetQualityLevel` at `0x004dd6b0`. |
| `0x004cf030` | `CMouseSensitivityMenuItem__scalar_deleting_dtor` | DATA xref `0x005de6b8`; scalar-deleting destructor path calls `CMenuItem__Destructor_Thunk` and frees through `CDXMemoryManager__Free` when flags bit 0 is set. |
| `0x004cf8e0` | `CMultiSample__GetSampleCountLabel` | DATA xref `0x005de258`; resolves MSAA labels through active display-profile capability bits and fallback `Localization__GetStringById(0xd4)`. |
| `0x00527d00` | `CReconnectInterface__VFunc_07_00527d00` | CALL xref `0x00423f45` from `CLIParams__ParseCommandLine`; `-landscape0/-landscape1/-landscape2` paths pass float values that the setter rounds and marks explicit. |
| `0x00528690` | `CTweak__ctor_base` | CALL xref `0x00527c99`; links the tweak record into the global tweak list `DAT_0089c018`. |
| `0x005286b0` | `CTweak__dtor_base` | JUMP xref `0x004530a0`; unlinks the tweak record from global tweak list `DAT_0089c018`. |
| `0x004530a0` | `CTweak__dtor_base_thunk_004530a0` | CALL xref `0x00554f75`; one-instruction jump thunk to `CTweak__dtor_base`. |

Context exports covered `PauseMenu__Init`, `CLIParams__ParseCommandLine`, `CReconnectInterface__ctor`, `CVideoDetailLevel__GetCurrentPresetFromItems`, `CRTMesh__SetQualityLevel`, `CMenuItem__Destructor_Thunk`, and `CDXMemoryManager__Free`.

Fresh Ghidra export counts: `9` metadata rows, `9` tag rows, `64 xref rows`, `175 instruction rows`, and `9 decompile rows`. Context export counts: `7` metadata rows, `7` tag rows, `869 context xref rows`, `1887 context instruction rows`, and `7 context decompile rows`.

Codex read-only consults used; no Cursor/Composer. The central accounting paths are `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, and `wave1108-current-risk-rank`.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-065722_post_wave1212_options_detail_tweak_current_risk_review_verified` (`19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0`).

Boundary: this wave strengthens rebuild-grade static contracts and the rebuild-grade specification aiming at no noticeable difference. Runtime options-menu behavior, runtime CLI/tweak behavior, runtime device behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
