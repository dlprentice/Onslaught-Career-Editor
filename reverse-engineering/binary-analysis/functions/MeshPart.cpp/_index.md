# MeshPart.cpp Functions

> Source File: MeshPart.cpp | Binary: BEA.exe
> Debug Path: 0x0062fe70 (`C:\dev\ONSLAUGHT2\MeshPart.cpp`)

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

CMeshPart represents a sub-component of a 3D mesh in the Battle Engine Aquila rendering system. Each mesh part contains geometry data (vertices, triangles) for a specific material or region, along with bone weights for skeletal animation support.

Wave1159 current-risk update: Wave1159 (`wave1159-cmeshpart-name-pose-current-risk-review`) accounts for `12 CMeshPart name/load/pose current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, no runtime-file mutation, and Codex read-only consults used for candidate/accounting and system-map sanity while Codex root made the final judgment. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `497/1179 = 42.15%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 682; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `33 xref rows` and `1790 instruction rows`. Static anchors include `CMeshPart__LoadOldStyle_VersionA`, `CMeshPart__RebuildPerVertexNormalsAndTangents`, `CMeshPart__PopulatePoseCacheRecursive`, `CMeshPart__EvaluatePoseTransformForFrame`, and `CMesh__FindPartByNameI`. Verified backup: `G:\GhidraBackups\BEA_20260606-004711_post_wave1159_cmeshpart_name_pose_current_risk_review_verified`. Runtime mesh loading, pose-cache, render/collision behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1159; wave1159-cmeshpart-name-pose-current-risk-review; 497/1179 = 42.15%; 12 CMeshPart name/load/pose current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 682; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 33 xref rows; 1790 instruction rows; CMeshPart__LoadOldStyle_VersionA; CMeshPart__RebuildPerVertexNormalsAndTangents; CMeshPart__PopulatePoseCacheRecursive; CMeshPart__EvaluatePoseTransformForFrame; CMesh__FindPartByNameI; G:\GhidraBackups\BEA_20260606-004711_post_wave1159_cmeshpart_name_pose_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave905 static review (`mesh-motion-world-particle-static-review-wave905`) records a `static-coherent mesh/motion/world/particle core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only): `506` rows across `41` families, including `CMeshPart` `54`, `CMesh` `40`, `CWorld` `38`, `CWorldPhysicsManager` `32`, `CThing` `28`, `CParticleManager` `23`, and `CMeshCollisionVolume` `21`; anchors include `CThing__InitRenderThingFromInitMeshName`, `CMesh__LoadByNameWithStatus`, `CMeshPart__PopulatePoseCacheRecursive`, `CWorld__InitOccupancyBitplanes`, `CWorldPhysicsManager__CreateThingByType`, `CParticleManager__Update`, `CParticleSet__LoadFromArchive`, and `CParticleDescriptor__Load`; mesh bridge counts include `213/213` loose meshes, `139/139` embedded meshes, and `352/352` model material/texture-binding rows. Verified backup: `G:\GhidraBackups\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`.

## Wave1100 CMeshPart Load / Geometry Review (2026-06-04)

Wave1100 CMeshPart load geometry review (`cmeshpart-load-geometry-review-wave1100`) re-read twenty-four saved load, geometry-allocation, polybucket, transform, clone, merge, and optimization predicate rows after Wave1099's CMesh resource registry review. The saved names, signatures, comments, and tags remained coherent, so Wave1100 made no Ghidra mutation, no rename, no signature/comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Fresh serialized exports verified `24` metadata rows, `24` tag rows, `46` xref rows, `6091` instruction rows, and `24` decompile rows. Queue closure remains `6410/6410 = 100.00%`; Wave911 focused re-audit progress remains `812/1408 = 57.67%`; expanded static surface remains `1560/1560 = 100.00%`; Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

| Address | Current read-back evidence |
| --- | --- |
| `0x004a51f0 CMeshPart__FreeResources` | Tail entry into `0x004ae640 CMeshPart__FreeOwnedResourcePointers`, releasing cached position/orientation fields, dynamic geometry/material arrays, bone/link/influence buffers, polybucket `+0x100`, helper `+0xfc`, and vtable-owned field `+0x138`. |
| `0x004ae2b0 CMeshPart__CreatePolyBucket` | Allocates the `0xb8` polybucket-style object at `+0x100`, clones the part, optionally calls `CMeshPart__OptimizePolygons`, builds the bucket, and frees failed bucket/clone resources. |
| `0x004ae860 CMeshPart__AllocateGeometry` | Records DVertex/PVertex/triangle/texcoord/frame counts at `+0xa8/+0xac/+0xb0/+0xb8/+0xb4`, then allocates DVertex storage at `+0x134`, PVertex frame tables at `+0x84`, and triangle storage at `+0x80`. |
| `0x004aede0 CMeshPart__LoadOldStyle_VersionA` | Old-style loader with `RET 0x14`; reads `0x60`-byte vertex/material records, negates loaded Z, clamps material indices, transforms vertices, builds triangle pointers, and rebuilds normals/tangents. |
| `0x004af110 CMeshPart__LoadOldStyle_VersionB_WithExtraBlock` | Adjacent old-style loader with the same `RET 0x14` ABI plus an extra 4-byte block per `+0xb8` entry before the per-frame vertex loop. |
| `0x004af470 CMeshPart__LoadVerticesAndTriangles` | Non-skinned loader for DVertex/PVertex/triangle stream data; remaps split DVertices and calls `CMeshPart__RebuildPerVertexNormalsAndTangents`. |
| `0x004afbb0 CMeshPart__LoadVerticesWithBones` | Skinned loader using parent mesh tables, `influence_count` bone/influence records, and `format_tag`-specific fields before remapping split DVertices and rebuilding normals/tangents. |
| `0x004b0800 CMeshPart__ApplyRootTransformRecursive` | Recursive transform helper with `RET 0x44`, a 12-dword transform block, origin floats, optional frame override, child/material recursion through `+0x94/+0x90`, and basis rebuild helpers. |
| `0x004b27a0 CMeshPart__LoadFromStream` | Chunk-reader path that deserializes a `0x13c` CMeshPart record, back-links parent mesh at `+0x128`, allocates geometry, reads materials/texcoords/keyframes/bones/weights/slots, optional polybucket/cache data, and `CDXMeshVB` data. |
| `0x004b3180 CMeshPart__LoadMaterial` | Material loader allocates/updates a `0x28`-byte material record and reads two `0x10`-byte blocks plus trailing dwords through `CChunkReader__Read`. |
| `0x004b31f0 CMeshPart__OptimizePolygons` | PVertex-count gate `+0xac > 31`, scratch allocation, `0.2` / `0.3` thresholds, neighborhood/normal comparison, triangle-index rewriting, and removed vertex/poly reporting. |
| `0x004b3b70 CMeshPart__Clone` | Allocates a `0x13c` clone, calls `CMeshPart__Init`, copies transform/bounds/material/name/link metadata, duplicates geometry arrays, and remaps triangle DVertex pointers. |
| `0x004b4250 CMeshPart__Merge` | Merges source geometry into destination, builds/interpolates pose transforms with `CMCMech__BuildInterpolatedPoseAndAnchor`, transforms source vertices, remaps triangle pointers, and updates counts/pointers. |
| `0x004bae70 CMeshPart__CanOptimizePart_Strict` | `CMesh__OptimizeParts` predicate blocking strict optimization for protected wheel/body/axle, buggy `CORE`/`x1`, turret/barrel, door, mech, tentacle, and barrel-spinner cases. |
| `0x004bb040 CMeshPart__CanMergeInOptimizePass` | Merge-eligibility predicate mirroring the protected token filters and preserving the merge-specific buggy `CORE`/`x1` gate. |

Source-reference context: `references/Onslaught/ResourceAccumulator.cpp` records `resfile_cmeshpartsize = sizeof(CMeshPart)` and checks serialized resource files against that value. That supports the importance of the observed `0x13c` serialized record size without proving exact Steam retail layout identity. Runtime mesh loading, skinning, collision, culling, render, or optimization behavior; exact CMeshPart/CMesh/CPolyBucket/DVertex/PVertex/material/bone/stream layouts; exact source-body identity; BEA patching; gameplay outcomes; and rebuild parity remain separate proof.

Probe token anchor: Wave1100; cmeshpart-load-geometry-review-wave1100; 0x004a51f0 CMeshPart__FreeResources; 0x004ae2b0 CMeshPart__CreatePolyBucket; 0x004ae860 CMeshPart__AllocateGeometry; 0x004aede0 CMeshPart__LoadOldStyle_VersionA; 0x004af470 CMeshPart__LoadVerticesAndTriangles; 0x004afbb0 CMeshPart__LoadVerticesWithBones; 0x004b27a0 CMeshPart__LoadFromStream; 0x004b31f0 CMeshPart__OptimizePolygons; 0x004b3b70 CMeshPart__Clone; 0x004b4250 CMeshPart__Merge; 0x004bae70 CMeshPart__CanOptimizePart_Strict; 0x004bb040 CMeshPart__CanMergeInOptimizePass; C:\dev\ONSLAUGHT2\MeshPart.cpp; resfile_cmeshpartsize; 0x13c; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; read-only review.

## Wave1008 MeshPart Pose Cache Spine Review (2026-05-31)

Wave1008 MeshPart pose cache spine review (`meshpart-pose-cache-spine-review-wave1008`) re-read the Wave817 pose/cache rows after the Wave1007 re-audit. The saved Wave817 names, signatures, comments, and tags remained coherent, so Wave1008 made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Fresh serialized exports verified 3 metadata rows, 3 tag rows, 8 xref rows, 467 body-instruction rows, 3 decompile rows, 6 context metadata rows, 708 context xref rows, 1622 context body-instruction rows, 6 context decompile rows, and 105 callsite instruction rows. Queue closure remains `6223/6223 = 100.00%`; Wave911 focused re-audit progress remains `499/1408 = 35.44%`; expanded static surface progress advances to `679/1478 = 45.94%`; Wave911 top-500 risk-ranked coverage remains `398/500 = 79.60%`. Verified backup: `G:\GhidraBackups\BEA_20260531-150639_post_wave1008_meshpart_pose_cache_spine_review_verified`.

| Address | Current read-back evidence |
| --- | --- |
| `0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive` | Scalarized `RET 0x50` aggregate-stack helper; still calls `CMeshPart__EvaluateAnimatedTransformCore`, writes transform/anchor/cache rows, and recurses through child count/table `+0x90/+0x94`. |
| `0x004b4cd0 CMeshPart__RefreshCachedPoseIfStale` | `RET 0x10` refresh gate using `DAT_008a9aac`, root matrix `DAT_00704db8`, first parent part from `mesh_context+0x160`, and callsite `0x004b4dbc` into `CMeshPart__PopulatePoseCacheRecursive`. |
| `0x004b4de0 CMeshPart__EvaluatePoseTransformForFrame` | Seven-argument cdecl evaluator from `0x00445130`, `0x004ad70a`, raw `0x004dd1cf`, and raw `0x004dede9`; uses defaults `DAT_00704de8` and `DAT_00704db8`, cache refresh, wrapped-frame resolution, CMCMech interpolation, `Vec3__SetXYZ`, and `Mat34__SetRows`. |

Context read-back includes `0x004b0d00 CMeshPart__InterpolateSegmentTransform`, `0x004b0fb0 CMCMech__BuildInterpolatedPoseAndAnchor`, `0x004b24d0 CMeshPart__ResolveWrappedFrameIndexAndLerp`, `0x004b5330 CMeshPart__EvaluateAnimatedTransformCore`, `0x00401ec0 Vec3__SetXYZ`, and `0x00401f10 Mat34__SetRows`. Runtime animation, collision, render, or cache behavior; exact aggregate C types; concrete `CMeshPart`/pose-cache/controller layouts; exact source-body identity; BEA patching; and rebuild parity remain separate proof.

## Wave960 CMeshPart Old-Style Loader Review (2026-05-28)

Wave960 CMeshPart old-style loader review (`cmeshpart-oldstyle-loader-review-wave960`) re-read the old-style loader pair `0x004aede0 CMeshPart__LoadOldStyle_VersionA` and `0x004af110 CMeshPart__LoadOldStyle_VersionB_WithExtraBlock` with current `CMesh__Load` and MeshPart loader context after static export-contract closure. The review made no mutation: no renames, no signature/comment/tag changes, no function-boundary changes, and no executable-byte changes.

Fresh serialized Ghidra exports verified 9 metadata rows, 9 tag rows, 15 xref rows, 729 around-address instruction rows, 7254 function-body instruction rows, 9 decompile-index rows, and 6 direct string dumps. String/version anchors: `C:\dev\ONSLAUGHT2\MeshPart.cpp`, `2.01`, `2.02`, `2.03`, `2.06`, and `HORI`. Current call/ABI anchors include `0x004a8f05`, `0x004a8f49`, `0x004af10d RET 0x14`, and `0x004af462 RET 0x14`; context still contrasts the newer non-skinned/skinned loaders at `0x004af470 CMeshPart__LoadVerticesAndTriangles` and `0x004afbb0 CMeshPart__LoadVerticesWithBones`. Wave911 focused re-audit progress after Wave960 is `305/1408 = 21.66%`; static export-contract closure remains `6151/6151 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260528-123300_post_wave960_cmeshpart_oldstyle_loader_review_verified`.

Continuity note: `test:ghidra-cmeshpart-wave449` and `test:ghidra-cmesh-segment-review-wave914` pass against the current evidence. The historical Wave815 probe still has stale queue/state snapshot expectations, so Wave960 owns the current old-style loader validation. Runtime mesh loading/render/collision behavior, concrete `CMeshPart` layouts, exact source method identity, BEA patching, and rebuild parity remain separate proof.

## Wave817 MeshPart Pose Cache (2026-05-24)

Wave817 meshpart pose cache (`meshpart-pose-cache-wave817`, `wave817-readback-verified`) saved comments/tags/signatures for three adjacent MeshPart pose/cache rows: `0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive`, `0x004b4cd0 CMeshPart__RefreshCachedPoseIfStale`, and `0x004b4de0 CMeshPart__EvaluatePoseTransformForFrame`. The pass corrected three stale locked no-argument signatures to observed ABI forms, made no renames, no function-boundary changes, and no executable-byte changes.

Static read-back evidence:

| Address | Evidence |
| --- | --- |
| `0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive` | Scalarized `RET 0x50` aggregate-stack signature; calls `CMeshPart__EvaluateAnimatedTransformCore`, writes a 12-dword transform and anchor vec4 into pose-cache arrays indexed by `mesh_part+0x88`, stores scalar/cache values, and recurses through child count/table `+0x90/+0x94`. |
| `0x004b4cd0 CMeshPart__RefreshCachedPoseIfStale` | `RET 0x10` cache refresh gate using `DAT_008a9aac`, `this+0x14`, `force_refresh`, pose-controller vtable slots `+0x70/+0x1c/+0x18/+0x20`, root matrix `DAT_00704db8`, first parent part through `mesh_context+0x160`, and callsite `0x004b4dbc` into `CMeshPart__PopulatePoseCacheRecursive`. |
| `0x004b4de0 CMeshPart__EvaluatePoseTransformForFrame` | Seven-argument cdecl ABI from callsites `0x00445130`, `0x004ad70a`, `0x004dd1cf`, and `0x004dede9` with `ADD ESP, 0x1c`; initializes `DAT_00704de8` anchor and `DAT_00704db8` transform outputs, chooses cached-pose refresh/copy or wrapped-frame interpolation, and can apply pose-controller transform callbacks through `Vec3__SetXYZ` and `Mat34__SetRows`. |

Queue telemetry after Wave817 is 6098 total, 5605 commented, 493 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5605/6098 = 91.92%`, strict proxy `5605/6098 = 91.92%`, and next raw commentless row `0x004b7d90 CGame__PumpBinkVoiceSampleQueue`. Verified backup: `G:\GhidraBackups\BEA_20260524-154905_post_wave817_meshpart_pose_cache_verified`. Exact source aggregate C types, concrete MeshPart/cache/controller layouts, exact source-body identity, runtime animation/render/collision behavior, BEA patching, and rebuild parity remain deferred.

