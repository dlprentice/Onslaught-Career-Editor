# mesh.cpp Function Mappings

Wave1216 (`wave1216-render-resource-texture-hud-tail-current-risk-review`) re-read `CPDMesh__dtor_base` as part of the mesh/render-resource tail current-risk review. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified`. Runtime mesh/resource behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

> Functions from mesh.cpp mapped to BEA.exe binary
> Debug path: [maintainer-local-source-export-root]\mesh.cpp (at 0x0062f8e8)

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

- **Functions Mapped:** 36 tracked entries in this note, including the Wave 366 deserializer helper updates, Wave 443/444/445 CMesh hardening, the Wave449 random-vertex companion correction, the Wave458 optimization-constraint predicate, the Wave811 LegMotion animation predicate correction, the Wave813 CMesh usage clearout/resource-lifetime pass, the Wave814 mesh segment tail corrections, the Wave815 CMesh/MeshPart tail corrections, and the Wave816 mesh animation tail correction
- **Status:** NEW (Dec 2025)
- **Classes:** CMesh

Wave1099 CMesh resource registry review (`cmesh-resource-registry-review-wave1099`) re-read eighteen saved CEngine/CMesh resource registry, load, deserialize, cache, texture-binding, optimization, and release rows with no mutation. Fresh read-only exports verified `18` metadata rows, `18` tag rows, `63` xref rows, `6524` instruction rows, and `18` decompile rows. The slice ties `0x00449dc0 CEngine__LoadAllNamedMeshes`, `0x004a5020 CMesh__Init`, `0x004a50b0 CMesh__FreeResourcesAndUnlink`, `0x004a5200 CMesh__InitStatic`, `0x004a52d0 CMesh__ClearOut`, `0x004a5430 CMesh__FreeUnusedAndReportLeaks`, `0x004a5970 CMesh__LoadByNameWithStatus`, `0x004a5b70 CMesh__Load`, `0x004aa6e0 CMesh__FindOrCreate`, `0x004aab90 CMesh__Deserialize`, and `0x004adf90 CMesh__ReleaseEmbeddedResources` into one static mesh registry/load/release map. Core static anchors: global mesh list `DAT_00704ad8`, default embedded resource `DAT_00704adc`, leak/report counter `DAT_00704ae0`, archive flag `DAT_00704ae4`, optimization counters `DAT_00704af0` / `DAT_00704af4`, `data\Meshes`, and `data\resources\meshes\m_%s.aya`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-193549_post_wave1099_cmesh_resource_registry_review_verified`. Runtime mesh/resource/texture/VBuf/render behavior, exact layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1099; cmesh-resource-registry-review-wave1099; 0x00449dc0 CEngine__LoadAllNamedMeshes; 0x004a5020 CMesh__Init; 0x004a50b0 CMesh__FreeResourcesAndUnlink; 0x004a5200 CMesh__InitStatic; 0x004a52d0 CMesh__ClearOut; 0x004a5430 CMesh__FreeUnusedAndReportLeaks; 0x004a5970 CMesh__LoadByNameWithStatus; 0x004a5b70 CMesh__Load; 0x004aa6e0 CMesh__FindOrCreate; 0x004aab90 CMesh__Deserialize; 0x004adf90 CMesh__ReleaseEmbeddedResources; DAT_00704ad8; DAT_00704adc; data\Meshes; data\resources\meshes\m_%s.aya; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-193549_post_wave1099_cmesh_resource_registry_review_verified; read-only review.

Wave1159 current-risk update: Wave1159 (`wave1159-cmeshpart-name-pose-current-risk-review`) accounts for `12 CMeshPart name/load/pose current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, no runtime-file mutation, and Codex read-only consults used for candidate/accounting and system-map sanity while Codex root made the final judgment. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `497/1179 = 42.15%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 682; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `33 xref rows` and `1790 instruction rows`. Static anchors include `CMeshPart__LoadOldStyle_VersionA`, `CMeshPart__RebuildPerVertexNormalsAndTangents`, `CMeshPart__PopulatePoseCacheRecursive`, `CMeshPart__EvaluatePoseTransformForFrame`, and `CMesh__FindPartByNameI`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-004711_post_wave1159_cmeshpart_name_pose_current_risk_review_verified`. Runtime mesh loading, pose-cache, render/collision behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1159; wave1159-cmeshpart-name-pose-current-risk-review; 497/1179 = 42.15%; 12 CMeshPart name/load/pose current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 682; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 33 xref rows; 1790 instruction rows; CMeshPart__LoadOldStyle_VersionA; CMeshPart__RebuildPerVertexNormalsAndTangents; CMeshPart__PopulatePoseCacheRecursive; CMeshPart__EvaluatePoseTransformForFrame; CMesh__FindPartByNameI; [maintainer-local-ghidra-backup-root]\BEA_20260606-004711_post_wave1159_cmeshpart_name_pose_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave905 static review (`mesh-motion-world-particle-static-review-wave905`) records a `static-coherent mesh/motion/world/particle core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only): `506` rows across `41` families, including `CMeshPart` `54`, `CMesh` `40`, `CWorld` `38`, `CWorldPhysicsManager` `32`, `CThing` `28`, `CParticleManager` `23`, and `CMeshCollisionVolume` `21`; anchors include `CThing__InitRenderThingFromInitMeshName`, `CMesh__LoadByNameWithStatus`, `CMeshPart__PopulatePoseCacheRecursive`, `CWorld__InitOccupancyBitplanes`, `CWorldPhysicsManager__CreateThingByType`, `CParticleManager__Update`, `CParticleSet__LoadFromArchive`, and `CParticleDescriptor__Load`; mesh bridge counts include `213/213` loose meshes, `139/139` embedded meshes, and `352/352` model material/texture-binding rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`.

Wave939 (`meshcollisionvolume-swept-sphere-query-review-wave939`) is documented in [`MeshCollisionVolume.cpp`](../MeshCollisionVolume.cpp/_index.md) because the reviewed cluster sits on the mesh collision-volume path. Probe anchor: Wave939; `0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50`; `0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0`; `0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds`; `0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart`; `0x004acf30 CMeshCollisionVolume__ResolveContactNormalAndPlane`; `0x004ad600 CMeshCollisionVolume__SetPartBounds`; `0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`; `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord`; comment-only mutation; `24-entry direction-pointer table as 8 triangle tests`; `173/1408 = 12.29%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-024426_post_wave939_meshcollisionvolume_swept_sphere_query_review_verified`. Runtime collision correctness and rebuild parity remain separate proof.

Wave940 (`line-cylinder-dispatch-review-wave940`) is documented in [`cylinder.cpp`](../cylinder.cpp/_index.md) because the reviewed cluster centers on CLine/CCylinder/CSphere primitive dispatch. Mesh context remained relevant through `0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`, `0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism`, `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord`, and `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830`, while primary anchors were `0x004059a0 CCylinder__VFunc_01_004059a0`, `0x004098c0 CLine__VFunc_01_004098c0`, `0x004098e0 CLine__ctor_copy`, `0x00426340 CLine__ScalarDeletingDestructor_00426340`, `0x00426360 CLine__SetBaseVtable_00426360`, `0x00426320 CSphere__VFunc_01_00426320`, and vtables `0x005d88cc`, `0x005d8bfc`, and `0x005d95e8`. Wave940 was a read-only review with no Ghidra mutation. Wave911 focused re-audit progress after Wave940 is `178/1408 = 12.64%`; static export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-030741_post_wave940_line_cylinder_dispatch_review_verified`. Runtime primitive dispatch behavior, runtime collision/trace behavior, exact primitive layouts, exact source-body identity, and rebuild parity remain separate proof.

