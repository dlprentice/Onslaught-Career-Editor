# BattleEngine Damage Source/Read-Back Bridge Probe - 2026-05-06

Status: public-safe reverse-engineering evidence

Source branch: `wip/sandbox`

Source commit before this wave: `23b8382edd77706b6ef69d0d8b60b6939c4edf4c`

Evidence-report commit: c069a694fcca228e9c4631fa9e0aa98351e52df8

Recorded at: 2026-05-06

## Scope

This proof adds a narrow, public-safe bridge between selected Stuart source damage anchors and existing retail damage-handler read-back evidence.

It does not launch the game, read or mutate `BEA.exe`, mutate Ghidra, export source excerpts, or interpret runtime gameplay state. It checks source tokens, existing source-coverage evidence, existing `CUnit__ApplyDamage` read-back evidence, and the current `CUnit__ApplyDamage` function note.

## Current Status Update - 2026-05-07

This evidence now supports partial retail candidate accounting for four selected damage source anchors:

- `damage_stat_fixed_point`
- `damage_shield_efficiency`
- `damage_walker_energy_tracks_shields`
- `damage_invulnerability_restore`

Latest source-to-binary gap baseline:

- `npm run test:battleengine-source-binary-gap`: PASS, binary families `3/3`, source anchors `17/17`.
- The current source-only pending-binary-identity count is `10`.
- The current partial retail candidate count is `7`: four damage anchors, configuration defaults, target-lock behavior, and augmented-weapon activation/depletion.

This is damage-family bridge evidence only. The checked source anchors and `CUnit__ApplyDamage` read-back evidence are related, but exact `CBattleEngine::Damage` to `CUnit__ApplyDamage` control-flow identity remains unresolved.

## Private Evidence Policy

Ignored local evidence remains under `subagents/`. This report does not include source excerpts, binaries, private absolute paths, runtime captures, screenshots, frame data, Ghidra project files, or mutation logs.

Ignored evidence includes:

- `battleengine-damage-source-readback-bridge.json`

The ignored JSON stores repo-relative filenames, token labels, line numbers, summaries, and pass/fail state only.

## Checks

| Check | Result | Selected Evidence |
| --- | --- | --- |
| Source core damage anchors | PASS | Fixed-point damage stats and shield-efficiency absorption tokens |
| Source restore/energy anchors | PASS | Walker energy/shield mirroring and vulnerability-restore tokens |
| Source coverage evidence | PASS | Existing logic coverage report records the selected damage source anchors |
| Retail damage read-back evidence | PASS | Existing mechanics read-back report records selected `CUnit__ApplyDamage` decompile tokens |
| Function note | PASS | `CUnit__ApplyDamage` note records the bridge and exact-identity boundary |

## Commands Run

Command:

```powershell
npm run test:battleengine-damage-source-readback-bridge
```

Result: PASS

Important output:

- 5/5 checks passed.
- Selected `BattleEngine.cpp` source damage anchors are present.
- Existing source-coverage evidence records the selected damage anchors.
- Existing mechanics read-back evidence records selected current `CUnit__ApplyDamage` decompile tokens.
- The function note records the bridge without claiming exact identity.

## What Is Proven

- Selected Stuart source damage anchors are present.
- Existing source-coverage evidence records the selected damage anchors.
- Fresh retail read-back evidence records selected `CUnit__ApplyDamage` damage-handler tokens.
- The current function note documents the bridge without claiming exact source-to-retail identity.
- The aggregate gap probe can treat the four selected damage anchors as partial retail candidate evidence instead of pure source-only evidence.
- The new `tools/battleengine_damage_source_readback_bridge_probe.py` script provides a repeatable public-safe validation layer over source tokens, tracked evidence, and docs.

## What Is Not Proven

- Exact `CBattleEngine::Damage` to `CUnit__ApplyDamage` control-flow identity.
- Damage, shield, energy, or invulnerability behavior in a running mission.
- Runtime gameplay-state interpretation.
- Ghidra rename-map mutation or read-back.
- Rebuildable open-source gameplay implementation.

## Release Posture

GREEN for a selected BattleEngine damage source/read-back bridge.

Remaining RE gaps are exact source-to-retail identity for full damage/energy/transform mechanics, runtime gameplay-state interpretation, and rebuildable implementation parity.
