# Goodies Source Access Probe - 2026-05-07

## Scope

This note records a read-only source-access probe for the Goodies state APIs in Stuart's source tree. It does not launch BEA, read or write `BEA.exe`, mutate Ghidra, patch the installed game, or touch save files.

Source is architecture/name evidence only. Steam retail binary read-back and copied-profile runtime proof remain the authority for shipping behavior.

## Commands Run

| Command | Result | Important Output | What It Proves |
| --- | --- | --- | --- |
| `py -3 tools\goodies_source_access_probe.py --check` | PASS | `source Goodie API lines: set=3 get=3 direct71to73=0` | Source-level `CAREER.GetGoodieState` / `CAREER.SetGoodieState` callers are bounded and no direct source API call targets Goodies 71-73. |

## Finding

- Source-level `CAREER.SetGoodieState` callers are limited to the FEPGoodies coordinate wrapper and the two gameplay FMV unlock paths.
- Source-level `CAREER.GetGoodieState` callers are limited to the FEPGoodies coordinate wrapper and the two gameplay FMV unlock checks.
- `Career.cpp` still contains the intended 71-73 unlock/instruction tokens.
- `FEPGoodies.cpp` still has no direct `get_goodie_number` return for 71, 72, or 73.

## Not Claimed

- This is not proof of Steam retail binary behavior.
- This is not runtime proof that Goodies 71-73 are unreachable.
- This does not rule out indirect binary array access or runtime-only paths.
