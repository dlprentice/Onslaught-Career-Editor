# Ghidra Cannon Activation Signature Correction - 2026-05-10

## Summary

Wave 315 completed a saved Ghidra name/signature/comment correction tranche for `9` Cannon activation, target, and helper targets.

The tranche corrected three stale saved labels:

- `0x0041b450` is now `CCannon__VFuncSlot_02_RemoveFromWorldAndForward`, superseding the older `CCannon__Destructor` label.
- `0x0041b470` is now `CCannon__AdvanceActivationAnimationState`, superseding the older `CCannon__SetState` label.
- `0x0041b590` is now `CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph`, superseding the older `CCannon__CanFire` label.

It also hardened signatures and proof-boundary comments for `CCannon__Init`, `CCannon__UpdateState`, `CCannon__GetMidpoint`, `CCannon__UpdateLinkedEffectsByHeightClearance`, `CCannon__MarkDestroyedAndResetState`, and `CCannon__SelectTarget`.

## Validation

- Headless correction dry run: `updated=0 skipped=9 renamed=0 missing=0 bad=0`.
- Headless correction apply: `updated=9 skipped=0 renamed=3 missing=0 bad=0`.
- Metadata read-back: `9/9` targets found.
- Decompile read-back: `9/9` targets dumped.
- Xref read-back: saved target xrefs present for every target.
- Instruction read-back: `1161` instruction rows.
- Vtable read-back: `CCannon`, `CSentinel`, `CWarspiteDome`, and `CGroundVehicle` rows checked.
- Focused probe: `PASS`, `9` targets, `3` renamed targets, `0` failures.
- Whole-database queue snapshot: `5868` functions, `648` commented functions, `5220` commentless functions, `2046` undefined signatures, and `2336` `param_N` signatures.

## Boundary

This is saved static Ghidra refinement only. It does not prove a tracked Stuart `Cannon.cpp` source-body match, exact source virtual names, concrete Cannon/helper layouts, local-variable names, Ghidra tags, structure types, runtime turret activation, runtime firing behavior, BEA launch behavior, game patching, or rebuild parity.

Raw read-back exports and generated proof JSON remain under ignored `subagents/`.
