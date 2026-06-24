# BattleEngine Weapon Burst Raw Callsites - 2026-05-09

Status: public-safe read-only Ghidra instruction-window triage, not function-boundary, retail identity, or runtime proof

## Objective

Continue from `release/readiness/battleengine_weapon_burst_caller_xrefs_2026-05-09.md`.

That pass showed two raw no-function callsites into `CGeneralVolume__SpawnBurstFromPresetWithFallback` at `0x00506010`: `0x0044e093` and `0x004f4bd6`. This pass asks whether bounded instruction windows around those raw callsites expose an obvious Weapon- or BattleEngine-owned direct caller.

## Inputs

- Raw callsite target list: `subagents/battleengine-weapon-burst-raw-callsites/current/raw_callsite_addresses.txt`
- Read-only instruction-window export: `subagents/battleengine-weapon-burst-raw-callsites/current/raw_callsite_instructions.tsv`
- Probe: `tools/battleengine_weapon_burst_raw_callsite_probe.py`
- Probe test: `tools/battleengine_weapon_burst_raw_callsite_probe_test.py`

## Commands

Read-only Ghidra export:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/battleengine-weapon-burst-raw-callsites/current/raw_callsite_addresses.txt subagents/battleengine-weapon-burst-raw-callsites/current/raw_callsite_instructions.tsv 20 36
```

Probe validation:

```powershell
py -3 tools\battleengine_weapon_burst_raw_callsite_probe_test.py
py -3 tools\battleengine_weapon_burst_raw_callsite_probe.py --check
py -3 -m py_compile tools\battleengine_weapon_burst_raw_callsite_probe.py tools\battleengine_weapon_burst_raw_callsite_probe_test.py
cmd.exe /c npm run test:battleengine-weapon-burst-raw-callsites
```

## Result

```text
BattleEngine weapon burst raw callsite probe
Status: PASS
Classification: raw-callsites-unowned-shared-context
Instruction rows: 114
Target callsites: 2
Owned function rows: 0
Weapon/BattleEngine-named rows: 0
```

Key read-only facts:

| Evidence | Current result |
| --- | --- |
| Target helper | `CGeneralVolume__SpawnBurstFromPresetWithFallback` at `0x00506010`. |
| Raw callsites checked | `0x0044e093` and `0x004f4bd6`. |
| Instruction-window rows | `114` rows across both bounded windows. |
| Target calls observed | Both checked windows contain the expected call into `0x00506010`. |
| Owned-function rows | `0`; the checked windows remain raw/no-function rows in the current export. |
| Weapon/BattleEngine-named rows | `0` in the checked export. |
| Context signals | `0x0044e093` includes list/range context; `0x004f4bd6` includes floating-point threshold/setup context. |

The ignored JSON report is written to `subagents/battleengine-weapon-burst-raw-callsites/current/weapon-burst-raw-callsites.json`.

## What This Proves

- The current read-only instruction-window export has both raw callsites into `0x00506010`.
- Both checked callsite windows are currently outside Ghidra-owned function rows in this export.
- The checked windows contain shared context signals rather than an obvious Weapon- or BattleEngine-named owner.

## What This Does Not Prove

- This does not create, rename, or mutate a Ghidra function boundary.
- This does not prove exact source `CWeapon::Fire` or `CBattleEngine::WeaponFired` identity.
- This does not prove whether retail weapon fire clears stealth.
- This does not rule out indirect, virtual-dispatch, callback, inlined, or runtime-only weapon-fire behavior elsewhere.
- This does not prove runtime cloak activation, target-lock behavior, projectile behavior, or fire-while-cloaked behavior.
- This does not patch or launch `BEA.exe` and does not inspect private runtime captures.
- This does not make the repository rebuildable from scratch.

## Outcome

`weapon_fire_breaks_stealth` remains source-only in aggregate source-to-binary gap accounting. This pass further weakens a clean weapon-specific interpretation for `0x00506010`: the named direct callers looked shared in the prior wave, and the two raw no-function callsites do not currently expose an obvious Weapon/BattleEngine owner in bounded instruction windows.

Future static work should inspect only a concrete enclosing boundary, vtable, or caller path that can be tied back to weapon/fire input. Otherwise, runtime cloak/fire proof still needs a copied-profile setup with a verified cloak-active baseline.

## Privacy / Release Safety

This report stores repo-relative filenames, public addresses already present in repo evidence, current function names, command summaries, instruction counts, context labels, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, or Ghidra mutation logs.
