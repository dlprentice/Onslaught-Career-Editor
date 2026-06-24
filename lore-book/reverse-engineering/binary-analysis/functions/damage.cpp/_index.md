# damage.cpp

> Damage system functions from `BEA.exe` - static retail evidence for damage texture/table helpers.

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.


**Debug path string**: `C:\dev\ONSLAUGHT2\damage.cpp` at `0x006282dc`

## Wave1146 Current-Risk Recheck

Wave1146 (`wave1146-mixed-engine-score20-current-risk-review`) re-read the mixed CDamage/CConsole/CDebugMarkers/CEngine score20 current-risk slice with fresh Ghidra exports: damage sentinel, console status-history, debug-marker shutdown, and engine resource/view/light helpers. It accounts for `8 current-risk rows`, moves Wave1108 current focused accounting to `306/1179 = 25.95%`, keeps static closure at `6411/6411 = 100.00%` with `0 / 0 / 0` debt, and verified backup `G:\GhidraBackups\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified`; previous completed backup `G:\GhidraBackups\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified`. This was a read-only review with no mutation and no Codex subagent; runtime behavior, exact layouts, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1146; wave1146-mixed-engine-score20-current-risk-review; 306/1179 = 25.95%; 8 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 873; current risk candidates: 6166; mixed CDamage/CConsole/CDebugMarkers/CEngine score20 current-risk review; fresh Ghidra export; damage sentinel; console status-history; debug-marker shutdown; engine resource/view/light helpers; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CDamage__ctor_clear_head_and_init_flag; CConsole__ResetStatusHistoryBuffer; CDebugMarkers__Shutdown; CEngine__InitResources; CEngine__LoadAllNamedMeshes; CEngine__GetViewMatrixFromCamera; CEngine__ResetPos; CEngine__SetupLights; G:\GhidraBackups\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

The damage-row anchor is `0x00440b70 CDamage__ctor_clear_head_and_init_flag`: fresh metadata, tag, xref, instruction, and decompile exports preserve the damage sentinel read-back at `+0x1588c` and the `CDamage__Init` relationship.

## Functions

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x00440b70 | CDamage__ctor_clear_head_and_init_flag | SAVED | Wave 364 owner correction from stale `CUnitAI__ResetPrimaryAndTailSentinels`; clears damage-object head and initializes the `+0x1588c` flag/sentinel before `CDamage__Init`. |
| 0x00440b90 | CDamage__Init | SAVED | Initializes damage tables and the default damage texture context. |
| 0x00440c00 | CDamage__FreeOwnedDamageObjects | SAVED | Releases nested owned damage-object pointers and nulls them. |
| 0x00440c40 | CDamage__ResetDamageTables | SAVED | Clears damage lookup/work tables and restores default runtime flags. |
| 0x00440c70 | CDamage__LoadDamageTexture | SAVED | Loads and processes the damage texture through a 12-byte texture-info record. |
| 0x00440eb0 | CDamage__InsertCellEntry | SAVED | Inserts a damage-grid cell entry; four stack arguments plus ECX receiver. |
| 0x00440f80 | CDamage__RemoveCellEntryByCoords | SAVED | Removes a damage-grid cell entry by coordinates; three stack arguments plus ECX receiver. |
| 0x00441000 | CDamage__CreateTextureBuffer | SAVED | Creates/allows the texture-buffer context from chunk-reader input. |

## Wave996 Residual Review

Wave996 (`cdamage-residual-review-wave996`) re-reviewed the Wave911-anchored `0x00440b70 CDamage__ctor_clear_head_and_init_flag` candidate plus the adjacent Wave346 `CDamage` table/texture/grid helper island. Fresh read-only exports matched the already-saved Wave346/Wave364 evidence, so no Ghidra mutation, rename, signature change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation was needed.

Read-back anchors include `0x00440b90 CDamage__Init`, `0x00440c70 CDamage__LoadDamageTexture`, `0x00440eb0 CDamage__InsertCellEntry`, `0x00440f80 CDamage__RemoveCellEntryByCoords`, `0x00441000 CDamage__CreateTextureBuffer`, and context `0x0044a130 CEngine__InitDamageSystem`. Exports verified `9` metadata rows, `9` tag rows, `9` xref rows, `407` body-instruction rows, and `9` decompile rows. Wave911 focused re-audit progress remains `464/1408 = 32.95%`; expanded static surface progress is `576/1478 = 38.97%`; queue closure remains `6222/6222 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260531-081328_post_wave996_cdamage_residual_review_verified`.

Runtime terrain damage behavior, runtime damage/decal texture rendering behavior, exact `CDamage`, texture-info, damage-cell, `CEngine`, or landscape layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

## Wave995 Residual Recheck

Wave995 early high-signal residual review (`early-high-signal-residual-review-wave995`) re-read `0x00440b70 CDamage__ctor_clear_head_and_init_flag` as context for the adjacent Wave364 residual cluster. The saved damage owner correction still holds; the same Wave995 pass corrected `0x00441e50 CDebugMarkers__Shutdown` stale Wave364 allocator/free wording to `CDXMemoryManager__Free` at `0x00549220` with memory-manager context `0x009c3df0`. Wave911 focused re-audit progress is `464/1408 = 32.95%`; expanded static surface progress is `569/1478 = 38.50%`; queue closure remains `6222/6222 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260531-073718_post_wave995_early_high_signal_residual_review_verified`. Runtime marker behavior, exact debug-marker manager layout, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

