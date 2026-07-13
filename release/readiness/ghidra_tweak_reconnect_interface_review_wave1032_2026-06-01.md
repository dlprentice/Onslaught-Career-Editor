# Ghidra Tweak Reconnect Interface Review Wave1032

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004530a0` → `CTweak__dtor_base_thunk_004530a0` (was `CTweak__dtor_unlink_from_static_list_004530a0`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete read-only static review
Date: 2026-06-01
Scope: `tweak-reconnect-interface-review-wave1032`

Wave1032 re-read the CTweak / CReconnectInterface / frontend handoff cluster from the Wave911 residual surface. The pass made no Ghidra mutation: no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state confirmed by Wave1032 | Fresh evidence |
| --- | --- | --- |
| `0x00527c90 CReconnectInterface__ctor` | `void * __thiscall CReconnectInterface__ctor(void * this, void * tweak_name, int default_index_one_based)` | Calls `CTweak__ctor_base`, stores the key pointer at `+0x08`, installs `0x005e4a80`, stores `default_index_one_based - 1` at `+0x0c`, clears `+0x10`, and returns with `RET 0x8`. |
| `0x00527d00 CReconnectInterface__VFunc_07_00527d00` | `void __thiscall CReconnectInterface__VFunc_07_00527d00(void * this, float tweak_value)` | Rounds the single float stack argument, stores it at `this+0x0c`, marks `this+0x10`, returns with `RET 0x4`, and is called by the `-landscape0/-landscape1/-landscape2` parser paths. |
| `0x00528690 CTweak__ctor_base` | `void * __thiscall CTweak__ctor_base(void * this, void * callback_context)` | Installs the base purecall table, stores callback context at `+0x08`, links the object into `DAT_0089c018` through `+0x04`, and returns `this`. |
| `0x005286b0 CTweak__dtor_base` | `void __fastcall CTweak__dtor_base(void * this)` | Resets the base vtable and unlinks the object from `DAT_0089c018`; `0x004530a0 CTweak__dtor_base_thunk_004530a0` remains a one-instruction thunk to this body. |
| `0x00528b20 CTweakInt_SetNumViewpoints__ctor` | `void * __thiscall CTweakInt_SetNumViewpoints__ctor(void * this, void * callback_context, int initial_value)` | Base-list setup followed by `PTR_CEngine__SetNumViewpoints_005e4aa4` installation and `initial_value` storage at `+0x0c`. |

Context evidence:

- `0x00527c50 CFrontEnd__AdvanceStateAndRelinquishControl` still advances state `1 -> 2`, relinquishes a controller in state `3`, clears the state, returns true, and consumes two explicit stack arguments with `RET 0x8`.
- `0x0054d4ac` is intentionally not a standalone function. The instruction-window export places it inside `0x0054d3f0 CDXMeshVB__ReleaseResources`; the following static constructor stubs at `0x0054d4dc` and `0x0054d50c` call `CReconnectInterface__ctor`.
- `0x005e4a80` is a mixed CReconnectInterface table: slot 0 points at `CReconnectInterface__VFunc_07_00527d00`, but adjacent entries include zero/float/data values. This supports preserving the bounded `VFunc_07` label rather than over-promoting a source-style virtual name.
- `0x005e4a94` and `0x005e4aa4` show the adjacent CTweak-style table/function-pointer context, including `CRT__Purecall_0055df1f`, `CVar__SetValueRounded`, and `CEngine__SetNumViewpoints`.

Evidence counts:

- Primary exports: 5 metadata rows, 5 tag rows, 15 xref rows, 58 body-instruction rows, and 5 decompile rows.
- Context exports: 3 metadata rows, 3 tag rows, 53 xref rows, 19 body-instruction rows, and 3 decompile rows, with the single intentional missing context function at `0x0054d4ac`.
- Xref-site windows: 13 call-site targets, 273 around-instruction rows, missing=0.
- Vtable/table windows: 3 table addresses and 24 rows.
- String/data checks for `0x00618938`, `0x00618988`, `0x006189d8`, `0x00618a08`, and `0x00618a38` produced empty C-string payloads, reinforcing that the mixed table is not a simple string/name table.
- Queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave911 focused re-audit progress after Wave1032: `631/1408 = 44.82%`; expanded static surface progress: `860/1493 = 57.60%`; Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-043550_post_wave1032_tweak_reconnect_interface_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The selected CTweak and CReconnectInterface rows still have coherent saved names, signatures, comments, tags, xrefs, instruction bodies, and decompile output.
- The `CReconnectInterface__VFunc_07_00527d00` evidence is strong enough for a bounded setter label and signature, but not strong enough for a more specific source-style virtual name.
- The `0x0054d4ac` stale context address is mid-function inside `CDXMeshVB__ReleaseResources`, not an unmodeled standalone target.

What remains unproven:

- Exact source symbol identity for `CReconnectInterface__VFunc_07_00527d00`.
- Concrete CTweak/CReconnectInterface layouts and table schemas.
- Runtime frontend reconnect, landscape-detail, viewpoint, tweak registration, or tweak cleanup behavior.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1032; tweak-reconnect-interface-review-wave1032; 0x00527c90 CReconnectInterface__ctor; 0x00527d00 CReconnectInterface__VFunc_07_00527d00; 0x00528690 CTweak__ctor_base; 0x005286b0 CTweak__dtor_base; 0x00528b20 CTweakInt_SetNumViewpoints__ctor; 0x00527c50 CFrontEnd__AdvanceStateAndRelinquishControl; 0x004530a0 CTweak__dtor_base_thunk_004530a0; 0x0054d4ac; 631/1408 = 44.82%; 860/1493 = 57.60%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-043550_post_wave1032_tweak_reconnect_interface_review_verified; no mutation.
