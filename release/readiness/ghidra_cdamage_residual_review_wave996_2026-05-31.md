# Ghidra CDamage Residual Review Wave996 Readiness Note

Status: complete read-only static read-back evidence
Date: 2026-05-31
Scope: `cdamage-residual-review-wave996`

Wave996 re-reviewed the Wave911-anchored `0x00440b70 CDamage__ctor_clear_head_and_init_flag` candidate plus the adjacent Wave346 `CDamage` table/texture/grid helper island. Fresh read-only metadata, tag, xref, instruction, and decompile exports matched the already-saved Wave346/Wave364 evidence, so this wave made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary targets and context:

| Address | Read-back evidence |
| --- | --- |
| `0x00440b70 CDamage__ctor_clear_head_and_init_flag` | Wave364 owner correction still holds; clears the damage-object head and `+0x1588c` init/sentinel field used by `CDamage__Init`. |
| `0x00440b90 CDamage__Init` | Calls `CDamage__LoadDamageTexture` for `data/textures/mixers/damage0.tga`, clears the observed damage table/lookup arrays, and seeds flags/counters. |
| `0x00440c00 CDamage__FreeOwnedDamageObjects` | Frees nested texture state via `CDXMemoryManager__Free` at `0x00549220` with context `0x009c3df0`, then clears stored pointers. |
| `0x00440c40 CDamage__ResetDamageTables` | Clears damage lookup/work tables and restores active/free-list flags. |
| `0x00440c70 CDamage__LoadDamageTexture` | Saved signature remains `void __thiscall CDamage__LoadDamageTexture(void * this, char * tgaPath)`; ECX/`this` is the 12-byte texture-info record, not the full `CDamage` object. |
| `0x00440eb0 CDamage__InsertCellEntry` | Saved signature remains four stack arguments plus ECX receiver; instruction read-back includes `RET 0x10`. |
| `0x00440f80 CDamage__RemoveCellEntryByCoords` | Saved signature remains three stack arguments plus ECX receiver; instruction read-back includes `RET 0x0c`, so the older fourth stack argument remains stale. |
| `0x00441000 CDamage__CreateTextureBuffer` | Creates the texture-info buffer from a `CChunkReader` stream and marks damage texture state initialized. |
| `0x0044a130 CEngine__InitDamageSystem` | Context anchor; calls `CDamage__ResetDamageTables` from the landscape/tree-shadow damage init bridge. |

Fresh read-back evidence:

- Exports: `9` metadata rows, `9` tag rows, `9` xref rows, `407` body-instruction rows, and `9` decompile rows.
- Xrefs confirm `CDXLandscape__Init -> CDamage__Init`, `CLTShell__ShutdownRuntimeAndReleaseResources -> CDamage__FreeOwnedDamageObjects`, `CEngine__InitDamageSystem -> CDamage__ResetDamageTables`, `CDamage__Init -> CDamage__LoadDamageTexture`, `CDXEngine__ApplyLandscapeDamageStamp -> CDamage__InsertCellEntry` and `CDamage__RemoveCellEntryByCoords`, `CResourceAccumulator__ReadResourceFile -> CDamage__CreateTextureBuffer`, and `CGame__RestartLoopRunLevel -> CEngine__InitDamageSystem`.
- Queue closure remains `6222/6222 = 100.00%`.
- Wave911 focused re-audit progress remains `464/1408 = 32.95%` because the Wave911 candidate anchor was already counted by Wave995 context.
- Expanded static surface progress is now `576/1478 = 38.97%` after seven adjacent `CDamage` helpers received dedicated post-100 read-only review.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-081328_post_wave996_cdamage_residual_review_verified`, `19` files, `173869959` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave996; `cdamage-residual-review-wave996`; `0x00440b70 CDamage__ctor_clear_head_and_init_flag`; `0x00440b90 CDamage__Init`; `0x00440c70 CDamage__LoadDamageTexture`; `0x00440eb0 CDamage__InsertCellEntry`; `0x00440f80 CDamage__RemoveCellEntryByCoords`; `0x00441000 CDamage__CreateTextureBuffer`; `0x0044a130 CEngine__InitDamageSystem`; `464/1408 = 32.95%`; `576/1478 = 38.97%`; `6222/6222 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260531-081328_post_wave996_cdamage_residual_review_verified`; no mutation.

What this proves:

- The reviewed rows exist in the saved Ghidra project with the expected names, signatures, comments, and tags.
- The Wave346 calling-convention nuance still holds for the `CDamage` helpers.
- The Wave364 owner correction for `0x00440b70` still holds.
- The fresh xrefs preserve the terrain-damage, texture-buffer, landscape, and engine-init context.

What remains unproven:

- Runtime terrain damage behavior.
- Runtime damage/decal texture rendering behavior.
- Exact `CDamage`, texture-info, damage-cell, `CEngine`, or landscape layouts.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
