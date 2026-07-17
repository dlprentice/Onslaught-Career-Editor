# CBattleEngine__FinishedPlayingCurrentAnimation

> Address: `0x0040eeb0` | Source family: `references/Onslaught/BattleEngine.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `int __thiscall CBattleEngine__FinishedPlayingCurrentAnimation(void * this)`
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Runtime behavior proof: not yet

## Summary

Transition-completion helper that checks the current render animation against the fly-to-walk and walk-to-fly transition strings, then switches to the settled walk or fly animation when a transition has completed.

The current Ghidra correction supersedes the older broad `CUnit__FinishedPlayingCurrentAnimation` owner label. Source/decompile evidence supports the narrower `CBattleEngine::FinishedPlayingCurrentAnimation()` identity.

## Evidence

- Source anchor: `CBattleEngine::FinishedPlayingCurrentAnimation()` in `references/Onslaught/BattleEngine.cpp`.
- Read-back tokens include `flytowalk`, `walktofly`, animation-index lookup, and the next-animation dispatch helper.
- Saved signature uses a `this` pointer and removes the old generic `param_1` signature.

## Boundaries

- Does not prove runtime transition completion behavior.
- Does not prove concrete `CBattleEngine` layout, tags, local variable names, or structure types.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
