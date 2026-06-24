
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

# FEPWingmen.cpp

Front End Page for wingmen/ally selection screen. Handles the UI for selecting wingmen before missions.

**Debug Path String:** `C:\dev\ONSLAUGHT2\FEPWingmen.cpp`
**String Address:** `0x0063fd4c`

Wave566 status: saved static Ghidra evidence, not runtime proof. `FEPWingmen.cpp` is not present in `references/Onslaught`, so the current comments/tags are retail-binary-first and deliberately avoid `source-parity`.

Wave1045 (`frontend-vtable-boundary-wave1045`) recovered the four deferred `CFEPWingmen` vtable boundaries from vtable `0x005dba10`: `0x005216c0 CFEPWingmen__Init`, `0x00521d20 CFEPWingmen__ButtonPressed`, `0x00522160 CFEPWingmen__RenderPreCommon`, and `0x00522190 CFEPWingmen__Render`. Wave1051 (`fepwingmen-page-review-wave1051`) then re-read the full page, closed the stale `missing-boundary-deferred` wording/tag on `0x00521c80 CFEPWingmen__Update`, and normalized `0x005230e0 CFEPWingmen__FindCurrentLevelRecord` around the recovered ButtonPressed/Render callsites. Queue closure is `6246/6246 = 100.00%`; Wave911 focused progress remains `744/1408 = 52.84%`; expanded static surface progress is `1032/1509 = 68.39%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260601-150857_post_wave1051_fepwingmen_page_review_verified`. FEPWingmen.cpp source is absent from `references/Onslaught`, so the reviewed rows remain retail Ghidra/vtable evidence only.

## Functions Found

| Address | Name | Saved state | Purpose / evidence |
|---------|------|-------------|--------------------|
| `0x00521650` | `CFEPWingmen__GetWingmenCount` | `char CFEPWingmen__GetWingmenCount(void)` | Scans `DAT_0089da6c` / `DAT_0089da74` for current level `DAT_0089d94c`, then counts nonzero record slots `+0x04`, `+0x0c`, and `+0x08`. |
| `0x005216c0` | `CFEPWingmen__Init` | `int __fastcall CFEPWingmen__Init(void * this)` | Wave1045 vtable `0x005dba10` slot 0 boundary recovery; initializes Wingmen state fields, frontend thing resources, and list state. |
| `0x00521a60` | `CFEPWingmen__Destroy` | `void __fastcall CFEPWingmen__Destroy(void * this)` | Vtable `0x005dba10` slot 1 cleanup path; frees frontend thing pointers at `this+0x08/+0x0c/+0x10`, then drains the pointer set at `this+0x28`. Signature convention remains deferred. |
| `0x00521ae0` | `CFEPWingmen__Load` | `void __thiscall CFEPWingmen__Load(void * this, void * stream)` | Wave565 corrected the stale `__stdcall` signature. `RET 0x4`, `ECX` receiver storage, and stack stream use prove `this` plus one `stream` argument. |
| `0x00521c80` | `CFEPWingmen__Update` | `void __thiscall CFEPWingmen__Update(void * this, int state)` | Vtable slot 2 per-frame update; updates timer/fade fields and calls the shared spinner helper for live frontend thing slots. |
| `0x00521d20` | `CFEPWingmen__ButtonPressed` | `void __thiscall CFEPWingmen__ButtonPressed(void * this, int button, float val)` | Wave1045 vtable `0x005dba10` slot 3 boundary recovery; target of the `CFEPWingmen__Update` dev-mode vtable `+0x0c` path, dispatches frontend button ids and updates current-level state. |
| `0x00522160` | `CFEPWingmen__RenderPreCommon` | `void __stdcall CFEPWingmen__RenderPreCommon(float transition, int dest)` | Wave1045 vtable `0x005dba10` slot 4 boundary recovery; compact transition/pre-common render helper returning with `RET 0x8`. |
| `0x00522190` | `CFEPWingmen__Render` | `void __thiscall CFEPWingmen__Render(void * this, float transition, int dest)` | Wave1045 vtable `0x005dba10` slot 5 boundary recovery; render body calls `CFEPWingmen__FindCurrentLevelRecord`, text/render-surface helpers, and `CFrontEnd__RenderOverlayEffects`. |
| `0x005230e0` | `CFEPWingmen__FindCurrentLevelRecord` | `void * __thiscall CFEPWingmen__FindCurrentLevelRecord(void * this)` | Wave566 owner-corrected this from stale `CVBufTexture__FindListEntryByGlobalId89D94C`. Deferred FEPWingmen callsites pass `ECX=&DAT_0089da44`; the helper walks records from `this+0x28` / cursor `this+0x30` and returns the record whose first dword matches `DAT_0089d94c`. |
| `0x005230c0` | `CFEPWingmen__TransitionNotification` | `void __thiscall CFEPWingmen__TransitionNotification(void * this, int from_page)` | Wave565 renamed former `CFEPWingmen__VFunc_06_005230c0`. Vtable slot 6 plus matching frontend-page convention prove the transition-notification role; `from_page` is ignored. |
| `0x0046baf0` | `CFEPWingmen__UpdateSpinnerTransformAndPulse` | `void __thiscall CFEPWingmen__UpdateSpinnerTransformAndPulse(void * this)` | Shared frontend spinner transform/pulse helper called by `CFEPWingmen__Update`, `CFEPMultiplayerStart__Process`, and `CFEPBEConfig__UpdateTransitionTimers`. |

