# BattleEngine Weapon Stealth Source Anchor - 2026-05-07

Status: public-safe source-anchor RE evidence, not runtime or binary identity proof

## Objective

Extend BattleEngine rebuild-coverage with a source-backed weapon/stealth interaction anchor.

## What Changed

`tools/battleengine_logic_coverage_probe.py` now checks `weapon_fire_breaks_stealth` in `references/Onslaught/BattleEngine.cpp`.

The anchor covers:

- `CBattleEngine::WeaponFired(...)`,
- the jet weapon-fired path,
- the walker weapon-fired path,
- stealth reset after either weapon path reports a fired weapon.

`tools/battleengine_source_binary_gap_probe.py` also classifies the new anchor as source-only pending retail-binary identity.

## Validation

Commands:

```powershell
npm run test:battleengine-logic-coverage
npm run test:battleengine-source-binary-gap
npm run test:battleengine-weapon-stealth-name-scan
```

Current results after later gap-accounting refinement:

- BattleEngine logic coverage: source anchors `17/17`, doc anchors `3/3`.
- BattleEngine source-to-binary gap: source anchors `17/17`, source-only pending binary identity `1`, partial retail candidates pending exact identity `16`.
- Weapon-fired stealth name scan: checked `5862` current Ghidra function-name rows and found `0` strict WeaponFired/Stealth/Cloak/Decloak named candidates.
- Weapon-fired stealth operand search: checked `377` current Ghidra operand-token rows for suspected stealth-adjacent fields and found `0` weapon/fire/projectile object-offset rows.
- WeaponFired source callsite probe: checked `8` source occurrences and found `0` unexpected direct source callsites outside expected declarations/definitions and the part-delegation calls inside `CBattleEngine::WeaponFired`.

The name, operand, and source-callsite scans are triage only. They keep `weapon_fire_breaks_stealth` in source-only pending retail-binary identity status until a later source-to-binary pass finds a concrete decompile/control-flow candidate or copied-profile runtime proof answers the behavior directly.

## Not Claimed

- This is not retail Steam binary identity proof for stealth reset on weapon fire.
- This is not Ghidra mutation or read-back.
- This is not runtime stealth or combat proof.
- This does not prove live targeting consequences after firing.
- The strict function-name scan does not prove absence of a retail implementation.
- This does not make the repository rebuildable from scratch.
