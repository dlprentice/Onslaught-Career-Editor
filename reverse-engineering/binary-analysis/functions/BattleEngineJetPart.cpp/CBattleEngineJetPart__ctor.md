# CBattleEngineJetPart__ctor

> Address: `0x00410210` | Source family: `references/Onslaught/BattleEngineJetPart.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `void * __thiscall CBattleEngineJetPart__ctor(void * this, void * mainPart)`
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Runtime behavior proof: not yet

## Summary

Constructor-style body for `CBattleEngineJetPart`. The checked retail body initializes the weapon set, stores the owning BattleEngine pointer, clears movement and state fields, seeds timing fields, calls `CBattleEngineJetPart__ResetConfiguration`, and sets the thruster value.

The current correction supersedes the older `CBattleEngine__InitTargetSetBucketState` label.

## Evidence

- Source anchor: `CBattleEngineJetPart::CBattleEngineJetPart(CBattleEngine* main_part)`.
- Read-back tokens include `mainPart`, `+0x18`, timing-field initialization, `ResetConfiguration`, and `ret 0x4`.
- Saved signature carries `this` and one `mainPart` stack argument.

## Boundaries

- Does not prove concrete `CBattleEngineJetPart` layout, tags, or local variable names.
- Does not prove runtime jet behavior.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