## Wave816 Mesh Animation Tail (2026-05-24)

Wave816 mesh animation tail (`mesh-animation-tail-wave816`, `wave816-readback-verified`) saved comments/tags for `0x004b0cd0 CMesh__SelectModeSpecificPtr`, `0x004b0d00 CMeshPart__InterpolateSegmentTransform`, and `0x004b0fb0 CMCMech__BuildInterpolatedPoseAndAnchor`. The pass corrected two stale locked no-argument signatures to observed `__thiscall` stack-cleanup forms, made no renames, no function-boundary changes, and no executable-byte changes.

Static read-back evidence:

| Address | Evidence |
| --- | --- |
| `0x004b0cd0 CMesh__SelectModeSpecificPtr` | Mesh-side mode selector included as the tranche head; reads `+0x8c` and returns `this`, alternate pointer `+0x124`, or null depending on mode. |
| `0x004b0d00 CMeshPart__InterpolateSegmentTransform` | Sole direct callsite `0x004b17fc` pushes five stack arguments and sets `ECX` to the part; the callee exits with `RET 0x14`, clamps frame indices against `+0xb8`, maps through byte table `+0xc4`, reads anchors at `+0xc8`, reads transform rows at `+0x10c`, and writes output transform/anchor buffers. |
| `0x004b0fb0 CMCMech__BuildInterpolatedPoseAndAnchor` | MeshPart cache/render context helper included because it calls `CMeshPart__InterpolateSegmentTransform`; representative callsites push nine stack dwords and the body exits with `RET 0x24`, using global pose cache slots `DAT_00704cf0`/`DAT_00704d20`, anchors `DAT_00704cd0`/`DAT_00704ce0`, parent part `+0x98`, and optional pose-controller vtable callbacks. |