## Wave816 Mesh Animation Tail (2026-05-24)

Wave816 mesh animation tail (`mesh-animation-tail-wave816`, `wave816-readback-verified`) saved comments/tags for `0x004b0cd0 CMesh__SelectModeSpecificPtr`, `0x004b0d00 CMeshPart__InterpolateSegmentTransform`, and `0x004b0fb0 CMCMech__BuildInterpolatedPoseAndAnchor`. The pass corrected two stale locked no-argument signatures to observed `__thiscall` stack-cleanup forms, made no renames, no function-boundary changes, and no executable-byte changes.

Static read-back evidence:

| Address | Evidence |
| --- | --- |
| `0x004b0cd0 CMesh__SelectModeSpecificPtr` | Reads mode field `+0x8c`; modes `1` and `3` return `this`, mode `6` returns alternate pointer `+0x124`, otherwise returns null. Post-read-back exports show 15 call xrefs. |
| `0x004b0d00 CMeshPart__InterpolateSegmentTransform` | Included here as the immediate mesh-part animation companion: sole direct callsite `0x004b17fc` pushes five stack arguments, sets `ECX` to the part, and the callee exits with `RET 0x14`. |
| `0x004b0fb0 CMCMech__BuildInterpolatedPoseAndAnchor` | Included here because this mesh animation tail calls through `CMeshPart__InterpolateSegmentTransform`; representative callsites push nine stack dwords and the body exits with `RET 0x24`. Evidence includes pose cache globals `DAT_00704cf0`/`DAT_00704d20`, anchor globals `DAT_00704cd0`/`DAT_00704ce0`, and parent part `+0x98`. |

