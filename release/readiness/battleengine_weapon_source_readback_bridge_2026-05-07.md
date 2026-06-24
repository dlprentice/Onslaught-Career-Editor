# BattleEngine Weapon Source/Read-Back Bridge - 2026-05-07

Status: public-safe static source/read-back bridge evidence, not runtime or exact identity proof

## Objective

Add a repeatable public-safe check that connects two source-only weapon behavior anchors with existing retail helper read-back documentation, while keeping exact source-to-retail identity and runtime weapon behavior explicitly unproven.

## What Changed

Added:

- `tools/battleengine_weapon_source_readback_bridge_probe.py`
- `npm run test:battleengine-weapon-source-readback-bridge`

Updated:

- `release/readiness/battleengine_weapon_helper_ghidra_readback_2026-05-07.md`
- `reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__UpdateWeaponEffect.md`
- `reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__AddProjectile.md`

The probe checks:

- Stuart source augmented-weapon meter tokens in `references/Onslaught/BattleEngine.cpp`,
- Stuart source weapon-fired stealth-reset tokens in `references/Onslaught/BattleEngine.cpp`,
- the source-only augmented-weapon readiness note,
- the source-only weapon-fired stealth readiness note,
- existing retail weapon-helper read-back evidence,
- the current `CBattleEngine__UpdateWeaponEffect` function note,
- the current `CBattleEngine__AddProjectile` function note.

## Validation

Commands:

```powershell
py -3 -m py_compile tools\battleengine_weapon_source_readback_bridge_probe.py
npm run test:battleengine-weapon-source-readback-bridge
```

Result:

- Python compile check passed.
- Bridge probe passed `7/7` checks.
- The generated raw JSON report stayed under ignored `subagents/battleengine-weapon-source-readback-bridge/current/`.

## What This Proves

- The checked source augmented-weapon and weapon-fired stealth anchors are present.
- Existing source-anchor evidence keeps both behaviors classified as source-only pending retail-binary identity.
- Existing retail helper read-back evidence records the related weapon-effect and projectile helper functions.
- Current function notes keep the helper evidence visible without claiming augmented-meter or stealth-reset identity.

## Not Claimed

- This does not prove exact augmented-meter control-flow identity in the Steam retail executable.
- This does not prove exact weapon-fired stealth-reset control-flow identity in the Steam retail executable.
- This does not prove runtime weapon firing, projectile behavior, stealth behavior, or augmented-weapon behavior.
- This does not run `BEA.exe`.
- This does not mutate Ghidra or apply a rename map.
- This does not make the repository rebuildable from scratch.

## Privacy

The public report contains repo-relative filenames, token names, command results, and proof boundaries only. It does not include source excerpts, binaries, private absolute paths, runtime captures, screenshots, frame data, Ghidra project files, raw decompile output, or mutation logs.
