# CGeneralVolume__BeginWalkToFlyTransition

> Address: `0x00424990` | Source family: `CGeneralVolume`

## Status

- Named in Ghidra: yes
- Fresh read-back: `release/readiness/ghidra_cockpit_volume_unitai_signature_correction_2026-05-11.md`
- Saved signature: `void __fastcall CGeneralVolume__BeginWalkToFlyTransition(void * this)`
- Runtime behavior proof: not yet
- Exact source-file identity: not yet

## Summary

Transition helper that begins the walk-to-fly animation path.

The current decompile read-back supports the helper name with these token-level signals:

- `s_walktofly_006234b0`
- `FindAnimationIndex`
- transition animation-index storage at `this + 0x11c`
- transition state storage at `this + 0x114` with state value `2`
- `CBattleEngine__Morph` callsite read-back shows ECX-only object dispatch, not a stack parameter.

## Interpretation

This function is a concrete retail-binary anchor for the `walktofly` transition string. It pairs with `CGeneralVolume__BeginFlyToWalkTransition` and should be used as a bounded transition helper finding, not as full transform-state reconstruction.

## Boundaries

- Does not prove exact source `CBattleEngine::Morph` / transform-morph identity.
- Does not prove runtime walker-to-flight behavior in a running mission.
- Does not mutate `BEA.exe`.
- Does not prove concrete `CGeneralVolume` layout, local names, tags, or rebuild parity.
