# BattleEngine Logic Coverage Probe

Status: public-safe reverse-engineering evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `5f02adef`
Evidence-report commit: e1ba16f190c91db1bd388f95d5d010d023bdca41

## Purpose

This pass adds a machine-checkable, read-only source-anchor coverage probe for core BattleEngine gameplay logic. It advances rebuild coverage by proving that specific mechanics anchors are present in the local Stuart source reference tree and are connected to tracked RE documentation.

This is not a retail-binary identity proof, Ghidra mutation, runtime gameplay proof, or open-source reimplementation.

## Current Status Update - 2026-05-07

This report remains the historical introduction for the BattleEngine logic coverage probe. The current checked source-anchor set has since expanded beyond the original 11 anchors.

Latest source-only coverage baseline:

- `npm run test:battleengine-logic-coverage`: PASS, source anchors `17/17`, doc anchors `3/3`.
- Additional source anchors added after this report cover source `CBattleEngine::Morph()`, cloak behavior, target locking, augmented-weapon charge/decay/reset, jet stall fallback, and weapon-fired stealth reset.
- Each added anchor has its own public-safe readiness note in `release/readiness/`.

The proof boundary is unchanged: these are source/reference anchors unless a later Ghidra/read-back or runtime proof identifies the exact Steam retail implementation.

## Command

```powershell
npm run test:battleengine-logic-coverage
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_logic_coverage_probe.py --check
```

Working directory:

```text
repo root
```

Result: PASS.

Important output summary:

```text
BattleEngine logic coverage probe
Status: pass
Source anchors: 11/11
Doc anchors: 3/3
- PASS: damage_stat_fixed_point: references/Onslaught/BattleEngine.cpp
- PASS: damage_shield_efficiency: references/Onslaught/BattleEngine.cpp
- PASS: damage_walker_energy_tracks_shields: references/Onslaught/BattleEngine.cpp
- PASS: damage_invulnerability_restore: references/Onslaught/BattleEngine.cpp
- PASS: transform_reject_special_moves: references/Onslaught/BattleEngine.cpp
- PASS: transform_jet_to_walker_event: references/Onslaught/BattleEngine.cpp
- PASS: transform_walker_to_jet_energy_gate: references/Onslaught/BattleEngine.cpp
- PASS: jet_energy_cost: references/Onslaught/BattleEngineJetPart.cpp
- PASS: walker_recharge: references/Onslaught/BattleEngineWalkerPart.cpp
- PASS: config_defaults: references/Onslaught/BattleEngineDataManager.cpp
- PASS: player_god_mode_toggles: references/Onslaught/Player.cpp
- PASS: doc: reverse-engineering/game-mechanics/god-mode.md
- PASS: doc: reverse-engineering/source-code/_index.md
- PASS: doc: reverse-engineering/quick-reference/source-files.md
```

## What This Proves

- The repo has a repeatable read-only probe for selected BattleEngine source mechanics anchors.
- The probe covers damage stat encoding, shield efficiency, walker energy/shield coupling, invulnerability restoration, transform rejection/gates/events, jet energy cost, walker recharge, default configuration values, and player god-mode toggles.
- The probe also checks that current RE docs point at BattleEngine source families and god-mode source/runtime posture.
- The generated JSON report is private/ignored under `subagents/` and contains repo-relative filenames, token names, line numbers, summaries, and pass/fail state.

## What This Does Not Prove

- Steam retail binary function identity for these source anchors.
- Ghidra rename-map mutation or read-back.
- Runtime gameplay-state interpretation.
- Continuous frame streaming.
- Rebuildable open-source gameplay implementation.

## Privacy / Release Safety

The committed evidence is public-safe. It does not include source excerpts, private absolute paths, private assets, runtime frame captures, screenshots, binaries, or Ghidra mutation logs.

The raw JSON report remains ignored local evidence under `subagents/battleengine-logic-coverage/`.

## Recommended Next Step

Use this probe as a baseline for deeper logic reconstruction:

1. Add more source anchors only when they map to concrete rebuild needs.
2. Pair future source anchors with retail-binary/Ghidra read-back before claiming Steam binary identity.
3. Keep runtime gameplay interpretation separate until a real observe/state proof exists.
