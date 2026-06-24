# CCareer__UpdateGoodieStates

> Address: 0x0041c470 | Source: `references/Onslaught/Career.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Yes (matches `CCareer::UpdateGoodieStates()` in `references/Onslaught/Career.cpp`; PC port differs in encoding details)

## Purpose
Complex goodie unlock logic. This is the master function that evaluates all goodie unlock conditions including kill thresholds, level completion, grade milestones, and special conditions.

## Signature
```c
void CCareer::UpdateGoodieStates(void);
```

## Unlock Conditions (from FEPGoodies.cpp)
- Kill count thresholds (aircraft, vehicles, etc.)
- Level completion (specific missions)
- Grade requirements (A-rank on level X, S-rank on level Y)
- Cumulative grades (10 S-ranks total, etc.)
- Episode completion

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Called after mission completion and kill count updates
- In memory, `CGoodie::mState` values are normal ints `0/1/2/3` (GS_UNKNOWN/INSTRUCTIONS/NEW/OLD). In the repo's historical aligned file view they appear as `value << 16` because CCareer bytes are copied from `source + 2`.
- Don’t patch goodies using legacy 4-byte aligned offsets; patch using the true dword view offsets (`file_off = 0x0002 + career_off`).
- **Historical confusion**: Earlier docs claimed Goodie 228 overlapped mCareerInProgress. In the true view, Goodie 228 is at `0x22D6` and `mCareerInProgress` is at `0x248A`. The legacy aligned view placed “goodie 228” at `0x22D4`. Do NOT write to `0x22D4` as if it were mCareerInProgress.
- Kill totals are compared as `kills_payload = (kill_dword & 0x00FFFFFF)` (see `reverse-engineering/save-file/kill-tracking.md`). The “shift-16” appearance in some hex views is an alignment artifact, not what the binary compares.

## Where The Truth Lives
- Full unlock tables (source-of-truth): `reverse-engineering/save-file/goodies-system.md`
- Source logic: `references/Onslaught/Career.cpp` (`CCareer::UpdateGoodieStates()`) and `references/Onslaught/FEPGoodies.cpp` (goodies[] data)
- Binary: `CCareer__UpdateGoodieStates` at `0x0041c470` (uses `& 0x00FFFFFF` masks before threshold compares)
- Supporting helpers now source-mapped:
  - `CGrade__ctor_char` (`0x00420ab0`) from `CGrade(char g)`
  - `CGrade__operator_gte` (`0x00420ac0`) from `CGrade::operator >=`
  - `CCareer__GetNode` (`0x00420af0`) from inline `CCareer::GetNode(int)`
  - `CCareer__NodeArrayAt` (`0x00421970`) compiler-emitted `node_base + index*0x40` helper used in one unlock branch

## 2026-05-07 Headless Read-Back

A read-only Ghidra headless export rechecked this function and seven supporting helpers:

- `CCareer__UpdateGoodieStates` (`0x0041c470`)
- `TOTAL_S_GRADES` (`0x0041c240`)
- `CCareer__GetAndResetGoodieNewCount` (`0x00421550`)
- `CCareer__GetAndResetFirstGoodie` (`0x00421560`)
- `CGrade__ctor_char` (`0x00420ab0`)
- `CGrade__operator_gte` (`0x00420ac0`)
- `CCareer__GetNode` (`0x00420af0`)
- `CCareer__NodeArrayAt` (`0x00421970`)

Result: `targets=8 dumped=8 missing=0 failed=0`.

Public-safe observations from the read-back:

- `CCareer__UpdateGoodieStates` still calls `CCareer__CountGoodies`, `TOTAL_S_GRADES`, the `CGrade` constructor/comparison helpers, `CCareer__GetNode`, and `CCareer__NodeArrayAt`.
- The four `TOTAL_S_GRADES` callsites line up with developer-item Goodies `74..77`.
- Source inspection confirms Goodies `71..73` are explicitly marked new when `COMPLETE_LEVEL_OR_EVO(741)` is true; the related episode-instruction logic marks 71 in episode 7 and 72/73 in episode 8, even though the normal Goodies wall coordinate mapping still skips from 70 to 74.
- Kill-threshold branches mask packed kill counters with `0xffffff`, matching the current true-view save docs.
- The function updates the aggregate new-goodie counter global consumed by `CCareer__GetAndResetGoodieNewCount`.
- The function updates the first-goodie flag global consumed by `CCareer__GetAndResetFirstGoodie`.
- No game launch, rename map, signature edit, or executable patch was performed for this read-back.

## Related Functions
- [CCareer__Update](CCareer__Update.md) - Calls this after mission updates
- [CCareer__UpdateThingsKilled](CCareer__UpdateThingsKilled.md) - Kill counts affect unlocks
- [TOTAL_S_GRADES](TOTAL_S_GRADES.md) - S-rank milestone checks
- [CCareer__GetAndResetGoodieNewCount](CCareer__GetAndResetGoodieNewCount.md) - Debriefing new-goodie count consume/reset
- [CCareer__GetAndResetFirstGoodie](CCareer__GetAndResetFirstGoodie.md) - Debriefing first-goodie consume/reset gate
