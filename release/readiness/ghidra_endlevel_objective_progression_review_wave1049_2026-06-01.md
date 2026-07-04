# Ghidra End-Level Objective Progression Review Wave1049

Status: complete read-only static review
Date: 2026-06-01
Scope: `endlevel-objective-progression-review-wave1049`

Wave1049 re-read the static end-level objective/progression bridge from MissionScript objective handlers through CGame objective state, END_LEVEL_DATA snapshot/predicate helpers, Career link recalculation, slot persistence context, and outro-FMV selection. Fresh metadata, tag, xref, instruction, and decompile evidence matched the saved Ghidra state, so the wave made no mutation: no rename, signature change, comment/tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation occurred.

Reviewed rows:

| Address | Saved row | Fresh static evidence |
| --- | --- | --- |
| `0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete` | `bool __fastcall CEndLevelData__IsAllSecondaryObjectivesComplete(void * this)` | Scans secondary objective status slots at `this+0x4d0`, returns false when any failed status is present, and logs `ERROR: No secondary objectives` when no complete/failed secondary objective is defined. |
| `0x0046d470 CGame__FillOutEndLevelData` | `void __fastcall CGame__FillOutEndLevelData(void * this)` | Captures the end-of-level snapshot into `DAT_006728f8`, including primary/secondary objective arrays, timers, score/lives context, kill counts, progression/grade fields, and calls the secondary-objective predicate. |
| `0x00472670 CGame__GetNumPrimaryObjectives` | `int __fastcall CGame__GetNumPrimaryObjectives(void * this)` | Counts non-empty entries in the ten-entry primary objective array at `CGame+0x4c`. |
| `0x00472690 CGame__GetNumSecondaryObjectives` | `int __fastcall CGame__GetNumSecondaryObjectives(void * this)` | Counts non-empty entries in the ten-entry secondary objective array at `CGame+0x9c`. |
| `0x0041bdf0 CCareer__ReCalcLinks` | `void __fastcall CCareer__ReCalcLinks(void * this)` | Uses `END_LEVEL_DATA`, child links, the secondary-objective predicate, and the world 500 slot branch at career `+0x240c` bits `29/30` for source slots `61/62`. |
| `0x0046d9f0 CGame__RunOutroFMV` | `void __fastcall CGame__RunOutroFMV(void * this)` | Resolves outro FMV lookup types `1/2`, applies level-specific branches for `500` and `720`, consults the secondary-objective predicate, applies goodie unlock updates, and reaches credits/fallback cutscene paths. |
| `0x005343e0 IScript__PrimaryObjectiveComplete` | `void __stdcall IScript__PrimaryObjectiveComplete(void * script_args, void * unused_state, void * out_result)` | Script command handler writes primary objective text to `DAT_008a9ae0` and state `1` to `DAT_008a9adc`. |
| `0x00534410 IScript__SecondaryObjectiveComplete` | `void __stdcall IScript__SecondaryObjectiveComplete(void * script_args, void * unused_state, void * out_result)` | Script command handler writes secondary objective text to `DAT_008a9b30` and state `1` to `DAT_008a9b2c`. |
| `0x00534440 IScript__PrimaryObjectiveFailed` | `void __stdcall IScript__PrimaryObjectiveFailed(void * script_args, void * unused_state, void * out_result)` | Script command handler writes primary objective text to `DAT_008a9ae0` and state `2` to `DAT_008a9adc`. |
| `0x00534470 IScript__SecondaryObjectiveFailed` | `void __stdcall IScript__SecondaryObjectiveFailed(void * script_args, void * unused_state, void * out_result)` | Script command handler writes secondary objective text to `DAT_008a9b30` and state `2` to `DAT_008a9b2c`. |

Context rows:

- `0x0041bd00 CCareer__Update` calls `CCareer__ReCalcLinks` after won-level career updates, then recomputes goodie states.
- `0x0046f2f0 CGame__DeclareLevelWon` / `0x0046f430 CGame__DeclareLevelLost` feed the level-end state consumed by the snapshot and career update path.
- `0x0046d3a0 CGame__SetSlot`, `0x0046d410 CGame__GetSlot`, and `0x004214e0 CCareer__SetSlot` keep the runtime and save-persistent slot bridges tied to `this+0x308` and career slots.
- `0x005338d0 IScript__SetSlot`, `0x00533900 IScript__SetSlotSave`, and `0x005339a0 IScript__GetSlotBitValue` connect MissionScript slot operations to `CGame__SetSlot`, `CGame__GetSlot`, and `CCareer__SetSlot`.

Evidence counts:

- Primary exports: `10` metadata rows, `10` tag rows, `13` xref rows, `761` function-body instruction rows, and `10` decompile rows.
- Context exports: `12` metadata rows, `12` tag rows, `23` xref rows, `6129` function-body instruction rows, and `12` decompile rows.
- Queue closure remains `6246/6246 = 100.00%`, with `0` commentless rows, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave1049 targets are outside the Wave911 focused TSV, so Wave911 focused progress remains `744/1408 = 52.84%`; expanded static surface progress advances to `1012/1509 = 67.06%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-134936_post_wave1049_endlevel_objective_progression_review_verified`, 19 files, 174590855 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The reviewed objective/progression rows still exist as saved Ghidra function objects in the loaded database.
- The saved names, signatures, comments, tags, xrefs, instruction bodies, and decompile exports are internally coherent across MissionScript objective commands, CGame objective arrays, END_LEVEL_DATA snapshot/predicate helpers, Career link recalculation, slot bridges, and outro-FMV selection.
- The review is static Ghidra evidence only, tied to serialized metadata/tags/xrefs/instructions/decompile exports and a verified project backup.

What remains separate proof:

- Runtime objective UI behavior, runtime mission-script dispatch/argument behavior, runtime progression/save outcome behavior, runtime outro/cutscene behavior, and runtime goodie unlock behavior.
- Complete mission-script corpus coverage and exact command descriptor schema.
- Concrete `CGame`, `CEndLevelData`, `CCareer`, and MissionScript value/object layouts beyond observed offsets.
- Exact source-body identity where retail code and source names remain only source-aligned.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1049; endlevel-objective-progression-review-wave1049; 0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete; 0x0046d470 CGame__FillOutEndLevelData; 0x0041bdf0 CCareer__ReCalcLinks; 0x0046d9f0 CGame__RunOutroFMV; 0x005343e0 IScript__PrimaryObjectiveComplete; 0x00534470 IScript__SecondaryObjectiveFailed; CGame__SetSlot; IScript__SetSlotSave; IScript__GetSlotBitValue; 744/1408 = 52.84%; 1012/1509 = 67.06%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-134936_post_wave1049_endlevel_objective_progression_review_verified; no mutation.
