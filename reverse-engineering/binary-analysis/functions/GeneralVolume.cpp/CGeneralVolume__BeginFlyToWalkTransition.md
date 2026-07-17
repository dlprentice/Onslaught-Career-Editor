# CGeneralVolume__BeginFlyToWalkTransition

> Address: `0x00424920` | Source family: `CGeneralVolume`

## Status

- Named in Ghidra: yes
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Saved signature: `void __fastcall CGeneralVolume__BeginFlyToWalkTransition(void * this)`
- Runtime behavior proof: not yet
- Exact source-file identity: not yet

## Summary

Transition helper that begins the fly-to-walk animation path.

The current decompile read-back supports the helper name with these token-level signals:

- `s_flytowalk_006234bc`
- `FindAnimationIndex`
- transition animation-index storage at `this + 0x11c`
- transition state storage at `this + 0x114` with state value `1`
- `CBattleEngine__Morph` callsite read-back shows ECX-only object dispatch, not a stack parameter.

## Interpretation

This function is a concrete retail-binary anchor for the `flytowalk` transition string. It is best treated as a helper reached from transform/state-machine investigation, not as proof of the full BattleEngine transform source method.

## Boundaries

- Does not prove exact source `CBattleEngine::Morph` / transform-morph identity.
- Does not prove runtime fly-to-walker behavior in a running mission.
- Does not mutate `BEA.exe`.
- Does not prove concrete `CGeneralVolume` layout, local names, tags, or rebuild parity.
