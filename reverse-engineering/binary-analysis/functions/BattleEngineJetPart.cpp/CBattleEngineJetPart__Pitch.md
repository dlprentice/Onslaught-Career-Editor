# CBattleEngineJetPart__Pitch

> Address: `0x00410670` | Source family: `references/Onslaught/BattleEngineJetPart.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `void __thiscall CBattleEngineJetPart__Pitch(void * this, float moveY)`
- Fresh read-back: `release/readiness/ghidra_battleengine_jetpart_signature_correction_2026-05-10.md`
- Runtime behavior proof: not yet

## Summary

Source-aligned jet pitch input helper. The checked retail body applies pitch velocity from `moveY`, scales through zoom/slow-movement/transform-start context, and updates the main-part pitch velocity field.

The current correction supersedes the older `CGeneralVolume__DrainLinkedObjectFromVelocity` label.

## Evidence

- Source anchor: `CBattleEngineJetPart::Pitch(float vy)`.
- Read-back tokens include `moveY`, `CGeneralVolume__ToDoubleIdentity`, transform-start context around `+0x520`, and main-part pitch velocity around `+0x280`.
- Instruction read-back includes `ret 0x4`, matching one stack float argument.

## Boundaries

- The post-signature decompile still contains a local `unaff_` artifact, so local/type cleanup remains open.
- Does not prove runtime input behavior or exact controller dispatch.
- Does not prove concrete layouts, tags, or local variable names.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
