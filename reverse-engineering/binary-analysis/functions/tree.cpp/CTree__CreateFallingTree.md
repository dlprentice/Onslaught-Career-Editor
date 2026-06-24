# CTree__CreateFallingTree

| Property | Value |
| --- | --- |
| Address | `0x004f69b0` |
| Saved signature | `void __thiscall CTree__CreateFallingTree(void * this, void * impact_vector)` |
| Wave | Wave520 CTree static re-audit |

Creates the falling-tree data object when a standing tree is converted into a falling state. The body skips if `this+0x48` is already set, copies a 12-dword tree-type matrix block from `DAT_008406b8` using `this+0x40` as an index, allocates `0xc0` bytes from `tree.cpp` line `0xf0`, derives scale through CTree virtual slot `+0x40`, calls `CTree__InitFallingTreeData`, stores the result at `this+0x48`, seeds `+0xbc` to `-1.0`, schedules event `0xbb9` after 0.5 seconds, and immediately calls `CTree__UpdateFallingTree`.

Evidence: `RET 0x4`, calls from the recovered vtable gates and dropship helper, decompile tokens `DAT_008406b8` / `OID__AllocObject(0xc0)` / `CTree__InitFallingTreeData`, and post xref/read-back coverage.

Claim boundary: static retail-binary evidence only. Exact source identity, concrete layouts, runtime knockdown behavior, BEA patching, and rebuild parity remain unproven.
