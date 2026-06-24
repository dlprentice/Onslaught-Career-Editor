# CBattleEngineJetPart__Thrust

> Address: `0x00410310` | Source family: `references/Onslaught/BattleEngineJetPart.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `void __thiscall CBattleEngineJetPart__Thrust(void * this, float moveY)`
- Fresh read-back: `release/readiness/ghidra_battleengine_jetpart_signature_correction_2026-05-10.md`
- Runtime behavior proof: not yet

## Summary

Source-aligned jet thrust input helper. The checked retail body updates the thruster value from `moveY`, tracks the hard-forward timing window, starts loop state when the threshold sequence, energy gate, and velocity gate agree, and stores the last Y input.

The current correction supersedes the older `CGeneralVolume__HandleBoostWindowInput` label.

## Evidence

- Source anchor: `CBattleEngineJetPart::Thrust(float vy)`.
- Read-back tokens include `moveY`, state offsets around `+0x20`, `+0x24`, `+0x2c`, `+0x44`, and the main-part pitch velocity field around `+0x280`.
- Instruction read-back includes `ret 0x4`, matching one stack float argument.

## Boundaries

- Does not prove runtime input behavior or exact controller dispatch.
- Does not prove concrete layouts, tags, or local variable names.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
