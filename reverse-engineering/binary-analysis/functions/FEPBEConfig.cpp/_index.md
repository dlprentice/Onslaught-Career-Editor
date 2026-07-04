# FEPBEConfig.cpp Functions

> Source File: FEPBEConfig.cpp | Binary: BEA.exe
> Debug Path: 0x00628fac (`[maintainer-local-source-export-root]\FEPBEConfig.cpp`)
> RTTI: `.?AVCFEPBEConfig@@` at 0x00629c58
> Current saved-Ghidra wave: Wave 999 (`2026-05-31` read-only review; Wave367/Wave403 saved corrections preserved)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`CFEPBEConfig` is the frontend page for Battle Engine configuration. The current saved retail-binary evidence covers the profile/config list helpers, weapon property/sound helpers, selected-entry global-id helper, init/load/cleanup lifecycle, projection/render helpers, and the core `CFEPBEConfig` vtable slots used by update, input, render-pre-common, render, reset/timestamp, and load paths.

The older note that described `0x0044fa93` as an unrecognized init region is superseded. Fresh byte/prologue inspection plus saved Ghidra body repair show the function boundary starts at `0x0044fa90`, the SEH prologue before the `beconf::init() 0-5` trace strings. Ghidra now has a saved `CFEPBEConfig__Init` function body covering `0x0044fa90-0x0044fd9f`.

