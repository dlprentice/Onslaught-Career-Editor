# MeshCollisionVolume.cpp Functions

Wave1162 current-risk update: Wave1162 (`wave1162-collision-terrain-detector-current-risk-review`) re-read the mesh-volume and detector bridge with fresh Ghidra evidence. It covers `CMeshCollisionVolume__IsDirectionInsideTrianglePrism`, `CMeshCollisionVolume__VFunc_03_004ac6e0`, and `CMeshCollisionVolume__VFunc_04_004ad830` beside HLCollisionDetector and HeightField context. Accounting advances to `547/1179 = 46.40%` with `14 collision/terrain detector current-risk rows`, current focused candidates: 1178, live regenerated current focused candidates: 1178, remaining active focused work: 632, current risk candidates: 6166, fresh Ghidra export, read-only review, no mutation, `0 / 0 / 0`, `6411/6411 = 100.00%`, `41 xref rows`, and `2104 instruction rows`. Anchors include `CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags`, `CMeshCollisionVolume__IsDirectionInsideTrianglePrism`, `CHeightField__GetHeightSamplePacked16`, `CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions`, `CHLCollisionDetector__ProcessMapWhoCollisionSweep`, and `CHLCollisionDetector__HandleScheduledCollisionEvent`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-021413_post_wave1162_collision_terrain_detector_current_risk_review_verified`; source denominator `wave1108-current-risk-rank`; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Runtime collision behavior, exact vector/AABB/contact layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Wave1161 current-risk update: Wave1161 (`wave1161-collision-seeking-round-current-risk-review`) accounts for `17 collision-seeking/mesh-collision current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, no runtime-file mutation, and Codex read-only consults used while Codex root made the final judgment. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `533/1179 = 45.21%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 646; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `74 xref rows` and `1567 instruction rows`. Static anchors include `CCollisionSeekingRound__InitCollisionLineAndSound`, `CCollisionSeekingRound__ResolveRoundCollisionResponse`, `CCollisionSeekingRound__ProcessMapWhoCollisionSweep`, `CMeshCollisionVolume__TestSweptSphereAgainstMeshPart`, `CMeshCollisionVolume__ResolveContactNormalAndPlane`, and `CCollisionSeekingRound__ShutdownMonitorAndDestruct`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-014548_post_wave1161_collision_seeking_round_current_risk_review_verified`. Runtime collision behavior, runtime projectile behavior, exact CCollisionSeekingRound/CMeshCollisionVolume/CLine layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1161; wave1161-collision-seeking-round-current-risk-review; 533/1179 = 45.21%; 17 collision-seeking/mesh-collision current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 646; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 74 xref rows; 1567 instruction rows; CCollisionSeekingRound__InitCollisionLineAndSound; CCollisionSeekingRound__ResolveRoundCollisionResponse; CCollisionSeekingRound__ProcessMapWhoCollisionSweep; CMeshCollisionVolume__TestSweptSphereAgainstMeshPart; CMeshCollisionVolume__ResolveContactNormalAndPlane; CCollisionSeekingRound__ShutdownMonitorAndDestruct; [maintainer-local-ghidra-backup-root]\BEA_20260606-014548_post_wave1161_collision_seeking_round_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

> Source File: MeshCollisionVolume.cpp | Binary: BEA.exe
> Debug Path: `[maintainer-local-source-export-root]\MeshCollisionVolume.cpp` at 0x0062fe40

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Mesh-based collision volume system for physics calculations. This file handles the creation and management of collision bounding volumes for mesh parts, used in the game's physics and collision detection systems.

The main function allocates collision volume data structures (0x74 bytes per mesh part) and computes bounding box information for each mesh component.

Wave1071 (`texel-unpack-head-mid-review-wave1071`) re-read `0x0058546f CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4` as part of the Wave672/Wave673 texel-unpack head/middle table. Fresh metadata/tags/xrefs/instructions/decompile evidence ties the row to DATA slot `0x005ea048` and four 16-bit lane expansion, but owner/layout identity remains unproven, so the current saved owner label is retained as bounded static state rather than promoted exact source identity. Queue closure remains `6246/6246 = 100.00%`; expanded static surface progress advances to `1319/1560 = 84.55%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-031627_post_wave1071_texel_unpack_head_mid_review_verified`. Runtime texture output behavior, runtime codec/FourCC behavior, exact profile/descriptor/layout identity, exact source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave 387 also records four nearby geometry/collision helpers used by the saved MeshCollisionVolume swept-sphere path. Wave446 extends that static evidence with the immediate swept-sphere/segment-triangle helpers, two recovered MeshCollisionVolume vtable bodies, and the stale `Geometry__NoOpHook` correction to `Vec3__MagnitudeSquared`. Their exact source-file identity and concrete vector/AABB/contact layouts remain unproven, so they are listed here as caller-owned follow-up evidence rather than as fully recovered source bodies.