**Total:** 11 documented function objects after Wave1045. The formerly deferred vtable entries at slots 0, 3, 4, and 5 now have saved function boundaries.

## Vtable Evidence

Primary table starts at `0x005dba10`.

| Slot | Pointer | Status |
| ---: | --- | --- |
| 0 | `0x005216c0` | `CFEPWingmen__Init` |
| 1 | `0x00521a60` | `CFEPWingmen__Destroy` |
| 2 | `0x00521c80` | `CFEPWingmen__Update` |
| 3 | `0x00521d20` | `CFEPWingmen__ButtonPressed`; called from `CFEPWingmen__Update` dev-mode path via vtable `+0x0c`. |
| 4 | `0x00522160` | `CFEPWingmen__RenderPreCommon` |
| 5 | `0x00522190` | `CFEPWingmen__Render` |
| 6 | `0x005230c0` | `CFEPWingmen__TransitionNotification` |
| 7 | `0x00452b60` | `CFrontEndPage__Process_NoOp` |
| 8 | `0x0040c640` | `DebugTrace` |
| 9 | `0x00521ae0` | `CFEPWingmen__Load` |

Slot 10 points at `0x006139a8`, then the adjacent `CFEPBEConfig` table begins. Treat slot 10 as non-method/table metadata unless future evidence proves otherwise.

## Wave1045 Recovered Boundary Region

The range `0x005216c0 - 0x00521a5f` previously contained real FEPWingmen instructions without a Ghidra function object. Wave1045 recovered `0x005216c0 CFEPWingmen__Init`; it includes `FEPWingmen.cpp` debug-string xrefs:

- `0x00521708` pushes `0x0063fd4c` with line `0x37`.
- `0x005217cb` pushes `0x0063fd4c` with line `0xe7`.
- `0x0052188e` pushes `0x0063fd4c` with line `0xeb`.

Wave1045 also recovered `0x00521d20 CFEPWingmen__ButtonPressed`, `0x00522160 CFEPWingmen__RenderPreCommon`, and `0x00522190 CFEPWingmen__Render`. Post exports verified all four recovered rows plus the Goodies rows, and the vtable slot export now resolves the `0x005dba10` slot pointers as `OK`.

## Wave1045 Frontend Vtable Boundary Recovery

Wave1045 saved four `CFEPWingmen` function objects from vtable `0x005dba10` with the `frontend-vtable-boundary-wave1045` and `wave1045-readback-verified` tags. Post exports verified `8` metadata rows, `8` tag rows, `8` DATA xref rows, `3540` function-body instruction rows, `8` decompile rows, and `135` frontend vtable slot rows across Goodies and Wingmen. Wave911 focused progress remains `735/1408 = 52.20%`; expanded static surface progress is `985/1501 = 65.62%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260601-112809_post_wave1045_frontend_vtable_boundary_verified`.

