# CTree__InitFallingTreeData

| Property | Value |
| --- | --- |
| Address | `0x004f5f60` |
| Saved signature | `void * __thiscall CTree__InitFallingTreeData(void * this, void * tree_type_matrix, float scale, void * impact_vector)` |
| Wave | Wave520 CTree static re-audit |

Initializes a falling-tree data object from a 12-dword tree-type matrix block, a scale value, and an impact/direction vector. The body mirrors the matrix into current/base/previous matrix slots, clears angle/velocity fields, copies the vector, derives a normalized side/fall axis, stores angular velocity bits `0x3ca3d70a`, and returns `this`.

Evidence: `RET 0x0c`, callsite `0x004f6a38` from `CTree__CreateFallingTree`, post metadata/tag/decompile read-back, and Wave520 probe coverage.

Claim boundary: static retail-binary evidence only. Exact structure field names, source-body identity, runtime falling-tree physics, BEA patching, and rebuild parity remain unproven.
