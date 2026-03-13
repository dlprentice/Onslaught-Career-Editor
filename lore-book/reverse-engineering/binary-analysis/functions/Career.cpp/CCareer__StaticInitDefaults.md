# CCareer__StaticInitDefaults

> Address: `0x0041b6a0`
>
> Source: startup init-table entry (`g_InitFuncTable[3]` @ `0x006220b0`).
> Defaults align with `references/Onslaught/Career.cpp` (`CCareer::CCareer()`), and node/link/goodie clearing overlaps `CCareer::Blank()` but does **not** build the mission graph.

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial

## Purpose
Initialize global `CAREER` to safe defaults early in startup, before any load/new-career logic runs.

## Signature
```c
void CCareer__StaticInitDefaults(void);
```

## Behavior (Retail / Steam)
- Runs via an early startup function-pointer table (`g_InitFuncTable`).
- Clears/initializes large CCareer arrays:
  - `CCareerNode[100]`: calls `CCareerNode__Blank` for each node (stride `0x40`, base `CAREER+0x04`)
  - `CCareerNodeLink[200]`: sets `mLinkType = 0`, `mToNode = -1` (base `CAREER+0x1904`)
  - `mGoodies[300] = 0` (base `CAREER+0x1F44`)
- Sets persisted option defaults (fixed CCareer region; true-view file offsets shown):
  - `CAREER_mCareerInProgress = 0` (file `0x248A`)
  - `CAREER_mSoundVolume = 0.8f` (file `0x248E`)
  - `CAREER_mMusicVolume = 0.9f` (file `0x2492`)
  - `CAREER_mInvertYFlight_{P1,P2} = 0` (file `0x249E/0x24A2`, Steam semantics `0=Off`, non-zero=On)
  - `CAREER_mInvertYWalker_{P1,P2} = 0` (file `0x24A6/0x24AA`, semantics presumed same; verification pending on walker path)
  - `CAREER_mVibration_{P1,P2} = 1` (file `0x24AE/0x24B2`)
  - `CAREER_mControllerConfig_{P1,P2} = 1` (file `0x24B6/0x24BA`)

## Notes
- This does **not** build the mission graph (no per-node world numbers, and links are left with `mToNode=-1`).
  - Mission-graph construction for a new career happens in [CCareer__Blank](CCareer__Blank.md).
- Retail `.bes` layout nuance: CCareer is copied from/to `file+2` (true dword boundaries are `file_off % 4 == 2`).

## Related
- [CCareer__Blank](CCareer__Blank.md)
- [CCareerNode__Blank](CCareerNode__Blank.md)
- `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md` (`g_InitFuncTable` section)