## Wave 364 Early Owner Correction

Wave 364 corrected `0x00440b70` from the stale `CUnitAI__ResetPrimaryAndTailSentinels` label to `CDamage__ctor_clear_head_and_init_flag` after source/debug-path clustering, caller context, metadata, decompile, xref, instruction, and tag read-back.

The saved signature is `void __fastcall CDamage__ctor_clear_head_and_init_flag(void * damage)`. The checked body clears the damage-object head and initializes the `+0x1588c` flag/sentinel used by the adjacent damage initialization path. The prior UnitAI owner label is superseded and should not be used as evidence for UnitAI state.

## Wave 346 Signature Read-Back

Wave 346 saved and read back the current `CDamage` signatures/comments/tags after metadata, decompile, xref, instruction, and tag review:

- `CDamage__Init`: `void __fastcall CDamage__Init(void * damage)`
- `CDamage__FreeOwnedDamageObjects`: `void __fastcall CDamage__FreeOwnedDamageObjects(void * damage)`
- `CDamage__ResetDamageTables`: `void __fastcall CDamage__ResetDamageTables(void * damage)`
- `CDamage__LoadDamageTexture`: `void __thiscall CDamage__LoadDamageTexture(void * this, char * tgaPath)`
- `CDamage__InsertCellEntry`: `int __thiscall CDamage__InsertCellEntry(void * this, int cellIndex, int coordX, int coordY, int stampValue)`
- `CDamage__RemoveCellEntryByCoords`: `void __thiscall CDamage__RemoveCellEntryByCoords(void * this, int cellIndex, int coordX, int coordY)`
- `CDamage__CreateTextureBuffer`: `void __thiscall CDamage__CreateTextureBuffer(void * this, void * chunkReader)`

The important Ghidra nuance from this wave is that `__thiscall` signatures need the ECX receiver named `this`; otherwise Ghidra inserts a hidden receiver and shifts the intended first semantic parameter onto the stack. For `CDamage__LoadDamageTexture`, ECX/`this` is the 12-byte texture-info record, not the full `CDamage` object. The semantic distinction is recorded in the saved comment rather than by renaming the ECX parameter away from `this`.

## Behavior Summary

### CDamage__Init (0x00440b90)

- Initializes damage runtime state.
- Allocates/uses a texture-info context and loads `"data/textures/mixers/damage0.tga"`.
- Clears the large damage table region and seeds default runtime flags.
- Exact concrete `CDamage` layout remains unproven.

### CDamage__FreeOwnedDamageObjects (0x00440c00)

- Releases nested owned damage-object pointers when present.
- Nulls the owning slots after release.
- Used as cleanup before reinitialization/destruction-style paths.

### CDamage__ResetDamageTables (0x00440c40)

- Clears the large damage lookup/work tables.
- Restores default runtime flags after the table reset.
- The table sizes and offsets are static decompile evidence, not final structure typing.

### CDamage__LoadDamageTexture (0x00440c70)

- Loads a TGA file into a local buffer and derives mipmap level from texture size.
- Allocates texture pixel storage using lookup tables near `DAT_0062829c` / `DAT_00628298`.
- Converts source pixels into the damage texture buffer and generates lower mip levels.
- Post-processes pixel values for the damage/decal texture representation.

### CDamage__InsertCellEntry (0x00440eb0)

- Inserts a damage-grid cell entry into the per-cell bookkeeping structure.
- Final saved signature has four stack arguments and `ret 0x10` evidence.

### CDamage__RemoveCellEntryByCoords (0x00440f80)

- Removes or clears a damage-grid cell entry by cell index and coordinates.
- Final saved signature has three stack arguments and `ret 0x0c` evidence.
- The older four-stack-argument interpretation was stale.

### CDamage__CreateTextureBuffer (0x00441000)

- Creates the texture-buffer context from chunk-reader input.
- Allocates or prepares the backing pixel buffer and marks the texture context initialized.

## Partial Data Shapes

The current evidence supports only partial, proof-bounded data shapes:

| Structure | Evidence |
|-----------|----------|
| Damage system object | Owns table regions, runtime flags, and texture-context pointers, but concrete full layout is not certified. |
| Texture-info record | 12-byte record used by `CDamage__LoadDamageTexture`; contains pixel-buffer pointer and size/mipmap metadata. |
| Damage cell entry | Grid bookkeeping entry inserted/removed by `CDamage__InsertCellEntry` and `CDamage__RemoveCellEntryByCoords`; concrete struct layout remains open. |

## Related Strings

- `"data/textures/mixers/damage0.tga"` at `0x006282b8` - default damage texture.

## Claim Boundary

This page records saved static Ghidra evidence only. Runtime damage rendering, decal visual parity, exact source identity, concrete layout recovery, local/type recovery, BEA launch, game patching, and rebuild parity remain unproven.