Wave1121 (`wave1121-mixed-score24-current-risk-review`) re-read `0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0` and `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830` as part of the score-24 mixed current-risk head. Fresh post exports keep slot-3 DATA xref `0x005d95d4`, slot-4 DATA xref `0x005d95d8`, swept-sphere bounds/mesh-part tests, and segment-triangle hit evidence coherent with Wave446/Wave1098. Wave1121 made no MeshCollisionVolume mutation. Current focused accounting moves to `122/1179 = 10.35%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-033658_post_wave1121_mixed_score24_current_risk_review_verified`. Runtime mesh collision behavior, exact vector/AABB/contact layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1127 (`wave1127-mixed-score23-current-risk-review`) re-read and tag-normalized `0x00479200 Geometry__SelectClosestPointOnTriangleEdges` as a score-23 current-risk row. Fresh evidence keeps the helper tied to the swept-sphere triangle core caller `CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`: it computes clamped projections across all three triangle edges, compares candidate distances with `Vec3__MagnitudeSquared` / `Vec3__Dot`, and writes the nearest candidate to `outClosest`. Wave1127 added tags only; no rename, signature, comment, function-boundary, or executable-byte change was made. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-071212_post_wave1127_mixed_score23_current_risk_review_verified`. Runtime collision behavior, exact vector/contact layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave939 (`meshcollisionvolume-swept-sphere-query-review-wave939`) re-reviewed the swept-sphere query dispatch layer after a Composer 2.5 adversarial consult and fresh Ghidra exports. Primary anchors were `0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50`, `0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0`, `0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds`, `0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart`, `0x004acf30 CMeshCollisionVolume__ResolveContactNormalAndPlane`, and `0x004ad600 CMeshCollisionVolume__SetPartBounds`, with Wave913 context including `0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore` and `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord`. Wave939 made a comment-only mutation at `0x004ac140`: the old "24 direction-table triangle faces" wording was normalized to "24-entry direction-pointer table as 8 triangle tests"; no rename, signature change, function-boundary change, or executable-byte change was made. Evidence counts: 7 pre metadata/tag rows, 14 xref rows, 1747 instruction rows, 7 decompile rows; 10 context metadata/tag rows, 18 xref rows, 2743 instruction rows, 10 decompile rows; 7 post metadata/tag rows, 14 xref rows, 1747 instruction rows, and 7 post decompile rows. Wave911 focused re-audit progress after Wave939 is `173/1408 = 12.29%`; static export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-024426_post_wave939_meshcollisionvolume_swept_sphere_query_review_verified`. Runtime collision correctness, exact MeshCollisionVolume/mesh-part/bounds/contact layouts, exact source-body identity, and rebuild parity remain separate proof.