Queue telemetry after Wave816 is 6098 total, 5602 commented, 496 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5602/6098 = 91.87%`, strict proxy `5602/6098 = 91.87%`, and next raw commentless row `0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive`. Verified backup: `G:\GhidraBackups\BEA_20260524-151844_post_wave816_mesh_animation_tail_verified`. Exact concrete CMesh/CMeshPart/CMCMech/controller layouts, exact source-body identity, runtime animation/render/collision behavior, BEA patching, and rebuild parity remain deferred.

## Wave815 MeshPart Tail (2026-05-24)

Wave815 meshpart tail (`meshpart-tail-wave815`, `wave815-readback-verified`) saved comments/tags for `0x004adf80 CMesh__ClearField08`, corrected `0x004ae640 CMeshPart__FreeOwnedResourcePointers_004ae640` to `0x004ae640 CMeshPart__FreeOwnedResourcePointers`, and corrected the old-style loader signatures for `0x004aede0 CMeshPart__LoadOldStyle_VersionA` and `0x004af110 CMeshPart__LoadOldStyle_VersionB_WithExtraBlock`. The pass made one rename, corrected two stale locked no-argument signatures to `__thiscall` plus five stack arguments, made no function-boundary changes, and made no executable-byte changes.

Static read-back evidence:

| Address | Evidence |
| --- | --- |
| `0x004adf80 CMesh__ClearField08` | CMesh-side 0x24-byte embedded record field-clear helper documented here because it is paired with `CMeshPart__FreeOwnedResourcePointers` in the same tail tranche. |
| `0x004ae640 CMeshPart__FreeOwnedResourcePointers` | Shared owned-resource free body reached by `0x004a51f0 CMeshPart__FreeResources` tail jump and `CMeshPart__CreatePolyBucket` failure cleanup. Observed freed fields include `+0x104`, `+0x108`, `+0x94`, `+0x134`, frame table `+0x84` count `+0xb4`, triangle pointer `+0x80`, texcoord/material arrays, polybucket `+0x100`, helper `+0xfc`, and vtable-owned field `+0x138`. |
| `0x004aede0 CMeshPart__LoadOldStyle_VersionA` | `CMesh__Load` callsite `0x004a8f05` sets `ECX=ESI` and pushes five stack arguments; the function ends with `RET 0x14`, replacing the stale locked no-argument signature. |
| `0x004af110 CMeshPart__LoadOldStyle_VersionB_WithExtraBlock` | `CMesh__Load` callsite `0x004a8f49` uses the same five-stack-argument ABI, and epilogue `0x004af462` uses `RET 0x14`; VersionB consumes an extra per-count 4-byte block tied to part offset `+0xb8`. |

Queue telemetry after Wave815 is 6098 total, 5599 commented, 499 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5599/6098 = 91.82%`, strict proxy `5599/6098 = 91.82%`, and next raw commentless row `0x004b0cd0 CMesh__SelectModeSpecificPtr`. Verified backup: `G:\GhidraBackups\BEA_20260524-144421_post_wave815_meshpart_tail_verified`. Exact concrete CMesh/CMeshPart layouts, exact old mesh-format schema, exact source-body identity, extra-block field meaning, runtime mesh loading/render/collision behavior, BEA patching, and rebuild parity remain deferred.

