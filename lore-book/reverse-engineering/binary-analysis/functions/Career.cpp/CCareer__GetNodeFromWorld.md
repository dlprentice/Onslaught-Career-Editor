# CCareer__GetNodeFromWorld

> Address: 0x0041b8f0 | Source: `references/Onslaught/Career.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Look up node by world/level ID. Searches through the node array to find the CCareerNode matching a given world identifier.

## Signature
```c
void * CCareer__GetNodeFromWorld(void * this, int world_num);

// Source semantic signature:
// CCareerNode * CCareer::GetNodeFromWorldNo(int world_num);
```

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Returns pointer to node within the mNodes[100] array
- Retail disassembly confirms `__thiscall` with `ECX=this` and `RET 0x4`
- World IDs are mission identifiers like `100`, `110`, `200`, ... (see `level_structure` in `references/Onslaught/Levels.h`)

## Related Functions
- [CCareer__Update](CCareer__Update.md) - Resolves the finished node by `END_LEVEL_DATA.mWorldFinished`
- [CCareer__DoesBaseThingExist](CCareer__DoesBaseThingExist.md) - Finds node for `world_number` then queries persistence bits
- [CCareer__GetGradeForWorld](CCareer__GetGradeForWorld.md) - Gets grade for a world
- [CCareer__IsWorldLater](CCareer__IsWorldLater.md) - Resolves world numbers then uses reachability logic
