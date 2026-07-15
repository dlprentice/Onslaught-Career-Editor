# CBattleEngine__SelectNearestForwardTargetFromGlobalSet

> Address: `0x00406da0` | Source family: `references/Onslaught/BattleEngine.cpp`

## Status

- Named in Ghidra: yes
- Fresh read-back: `release/readiness/battleengine_helper_ghidra_readback_2026-05-06.md`; signature/comment hardened in `release/readiness/ghidra_early_queue_signature_correction_2026-05-10.md`
- Source alignment candidate: `CBattleEngine::GetClosestLockableUnit`
- Source candidate status: `hypothesis-only`; no reviewed retail rename was applied
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

Target-selection helper that walks a global candidate set and applies
side/profile, distance, forward-deflection, and existing-lock checks before
returning the nearest retained candidate or null.

The current decompile read-back supports the name with these token-level signals:

- `CUnit__IsCandidateSideCompatibleForTargeting`
- `CWeapon__DoesTargetMaskMatchDistanceProfile`
- `CWeapon__GetDistanceProfileField98`
- `CSPtrSet__First`
- `CSPtrSet__Next`

## Interpretation

This helper is a retail-binary anchor for target filtering and list traversal.
Its body and the three calls from `CBattleEngine__HandleLocks` align closely
with pinned-source `CBattleEngine::GetClosestLockableUnit`, but that exact source
identity remains a hypothesis rather than an accepted retail rename. Runtime
target-choice behavior remains unproven until a separately authorized copied-
runtime observation establishes it.

Wave 309 keeps `originW` because the checked callers pass a 16-byte vector plus `rangeScale`, and instruction read-back shows a `ret 0x18` stack cleanup. The exact vector/profile structures are still untyped.

## Boundaries

- Does not launch the game.
- Does not mutate `BEA.exe`.
- Does not apply a Ghidra rename map.
- Does not prove semantic target choice in gameplay.
- Does not promote source stealth/range semantics into a retail behavior claim.
- Does not accept `CBattleEngine::GetClosestLockableUnit` as the saved retail name.
