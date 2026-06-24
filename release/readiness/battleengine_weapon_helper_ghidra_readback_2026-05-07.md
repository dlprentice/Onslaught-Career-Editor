# BattleEngine Weapon Helper Ghidra Read-Back - 2026-05-07

Status: public-safe read-only Ghidra evidence, not runtime or exact source-identity proof

## Objective

Add fresh machine-checkable read-back evidence for two already named BattleEngine weapon helper functions:

- `CBattleEngine__UpdateWeaponEffect`
- `CBattleEngine__AddProjectile`

These are weapon-effect and projectile helper functions. They provide related weapon-system read-back evidence, while stealth, augmented-weapon behavior, and exact source-to-retail identity remain separate proof questions.

## What Changed

Added:

- `tools/battleengine_weapon_helper_ghidra_readback_probe.py`
- `npm run test:battleengine-weapon-helper-ghidra-readback`

The probe validates ignored Ghidra decompile exports under `subagents/battleengine-weapon-helper-ghidra-readback/current/decompile/`.

## Commands

```powershell
wsl bash -lc "cd <repo-root> && tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/battleengine-weapon-helper-ghidra-readback/current/addresses.txt subagents/battleengine-weapon-helper-ghidra-readback/current/decompile 90"
py -3 -m py_compile tools\battleengine_weapon_helper_ghidra_readback_probe.py
npm run test:battleengine-weapon-helper-ghidra-readback
```

## Result

- Headless Ghidra export passed with targets `2`, dumped `2`, missing `0`, failed `0`.
- The export printed the known GhydraMCP extension manifest warnings and `REPORT: Save succeeded`; this is treated as tool-environment/project-save noise for a read-only export script, not as an intentional Ghidra mutation.
- Python compile check passed.
- Weapon helper read-back probe passed `2/2` functions.
- Raw decompile and JSON evidence stayed ignored under `subagents/`.

## What This Proves

- Fresh headless Ghidra read-back can export current decompile output for the already named weapon helpers.
- `CBattleEngine__UpdateWeaponEffect` retains selected allocation, life, squared-life, gravity, and container-call tokens.
- `CBattleEngine__AddProjectile` retains selected disabled-flag, active-list, duplicate-walk, duration, and tail-add tokens.

## Not Claimed

- This does not prove exact Steam retail identity for every source weapon, augmented-weapon, or stealth anchor.
- This does not prove runtime weapon firing, projectile behavior, target-lock behavior, stealth reset, or augmented-weapon behavior.
- This does not apply a Ghidra rename map.
- This does not mutate `BEA.exe`.
- This does not launch BEA.exe.
- This does not make the repository rebuildable from scratch.
