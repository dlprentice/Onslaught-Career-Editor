# Ghidra Weapon Burst Raw Boundary Recovery - 2026-05-10

Status: public-safe saved-Ghidra function-boundary/comment recovery, not exact source identity or runtime proof

## Objective

Follow up `release/readiness/battleengine_weapon_burst_raw_callsites_2026-05-09.md` and `release/readiness/ghidra_weapon_burst_provisional_review_2026-05-09.md`.

Those passes left two direct callsites into `ProjectileBurst__SpawnFromPercentBucketFallback` at `0x00506010` outside saved Ghidra function ownership:

- `0x0044e093`
- `0x004f4bd6`

This pass asks whether those raw callsites have recoverable enclosing boundaries that can be saved conservatively without claiming a weapon owner, BattleEngine owner, exact source method, or runtime stealth behavior.

## Inputs

- Create-function target list: `subagents/ghidra-static-reaudit/weapon-burst-raw-boundary-recovery/current/create_function_targets.txt`
- Create dry/apply reports: `subagents/ghidra-static-reaudit/weapon-burst-raw-boundary-recovery/current/create_function_dry.tsv` and `subagents/ghidra-static-reaudit/weapon-burst-raw-boundary-recovery/current/create_function_apply.tsv`
- Saved comment inputs: `subagents/ghidra-static-reaudit/weapon-burst-raw-boundary-recovery/current/comments.tsv` and `subagents/ghidra-static-reaudit/weapon-burst-raw-boundary-recovery/current/target_comments.tsv`
- Read-back metadata/decompile/xref/instruction exports under `subagents/ghidra-static-reaudit/weapon-burst-raw-boundary-recovery/current/`
- Probe: `tools/ghidra_weapon_burst_raw_boundary_recovery_probe.py`
- Probe test: `tools/ghidra_weapon_burst_raw_boundary_recovery_probe_test.py`

## Commands

Focused Ghidra mutation and read-back:

```powershell
analyzeHeadless.bat <ghidra-projects-root> BEA -process BEA.exe -scriptPath tools -postScript CreateFunctionsFromAddressList.java subagents\ghidra-static-reaudit\weapon-burst-raw-boundary-recovery\current\create_function_targets.txt subagents\ghidra-static-reaudit\weapon-burst-raw-boundary-recovery\current\create_function_dry.tsv dry -noanalysis
analyzeHeadless.bat <ghidra-projects-root> BEA -process BEA.exe -scriptPath tools -postScript CreateFunctionsFromAddressList.java subagents\ghidra-static-reaudit\weapon-burst-raw-boundary-recovery\current\create_function_targets.txt subagents\ghidra-static-reaudit\weapon-burst-raw-boundary-recovery\current\create_function_apply.tsv apply -noanalysis
analyzeHeadless.bat <ghidra-projects-root> BEA -process BEA.exe -scriptPath tools -postScript GhidraApplyFunctionCommentsFromTsv.java subagents\ghidra-static-reaudit\weapon-burst-raw-boundary-recovery\current\comments.tsv apply -noanalysis
analyzeHeadless.bat <ghidra-projects-root> BEA -process BEA.exe -scriptPath tools -postScript GhidraApplyFunctionCommentsFromTsv.java subagents\ghidra-static-reaudit\weapon-burst-raw-boundary-recovery\current\target_comments.tsv apply -noanalysis
```

Probe validation:

```powershell
py -3 tools\ghidra_weapon_burst_raw_boundary_recovery_probe_test.py
cmd.exe /c npm run test:ghidra-weapon-burst-raw-boundary-recovery
py -3 -m py_compile tools\ghidra_weapon_burst_raw_boundary_recovery_probe.py tools\ghidra_weapon_burst_raw_boundary_recovery_probe_test.py
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

## Result

```text
Ghidra weapon-burst raw boundary recovery probe
Status: PASS
Recovered boundaries: 2
weapon_fire_breaks_stealth: unresolved
```

Saved Ghidra function-boundary results:

| Address | Saved name | Checked callsite | Context label |
| --- | --- | --- | --- |
| `0x0044e020` | `ProjectileBurstCallerBoundary_0044e020` | `0x0044e093 -> 0x00506010` | list/range context |
| `0x004f4920` | `ProjectileBurstCallerBoundary_004f4920` | `0x004f4bd6 -> 0x00506010` | floating-point threshold/setup context |

Read-back facts:

| Evidence | Current result |
| --- | --- |
| Create-function dry run | `would_create` for both target starts; no failed rows. |
| Create-function apply | `created` and renamed both functions; save succeeded. |
| Boundary comments | Saved proof-boundary comments on both recovered boundary functions. |
| Target comments | Updated `0x00506010` / `0x005069f0` comments so they no longer say the two raw callsites are unbounded. |
| Metadata read-back | `4/4` rows OK for `0x00506010`, `0x005069f0`, `0x0044e020`, and `0x004f4920`. |
| Decompile read-back | `2/2` recovered boundary decompiles OK. |
| Xref read-back | `0x0044e093` now resolves from `ProjectileBurstCallerBoundary_0044e020`; `0x004f4bd6` now resolves from `ProjectileBurstCallerBoundary_004f4920`. |
| Instruction read-back | Both checked callsites now carry the recovered boundary function entry/name. |
| Queue refresh | `5868` functions, `513` commented functions, `5355` commentless functions, `2069` undefined signatures, `2437` `param_N` signatures, `0` helpers, `0` wrappers, `0` uncertain owners. |

The ignored JSON report is written to `subagents/ghidra-static-reaudit/weapon-burst-raw-boundary-recovery/current/weapon-burst-raw-boundary-recovery.json`.

## What This Proves

- The current saved Ghidra database now has two owner-neutral function boundaries for the two prior raw callsites into `ProjectileBurst__SpawnFromPercentBucketFallback`.
- The saved xrefs and instruction rows now resolve those callsites through `ProjectileBurstCallerBoundary_0044e020` and `ProjectileBurstCallerBoundary_004f4920`.
- The target helper comments have been corrected so they no longer describe those two callsites as still lacking boundaries.

## What This Does Not Prove

- This does not identify exact retail `CWeapon::Fire`.
- This does not identify exact retail `CBattleEngine::WeaponFired`.
- This does not close `weapon_fire_breaks_stealth`.
- This does not prove whether retail weapon fire clears stealth.
- This does not prove runtime cloak activation or fire-while-cloaked behavior.
- This does not claim final signatures, structure layouts, tags, local-variable names, or source identity for the recovered boundary functions.
- This does not patch, launch, or mutate `BEA.exe`.

## Outcome

The raw function-boundary part of the `0x00506010` caller gap is now narrowed: both prior raw callsites have saved owner-neutral boundaries. The stronger gameplay/source question remains open. `weapon_fire_breaks_stealth` stays source-only until a later static identity pass or copied-profile runtime proof closes it.

## Privacy / Release Safety

This report stores repo-relative filenames, public addresses already present in repo evidence, current function names, command summaries, row counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, or raw Ghidra mutation logs.
