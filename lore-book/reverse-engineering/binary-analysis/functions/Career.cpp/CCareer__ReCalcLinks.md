# CCareer__ReCalcLinks

> Address: `0x0041bdf0`
>
> Source: `references/Onslaught/Career.cpp` (`CCareer::ReCalcLinks()`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
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

## Wave1049 Re-Audit

Wave1049 (`endlevel-objective-progression-review-wave1049`) re-read `0x0041bdf0 CCareer__ReCalcLinks` with no mutation. Fresh Ghidra evidence keeps the saved signature `void __fastcall CCareer__ReCalcLinks(void * this)`, keeps the call to `0x004496e0 CEndLevelData__IsAllSecondaryObjectivesComplete`, and keeps the world-500 branch at career `+0x240c` bits `29/30`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-134936_post_wave1049_endlevel_objective_progression_review_verified`. Runtime progression/save outcome behavior, exact layout identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Related Functions
- [CCareer__Update](CCareer__Update.md) - Calls this after a win
- [CCareer__Blank](CCareer__Blank.md) - Initializes the `level_structure` graph used by this logic
