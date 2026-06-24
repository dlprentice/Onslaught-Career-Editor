# BattleEngine Weapon Slot0 Function Recovery - 2026-05-09

Status: public-safe saved Ghidra function-boundary recovery, not exact source identity or runtime proof

## Objective

Continue the static re-audit campaign by turning the previously raw weapon vtable slot-0 target at `0x00506930` into a saved Ghidra function object only after preflight, dry-run, apply, and read-back evidence.

The conservative recovered name is `CWeapon__VFunc_00_00506930`. This name records vtable ownership and slot position without claiming exact `CWeapon::Fire` or `CBattleEngine::WeaponFired` identity.

## Inputs

- Pre-mutation instruction ownership export: `subagents/ghidra-static-reaudit/boundary-00506930/current/instructions_before.tsv`
- Dry-run create result: `subagents/ghidra-static-reaudit/boundary-00506930/current/create_function_dry.tsv`
- Apply result: `subagents/ghidra-static-reaudit/boundary-00506930/current/create_function_apply.tsv`
- Post-apply decompile index: `subagents/ghidra-static-reaudit/boundary-00506930/current/decompile_after/index.tsv`
- Post-apply all-functions export: `subagents/ghidra-static-reaudit/boundary-00506930/current/functions_all_after.tsv`
- Post-apply xref export: `subagents/ghidra-static-reaudit/boundary-00506930/current/xrefs_after.tsv`
- Post-apply instruction ownership export: `subagents/ghidra-static-reaudit/boundary-00506930/current/instructions_after.tsv`
- Probe: `tools/battleengine_weapon_slot0_function_recovery_probe.py`
- Probe test: `tools/battleengine_weapon_slot0_function_recovery_probe_test.py`

## Commands

Preflight and mutation:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/boundary-00506930/current/instruction_addresses.txt subagents/ghidra-static-reaudit/boundary-00506930/current/instructions_before.tsv 4 8
bash tools/run_ghidra_headless_postscript.sh CreateFunctionsFromAddressList.java subagents/ghidra-static-reaudit/boundary-00506930/current/create_function_targets.txt subagents/ghidra-static-reaudit/boundary-00506930/current/create_function_dry.tsv dry
bash tools/run_ghidra_headless_postscript.sh CreateFunctionsFromAddressList.java subagents/ghidra-static-reaudit/boundary-00506930/current/create_function_targets.txt subagents/ghidra-static-reaudit/boundary-00506930/current/create_function_apply.tsv apply
```

Read-back:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/boundary-00506930/current/readback_addresses.txt subagents/ghidra-static-reaudit/boundary-00506930/current/decompile_after 60
bash tools/run_ghidra_headless_postscript.sh ExportWeakFunctionList.java subagents/ghidra-static-reaudit/boundary-00506930/current/functions_all_after.tsv all
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/boundary-00506930/current/readback_addresses.txt subagents/ghidra-static-reaudit/boundary-00506930/current/xrefs_after.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/boundary-00506930/current/instruction_addresses.txt subagents/ghidra-static-reaudit/boundary-00506930/current/instructions_after.tsv 4 8
```

Probe validation:

```powershell
py -3 tools\battleengine_weapon_slot0_function_recovery_probe_test.py
py -3 tools\battleengine_weapon_slot0_function_recovery_probe.py --check
py -3 -m py_compile tools\battleengine_weapon_slot0_function_recovery_probe.py tools\battleengine_weapon_slot0_function_recovery_probe_test.py
cmd.exe /c npm run test:battleengine-weapon-slot0-function-recovery
```

## Result

```text
BattleEngine weapon slot0 function recovery probe
Status: PASS
Classification: slot0-function-boundary-recovered
Function: 0x00506930 CWeapon__VFunc_00_00506930
Dry-run status: would_create
Apply status: created
Legacy weak names after recovery: 0
Decompile read-back OK: True
Inner call owned by recovered function: True
```

Key facts:

| Evidence | Current result |
| --- | --- |
| Pre-mutation overlap check | `0x00506930` was unowned; `0x005069f0` and `0x005078b0` were already separate owned function entries. |
| Dry-run create | `would_create=1`, `failed=0`. |
| Apply | Created and named `0x00506930` as `CWeapon__VFunc_00_00506930`; `created=1`, `renamed=1`, `failed=0`. |
| Decompile read-back | Exported `3/3` selected targets with `0` missing and `0` failed. |
| All-functions read-back | Current function-object count is `5863`; legacy weak functions remain `0`. |
| Xref read-back | Vtable `DATA` reference `0x005dfc94 -> 0x00506930` targets the recovered function. |
| Inner call ownership | Callsite `0x005069b6 -> 0x005069f0` is now owned by `CWeapon__VFunc_00_00506930`. |

The ignored JSON report is written to `subagents/ghidra-static-reaudit/boundary-00506930/current/slot0-function-recovery.json`.

## What This Proves

- The saved Ghidra database now has a function object at `0x00506930`.
- The recovered function uses the conservative name `CWeapon__VFunc_00_00506930`.
- The function was created after a dry-run create preflight and read back through decompile, all-functions, xref, and instruction-ownership exports.
- The all-functions export advanced from `5862` to `5863` function objects while keeping the legacy weak-name count at `0`.
- The vtable slot-0 reference and the inner body call ownership now line up with the recovered function boundary.

## What This Does Not Prove

- This does not prove exact source `CWeapon::Fire` or `CBattleEngine::WeaponFired` identity.
- This does not prove retail weapon fire clears or preserves stealth.
- This does not harden the recovered function signature beyond Ghidra's current `undefined` decompiler output.
- This does not prove runtime cloak activation, target-lock behavior, projectile behavior, or fire-while-cloaked behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Outcome

The first static re-audit boundary-risk seed is closed at the Ghidra database level: `0x00506930` is no longer a raw missing function object. The remaining weapon-fire stealth gap is narrower but still open because exact source identity and runtime behavior remain unproven.

Future static work should treat `CWeapon__VFunc_00_00506930`, `CEngine__SpawnProjectileBurstFromCurrentPreset`, and `CGeneralVolume__SpawnBurstFromPresetWithFallback` as a provisional weapon/burst cluster and refine names/signatures/comments only when source, xref, decompile, or runtime evidence supports stronger claims.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses already present in repo evidence, function names/signatures, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, or raw private proof payloads.