Wave940 (`line-cylinder-dispatch-review-wave940`) kept the adjacent MeshCollisionVolume collision helpers as context for a read-only line/cylinder primitive dispatch review. The pass checked `0x004059a0 CCylinder__VFunc_01_004059a0`, `0x004098c0 CLine__VFunc_01_004098c0`, `0x004098e0 CLine__ctor_copy`, `0x00426340 CLine__ScalarDeletingDestructor_00426340`, `0x00426360 CLine__SetBaseVtable_00426360`, `0x00426320 CSphere__VFunc_01_00426320`, and vtables `0x005d88cc`, `0x005d8bfc`, and `0x005d95e8` while preserving MeshCollisionVolume anchors `0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`, `0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism`, `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord`, and `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830`. Mutation status: read-only review; no mutation was warranted. Wave911 focused re-audit progress after Wave940 is `178/1408 = 12.64%`; static export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-030741_post_wave940_line_cylinder_dispatch_review_verified`. Runtime primitive dispatch behavior, runtime collision/trace behavior, exact primitive layouts, exact source-body identity, and rebuild parity remain separate proof.

Wave1098 (`primitive-collision-bridge-review-wave1098`) revisited the primitive-to-MeshCollisionVolume bridge after full static closure and saved tag-only normalization for twenty-one rows. The MeshCollisionVolume side includes `0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50`, `0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds`, `0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart`, `0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0`, `0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`, `0x00478c20 Geometry__IntersectSegmentTriangleAndStoreHit`, `0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism`, `0x00479200 Geometry__SelectClosestPointOnTriangleEdges`, `0x00479630 Geometry__RaySphereEntryDistance`, `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord`, and `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830`; the primitive bridge side includes `0x004059a0 CCylinder__VFunc_01_004059a0`, `0x004098c0 CLine__VFunc_01_004098c0`, `0x004098e0 CLine__ctor_copy`, `0x00426320 CSphere__VFunc_01_00426320`, and `0x0043fe20 CCylinder__ResolveCollisionVFunc02`. Probe token anchor: Wave1098; primitive-collision-bridge-review-wave1098; 0x004059a0 CCylinder__VFunc_01_004059a0; 0x004098c0 CLine__VFunc_01_004098c0; 0x004098e0 CLine__ctor_copy; 0x00426320 CSphere__VFunc_01_00426320; 0x0043fe20 CCylinder__ResolveCollisionVFunc02; 0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50; 0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds; 0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart; 0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0; 0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore; 0x00478c20 Geometry__IntersectSegmentTriangleAndStoreHit; 0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified; tag-only normalization. Runtime collision/trace correctness, exact primitive/vector/AABB/mesh/contact/vtable layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave889 texture codec surface prelude (`texture-codec-surface-prelude-wave889`, `wave889-readback-verified`) saved comments/tags for the texture codec, surface-node, mapped-resource, vertex-shader parser, and resample prelude tranche. Probe token anchor: Wave889 texture codec surface prelude; texture-codec-surface-prelude-wave889; 0x00579a9a CVertexShader__CompileScriptWithDirectiveParser; 0x00579b39 CDXTexture__LookupNamedFormatDescriptor; 0x00579e08 CDXTexture__DecodeBmpDibFromMemory; 0x0057ca6a CDXTexture__DecodeFromMemory_WithFallbackCodecs; 0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode; 0x0057cca4 CFastVB__BuildResampleKernelBuckets; 0x0057cf60 CDXTexture__CopyDxtBlockRegion; 0x0057d0ee CWaypointManager__BoxBlurPackedColorRows_Scalar; 6054/6113 = 99.03%; [maintainer-local-ghidra-backup-root]\BEA_20260526-040930_post_wave889_texture_codec_surface_prelude_verified. Static evidence ties the tranche to directive parsing, descriptor lookup, codec dispatch, surface-node cleanup, mapped texture export, resample bucket setup, and DXT block copying. Exact texture/codec/surface-node/mapped-file/descriptor/parser/resample table layouts, exact source-body identity, runtime texture decode/encode/export/resample/render behavior, BEA patching, and rebuild parity remain deferred.

## Wave758 SetPartBounds Unwind Read-Back

Wave758 static read-back (`unwind-continuation-wave758`, `wave758-readback-verified`) preserved the existing `0x005d3980 CMeshCollisionVolume__SetPartBounds_Unwind` name and hardened its saved signature/comment/tags as `void __cdecl CMeshCollisionVolume__SetPartBounds_Unwind(void)`. DATA scope-table xref `0x0061c5ec` points at the body; instruction/decompile evidence calls `OID__FreeObject_Callback` on `*(EBP+0x4)` with MeshCollisionVolume.cpp debug path `0x0062fe40` and raw pushed immediate tokens `0x229` and `0x6c`. No rename, function-boundary change, or executable-byte change was made. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-123821_post_wave758_unwind_continuation_verified`. Exact parent source-body identity, exact allocator callback argument semantics for the two immediates, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Wave724 Texture Row Edge Padding Current-Owner Note

