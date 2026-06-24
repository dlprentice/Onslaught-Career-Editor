# Ghidra CSpawnPoint / CSphereTrigger Wave505 Readiness Note

Date: 2026-05-17

## Summary

Wave505 saved static Ghidra names, signatures, comments, and tags for six adjacent respawn/trigger helpers. The tranche corrects stale `CGame` ownership for spawn-point respawn helpers reached by `CGame__RespawnPlayer`, and corrects stale `CSphereTrigger__Update` naming to `CSphereTrigger__Hit`.

This is static retail Ghidra evidence only. It does not prove exact `CSpawnPoint`, `CStart`, BattleEngine init/effect, map-who, `CSphereTrigger`, monitor/list, particle-effect, or collision-report layouts, nor runtime respawn/trigger behavior, BEA launch behavior, game patching, or rebuild parity.

## Targets

| Address | Saved signature |
| --- | --- |
| `0x004e46c0` | `void __thiscall CSpawnPoint__Init(void * this, void * init)` |
| `0x004e47c0` | `void __fastcall CSpawnPoint__VFuncSlot02_RemoveFromSpawnPointList(void * this)` |
| `0x004e47e0` | `void * __thiscall CSpawnPoint__SpawnBattleEngine(void * this, int play_effect)` |
| `0x004e49f0` | `bool __fastcall CSpawnPoint__Available(void * this)` |
| `0x004e5540` | `void __fastcall CSphereTrigger__OnTriggered(void * this)` |
| `0x004e5700` | `void __thiscall CSphereTrigger__Hit(void * this, void * other_thing, void * collision_report)` |

## Evidence

- `references/Onslaught/game.cpp` shows `CGame::RespawnPlayer` selecting available `CSpawnPoint` objects and calling `SpawnBattleEngine(TRUE)`.
- Retail xrefs show `CGame__RespawnPlayer` calls the corrected spawn-point helpers at `0x004e47e0` and `0x004e49f0`.
- Retail decompile shows `0x004e5700` calls `CComplexThing__Hit(this, other_thing, collision_report)`, so the old `CSphereTrigger__Update` label was stale.
- Artifacts are under `subagents/ghidra-static-reaudit/wave505-spawnpoint-trigger-004e43d0/`.

## Verification

- `ApplySpawnPointSphereTriggerWave505.java` dry: `updated=0 skipped=6 created=0 would_create=0 renamed=0 would_rename=5 missing=0 bad=0`.
- `ApplySpawnPointSphereTriggerWave505.java` apply: `updated=6 skipped=0 created=0 would_create=0 renamed=5 would_rename=0 missing=0 bad=0`.
- `ApplySpawnPointSphereTriggerWave505.java` final verify dry: `updated=0 skipped=6 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- All three mutation passes reported `REPORT: Save succeeded`.
- Post-readback verified `6` metadata rows, `6` tag rows, `7` xref rows, `726` instruction rows, and `6` decompile exports.
- `py -3 tools\ghidra_spawnpoint_spheretrigger_wave505_probe.py --check` passed.
- `npm run test:ghidra-spawnpoint-spheretrigger-wave505` passed.
- `npm run test:ghidra-static-reaudit-queue` passed after queue refresh.
- Refreshed queue: `6078` functions, `2317` commented, `3761` commentless, `1636` undefined signatures, `1486` `param_N` signatures.
- Telemetry proxy: comment-backed `2317/6078 = 38.12%`; strict comment-plus-clean-signature `2263/6078 = 37.23%`. These are telemetry only, not completion certification.
- Backup `G:\GhidraBackups\BEA_20260517-154500_post_wave505_spawnpoint_spheretrigger_verified` verified `19` files, `158010247` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.
