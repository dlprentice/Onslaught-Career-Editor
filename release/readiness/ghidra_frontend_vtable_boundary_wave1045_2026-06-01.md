# Ghidra Frontend Vtable Boundary Wave1045

Status: complete static function-boundary mutation evidence
Date: 2026-06-01
Scope: `frontend-vtable-boundary-wave1045`

Wave1045 recovered eight frontend vtable-pointed function boundaries that were valid retail code but were not modeled as Ghidra function objects. The pass started as a read-only review of `CFrontEnd__InitPageStateDefaults` and `CFrontEnd__RenderOverlayEffects`; callsites from `CFrontEnd__RenderOverlayEffects` exposed missing `CFEPGoodies` and `CFEPWingmen` vtable slots. The mutation created the missing function objects, saved bounded names/signatures/comments/tags, and did not change executable bytes or launch BEA.

Recovered rows:

| Address | Saved row | Evidence |
| --- | --- | --- |
| `0x0045c7a0` | `CFEPGoodies__Init` | `CFEPGoodies` vtable `0x005db998` slot 0 DATA ref; initializes Goodies page state fields and copies the default table from `0x00679870`. |
| `0x0045c9e0` | `CFEPGoodies__Shutdown` | `CFEPGoodies` vtable `0x005db998` slot 1 DATA ref; compact shutdown thunk to `CFEPGoodies__FreeUpGoodyResources`. |
| `0x0045e0d0` | `CFEPGoodies__Render` | `CFEPGoodies` vtable `0x005db998` slot 5 DATA ref; large render body reaches `CFrontEnd__RenderOverlayEffects` at callsite `0x0045ff36`. |
| `0x0045ffa0` | `CFEPGoodies__TransitionNotification` | `CFEPGoodies` vtable `0x005db998` slot 6 DATA ref; calls `PLATFORM__GetSysTimeFloat` and resets Goodies selection/animation fields. |
| `0x005216c0` | `CFEPWingmen__Init` | `CFEPWingmen` vtable `0x005dba10` slot 0 DATA ref; initializes Wingmen state/list/frontend-thing resources. |
| `0x00521d20` | `CFEPWingmen__ButtonPressed` | `CFEPWingmen` vtable `0x005dba10` slot 3 DATA ref; formerly deferred target of `CFEPWingmen__Update` vtable `+0x0c` dev-mode path. |
| `0x00522160` | `CFEPWingmen__RenderPreCommon` | `CFEPWingmen` vtable `0x005dba10` slot 4 DATA ref; compact transition render-pre-common helper returning with `RET 0x8`. |
| `0x00522190` | `CFEPWingmen__Render` | `CFEPWingmen` vtable `0x005dba10` slot 5 DATA ref; large render body calls shadow offsets, render-state/surface helpers, `CFEPWingmen__FindCurrentLevelRecord`, text helpers, and `CFrontEnd__RenderOverlayEffects` at callsite `0x005230ac`. |

Read-back evidence:

- Dry run: `updated=0 skipped=0 created=0 would_create=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- First apply saved seven rows, then hit a defined-data obstruction at `0x0045e0d0 CFEPGoodies__Render`: `createFunction returned null at 0x0045e0d0 (disassemble=true)`. This was recovered, not left open.
- Recovery dry run: `updated=0 skipped=7 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Recovery apply: `updated=1 skipped=7 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`.
- Final dry run: `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `8` metadata rows, `8` tag rows, `8` DATA xref rows, `3540` function-body instruction rows, `8` decompile rows, and `135` frontend vtable slot rows.
- Queue after Wave1045 is `6246/6246 = 100.00%`, with `0` commentless rows, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave1045 targets are not Wave911 focused TSV rows, so Wave911 focused progress remains `735/1408 = 52.20%`; expanded static surface progress advances to `985/1501 = 65.62%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-112809_post_wave1045_frontend_vtable_boundary_verified`, 19 files, 174590855 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The eight vtable-pointed retail code addresses now exist as saved Ghidra function objects.
- The saved names, signatures, comments, and tags read back from the loaded Ghidra project.
- `CFEPGoodies` and `CFEPWingmen` vtable slots previously reported as `NO_FUNCTION_AT_POINTER` now resolve to saved function rows.
- The `0x0045e0d0` partial apply failure was an expected recoverable listing-state obstruction and was closed by the recovery dry/apply/final-dry chain.

What remains separate proof:

- Runtime Goodies wall behavior, model/video playback, asset visibility, and visual parity.
- Runtime Wingmen menu/input/render behavior.
- Exact concrete `CFEPGoodies` and `CFEPWingmen` layouts.
- Exact source-body identity for `FEPWingmen.cpp`, which is absent from `references/Onslaught`.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1045; frontend-vtable-boundary-wave1045; 0x0045c7a0 CFEPGoodies__Init; 0x0045c9e0 CFEPGoodies__Shutdown; 0x0045e0d0 CFEPGoodies__Render; 0x0045ffa0 CFEPGoodies__TransitionNotification; 0x005216c0 CFEPWingmen__Init; 0x00521d20 CFEPWingmen__ButtonPressed; 0x00522160 CFEPWingmen__RenderPreCommon; 0x00522190 CFEPWingmen__Render; 0x005db998; 0x005dba10; 735/1408 = 52.20%; 985/1501 = 65.62%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-112809_post_wave1045_frontend_vtable_boundary_verified; function-boundary recovery.
