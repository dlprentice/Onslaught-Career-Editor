# CCareer__CountGoodies

> Address: 0x0041c450 | Source: `references/Onslaught/Career.cpp` (`CCareer::CountGoodies()`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Count goodies whose state is at least `GS_NEW` (`> GS_INSTRUCTIONS`), returning the total unlocked-goodie count.

## Signature
```c
int CCareer__CountGoodies(void * this);
```

## Notes
- Retail implementation iterates 300 entries from `this + 0x1F44` and increments count when `state > 1`.
- This matches source `CCareer::CountGoodies()` semantics.
- Used by `CCareer__UpdateGoodieStates` to compare old vs new unlocked-goodie totals.

## Related Functions
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md) - Caller that recomputes and compares goodie totals
- [CCareer__GetAndResetGoodieNewCount](CCareer__GetAndResetGoodieNewCount.md) - Debriefing helper for newly unlocked goodies
