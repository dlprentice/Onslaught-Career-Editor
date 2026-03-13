# CCareer__SaveWithFlag

> Address: 0x004213c0 | Source: `references/Onslaught/Career.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (MCP, read-back verified 2026-02-13)
- **Verified vs Source:** Behavior-level verified (2026-02-23): retail implementation sets `mCareerInProgress = TRUE` then executes the same save body inline.

## Purpose
Save with `mCareerInProgress` set. In retail Steam, this is a dedicated routine that sets the progress flag and then performs the full save serialization body directly.

## Signature
```c
// Binary calling convention: __thiscall, returns void, pops 4 bytes (1 arg)
void CCareer::SaveWithFlag(void* dest);
```

Ghidra signature (Steam build, verified 2026-02-13):
```c
void CCareer__SaveWithFlag(void * this, void * dest);
```

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Sets `mCareerInProgress` to `1` in-memory (`this+0x2488 = 0x00000001`), which appears as `0x00010000` in the repo’s historical aligned file view.
- Serializes the same fields as `CCareer__Save` (version word + fixed CCareer dump + variable options entries + `OptionsTail_Write`) inlined in this function body.
- Deep-pass verified callsite (2026-02-23): `0x00465045` in `CFEPSaveGame__CreateSave` calls `CCareer__SaveWithFlag`.
- No `CALL CCareer__Save` occurs inside `CCareer__SaveWithFlag`; parity is by duplicated logic, not wrapper call-through.
- WARNING: Offset 0x22D4 is Goodie 228, NOT progress flag!
- Our patcher does NOT write mCareerInProgress to avoid Goodie 228 corruption

## Related Functions
- [CCareer__Save](CCareer__Save.md) - Core save function
- [CCareer__Load](CCareer__Load.md) - Loads and clears flag