Wave724 texture row edge padding head retained three current `CMeshCollisionVolume__*` owner labels for `0x005ab4d0`, `0x005ab620`, and `0x005ab700` while hardening the adjacent texture/decode row-cache tranche documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texture-row-edge-padding-head-wave724`; the next queue head after this pass is `0x005aba90 CDXTexture__SelectNextScanTableForProgress`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh` | `void __fastcall CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh(void * texture_context)` | Mirrors/copies high-side edge rows for component-plane row buffers using ECX texture/decode context. The existing owner label is retained as current Ghidra state, but static evidence is texture row-cache/edge-padding behavior rather than owner/source identity proof. |
| `0x005ab620 CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth` | `void CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth(void)` | Comment/tag-only because Ghidra still exposes hidden EAX storage. Mirrors/copies both edge sides for component-plane row buffers using texture/decode context evidence; current owner/source identity remains unproven. |
| `0x005ab700 CMeshCollisionVolume__FinalizeEdgePaddingRows` | `void CMeshCollisionVolume__FinalizeEdgePaddingRows(void)` | Comment/tag-only because Ghidra still exposes hidden EAX storage. Finalizes component-plane edge-padding rows and records first-component padding height at row-cache `+0x48`; current owner/source identity remains unproven. |

Wave724 read-back evidence verified `5` metadata rows, `5` tag rows, `5` xref rows, `2405` instruction rows, and `5` decompile rows across `0x005ab420 CTexture__BuildComponentPlaneRowPointers` through `0x005ab9c0 CDXTexture__InitComponentPlaneRowCache`. Post-Wave724 queue telemetry is `6098` total, `4260` commented, `1838` commentless, `1216` exact-undefined signatures, `109` `param_N`, strict clean-signature proxy `4202/6098 = 68.91%`, and next high-signal head `0x005aba90 CDXTexture__SelectNextScanTableForProgress`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-055657_post_wave724_texture_row_edge_padding_head_verified`.

Probe anchors: `Wave724 texture row edge padding head`, `texture-row-edge-padding-head-wave724`, `0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh`, `0x005ab620 CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth`, `0x005ab700 CMeshCollisionVolume__FinalizeEdgePaddingRows`, `0x005aba90 CDXTexture__SelectNextScanTableForProgress`, `0x0042f220 CSPtrSet__Clear`.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004abe50 | CMeshCollisionVolume__VFunc_02_004abe50 | Vtable slot-2 wrapper that builds a local sphere/line-style record and dispatches to slot +0x0c | ~160 bytes |
| 0x004ac000 | CMeshCollisionVolume__InitDirectionLookupTable | Initializes direction lookup table used by collision-volume setup paths | ~1536 bytes |
| 0x004ac0e0 | CMeshCollisionVolume__dtor_base | Destructor body called by the scalar-deleting wrapper; frees per-part collision data at `+0x24` | ~96 bytes |
| 0x004ac140 | CMeshCollisionVolume__TestSweptSphereAgainstBounds | Swept-sphere versus bounds test with early reject/accept hit-state updates | ~864 bytes |
| 0x004ac4a0 | CMeshCollisionVolume__TestSweptSphereAgainstMeshPart | Iterates mesh-part candidates and tests swept-sphere collisions | ~1040 bytes |
| 0x004acf30 | CMeshCollisionVolume__ResolveContactNormalAndPlane | Builds contact normal/plane output from candidate axes and fallback rules | ~944 bytes |
| 0x004acde0 | CMeshCollisionVolume__InitContactOutputRecord | Initializes contact-output record fields and sets active/result flag; Wave795 clears the exact-undefined return while preserving the hidden EBX/tail-block boundary | ~64 bytes |
| 0x004ad600 | CMeshCollisionVolume__SetPartBounds | Allocates and initializes collision bounds for mesh parts | ~456 bytes |
| 0x005d3980 | CMeshCollisionVolume__SetPartBounds_Unwind | Exception handler for SetPartBounds memory cleanup | ~25 bytes |

## Geometry / Collision Helper Follow-up (Wave387)

| Address | Name | Evidence Boundary |
|---------|------|-------------------|
| 0x00479020 | CMeshCollisionVolume__IsDirectionInsideTrianglePrism | Saved signature/comment/tag metadata for the signed edge/plane dot-test helper called from `CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`. |
| 0x00479200 | Geometry__SelectClosestPointOnTriangleEdges | Saved signature/comment/tag metadata for the helper that clamps candidate points along all three triangle edges and selects the nearest result. |
| 0x00479630 | Geometry__RaySphereEntryDistance | Saved signature/comment/tag metadata for the normalized ray/sphere entry-distance helper that returns the retail sentinel when no positive entry is observed. |
| 0x00479770 | Geometry__DistanceOutsideAabb | Supersedes the older `CMeshCollisionVolume__Helper_00479770` doc label; current saved evidence is AABB overhang distance context called from `CMeshCollisionVolume__TestSweptSphereAgainstBounds`. The all-three-axis branch records the retail instruction sequence rather than an idealized formula. |

This follow-up is saved static Ghidra evidence only. It does not prove runtime collision behavior, exact Stuart-source method identity, concrete vector/AABB/mesh-collision layouts, concrete local names/types, BEA launch, game patching, or rebuild parity.

## Follow-up Recovery Notes (Wave56 Prep)

- `0x004ac6b0`: headless create probe failed (`createFunction returned null after disassemble`); function object still missing and queued for targeted retry.
- `0x004acde0`: function object created in wave56 prep and promoted in wave57 to `CMeshCollisionVolume__InitContactOutputRecord`.

## CollisionSeekingRound Boundary Follow-up (Wave322)

- `0x00426300` is now saved as `CMeshCollisionVolume__ScalarDeletingDestructor_00426300` with signature `void * __thiscall CMeshCollisionVolume__ScalarDeletingDestructor_00426300(void * this, int deleteFlags)`.
- Wave445 now saves the called destructor body at `0x004ac0e0` as `CMeshCollisionVolume__dtor_base` with signature `void __thiscall CMeshCollisionVolume__dtor_base(void * this)`.
- The corrections are scoped to the CollisionSeekingRound helper boundary, scalar-deleting destructor wrapper, and the destructor body. They do not prove concrete helper subtype layout, tags, locals, runtime collision-volume behavior, or rebuild parity.

## Wave445 MeshCollisionVolume Bridge Hardening

Fresh metadata, decompile, xref, instruction, and tag read-back on 2026-05-16 hardened three MeshCollisionVolume entries in the CMesh-adjacent queue-head cluster. `ApplyCMeshWave445.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_cmesh_wave445_probe.py --check` passed. The CMesh-specific companions are documented in [../mesh.cpp/_index.md](../mesh.cpp/_index.md).

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004ac0e0` | `void __thiscall CMeshCollisionVolume__dtor_base(void * this)` | Called by `CMeshCollisionVolume__ScalarDeletingDestructor_00426300`; installs the MeshCollisionVolume vtable during cleanup, frees per-part collision data at `+0x24` when present, clears the pointer, then restores the base vtable. |
| `0x004acde0` | `void CMeshCollisionVolume__InitContactOutputRecord(void)` | Wave795 signature-debt hardening clears the final MeshCollisionVolume exact-undefined return while preserving the Wave445 boundary. The block uses hidden EBX as the contact/output record, copies caller-frame stack vector/float fields, sets record `+0x20` active/result flag to `1`, restores registers, and falls into a parent-style `RET 0x10`; exact hidden EBX/caller-frame ABI remains unproven. |
| `0x004ad600` | `void __thiscall CMeshCollisionVolume__SetPartBounds(void * this, void * mesh, int part_index, float bounds_status)` | Lazy allocates a per-part array at `this+0x24` sized `mesh->+0x15c * 0x74` with allocation tag `0x6c`, initializes entry status to `-1.0f`, validates `mesh->+0x160[part_index]`, chooses standard mesh-part or interpolated mech-pose bounds based on `this+0x1c`, writes two 4x3 matrices plus a vec4, and stores `bounds_status` at entry `+0x70`. |

