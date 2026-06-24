# CCareerNode__GetChildLinks

> Address: 0x0041b940 | Source: `references/Onslaught/Career.cpp` (`CCareerNode::GetChildLinks`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Return this node’s two outgoing links (lower + higher) as a small pointer set.

## Behavior (Retail `BEA.exe`)
- Reads `mLowerLink` (`this+0x08`) and `mHigherLink` (`this+0x0C`)
- For each link index:
  - if index `< 0`, uses null
  - else computes a pointer into `CCareerNodeLink[200]` (base `0x00661f24`, 8 bytes each)
- Appends both pointers into an `SPtrSet<CCareerNodeLink>` and returns it

## Signature
```c
// Conceptual signature (templates erased in retail build)
SPtrSet<CCareerNodeLink> CCareerNode::GetChildLinks(void);
```

## Related Functions
- [CCareerNode__GetParentLinks](CCareerNode__GetParentLinks.md) - scans all nodes’ child links to find incoming links to `this`
