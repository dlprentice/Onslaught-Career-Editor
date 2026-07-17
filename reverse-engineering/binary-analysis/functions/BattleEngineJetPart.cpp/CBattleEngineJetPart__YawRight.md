# CBattleEngineJetPart__YawRight

> Address: `0x004109d0` | Source family: `references/Onslaught/BattleEngineJetPart.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `void __thiscall CBattleEngineJetPart__YawRight(void * this, float moveX)`
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Runtime behavior proof: not yet

## Summary

Source-aligned right-yaw helper for jet special-move input. The checked retail body tracks hard-right timing, can break a loop from a left/right threshold sequence, can start a right barrel roll with lateral velocity injection, stores the last X input, and adds strafing acceleration when energy/input thresholds agree.

The current correction supersedes the older `CGeneralVolume__HandleAxisNegativeThresholdCross` label.

## Evidence

- Source anchor: `CBattleEngineJetPart::YawRight(float vx)`.
- Read-back tokens include `moveX`, timing/state offsets around `+0x28`, `+0x3c`, `+0x40`, and `+0x48`.
- Instruction read-back includes `ret 0x4`, matching one stack float argument.

## Boundaries

- Does not prove runtime input behavior, loop-break behavior, or roll behavior.
- Does not prove concrete layouts, tags, or local variable names.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