These are saved static Ghidra facts only. They do not prove runtime collision behavior, exact matrix/vector/contact-record layouts, exact field names/types, exact source method identity, BEA launch behavior, game patching, or rebuild parity.

## Wave446 Collision / Geometry Hardening

Fresh metadata, decompile, xref, vtable, and tag read-back on 2026-05-16 recovered two missing MeshCollisionVolume vtable function boundaries and hardened the adjacent collision geometry helpers. `ApplyCollisionGeometryWave446.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_collision_geometry_wave446_probe.py --check` passed.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004262e0` | `int __thiscall CMeshCollisionVolume__VFunc_05_004262e0(void * this, void * query_arg0, void * query_arg1, void * delegate_object, void * query_arg3)` | MeshCollisionVolume vtable slot 5 at `0x005d95dc`; forwards four stack arguments and the current object into the delegate object's vtable slot `+0x04`, then returns with `RET 0x10`. |
| `0x00426320` | `int __thiscall CSphere__VFunc_01_00426320(void * this, void * query_arg0, void * query_arg1, void * delegate_object, void * query_arg3)` | CSphere-adjacent forwarder from the `0x005d95e8` / `0x005d95fc` table region; forwards to delegate vtable slot `+0x0c`. Exact owner table split remains open. |
| `0x00477ba0` | `double __fastcall Vec3__MagnitudeSquared(void * this)` | Corrects stale `Geometry__NoOpHook`; instruction body computes `x*x + y*y + z*z` from `ECX`, `ECX+4`, and `ECX+8`. Post-apply swept-sphere decompile now calls `Vec3__MagnitudeSquared(sweep_delta)` instead of relying on `extraout_ST0`. |
| `0x00478160` | `int __cdecl Geometry__ClipSegmentAgainstAABB3D(float * start_x, float * start_y, float * start_z, float * end_x, float * end_y, float * end_z, float * bounds_minmax)` | Clips scalar endpoint pointers against a six-float AABB ordered `minX, minY, maxX, maxY, minZ, maxZ`; called by `CMapWho__GetFirstEntryWithinLine` and `CPolyBucket__StartLineSearch`. |
| `0x00478510` | `int __cdecl CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore(void * triangle_vertex0, void * triangle_vertex1, void * triangle_vertex2, void * sphere_start, void * sweep_delta, float sphere_radius, void * contact_record)` | Tests swept sphere against one triangle, uses `Vec3__MagnitudeSquared`, `Geometry__RaySphereEntryDistance`, and closest-edge fallback, then writes contact point/normal/time/status fields. |
| `0x00478c20` | `int __cdecl Geometry__IntersectSegmentTriangleAndStoreHit(void * triangle_vertex0, void * triangle_vertex1, void * triangle_vertex2, void * segment_start, void * segment_end, void * contact_record)` | Segment-triangle intersection helper; post-boundary xref now comes from recovered `CMeshCollisionVolume__VFunc_04_004ad830` instead of `<no_function>`. |
| `0x004ac6e0` | `int __thiscall CMeshCollisionVolume__VFunc_03_004ac6e0(void * this, void * query_arg0, float * motion_record, void * query_arg2, void * contact_record)` | Function boundary recovered for vtable slot 3 at `0x005d95d4`; scans mesh parts, refreshes bounds, dispatches swept-sphere tests, accumulates contact candidates, and updates motion/contact records. |
| `0x004ad830` | `int __thiscall CMeshCollisionVolume__VFunc_04_004ad830(void * this, void * query_arg0, void * state_record, void * segment_offsets, void * contact_record)` | Function boundary recovered for vtable slot 4 at `0x005d95d8`; scans line-triangle buckets, calls `Geometry__IntersectSegmentTriangleAndStoreHit`, and transforms the winning hit/normal through the part basis. |

These are saved static Ghidra facts only. They do not prove runtime collision behavior, concrete vector/AABB/contact-record layouts, exact owner/source identity, BEA launch behavior, game patching, or rebuild parity.

## Wave913 Mesh/Collision Re-Audit Review

Wave913 re-reviewed six Wave911-focused mesh/collision candidates (`0x00479020`, `0x00479200`, `0x004ad830`, `0x00478c20`, `0x00478510`, and `0x00477ba0`) with fresh metadata, tag, instruction, and decompile exports. The saved names/signatures/comments remain appropriate for the current static evidence, so no Ghidra mutation was performed. The exact source-identity, concrete vector/contact/AABB layouts, runtime collision behavior, BEA patching, and rebuild parity boundaries remain open.

## Wave535 MeshCollisionVolume Core Hardening

Fresh metadata, decompile, xref, instruction, and tag read-back on 2026-05-18 hardened five adjacent MeshCollisionVolume core collision entries. `ApplyMeshCollisionVolumeCoreWave535.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_meshcollisionvolume_core_wave535_probe.py --check` plus `npm run test:ghidra-meshcollisionvolume-core-wave535` passed.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004abe50` | `int __thiscall CMeshCollisionVolume__VFunc_02_004abe50(void * this, void * query_arg0, void * query_arg1, void * source_sphere_record, void * contact_record)` | CMeshCollisionVolume vtable slot 2 at `0x005d95d0`; uses ECX as the current object, builds a local `0x005d95e8`-record from `source_sphere_record`, dispatches through this object's vtable slot `+0x0c`, and returns with `RET 0x10`. |
| `0x004ac000` | `void __cdecl CMeshCollisionVolume__InitDirectionLookupTable(void)` | Lazy initializer for the global direction lookup table at `0x00704bf8..0x00704c54`; sets flag `0x00704cc8` once populated. |
| `0x004ac140` | `int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstBounds(void * part_context, void * bounds_record, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)` | `RET 0x18` stack-cleaning helper from vtable slot 3; tests a swept sphere against bounds center/extent fields and either direction-table triangle faces or `Geometry__DistanceOutsideAabb`. |
| `0x004ac4a0` | `int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstMeshPart(void * part_context, void * mesh_part, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)` | `RET 0x18` stack-cleaning helper from vtable slot 3; starts a mesh-part triangle bucket search, expands quantized triangle vertices through `mesh_part+0x100`, and calls the swept-sphere triangle core for candidates. |
| `0x004acf30` | `int __stdcall CMeshCollisionVolume__ResolveContactNormalAndPlane(float * contact_record, float hit_x, float hit_y, float hit_z, float hit_w, float normal_x, float normal_y, float normal_z, float normal_w, float unused_source_w, float * out_contact_point, float * out_contact_normal)` | `RET 0x30` contact-resolution helper from vtable slot 3; normalizes vectors, handles contact-record sentinel flags, appends candidate normals, and writes output point/normal vectors. The tenth stack dword is observed but currently unused. |

