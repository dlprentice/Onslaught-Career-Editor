# BattleEngine Jet Stall Source Anchor - 2026-05-07

Status: public-safe source-anchor RE evidence, not runtime or binary identity proof

## Objective

Extend BattleEngine rebuild-coverage with a source-backed jet stall behavior anchor.

## What Changed

`tools/battleengine_logic_coverage_probe.py` now checks `jet_stall_forces_morph_to_walker` in `references/Onslaught/BattleEngineJetPart.cpp`.

The anchor covers:

- transform-settling time before stall detection,
- low-speed stall entry,
- stall timer capture,
- stall recovery when speed rises,
- sustained-stall morph call.

`tools/battleengine_source_binary_gap_probe.py` also classifies the new anchor as source-only pending retail-binary identity.

## Validation

Commands:

```powershell
npm run test:battleengine-logic-coverage
npm run test:battleengine-source-binary-gap
```

Results after this anchor:

- BattleEngine logic coverage: source anchors `16/16`, doc anchors `3/3`.
- BattleEngine source-to-binary gap: source anchors `16/16`, source-only pending binary identity `16`.

## Not Claimed

- This is not retail Steam binary identity proof for jet stall behavior.
- This is not Ghidra mutation or read-back.
- This is not runtime flight proof.
- This does not prove live stall timing or forced walker transition in a copied profile.
- This does not make the repository rebuildable from scratch.
