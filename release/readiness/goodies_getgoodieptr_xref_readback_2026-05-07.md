# Goodies GetGoodiePtr Xref Read-Back - 2026-05-07

This note records read-only Ghidra xref exports for:

- `CCareer__GetGoodiePtr` at `0x00421980`
- the concrete `g_Career_mGoodies[71..73]` state addresses used by the current retail symbol layout

The goal was to check whether the retail helper used to address `CGoodie` entries, or the concrete 71-73 state addresses themselves, appear outside the known unlock-recomputation function. Either would be a candidate hidden/non-grid request path.

## Safety

- Did not launch `BEA.exe`.
- Did not patch the installed game.
- Did not run runtime proof.
- Did not commit raw Ghidra exports from `subagents/`.
- Ghidra headless was used in `-process` / `-noanalysis` mode with a read-only export script.

## Commands

| Command | Result | Important Output | What It Proves |
| --- | --- | --- | --- |
| `analyzeHeadless ... -postScript ExportXrefsForAddresses.java <ignored-addresses> <ignored-xrefs> -noanalysis` | PASS | `Wrote 423 rows` | Exports Ghidra xrefs to `CCareer__GetGoodiePtr` into ignored local evidence. |
| `analyzeHeadless ... -postScript ExportXrefsForAddresses.java <ignored-71-73-addresses> <ignored-71-73-xrefs> -noanalysis` | PASS | `Wrote 3 rows` | Exports direct xrefs to `g_Career_mGoodies[71]`, `[72]`, and `[73]`. |
| `py -3 tools\goodies_getgoodieptr_xref_probe.py --check` | PASS | `GetGoodiePtr rows: 423; callers: CCareer__UpdateGoodieStates=423`; `Goodies 71-73 direct data references: 0` | Public-safe verifier confirms every exported `GetGoodiePtr` call currently resolves to `CCareer__UpdateGoodieStates`, and no direct data xrefs were reported for 71-73. |

## Finding

The current Ghidra xref set has 423 calls to `CCareer__GetGoodiePtr`, and all 423 are from `CCareer__UpdateGoodieStates`.

This supports the current static model:

- `CCareer__GetGoodiePtr` is used by the retail unlock-recomputation path.
- The helper is not currently evidence for a frontend direct-selection path to Goodies 71-73.
- Ghidra reports no direct data xrefs to `g_Career_mGoodies[71]`, `[72]`, or `[73]` in this project.
- The existing frontend Goodies path still routes normal selection through `get_goodie_number(mCX, mCY)`, which skips from 70 to 74 on the known wall mapping.

## Not Claimed

- This is not proof that Goodies 71-73 are unreachable at runtime.
- This is not proof that no indirect array write/read exists elsewhere.
- This is not runtime proof after completing level 741/742.
- This is not a copied-profile hidden-selection search.

The remaining 71-73 question is now narrower: source and retail unlock recomputation know those indices, but no normal wall-coordinate path or `GetGoodiePtr`-based frontend path is proven.
