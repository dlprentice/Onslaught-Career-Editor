# CCareer__StaticInitDefaults

<!-- ghidra-name-drift-accepted: 0x0041b6a0 CCareer_T3_0041b6a0 (2026-08-17) -->

> Address: `0x0041b6a0`
>
> **The saved Ghidra name is now the Tier-3 placeholder `CCareer_T3_0041b6a0`.**
> This page keeps its old title so existing references still resolve.
>
> Source: startup init-table entry (`g_InitFuncTable[3]` @ `0x006220b0`).
> Defaults align with `references/Onslaught/Career.cpp` (`CCareer::CCareer()`), and node/link/goodie clearing overlaps `CCareer::Blank()` but does **not** build the mission graph.

## Name demotion — 2026-08-17

The 2026-08-17 anchor audit
([`name-cohort-promotion-manifest-2026-08-17.tsv`](../../name-cohort-promotion-manifest-2026-08-17.tsv))
found no `CCareer` type descriptor anywhere in the shipped image and no vtable
owning this VA, so the descriptive name was replaced by a neutral placeholder.

That audit graded names against RTTI and vtable anchors only. It did not
re-read the body, and it does not touch the two independent things this page
actually stands on: that `g_InitFuncTable[3]` at `0x006220B0` points here, and
the measured field offsets and default values recorded below. Those remain as
measured. What is withdrawn is the implication that the image itself proves the
`CCareer::` ownership and the `StaticInitDefaults` spelling.

## Status
- **Named in Ghidra:** yes, but only as the placeholder `CCareer_T3_0041b6a0`
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
