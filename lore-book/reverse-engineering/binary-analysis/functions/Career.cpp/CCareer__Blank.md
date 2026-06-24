# CCareer__Blank

> Address: `0x0041b7c0`
>
> Source: `references/Onslaught/Career.cpp` (`CCareer::Blank()`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Yes

## Purpose
Reset the career to a fresh state and (re)build the mission graph (nodes + links) from the `level_structure` table.

## Signature
```c
void CCareer::Blank(void);
```

## Behavior (Retail / Steam)
- Rebuilds the mission graph for `DAT_00624184` nodes (expected 43):
  - Node array (`mNode[]`, 0x40 bytes per node, starts at `this+0x04`):
    - `mComplete = 0`
    - `mLowerLink/mHigherLink = even/odd sequential link indices`
    - `mWorldNumber = level_structure[i][0]` (world IDs like 100, 110, 200, ...)
    - `mNumAttempts = 0`
    - `mBaseThingsExists[9] = 0xFFFFFFFF`
    - `mRanking = -1.0f`
  - Link array (`mNodeLink[]`, 0x08 bytes per link, starts at `this+0x1904`):
    - `mLinkType = CN_NOT_COMPLETE (0)`
    - `mToNode = level_structure[i][1]` for lower link, `level_structure[i][2]` for higher link
- Clears derived/progress fields:
  - `mGoodies[300] = 0` (locked)
  - `mKilledThings[5] = 0`
  - `mSlots[32] = 0`
  - `mCareerInProgress = 0` (`this+0x2488`)
  - `g_bGodModeEnabled = 0` (`this+0x2494`, still cheat-gated)
  - reserved dword at `this+0x2498 = 0`
  - header dword0 (`new_goodie_count`) at `this+0x0000 = 0`
  - UI badge globals: `g_bNewGoodieFlag` (`0x00662b20`) and `g_bNewTechFlag` (`0x00662b24`) cleared to 0
- Calls `CCareer__UpdateGoodieStates` at end to recompute derived goodies state.

## Notes
- Retail `.bes` layout nuance: CCareer is copied from/to `file+2` (true dword boundaries are `file_off % 4 == 2`).
- Retail node struct has a leading dword at node offset `+0x00` (documented as `state` in `struct-layouts.md`). This reset routine does not write it via `CCareerNode__Blank`; preserve it in save patching.

## Related Functions
- [CCareer__Update](CCareer__Update.md) - Applies END_LEVEL_DATA after a win and calls `ReCalcLinks` + `UpdateGoodieStates`
- [CCareer__ReCalcLinks](CCareer__ReCalcLinks.md) - Updates link completion/broken state
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md) - Recomputes goodie state
- [CCareer__Load](CCareer__Load.md) - Deserialize fixed CCareer + optional options/tail
- [CCareer__Save](CCareer__Save.md) - Serialize fixed CCareer + options/tail