This is static retail Ghidra/vtable evidence only. It does not prove runtime Wingmen menu/input/render behavior, exact button semantics, exact concrete `CFEPWingmen` or record layouts, exact source-body identity, BEA patching, gameplay outcomes, or rebuild parity.

## Wave1051 FEPWingmen Page Normalization

Wave1051 saved comment/tag normalization across the eleven documented `FEPWingmen.cpp` rows with the `fepwingmen-page-review-wave1051` and `wave1051-readback-verified` tags. It made no rename, signature change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation.

Fresh primary exports verified pre/post `11` metadata rows, `11` tag rows, `27` xref rows, `1818` function-body instruction rows, and `11` decompile rows. Context exports recorded `15` metadata/tag/decompile index rows with one expected missing context function at `0x0046a180`, `321` xref rows, `3472` instruction rows, and `14` dumped context decompile bodies. Vtable export verified `0x005dba10 CFEPWingmen_vtable` with `11` slots: slots 0-9 resolve to the expected page methods/shared callbacks, while slot 10 points at `0x006139a8` with `NO_FUNCTION_AT_POINTER` and remains adjacent table/metadata context.

The saved `0x00521c80 CFEPWingmen__Update` comment now states that the dev-mode/state-zero vtable slot `+0x0c` dispatch resolves to `0x00521d20 CFEPWingmen__ButtonPressed`, closing the older missing-boundary-deferred wording/tag. The saved `0x005230e0 CFEPWingmen__FindCurrentLevelRecord` comment now points at recovered `CFEPWingmen__ButtonPressed` and `CFEPWingmen__Render` callsites loading `ECX=&DAT_0089da44`, calling the helper, and reading returned record fields at `+0x04/+0x08/+0x0c`.

Runtime Wingmen menu/input/render behavior, exact button behavior, visible frontend output, exact concrete `CFEPWingmen`/record/frontend thing/text/layout/controller-input layouts, exact source-body identity for absent `FEPWingmen.cpp`, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1051; fepwingmen-page-review-wave1051; 0x00521c80 CFEPWingmen__Update; 0x00521d20 CFEPWingmen__ButtonPressed; 0x00522190 CFEPWingmen__Render; 0x005230e0 CFEPWingmen__FindCurrentLevelRecord; CFEPWingmen__UpdateSpinnerTransformAndPulse; 0x005dba10 CFEPWingmen_vtable; 0x006139a8; NO_FUNCTION_AT_POINTER; C:\dev\ONSLAUGHT2\FEPWingmen.cpp; 744/1408 = 52.84%; 1032/1509 = 68.39%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-150857_post_wave1051_fepwingmen_page_review_verified; comment/tag normalization.

## Function Notes

### `CFEPWingmen__GetWingmenCount` (`0x00521650`)

Counts available wingman entries for the current level. `CFEPBEConfig__Render` and `CFEPBEConfig__ButtonPressed` call it. The function resets the global iterator to `DAT_0089da6c`, walks list links through `DAT_0089da74`, compares each record's first dword to `DAT_0089d94c`, then counts filled slots at `+0x04`, `+0x0c`, and `+0x08`.

### `CFEPWingmen__Destroy` (`0x00521a60`)

Frees up to three frontend thing pointers at `this+0x08`, `this+0x0c`, and `this+0x10` via `CFrontEndThing__dtor_base` and `CDXMemoryManager__Free`. It then drains the pointer set at `this+0x28`, removing each value with `CSPtrSet__Remove`, cleaning it with `CFEPBEConfig__CleanupSquads`, and freeing it. The current Ghidra signature remains `__fastcall`; a future convention pass should decide whether to normalize it to `__thiscall`.

### `CFEPWingmen__Load` (`0x00521ae0`)

Wave565 corrected this to `void __thiscall CFEPWingmen__Load(void * this, void * stream)`. The function allocates a `0x24`-byte record from the `FEPWingmen.cpp` debug path at line `0xd3`, initializes `record+0x14` as a `CSPtrSet`, reads version/count/name-string data from `CDXMemBuffer`, applies version `<2` defaults for slots `+0x04/+0x08/+0x0c`, applies version `<3` default for slot `+0x10`, and appends the record to `this+0x28`.

### `CFEPWingmen__Update` (`0x00521c80`)

