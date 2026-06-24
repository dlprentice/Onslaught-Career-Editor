# BattleEngine Target/Profile Ghidra Read-Back - 2026-05-07

Status: public-safe read-only Ghidra evidence, not runtime or exact source-identity proof

## Objective

Add fresh machine-checkable read-back evidence for the already named BattleEngine target/profile helper cluster that supports targeting, aim selection, weapon-profile lookup, target masks, and projectile metric calculations.

## What Changed

Added:

- `tools/battleengine_target_profile_ghidra_readback_probe.py`
- `npm run test:battleengine-target-profile-ghidra-readback`

The probe validates ignored Ghidra decompile exports under `subagents/battleengine-target-profile-ghidra-readback/current/decompile/`.

## Functions Checked

- `CBattleEngine__CalcUnitOverCrossHair` (current saved name for the older aim-target helper)
- `CBattleEngine__HandleAutoAim` (current saved name for the older ballistic target-acquisition helper)
- `CBattleEngine__ApplyWeaponProfileByIndex`
- `CBattleEngine__GetWeaponProfileByIndex`
- `CBattleEngine__DoesTargetMaskMatchProfileByDistance`
- `CBattleEngine__ComputeProjectileMetricFromTargetProfile`
- `CBattleEngine__GetTargetSetEntryByIndex`

## Commands

```powershell
wsl bash -lc "cd <repo-root> && tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/battleengine-target-profile-ghidra-readback/current/addresses.txt subagents/battleengine-target-profile-ghidra-readback/current/decompile 90"
py -3 -m py_compile tools\battleengine_target_profile_ghidra_readback_probe.py
npm run test:battleengine-target-profile-ghidra-readback
```

## Result

- Headless Ghidra export passed with targets `7`, dumped `7`, missing `0`, failed `0`.
- The export printed the known GhydraMCP extension manifest warnings and `REPORT: Save succeeded`; this is treated as tool-environment/project-save noise for a read-only export script, not as an intentional Ghidra mutation.
- Python compile check passed.
- Target/profile read-back probe passed `7/7` functions.
- Raw decompile and JSON evidence stayed ignored under `subagents/`.

## What This Proves

- Fresh headless Ghidra read-back can export current decompile output for the named target/profile helper cluster.
- The selected functions retain current crosshair target, auto-aim handling, profile lookup/apply, target-mask, projectile metric, and target-set lookup tokens.
- The target/profile helper cluster is now covered by repeatable public-safe read-back validation.

## Not Claimed

- This does not prove exact Steam retail binary identity for every source target-lock or weapon behavior anchor.
- This does not prove runtime target choice, aim correctness, projectile behavior, lock acquisition, stealth behavior, or gameplay-state interpretation.
- This does not apply a Ghidra rename map.
- This does not mutate `BEA.exe`.
- This does not launch BEA.exe.
- This does not make the repository rebuildable from scratch.
