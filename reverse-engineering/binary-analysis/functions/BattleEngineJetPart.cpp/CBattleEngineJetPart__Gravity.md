# CBattleEngineJetPart__Gravity

> Address: `0x004114d0` | Source family: `references/Onslaught/BattleEngineJetPart.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `float __thiscall CBattleEngineJetPart__Gravity(void * this)`
- Fresh read-back: `release/readiness/ghidra_battleengine_jetpart_signature_correction_2026-05-10.md`
- Runtime behavior proof: not yet

## Summary

Source-aligned jet gravity helper. The checked retail body returns a small gravity factor when the linked main-part energy field is zero and otherwise returns `0.0`.

The current correction supersedes the older `CGeneralVolume__GetFlagFCScalar` label.

## Evidence

- Source anchor: `CBattleEngineJetPart::Gravity()`.
- Read-back tokens include the linked main-part pointer at `+0x18`, energy-like field context around `+0xfc`, and two return paths.
- Saved signature now returns `float` and removes the old generic flag-scalar owner.

## Boundaries

- Does not prove runtime flight physics behavior.
- Does not prove exact constant names, concrete layouts, tags, or local variable names.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
