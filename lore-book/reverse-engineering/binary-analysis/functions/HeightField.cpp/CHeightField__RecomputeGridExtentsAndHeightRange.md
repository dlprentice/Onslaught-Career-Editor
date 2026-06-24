# CHeightField__RecomputeGridExtentsAndHeightRange

> Address: `0x0047ef20`

## Status

- **Named in Ghidra:** Yes, owner-corrected in Wave396
- **Signature Set:** Yes
- **Verified vs Source:** No exact source-body match claimed

## Signature

```c
void * __fastcall CHeightField__RecomputeGridExtentsAndHeightRange(void * this);
```

## Static Evidence

Wave396 corrected the prior saved `CDXBattleLine__RecomputeGridExtentsAndHeightRange` label to heightfield ownership. The post-apply read-back walks heightfield dimensions at `+0x10bc/+0x10c0`, sample-row state at `+0x20`, threshold context at `+0x1034`, and grid extent plus height min/max sentinel state. `CDXBattleLine__BuildMesh` and `CDXBattleLine__UpdateHeightmap` still call this helper and consume its recomputed bounds.

## Boundaries

- This is static saved-Ghidra owner/name/signature/comment/tag evidence.
- The correction does not prove runtime terrain behavior, exact source identity, concrete field names, local variable names, local types, or rebuild parity.
