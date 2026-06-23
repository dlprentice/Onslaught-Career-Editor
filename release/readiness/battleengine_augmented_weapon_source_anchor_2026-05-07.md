# BattleEngine Augmented Weapon Source Anchor - 2026-05-07

Status: public-safe source-anchor RE evidence, not runtime or binary identity proof

## Objective

Extend BattleEngine rebuild-coverage with a source-backed augmented-weapon meter behavior anchor.

## What Changed

`tools/battleengine_logic_coverage_probe.py` now checks `augmented_weapon_charge_decay_and_reset` in `references/Onslaught/BattleEngine.cpp`.

The anchor covers:

- augmented meter constants,
- meter gain from absorbed shield damage when augmentation is inactive,
- maximum-value activation,
- active meter decay,
- augment state activation,
- unaugment reset state.

`tools/battleengine_source_binary_gap_probe.py` also classifies the new anchor as source-only pending retail-binary identity.

## Validation

Commands:

```powershell
npm run test:battleengine-logic-coverage
npm run test:battleengine-source-binary-gap
```

Results after this anchor:

- BattleEngine logic coverage: source anchors `15/15`, doc anchors `3/3`.
- BattleEngine source-to-binary gap: source anchors `15/15`, source-only pending binary identity `15`.

## Not Claimed

- This is not retail Steam binary identity proof for augmented weapons.
- This is not Ghidra mutation or read-back.
- This is not runtime weapon behavior proof.
- This does not prove live HUD/audio behavior for augmentation.
- This does not make the repository rebuildable from scratch.