Wave1147 (`wave1147-frontend-game-shell-score20-current-risk-review`) re-read `0x00451a40 FEPBEConfig__FindSelectedEntryByGlobalId` as part of the frontend/game shell score20 current-risk review. Fresh Ghidra exports found the saved name/signature/comment static-consistent with no mutation to this row. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified`.

Wave1197 (`wave1197-fepbeconfig-frontend-residual-current-risk-review`) saved comment/tag normalization for `4 FEPBEConfig/frontend residual score15-16 current-risk rows`: `CFEPBEConfig__Init`, `CFEPMultiplayerStart__SetConfigDescriptionByIndex`, `CFEPBEConfig__PlayWeaponSound`, and `CFEPBEConfig__PlayWeaponSoundAlt`. fresh Ghidra export evidence verified `4 xref rows`, `860 instruction rows`, and `4 decompile rows`; dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0`, `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0`, and final dry updated=0 skipped=4. No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer. Wave1108 current focused accounting is `885/1179 = 75.06%`; current risk candidates: 6166; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 294; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; wave1108-current-risk-rank. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-211310_post_wave1197_fepbeconfig_frontend_residual_current_risk_review_verified`. Static target: rebuild-grade static contracts and rebuild-grade specification for no noticeable difference; runtime frontend/config loading behavior, runtime frontend audio/text behavior, exact layouts, source identity, patching, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Functions

| Address | Saved name | Signature | Purpose |
| --- | --- | --- | --- |
| `0x0044eab0` | `CFEPMultiplayerStart__GetConfigIdByIndex` | `int __cdecl ...(int config_index)` | Walks the selected config list and returns the config id at `config_index`. |
| `0x0044eb30` | `CFEPMultiplayerStart__SetConfigDescriptionByIndex` | `void __cdecl ...(int config_index)` | Resolves config name/type text with `Unknown Configuration` fallback. |
| `0x0044ecf0` | `CFEPMultiplayerStart__GetConfigCount` | `int __cdecl ...(void)` | Returns selected BattleEngine profile config count. |
| `0x0044ed40` | `CFEPMultiplayerStart__LookupProfileField5CBySelectionIndex` | `int __cdecl ...(int config_index)` | Resolves selected config name and returns matched record field `+0x5c`. |
| `0x0044eea0` | `CFEPMultiplayerStart__LookupProfileField4CPlusFlagBySelectionIndex` | `int __cdecl ...(int config_index)` | Resolves selected config name and returns field `+0x4c` adjusted by flag `+0x60`. |
| `0x0044f030` | `CFEPBEConfig__GetWeaponProperty` | `int __cdecl ...(void * config, int weapon_index, int property_index)` | Primary weapon property lookup returning weapon-record slots `+0x10/+0x11/+0x12`. |
| `0x0044f300` | `CFEPBEConfig__GetWeaponPropertyAlt` | `int __cdecl ...(void * config, int weapon_index, int property_index)` | Alternate weapon property lookup through matched config alternate list `+0x50/+0x58`. |
| `0x0044f530` | `CFEPBEConfig__PlayWeaponSound` | `void __cdecl ...(void * config, int weapon_index)` | Primary weapon sound/text helper using weapon-record field `+0x0f`, with `Unknown Weapon` fallback. |
| `0x0044f830` | `CFEPBEConfig__PlayWeaponSoundAlt` | `void __cdecl ...(void * config, int weapon_index)` | Alternate weapon sound/text helper using the alternate weapon list. |
| `0x0044fa90` | `CFEPBEConfig__Init` | `void __thiscall ...(void * this)` | Corrected init boundary and body; starts at the SEH prologue before `beconf::init() 0-5`. |
| `0x0044fda0` | `CFEPBEConfig__Cleanup` | `void __thiscall ...(void * this)` | Frees owned frontend/config-entry storage and delegates per-entry cleanup. |
| `0x0044fdf0` | `CFEPBEConfig__CleanupSquads` | `void __thiscall ...(void * this)` | Clears a config entry squad/name pointer set at `+0x14`. |
| `0x0044fe70` | `CFEPBEConfig__Load` | `void __thiscall ...(void * this, void * mem_buffer)` | Loads one BattleEngine config entry from a memory buffer. |
| `0x00450010` | `CFEPBEConfig__UpdateTransitionTimers` | `void __thiscall ...(void * this, int menu_state)` | Vtable slot 1; transition/timer state update and zero-state callback context. |
| `0x00450090` | `CFEPBEConfig__ButtonPressed` | `void __thiscall ...(void * this, int button, int player_index)` | Vtable slot 2; frontend button/action dispatch and selected config index changes. |
| `0x00450390` | `CFEPBEConfig__RenderPreCommon` | `void __thiscall ...(void * this, float transition, int dest)` | Vtable slot 3; common selection marker render path. |
| `0x00450400` | `CFEPBEConfig__PushProjectionMatrixForRender` | `void __cdecl ...(void)` | Saves active projection matrix and installs CFEPBEConfig projection values. |
| `0x00450440` | `CFEPBEConfig__PopProjectionMatrixAfterRender` | `void __cdecl ...(void)` | Restores saved projection matrix and marks projection state dirty. |
| `0x00450460` | `CFEPMultiplayerStart__RenderConfigPipRow` | `void __cdecl ...(float x, float y, float rating, uint argb)` | Renders rating pips from a rounded `1-5` count, color bands, alpha, and surface calls. |
| `0x004505b0` | `CFEPBEConfig__Render` | `void __thiscall ...(void * this, float transition, int dest)` | Vtable slot 4; BattleEngine config page render body. |
| `0x00451930` | `CFEPBEConfig__FindEntryByName` | `void * __cdecl ...(char * entry_name)` | Linear lookup over the global config/profile list by record name at `+0xa8`. |
| `0x004519c0` | `CFEPBEConfig__ResetTimestampAndModeFlag` | `void __thiscall ...(void * this)` | Vtable slot 5; stores platform time, clears a mode flag, and conditionally re-enables it. |
| `0x00451a40` | `FEPBEConfig__FindSelectedEntryByGlobalId` | `int * __fastcall ...(void * list_state)` | Selected/global-id entry lookup over `list_state`; Wave403 supersedes the stale `CUnitAI__FindLinkedNodeByGlobalId` owner label. |

**Total: 23 saved targets.**

## Wave999 FEPBEConfig Helper Review (2026-05-31)

Wave999 (`fepbeconfig-helper-review-wave999`) re-reviewed the Wave911 risk-ranked FEPBEConfig / FEPMultiplayerStart helper island around the prior Wave367 boundary/signature work and Wave403 selected-entry owner correction. Fresh read-only metadata, tag, xref, instruction, and decompile exports matched the saved evidence, so no Ghidra mutation, rename, signature change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation was needed.

Primary checked anchors: `0x0044eb30 CFEPMultiplayerStart__SetConfigDescriptionByIndex`, `0x0044f530 CFEPBEConfig__PlayWeaponSound`, `0x0044f830 CFEPBEConfig__PlayWeaponSoundAlt`, and `0x00451a40 FEPBEConfig__FindSelectedEntryByGlobalId`. Context rows: `0x0044eab0 CFEPMultiplayerStart__GetConfigIdByIndex`, `0x0044ecf0 CFEPMultiplayerStart__GetConfigCount`, `0x0044f030 CFEPBEConfig__GetWeaponProperty`, `0x0044f300 CFEPBEConfig__GetWeaponPropertyAlt`, `0x00450090 CFEPBEConfig__ButtonPressed`, `0x004505b0 CFEPBEConfig__Render`, and `0x00451930 CFEPBEConfig__FindEntryByName`.

Fresh evidence verified `11` metadata rows, `11` tag rows, `31` xref rows, `3001` body-instruction rows, and `11` decompile rows. Existing Wave367/Wave403 probes still pass. Queue closure remains `6222/6222 = 100.00%`; Wave911 focused re-audit progress remains `467/1408 = 33.17%`; expanded static surface progress is `596/1478 = 40.32%`; Wave911 top-500 risk-ranked coverage is `343/500 = 68.60%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-094628_post_wave999_fepbeconfig_helper_review_verified`.

Boundary: this proves static helper coherence for the selected frontend config rows only. Exact Stuart source-body identity, concrete FEPBEConfig/config-entry/weapon-record/list layouts, runtime frontend menu behavior, runtime audio/text presentation behavior, BEA patching, and rebuild parity remain separate proof.

## Vtable Snapshot

| Slot | Pointer | Saved function |
| ---: | --- | --- |
| 0 | `0x0044fda0` | `CFEPBEConfig__Cleanup` |
| 1 | `0x00450010` | `CFEPBEConfig__UpdateTransitionTimers` |
| 2 | `0x00450090` | `CFEPBEConfig__ButtonPressed` |
| 3 | `0x00450390` | `CFEPBEConfig__RenderPreCommon` |
| 4 | `0x004505b0` | `CFEPBEConfig__Render` |
| 5 | `0x004519c0` | `CFEPBEConfig__ResetTimestampAndModeFlag` |
| 6 | `0x00452b60` | `CFrontEndPage__Process_NoOp` |
| 7 | `0x0040c640` | `DebugTrace` |
| 8 | `0x0044fe70` | `CFEPBEConfig__Load` |

Slots after the `CFEPBEConfig` load entry run into adjacent RTTI/vtable data and other frontend class entries. Do not treat `0x00613740`, `0x00452b00`, or `0x00452b30` as additional `CFEPBEConfig` slots without a separate owner/type proof.

## Init Boundary Correction

The current saved init function is:

```text
0x0044fa90 CFEPBEConfig__Init
body: 0x0044fa90-0x0044fd9f
```

The old `0x0044fa93` note was a mid-prologue address. During Wave 367, an intermediate Ghidra state had function metadata but an empty function body, which made decompile read-back fail. The repair flow decoded the listing and explicitly set the function body; final read-back verified metadata, instructions, tags, and decompile all cleanly.

## Debug Strings

| Address | String | Usage |
| --- | --- | --- |
| `0x00628ec0` | `Unknown Weapon` | Fallback when weapon lookup fails. |
| `0x00628ef0` | `beconf::init() 5\n` | Init trace stage 5. |
| `0x00628f10` | `beconf::init() 4\n` | Init trace stage 4. |
| `0x00628f24` | `beconf::init() 2\n` | Init trace stage 2. |
| `0x00628f50` | `beconf::init() 1\n` | Init trace stage 1. |
| `0x00628f64` | `beconf::init() 3\n` | Init trace stage 3. |
| `0x00628fac` | `[maintainer-local-source-export-root]\FEPBEConfig.cpp` | Debug source path. |
| `0x00628fd0` | `beconf::init() 0\n` | Init trace stage 0. |

## Wave750 Unwind Cleanup Evidence (2026-05-22)

Wave750 saved four FEPBEConfig-adjacent compiler-generated SEH unwind cleanup callbacks with the `unwind-continuation-wave750` and `wave750-readback-verified` tags. All are static retail Ghidra evidence only, saved as `void __cdecl Unwind@...(void)`, with no renames, no function-boundary changes, and no executable-byte changes.

| Address | Evidence |
| --- | --- |
| `0x005d25a0 Unwind@005d25a0` | DATA scope-table xref `0x0061b414`; calls `CDXMemBuffer__dtor_base` on stack-local memory buffer `EBP-0x208`. |
| `0x005d25c0 Unwind@005d25c0` | DATA scope-table xref `0x0061b43c`; calls `CSPtrSet__Clear` on `(*(EBP-0x10))+0x14`. |
| `0x005d25e0 Unwind@005d25e0` | DATA scope-table xref `0x0061b464`; calls `OID__FreeObject_Callback` for FEPBEConfig.cpp debug path `0x00628fac`, line `0x80`, allocation/type value `0x18f`. |
| `0x005d2610 Unwind@005d2610` | DATA scope-table xref `0x0061b48c`; jumps to `CMenuItem__RestoreCompactVTable` with the menu item pointer at `*(EBP-0x10)`. |

Read-back backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-193422_post_wave750_unwind_continuation_verified`. Exact parent source-body identity, runtime FEPBEConfig cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Claim Boundary

This page records saved static retail Ghidra evidence: boundaries, names, signatures, function comments, tags, xrefs, vtable slots, instructions, and decompile read-back for the listed targets. It does not prove exact Stuart-source method identities, concrete class/record layouts, local variable/type recovery, runtime frontend/config/render/input behavior, BEA launch behavior, game patching, or rebuild parity.