Queue telemetry after Wave816 is 6098 total, 5602 commented, 496 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5602/6098 = 91.87%`, strict proxy `5602/6098 = 91.87%`, and next raw commentless row `0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-151844_post_wave816_mesh_animation_tail_verified`. Exact concrete CMesh/CMeshPart/CMCMech/controller layouts, exact source-body identity, runtime animation/render/collision behavior, BEA patching, and rebuild parity remain deferred.

## Wave815 MeshPart Tail (2026-05-24)

Wave815 meshpart tail (`meshpart-tail-wave815`, `wave815-readback-verified`) saved comments/tags for `0x004adf80 CMesh__ClearField08`, corrected `0x004ae640 CMeshPart__FreeOwnedResourcePointers_004ae640` to `0x004ae640 CMeshPart__FreeOwnedResourcePointers`, and corrected the old-style loader signatures for `0x004aede0 CMeshPart__LoadOldStyle_VersionA` and `0x004af110 CMeshPart__LoadOldStyle_VersionB_WithExtraBlock`. The pass made one rename, corrected two stale locked no-argument signatures to `__thiscall` plus five stack arguments, made no function-boundary changes, and made no executable-byte changes.

Static read-back evidence:

| Address | Evidence |
| --- | --- |
| `0x004adf80 CMesh__ClearField08` | Clears field `+0x08` on the 0x24-byte CMesh embedded resource/material record. `CMesh__InitStatic` calls it after allocation, while `CMesh__Load` and `CMesh__Deserialize` pass it to vector-constructor setup paired with `CMesh__ReleaseEmbeddedResources`. |
| `0x004ae640 CMeshPart__FreeOwnedResourcePointers` | Shared CMeshPart resource-free body reached by `0x004a51f0 CMeshPart__FreeResources` and `CMeshPart__CreatePolyBucket`; documented here because `CMesh__FreeResourcesAndUnlink` owns the tail-entry call chain. |
| `0x004aede0 CMeshPart__LoadOldStyle_VersionA` | `CMesh__Load` callsite `0x004a8f05` sets `ECX=ESI` and pushes five stack arguments; the old loader ends with `RET 0x14` and calls `CMeshPart__RebuildPerVertexNormalsAndTangents(this, 1)`. |
| `0x004af110 CMeshPart__LoadOldStyle_VersionB_WithExtraBlock` | `CMesh__Load` callsite `0x004a8f49` uses the same five-stack-argument ABI, and epilogue `0x004af462` uses `RET 0x14`; the VersionB body consumes an extra per-count 4-byte block tied to part offset `+0xb8`. |

Queue telemetry after Wave815 is 6098 total, 5599 commented, 499 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5599/6098 = 91.82%`, strict proxy `5599/6098 = 91.82%`, and next raw commentless row `0x004b0cd0 CMesh__SelectModeSpecificPtr`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-144421_post_wave815_meshpart_tail_verified`. Exact concrete CMesh/CMeshPart layouts, exact old mesh-format schema, exact source-body identity, extra-block field meaning, runtime mesh loading/render/collision behavior, BEA patching, and rebuild parity remain deferred.

## Wave814 Mesh Segment Tail (2026-05-24)

Wave814 mesh segment tail (`mesh-segment-tail-wave814`, `wave814-readback-verified`) saved names/signatures/comments/tags for four adjacent CMesh/CRTMesh/destructible helper rows: `0x004aa4e0 CMesh__SumChainedField1C`, `0x004aa500 CMesh__GetChainedRecordNameAndIdByIndex`, `0x004aa6b0 CMesh__GetNameOrUnknown`, and `0x004aa8a0 CMesh__FindPartByNameI`. The pass corrected stale owners and stale phantom parameters, made four renames, made no function-boundary changes, and made no executable-byte changes.

Wave914 re-reviewed those four Wave814 rows plus `0x004aa680 CMesh__FindEntryByPartId` and `0x004aa820 CMesh__FindPartField40ByNameAndOwner` with fresh metadata, tag, instruction, and decompile exports. The saved names/signatures/comments remain appropriate for the current evidence; no Ghidra mutation was performed.

Static read-back evidence:

| Address | Evidence |
| --- | --- |
| `0x004aa4e0 CMesh__SumChainedField1C` | Recursively follows the CMesh/resource chain pointer at `this+0x08` and sums each node's field `+0x1c`; `CRTMesh__Init` calls it on the mesh/resource pointer at `this+0x14`. |
| `0x004aa500 CMesh__GetChainedRecordNameAndIdByIndex` | Resolves flat record indexes across the same chain, copies the selected 0x150-byte record name at `+0x4c`, writes record field `+0x14c`, and falls back to empty string `0x00662b2c` plus `-1`; `RET 0xc` removes the stale `unused_ctx`. |
| `0x004aa6b0 CMesh__GetNameOrUnknown` | Scans global mesh list `DAT_00704ad8` by next-link `+0x158`, returns mesh name `+0x24`, or returns `0x0062f8d4` (`unknown mesh name`); caller read-back proves the old controller-specific one-stack-argument signature was stale. |
| `0x004aa8a0 CMesh__FindPartByNameI` | Scans part pointer table `this+0x160` for count `this+0x15c`, compares part names at `part+0xdc` with `stricmp`, and returns the matching part pointer or null; `RET 0x4` removes the stale `unused_ctx`. |

Caller read-back ties the corrected helpers to `CRTMesh__Init`, destructible-segment name dispatch, `CHud__RenderTargetIndicatorOverlay`, shared grounded-unit init, and `CMeshPart__CreatePolyBucket`. Queue telemetry after Wave814 is 6098 total, 5595 commented, 503 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5595/6098 = 91.75%`, strict proxy `5595/6098 = 91.75%`, and next raw commentless row `0x004adf80 CMesh__ClearField08`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-141602_post_wave814_mesh_segment_tail_verified`. Exact concrete CMesh/CMeshPart/CRTMesh/destructible layouts, exact source-body identity, runtime mesh/destructible/RTMesh behavior, BEA patching, and rebuild parity remain deferred.

## Wave811 CMesh LegMotion Animation (2026-05-24)

Wave811 CMesh LegMotion animation (`cmesh-legmotion-animation-wave811`, `wave811-readback-verified`) corrected stale `0x0049c2d0 CMeshPart__HasAnimationToken_623074` to `0x0049c2d0 CMesh__HasLegMotionAnimation` and saved `bool __cdecl CMesh__HasLegMotionAnimation(void * mesh)`. Static instruction evidence loads `mesh` from `ESP+4`, pushes string token `0x00623074` (`LegMotion`), calls `CMesh__FindAnimationIndexByName`, compares the returned index with `-1`, and returns the boolean result. Caller read-back explains the owner correction: `CMeshPart__CanOptimizePart_Strict` and `CMeshPart__CanMergeInOptimizePass` pass `part+0x128`, while `CMesh__HasSpecialOptimizationConstraints` passes `mesh` directly.

Read-back verified 1 metadata row, 1 tag row, 9 xref rows, 181 instruction rows, 1 decompile row, 4 caller metadata rows, and 4 caller decompile rows. Queue telemetry after Wave811 is 6098 total, 5586 commented, 512 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5586/6098 = 91.60%`, strict proxy `5586/6098 = 91.60%`, and next raw commentless row `0x004a25c0 CLTShell__ValidateAndRollHeapDeltas`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-125806_post_wave811_cmesh_legmotion_animation_verified`. Exact `part+0x128` field meaning, concrete `CMesh`/`CMeshPart` layouts, source identity, runtime mesh optimization behavior, runtime animation behavior, BEA patching, and rebuild parity remain deferred.

## Wave813 CMesh usage clearout (2026-05-24)

Wave813 CMesh usage clearout (`cmesh-usage-clearout-wave813`, `wave813-readback-verified`) saved signatures/comments/tags for four adjacent static CMesh resource-lifetime helpers: `0x004a52b0 CMesh__ClearAllUsageMarkers`, `0x004a52d0 CMesh__ClearOut`, `0x004a53f0 CMesh__StatusLoadingMeshResources`, and `0x004a5430 CMesh__FreeUnusedAndReportLeaks`. The pass hardened four `void __cdecl ... (void)` signatures and made no renames, function-boundary changes, or executable-byte changes.

Static evidence ties the tranche to global mesh list `DAT_00704ad8`, next-link `+0x158`, usage/ref marker `+0x170`, default embedded resource `DAT_00704adc`, leak/report counter `DAT_00704ae0`, leaked mesh format string `0x0062f938`, loading-status string `0x0062f9a0`, global console/status object `DAT_00663498`, CLTShell shutdown callsites `0x004f0166`, `0x004f01bf`, and `0x004f01c4`, frontend/game loading callsites `0x00468809` and `0x0046cdba`, frontend release callsite `0x0046928d`, and raw callsite `0x0046ca13` that Ghidra does not currently attach to a function.

Read-back verified 4 metadata rows, 4 tag rows, 8 xref rows, 484 instruction rows, 4 decompile rows, 4 caller metadata rows, 4 caller decompile rows, and 147 callsite instruction rows. Queue telemetry after Wave813 is 6098 total, 5591 commented, 507 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5591/6098 = 91.69%`, strict proxy `5591/6098 = 91.69%`, and next raw commentless row `0x004aa4e0 CRTMesh__SumSubtreeField1C`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-134919_post_wave813_cmesh_usage_clearout_verified`. Exact `CMesh` list/resource layout, runtime shutdown/loading/end-of-level leak behavior, BEA patching, and rebuild parity remain deferred.

## Wave796 Final Signature Debt (2026-05-24)

Wave796 signature debt (`signature-debt-wave796`, `wave796-readback-verified`) saved the final CNamedMesh param-name hardening row: `0x004bbcd0 CNamedMesh__VFunc_09_004bbcd0` as `void __thiscall CNamedMesh__VFunc_09_004bbcd0(void * this, void * init_record, void * unused_slot_arg)`. The pass made no renames, no function-boundary changes, and no executable-byte changes. Queue telemetry after the pass is 6098 total, 5544 commented, 554 commentless, 0 exact-undefined signatures, 0 param_N signatures, and strict clean-signature proxy `5544/6098 = 90.92%`; raw commentless head remains `0x0042f220 CSPtrSet__Clear`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-050846_post_wave796_final_param_signature_debt_verified`. Hidden register/thiscall storage, exact source identity, runtime behavior, BEA patching, and rebuild parity remain deferred.

