# BattleEngine Selection Helper Ghidra Read-Back - 2026-05-07

Status: public-safe read-only Ghidra evidence, not runtime or exact source-identity proof

## Objective

Add fresh machine-checkable read-back evidence for the already named BattleEngine selection, weapon-entry, and selected-weapon helper cluster that supports weapon cycling, selected entry lookup, usability gates, current/fallback resolution, and weapon-set cleanup.

## What Changed

Added:

- `tools/battleengine_selection_helper_ghidra_readback_probe.py`
- `npm run test:battleengine-selection-helper-ghidra-readback`

The probe validates ignored Ghidra decompile exports under `subagents/battleengine-selection-helper-ghidra-readback/current/decompile/`.

## Functions Checked

- `CCockpit__CycleToNextUsableWeapon`
- `CGeneralVolume__GetSelectedWeaponDef`
- `CGeneralVolume__GetSelectedWeaponDef_CachedPath`
- `CCockpit__DestroyWeaponSetAndOwnedNodes`
- `CBattleEngine__GetIndexedEntry`
- `CBattleEngine__IsIndexedEntryUsable`
- `CBattleEngine__IsResolvedEntryUsable`
- `CBattleEngine__DestroySPtrSetElementsAndClear`
- `CBattleEngine__IsCurrentResolvedEntry`

## Commands

```powershell
wsl bash -lc "cd <repo-root> && tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/battleengine-selection-helper-ghidra-readback/current/addresses.txt subagents/battleengine-selection-helper-ghidra-readback/current/decompile 90"
py -3 -m py_compile tools\battleengine_selection_helper_ghidra_readback_probe.py
npm run test:battleengine-selection-helper-ghidra-readback
```

## Result

- Headless Ghidra export passed with targets `9`, dumped `9`, missing `0`, failed `0`.
- The export printed the known GhydraMCP extension manifest warnings and `REPORT: Save succeeded`; this is treated as tool-environment/project-save noise for a read-only export script, not as an intentional Ghidra mutation.
- Python compile check passed.
- Selection-helper read-back probe passed `9/9` functions.
- Raw decompile and JSON evidence stayed ignored under `subagents/`.

## What This Proves

- Fresh headless Ghidra read-back can export current decompile output for the named selection/weapon-entry helper cluster.
- The selected functions retain current selected-entry traversal, current/fallback resolution, selected weapon-definition lookup, usability gate, weapon-cycle, and cleanup tokens.
- The selection-helper cluster is now covered by repeatable public-safe read-back validation.

## Not Claimed

- This does not prove exact Steam retail binary identity for every source weapon-change or selection behavior anchor.
- This does not prove runtime weapon cycling, firing readiness, selected weapon behavior, or gameplay-state interpretation.
- This does not apply a Ghidra rename map.
- This does not mutate `BEA.exe`.
- This does not launch BEA.exe.
- This does not make the repository rebuildable from scratch.
