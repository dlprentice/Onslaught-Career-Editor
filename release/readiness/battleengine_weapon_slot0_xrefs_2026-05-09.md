# BattleEngine Weapon Slot0 Xref Triage - 2026-05-09

Status: public-safe read-only Ghidra xref/caller triage, not retail identity or runtime proof

## Objective

Continue narrowing the construction-side weapon slot-0 candidate from `release/readiness/battleengine_weapon_slot0_boundary_2026-05-09.md`.

This pass asks a bounded static question: how is the raw slot-0 stub at `0x00506930`, its inner body at `0x005069f0`, and the boundary-adjacent helper at `0x005078b0` currently referenced in Ghidra?

## Inputs

- Xref target list: `subagents/battleengine-weapon-slot0-xrefs/current/addresses.txt`
- Read-only xref export: `subagents/battleengine-weapon-slot0-xrefs/current/slot0_xrefs.tsv`
- Read-only decompile index: `subagents/battleengine-weapon-slot0-xrefs/current/decompile/index.tsv`
- Probe: `tools/battleengine_weapon_slot0_xref_probe.py`
- Probe test: `tools/battleengine_weapon_slot0_xref_probe_test.py`

## Commands

Read-only Ghidra exports:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/battleengine-weapon-slot0-xrefs/current/addresses.txt subagents/battleengine-weapon-slot0-xrefs/current/slot0_xrefs.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/battleengine-weapon-slot0-xrefs/current/decompile_addresses.txt subagents/battleengine-weapon-slot0-xrefs/current/decompile 40
```

Probe validation:

```powershell
py -3 tools\battleengine_weapon_slot0_xref_probe_test.py
py -3 tools\battleengine_weapon_slot0_xref_probe.py --check
py -3 -m py_compile tools\battleengine_weapon_slot0_xref_probe.py tools\battleengine_weapon_slot0_xref_probe_test.py
cmd.exe /c npm run test:battleengine-weapon-slot0-xrefs
```

## Result

```text
BattleEngine weapon slot0 xref probe
Status: PASS
Classification: slot0-xrefs-vtable-stub-and-named-burst-caller
Slot0 DATA refs: 1
Slot0 direct code refs: 0
Inner named callers: CGeneralVolume__SpawnBurstFromPresetWithFallback
Inner raw outer-stub callsites: 0x005069b6
Post-return helper inner callsites: 0x00506b75
```

Key read-only facts:

| Evidence | Current result |
| --- | --- |
| `0x00506930` direct xrefs | One direct `DATA` reference from vtable entry `0x005dfc94`; no direct code refs in the checked export. |
| `0x005069f0` direct xrefs | Two direct call refs: raw outer-stub callsite `0x005069b6`, and named caller `CGeneralVolume__SpawnBurstFromPresetWithFallback` at `0x00506010`. |
| `0x005069f0` current name | `CEngine__SpawnProjectileBurstFromCurrentPreset`. |
| `0x005078b0` direct xrefs | One direct call from the checked inner body at `0x00506b75`. |
| `0x005078b0` current name | `CEngine__GetListEntryIdByIndex`. |

The ignored JSON report is written to `subagents/battleengine-weapon-slot0-xrefs/current/weapon-slot0-xrefs.json`.

## What This Proves

- The current read-only Ghidra xref export has one direct `DATA` reference to `0x00506930` from vtable entry `0x005dfc94`.
- No direct code reference to the raw `0x00506930` slot-0 stub appears in the checked xref export.
- The current xref export shows `0x005069f0` is called by the raw outer-stub callsite `0x005069b6` and by `CGeneralVolume__SpawnBurstFromPresetWithFallback` at `0x00506010`.
- The current decompile index names `0x005069f0` as `CEngine__SpawnProjectileBurstFromCurrentPreset`.
- The current decompile index names `0x005078b0` as `CEngine__GetListEntryIdByIndex`, and the checked xref export shows it is called from the inner body at `0x00506b75`.

## What This Does Not Prove

- This does not create, rename, or mutate a Ghidra function boundary.
- This does not prove exact source `CWeapon::Fire` or `CBattleEngine::WeaponFired` identity.
- This does not prove whether retail weapon fire clears stealth.
- This does not rule out indirect, virtual-dispatch, callback, inlined, or runtime-only weapon-fire behavior elsewhere.
- This does not prove runtime cloak activation, target-lock behavior, projectile behavior, or fire-while-cloaked behavior.
- This does not patch or launch `BEA.exe` and does not inspect private runtime captures.
- This does not make the repository rebuildable from scratch.

## Outcome

`weapon_fire_breaks_stealth` remains source-only in aggregate source-to-binary gap accounting. This xref pass narrows the raw candidate story: `0x00506930` currently looks like a vtable-entry stub with no direct code callers in the checked export, while `0x005069f0` is a currently named burst/projectile helper reached from both the raw stub and a named `CGeneralVolume` fallback caller.

Future static work should follow the caller side of `CGeneralVolume__SpawnBurstFromPresetWithFallback` / burst-preset setup or pivot to a copied-profile runtime proof only after a verified cloak-active baseline is available.

## Privacy / Release Safety

This report stores repo-relative filenames, public addresses already present in repo evidence, current function names, command summaries, xref counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, or Ghidra mutation logs.
