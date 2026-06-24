# CCareer__Update

> Address: `0x0041bd00`
>
> Source: `references/Onslaught/Career.cpp` (`CCareer::Update()`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Update career progress from the current `END_LEVEL_DATA` snapshot.

This is the “mission finished” entry point: it updates slots/kills, updates node completion + ranking, recalculates links, then recomputes goodies.

2026-06-08 MissionScript Objective/Outcome Command-Effect static proof: `missionscript-objective-outcome-command-effect-static-proof.md` and `missionscript-objective-outcome-command-effect.v1.json` use this function as the Career bridge from CGame end-level snapshots and objective/outcome command state toward progression updates, with `CGame__FillOutEndLevelData`, `CGame__DeclareLevelWon`, `CGame__DeclareLevelLost`, and `CEndLevelData__IsAllSecondaryObjectivesComplete` as adjacent anchors. This is static bridge accounting only; runtime command effects, runtime level outcome behavior, runtime save/career behavior, exact layout, patching, Godot, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Signature
```c
void CCareer::Update(void);
```

## High-Level Flow (Source-Parity)
1. If `END_LEVEL_DATA.mFinalState != GAME_STATE_LEVEL_WON`:
   - `UpdateGoodieStates()` and return.
2. Copy `END_LEVEL_DATA.mSlots` into `mSlots` (slots are overwritten, not accumulated).
3. `UpdateThingsKilled()` (adds per-level kill deltas into career totals).
4. Resolve the finished node by `END_LEVEL_DATA.mWorldFinished`:
   - If not found: fatal error.
5. Update ranking if improved (`if END_LEVEL_DATA.mRanking > node->mRanking`).
6. Set `node->mComplete = TRUE`.
7. Set `mCareerInProgress = TRUE` (persisted in save).
8. `ReCalcLinks()` (unlock/mark links; handles world 500 special-case).
9. `UpdateGoodieStates()` (recompute goodies based on new progress).

## Wave1049 Re-Audit

Wave1049 (`endlevel-objective-progression-review-wave1049`) re-read `CCareer__Update` as context for the end-level objective/progression bridge with no mutation. Fresh evidence keeps `CCareer__Update` calling `CCareer__ReCalcLinks` after won-level updates and keeps the world-500 slot branch connected to `CGame__SetSlot`, `IScript__SetSlotSave`, and `IScript__GetSlotBitValue` context. Verified backup: `G:\GhidraBackups\BEA_20260601-134936_post_wave1049_endlevel_objective_progression_review_verified`. Runtime progression/save outcome behavior, concrete Career/CGame layout identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Related Functions
- [CCareer__ReCalcLinks](CCareer__ReCalcLinks.md) - Update link completion/broken state
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md) - Goodie unlock recomputation
- [CCareer__UpdateThingsKilled](CCareer__UpdateThingsKilled.md) - Kill counter accumulation
- [CCareer__GetGradeFromRanking](CCareer__GetGradeFromRanking.md) - Converts ranking to grade
