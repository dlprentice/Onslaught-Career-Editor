# Goodies IScript Read-Back - 2026-05-07

## Scope

This note records a read-only Ghidra decompile export for the mission-script Goodie state handlers:

- `IScript__SetGoodieState` at `0x00533a70`
- `IScript__GetGoodieState` at `0x00533aa0`

It does not launch BEA, mutate `BEA.exe`, patch the installed game, mutate saves, or commit raw decompile output. Raw Ghidra exports remain ignored under `subagents/`.

## Commands Run

| Command | Result | Important Output | What It Proves |
| --- | --- | --- | --- |
| `analyzeHeadless ... -postScript ExportFunctionsByAddressDecompile.java <ignored-addresses> <ignored-decompile-dir> 60 -noanalysis` | PASS | `targets=2 dumped=2 missing=0 failed=0` | Exports both IScript Goodie state handlers from the local Ghidra project into ignored evidence. |
| `py -3 tools\goodies_iscript_readback_probe.py --check` | PASS | `IScript Goodie handlers: set=PASS, get=PASS, index=PASS` | Public-safe verifier confirms the expected read/write tokens remain present in the exported decompile. |

## Finding

- `IScript__SetGoodieState` writes a state value through the mission-script Goodie index path.
- `IScript__GetGoodieState` reads `g_Career_mGoodies[index-1]` and returns a scalar script result.
- Mission scripts are therefore a real Goodie state access surface separate from the frontend wall coordinate mapper.

## Not Claimed

- This is not proof that any current mission script targets Goodies 71-73.
- This is not copied-profile runtime proof.
- This does not prove hidden/non-grid Goodies 71-73 reachability.
