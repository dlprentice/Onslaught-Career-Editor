# Goodies Ghidra Headless Read-Back - 2026-05-07

## Scope

This pass used the local Ghidra project to re-read the compiled retail Goodies frontend functions. It did not apply a rename map, change signatures, patch `BEA.exe`, launch the game, or run runtime proof.

Private decompile output remains ignored under:

```text
subagents/ghidra-goodies-readback-2026-05-07/decompile/
```

## Command

```powershell
cmd.exe /c <ghidra-install>\support\analyzeHeadless.bat `
  <ghidra-projects-root> BEA `
  -process BEA.exe `
  -scriptPath <repo>\tools `
  -postScript ExportFunctionsByAddressDecompile.java `
    <repo>\subagents\ghidra-goodies-readback-2026-05-07\goodies_addresses.txt `
    <repo>\subagents\ghidra-goodies-readback-2026-05-07\decompile `
    60 `
  -noanalysis
```

Result: PASS

Important output:

```text
targets=8 dumped=8 missing=0 failed=0
```

Follow-up fresh export for the guarded selection-handler set:

```powershell
<ghidra-install>\support\analyzeHeadless.bat <ghidra-projects-root> BEA -process BEA.exe -scriptPath <repo>\tools -postScript ExportFunctionsByAddressDecompile.java <ignored-addresses> <ignored-decompile-dir> 60 -noanalysis
```

Result: PASS

Important output:

```text
targets=6 dumped=6 missing=0 failed=0
selection target constants: PASS hits=0
```

Ghidra headless also printed `REPORT: Save succeeded for processed file: /BEA.exe`. No mutation script was run; this should be treated as headless project save behavior, not as a rename/signature/patch wave.

## Functions Rechecked

| Address | Function | Result |
| --- | --- | --- |
| `0x0045ac30` | `CFEPGoodies__BuildStaticGoodieDataTable` | dumped |
| `0x0045c770` | `CGoodieData__ctor` | dumped |
| `0x0045c870` | `CFEPGoodies__Deserialise` | dumped |
| `0x0045c9f0` | `CFEPGoodies__StartLoadingGoody` | dumped |
| `0x0045cb80` | `get_goodie_number` | dumped |
| `0x0045cc10` | `CFEPGoodies__LoadingGoodyPoll` | dumped |
| `0x0045cd10` | `CFEPGoodies__FreeUpGoodyResources` | dumped |
| `0x0045d7e0` | `CFEPGoodies__Process` | dumped with signature `void __thiscall CFEPGoodies__Process(void * this, int state)` |

## Public-Safe Findings

- `get_goodie_number` confirms the visible wall ranges already documented for bios, units, FMVs, concept art, race levels, and developer items.
- `goodie_71_res_PC.aya` through `goodie_73_res_PC.aya` remain shipped resource archives that are not exposed by the known compiled wall-coordinate mapping.
- Goodie slot `232` remains displayable as an FMV coordinate mapping even though the PC resource folder has no separate `goodie_232_res_PC.aya`.
- `CFEPGoodies__StartLoadingGoody` resolves the selected Goodie id, asks the resource accumulator for the `-1000 - goodieId` resource filename, and splits selections into resource-backed versus media/level-style paths.
- `CFEPGoodies__Process` is no longer just a probable/name-only mapping in the docs: the 2026-05-07 read-back index confirms the function signature. Remaining caution is limited to unresolved frontend page struct-field names inside the method body.
- Follow-up source/decompile comparison now documents and guards a partial `CFEPGoodies` field map for selected wall coordinates, current Goodie type, and current load state. Animation/camera internals, image controls, display flags, and the cheat/developer bucket side effect remain intentionally untyped.
- Follow-up probe hardening now checks `CFEPGoodies__ButtonPressed`, `CFEPGoodies__Process`, and `CFEPGoodies__LoadingGoodyPoll` for direct `0x47`/`0x48`/`0x49` target constants. The current read-back is `PASS hits=0`, so these selection/update paths still do not show a direct binary-only 71-73 selector in the exported decompile.

## What This Does Not Prove

- It does not replay the running game.
- It does not prove textured/animated native model rendering.
- It does not mutate Ghidra names, signatures, comments, or types.
- It does not patch or read/write the installed Steam `BEA.exe`.
- It does not commit private decompile output.

## Follow-Up

Next static RE work should either type the remaining Goodies content-bucket branches more precisely with read-back evidence, or move to a copied-profile runtime replay of representative Goodies wall selections using the windowed patch on the copied executable only.