## Wave814 Mesh Segment Tail Caller Evidence (2026-05-24)

Wave814 mesh segment tail (`mesh-segment-tail-wave814`, `wave814-readback-verified`) corrected four adjacent CMesh helper rows that also affect MeshPart caller read-back: `0x004aa4e0 CMesh__SumChainedField1C`, `0x004aa500 CMesh__GetChainedRecordNameAndIdByIndex`, `0x004aa6b0 CMesh__GetNameOrUnknown`, and `0x004aa8a0 CMesh__FindPartByNameI`. MeshPart evidence specifically shows `CMeshPart__CreatePolyBucket` calling `CMesh__GetNameOrUnknown` through its parent mesh pointer, while the same wave records global mesh list `DAT_00704ad8`, empty-string fallback `0x00662b2c`, unknown-name fallback `0x0062f8d4`, post-wave strict proxy `5595/6098 = 91.75%`, and next raw commentless row `0x004adf80 CMesh__ClearField08`. Verified backup: `G:\GhidraBackups\BEA_20260524-141602_post_wave814_mesh_segment_tail_verified`. Exact concrete CMesh/CMeshPart/CRTMesh/destructible layouts, exact source-body identity, runtime mesh/destructible/RTMesh behavior, BEA patching, and rebuild parity remain deferred.

## Wave811 CMesh LegMotion Animation Caller Evidence (2026-05-24)

Wave811 CMesh LegMotion animation (`cmesh-legmotion-animation-wave811`, `wave811-readback-verified`) corrected stale `0x0049c2d0 CMeshPart__HasAnimationToken_623074` to `0x0049c2d0 CMesh__HasLegMotionAnimation` after caller read-back showed the helper is CMesh-owned. The saved signature is `bool __cdecl CMesh__HasLegMotionAnimation(void * mesh)`: the helper pushes string token `0x00623074` (`LegMotion`), calls `CMesh__FindAnimationIndexByName`, and returns whether the lookup result is not `-1`.

MeshPart caller evidence remains important: `CMeshPart__CanOptimizePart_Strict` and `CMeshPart__CanMergeInOptimizePass` call `CMesh__HasLegMotionAnimation` after passing `part+0x128`, while `CMesh__HasSpecialOptimizationConstraints` passes its `mesh` argument directly. Queue telemetry after Wave811 is `6098` total, `5586` commented, `512` commentless, 0 exact-undefined signatures, 0 `param_N`, and strict proxy `5586/6098 = 91.60%`; next raw commentless row is `0x004a25c0 CLTShell__ValidateAndRollHeapDeltas`. Verified backup: `G:\GhidraBackups\BEA_20260524-125806_post_wave811_cmesh_legmotion_animation_verified`. Exact `part+0x128` field meaning, concrete `CMesh`/`CMeshPart` layouts, source identity, runtime mesh optimization behavior, runtime animation behavior, BEA patching, and rebuild parity remain deferred.

## Wave758 MeshPart.cpp Unwind Continuation (2026-05-23)

