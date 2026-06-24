# CBattleEngineWalkerPart__ResetConfiguration

> Address: `0x004146b0` | Source family: `references/Onslaught/BattleEngineWalkerPart.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `void __thiscall CBattleEngineWalkerPart__ResetConfiguration(void * this)`
- Fresh read-back: `release/readiness/ghidra_battleengine_resetconfiguration_signature_tranche_2026-05-10.md`
- Runtime behavior proof: not yet

## Summary

Reset-configuration body for the walker part. The checked retail body drains the walker weapon pointer set, frees old primary and augmented weapon pointers, walks the linked configuration walker-weapon list at configuration `+0x40`, creates and initializes replacement weapons, then creates primary and augmented weapon slots from linked profile strings at configuration `+0x60` and `+0x64`.

## Evidence

- Source anchor: `CBattleEngineWalkerPart::ResetConfiguration()`.
- Read-back tokens include `CSPtrSet__Remove`, virtual deleting-destructor dispatches for old primary/augmented weapons, `CWorldPhysicsManager__CreateWeaponByIndex`, `CSPtrSet__AddToTail`, configuration `+0x40`, `+0x60`, and `+0x64`.
- Xrefs include `CBattleEngine__UpdateConfiguration` and `CBattleEngine__InitDashMoveParams`.
- Saved signature now removes the old `param_1` register-parameter debt and names the member receiver as `this`.

## Boundaries

- Does not prove concrete `CBattleEngineWalkerPart`, `CBattleEngineData`, or `CWeapon` layouts.
- Does not prove local variable names, structure types, or tags.
- Does not prove runtime reset/weapon behavior.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
