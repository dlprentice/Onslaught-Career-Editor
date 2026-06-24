# CCareerNode__GetParentLinks

> Address: 0x0041b9f0 | Source: `references/Onslaught/Career.cpp` (`CCareerNode::GetParentLinks`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Build the list of incoming links (parent edges) that lead to this node.

## Behavior (Source-aligned)
- Initializes an output `SPtrSet<CCareerNodeLink>` (caller-owned; stack arg)
- Loops `num_nodes` (retail count: `DAT_00624184`)
- For each node:
  - gets its child links (`CCareerNode__GetChildLinks` @ `0x0041b940`)
  - for each `CCareerNodeLink` in that set:
    - if `CAREER.GetNode(link->mToNode) == this`, append `link`

## Retail Usage
- `Career_IsWorldUnlocked` @ `0x00461a50` uses `GetParentLinks()` and returns true if any parent link has `mLinkType == CN_COMPLETE (1)`.
- `CCareer__ReCalcLinks` uses it to downgrade alternate `CN_COMPLETE` links to `CN_COMPLETE_BROKEN` after a win.

## Signature
```c
// Conceptual signature (templates erased in retail build)
SPtrSet<CCareerNodeLink> CCareerNode::GetParentLinks(void);
```

## Notes
- In the Steam `.bes` file, parent-link completion is encoded in `CCareerNodeLink[200]`:
  - `mLinkType` is the first dword (0/1/2)
  - `mToNode` is the second dword (node index)