Wave758 static read-back (`unwind-continuation-wave758`, `wave758-readback-verified`) saved comments/tags/signatures for MeshPart.cpp-adjacent compiler-generated SEH unwind allocation-cleanup callbacks from `0x005d39b0 Unwind@005d39b0` through `0x005d3a99 Unwind@005d3a99`. Evidence includes MeshPart.cpp debug path `0x0062fe70`, DATA scope-table xrefs `0x0061c614` through `0x0061c6c4`, and seven `OID__FreeObject_Callback` rows. Exact anchors include `0x005d3a10 Unwind@005d3a10`. Verified backup: `G:\GhidraBackups\BEA_20260523-123821_post_wave758_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

| Address | Evidence |
| --- | --- |
| 0x005d39b0 | DATA xref `0x0061c614`; `OID__FreeObject_Callback(*(EBP-0x10))` with line token `0x46` and allocation/type value `0xe9`. |
| 0x005d39e0 | DATA xref `0x0061c63c`; `OID__FreeObject_Callback(*(EBP-0x10))` with allocation/type value `0x15f`. |
| 0x005d3a10 | DATA xref `0x0061c664`; `OID__FreeObject_Callback(*(EBP-0x154))` with line token `0x74` and allocation/type value `0x717`. |
| 0x005d3a40 | DATA xref `0x0061c68c`; `OID__FreeObject_Callback(*(EBP+0x8))` with allocation/type value `0xa2a`. |
| 0x005d3a59 | DATA xref `0x0061c694`; `OID__FreeObject_Callback(*(EBP+0x8))` with line token `0x74` and allocation/type value `0xab6`. |
| 0x005d3a80 | DATA xref `0x0061c6bc`; `OID__FreeObject_Callback(*(EBP-0x10))` with allocation/type value `0xc28`. |
| 0x005d3a99 | DATA xref `0x0061c6c4`; `OID__FreeObject_Callback(*(EBP-0x10))` with allocation/type value `0xc58`. |

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004a51f0 | CMeshPart__FreeResources | Tail entry used by CMesh teardown; jumps into the shared owned-resource free body | ~5-byte thunk plus 0x004ae640 body |
| 0x004aa3f0 | CMeshPart__CopyPrimaryAxesToOutVec3Triplet | Copies the part's primary basis/axis triplet into an output vec3 array | ~32 bytes |
| 0x004adff0 | CMeshPart__SetVertexCount | Allocates vertex arrays (positions, UVs, colors, normals) | ~176 bytes |
| 0x004ae2b0 | CMeshPart__CreatePolyBucket | Creates polygon bucket for rendering optimization | ~256 bytes |
| 0x004ae4b0 | CMeshPart__Init | Initializes mesh part with default values and matrices | ~400 bytes |
| 0x004ae640 | CMeshPart__FreeOwnedResourcePointers | Wave815 shared owned-resource free body reached by the 0x004a51f0 tail entry and failure cleanup | bounded |
| 0x004ae860 | CMeshPart__AllocateGeometry | Allocates DVertices, PVertices, and Triangles arrays | ~480 bytes |
| 0x004aede0 | CMeshPart__LoadOldStyle_VersionA | Wave815 old-style loader with `RET 0x14` and five stack arguments after `this` | bounded |
| 0x004af110 | CMeshPart__LoadOldStyle_VersionB_WithExtraBlock | Wave815 old-style loader variant with `RET 0x14` and extra `+0xb8` block handling | bounded |
| 0x004af470 | CMeshPart__LoadVerticesAndTriangles | Loads vertex/triangle data from file stream | ~1856 bytes |
| 0x004afbb0 | CMeshPart__LoadVerticesWithBones | Loads vertices with bone weights for skinned meshes | ~2720 bytes |
| 0x004b0800 | CMeshPart__ApplyRootTransformRecursive | Applies parent transform data to the part and recursively propagates child/material transforms | ~1024 bytes |
| 0x004b0c00 | CMeshPart__GetBasisX | Writes the part X-basis vector to an output vec3 | ~32 bytes |
| 0x004b0c20 | CMeshPart__GetBasisY | Writes the part Y-basis vector to an output vec3 | ~32 bytes |
| 0x004b0c40 | CMeshPart__FindNearestVertexIndex | Finds the nearest first-frame PVertex to a supplied query position | ~192 bytes |
| 0x004b0d00 | CMeshPart__InterpolateSegmentTransform | Wave816 frame/anchor/transform interpolation helper; observed `RET 0x14` stack cleanup | bounded |
| 0x004b0fb0 | CMCMech__BuildInterpolatedPoseAndAnchor | Wave816 CMCMech pose/cache bridge called by MeshPart cache/render paths; observed `RET 0x24` stack cleanup | bounded |
| 0x004b1a40 | CMeshPart__CacheFrameData | Builds optional per-frame position and transform caches | ~464 bytes |
| 0x004b1d30 | CMeshPart__LinkDamagedPartVariantsBySuffix | Links sibling damaged-part variants by `_damaged` suffix and optional damage number | ~384 bytes |
| 0x004b1eb0 | CMeshPart__RebuildPerVertexNormalsAndTangents | Rebuilds accumulated per-vertex normal/tangent-style vectors from first-frame triangles | ~720 bytes |
| 0x004b24d0 | CMeshPart__ResolveWrappedFrameIndexAndLerp | Resolves wrapped animation frame index and writes fractional lerp output | ~256 bytes |
| 0x004b27a0 | CMeshPart__LoadFromStream | Main deserialization - loads entire mesh part from stream | ~2560 bytes |
| 0x004b3180 | CMeshPart__LoadMaterial | Loads material/shader data (40 bytes struct) | ~112 bytes |
| 0x004b31f0 | CMeshPart__OptimizePolygons | Removes redundant vertices and degenerate triangles | ~2400 bytes |
| 0x004b3b70 | CMeshPart__Clone | Deep copies mesh part including all geometry data | ~1760 bytes |
| 0x004b4250 | CMeshPart__Merge | Merges another mesh part into this one | ~768 bytes |
| 0x004b4ba0 | CMeshPart__PopulatePoseCacheRecursive | Wave817 recursive pose-cache population helper with scalarized `RET 0x50` aggregate-stack signature | bounded |
| 0x004b4cd0 | CMeshPart__RefreshCachedPoseIfStale | Wave817 timestamp-gated pose-cache refresh helper with `RET 0x10` stack cleanup | bounded |
| 0x004b4de0 | CMeshPart__EvaluatePoseTransformForFrame | Wave817 seven-argument cdecl pose transform evaluator used by dive-bomber, mesh-collision, and raw render/update sites | bounded |
| 0x004bae70 | CMeshPart__CanOptimizePart_Strict | Strict optimization predicate called by `CMesh__OptimizeParts` | bounded |
| 0x004bb040 | CMeshPart__CanMergeInOptimizePass | Merge-eligibility predicate called by `CMesh__OptimizeParts` | bounded |
| 0x004b5330 | CMeshPart__EvaluateAnimatedTransformCore | Evaluates animated transform/frame interpolation and writes pose/current-part outputs; signature deferred | ~1952 bytes |
| 0x004b5ad0 | CMeshPart__RenderAnimatedRecursive | Recursive mesh-part render wrapper around animated transform evaluation and mesh render dispatch; signature deferred | ~944 bytes |
| 0x0049f600 | CMeshPart__NameAvoidsBarrelSpinnerOptimizationTokens | Returns false for protected barrel/spinner optimization names and true otherwise | ~100 bytes |
| 0x0049f670 | CMeshPart__AnyChildNameMatchesBarrelSpinnerOptimizationTokens | Scans child names for the same barrel/spinner optimization-token set | ~430 bytes |
| 0x00495030 | CMeshPart__PassesBuggyCoreStateForStrictOptimize | Buggy-specific optimize gate used by strict mesh-part optimize checks | ~96 bytes |
| 0x00495090 | CMeshPart__PassesBuggyCoreStateForMergeOptimize | Buggy-specific optimize gate used by merge optimize checks | ~96 bytes |

## Recent Headless Semantic Promotions (2026-02-26)

| Address | Symbol | Description |
|---------|--------|-------------|
| `0x004ae110` | `CMeshPart__StartTriangleBucketSearch` | Starts triangle polybucket search and maps local triangle indices to mesh triangle pointers |
| `0x004ae1a0` | `CMeshPart__GetNextTriangleFromBucketSearch` | Advances active triangle search and maps next local indices to mesh triangle pointers |
| `0x004ae220` | `CMeshPart__StartLineTriangleBucketSearch` | Starts line-triangle polybucket search and maps first local indices to mesh triangle pointers |
| `0x004ae430` | `CMeshPart__GetNextLineTriangleFromBucketSearch` | Advances line-triangle search and maps next local indices to mesh triangle pointers |
| `0x004a51f0` | `CMeshPart__FreeResources` | Wave443 CMesh-head pass saved the public tail entry called by CMesh teardown; it jumps into the owned-resource free body at `0x004ae640`. |
| `0x004aa3f0` | `CMeshPart__CopyPrimaryAxesToOutVec3Triplet` | Wave444 saved signature/comment/tag read-back for the helper that copies part offsets `+0x00/+0x10/+0x20` to an output vec3 triplet; callers include `CMesh__Load`, `CMeshPart__ApplyRootTransformRecursive`, and `CSoundManager__UpdateSoundPosition`. |
| `0x004ae640` | `CMeshPart__FreeOwnedResourcePointers` | Wave815 owner/name cleanup for the bulk free body reached by the `0x004a51f0` tail entry; frees owned resource pointers/arrays while exact field identities remain bounded |

## Wave447 CMeshPart Bucket / Allocation Hardening

Fresh metadata, decompile, xref, instruction, and tag read-back on 2026-05-16 hardened nine existing CMeshPart functions in the queue-head mesh-part cluster. `ApplyCMeshPartWave447.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_cmeshpart_wave447_probe.py --check` passed.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004adff0` | `void __thiscall CMeshPart__SetVertexCount(void * this, int vertex_count)` | Clears any previous five-pointer vertex channel block at `+0x0c..+0x1c`, stores the new count at `+0x08`, allocates `vertex_count * 0x14`, and derives channel pointers. |
| `0x004ae110` | `int __thiscall CMeshPart__StartTriangleBucketSearch(void * this, int search_key0, int search_key1, void * out_triangle_vertices, void * query_context)` | Starts a polybucket triangle search through part `+0x100`, calls `CPolyBucket__StartSearch`, and writes the first mapped vertex triplet. |
| `0x004ae1a0` | `int __thiscall CMeshPart__GetNextTriangleFromBucketSearch(void * this, void * out_triangle_vertices, void * query_context)` | Advances the active triangle search with `CPolyBucket__GetNextTriangle` and writes the next mapped vertex triplet. |
| `0x004ae220` | `int __thiscall CMeshPart__StartLineTriangleBucketSearch(void * this, int line_arg0, int line_arg1, void * out_triangle_vertices, void * query_context)` | Starts a line-triangle polybucket search with `CPolyBucket__StartLineSearch`; callers include `CMeshCollisionVolume__VFunc_04_004ad830` and `CStaticShadows__BuildShadowMaps`. |
| `0x004ae2b0` | `void __fastcall CMeshPart__CreatePolyBucket(void * this)` | Lazily allocates a 0xb8-byte bucket-style object at part `+0x100` for mesh types 1 or 3, clones/optionally optimizes the part, builds the bucket, and releases failed bucket/clone resources. |
| `0x004ae430` | `int __thiscall CMeshPart__GetNextLineTriangleFromBucketSearch(void * this, void * out_triangle_vertices, void * line_search_context, void * query_context)` | Advances line-triangle search with `CPolyBucket__GetNextLineTriangle` and writes the next mapped vertex triplet. |
| `0x004ae4b0` | `void * __fastcall CMeshPart__Init(void * this)` | Clears observed fields, copies the global 4x3 basis block, seeds defaults, allocates a 0x28-byte helper and a 0x128-byte CDXMeshVB-style object, then back-links that object to the part. |
| `0x004ae860` | `int __thiscall CMeshPart__AllocateGeometry(void * this, int dvertex_count, int pvertex_count, int triangle_count, int texcoord_count, int frame_count)` | Records geometry counts, allocates DVertex storage, per-frame PVertex pointer slots and arrays, and triangle storage. |
| `0x004aea50` | `void __fastcall CMeshPart__ComputeLocalBoundsAndBoundingRadius(void * this)` | Scans first-frame vertices, computes min/max local bounds, writes center/extents/status into helper record `+0xfc`, stores median extent at `+0x130`, and computes radius/magnitude fields. |