## Wave758 mesh.cpp Unwind Continuation (2026-05-23)

Wave758 static read-back (`unwind-continuation-wave758`, `wave758-readback-verified`) saved comments/tags/signatures for the next mesh.cpp-adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d38bc Unwind@005d38bc` through `0x005d3960 Unwind@005d3960`. Evidence includes mesh.cpp debug path `0x0062f8e8`, DATA scope-table xrefs `0x0061c55c` through `0x0061c5c4`, four `OID__FreeObject_Callback` allocation cleanup rows, and two `CLine__SetBaseVtable_00426360` vtable-restore callbacks. Exact anchors include `0x005d3940 Unwind@005d3940`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-123821_post_wave758_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

Representative Wave758 rows:

| Address | Evidence |
| --- | --- |
| 0x005d38bc | DATA xref `0x0061c55c`; `OID__FreeObject_Callback(*(EBP-0x34c))` with line token `0x80` and allocation/type value `0x9cc`. |
| 0x005d38db | DATA xref `0x0061c564`; `OID__FreeObject_Callback(*(EBP-0x350))` with line token `0x01` and allocation/type value `0x9fc`. |
| 0x005d38f7 | DATA xref `0x0061c56c`; `OID__FreeObject_Callback(*(EBP-0x34c))` with allocation/type value `0xa05`. |
| 0x005d3913 | DATA xref `0x0061c574`; `OID__FreeObject_Callback(*(EBP-0x34c))` with allocation/type value `0xa58`. |
| 0x005d3940 | DATA xref `0x0061c59c`; `CLine__SetBaseVtable_00426360(EBP-0x28)`. |
| 0x005d3960 | DATA xref `0x0061c5c4`; loads `ECX` from `*(EBP-0x10)` and jumps to `CLine__SetBaseVtable_00426360`. |

## Wave757 mesh.cpp Unwind Continuation (2026-05-23)

Wave757 static read-back (`unwind-continuation-wave757`, `wave757-readback-verified`) saved comments/tags/signatures for mesh.cpp-adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d36f0 Unwind@005d36f0` through `0x005d38a0 Unwind@005d38a0`. Evidence includes mesh.cpp debug path `0x0062f8e8`, DATA scope-table xrefs `0x0061c46c` through `0x0061c554`, thirteen `OID__FreeObject_Callback` allocation cleanup rows, and `0x005d3720 Unwind@005d3720` calling `CDXMemBuffer__dtor_base(EBP-0x340)`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-120201_post_wave757_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

Representative Wave757 rows:

| Address | Evidence |
| --- | --- |
| 0x005d36f0 | DATA xref `0x0061c46c`; `OID__FreeObject_Callback(*(EBP-0x10))` with allocation/type value `0x91`. |
| 0x005d3720 | DATA xref `0x0061c494`; `CDXMemBuffer__dtor_base(EBP-0x340)`. |
| 0x005d3740 | DATA xref `0x0061c4dc`; `OID__FreeObject_Callback(*(EBP-0x82c))` with allocation/type value `0x349`. |
| 0x005d37b0 | DATA xref `0x0061c4fc`; `OID__FreeObject_Callback(*(EBP-0x794))` with allocation/type value `0x584`. |
| 0x005d3820 | DATA xref `0x0061c4cc`; `OID__FreeObject_Callback(*(EBP-0x810))` with allocation/type value `0x28d`. |
| 0x005d38a0 | DATA xref `0x0061c554`; `OID__FreeObject_Callback(*(EBP-0x34c))` with allocation/type value `0x982`. |

## Function List

