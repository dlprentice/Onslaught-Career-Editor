# CCareer__GetNode

> Address: `0x00420af0`
>
> Source: `references/Onslaught/Career.h` inline `CCareer::GetNode(int num)`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Signature
```c
void * CCareer__GetNode(void * this, int node_index);
```

## Behavior
- Returns `NULL` when `node_index < 0`.
- Otherwise returns pointer to the node entry at `this + 0x0004 + node_index * 0x40`.

This matches Stuart's inline accessor:
```cpp
CCareerNode* GetNode(int num) { if (num < 0) return NULL ; return &mNode[num] ; }
```

## Notes
- Called from `CCareer__UpdateGoodieStates` in grade-check loops.
- No explicit upper-bound guard is present in this helper (same as source inline behavior).
- Decompile/mutation was validated via direct HTTP plugin route after MCP bridge transport closed.

## Related
- [CCareer__GetNodeFromWorld](CCareer__GetNodeFromWorld.md)
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md)
