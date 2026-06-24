# Ghidra FEPWingmen Page Review Wave1051

Status: complete saved comment/tag normalization
Date: 2026-06-01
Scope: `fepwingmen-page-review-wave1051`

Wave1051 re-read the FEPWingmen page after Wave1045 recovered the missing vtable function boundaries. It saved a bounded comment/tag normalization across the Wingmen page rows: the stale `missing-boundary-deferred` tag and older missing-boundary wording on `0x00521c80 CFEPWingmen__Update` are now closed, and `0x005230e0 CFEPWingmen__FindCurrentLevelRecord` now points at the recovered `CFEPWingmen__ButtonPressed` and `CFEPWingmen__Render` callsites instead of older deferred-callsite framing.

The wave made no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Reviewed rows:

| Address | Saved row | Fresh static evidence |
| --- | --- | --- |
| `0x00521650 CFEPWingmen__GetWingmenCount` | `char CFEPWingmen__GetWingmenCount(void)` | Counts nonzero wingman slots for the current level record. |
| `0x005216c0 CFEPWingmen__Init` | `int __fastcall CFEPWingmen__Init(void * this)` | Wave1045 `0x005dba10` slot 0 function-boundary recovery remains coherent. |
| `0x00521a60 CFEPWingmen__Destroy` | `void __fastcall CFEPWingmen__Destroy(void * this)` | Frees frontend thing pointers and drains the page record set. |
| `0x00521ae0 CFEPWingmen__Load` | `void __thiscall CFEPWingmen__Load(void * this, void * stream)` | Loads `0x24`-byte records from the `FEPWingmen.cpp` stream and appends them to the page list. |
| `0x00521c80 CFEPWingmen__Update` | `void __thiscall CFEPWingmen__Update(void * this, int state)` | Saved correction: per-frame update calls `CFEPWingmen__UpdateSpinnerTransformAndPulse` for live frontend thing slots, clamps fade fields, and dispatches vtable slot `+0x0c`; Wave1045 proves that target is `0x00521d20 CFEPWingmen__ButtonPressed`, so the older missing-boundary-deferred wording/tag is closed. |
| `0x00521d20 CFEPWingmen__ButtonPressed` | `void __thiscall CFEPWingmen__ButtonPressed(void * this, int button, float val)` | Recovered vtable slot 3 input body calls `CFEPWingmen__FindCurrentLevelRecord(&DAT_0089da44)` and plays frontend sounds while updating current-level state. |
| `0x00522160 CFEPWingmen__RenderPreCommon` | `void __stdcall CFEPWingmen__RenderPreCommon(float transition, int dest)` | Recovered vtable slot 4 pre-common render helper. |
| `0x00522190 CFEPWingmen__Render` | `void __thiscall CFEPWingmen__Render(void * this, float transition, int dest)` | Recovered vtable slot 5 render body repeatedly calls `CFEPWingmen__FindCurrentLevelRecord(&DAT_0089da44)`. |
| `0x005230c0 CFEPWingmen__TransitionNotification` | `void __thiscall CFEPWingmen__TransitionNotification(void * this, int from_page)` | Vtable slot 6 transition callback remains coherent. |
| `0x005230e0 CFEPWingmen__FindCurrentLevelRecord` | `void * __thiscall CFEPWingmen__FindCurrentLevelRecord(void * this)` | Saved normalization: older deferred-callsite framing is superseded by recovered ButtonPressed/Render callsites; body walks `this+0x28/+0x30` records and returns the first id matching `DAT_0089d94c`. |
| `0x0046baf0 CFEPWingmen__UpdateSpinnerTransformAndPulse` | `void __thiscall CFEPWingmen__UpdateSpinnerTransformAndPulse(void * this)` | Shared frontend spinner transform/pulse helper remains coherent. |

Vtable evidence:

- `0x005dba10` slots 0-9 resolve to `CFEPWingmen__Init`, `CFEPWingmen__Destroy`, `CFEPWingmen__Update`, `CFEPWingmen__ButtonPressed`, `CFEPWingmen__RenderPreCommon`, `CFEPWingmen__Render`, `CFEPWingmen__TransitionNotification`, `CFrontEndPage__Process_NoOp`, `DebugTrace`, and `CFEPWingmen__Load`.
- Slot 10 points at `0x006139a8` with `NO_FUNCTION_AT_POINTER`; this remains adjacent table/metadata context, not current method proof.

Evidence counts:

- Primary exports: pre/post `11` metadata rows, `11` tag rows, `27` xref rows, `1818` function-body instruction rows, and `11` decompile rows.
- Context exports: `15` metadata/tag/decompile index rows with one expected missing context function at `0x0046a180`, `321` xref rows, `3472` function-body instruction rows, and `14` dumped context decompile bodies.
- Vtable export: pre/post `1` vtable anchor and `11` slot rows.
- Debug string: `0x0063fd4c` -> `C:\dev\ONSLAUGHT2\FEPWingmen.cpp`.
- Apply gate: dry reported `updated=0 skipped=11 comment_updated=2 tags_added=51 tags_removed=0 would_remove_tags=1 missing=0 bad=0`; apply reported `updated=11 skipped=0 comment_updated=2 tags_added=51 tags_removed=1 would_remove_tags=0 missing=0 bad=0`; final dry reported `updated=0 skipped=11 comment_updated=0 tags_added=0 tags_removed=0 would_remove_tags=0 missing=0 bad=0`.
- Queue closure remains `6246/6246 = 100.00%`, with `0` commentless rows, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused progress remains `744/1408 = 52.84%`; expanded static surface progress advances to `1032/1509 = 68.39%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-150857_post_wave1051_fepwingmen_page_review_verified`, 19 files, 174623623 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The reviewed Wingmen rows still exist as saved Ghidra function objects in the loaded database.
- Saved comments/tags now reflect that Wave1045 recovered the formerly missing Wingmen vtable slot bodies.
- `CFEPWingmen__Update` no longer carries the stale missing-boundary tag or stale missing-boundary wording.
- The Wingmen page surface is coherent across metadata, tags, xrefs, instruction bodies, decompile exports, vtable slots, debug-string evidence, context helpers, and a verified project backup.

What remains separate proof:

- Runtime Wingmen menu/input/render behavior, exact button behavior, visible frontend output, and gameplay outcomes.
- Exact concrete `CFEPWingmen`, record, frontend thing, text/layout, and controller/input layouts beyond observed offsets.
- Exact source-body identity because `FEPWingmen.cpp` is absent from `references/Onslaught`.
- BEA patching behavior and rebuild parity.

Probe token anchor: Wave1051; fepwingmen-page-review-wave1051; 0x00521c80 CFEPWingmen__Update; 0x00521d20 CFEPWingmen__ButtonPressed; 0x00522190 CFEPWingmen__Render; 0x005230e0 CFEPWingmen__FindCurrentLevelRecord; CFEPWingmen__UpdateSpinnerTransformAndPulse; 0x005dba10 CFEPWingmen_vtable; 0x006139a8; NO_FUNCTION_AT_POINTER; C:\dev\ONSLAUGHT2\FEPWingmen.cpp; 744/1408 = 52.84%; 1032/1509 = 68.39%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-150857_post_wave1051_fepwingmen_page_review_verified; comment/tag normalization.