| Address | Name | Status | Description |
|---------|------|--------|-------------|
| 0x0044c1c0 | CMesh__DeserializeTripletDwords | NAMED | Wave 366 helper: reads three dwords from a CDXMemBuffer-style stream into `this+0x00/+0x04/+0x08` |
| 0x0044c210 | CMesh__DeserializeNineDwords | NAMED | Wave 366 helper: reads nine dwords from a CDXMemBuffer-style stream through `this+0x28` |
| 0x004a5020 | CMesh__Init | NAMED | Initialize mesh instance, allocate resources, link to global mesh list |
| 0x004a50b0 | CMesh__FreeResourcesAndUnlink | NAMED | Unlinks a mesh from the global list and frees owned mesh/material/part resources |
| 0x004a5200 | CMesh__InitStatic | NAMED | Static initialization, loads default texture (meshtex\default.tga) |
| 0x004a5500 | CMesh__MapStateNameToId | NAMED | Maps mesh animation state-name tokens to a state id field |
| 0x004a5670 | CMesh__OptimizeTextures | NAMED | Deduplicates material/texture entries and rewrites part material indices |
| 0x004a5970 | CMesh__LoadByNameWithStatus | NAMED | Builds a `data\Meshes\` path, opens a mem-buffer, and dispatches to `CMesh__Load` |
| 0x004a5b70 | CMesh__Load | NAMED | Large mesh loading function (~18KB), handles file format parsing and validation |
| 0x0049c2d0 | CMesh__HasLegMotionAnimation | NAMED | Wave811 CMesh LegMotion animation predicate; looks up `LegMotion` (`0x00623074`) through `CMesh__FindAnimationIndexByName`; CMeshPart callers pass `part+0x128` |
| 0x004aa4e0 | CMesh__SumChainedField1C | NAMED | Wave814 chain helper; recursively sums field `+0x1c` across the `this+0x08` CMesh/resource chain |
| 0x004aa500 | CMesh__GetChainedRecordNameAndIdByIndex | NAMED | Wave814 chain helper; resolves flat chained record indexes and copies record name/id with empty-string fallback `0x00662b2c` |
| 0x004aa6b0 | CMesh__GetNameOrUnknown | NAMED | Wave814 owner/signature correction; returns CMesh name from global list `DAT_00704ad8` or `0x0062f8d4` (`unknown mesh name`) |
| 0x004aa6e0 | CMesh__FindOrCreate | NAMED | Find existing mesh by name or create new one, increments refcount |
| 0x004aa8a0 | CMesh__FindPartByNameI | NAMED | Wave814 owner/signature correction; searches the part pointer table by case-insensitive part name |
| 0x004aab90 | CMesh__Deserialize | NAMED | Deserialize mesh from chunk-reader/resource streams, including chained mesh and AYA resource handling |
| 0x004ab360 | CMesh__OptimizeParts | NAMED | Optimize mesh parts by merging compatible static parts and rewriting child/material lists |
| 0x004bb210 | CMesh__HasSpecialOptimizationConstraints | NAMED | Mesh-wide protected animation/name constraint guard called by `CMesh__OptimizeParts` |
| 0x004a52b0 | CMesh__ClearAllUsageMarkers | NAMED | Clears usage-marker flags across mesh usage arrays/tables |
| 0x004a5430 | CMesh__FreeUnusedAndReportLeaks | NAMED | Frees currently unused resources and emits leak/report diagnostics |
| 0x004adf80 | CMesh__ClearField08 | NAMED | Wave815 helper clears field `+0x08` on a 0x24-byte CMesh embedded resource/material record before constructor/default setup |
| 0x004aa410 | CMesh__FindTextureByNameSuffixHint | NAMED | Resolves texture entry using suffix-hint matching |
| 0x004aa5a0 | CMesh__GetPartField40ByFlatIndex | NAMED | Returns part field `+0x40` via flattened part index lookup |
| 0x004aa5e0 | CMesh__FindEntryByInclusiveRangeTable | NAMED | Resolves entry by inclusive range-table traversal |
| 0x004aa630 | CMesh__FindAnimationIndexByName | NAMED | Finds an animation/state record by name and returns its record `+0x10` id/index |
| 0x004aa680 | CMesh__FindEntryByPartId | NAMED | Finds a 0x24-byte mesh entry by part/id field at record `+0x10` |
| 0x004aa7e0 | CMesh__FindEntryValueByTypeId | NAMED | Resolves typed entry value from mesh lookup tables |
| 0x004aa820 | CMesh__FindPartField40ByNameAndOwner | NAMED | Finds a part by name and owner pointer, returning the part field at `+0x40` |
| 0x004aa900 | CMesh__CreatePolyBucketsForAllParts | NAMED | Builds polygon bucket structures across all mesh parts |
| 0x004aa940 | CMesh__GetRandomVertexWeightedByPartArea | NAMED | Selects a static mesh-part vertex using area-weighted/random polybucket sampling |
| 0x004b25d0 | CMesh__GetRandomVertexFromPolyBucket | NAMED | Writes a random polybucket triangle vertex into `out_vec4` after choosing one of the triangle's three short-coordinate vertices |
| 0x004b0cd0 | CMesh__SelectModeSpecificPtr | NAMED | Wave816 mode selector: mode `1`/`3` returns `this`, mode `6` returns `this+0x124`, otherwise null |
| 0x004ab330 | CMesh__FindByRuntimeId | NAMED | Finds mesh entry by runtime id/key |
| 0x004adf90 | CMesh__ReleaseEmbeddedResources | NAMED | Releases a 0x24-byte mesh material/texture resource record and associated counters |
| 0x004ae080 | CMesh__InitSingleVertexPartDefaults | NAMED | Initializes a single-vertex material/part record with default vertex values |
| 0x004ae0d0 | CMesh__InitPartVBufTextureFormats | NAMED | Initializes VBuf texture resources and observed VB/IB format constants |

## Function Details

### Wave 366 Deserializer Helpers (0x0044c1c0, 0x0044c210)

Fresh metadata, decompile, instruction, and callsite read-back on 2026-05-13 hardened two lower-address CMesh helper signatures that are called from mesh deserialization context:

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x0044c1c0` | `void __thiscall CMesh__DeserializeTripletDwords(void * this, void * mem_buffer)` | One `mem_buffer` stack argument, three `CDXMemBuffer__Read` dword reads, writes to `this+0x00/+0x04/+0x08`, and `ret 0x4`. |
| `0x0044c210` | `void __thiscall CMesh__DeserializeNineDwords(void * this, void * mem_buffer)` | One `mem_buffer` stack argument, nine `CDXMemBuffer__Read` dword reads, writes through `this+0x28`, and `ret 0x4`. |

These are saved static Ghidra facts only. The concrete destination structure/type names and exact source method identities remain open.

### Wave 443 CMesh Head Hardening (0x004a5020..0x004a5b70)

