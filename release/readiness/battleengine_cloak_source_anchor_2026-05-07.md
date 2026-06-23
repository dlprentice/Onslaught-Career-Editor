# BattleEngine Cloak Source Anchor - 2026-05-07

Status: public-safe source-anchor RE evidence, not runtime or binary identity proof

## Objective

Extend the BattleEngine rebuild-coverage probe with a concrete cloaking behavior anchor.

## What Changed

`tools/battleengine_logic_coverage_probe.py` now checks `cloak_energy_gate_burn_and_render` in `references/Onslaught/BattleEngine.cpp`.

The anchor covers:

- `CBattleEngine::HandleCloak()`,
- the `mMinTransformEnergy` gate before cloak activation,
- active cloak energy drain through `mMaxAirEnergyCost`,
- forced `Decloak()` when energy reaches zero,
- desired stealth assignment from configuration,
- `RF_CLOAKED` render flag behavior.

`tools/battleengine_source_binary_gap_probe.py` also classifies the new anchor as source-only pending retail-binary identity.

## Validation

Commands:

```powershell
npm run test:battleengine-logic-coverage
npm run test:battleengine-source-binary-gap
```

Results after the anchor was added:

- BattleEngine logic coverage: PASS, source anchors `13/13`, doc anchors `3/3`.
- BattleEngine source-to-binary gap: PASS, source anchors `13/13`, source-only pending binary identity `13`.

## Follow-Up Read-Only Candidate Evidence

`release/readiness/battleengine_cloak_stealth_candidate_2026-05-07.md` adds bounded read-only retail-candidate evidence for stealth-style interpolation and target-range scaling in current Ghidra decompile exports.

That later pass intentionally does not promote this full source anchor to retail identity. Cloak activation, cloak button handling, active energy burn, forced decloak, `RF_CLOAKED` render identity, weapon-fired stealth reset, runtime behavior, and rebuild parity remain unproven.

## Not Claimed

- This is not retail Steam binary identity proof for the cloak path.
- This is not Ghidra mutation or read-back.
- This is not runtime gameplay proof.
- This does not prove visual cloak rendering in the WinUI app or in the game.
- This does not make the repository rebuildable from scratch.
