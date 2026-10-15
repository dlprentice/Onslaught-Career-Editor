# CCareer__GetLevelStructure

> Address: 0x0041b7b0 | Source: `references/Onslaught/Career.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Return the pointer to the static `level_structure` table that defines world/link topology.

## Signature
```c
void * CCareer__GetLevelStructure(void);

// Source semantic signature:
// CLevelStructure * CCareer::GetLevelStructure();
```

## Notes
- Decompile is a constant-address return helper (`return &DAT_00623e28`).
- Callers load `ECX = &CAREER` before calling; implementation does not read `this`.
- Used by frontend level-select setup to read world IDs and link metadata.

## Related Functions
- [CCareer__Blank](CCareer__Blank.md) - Seeds node/link arrays from `level_structure`
- [CCareer__GetNodeFromWorld](CCareer__GetNodeFromWorld.md) - Resolves nodes using world numbers from this table
- [CCareer__GetGradeForWorld](CCareer__GetGradeForWorld.md) - Consumes world IDs when building grade/UI state
