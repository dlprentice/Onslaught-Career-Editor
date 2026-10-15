# CCareer__Later

> Address: `0x0041bc60`
>
> Source: `references/Onslaught/Career.cpp` (`CCareer::Later(CCareerNode*, CCareerNode*)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Depth-first reachability test over the campaign graph.

Returns `true` if `inCurrentNode` is reachable by following child links (lower/higher) starting from `inDiesOnNode`.

## Signature
```c
bool CCareer::Later(CCareerNode* inDiesOnNode, CCareerNode* inCurrentNode);
```

## Algorithm (Source-Parity)
1. If either node is null: return false.
2. If nodes are equal: return true.
3. Recurse into `mNodeLink[inDiesOnNode->mLowerLink].mToNode` (if not -1).
4. Recurse into `mNodeLink[inDiesOnNode->mHigherLink].mToNode` (if not -1).

## Related Functions
- [CCareer__IsWorldLater](CCareer__IsWorldLater.md) - Resolves world numbers then calls this
