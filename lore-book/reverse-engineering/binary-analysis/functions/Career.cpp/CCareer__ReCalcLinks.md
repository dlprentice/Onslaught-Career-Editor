# CCareer__ReCalcLinks

> Address: `0x0041bdf0`
>
> Source: `references/Onslaught/Career.cpp` (`CCareer::ReCalcLinks()`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Yes

## Purpose
Recalculate child link completion after a level win.

This is where the campaign graph “unlocks” the next missions and where alternate-path links are marked `CN_COMPLETE_BROKEN`.

## Signature
```c
void CCareer::ReCalcLinks(void);
```

## Key Rules (Source-Parity)
- Iterates the two child links of the finished node:
  - Lower link: always eligible to complete.
  - Higher link: only completes if `END_LEVEL_DATA.IsAllSecondaryObjectivesComplete()` is true.
- Special-case `world == 500`: completion is gated by tech-slot bits (see below).
- When a link is marked complete:
  - Set `link->mLinkType = CN_COMPLETE (1)`.
  - If the destination node has *other* parent links that are also `CN_COMPLETE`, mark those other links as `CN_COMPLETE_BROKEN (2)` so only the active path stays “solid”.

### World 500 Special-Case (Rocket/Sub Branch)
For world 500 only, link completion ignores secondary objectives and instead checks tech-slot flags:
- `SLOT_500_ROCKET` = 61
- `SLOT_500_SUB` = 62

The game compares whether the iterated child link is the finished node’s “higher” link to choose which slot flag applies.

## Related Functions
- [CCareer__Update](CCareer__Update.md) - Calls this after a win
- [CCareer__Blank](CCareer__Blank.md) - Initializes the `level_structure` graph used by this logic
