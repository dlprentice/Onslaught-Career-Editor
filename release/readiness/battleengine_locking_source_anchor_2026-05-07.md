# BattleEngine Locking Source Anchor - 2026-05-07

Status: public-safe source-anchor RE evidence, not runtime or binary identity proof

## Objective

Extend BattleEngine rebuild-coverage with a source-backed target-locking behavior anchor.

## What Changed

`tools/battleengine_logic_coverage_probe.py` now checks `target_lock_modes_and_stealth_range` in `references/Onslaught/BattleEngine.cpp`.

The anchor covers:

- `CBattleEngine::HandleLocks()`,
- weapon readiness before acquiring new locks,
- max-lock limiting,
- direct, proximity, and sequence lock modes,
- direct-lock start calls,
- target stealth reducing effective lock range.

`tools/battleengine_source_binary_gap_probe.py` originally classified the new anchor as source-only pending retail-binary identity. Later read-back bridge evidence now promotes this anchor to partial retail candidate pending exact identity.

## Validation

Commands:

```powershell
npm run test:battleengine-logic-coverage
npm run test:battleengine-source-binary-gap
npm run test:battleengine-targeting-source-readback-bridge
```

Current results after later source/read-back bridge and gap-accounting refinement:

- BattleEngine logic coverage: source anchors `17/17`, doc anchors `3/3`.
- BattleEngine source-to-binary gap: source anchors `17/17`, source-only pending binary identity `15`, partial retail candidates pending exact identity `2`.
- Targeting source/read-back bridge: checked `5/5` source, helper-readback, and function-note anchors.

This is a partial bridge, not exact identity. Related target/projectile helper read-back exists for `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` and `CBattleEngine__SelectNearestForwardTargetFromGlobalSet`, but exact `CBattleEngine::HandleLocks` to retail helper control-flow identity is still unresolved.

## Not Claimed

- This is not retail Steam binary identity proof for target locking.
- This is not Ghidra mutation or read-back.
- This is not runtime targeting proof.
- This does not prove target locking behavior in a live copied profile.
- Partial retail helper evidence does not prove exact source method/control-flow boundaries.
- This does not make the repository rebuildable from scratch.