These are saved static Ghidra facts only. They do not prove runtime collision behavior, concrete mesh/contact/AABB layouts, exact source-body identity, BEA launch behavior, game patching, or rebuild parity. Wave795 later cleared the exact-undefined return for `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord` as `void CMeshCollisionVolume__InitContactOutputRecord(void)` while keeping the hidden EBX/caller-frame ABI and clean source boundary unresolved. Probe anchors: `Wave795 signature debt`, `signature-debt-wave795`, `0x0056a140 __allshl`, `0x005d0648 __setjmp3`, `0x005d06d0 __aullshr`, `0 exact-undefined signatures`, `0x0042f220 CSPtrSet__Clear`, `0x004bbcd0 CNamedMesh__VFunc_09_004bbcd0`, `[maintainer-local-ghidra-backup-root]\BEA_20260524-043918_post_wave795_final_undefined_signature_debt_verified`.


## Wave672 Texel Unpack Head Current-Owner Note

Wave672 texel unpack head retained the current owner label `CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4` for `0x0058546f` while hardening the adjacent CTexture/CFastVB/CDXTexture unpacker tranche documented in [`texture.cpp`](../texture.cpp/_index.md), [`FastVB.cpp`](../FastVB.cpp/_index.md), and [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texel-unpack-head-wave672`; the next queue head after this pass is `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058546f` | `void __thiscall CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Current-owner 16-16-16-16 unpacker computes the source pointer from `+0x1058/+0x105c/+0x20`, reads two dwords per texel, expands four 16-bit lanes to float4 output, and shows a decompiler `__aullshr` helper for the third lane. Exact owner/layout identity remains open. |

Wave672 read-back evidence verified `16` metadata rows, `16` tag rows, `16` xref rows, `1616` instruction rows, and `16` clean decompile rows across `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4` through `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4`. Post-Wave672 queue telemetry is `6098` total, `3746` commented, `2352` commentless, `1217` exact-undefined signatures, `571` `param_N`, strict clean-signature proxy `3696/6098 = 60.61%`, and next head `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-042809_post_wave672_texel_unpack_head_verified`.

Probe anchors: `Wave672 texel unpack head`, `texel-unpack-head-wave672`, `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`, `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4`, `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`.

## Semantic Promotion Follow-up (Wave63)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0058546f | CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4 | Dispatch-table sibling in texture-unpack family; unpacks 16-16-16-16 packed texels into float4 channels. |

## Function Details

### CMeshCollisionVolume__SetPartBounds (0x004ad600)

**Saved Signature:** `void __thiscall CMeshCollisionVolume__SetPartBounds(void * this, void * mesh, int part_index, float bounds_status)`

**Purpose:** Initializes collision volume data for a specific mesh part. Allocates memory for collision structures if not already allocated, then computes and stores bounding box data.

**Key Operations:**
1. **Memory Allocation** (lines 0x229 referenced):
   - Allocates `numParts * 0x74` bytes for collision data array
   - Each collision entry is 0x74 (116) bytes containing two 4x4 matrices and additional data
   - Uses memory allocator ID 0x6c

2. **Collision Data Structure** (per part, 0x74 bytes):
   - Offset 0x00: First 4x3 matrix (0x30 bytes) - likely world-space bounds
   - Offset 0x30: Second 4x3 matrix (0x30 bytes) - likely local-space bounds
   - Offset 0x60: 4x float vector (0x10 bytes) - bounding info
   - Offset 0x70: float value initialized to -1.0f (0xBF800000)

3. **Bounds Calculation:**
   - If `this+0x1c == 0`: calls `CMeshPart__EvaluatePoseTransformForFrame` for standard mesh bounds
   - If `this+0x1c != 0`: calls `CMCMech__BuildInterpolatedPoseAndAnchor` for interpolated mech pose/bounds calculation
   - Both paths write matrix data and bounding info to the collision structure

4. **Error Handling:**
   - Logs error "Error: Can't find mesh part in..." (string at 0x0062fe20) if mesh part lookup fails

**Class Fields Used:**
- `this+0x14`: Pointer to mesh/model data
- `this+0x1c`: Mode flag (determines bounds calculation method)
- `this+0x24`: Pointer to collision data array (allocated on first call)

### CMeshCollisionVolume__SetPartBounds_Unwind (0x005d3980)

**Signature:** `void CMeshCollisionVolume::SetPartBounds_Unwind(void* ptr)`

**Purpose:** SEH exception handler that frees memory allocated in SetPartBounds if an exception occurs during initialization.

**Key Operations:**
- Calls memory deallocator `OID__FreeObject_Callback` (caller passes alloc tag 0x6c for context)
- Same line number (0x229) as the allocation, indicating paired alloc/dealloc

## Key Observations

1. **Memory Management Pattern:** Uses structured exception handling (SEH) with paired allocator/deallocator (0x6c) for safe memory management during collision volume setup.

2. **Lazy Initialization:** Collision data is only allocated on first use (`this+0x24 == 0` check), not during object construction.

3. **Per-Part Storage:** Each mesh part gets a dedicated 0x74-byte collision structure, allowing independent collision calculations per mesh segment.

4. **Dual Bounds Modes:** The `field_0x1c` flag switches between two different bounds calculation methods, possibly for static vs. animated meshes or different collision precision levels.

5. **Float Sentinel Value:** The -1.0f (0xBF800000) initialization at offset 0x70 likely indicates "unprocessed" or "invalid" state.

6. **Matrix Storage:** Two 4x3 matrices (48 bytes each) suggest storage of both local and world-space oriented bounding boxes for efficient collision testing.

## Related Functions

- `CMeshPart__EvaluatePoseTransformForFrame` - Standard mesh bounds calculation
- `CMCMech__BuildInterpolatedPoseAndAnchor` - Interpolated mech pose/bounds calculation
- `OID__AllocObject` - Memory allocator
- `OID__FreeObject_Callback` - Memory deallocator callback wrapper
- `FUN_004011b0` - Matrix/vector initialization

## Data Structures

```cpp
// Collision volume entry (0x74 bytes per mesh part)
struct MeshPartCollision {
    float matrix1[12];    // 0x00: 4x3 matrix (world bounds?)
    float matrix2[12];    // 0x30: 4x3 matrix (local bounds?)
    float boundingInfo[4]; // 0x60: bounding sphere/box data
    float status;         // 0x70: -1.0f = unprocessed
};
```

---
*Discovered via Phase 1 xref analysis (Dec 2025)*

## Wave1151 Current-Risk Tag Normalization

Wave1151 tag-only normalization re-confirms the primitive wrapper side of the MeshCollisionVolume bridge through `0x004059a0 CCylinder__VFunc_01_004059a0` and `0x004098c0 CLine__VFunc_01_004098c0`. This was tag-only Wave1151/current-risk normalization; no collision semantic mutation was made. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