Fresh metadata, decompile, xref, instruction, and tag read-back on 2026-05-16 hardened the queue-head mesh functions. `ApplyCMeshWave443.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_cmesh_wave443_probe.py --check` passed against eight post-apply decompile exports.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004a5020` | `void * __thiscall CMesh__Init(void * this)` | ECX receiver, zeroes mesh fields, sets `+0x164` to `0.5f`, allocates the `+0x150` buffer, and links through `DAT_00704ad8`. |
| `0x004a50b0` | `void __thiscall CMesh__FreeResourcesAndUnlink(void * this)` | ECX receiver, walks/unlinks `DAT_00704ad8`, frees material arrays, part pointers, emitters/index/texture arrays, and decrements chained mesh refcount `+0x170`. |
| `0x004a5200` | `int __cdecl CMesh__InitStatic(void)` | No arguments, releases old `DAT_00704adc`, allocates a 0x24-byte default entry, initializes defaults, resolves `meshtex\default.tga`, and returns 1. |
| `0x004a5500` | `void __stdcall CMesh__MapStateNameToId(char * state_name, void * state_record)` | `ret 0x8`, compares fixed state tokens such as `STAND`, `SHOOT`, `HOVER`, and `SHOOTWALK`, then writes the id at `state_record+0x10`. |
| `0x004a5670` | `void __thiscall CMesh__OptimizeTextures(void * this)` | ECX receiver, scans 0x24-byte material entries for duplicate texture/float payloads and rewrites CMeshPart dynamic-vertex material slots. |
| `0x004a5970` | `int __thiscall CMesh__LoadByNameWithStatus(void * this, char * mesh_name, void * load_context)` | `ret 0x8`, logs/statuses the mesh name, builds a `data\Meshes\` path from the basename, copies the basename to `this+0x24`, opens a mem-buffer, and calls `CMesh__Load`. |
| `0x004a5b70` | `int __thiscall CMesh__Load(void * this, void * mem_buffer, void * load_context)` | Main stream loader; validates `DAT_00704a90` and version tokens, allocates material/part tables, supports old/new CMeshPart paths, maps state names, handles chained mesh loads, then optimizes/link/bounds/cache-refreshes parts. |

The companion `0x004a51f0` `CMeshPart__FreeResources` entry is documented in [../MeshPart.cpp/_index.md](../MeshPart.cpp/_index.md). These are saved static Ghidra facts only; concrete field names/types, runtime asset behavior, exact source-body identity, and rebuild parity remain open.

### Wave 444 CMesh Tail Lookup Hardening (0x004aa410..0x004aa940)

Fresh metadata, decompile, xref, instruction, and tag read-back on 2026-05-16 hardened the next CMesh queue-head/tail lookup cluster. `ApplyCMeshWave444.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_cmesh_wave444_probe.py --check` passed against eleven post-apply metadata/decompile/tag/xref exports. Three stale or generic names were corrected to mesh-level owners: `CMesh__FindAnimationIndexByName`, `CMesh__FindEntryByPartId`, and `CMesh__FindPartField40ByNameAndOwner`.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004aa410` | `void * __cdecl CMesh__FindTextureByNameSuffixHint(void * texture_record)` | Validates the texture name pointer at record `+0x08`, warns on null, and dispatches `CTexture__FindTexture` with suffix-hint modes `4`, `2`, and `1`. |
| `0x004aa5a0` | `int __thiscall CMesh__GetPartField40ByFlatIndex(void * this, int flat_part_index)` | Chained part-table lookup subtracts count `+0x1c`, follows the `+0x08` chain, and returns the selected part field `+0x40` or `0`; `ret 0x4` confirms one stack argument. |
| `0x004aa5e0` | `int __thiscall CMesh__FindEntryByInclusiveRangeTable(void * this, int lookup_value)` | Scans 12-byte records at `+0x10` for inclusive start/end range fields at `+0x04/+0x08`, follows the `+0x08` chain, and returns `0` on exhaustion. |
| `0x004aa630` | `int __thiscall CMesh__FindAnimationIndexByName(void * this, char * animation_name)` | Scans `+0x14` animation count across 0x24-byte records at `+0x18`, uses `stricmp`, returns record `+0x10` on match or `-1` on miss, and is called by animation-bearing mesh-part helpers. |
| `0x004aa680` | `void * __thiscall CMesh__FindEntryByPartId(void * this, int part_id)` | Generic mesh 0x24-byte entry lookup, not CMCMech-specific; returns first record whose `+0x10` part/id matches, with CMCMech/CMCBuggy/cutscene-prep callers. |
| `0x004aa6e0` | `void * __cdecl CMesh__FindOrCreate(char * mesh_name, void * load_context)` | Scans `DAT_00704ad8` / `g_pMeshList` by `mesh_name` at `+0x24`, increments refcount `+0x170` on hit, otherwise allocates 0x174 bytes, initializes/loads, and tears down on failure. |
| `0x004aa7e0` | `float __thiscall CMesh__FindEntryValueByTypeId(void * this, int type_id, int * out_index)` | Scans records for type id at record `+0x10`, writes the matching index to `out_index`, returns float field `+0x20`, and on miss writes `-1` plus default float `0x005d856c`. |
| `0x004aa820` | `int __thiscall CMesh__FindPartField40ByNameAndOwner(void * this, char * part_name, void * owner_part)` | Chained mesh-part lookup, not CMCMech-specific; matches name at record `+0x4c` and owner at `+0x14c`, returning field `+0x40` or `0`. |
| `0x004aa900` | `void __thiscall CMesh__CreatePolyBucketsForAllParts(void * this)` | Iterates the part pointer table at `+0x160` for count `+0x15c` and calls `CMeshPart__CreatePolyBucket`; ECX receiver and no stack cleanup indicate thiscall with no stack args. |
| `0x004aa940` | `void * __thiscall CMesh__GetRandomVertexWeightedByPartArea(void * this, void * out_vec3, void * out_part)` | Selects a static part and returns `out_vec3` after `CMesh__GetRandomVertexFromPolyBucket(this, out_vec3)`; large meshes build an area-weighted candidate list up to 150 and sample with `Random__NextLCGAbs`, while small meshes try up to 15 random static parts. |

The companion `0x004aa3f0` `CMeshPart__CopyPrimaryAxesToOutVec3Triplet` entry is documented in [../MeshPart.cpp/_index.md](../MeshPart.cpp/_index.md). These are saved static Ghidra facts only; runtime mesh loading/render behavior, concrete `CMesh`/`CMeshPart` layouts, exact field names/types, exact source-body identity, and rebuild parity remain open.

### Wave 449 CMesh / CMeshPart Random Vertex Companion (0x004b25d0)

Fresh metadata, decompile, xref, instruction, callsite, and tag read-back on 2026-05-16 hardened the adjacent `CMesh__GetRandomVertexFromPolyBucket` helper while Wave449 hardened the surrounding CMeshPart load/optimize tranche. `ApplyCMeshPartWave449.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_cmeshpart_wave449_probe.py --check` passed.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004b25d0` | `void __thiscall CMesh__GetRandomVertexFromPolyBucket(void * this, void * out_vec4)` | Uses polybucket field `+0x100`, calls `CPolyBucket__GetRandomTriangle`, chooses one of the triangle's three short-coordinate vertices with `Random__NextLCGAbs % 3`, scales by mesh/part field `+0x50` and `DAT_005d8618`, and offsets by origin fields `+0x40/+0x44/+0x48`. `ret 0x4` confirms the single stack output pointer and corrects the stale phantom third argument. |

These are saved static Ghidra facts only. Runtime random-vertex selection, mesh loading/rendering, concrete `CMesh`/`CMeshPart`/`CPolyBucket` layouts, exact field names/types, exact source-body identity, BEA launch behavior, game patching, and rebuild parity remain open.

### Wave 458 CMesh Optimization Constraint Predicate (0x004bb210)

Fresh metadata, decompile, xref, instruction, and tag read-back on 2026-05-16 hardened the mesh-wide optimization guard called by `CMesh__OptimizeParts`. `ApplyMeshOptimizationWave458.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_mesh_optimization_wave458_probe.py --check` passed.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004bb210` | `bool __cdecl CMesh__HasSpecialOptimizationConstraints(void * mesh)` | Called by `CMesh__OptimizeParts` at `0x004ab772` with the mesh pointer. The body returns true when protected animation/name constraints are present, including wheel motion, repeated `0x623074` animation-token checks, `nmidoutcyl` child names, and tentacle-bone constraints, which can prevent leaf part removal. |

