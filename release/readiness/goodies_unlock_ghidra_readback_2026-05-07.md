# Goodies Unlock Ghidra Headless Read-Back - 2026-05-07

## Scope

This pass used the local Ghidra project to re-read the retail Goodies unlock/update function family. It did not launch the game, apply a rename map, change signatures, patch `BEA.exe`, or run runtime proof.

Private decompile output remains ignored under:

```text
subagents/ghidra-goodies-unlock-readback-2026-05-07/decompile/
```

## Command

```powershell
& '<ghidra-install>\support\analyzeHeadless.bat' '<ghidra-projects-root>' BEA `
  -process BEA.exe `
  -scriptPath '<repo>\tools' `
  -postScript ExportFunctionsByAddressDecompile.java `
    '<repo>\subagents\ghidra-goodies-unlock-readback-2026-05-07\goodies_unlock_addresses.txt' `
    '<repo>\subagents\ghidra-goodies-unlock-readback-2026-05-07\decompile' `
    80 `
  -noanalysis
```

Result: PASS

Important output:

```text
targets=8 dumped=8 missing=0 failed=0
```

Ghidra headless also printed `REPORT: Save succeeded for processed file: /BEA.exe`. No mutation script was run; this should be treated as headless project save behavior, not as a rename/signature/patch wave.

## Functions Rechecked

| Address | Function | Result |
| --- | --- | --- |
| `0x0041c470` | `CCareer__UpdateGoodieStates` | dumped |
| `0x0041c240` | `TOTAL_S_GRADES` | dumped |
| `0x00421550` | `CCareer__GetAndResetGoodieNewCount` | dumped |
| `0x00421560` | `CCareer__GetAndResetFirstGoodie` | dumped |
| `0x00420ab0` | `CGrade__ctor_char` | dumped |
| `0x00420ac0` | `CGrade__operator_gte` | dumped |
| `0x00420af0` | `CCareer__GetNode` | dumped |
| `0x00421970` | `CCareer__NodeArrayAt` | dumped |

## Public-Safe Findings

- `CCareer__UpdateGoodieStates` still calls `CCareer__CountGoodies`, `TOTAL_S_GRADES`, the `CGrade` constructor/comparison helpers, `CCareer__GetNode`, and `CCareer__NodeArrayAt`.
- The four `TOTAL_S_GRADES` callsites line up with developer-item Goodies `74..77`.
- Kill-threshold branches mask packed kill counters with `0xffffff`, matching the current true-view save docs.
- `CCareer__UpdateGoodieStates` updates the aggregate new-goodie counter consumed by `CCareer__GetAndResetGoodieNewCount`.
- `CCareer__UpdateGoodieStates` updates the first-goodie flag consumed by `CCareer__GetAndResetFirstGoodie`.
- The 2026-05-07 `CCareer__NodeArrayAt` decompile uses the simplified two-argument form `this + node_index * 0x40`, with `this` supplied through `ECX`.

## What This Does Not Prove

- It does not replay a running game session.
- It does not prove live save recomputation inside a BEA process.
- It does not observe mission-script Goodie unlocks at runtime.
- It does not mutate Ghidra names, signatures, comments, or types.
- It does not patch or read/write the installed Steam `BEA.exe`.
- It does not commit private decompile output.

## Follow-Up

Next Goodies RE work should either run a copied-profile/windowed runtime replay of representative Goodies wall selections, or continue with read-only static typing of the remaining frontend content-bucket branches. Any runtime proof must use a copied profile and must keep raw captures, paths, frames, and proof JSON private.
