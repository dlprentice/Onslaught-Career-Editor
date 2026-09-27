# CCareer__ReCalcLinks

Status: active — container traversal rechecked; remaining progression policy is a retained lead
Last updated: 2026-09-27
Summary: progression traverses the returned child-link prefix, not unconditionally both slots.
Source File: references/Onslaught/Career.cpp | Binary: BEA.exe (pristine specimen below)

> Address: `0x0041bdf0`
>
> Source: `references/Onslaught/Career.cpp` (`CCareer::ReCalcLinks()`)

## September 27 traversal correction

The prior blanket source/signature verification is withdrawn. In pristine
`BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`,
complete body `[0041bdf0,0041c158)` is 872 bytes, SHA-256
`32c68885a123f7d84e7ddc865353f2d1450dd77459c429fe5d9ec5ab15702d4c`.
Call `0041be55` obtains [GetChildLinks](CCareerNode__GetChildLinks.md);
`0041be5a–0041be87` tests the returned head/item, and
`0041c0f2–0041c12e` advances through next/item with null termination.
Thus the loop sees the returned prefix: zero, one or two items. A null lower
slot suppresses a non-null higher slot during the preceding copy.

These instructions and the separate isolated container experiment establish
that composition, not an actual occurrence in shipped career data. Remaining
secondary-objective/world-500/completion policy below is retained from earlier
work and needs a complete instruction-by-instruction policy recheck and an owned
original-code graph run. The 42 container cases did not execute this routine or
save persistence. Its saved prototype is not promoted by this document.

## Purpose
Recalculate child link completion after a level win.

This is where the campaign graph “unlocks” the next missions and where alternate-path links are marked `CN_COMPLETE_BROKEN`.

## Signature
```c
void CCareer::ReCalcLinks(void);
```

## Previously reported policy (not fully revalidated)
- Traverses the returned child-link prefix of the finished node; the following eligibility policies remain to be fully revalidated:
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
