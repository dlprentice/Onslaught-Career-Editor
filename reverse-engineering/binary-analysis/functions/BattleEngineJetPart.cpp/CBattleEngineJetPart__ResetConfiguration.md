# CBattleEngineJetPart__ResetConfiguration

> Address: `0x00412650` | Source family: `references/Onslaught/BattleEngineJetPart.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `void __thiscall CBattleEngineJetPart__ResetConfiguration(void * this)`
- Fresh read-back: `release/readiness/ghidra_battleengine_resetconfiguration_signature_tranche_2026-05-10.md`
- Runtime behavior proof: not yet

## Summary

Reset-configuration body for the jet part. The checked retail body drains the jet-part weapon pointer set, deletes old weapon entries, walks the linked configuration jet-weapon list at configuration `+0x50`, creates weapons by index, initializes them with the owning BattleEngine pointer, appends them to the part weapon set, and resets the current weapon index.

## Evidence

- Source anchor: `CBattleEngineJetPart::ResetConfiguration()`.
- Read-back tokens include `CSPtrSet__Remove`, `CWorldPhysicsManager__CreateWeaponByIndex`, `CSPtrSet__AddToTail`, configuration `+0x50`, and the owning main-part pointer at part `+0x18`.
- Xrefs include `CBattleEngine__UpdateConfiguration` and `CBattleEngineJetPart__ctor`.
- Saved signature now removes the old `param_1` register-parameter debt and names the member receiver as `this`.

## Boundaries

- Does not prove concrete `CBattleEngineJetPart`, `CBattleEngineData`, or `CWeapon` layouts.
- Does not prove local variable names, structure types, or tags.
- Does not prove runtime reset/weapon behavior.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
