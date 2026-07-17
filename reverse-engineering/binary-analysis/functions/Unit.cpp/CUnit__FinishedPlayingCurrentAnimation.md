# CUnit__FinishedPlayingCurrentAnimation

> Address: `0x0040eeb0` | Source family: `Unit.cpp`

## Superseded

This note is retained as historical context. The saved Ghidra symbol was corrected on 2026-05-10 to [`CBattleEngine__FinishedPlayingCurrentAnimation`](../BattleEngine.cpp/CBattleEngine__FinishedPlayingCurrentAnimation.md) after source/decompile read-back matched `CBattleEngine::FinishedPlayingCurrentAnimation()`.

## Status

- Named in Ghidra: superseded; current saved name is `CBattleEngine__FinishedPlayingCurrentAnimation`
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Runtime behavior proof: not yet

## Summary

Historical broad-owner label for the animation-completion helper that checks current animation state against the fly-to-walk and walk-to-fly transition strings.

The current decompile read-back supports the helper name with these token-level signals:

- `s_flytowalk_006234bc`
- `s_walktofly_006234b0`
- `FindAnimationIndex`
- `SharedUnitAnimation__PlayAnimationByNameIfPresent`

Wave 390 corrected the old GillMHead-specific animation helper label to the shared unit-animation helper after read-back showed the target is also reached from BattleEngine morph/animation paths.

## Interpretation

This helper provides a retail-binary bridge between the transition animation strings and the BattleEngine animation completion path. It supports transition-state reconstruction, but it does not prove complete transform behavior or gameplay semantics.

## Boundaries

- Does not prove runtime transition completion behavior.
- Does not prove exact source-to-binary identity for every caller branch.
- Does not mutate `BEA.exe`.
- This file is not the current saved Ghidra symbol name; use the BattleEngine function note for current evidence.
