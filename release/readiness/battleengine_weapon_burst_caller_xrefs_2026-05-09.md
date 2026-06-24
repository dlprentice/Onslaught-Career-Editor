# BattleEngine Weapon Burst Caller Xrefs - 2026-05-09

Status: public-safe read-only Ghidra xref/caller triage, not retail identity or runtime proof

## Objective

Continue the caller-side investigation from `release/readiness/battleengine_weapon_slot0_xrefs_2026-05-09.md`.

That prior pass showed `0x005069f0` is reached from both the raw slot-0 stub and the currently named `CGeneralVolume__SpawnBurstFromPresetWithFallback` at `0x00506010`. This pass asks whether direct xrefs into `0x00506010` look weapon-specific or instead show a broader shared burst/effect path.

## Inputs

- Xref target list: `subagents/battleengine-weapon-burst-caller-xrefs/current/addresses.txt`
- Read-only xref export: `subagents/battleengine-weapon-burst-caller-xrefs/current/burst_caller_xrefs.tsv`
- Read-only caller decompile index: `subagents/battleengine-weapon-burst-caller-xrefs/current/caller-decompile/index.tsv`
- Probe: `tools/battleengine_weapon_burst_caller_xref_probe.py`
- Probe test: `tools/battleengine_weapon_burst_caller_xref_probe_test.py`

## Commands

Read-only Ghidra exports:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/battleengine-weapon-burst-caller-xrefs/current/addresses.txt subagents/battleengine-weapon-burst-caller-xrefs/current/burst_caller_xrefs.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/battleengine-weapon-burst-caller-xrefs/current/caller_decompile_addresses.txt subagents/battleengine-weapon-burst-caller-xrefs/current/caller-decompile 40
```

Probe validation:

```powershell
py -3 tools\battleengine_weapon_burst_caller_xref_probe_test.py
py -3 tools\battleengine_weapon_burst_caller_xref_probe.py --check
py -3 -m py_compile tools\battleengine_weapon_burst_caller_xref_probe.py tools\battleengine_weapon_burst_caller_xref_probe_test.py
cmd.exe /c npm run test:battleengine-weapon-burst-caller-xrefs
```

## Result

```text
BattleEngine weapon burst caller xref probe
Status: PASS
Classification: burst-caller-xrefs-shared-effect-path
Xref rows: 10
Named caller functions: 6
Raw no-function callsites: 0x0044e093, 0x004f4bd6
Weapon-named caller rows: 0
```

Key read-only facts:

| Evidence | Current result |
| --- | --- |
| Target | `CGeneralVolume__SpawnBurstFromPresetWithFallback` at `0x00506010`. |
| Direct xref rows | `10` checked direct xref rows. |
| Named caller count | `6` current named caller functions. |
| Named caller functions | `CUnitAI__TrySpawnOrFinalizeAttachedUnit`, `CSentinel__UpdateFlamethrowers`, `CEngine_Unk_0050a080__Wrapper_00411bf0`, `CGeneralVolume__UpdateCurrentEntryProgressAndRefresh`, `CEngine_Unk_00506010__Wrapper_00411b90`, and `CGeneralVolume__ResetState588AndRefreshCurrentEntry`. |
| Raw no-function callsites | `0x0044e093` and `0x004f4bd6`. |
| Weapon/BattleEngine-named direct callers | `0` in the checked export. |

The ignored JSON report is written to `subagents/battleengine-weapon-burst-caller-xrefs/current/weapon-burst-caller-xrefs.json`.

## What This Proves

- The current read-only xref export has ten direct xref rows to `CGeneralVolume__SpawnBurstFromPresetWithFallback` at `0x00506010`.
- The checked direct named callers are spread across UnitAI, Sentinel, CEngine wrapper, and CGeneralVolume update/reset paths.
- The checked export also has two raw no-function callsites into `0x00506010`.
- No obvious Weapon- or BattleEngine-named direct caller to `0x00506010` appears in the checked xref export.

## What This Does Not Prove

- This does not create, rename, or mutate a Ghidra function boundary.
- This does not prove exact source `CWeapon::Fire` or `CBattleEngine::WeaponFired` identity.
- This does not prove whether retail weapon fire clears stealth.
- This does not rule out indirect, virtual-dispatch, callback, inlined, or runtime-only weapon-fire behavior elsewhere.
- This does not prove runtime cloak activation, target-lock behavior, projectile behavior, or fire-while-cloaked behavior.
- This does not patch or launch `BEA.exe` and does not inspect private runtime captures.
- This does not make the repository rebuildable from scratch.

## Outcome

`weapon_fire_breaks_stealth` remains source-only in aggregate source-to-binary gap accounting. This pass weakens a narrow weapon-specific interpretation for `0x00506010`: direct callers currently look like a broader shared burst/effect path, not a clean `CWeapon::Fire` / `CBattleEngine::WeaponFired` identity.

Future static work should inspect the two raw no-function callsites or the caller-specific wrapper paths only if a concrete caller can be tied back to weapon/fire input. Otherwise, runtime cloak/fire proof still needs a copied-profile setup with a verified cloak-active baseline.

## Privacy / Release Safety

This report stores repo-relative filenames, public addresses already present in repo evidence, current function names, command summaries, xref counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, or Ghidra mutation logs.
