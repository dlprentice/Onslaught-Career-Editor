# CCareerNode__Blank

> Address: `0x0041b740`
>
> Source: `references/Onslaught/Career.cpp` (`CCareerNode::Blank()`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Yes

## Purpose
Reset a `CCareerNode` to its default “blank” state (not completed, no links, default persistence bits, ranking unset).

## Signature
```c
void CCareerNode::Blank(void);
```

## Behavior (Retail / Steam)
Writes these fields (node-relative offsets):
- `+0x04` `mComplete = 0`
- `+0x08` `mLowerLink = -1`
- `+0x0C` `mHigherLink = -1`
- `+0x10` `mWorldNumber = 0`
- `+0x14` `mBaseThingsExists[9] = 0xFFFFFFFF` (all “base things exist” bits set)
- `+0x38` `mNumAttempts = 0`
- `+0x3C` `mRanking = -1.0f` (float bits `0xBF800000`)

Important nuance:
- The retail node struct has a leading dword at `+0x00` (documented as `state` in `struct-layouts.md`). This function does **not** write it; preserve it in save patching.

## Notes
- This is the retail mapping of Stuart’s `CCareerNode::Blank()`; older docs called it “Init”.

## Related Functions
- [CCareerNode__SetBaseThingExistTo](CCareerNode__SetBaseThingExistTo.md) - Modify per-level persistence bits (`mBaseThingsExists`)
- [CCareer__DoesBaseThingExist](CCareer__DoesBaseThingExist.md) - Query persistence bits by world number + offset
- [CCareer__Blank](CCareer__Blank.md) - Bulk career reset / graph initialization
