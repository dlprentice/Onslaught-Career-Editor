# Ghidra Wave900+ Through Wave1098 Recheck Note

Status: aggregate validation passed
Date: 2026-06-04
Scope: `wave900-plus-through-wave1098-recheck`

This note extends the post-Wave900 recheck chain through Wave1098. The intended local validation gate is:

```powershell
npm run test:ghidra-wave900-plus-through-wave1098-recheck
```

Wave1098 (`primitive-collision-bridge-review-wave1098`) re-read twenty-one saved primitive collision bridge rows across CLine, CCylinder, CSphere, geometry helper, and MeshCollisionVolume swept-sphere/line-query paths. The focused readiness note is [`ghidra_primitive_collision_bridge_review_wave1098_2026-06-04.md`](ghidra_primitive_collision_bridge_review_wave1098_2026-06-04.md).

Coverage anchors:

- Static function-quality closure remains `6410/6410 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress remains `1560/1560 = 100.00%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Representative rows include `0x004059a0 CCylinder__VFunc_01_004059a0`, `0x004098c0 CLine__VFunc_01_004098c0`, `0x004098e0 CLine__ctor_copy`, `0x00426320 CSphere__VFunc_01_00426320`, `0x0043fe20 CCylinder__ResolveCollisionVFunc02`, `0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50`, `0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds`, `0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart`, `0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0`, `0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`, `0x00478c20 Geometry__IntersectSegmentTriangleAndStoreHit`, and `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830`.
- Fresh pre/post exports verified `21` metadata rows, `21` tag rows, `79` xref rows, `3707` instruction rows, `21` decompile rows, and `64` vtable-slot rows.
- Tag-only dry/apply/final dry reported `tags_added=180` before apply, `updated=21` on apply, and `skipped=21 tags_added=0` on final dry, with no rename, signature, comment, missing, or bad rows.
- Caller/vtable context ties the row group to CLine/CCylinder/CSphere primitive vtable forwarders, cylinder/sphere collision resolver bridging, MeshCollisionVolume swept-sphere bounds and triangle tests, segment-triangle line hit storage, and contact-output initialization.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Runtime collision/trace correctness, exact primitive/vector/AABB/mesh/contact/vtable layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Validation result:

- `npm run test:ghidra-wave900-plus-through-wave1098-recheck`: PASS.
- Focused Wave1098 probe: PASS.
- Readiness notes: `201`.
- Covered waves: `199`.
- Package probe scripts: `197`.
- Evidence bases: `197`.
- Backup references: `199`.
- Apply scripts: `73`.
- Wave982-Wave1098 direct probes: `resultCount=117`, `passCount=1`, `failCount=116`, `disallowedFailureCount=0`.
- Current queue: `6410` total, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status `PASS`.

Probe token anchor: Wave1098; primitive-collision-bridge-review-wave1098; 0x004059a0 CCylinder__VFunc_01_004059a0; 0x004098c0 CLine__VFunc_01_004098c0; 0x004098e0 CLine__ctor_copy; 0x00426320 CSphere__VFunc_01_00426320; 0x0043fe20 CCylinder__ResolveCollisionVFunc02; 0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50; 0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds; 0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart; 0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0; 0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore; 0x00478c20 Geometry__IntersectSegmentTriangleAndStoreHit; 0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified; tag-only normalization.