Vtable slot 2 update path. It increments `this+0x14` by `_DAT_005d8574`, calls `CFEPWingmen__UpdateSpinnerTransformAndPulse` for live frontend thing pointers at `this+0x08/+0x0c/+0x10`, decrements/clamps fade fields `this+0x1c` and `this+0x20` by `_DAT_005d85c0`, and when `state == 0` plus `g_bDevModeEnabled`, calls vtable slot `+0x0c` with constants `0x2c` and `0x3f800000`. Wave1045 recovered that target as `0x00521d20 CFEPWingmen__ButtonPressed`.

### `CFEPWingmen__FindCurrentLevelRecord` (`0x005230e0`)

Wave566 corrected this saved Ghidra row from stale `CVBufTexture__FindListEntryByGlobalId89D94C` ownership to `CFEPWingmen__FindCurrentLevelRecord`. Before Wave1045, its representative xrefs were no-function callsites in deferred FEPWingmen instruction ranges; Wave1045 brought the button/render callsites under recovered function objects. Representative callsites load `ECX` with `0x89da44`, call `0x005230e0`, then read returned record fields at `+0x04`, `+0x08`, and `+0x0c`. The body seeds cursor `this+0x30` from list head `this+0x28`, follows node `+0x04` links, and returns the first record whose first dword equals current level global `DAT_0089d94c` or null. This aligns with `CFEPWingmen__Load` appending `0x24`-byte records to `this+0x28`.

### `CFEPWingmen__TransitionNotification` (`0x005230c0`)

Formerly `CFEPWingmen__VFunc_06_005230c0`. Vtable slot 6 matches the frontend `TransitionNotification` convention already established for `FEPCredits`, `FEPMultiplayerStart`, `FEPScreenPos`, and `FEPVirtualKeyboard`. The function ignores `from_page`, calls `PLATFORM__GetSysTimeFloat` through platform singleton `0x0088a0a8`, stores the timestamp at `this+0x04`, clears `this+0x18`, and returns with `RET 0x4`.

### `CFEPWingmen__UpdateSpinnerTransformAndPulse` (`0x0046baf0`)

Shared frontend helper, not exclusively Wingmen-owned despite its current name. It writes a yaw/pulse transform derived from `DAT_00672fd0` into matrix-like fields `this+0x14..0x40`, then oscillates alpha/pulse field `this+0x4c` using `this+0x48 * _DAT_005d8bb8`, direction flag `this+0x50`, and countdown `this+0x54`.

## Wave566 Evidence

- Apply script: `tools/ApplyFEPMixerMapWave566.java`
- Probe: `tools/ghidra_fep_mixermap_wave566_probe.py`
- Artifacts: `subagents/ghidra-static-reaudit/wave566-cvbuftexture-mixermap-005230e0/`

Read-back summary: dry `updated=0 skipped=5 renamed=0 would_rename=1 missing=0 bad=0`; apply `updated=5 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`; final dry `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified 5 metadata rows, 5 tag rows, 17 xref rows, 1125 target instruction rows, 5 decompile rows, 341 FEP callsite instruction rows, queue refresh PASS, and no `source-parity` tags.

## Wave565 Evidence

- Apply script: `tools/ApplyFEPWingmenWave565.java`
- Probe: `tools/ghidra_fepwingmen_wave565_probe.py`
- Artifacts: `subagents/ghidra-static-reaudit/wave565-fepwingmen-005230c0/`
- Ghidra backup: `G:\GhidraBackups\BEA_20260518-211003_post_wave565_fepwingmen_verified`

Read-back summary: dry `updated=0 skipped=6 renamed=0 would_rename=1 missing=0 bad=0`; apply `updated=6 skipped=0 renamed=1 missing=0 bad=0`; final dry `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified 6 metadata rows, 6 tag rows, 13 xref rows, 1015 target instruction rows, 6 decompile rows, 16 vtable rows, queue refresh PASS, and backup manifest match.

## Proof Boundaries

Wave566 proves saved static Ghidra names/comments/tags/signatures for the covered rows only. It does not prove runtime wingman selection behavior, concrete `CFEPWingmen` or record layouts, data-file schema, exact source identity, vtable slot names for missing boundaries, BEA launch behavior, game patching, or rebuild parity.
