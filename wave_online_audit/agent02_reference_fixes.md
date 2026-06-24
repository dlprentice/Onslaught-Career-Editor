# Online Audit Fixes: GHIDRA-REFERENCE.md + executable-analysis.md

Source audit: `reverse-engineering/binary-analysis/semantic-audit-online-pass-2026-02-12.json`

## Summary
The online audit flags `name_mismatch` rows in two docs. These are strictly naming mismatches (source-style `CCareer::X` vs current binary labels `CCareer__X`, plus a patch row that uses `prologue` instead of the function name). Below are the exact rows and concrete edits to make the docs match the audit expectations.

## reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md

### Wrong rows (exact locations)
- `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:242`
  - Current row: `| 0x004213c0 | CCareer::SaveToFile | Serializes career to buffer |`
  - Audit actual: `CCareer__SaveWithFlag`
- `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:243`
  - Current row: `| 0x00421200 | CCareer::LoadFromFile | Deserializes buffer to career |`
  - Audit actual: `CCareer__Load`
- `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:244`
  - Current row: `| 0x00421430 | CCareer::GetSaveSize | Calculates dynamic save size |`
  - Audit actual: `CCareer__GetSaveSize`
- `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:817`
  - Current row: `| 0x00465490 | prologue | `MOV EAX,1; RET 4` | Force `IsCheatActive()` TRUE ... |`
  - Audit actual: `IsCheatActive`

### Proposed edits (concrete)
1) Update the Save/Load system table to match actual symbols:
- Change line 242 to:
  - `| 0x004213c0 | CCareer__SaveWithFlag | Serializes career to buffer |`
- Change line 243 to:
  - `| 0x00421200 | CCareer__Load | Deserializes buffer to career |`
- Change line 244 to:
  - `| 0x00421430 | CCareer__GetSaveSize | Calculates dynamic save size |`

Optional clarification (if you want to preserve source naming): append parenthetical in Description, e.g. “(source: CCareer::SaveToFile)”, but keep the Function column exact.

2) Update the force-cheats patch row to use the real function name in the Function column:
- Change line 817 to:
  - `| 0x00465490 | IsCheatActive | `MOV EAX,1; RET 4` | Force `IsCheatActive()` TRUE ... |`

This keeps the patch context but aligns the Function column with the real symbol name so the audit passes.

## reverse-engineering/binary-analysis/executable-analysis.md

### Wrong rows (exact locations)
- `reverse-engineering/binary-analysis/executable-analysis.md:41`
  - Current row: `| 0x00421350 | CCareer::Save | Serializes career to buffer |`
  - Audit actual: `CCareer__Save`
- `reverse-engineering/binary-analysis/executable-analysis.md:42`
  - Current row: `| 0x004213c0 | CCareer::SaveWithFlag | Serializes career to buffer (sets a flag first) |`
  - Audit actual: `CCareer__SaveWithFlag`
- `reverse-engineering/binary-analysis/executable-analysis.md:43`
  - Current row: `| 0x00421200 | CCareer::LoadFromFile | Deserializes buffer to career |`
  - Audit actual: `CCareer__Load`
- `reverse-engineering/binary-analysis/executable-analysis.md:44`
  - Current row: `| 0x00421430 | CCareer::GetSaveSize | Calculates dynamic save size |`
  - Audit actual: `CCareer__GetSaveSize`

### Proposed edits (concrete)
- Change line 41 to:
  - `| 0x00421350 | CCareer__Save | Serializes career to buffer |`
- Change line 42 to:
  - `| 0x004213c0 | CCareer__SaveWithFlag | Serializes career to buffer (sets a flag first) |`
- Change line 43 to:
  - `| 0x00421200 | CCareer__Load | Deserializes buffer to career |`
- Change line 44 to:
  - `| 0x00421430 | CCareer__GetSaveSize | Calculates dynamic save size |`

Optional clarification: add source-name parenthetical in Description if desired, but keep the Function column as the exact symbol to satisfy the audit.
