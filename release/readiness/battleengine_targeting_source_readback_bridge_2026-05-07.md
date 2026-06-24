# BattleEngine Targeting Source/Read-Back Bridge - 2026-05-07

Status: public-safe source/read-back bridge evidence, not runtime or exact identity proof

## Objective

Add a repeatable public-safe check that connects the source target-lock anchor with existing retail helper read-back documentation for target/projectile helper functions.

## What Changed

Added:

- `tools/battleengine_targeting_source_readback_bridge_probe.py`
- `npm run test:battleengine-targeting-source-readback-bridge`

The probe checks:

- source `CBattleEngine::HandleLocks()` target-lock tokens,
- the source-only target-lock readiness note,
- current BattleEngine helper Ghidra read-back evidence,
- `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` function note,
- `CBattleEngine__SelectNearestForwardTargetFromGlobalSet` function note.

## Validation

Commands:

```powershell
py -3 -m py_compile tools\battleengine_targeting_source_readback_bridge_probe.py
npm run test:battleengine-targeting-source-readback-bridge
```

Result:

- Python compile check passed.
- Bridge probe passed `5/5` checks.
- The generated raw JSON report stayed under ignored `subagents/battleengine-targeting-source-readback-bridge/current/`.

## What This Proves

- The checked source target-lock anchor is present.
- Existing public-safe read-back evidence records related target/projectile helper tokens.
- Current function notes keep the target/projectile helper bridge visible without claiming runtime target choice.

## Not Claimed

- This does not prove exact `CBattleEngine::HandleLocks` to retail helper control-flow identity.
- This does not prove runtime target choice, lock acquisition, or projectile behavior in a copied-profile mission.
- This does not run BEA.exe.
- This does not mutate Ghidra or apply a rename map.
- This does not make the repository rebuildable from scratch.