These are saved static Ghidra facts only. They do not prove runtime mesh loading, rendering, collision, static-shadow behavior, concrete `CMeshPart`/polybucket/helper layouts, exact field names/types, exact source-body identity, BEA launch behavior, game patching, or rebuild parity.

## Wave448 CMeshPart Transform / Cache Hardening

Fresh metadata, decompile, xref, instruction, and tag read-back on 2026-05-16 hardened eight existing CMeshPart transform/cache/accessor functions. `ApplyCMeshPartWave448.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_cmeshpart_wave448_probe.py --check` passed.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004b0800` | `void __thiscall CMeshPart__ApplyRootTransformRecursive(void * this, int parent_transform_dword00, int parent_transform_dword01, int parent_transform_dword02, int parent_transform_dword03, int parent_transform_dword04, int parent_transform_dword05, int parent_transform_dword06, int parent_transform_dword07, int parent_transform_dword08, int parent_transform_dword09, int parent_transform_dword10, int parent_transform_dword11, float origin_x, float origin_y, float origin_z, float origin_w, void * frame_override_part)` | `ret 0x44` stack cleanup matches a 12-dword parent transform block, four origin/offset floats, and an optional frame-override part pointer; the body recurses through child/material pointers at `+0x94/+0x90`, translates `+0x60..+0x6c`, and refreshes cached transform/position blocks. |
| `0x004b0c00` | `void * __thiscall CMeshPart__GetBasisX(void * this, void * out_vec3)` | Writes offsets `+0x04`, `+0x14`, and `+0x24` into the caller output vec3 and returns that output pointer; instruction evidence ends with `ret 0x4`. |
| `0x004b0c20` | `void * __thiscall CMeshPart__GetBasisY(void * this, void * out_vec3)` | Writes offsets `+0x08`, `+0x18`, and `+0x28` into the caller output vec3 and returns that output pointer; instruction evidence ends with `ret 0x4`. |
| `0x004b0c40` | `int __thiscall CMeshPart__FindNearestVertexIndex(void * this, float query_x, float query_y, float query_z, float query_w_unused)` | Scans the first PVertex frame through `+0x84`, compares up to `+0xac` vertices against the supplied query position, and returns the nearest vertex index; the fourth stack float is retained for the observed `ret 0x10` cleanup. |
| `0x004b1a40` | `void __fastcall CMeshPart__CacheFrameData(void * this)` | Chooses cached frame count at `+0x118`, detects identity/zero-position shortcuts at `+0x120/+0x11c`, allocates optional caches at `+0x104/+0x108`, and calls `CMCMech__BuildInterpolatedPoseAndAnchor` per cached frame. |
| `0x004b1d30` | `void __fastcall CMeshPart__LinkDamagedPartVariantsBySuffix(void * this)` | Scans the parent mesh part table at `+0x128/+0x15c/+0x160` for sibling part names sharing the current prefix and `_damaged` suffix, parses optional damage numbers, warns on duplicates, chains variants through `+0x9c/+0xa0`, and marks linked variants at `+0xa4`. |
| `0x004b1eb0` | `void __thiscall CMeshPart__RebuildPerVertexNormalsAndTangents(void * this, int update_primary_normal)` | Below the observed `10001` DVertex guard, walks each DVertex and triangle, accumulates normalized face vectors from the first PVertex frame, optionally updates the primary normal based on `update_primary_normal`, and writes fallback axes when no contributing faces exist. |
| `0x004b24d0` | `int __thiscall CMeshPart__ResolveWrappedFrameIndexAndLerp(void * this, float frame_delta, int frame_table_index, void * out_lerp, void * frame_adjuster)` | Uses the parent mesh frame table and frame delta to compute an animation frame value, optionally lets `frame_adjuster` vfunc `+0x14` mutate that value, stores fractional lerp in `out_lerp`, and returns the wrapped frame index. |

These are saved static Ghidra facts only. They do not prove runtime animation, rendering, damage-variant swapping, concrete `CMeshPart` transform/cache/vertex layouts, exact field names/types, exact source-body identity, BEA launch behavior, game patching, or rebuild parity.

## Wave449 CMeshPart Load / Optimize Hardening

Fresh metadata, decompile, xref, instruction, callsite, and tag read-back on 2026-05-16 hardened eight existing CMeshPart load/deserialize/material/optimize/clone/merge functions plus the adjacent `CMesh__GetRandomVertexFromPolyBucket` helper. `ApplyCMeshPartWave449.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_cmeshpart_wave449_probe.py --check` passed.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004af470` | `void __thiscall CMeshPart__LoadVerticesAndTriangles(void * this, void * mem_buffer, void * part_table_entry, void * first_part_record, int part_index_limit, int unused_legacy_arg)` | Loads non-skinned DVertex/PVertex/triangle stream data, negates loaded Z components, clamps material/part indices against `part_index_limit`, handles split DVertex remapping, and ends with `ret 0x14`. The `0x004a8f5c` caller shows four immediate pushes plus an earlier retained `push 0`, so the unused legacy arg is kept for stack cleanup. |
| `0x004afbb0` | `void __thiscall CMeshPart__LoadVerticesWithBones(void * this, void * mem_buffer, void * parent_mesh, int unused_arg3, int part_index_limit, int unused_arg5, int influence_count, int format_tag)` | Loads skinned vertex/triangle data, resolves indices through `parent_mesh`, processes `influence_count` records per DVertex, handles `format_tag`-specific fields, normalizes/selects bone slots, and ends with `ret 0x1c`. |
| `0x004b27a0` | `void * __cdecl CMeshPart__LoadFromStream(void * chunk_reader, void * mesh_part, void * parent_mesh)` | Deserializes a 0x13c part from a chunk reader, back-links parent mesh, allocates optional geometry/cache/bone structures, calls `CMeshPart__LoadMaterial`, optionally loads `CPolyBucket`, and returns `mesh_part`. |
| `0x004b3180` | `void * __cdecl CMeshPart__LoadMaterial(void * chunk_reader, void * existing_material)` | Advances the chunk reader, allocates a 0x28-byte material when needed, reads two 0x10-byte blocks plus trailing dwords at `+0x20/+0x24`, and returns the material pointer. |
| `0x004b31f0` | `void __fastcall CMeshPart__OptimizePolygons(void * this)` | Runs when PVertex count at `+0xac` exceeds 31, allocates scratch arrays, uses threshold `0.2` or `0.3` above 300 vertices, compares triangle neighborhoods/normals, rewrites triangle vertex indices, and reports removed vertices/polys. |
| `0x004b3b70` | `void * __fastcall CMeshPart__Clone(void * this)` | Deep-clones a 0x13c CMeshPart after `CMeshPart__Init`, copying transforms, bounds, material/name/link metadata, geometry arrays, remapped triangle pointers, and optional keyframe/FOV/texcoord/bone/weight/slot data. |
| `0x004b4250` | `void __thiscall CMeshPart__Merge(void * this, void * source_part)` | Merges `source_part` into this part, allocates combined geometry arrays, copies existing geometry, builds/interpolates pose transforms, transforms source geometry through cofactor/determinant matrix math, remaps source triangle pointers, and updates counts/pointers; `ret 0x4` confirms one stack arg. |

