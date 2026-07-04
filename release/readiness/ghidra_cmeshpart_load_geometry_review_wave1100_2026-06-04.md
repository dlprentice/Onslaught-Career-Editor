# Ghidra CMeshPart Load Geometry Review Wave1100 Readiness Note

Status: complete read-only static review
Date: 2026-06-04
Scope: `cmeshpart-load-geometry-review-wave1100`

Wave1100 re-read twenty-four saved CMeshPart load, geometry-allocation, polybucket, transform, clone, merge, and optimization predicate rows as a focused post-100 static system review. The pass was read-only: no Ghidra names, signatures, comments, tags, function boundaries, or executable bytes were changed; BEA was not launched; no installed-game/runtime file was mutated.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004a51f0 CMeshPart__FreeResources` | Tail entry into `0x004ae640 CMeshPart__FreeOwnedResourcePointers`; frees cached positions/orientations, dynamic vertex/material arrays, bone/link arrays, influence-map runtime buffers, polybucket `+0x100`, helper `+0xfc`, and vtable-owned field `+0x138`. |
| `0x004ae2b0 CMeshPart__CreatePolyBucket` | Lazily allocates the `0xb8`-byte polybucket-style object at part `+0x100`, clones the part, optionally optimizes the clone, builds the bucket, and frees failed bucket/clone resources. |
| `0x004ae860 CMeshPart__AllocateGeometry` | Records DVertex/PVertex/triangle/texcoord/frame counts at `+0xa8/+0xac/+0xb0/+0xb8/+0xb4`, allocates DVertex storage at `+0x134`, per-frame PVertex arrays at `+0x84`, and triangle storage at `+0x80`. |
| `0x004aede0 CMeshPart__LoadOldStyle_VersionA` | Old-style loader with `RET 0x14`; reads `0x60`-byte vertex/material records, negates loaded Z, clamps material indices, initializes material slots, transforms vertices, builds triangle pointers, and rebuilds normals/tangents. |
| `0x004af110 CMeshPart__LoadOldStyle_VersionB_WithExtraBlock` | Adjacent old-style loader with the same `RET 0x14` ABI as VersionA plus an extra 4-byte block per `+0xb8` entry before the per-frame vertex triplet loop. |
| `0x004af470 CMeshPart__LoadVerticesAndTriangles` | Non-skinned loader; reads DVertex/PVertex/triangle stream data, remaps split DVertices, clamps part/material indices, and calls `CMeshPart__RebuildPerVertexNormalsAndTangents`. |
| `0x004afbb0 CMeshPart__LoadVerticesWithBones` | Skinned loader; uses parent mesh tables, reads `influence_count` bone/influence records, handles `format_tag`-specific fields, remaps split DVertices, and rebuilds normals/tangents. |
| `0x004b27a0 CMeshPart__LoadFromStream` | Chunk-reader path deserializes a `0x13c` CMeshPart record, back-links parent mesh at `+0x128`, allocates geometry, reads materials/texcoords/keyframes/bones/weights/slots, optional polybucket data, cache blocks, and `CDXMeshVB` data. |
| `0x004b31f0 CMeshPart__OptimizePolygons` | Runs when PVertex count `+0xac` exceeds `31`; allocates scratch, uses `0.2`/`0.3` thresholds, compares neighborhoods/normals, rewrites triangle indices, and reports removed vertices/polys. |
| `0x004b3b70 CMeshPart__Clone` | Allocates a `0x13c` clone, calls `CMeshPart__Init`, copies transform/bounds/material/name/link metadata, duplicates child/material arrays and geometry data, and remaps triangle DVertex pointers. |
| `0x004b4250 CMeshPart__Merge` | Merges source geometry into destination, builds/interpolates pose transforms with `CMCMech__BuildInterpolatedPoseAndAnchor`, transforms source vertices, remaps source triangle pointers, and updates geometry counts/pointers. |
| `0x004bae70 CMeshPart__CanOptimizePart_Strict` / `0x004bb040 CMeshPart__CanMergeInOptimizePass` | Optimization predicates called by `CMesh__OptimizeParts`; preserve wheel/body/axle, buggy `CORE`/`x1`, turret/barrel, door, mech, tentacle, and barrel-spinner protection evidence. |

Source-reference context:

- `references/Onslaught/ResourceAccumulator.cpp` records `resfile_cmeshpartsize = sizeof(CMeshPart)` and checks serialized resource files against that value, which supports the importance of the observed `0x13c` serialized record size without proving exact Steam retail layout identity.
- The local source-reference tree does not contain matching MeshPart method bodies for this retail slice, so Wave1100 claims remain anchored to Ghidra metadata, xrefs, instructions, decompile, debug path `[maintainer-local-source-export-root]\MeshPart.cpp`, and prior saved read-back comments.

Read-back evidence:

- Fresh read-only exports verified `24` metadata rows, `24` tag rows, `46` xref rows, `6091` instruction rows, and `24` decompile rows.
- Export logs reported `targets=24 found=24 missing=0`, `rows=24 missing=0`, `Wrote 46 rows`, `Wrote 6091 function-body instruction rows`, and `targets=24 dumped=24 missing=0 failed=0`.
- Static function-quality closure remains `6410/6410 = 100.00%`, expanded static surface remains `1560/1560 = 100.00%`, Wave911 focused progress remains `812/1408 = 57.67%`, and Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

What this proves:

- The twenty-four target function rows exist in the saved Ghidra project with saved names, signatures, comments, and tags.
- Fresh xrefs/decompile tie older Wave443/Wave444/Wave447/Wave448/Wave449/Wave458/Wave815/Wave960/Wave1008/Wave1099 evidence into one static CMeshPart load/geometry/free/optimization map.
- The observed CMeshPart loader/allocation/free paths cohere around the `0x13c` record size, DVertex/PVertex/triangle allocation, old-style/new-style/skinned stream loaders, polybucket construction/search, material loading, clone/merge, and optimization predicates.

What remains unproven:

- Runtime mesh loading, skinning, collision, culling, render, or optimization behavior.
- Exact CMeshPart, CMesh, CPolyBucket, DVertex, PVertex, material, bone/influence, `CDXMeshVB`, stream/chunk, or helper-record layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1100; cmeshpart-load-geometry-review-wave1100; 0x004a51f0 CMeshPart__FreeResources; 0x004ae2b0 CMeshPart__CreatePolyBucket; 0x004ae860 CMeshPart__AllocateGeometry; 0x004aede0 CMeshPart__LoadOldStyle_VersionA; 0x004af470 CMeshPart__LoadVerticesAndTriangles; 0x004afbb0 CMeshPart__LoadVerticesWithBones; 0x004b27a0 CMeshPart__LoadFromStream; 0x004b31f0 CMeshPart__OptimizePolygons; 0x004b3b70 CMeshPart__Clone; 0x004b4250 CMeshPart__Merge; 0x004bae70 CMeshPart__CanOptimizePart_Strict; 0x004bb040 CMeshPart__CanMergeInOptimizePass; [maintainer-local-source-export-root]\MeshPart.cpp; resfile_cmeshpartsize; 0x13c; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; read-only review.
