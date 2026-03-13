# CCareer__DoesBaseThingExist

> Address: `0x0041bb20`
>
> Source: `references/Onslaught/Career.cpp` (`CCareer::DoesBaseThingExist(int, int)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Query persistent “base thing exists” state for a given world number.

This is how the game carries objective/object existence forward between missions (single-player only).

## Signature
```c
// offset: 0..287 (BASE_THINGS_EXISTS_SIZE)
bool CCareer::DoesBaseThingExist(int world_number, int offset);
```

## Behavior (Source-Parity + Retail Notes)
- If the game is in multiplayer, returns `true` (persistence between previous levels is not supported).
- Finds the `CCareerNode*` for `world_number` (`CCareer__GetNodeFromWorldNo` in source; `CCareer__GetNodeFromWorld` in retail).
- If the node exists: returns `node->DoesBaseThingExist(offset)`.
- If the node is missing: returns `true` (assume it exists).

Retail implementation detail:
- Uses `mBaseThingsExists` bitset at node offset `+0x14` (9 dwords, 288 bits).
- The “offset” argument is a base-thing index (0..287), not a “node state” bit index.

## Related Functions
- [CCareerNode__SetBaseThingExistTo](CCareerNode__SetBaseThingExistTo.md) - Set/clear a base-thing bit
- [CCareerNode__Blank](CCareerNode__Blank.md) - Initializes `mBaseThingsExists[]` to all 1s
