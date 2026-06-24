# BattleEngine Weapon Event Handler Rename - 2026-05-09

Status: public-safe saved Ghidra semantic rename, not exact source identity or runtime proof

## Objective

Continue the static re-audit campaign by correcting two provisional weapon-table names after the `0x00506930` function-boundary recovery.

The saved Ghidra names now are:

| Address | Previous name | Current name |
| --- | --- | --- |
| `0x00506930` | `CWeapon__VFunc_00_00506930` | `CWeapon__HandleFireBurstEvent` |
| `0x00505f70` | `CWeapon__VFunc_01_00505f70` | `CWeapon__scalar_deleting_dtor` |

## Inputs

- Rename map: `subagents/ghidra-static-reaudit/weapon-cluster-provisional-name/current/rename_map_weapon_event_handler.txt`
- Dry-run log: `subagents/ghidra-static-reaudit/weapon-cluster-provisional-name/current/rename_dry.log`
- Apply log: `subagents/ghidra-static-reaudit/weapon-cluster-provisional-name/current/rename_apply.log`
- Post-rename decompile index: `subagents/ghidra-static-reaudit/weapon-cluster-provisional-name/current/decompile_after_rename/index.tsv`
- Post-rename table read-back: `subagents/ghidra-static-reaudit/weapon-cluster-provisional-name/current/table_005dfc94_after_rename.tsv`
- Probe: `tools/battleengine_weapon_event_handler_rename_probe.py`
- Probe test: `tools/battleengine_weapon_event_handler_rename_probe_test.py`

## Commands

```powershell
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\weapon-cluster-provisional-name\current\rename_map_weapon_event_handler.txt
```

The bash wrapper hit the known WSL/Windows preflight path issue in this lane, so the mutation used the direct headless route after the standalone preflight passed:

```powershell
& '<GHIDRA_HOME>\support\analyzeHeadless.bat' '<GHIDRA_PROJECTS_ROOT>' 'BEA' -process 'BEA.exe' -scriptPath '.\tools' -postScript GhidraBatchRename.java '.\subagents\ghidra-static-reaudit\weapon-cluster-provisional-name\current\rename_map_weapon_event_handler.txt' dry -noanalysis
& '<GHIDRA_HOME>\support\analyzeHeadless.bat' '<GHIDRA_PROJECTS_ROOT>' 'BEA' -process 'BEA.exe' -scriptPath '.\tools' -postScript GhidraBatchRename.java '.\subagents\ghidra-static-reaudit\weapon-cluster-provisional-name\current\rename_map_weapon_event_handler.txt' apply -noanalysis
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/weapon-cluster-provisional-name/current/decompile_addresses.txt subagents/ghidra-static-reaudit/weapon-cluster-provisional-name/current/decompile_after_rename 80
bash tools/run_ghidra_headless_postscript.sh DumpPointerTable.java 0x005dfc94 48 subagents/ghidra-static-reaudit/weapon-cluster-provisional-name/current/table_005dfc94_after_rename.tsv
```

Probe validation:

```powershell
py -3 tools\battleengine_weapon_event_handler_rename_probe_test.py
py -3 tools\battleengine_weapon_event_handler_rename_probe.py --check
py -3 -m py_compile tools\battleengine_weapon_event_handler_rename_probe.py tools\battleengine_weapon_event_handler_rename_probe_test.py
cmd.exe /c npm run test:battleengine-weapon-event-handler-rename
```

## Result

```text
BattleEngine weapon event-handler rename probe
Status: PASS
Classification: weapon-event-handler-and-dtor-renamed
Rename: 0x00506930 CWeapon__VFunc_00_00506930 -> CWeapon__HandleFireBurstEvent
Rename: 0x00505f70 CWeapon__VFunc_01_00505f70 -> CWeapon__scalar_deleting_dtor
Dry summary: {'applied': 0, 'skipped': 2, 'missing': 0, 'bad': 0}
Apply summary: {'applied': 2, 'skipped': 0, 'missing': 0, 'bad': 0}
Event handler renamed: True
Scalar dtor renamed: True
Event schedules burst: True
Scalar deleting dtor evidence: True
```

## What This Proves

- The saved Ghidra database now names `0x00506930` as `CWeapon__HandleFireBurstEvent`.
- The saved Ghidra database now names `0x00505f70` as `CWeapon__scalar_deleting_dtor`.
- The dry-run and apply logs were clean for both rename rows.
- Post-rename read-back confirms the `0x005dfc94` table names at slots 0 and 1.
- The event-handler decompile contains the weapon burst event id, projectile-burst helper call, and event reschedule path.
- The destructor decompile detaches/shuts down the weapon and conditionally frees the object.

## What This Does Not Prove

- This does not prove exact source `CWeapon::Fire` or `CBattleEngine::WeaponFired` identity.
- This does not prove retail weapon fire clears or preserves stealth.
- This does not settle owner/name/signature confidence for `0x00506010` or `0x005069f0`.
- This does not harden the recovered event-handler signature beyond the current Ghidra decompiler output.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Outcome

This closes the first semantic clean-up follow-up after the raw boundary recovery: the slot-0 placeholder name is now behavior-backed, and the slot-1 destructor-like placeholder is now named as a scalar deleting destructor.

The remaining weapon-fire stealth gap is still open. Future static work should keep auditing the provisional weapon/burst cluster, especially `0x00506010` and `0x005069f0`, before making stronger source-identity or runtime-behavior claims.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses already present in repo evidence, function names, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute asset paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, or raw private proof payloads.