The companion CMeshPart predicates `0x004bae70` and `0x004bb040` are documented in [../MeshPart.cpp/_index.md](../MeshPart.cpp/_index.md). These are saved static Ghidra facts only. Runtime mesh optimization behavior, concrete `CMesh`/`CMeshPart` layouts, exact field names/types, exact source-body identity, BEA launch behavior, game patching, and rebuild parity remain open.

### Wave 445 CMesh / MeshCollisionVolume Bridge Hardening (0x004aab90..0x004ae0d0)

Fresh metadata, decompile, xref, instruction, and tag read-back on 2026-05-16 hardened the next CMesh/MeshCollisionVolume queue-head cluster. `ApplyCMeshWave445.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_cmesh_wave445_probe.py --check` passed against nine post-apply metadata/decompile/tag/xref exports. The MeshCollisionVolume-specific entries are mirrored in [../MeshCollisionVolume.cpp/_index.md](../MeshCollisionVolume.cpp/_index.md).

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004aab90` | `void * __cdecl CMesh__Deserialize(void * primary_reader, void * resource_reader)` | Allocates a 0x174-byte CMesh, initializes it, reads mesh metadata/materials/emitters/parts from chunk-reader streams, can open `data\resources\meshes\m_%s.aya`, and recursively loads chained meshes. |
| `0x004ab330` | `void * __cdecl CMesh__FindByRuntimeId(int runtime_id)` | Scans `DAT_00704ad8` / `g_pMeshList` by mesh field `+0x154`, follows `+0x158`, and returns the matching CMesh pointer or `0`; no stack cleanup confirms cdecl. |
| `0x004ab360` | `void __thiscall CMesh__OptimizeParts(void * this)` | Adds count `+0x15c` to `DAT_00704af0`, merges compatible static parts while excluding Nexus/protected dependencies, transforms child geometry into parent space, rewrites part/material child lists, and increments `DAT_00704af4` for removed parts. |
| `0x004adf90` | `void __thiscall CMesh__ReleaseEmbeddedResources(void * this)` | Releases a 0x24-byte mesh material/resource record, freeing record `+0x0c` when count `+0x08` is nonzero, clearing resource fields, and decrementing the observed HUD/resource and CDXEngine counters. |
| `0x004ae080` | `void __thiscall CMesh__InitSingleVertexPartDefaults(void * this)` | Initializes a single-vertex record, calls `CMeshPart__SetVertexCount(1)`, writes default 1.0f values through allocated vertex arrays, sets record `+0x20`, and clears record `+0x04`. |
| `0x004ae0d0` | `void __thiscall CMesh__InitPartVBufTextureFormats(void * this)` | Resolves `CVBufTexture__GetOrCreate(record+0x00, 0)`, stores it at record `+0x04`, applies observed VB format `0x152/8/0x24/4/1`, and applies observed IB format `0x65/8/2/1`. |

These are saved static Ghidra facts only; runtime mesh loading/render/collision behavior, concrete `CMesh`/`CMeshCollisionVolume` layouts, exact field names/types, exact source-body identity, and rebuild parity remain open.

### CMesh__Init (0x004a5020)
- **Saved Signature:** `void * __thiscall CMesh__Init(void * this)`
- **Purpose:** Initialize a CMesh instance
- **Key Operations:**
  - Zeroes out mesh fields (positions, counts, pointers)
  - Sets default LOD value (0x3f000000 = 0.5f)
  - Allocates internal resource buffer (0x28 bytes)
  - Links mesh to global mesh list via DAT_00704ad8

### CMesh__FreeResourcesAndUnlink (0x004a50b0)
- **Saved Signature:** `void __thiscall CMesh__FreeResourcesAndUnlink(void * this)`
- **Purpose:** Unlink a mesh from global tracking and free owned runtime resources
- **Key Operations:**
  - Walks `DAT_00704ad8` and updates previous/next links via `this+0x158`
  - Frees material entries with `CMesh__ReleaseEmbeddedResources`
  - Calls `CMeshPart__FreeResources` for each non-null part pointer
  - Frees emitter/index/texture arrays and clears pointers
  - Decrements chained mesh refcount at `+0x170`

### CMesh__InitStatic (0x004a5200)
- **Saved Signature:** `int __cdecl CMesh__InitStatic(void)`
- **Purpose:** One-time static initialization for mesh system
- **Key Operations:**
  - Cleans up any existing default mesh data
  - Allocates new mesh texture storage
  - Loads "meshtex\default.tga" as fallback texture
- **Global State:** Uses DAT_00704adc for default mesh texture

### CMesh__MapStateNameToId (0x004a5500)
- **Saved Signature:** `void __stdcall CMesh__MapStateNameToId(char * state_name, void * state_record)`
- **Purpose:** Map mesh animation/state token strings to a small integer id
- **Key Operations:**
  - Compares state strings case-insensitively
  - Handles observed tokens including `STAND`, `SHOOT`, `SHOOT1`, `SHOOT2`, `HOVER`, and `SHOOTWALK`
  - Stores the selected id at `state_record+0x10`

### CMesh__OptimizeTextures (0x004a5670)
- **Saved Signature:** `void __thiscall CMesh__OptimizeTextures(void * this)`
- **Purpose:** Deduplicate equivalent material/texture payloads
- **Key Operations:**
  - Compares 0x24-byte material entries and referenced float payloads
  - Rewrites dynamic-vertex material indices in CMeshPart records to earlier duplicates
  - Emits the retail `OptimiseTextures` debug line

### CMesh__LoadByNameWithStatus (0x004a5970)
- **Saved Signature:** `int __thiscall CMesh__LoadByNameWithStatus(void * this, char * mesh_name, void * load_context)`
- **Purpose:** File-backed mesh load wrapper
- **Key Operations:**
  - Builds a `data\Meshes\` path from the basename of the requested mesh name
  - Copies the basename to `this+0x24`
  - Opens a `CDXMemBuffer` with file mode `0x11`
  - Calls `CMesh__Load(this, mem_buffer, load_context)` and returns its status

### CMesh__Load (0x004a5b70)
- **Saved Signature:** `int __thiscall CMesh__Load(void * this, void * mem_buffer, void * load_context)`
- **Purpose:** Main mesh loading function from file/stream
- **Size:** ~18KB of code (largest mesh function)
- **Key Features:**
  - Validates mesh file format magic numbers
  - Supports multiple mesh format versions
  - Handles mesh parts, emitters, textures, and bones
  - Contains 27 debug assertions referencing mesh.cpp
- **Note:** The 2026-05-16 Wave 443 headless export decompiled this target successfully with a 160s timeout. Earlier timeout notes are historical.

### CMesh__FindOrCreate (0x004aa6e0)
- **Saved Signature:** `void * __cdecl CMesh__FindOrCreate(char * mesh_name, void * load_context)`
- **Purpose:** Mesh resource manager - find cached or create new
- **Parameters:**
  - `mesh_name`: Mesh name string
  - `load_context`: Resource/load context
- **Key Operations:**
  - Iterates global mesh list (DAT_00704ad8) searching by name
  - If found, increments reference count at offset 0x170
  - If not found, allocates new mesh (0x174 bytes) and loads it
  - Logs warning "Mesh '%s' not found in level resource file" if not in level resources

### CMesh__Deserialize (0x004aab90)
- **Saved Signature:** `void * __cdecl CMesh__Deserialize(void * primary_reader, void * resource_reader)`
- **Purpose:** Load mesh from serialized binary data
- **Key Operations:**
  - Reads mesh name (300 char buffer)
  - Opens AYA archive from "data\resources\meshes\m_%s.aya"
  - Allocates arrays for mesh parts, emitters, materials
  - Tracks total emitter memory usage (DAT_00704ae8)
  - Supports recursive mesh loading for chained meshes
- **Debug Strings:**
  - "Skipping deserialisation of mesh %s as it is unnecessary"
  - "%dK total in emitters so far"

### CMesh__OptimizeParts (0x004ab360)
- **Saved Signature:** `void __thiscall CMesh__OptimizeParts(void * this)`
- **Purpose:** Runtime mesh optimization
- **Calling Convention:** thiscall (ECX = this)
- **Key Operations:**
  - Iterates all mesh parts looking for merge candidates
  - Calls the Wave458-hardened `CMeshPart__CanOptimizePart_Strict`, `CMeshPart__CanMergeInOptimizePass`, and `CMesh__HasSpecialOptimizationConstraints` predicates before removing or merging protected parts
  - Parts must have compatible properties (same type, single vertex buffer)
  - Transforms vertices when merging parts with different local transforms
  - Removes redundant intermediate parts
  - Tracks statistics in DAT_00704af0 (total parts) and DAT_00704af4 (removed parts)
- **Debug Strings:**
  - "Optimising mesh %s parts"
  - "Removing part %s"
  - "OptimiseParts : removed %d of %d"
  - Checks for "Nexus" parts (excluded from merging)

## CMesh Structure (Partial)

Based on function analysis:

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x00 | ptr | pMaterials | Material array pointer |
| 0x04 | int | materialCount | Number of materials |
| 0x14 | ptr | pVertices | Vertex buffer pointer |
| 0x18 | ptr | pIndices | Index buffer pointer |
| 0x1C | int | numEmitters | Emitter count |
| 0x20 | ptr | pEmitters | Emitter array pointer |
| 0x24 | char[300] | name | Mesh name string |
| 0x150 | ptr | pTextureList | Texture list pointer |
| 0x154 | int | unknown | |
| 0x158 | ptr | pNextMesh | Next mesh in global list |
| 0x15C | int | numParts | Number of mesh parts |
| 0x160 | ptr* | pParts | Array of part pointers |
| 0x164 | float | lodDistance | LOD distance threshold |
| 0x168 | int | flags | Mesh flags |
| 0x170 | int | refCount | Reference counter |
| 0x174 | | | Struct size = 0x174 bytes |

## Global Variables

| Address | Type | Name | Purpose |
|---------|------|------|---------|
| 0x00704ad8 | CMesh* | g_pMeshList | Head of global mesh linked list |
| 0x00704adc | void* | g_pDefaultMeshTex | Default mesh texture data |
| 0x00704ae0 | int | g_bMeshDebugLog | Enable mesh debug logging |
| 0x00704ae4 | char | g_bMeshArchiveOpen | Flag: AYA archive currently open |
| 0x00704ae8 | int | g_nEmitterMemory | Total emitter memory allocated |
| 0x00704af0 | int | g_nTotalParts | Total mesh parts (pre-optimize) |
| 0x00704af4 | int | g_nRemovedParts | Parts removed by optimization |

## Cross-References

The mesh.cpp debug string at 0x0062f8e8 has 54 total cross-references:
- 6 main functions (documented above)
- 48 Unwind exception handlers (compiler-generated cleanup code)

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x0062f8d4 | "unknown mesh name" | Default name for unnamed meshes |
| 0x0062f904 | "No mesh resource leaks!" | Shutdown validation message |
| 0x0062f938 | "Mesh '%s' leaked : refcount=%d" | Memory leak warning |
| 0x0062fa00 | "Mesh end-of-level resource leaks" | Level cleanup validation |
| 0x0062fadc | "data\Meshes\" | Mesh file path prefix |
| 0x0062fb28 | "Meshes/%s/Emitters" | Emitter data path |
| 0x0062fb5c | "Error loading chained mesh!" | Chain loading failure |
| 0x0062fc1c | "meshtex\%s" | Mesh texture path format |
| 0x0062fc80 | "Mesh '%s' not found in level resource file" | Missing resource warning |
| 0x0062fd28 | "data\resources\meshes\m_%s.aya" | AYA archive path format |

## Related
- Debug Path: `[maintainer-local-source-export-root]\mesh.cpp`
- Parent: [../README.md](../README.md)