The adjacent `0x004b25d0` `CMesh__GetRandomVertexFromPolyBucket` entry is documented in [../mesh.cpp/_index.md](../mesh.cpp/_index.md). These are saved static Ghidra facts only. They do not prove runtime mesh loading, skinning, rendering, material behavior, polygon optimization effects, clone/merge ownership, concrete `CMeshPart`/DVertex/PVertex/material/polybucket layouts, exact source identities, BEA launch behavior, game patching, or rebuild parity.

## Wave452 Render / Sort Hardening

Fresh metadata, decompile, xref, instruction, callsite, and tag read-back on 2026-05-16 hardened the render/sort tranche touching `CMeshPart`, `CSphere`, and `CMeshRenderer` render paths. `ApplyRenderSortWave452.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_render_sort_wave452_probe.py --check` passed.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004b5330` | `int CMeshPart__EvaluateAnimatedTransformCore(void)` | Comment/tag hardening only. The body evaluates animation-frame interpolation, writes transform/current-part outputs, and reaches `CMCMech__BuildInterpolatedPoseAndAnchor`; signature remains deferred because neighboring callsites mix normal cdecl arguments with by-value matrix/vector stack material. |
| `0x004b5ad0` | `int CMeshPart__RenderAnimatedRecursive(void)` | Comment/tag hardening only. The body prepares optional orientation/controller transforms, calls `CMeshPart__EvaluateAnimatedTransformCore`, dispatches `CMeshRenderer__RenderMesh`, and recurses across child part lists at `+0x90/+0x94`; signature remains deferred for the same by-value stack-shape reason. |
| `0x004b5e80` | `int CSphere__RenderPartsWithOrientation(void)` | Comment/tag hardening only. The body iterates the sphere mesh-part table, applies controller orientation transforms, prepares local matrices, and dispatches visible entries through `CMeshRenderer__RenderMesh`; signature remains deferred. |
| `0x004b6260` | `int CSphere__RenderAnimatedRecursive(void)` | Comment/tag hardening only. The body chooses cached-pose rendering, `CSphere__RenderPartsWithOrientation`, or `CMeshPart__RenderAnimatedRecursive`, then optionally follows linked/sibling parts through `+0x8`; signature remains deferred. |

These are saved static Ghidra facts only. They do not prove runtime rendering, exact `CMeshPart`/`CSphere` layouts, by-value matrix/vector types, exact source identities, BEA launch behavior, game patching, or rebuild parity.

## Wave458 CMeshPart Optimization Predicate Hardening

Fresh metadata, decompile, xref, instruction, and tag read-back on 2026-05-16 hardened the two CMeshPart optimization predicates called by `CMesh__OptimizeParts`. `ApplyMeshOptimizationWave458.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_mesh_optimization_wave458_probe.py --check` passed.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004bae70` | `int __cdecl CMeshPart__CanOptimizePart_Strict(void * part)` | Called by `CMesh__OptimizeParts` at `0x004ab549` and `0x004ab750` with one CMeshPart pointer. The body checks parent-mesh animation/protected-token conditions including wheel/body/axle, buggy `CORE`/`x1`, turret/barrel, door, mech, tentacle, and barrel-spinner cases before allowing strict part removal/optimization. |
| `0x004bb040` | `int __cdecl CMeshPart__CanMergeInOptimizePass(void * part)` | Called by `CMesh__OptimizeParts` at `0x004ab44e`, `0x004ab46e`, and `0x004ab565`. It mirrors the protected-token filters, uses the merge-specific buggy `CORE`/`x1` gate, and preserves observed shared true-return helper paths. |

