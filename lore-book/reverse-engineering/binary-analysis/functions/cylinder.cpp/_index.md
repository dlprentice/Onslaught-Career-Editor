# cylinder.cpp

> Cylinder collision helpers from `BEA.exe` - static retail evidence for `CCylinder`.

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Wave940 (`line-cylinder-dispatch-review-wave940`) re-reviewed the primitive line/cylinder dispatch wrappers with a Composer 2.5 consult plus fresh Ghidra metadata/tags/xref/instruction/decompile/vtable exports. Primary anchors were `0x004059a0 CCylinder__VFunc_01_004059a0`, `0x004098c0 CLine__VFunc_01_004098c0`, `0x004098e0 CLine__ctor_copy`, `0x00426340 CLine__ScalarDeletingDestructor_00426340`, and `0x00426360 CLine__SetBaseVtable_00426360`; context included `0x00426320 CSphere__VFunc_01_00426320` plus vtables `0x005d88cc`, `0x005d8bfc`, and `0x005d95e8`. The pass was a read-only review: no mutation, rename, signature change, comment change, function-boundary change, or executable-byte change was made. Evidence counts: 8 metadata rows, 8 tag rows, 1462 xref rows, 85 instruction rows, 8 decompile rows; 13 context metadata/tag rows, 528 context xref rows, 1830 context instruction rows, 13 context decompile rows; and 24 vtable-slot rows. Wave911 focused re-audit progress after Wave940 is `178/1408 = 12.64%`; static export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260528-030741_post_wave940_line_cylinder_dispatch_review_verified`. Runtime primitive dispatch behavior, runtime collision/trace behavior, exact primitive layouts, exact source-body identity, BEA patching behavior, and rebuild parity remain separate proof.

Wave1098 (`primitive-collision-bridge-review-wave1098`) re-read the same primitive collision bridge in a no-Cursor Codex-only pass and saved tag-only normalization for the CLine/CCylinder/CSphere bridge plus MeshCollisionVolume context. Probe token anchor: Wave1098; primitive-collision-bridge-review-wave1098; 0x004059a0 CCylinder__VFunc_01_004059a0; 0x004098c0 CLine__VFunc_01_004098c0; 0x004098e0 CLine__ctor_copy; 0x00426320 CSphere__VFunc_01_00426320; 0x0043fe20 CCylinder__ResolveCollisionVFunc02; 0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50; 0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds; 0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart; 0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0; 0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore; 0x00478c20 Geometry__IntersectSegmentTriangleAndStoreHit; 0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified; tag-only normalization. Runtime primitive dispatch/collision behavior, exact primitive/vector/contact layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Functions

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x004059a0 | CCylinder__VFunc_01_004059a0 | SAVED | Wave940 read-back: CCylinder vtable `0x005d88cc` slots `1`, `3`, and `5`; forwards four stack arguments plus `this` into `dispatchObject` vfunc `+0x8`. |
| 0x004098c0 | CLine__VFunc_01_004098c0 | SAVED | Wave940 read-back: CLine vtable `0x005d8bfc` slots `1`, `2`, `3`, and `5`; forwards four stack arguments plus `this` into `dispatch_target` vfunc `+0x10`. |
| 0x004098e0 | CLine__ctor_copy | SAVED | Wave940 read-back: installs CGeneralVolume base table `0x005d892c`, copies line data, then installs CLine table `0x005d8bfc`. |
| 0x00426340 | CLine__ScalarDeletingDestructor_00426340 | SAVED | Wave940 read-back: shared scalar-deleting destructor in the `0x005d88cc`, `0x005d8bfc`, and `0x005d95e8` table regions. |
| 0x00426360 | CLine__SetBaseVtable_00426360 | SAVED | Wave940 read-back: tiny CLine-style base-vtable reset used by the scalar-deleting destructor and unwind cleanup thunks. |
| 0x0043fde0 | CCylinder__ctor | SAVED | Copy/constructor helper for cylinder radius/basis context. |
| 0x0043fe20 | CCylinder__ResolveCollisionVFunc02 | SAVED | Vtable slot `2` collision resolver; four stack arguments plus ECX receiver. |

## Wave 346 Signature Read-Back

Wave 346 saved and read back the current `CCylinder` signatures/comments/tags after metadata, decompile, xref, instruction, vtable, and caller review:

- `CCylinder__ctor`: `void __thiscall CCylinder__ctor(void * this, void * sourceCylinder)`
- `CCylinder__ResolveCollisionVFunc02`: `int __thiscall CCylinder__ResolveCollisionVFunc02(void * this, void * movingStateA, void * movingStateB, void * radiusContext, void * contactOut)`

The vtable read-back shows `0x005d88cc` slot `2` pointing to `CCylinder__ResolveCollisionVFunc02`. The caller `CSphere__VFunc_02_004e4d70` pushes four stack arguments and passes ECX as the cylinder context before calling `0x0043fe20`.

## Claim Boundary

This is saved static Ghidra evidence only. Runtime collision behavior, exact source identity, concrete `CCylinder` layout, local/type recovery, BEA launch, game patching, and rebuild parity remain unproven.

## Wave1151 Current-Risk Tag Normalization

Wave1151 tag-only normalization also covers `0x004059a0 CCylinder__VFunc_01_004059a0` and `0x004098c0 CLine__VFunc_01_004098c0` as score21 current-risk rows. It preserves the primitive-collision wrapper contracts and adds Wave1151/current-risk tags only; no rename, signature, comment, boundary, or byte change was made. Verified backup: `G:\GhidraBackups\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
