# CBattleEngineJetPart__Turn

> Address: `0x00410490` | Source family: `references/Onslaught/BattleEngineJetPart.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `void __thiscall CBattleEngineJetPart__Turn(void * this, float moveX)`
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Runtime behavior proof: not yet

## Summary

Source-aligned jet turn helper. The checked retail body applies yaw and roll velocity through configuration turn-rate context, zoom scaling, low-speed grounded damping, slow-movement scaling, and transform-start interpolation before updating main-part yaw/roll velocity fields.

The current correction supersedes the older `CGeneralVolume__ApplyInputDampingToVelocity` label.

## Evidence

- Source anchor: `CBattleEngineJetPart::Turn(float vx)`.
- Read-back tokens include configuration/zoom context, `CGeneralVolume__ToDoubleIdentity`, and main-part yaw/roll velocity fields around `+0x278` and `+0x27c`.
- Instruction read-back includes `ret 0x4`, matching one stack float argument.

## Boundaries

- The post-signature decompile still contains local `unaff_` artifacts, so local/type cleanup remains open.
- Does not prove runtime input behavior or exact controller dispatch.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
