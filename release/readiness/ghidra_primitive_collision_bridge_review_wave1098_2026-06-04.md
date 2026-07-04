# Ghidra Primitive Collision Bridge Review Wave1098 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-04
Scope: `primitive-collision-bridge-review-wave1098`

Wave1098 re-read twenty-one saved primitive collision bridge rows spanning the `CLine`, `CCylinder`, `CSphere`, geometry helper, and `CMeshCollisionVolume` swept-sphere/line-query surfaces. The only saved Ghidra mutation was tag-only normalization: no names, signatures, comments, function boundaries, or executable bytes were changed; BEA was not launched; no installed-game/runtime file was mutated.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004059a0 CCylinder__VFunc_01_004059a0` | CCylinder vtable `0x005d88cc` slots `1`, `3`, and `5`; forwards the current cylinder plus four stack arguments to delegate vfunc `+0x8`. |
| `0x004098c0 CLine__VFunc_01_004098c0` | CLine vtable `0x005d8bfc` slots `1`, `2`, `3`, and `5`; forwards the line plus four stack arguments to delegate vfunc `+0x10`. |
| `0x004098e0 CLine__ctor_copy` | Copies line data while moving through the CGeneralVolume base table and CLine table install pattern. |
| `0x0040d470 CLine__ctor_fromEndpoints` | Builds a line record from endpoint pointers and installs the CLine table. |
| `0x00426320 CSphere__VFunc_01_00426320` | CSphere-adjacent forwarder from the `0x005d95e8` table region; forwards to delegate vfunc `+0x0c`. |
| `0x0043fe20 CCylinder__ResolveCollisionVFunc02` | CCylinder vtable slot `2` collision resolver reached by the sphere-as-cylinder proxy path. |
| `0x004e4d70 CSphere__VFunc02_ResolveCollisionAsCylinder` | Uses the sphere/cylinder bridge pattern before calling the cylinder collision resolver. |
| `0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50` | MeshCollisionVolume vtable slot `2`; builds a local sphere-style record and dispatches through the collision-volume table. |
| `0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds` | Swept-sphere bounds test; preserves the prior Wave939 correction that the table is an 8-triangle/24-entry direction-pointer table shape, not 24 triangle faces. |
| `0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart` | Iterates mesh-part triangle candidates and calls the swept-sphere triangle core. |
| `0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0` | MeshCollisionVolume slot `3`; scans parts, refreshes bounds, and accumulates swept-sphere contact candidates. |
| `0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore` | Triangle core uses `Geometry__RaySphereEntryDistance` and closest-edge fallback before writing contact state. |
| `0x00478c20 Geometry__IntersectSegmentTriangleAndStoreHit` | Segment-triangle hit helper used by the MeshCollisionVolume line-query vfunc. |
| `0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism` | Static edge/plane membership test helper for the triangle-prism path. |
| `0x00479200 Geometry__SelectClosestPointOnTriangleEdges` | Closest-edge fallback helper for triangle contact selection. |
| `0x00479630 Geometry__RaySphereEntryDistance` | Ray/sphere entry-distance helper returning a double distance/sentinel value. |
| `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord` | Contact output tail-block with hidden EBX/caller-frame ABI boundary still explicitly unproven. |
| `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830` | MeshCollisionVolume slot `4`; scans line-triangle buckets and calls `Geometry__IntersectSegmentTriangleAndStoreHit`. |

Read-back evidence:

- `ApplyPrimitiveCollisionBridgeReviewWave1098.java dry`: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=180 missing=0 bad=0`
- `ApplyPrimitiveCollisionBridgeReviewWave1098.java apply`: `updated=21 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=180 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyPrimitiveCollisionBridgeReviewWave1098.java final dry`: `updated=0 skipped=21 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Fresh pre/post exports verified `21` metadata rows, `21` tag rows, `79` xref rows, `3707` instruction rows, `21` decompile rows, and `64` vtable-slot rows.
- Export logs reported `targets=21 found=21 missing=0`, `rows=21 missing=0`, `Wrote 79 rows`, `Wrote 3707 function-body instruction rows`, `targets=21 dumped=21 missing=0 failed=0`, and `targets=4 rows=64`.
- Static function-quality closure remains `6410/6410 = 100.00%`, expanded static surface remains `1560/1560 = 100.00%`, Wave911 focused progress remains `812/1408 = 57.67%`, and Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

What this proves:

- The twenty-one target function rows exist in the saved Ghidra project with the expected saved names and signatures.
- The saved tags include `primitive-collision-bridge-review-wave1098` and `wave1098-readback-verified` on every target row.
- The observed bodies, xrefs, and vtable slots are static retail Ghidra evidence for the primitive collision bridge connecting line, cylinder, sphere, geometry, and MeshCollisionVolume swept collision paths.

What remains unproven:

- Runtime collision/trace correctness.
- Exact primitive, vector, AABB, mesh, contact, or vtable object layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1098; primitive-collision-bridge-review-wave1098; 0x004059a0 CCylinder__VFunc_01_004059a0; 0x004098c0 CLine__VFunc_01_004098c0; 0x004098e0 CLine__ctor_copy; 0x00426320 CSphere__VFunc_01_00426320; 0x0043fe20 CCylinder__ResolveCollisionVFunc02; 0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50; 0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds; 0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart; 0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0; 0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore; 0x00478c20 Geometry__IntersectSegmentTriangleAndStoreHit; 0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified; tag-only normalization.