The companion `0x004bb210` `CMesh__HasSpecialOptimizationConstraints` entry is documented in [../mesh.cpp/_index.md](../mesh.cpp/_index.md). These are saved static Ghidra facts only. They do not prove runtime optimization behavior, concrete `CMeshPart` layouts, exact field names/types, exact source-body identity, BEA launch behavior, game patching, or rebuild parity.

## CMeshPart Structure (Size: 0x13C = 316 bytes)

Key offsets discovered from decompilation:

| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| 0x00-0x2F | float[12] | Transform matrix | 4x3 matrix copied from global data |
| 0x30-0x5F | float[12] | Additional matrix | Copied during clone |
| 0x70-0x7F | float[4] | Bounding data | Copied during clone |
| 0x80 | int* | mTriangles | Triangle index array (12 bytes per tri) |
| 0x84 | int** | mPVertices | Per-frame vertex positions array |
| 0x88 | int | mPartIndex | Part identifier |
| 0x8c | int | mMeshType | 1=static, 3=skinned (triggers bone loading) |
| 0x90 | int | mNumMaterials | Count of material references |
| 0x94 | int* | mMaterials | Material pointer array |
| 0x98 | int* | mNextPart | Linked list - next part |
| 0x9c | int* | mPrevPart | Linked list - previous part |
| 0xa4 | int | Unknown | Copied during clone |
| 0xa8 | int | mNumDVertices | Dynamic vertex count |
| 0xac | int | mNumPVertices | Per-frame vertex count |
| 0xb0 | int | mNumTriangles | Triangle count |
| 0xb4 | int | mNumFrames | Animation frame count |
| 0xb8 | int | mNumTexCoords | Texture coordinate count |
| 0xbc | int | mNumKeyframes | Keyframe count for animation |
| 0xc0 | int | mNumBones | Bone count (skinned meshes only) |
| 0xc4 | byte* | mTexCoordData | Texture coordinate array |
| 0xc8 | float* | mPositionData | Position keyframe data |
| 0xcc | int* | mFOVData | Field-of-view keyframe data |
| 0xd0 | int* | mBoneIndices | Bone index mapping |
| 0xd4 | float** | mBoneWeights | Per-vertex bone weights |
| 0xd8 | int** | mBoneSlots | Bone slot assignments (3 per vertex) |
| 0xdc | char[60] | mName | Part name string (debug) |
| 0xfc | void* | mMaterial | Material structure pointer (40 bytes) |
| 0x100 | void* | mPolyBucket | Polygon bucket for rendering |
| 0x104 | float* | mPositionCache | Cached positions per frame |
| 0x108 | float* | mOrientationCache | Cached orientations per frame (0x30 bytes each) |
| 0x10c | void* | mKeyframeMatrix | Keyframe transformation matrices |
| 0x118 | int | mCachedFrameCount | Number of cached frames |
| 0x11c | int | mHasZeroPosition | Optimization flag |
| 0x120 | int | mHasIdentityMatrix | Optimization flag |
| 0x124 | int* | mSomePointer | Unknown reference |
| 0x128 | int* | mParentMesh | Pointer to parent CMesh |
| 0x12c | int | Unknown | |
| 0x130 | int | mFlags | Various flags |
| 0x134 | void* | mDVertices | Dynamic vertex array (0x60 bytes each) |
| 0x138 | int | mSomeValue | Preserved during load |

## Vertex Structures

### DVertex (Dynamic Vertex) - 0x60 bytes (96 bytes)
| Offset | Type | Field |
|--------|------|-------|
| 0x00-0x0F | float[4] | Position (x, y, z, w) |
| 0x20 | float | Normal X |
| 0x24 | float | Normal Y |
| 0x28 | float | Normal Z (negated on load) |
| 0x2c | uint | Color (ARGB, byte-swapped) |
| 0x30-0x47 | int[6] | Material/texture references (-1 = none) |

### PVertex (Per-frame Vertex) - 0x10 bytes (16 bytes)
| Offset | Type | Field |
|--------|------|-------|
| 0x00 | float | X position |
| 0x04 | float | Y position |
| 0x08 | float | Z position |
| 0x0c | float | W (usually 1.0) |

### Triangle - 0x0C bytes (12 bytes)
| Offset | Type | Field |
|--------|------|-------|
| 0x00 | int* | Vertex 0 pointer (into DVertices) |
| 0x04 | int* | Vertex 1 pointer |
| 0x08 | int* | Vertex 2 pointer |

## Key Observations

### Memory Allocation
- Uses custom allocator at `OID__AllocObject(size, type, filename, line)` for tracking
- Type 1 = general allocation, Type 0x24/0x46/0x74 = specific pools

### Coordinate System
- Z-coordinate is negated during load (`-z`) - indicates right-hand to left-hand conversion
- Color bytes are swapped (BGRA to ARGB conversion)

### Mesh Types
- Type 1: Static mesh (simple vertex loading)
- Type 3: Skinned mesh (includes bone weights and indices)

### Polygon Optimization
- `OptimizePolygons` removes vertices with similar normals (threshold 0.2-0.3)
- Removes degenerate triangles (where two vertices share the same index)
- Reports "Part %s removed %d of %d verts" and "Removed %d of %d polys"

### String References Found
- `"boss_fenrir.msh"` - Used in CreatePolyBucket for testing
- `"tempbuilding3.msh"` - Secondary test mesh
- `"Ignoring mesh '%s' for poly bucket"` - Debug message
- `"Merging %s into %s"` - Merge operation debug
- `"Got %d bones"` - Bone loading debug
- `"Meshes/%s/Part/%d/DVertices"` - Memory tracking label
- `"Meshes/%s/Part/%d/PVertices"` - Memory tracking label
- `"Meshes/%s/Part/%d/Triangles"` - Memory tracking label
- `"CORE"` / `"x1"` - Buggy optimize-state tags used by strict/merge gate helpers (`0x00495030` / `0x00495090`)
- Barrel/spinner optimization filters - Wave436 corrected `0x0049f600` and `0x0049f670`; the first returns false for protected names and the second returns true when any child name matches the protected token set. Both feed `CMeshPart__CanOptimizePart_Strict` / `CMeshPart__CanMergeInOptimizePass` callers.
- Wave458 hardened `CMeshPart__CanOptimizePart_Strict` and `CMeshPart__CanMergeInOptimizePass` signatures/comments after fresh `CMesh__OptimizeParts` xref read-back; runtime optimization effects and concrete layouts remain open.

### Bone Weight System
- Up to 3 bones can influence each vertex (stored in mBoneSlots)
- Weights are normalized to sum to 1.0
- Uses 1/3 subtraction trick to find top 3 contributing bones

---
*Discovered via Phase 1 xref analysis (Dec 2025); updated with Wave436 barrel/spinner optimization-token evidence and Wave443/Wave444/Wave447/Wave448/Wave449/Wave452/Wave458 `CMeshPart` read-back evidence (2026-05-16).*
