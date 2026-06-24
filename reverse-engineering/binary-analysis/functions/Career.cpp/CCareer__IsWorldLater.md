# CCareer__IsWorldLater

> Address: `0x0041bbb0`
>
> Source: `references/Onslaught/Career.cpp` (`CCareer::IsWorldLater(int, int)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Determine whether `inCurrentWorld` is *later* in the campaign graph than `inDiesOn` by doing a reachability test over child links.

## Signature
```c
bool CCareer::IsWorldLater(int inCurrentWorld, int inDiesOn);
```

## Behavior (Source-Parity)
1. Resolve `CCareerNode* currentNode` from `inCurrentWorld`.
2. Resolve `CCareerNode* diesOnNode` from `inDiesOn`.
3. If both exist and are different, return `Later(diesOnNode, currentNode)`, else `false`.

## Related Functions
- [CCareer__Later](CCareer__Later.md) - Depth-first reachability test over `mLowerLink/mHigherLink`
- [CCareer__GetNodeFromWorld](CCareer__GetNodeFromWorld.md) - World number to node pointer
