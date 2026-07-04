# Career.cpp Function Mappings

> Functions from Career.cpp mapped to BEA.exe binary
> Source: references/Onslaught/Career.cpp (Stuart's code)

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

- **Functions Mapped:** 37
- **Status:** MIGRATED from ghidra-analysis.md
- **Classes:** CCareer, CCareerNode

## Current Caveat

Wave 316 hardened `0x0041bd00` as `void __fastcall CCareer__Update(void * this)` and confirmed the older `0x00420cd0` / `0x00420d10` Career owner labels were stale. Those two bodies are now saved as `D3DDeviceProfileTable__GetAdapterRecord` and `D3DDeviceProfile__PackDeviceIndexKey` in options-tail display/profile context, not as `CCareer` helpers.

2026-06-08 MissionScript Slot Command-Effect static proof: `missionscript-slot-command-effect-static-proof.md` and `missionscript-slot-command-effect.v1.json` preserve the Career side of the slot bridge through `CCareer__SetSlot`, `IScript__SetSlotSave`, `CGame__SetSlot`, `CGame__GetSlot`, runtime storage `CGame+0x308`, true-view save slot base `0x240A`, `6 slot-using level rows`, `18 detailed slot call rows`, `6 GetSlot`, `8 SetSlot`, and `4 SetSlotSave`. This is MissionScript Slot Command-Effect static bridge accounting only, not runtime command effects, runtime save behavior, runtime slot persistence, exact `CCareer` layout, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 MissionScript Objective/Outcome Command-Effect static proof: `missionscript-objective-outcome-command-effect-static-proof.md` and `missionscript-objective-outcome-command-effect.v1.json` preserve the Career side of the objective/outcome bridge through `CCareer__Update`, `CGame__FillOutEndLevelData`, `CGame__DeclareLevelWon`, `CGame__DeclareLevelLost`, `CEndLevelData__IsAllSecondaryObjectivesComplete`, and the `IScript__PrimaryObjectiveComplete` / `IScript__SecondaryObjectiveComplete` / `IScript__PrimaryObjectiveFailed` / `IScript__SecondaryObjectiveFailed` / `IScript__LevelWon` / `IScript__LevelLost` / `IScript__LevelLostString` handler family. This is MissionScript Objective/Outcome Command-Effect static bridge accounting only, not runtime command effects, runtime objective UI, runtime level outcome behavior, runtime save/career progression, exact `CCareer` layout, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 MissionScript Goodie State Command-Effect static proof: `missionscript-goodie-state-command-effect-static-proof.md` and `missionscript-goodie-state-command-effect.v1.json` preserve the Career side of the Goodie-state bridge through `SetGoodieState`, `GetGoodieState`, `IScript__SetGoodieState`, `IScript__GetGoodieState`, `g_Career_mGoodies[index-1]`, `0x00662564`, true-view save Goodie base `0x1F46`, `300` Goodie entries, and script index N maps to save Goodie index N-1. `AddScore` is retained as descriptor/name context only. This is MissionScript Goodie State Command-Effect static bridge accounting only, not runtime command effects, runtime Goodie state mutation, runtime save behavior, runtime Goodies wall behavior, exact `CCareer` layout, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 Save / Options Controller Byte-Preservation Copied-File Proof: `save-options-controller-byte-preservation-copied-file-proof.md` and `save-options-controller-byte-preservation-copied-file.v1.json` preserve the Career/save side of copied-file byte proof through `10004`, `0x4BD1`, `file_offset = 0x0002 + career_offset`, no-op `DiffCount=0`, scoped Aircraft kill lower-24 payload allowlist `0x23F6-0x23F8`, metadata byte `0x23F9` preservation, options entries `0x24BE-0x26BD`, options tail `0x26BE-0x2713`, and legacy trap offsets `0x23A4`, `0x22D4`, and `0x240C` not touched. This is copied-file byte-preservation proof only, not runtime save/load behavior, runtime defaultoptions boot behavior, runtime menu/controller behavior, runtime Goodies wall behavior, exact `CCareer` layout, patch, Godot, rebuild, or no-noticeable-difference proof.

Wave 329 hardened signatures/comments/tags for 21 Career/save/Goodies helpers without renames. It corrected stale `CCareer__ReCalcLinks` wording: the world-500 `mSlots` branch at career `+0x240c` bits `29/30` maps to source slots `61/62` and is not god-mode flag evidence. Runtime save/load behavior, Goodies unlock behavior, concrete layouts, local/type recovery, and rebuild parity remain separate proof questions.

Wave 381 corrected the older Career-owner label at `0x004496e0`: the saved function is now `CEndLevelData__IsAllSecondaryObjectivesComplete`, documented under `EndLevelData.cpp`. Career paths still call it, but it is no longer documented as a `CCareer` method.

Wave1044 (`career-controller-residual-review-wave1044`) re-read the residual Career rows `0x0041b740 CCareerNode__Blank`, `0x0041c180 CCareer__UpdateThingsKilled`, `0x0041c470 CCareer__UpdateGoodieStates`, and `0x004214e0 CCareer__SetSlot` with no mutation. Fresh evidence kept the saved names/signatures/comments coherent with Stuart source and retail decompile: `CCareerNode__Blank` resets links/base-thing masks/ranking, `CCareer__UpdateThingsKilled` skips world `100` and folds five `g_LevelKillCounts` counters into the `this+0x23f4` kill-counter area, `CCareer__UpdateGoodieStates` walks the 300-entry Goodies state block at `this+0x1f44` through completion/grade predicates including `CCareer__GetGradeForWorld` and `CGrade__operator_gte`, and `CCareer__SetSlot` sets/clears `this+0x2408+(slot>>5)*4` after the `0..0xff` range check. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-103855_post_wave1044_career_controller_residual_review_verified`. Wave1044 overall keeps queue closure `6238/6238 = 100.00%`, Wave911 focused progress `735/1408 = 52.20%`, expanded static surface `977/1493 = 65.44%`, and top-500 coverage `500/500 = 100.00%`. Runtime save/progression behavior, runtime Goodies unlock behavior, concrete Career layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1049 (`endlevel-objective-progression-review-wave1049`) re-read the Career side of the end-level objective/progression bridge with no mutation. Fresh evidence keeps `0x0041bd00 CCareer__Update` calling `0x0041bdf0 CCareer__ReCalcLinks`, keeps `CCareer__ReCalcLinks` tied to `0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete`, and keeps the world-500 slot branch connected to script slot persistence through `CGame__SetSlot`, `IScript__SetSlotSave`, and `IScript__GetSlotBitValue`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-134936_post_wave1049_endlevel_objective_progression_review_verified`. Runtime progression/save outcome behavior, runtime goodie unlock behavior, concrete Career/CGame/EndLevelData layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Function List

| Address | Name | Status | Link |
|---------|------|--------|------|
| 0x0041b6a0 | CCareer__StaticInitDefaults | VERIFIED | [View](CCareer__StaticInitDefaults.md) |
| 0x0041b740 | CCareerNode__Blank | VERIFIED | [View](CCareerNode__Blank.md) |
| 0x0041b770 | CCareerNode__SetBaseThingExistTo | VERIFIED | [View](CCareerNode__SetBaseThingExistTo.md) |
| 0x0041b7b0 | CCareer__GetLevelStructure | VERIFIED | [View](CCareer__GetLevelStructure.md) |
| 0x0041b7c0 | CCareer__Blank | VERIFIED | [View](CCareer__Blank.md) |
| 0x0041b8f0 | CCareer__GetNodeFromWorld | VERIFIED | [View](CCareer__GetNodeFromWorld.md) |
| 0x0041b940 | CCareerNode__GetChildLinks | VERIFIED | [View](CCareerNode__GetChildLinks.md) |
| 0x0041b9f0 | CCareerNode__GetParentLinks | VERIFIED | [View](CCareerNode__GetParentLinks.md) |
| 0x0041bb20 | CCareer__DoesBaseThingExist | VERIFIED | [View](CCareer__DoesBaseThingExist.md) |
| 0x0041bbb0 | CCareer__IsWorldLater | VERIFIED | [View](CCareer__IsWorldLater.md) |
| 0x0041bc60 | CCareer__Later | VERIFIED | [View](CCareer__Later.md) |
| 0x0041bd00 | CCareer__Update | VERIFIED | [View](CCareer__Update.md) |
| 0x0041bdf0 | CCareer__ReCalcLinks | VERIFIED | [View](CCareer__ReCalcLinks.md) |
| 0x0041c180 | CCareer__UpdateThingsKilled | VERIFIED | [View](CCareer__UpdateThingsKilled.md) |
| 0x0041c240 | TOTAL_S_GRADES | VERIFIED | [View](TOTAL_S_GRADES.md) |
| 0x0041c330 | CCareer__GetGradeForWorld | VERIFIED | [View](CCareer__GetGradeForWorld.md) |
| 0x0041c450 | CCareer__CountGoodies | VERIFIED | [View](CCareer__CountGoodies.md) |
| 0x0041c470 | CCareer__UpdateGoodieStates | VERIFIED | [View](CCareer__UpdateGoodieStates.md) |
| 0x00420ab0 | CGrade__ctor_char | VERIFIED | [View](CGrade__ctor_char.md) |
| 0x00420ac0 | CGrade__operator_gte | VERIFIED | [View](CGrade__operator_gte.md) |
| 0x00420af0 | CCareer__GetNode | VERIFIED | [View](CCareer__GetNode.md) |
| 0x00421200 | CCareer__Load | NAMED | [View](CCareer__Load.md) |
| 0x00421350 | CCareer__Save | NAMED | [View](CCareer__Save.md) |
| 0x004213c0 | CCareer__SaveWithFlag | NAMED | [View](CCareer__SaveWithFlag.md) |
| 0x00421430 | CCareer__GetSaveSize | NAMED | [View](CCareer__GetSaveSize.md) |
| 0x00421470 | CCareer__GetGradeFromRanking | VERIFIED | [View](CCareer__GetGradeFromRanking.md) |
| 0x004214e0 | CCareer__SetSlot | VERIFIED | [View](CCareer__SetSlot.md) |
| 0x00421550 | CCareer__GetAndResetGoodieNewCount | VERIFIED | [View](CCareer__GetAndResetGoodieNewCount.md) |
| 0x00421560 | CCareer__GetAndResetFirstGoodie | VERIFIED | [View](CCareer__GetAndResetFirstGoodie.md) |
| 0x00421570 | CCareer__IsEpisodeAvailable | VERIFIED | [View](CCareer__IsEpisodeAvailable.md) |
| 0x004218f0 | CCareer__GetKillCounterTopByte_23F4 | VERIFIED | [View](CCareer__GetKillCounterTopByte_23F4.md) |
| 0x00421900 | CCareer__GetKillCounterTopByte_23F8 | VERIFIED | [View](CCareer__GetKillCounterTopByte_23F8.md) |
| 0x00421910 | CCareer__SetKillCounterTopByte_23F4 | VERIFIED | [View](CCareer__SetKillCounterTopByte_23F4.md) |
| 0x00421940 | CCareer__SetKillCounterTopByte_23F8 | VERIFIED | [View](CCareer__SetKillCounterTopByte_23F8.md) |
| 0x00421970 | CCareer__NodeArrayAt | VERIFIED | [View](CCareer__NodeArrayAt.md) |
| 0x00421980 | CCareer__GetGoodiePtr | VERIFIED | [View](CCareer__GetGoodiePtr.md) |

## Related
- Source: `references/Onslaught/Career.cpp`
- Header: `references/Onslaught/Career.h`
- Parent: [../README.md](../README.md)
