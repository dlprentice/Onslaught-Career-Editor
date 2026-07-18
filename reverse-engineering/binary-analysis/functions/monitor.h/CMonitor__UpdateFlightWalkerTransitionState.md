# CMonitor__UpdateFlightWalkerTransitionState

> Address: `0x0040a580` | Historical alias; current saved Ghidra name: `CBattleEngine__Morph`

## Status

- Named in Ghidra: yes
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Runtime behavior proof: bounded walker-to-jet path accepted

## Summary

Historical monitor/state helper name for the current `CBattleEngine__Morph` saved Ghidra function. The 2026-05-09 transition/targeting tranche corrected the owner/source bridge after re-reading the body against Stuart `CBattleEngine::Morph()`.

The current decompile read-back supports the helper name with these token-level signals:

- `CGeneralVolume__BeginFlyToWalkTransition`
- `CGeneralVolume__BeginWalkToFlyTransition`
- `SharedUnitAnimation__PlayAnimationByNameIfPresent`
- `s_flytowalk_006234bc`
- `s_walktofly_006234b0`
- `0x1771` / `6000` transform event IDs
- `CBattleEngine__SwapPrimarySecondaryPartReadersForState`
- source-parity energy-gate tokens
- `EVENT_MANAGER`

## Interpretation

This is the clearest current retail-binary state-machine anchor for fly/walker transition handling. It ties the two `CGeneralVolume` transition helpers to the source `CBattleEngine::Morph()` event, state, and energy-gate anchors. Concrete layout, tags/local names, and complete source-level control flow remain separate proof targets.

A copied-runtime Level 100 control and two early-flight runs now confirm the
player-one path through this body: raw state `2` is rejected while flight is
disabled; enabled runs write state `1` and later settle at state `3`. The two
state-`1` intervals were 535.359–537.249 ms. See
[`walker-transform-morph-timing-v1.json`](../../../game-mechanics/walker-transform-morph-timing-v1.json).

Wave 390 corrected the old GillMHead-specific playback-helper label to the shared unit-animation helper because the same target is used by BattleEngine morph/animation paths.

## Boundaries

- Proves only the bounded player-one walker-to-jet path described above.
- Does not prove concrete `CBattleEngine` layout or local names.
- Does not prove runtime event behavior.
- Does not mutate `BEA.exe`.
- Does not apply a Ghidra rename map.
