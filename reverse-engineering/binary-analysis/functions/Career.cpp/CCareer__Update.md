# CCareer__Update

> Address: `0x0041bd00`
>
> Source: `references/Onslaught/Career.cpp` (`CCareer::Update()`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Yes

## Purpose
Update career progress from the current `END_LEVEL_DATA` snapshot.

This is the “mission finished” entry point: it updates slots/kills, updates node completion + ranking, recalculates links, then recomputes goodies.

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

## Related Functions
- [CCareer__ReCalcLinks](CCareer__ReCalcLinks.md) - Update link completion/broken state
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md) - Goodie unlock recomputation
- [CCareer__UpdateThingsKilled](CCareer__UpdateThingsKilled.md) - Kill counter accumulation
- [CCareer__GetGradeFromRanking](CCareer__GetGradeFromRanking.md) - Converts ranking to grade
