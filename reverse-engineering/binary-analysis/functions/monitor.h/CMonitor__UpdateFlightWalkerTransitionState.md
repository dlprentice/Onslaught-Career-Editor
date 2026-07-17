# CMonitor__UpdateFlightWalkerTransitionState

> Address: `0x0040a580` | Historical alias; current saved Ghidra name: `CBattleEngine__Morph`

## Status

- Named in Ghidra: yes
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Runtime behavior proof: not yet

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

This is the clearest current retail-binary state-machine anchor for fly/walker transition handling. It ties the two `CGeneralVolume` transition helpers to the source `CBattleEngine::Morph()` event, state, and energy-gate anchors. Runtime behavior, concrete layout, tags/local names, and complete source-level control flow remain separate proof targets.

Wave 390 corrected the old GillMHead-specific playback-helper label to the shared unit-animation helper because the same target is used by BattleEngine morph/animation paths.

## Boundaries

- Does not prove runtime `CBattleEngine::Morph()` behavior.
- Does not prove concrete `CBattleEngine` layout or local names.
- Does not prove runtime event behavior.
- Does not mutate `BEA.exe`.
- Does not apply a Ghidra rename map.
