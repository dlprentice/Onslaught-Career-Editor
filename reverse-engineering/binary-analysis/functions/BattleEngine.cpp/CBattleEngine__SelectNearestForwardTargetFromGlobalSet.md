# CBattleEngine__SelectNearestForwardTargetFromGlobalSet

> Address: `0x00406da0` | Source family: `references/Onslaught/BattleEngine.cpp`

## Status

- Named in Ghidra: yes
- Fresh read-back: `release/readiness/battleengine_helper_ghidra_readback_2026-05-06.md`; signature/comment hardened in `release/readiness/ghidra_early_queue_signature_correction_2026-05-10.md`
- Runtime behavior proof: not yet

## Current Saved Signature

```c
void * __thiscall CBattleEngine__SelectNearestForwardTargetFromGlobalSet(
    void * this,
    void * profile,
    float originX,
    float originY,
    float originZ,
    float originW,
    float rangeScale);
```

## Summary

Target-selection helper that walks candidate sets and applies profile/mode/mask checks before returning a selected forward target.

The current decompile read-back supports the name with these token-level signals:

- `CBattleEngine__IsWeaponModeCompatibleWithMountState`
- `CBattleEngine__DoesTargetMaskMatchProfileByDistance`
- `CBattleEngine__GetProfileField98ByDistance`
- `CSPtrSet__First`
- `CSPtrSet__Next`

## Interpretation

This helper is a retail-binary anchor for target filtering and list traversal. It supports the existing forward-target selection name, but runtime target-choice behavior remains unproven until tested in a running copied-profile mission or through a narrower runtime trace.

Wave 309 keeps `originW` because the checked callers pass a 16-byte vector plus `rangeScale`, and instruction read-back shows a `ret 0x18` stack cleanup. The exact vector/profile structures are still untyped.

## Boundaries

- Does not launch the game.
- Does not mutate `BEA.exe`.
- Does not apply a Ghidra rename map.
- Does not prove semantic target choice in gameplay.
