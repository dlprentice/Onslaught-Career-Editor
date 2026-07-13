# Mesh / Resource / Render Static Contract

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x005441b0` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1220 static closeout acceptance: active current-risk focused accounting is `1179/1179 = 100.00%`; remaining active focused work: 0. This is static Ghidra/read-back/system-map acceptance for the current-risk lane, not runtime render/resource behavior, exact layout proof, exact source-body identity, BEA patching proof, visual output proof, rebuild parity, or no-noticeable-difference parity.

Historical Wave1217 and earlier anchors below are at-wave snapshots; their older active current-risk counters are preserved as evidence provenance, not current status.

Wave1217 measured anchor: unique-address accounting governs active current-risk progress. Probe token anchor: Wave1217; wave1217-lifecycle-cleanup-tail-current-risk-review; 1155/1179 = 97.96%; 10 lifecycle/cleanup tail current-risk rows; CCarrierAI__scalar_deleting_dtor; CTree__scalar_deleting_dtor; CActorBase__shared_scalar_deleting_dtor_004bfd00; CRTBuilding__ScalarDeletingDestructor; CActor__dtor_base_Thunk; CCSPersistentThing__dtor_base; CTree__dtor_base; CWarspite__ScalarDeletingDestructor; CMine__VFunc02_CleanupLinkedParticleAndForward; CMine__TryDestroyedResetAndDispatchVFunc1D4; 6411/6411 = 100.00%; 0 / 0 / 0; 12 xref rows; 137 instruction rows; 10 decompile rows; 103 context xref rows; 681 context instruction rows; 14 context decompile rows; 29 data-xref rows; current focused candidates: 1117; live regenerated current focused candidates: 1117; remaining active focused work: 24; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; stale CTree destructor-body reference corrected; CCarrierAI tag gap corrected; updated=10 skipped=0; comment_only_updated=10; tags_added=80; no rename; no signature change; no function-boundary change; no executable-byte change; unique-address accounting; Codex read-only consults used; no Cursor/Composer; legacy additive counter is deprecated (`1186/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md; unit-battleengine-gameplay-static-contract.md; mesh-resource-render-static-contract.md; continuity denominator; [maintainer-local-ghidra-backup-root]\BEA_20260607-110625_post_wave1217_lifecycle_cleanup_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

Wave1217 lifecycle cleanup context: `CRTBuilding__ScalarDeletingDestructor` remains the RTBuilding scalar-deleting wrapper for `CRTBuilding__Destructor`; `CTree__scalar_deleting_dtor` now explicitly calls `CTree__dtor_base at 0x004f63c0`, correcting the stale destructor-body reference. These are static render/lifecycle anchors, not runtime render or cleanup proof.

Wave1216 measured anchor: unique-address accounting governs active current-risk progress. Probe token anchor: Wave1216; wave1216-render-resource-texture-hud-tail-current-risk-review; 1145/1179 = 97.12%; 7 render/resource/texture/HUD tail current-risk rows; CThing__InitRenderThingFromInitMeshName; CPDMesh__dtor_base; CWaterRenderSystem__ResetAndMarkSourceFlag; CAtmosphericsProfile__ResetAndInitSnowResources; CHudComponent__RenderPassEntry; CTexture__NodeType11_Ctor_WithDescriptorCopy; CTexture__NodeType12_Ctor_WithStackScalars; CTexture__NodeType11_Dtor_DeleteOnFlag_Body; CTexture__NodeType11_Dtor_DeleteOnFlag; 6411/6411 = 100.00%; 0 / 0 / 0; 12 xref rows; 962 instruction rows; 7 decompile rows; 28 context xref rows; 1015 context instruction rows; 9 context decompile rows; 6 texture-context xref rows; 111 texture-context instruction rows; 6 texture-context decompile rows; 13 data-xref rows; current focused candidates: 1127; live regenerated current focused candidates: 1127; remaining active focused work: 34; current risk candidates: 6166; fresh Ghidra export; texture label correction; 4 renamed; 4 comments updated; 25 tags added; no signature change; no function-boundary change; no executable-byte change; unique-address accounting; Codex read-only consults used; no Cursor/Composer; legacy additive counter is deprecated (`1176/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md; mesh-resource-render-static-contract.md; texture-resource-decode-static-contract.md; continuity denominator; [maintainer-local-ghidra-backup-root]\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

Wave1214 measured anchor: unique-address accounting governs active current-risk progress. Wave1214 (`wave1214-math-color-screen-dispatch-current-risk-review`) accounts for `8 math/color/screen transform dispatch current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This read-only review covered `Color32__LerpArgb`, `Math__InvLerpClamp01`, `CPDSelector__ConvertNormalizedToScreenCoords`, `CRT__AcosDispatch_ST0`, `Math__BuildTranslationMatrix4x4_Dispatch_Thunk`, `Math__BuildQuaternionRotationMatrix_Dispatch_Thunk`, `Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk`, and `Math__InterpolateVec4ByRatio_Dispatch_Thunk`. There was no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; active current-risk progress is `1133/1179 = 96.10%`; remaining active focused work: 46; legacy additive counter is deprecated (`1164/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1127; live regenerated current focused candidates: 1127; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `58 xref rows`, `175 instruction rows`, `8 decompile rows`, `43 context xref rows`, `3821 context instruction rows`, and `20 context decompile rows`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-081942_post_wave1214_math_color_screen_dispatch_current_risk_review_verified`. Active measurement files: `static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `mesh-resource-render-static-contract.md`, and `reverse-engineering/binary-analysis/wave1108-current-risk-rank.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime particle rendering behavior, runtime screen-coordinate output, runtime x87/CRT edge cases, runtime CPU feature dispatch, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave1214 mesh/render context: the dispatch thunk context keeps `Math__BuildTranslationMatrix4x4_Dispatch_Thunk` tied to `CMeshRenderer__RenderMeshCore` callsites and keeps `Math__BuildQuaternionRotationMatrix_Dispatch_Thunk` tied to `CFastVB__BuildTransformMatrixWithOffsets` and `CTexture__BuildTransformMatrixWithOptionalOffsets`. This is static cross-reference context only, not runtime render proof.

Wave1213 measured anchor: unique-address accounting governs active current-risk progress. Wave1213 (`wave1213-render-resource-lifecycle-tail-current-risk-review`) accounts for `6 render-resource lifecycle tail current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This read-only review covered `CIBuffer__CreateConfigured`, `CIBuffer__LockDirect`, `CDXSurf__UnlinkNodeFromGlobalList`, `CDXBattleLine__DestructorThunk`, `CDXLandscape__Destructor`, and `CDXLandscape__ReleaseBuffers`. There was no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; active current-risk progress is `1125/1179 = 95.42%`; remaining active focused work: 54; legacy additive counter is deprecated (`1156/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1127; live regenerated current focused candidates: 1127; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `13 xref rows`, `152 instruction rows`, `6 decompile rows`, `41 context xref rows`, `1369 context instruction rows`, and `15 context decompile rows`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-074242_post_wave1213_render_resource_lifecycle_tail_current_risk_review_verified`. Active measurement files: `static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `mesh-resource-render-static-contract.md`, and `reverse-engineering/binary-analysis/wave1108-current-risk-rank.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime Direct3D behavior, runtime terrain/HUD output, runtime lost-device behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave1207 measured anchor: unique-address accounting governs active current-risk progress. Wave1207 (`wave1207-d3d-render-resource-lifecycle-current-risk-review`) accounts for `6 D3D/render-resource lifecycle current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This read-only review made no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; active current-risk progress is `1089/1179 = 92.37%`; remaining active focused work: 90; legacy additive counter is deprecated (`1120/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `36 xref rows`, `260 instruction rows`, and `6 decompile rows`. Anchors: `CVertexShader__scalar_deleting_dtor`, `CVertexShader__VFunc_02_00501a10`, `DeviceObject__dtor_body`, `DeviceObject__scalar_deleting_dtor`, `CDXMeshVB__scalar_deleting_dtor`, and `CDXMeshVB__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-033229_post_wave1207_d3d_render_resource_lifecycle_current_risk_review_verified`. Active measurement files: `static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, and `reverse-engineering/binary-analysis/wave1108-current-risk-rank.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime Direct3D behavior, runtime shader behavior, runtime render-resource behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Status: static contract from saved Ghidra and asset-count evidence
Last updated: 2026-06-07
Tag: `mesh-resource-render-static-contract-wave1164`
Prior/compatibility tag: `mesh-resource-render-static-contract-wave1104`
Scope: Wave1104 contract consolidation plus Wave1159 and Wave1164 current-risk re-reads for engine render bootstrap, CDXEngine frame render spine, render-state/matrix helpers, render queue, CMesh/CMeshPart resource and geometry loaders, primitive collision bridges, name/optimization predicates, pose-cache helpers, terrain texture/maptex loading, landscape cache/LOD, dynamic unit render handoff, atmospherics overlay state, and texture/model asset bridge counts.

This contract consolidates the mesh/resource/render evidence into one subsystem-level reference for static planning. It is intended for parser, renderer, model/resource tooling, clean-room rebuild notes, and later runtime-proof design. It does not replace the per-wave readiness notes, the static system review baselines, or the function owner docs.

Wave1204 measured anchor: unique-address accounting governs active current-risk progress. Wave1204 (`wave1204-geometry-terrain-residual-current-risk-review`) accounts for `9 Geometry/Terrain residual current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and tag-only normalization. Ghidra apply reported `updated=1 skipped=0` with `tags_added=11`; final dry updated=0 skipped=1. No rename, no signature change, no comment change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; active current-risk progress is `1071/1179 = 90.84%`; remaining active focused work: 108; legacy additive counter is deprecated (`1102/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `15 xref rows`, `1058 instruction rows`, and `9 decompile rows`. Anchors: `ShadowHeightfield__AnyBoundsCornerAboveSampledHeight`, `Geometry__RaySphereEntryDistance`, `Geometry__DistanceOutsideAabb`, `CHeightField__Load`, `CHeightField__Constructor`, `Triangulate__SplitTriangleAtPointAndLegalizeEdges`, `Triangulate__TryFlipSharedEdgeForQuality`, `Triangulate__FindTriangleByDirectedEdge`, and `Triangulate__RelaxMeshByEdgeFlips`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-013948_post_wave1204_geometry_terrain_residual_current_risk_review_verified`. Active measurement files: `static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, and `reverse-engineering/binary-analysis/wave1108-current-risk-rank.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime terrain behavior, runtime collision behavior, runtime shadow behavior, runtime triangulation behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Current dashboard context:

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave911 focused risk queue | `812/1408 = 57.67%` |
| Wave911 top-500 risk-ranked subset | `500/500 = 100.00%` |
| Wave1108 current focused accounting | `1179/1179 = 100.00%` |

Wave1204 current-risk update: Wave1204 (`wave1204-geometry-terrain-residual-current-risk-review`) ties the shadow-heightfield corner predicate, two primitive geometry helpers, CHeightField load/constructor rows, and the Triangulate split/flip/find/relax helpers into this contract. It is the current measured geometry/terrain residual slice and advances the active unique-address counter to `1071/1179 = 90.84%`. The row `0x00402dd0 ShadowHeightfield__AnyBoundsCornerAboveSampledHeight` received missing current-risk/static tags only; all names, signatures, comments, function boundaries, and executable bytes were left unchanged.

Wave1164 current-risk update: Wave1164 (`wave1164-engine-render-resource-current-risk-review`) accounts for `19 CEngine/CDXEngine/CDXLandscape/CUnit/render-resource current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, no runtime-file mutation, and Codex read-only consults used while Codex root made the final judgment. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `583/1179 = 49.45%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 596; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `52 xref rows` and `3400 instruction rows`. Static anchors include `CEngine__SetViewpoint`, `CEngine__UpdatePos`, `CVBufTexture__RenderDynamicUnitPass`, `CMapTex__LoadTexture`, `CMapTex__LoadMixerTextureSet`, `CUnit__RenderWithDistanceFade`, `CDXEngine__GenerateLandscapeCacheTileChunk`, `CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer`, `CDXLandscape__UpdateLOD`, and `CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-033330_post_wave1164_engine_render_resource_current_risk_review_verified`. Runtime render behavior, runtime landscape/terrain texture/atmospherics/unit-render behavior, exact CEngine/CDXEngine/CDXLandscape/CMapTex/CUnit/CVBufTexture/atmospherics layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1164; wave1164-engine-render-resource-current-risk-review; 583/1179 = 49.45%; 19 CEngine/CDXEngine/CDXLandscape/CUnit/render-resource current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 596; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 52 xref rows; 3400 instruction rows; CEngine__SetViewpoint; CEngine__UpdatePos; CVBufTexture__RenderDynamicUnitPass; CMapTex__LoadTexture; CMapTex__LoadMixerTextureSet; CUnit__RenderWithDistanceFade; CDXEngine__GenerateLandscapeCacheTileChunk; CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer; CDXLandscape__UpdateLOD; CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay; [maintainer-local-ghidra-backup-root]\BEA_20260606-033330_post_wave1164_engine_render_resource_current_risk_review_verified; mesh-resource-render-static-contract.md; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave1159 current-risk update: Wave1159 (`wave1159-cmeshpart-name-pose-current-risk-review`) accounts for `12 CMeshPart name/load/pose current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, no runtime-file mutation, and Codex read-only consults used for candidate/accounting and system-map sanity while Codex root made the final judgment. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `497/1179 = 42.15%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 682; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `33 xref rows` and `1790 instruction rows`. Static anchors include `CMeshPart__LoadOldStyle_VersionA`, `CMeshPart__RebuildPerVertexNormalsAndTangents`, `CMeshPart__PopulatePoseCacheRecursive`, `CMeshPart__EvaluatePoseTransformForFrame`, and `CMesh__FindPartByNameI`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-004711_post_wave1159_cmeshpart_name_pose_current_risk_review_verified`. Runtime mesh loading, pose-cache, render/collision behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1159; wave1159-cmeshpart-name-pose-current-risk-review; 497/1179 = 42.15%; 12 CMeshPart name/load/pose current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 682; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 33 xref rows; 1790 instruction rows; CMeshPart__LoadOldStyle_VersionA; CMeshPart__RebuildPerVertexNormalsAndTangents; CMeshPart__PopulatePoseCacheRecursive; CMeshPart__EvaluatePoseTransformForFrame; CMesh__FindPartByNameI; [maintainer-local-ghidra-backup-root]\BEA_20260606-004711_post_wave1159_cmeshpart_name_pose_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave1104 is a contract/doc/probe consolidation only. It made no Ghidra mutation, no executable-byte change, no BEA launch, and no installed-game or runtime-file mutation.

## Baseline Static System Slices

| Slice | Contract role |
| --- | --- |
| Wave904 `texture-render-static-review-wave904` | Static-coherent texture/resource/decode/render baseline: texture lookup/lifetime, DirectX texture load/decode/upload, CFastVB dispatch/math/render, CVBufTexture/CVBuffer/CIBuffer render paths, render-state cache, render queue, mesh-renderer entry, and asset extraction counts. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-101300_post_wave904_texture_render_static_review_verified`. |
| Wave905 `mesh-motion-world-particle-static-review-wave905` | Static-coherent mesh/motion/world/particle baseline: thing/render initialization, CMesh/CMeshPart geometry and pose-cache rows, world occupancy and physics-manager lists, mesh collision, particle manager/set/descriptor rows, and mesh asset bridge counts. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`. |
| Waves1093-1100 | Recent focused rechecks tying engine bootstrap, frame render spine, state/matrix support, render queue, primitive collision, CMesh registry, and CMeshPart load/geometry rows into the current `6410/6410 = 100.00%` closure state. |

## Engine And Frame Render Contract

Wave1093 re-read the CEngine constructor/lifecycle/resource/viewpoint/deserialize surface. Wave1094 then connected the game render loop to the CDXEngine frame render spine.

| Address | Static contract |
| --- | --- |
| `0x00449820 CEngine__ctor` | Installs engine vtable, seeds clip constants, clears owned resource pointers, and initializes viewpoint-adjacent state. |
| `0x004499d0 CEngine__Init` | Registers render/mesh cvars and allocates major render resources: gamut, map textures, water, landscape, HUD/light resources, screen effects, shadows, and trees. |
| `0x00449d50 CEngine__InitResources` | Loads zoom textures, blob shadows, highlight/hit/cloak textures, and landscape cloud-shadow texture resources. |
| `0x00449dc0 CEngine__LoadAllNamedMeshes` | Reads named mesh entries, reports `Loading named meshes`, reuses existing names by case-insensitive compare, and calls `CMesh__FindOrCreate` for new entries. |
| `0x00449ef0 CEngine__GetViewMatrixFromCamera` | Calls camera orientation vfunc, builds/transposes view basis terms, and copies the output view matrix block. |
| `0x0044a020 CEngine__SetViewpoint` | Stores per-view viewport/player/camera wrapper state and allocates a `CInterpolatedCamera`. |
| `0x0044a6e0 CEngine__Deserialize` | Reads `ENGN`/map-texture chunk data and dispatches map texture deserialize/init context. |
| `0x0046e460 CGame__Render` | Coordinates split-screen/fullscreen viewport setup, `CEngine__SetViewpoint`, `CDXEngine__PreRender`, repeated `CDXEngine__Render`, and `CDXEngine__PostRender`. |
| `0x0053e220 CDXEngine__PreRender` | Prepares per-frame engine/viewpoint state before per-view render loops. |
| `0x0053e2e0 CDXEngine__Render` | Drives per-view world rendering and reaches render queue, particle texture, water, Kempy cube, overlay, and fullscreen effect paths. |
| `0x0053ecc0 CDXEngine__PostRender` | Reaches HUD/viewpoint overlays including `0x00487d10 CHud__RenderBattleline`. |

Evidence anchors:

- Wave1093 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-155838_post_wave1093_cengine_core_bootstrap_review_verified`.
- Wave1094 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-163255_post_wave1094_cdxengine_frame_render_spine_review_verified`.
- Representative CDXEngine context: `0x0053bb50 CDXEngine__RenderOptionalFullscreenEffectPass`, `0x005441b0 CDXEngine__RenderKempyCubeFaces`, `0x0054f7e0 CDXEngine__RenderParticleTexturePass`, `0x00542a50 CDXEngine__BuildDirectionalSampleRing`, `0x00551920 CRenderQueue__BeginFrame`, and `0x005528b0 CRenderQueue__RenderAll`.

## Render-State And Queue Contract

Wave1095 re-read render-state/matrix support. Wave1096 re-read the CRenderQueue core and multipass handoff surface.

| Address | Static contract |
| --- | --- |
| `0x00513af0 D3DStateCache__SetSlotMode4or5` | Updates per-slot state array `DAT_008557f4` to mode `4` or `5` based on `DAT_008554fc`, then notifies `DAT_00888a50` through vfunc `+0x10c` when the slot changes. |
| `0x00513820 D3DStateCache__SetStateCached` | Cached state helper with broad render/frontend/device callers. |
| `0x00550b10 CDXEngine__SetProjectionMatrix` | Projection/depth matrix writer retained as matrix-context evidence. |
| `0x00550ca0 CDXEngine__SetWorldMatrixElements` | World-transform writer retained as matrix-context evidence. |
| `0x00550d50 CDXEngine__ApplyPendingRenderState` | Pending render-state flush retained as render-state context. |
| `0x005515e0 CRenderQueueBucket__RenderAndRecycle` | Walks bucket-linked render items, updates cached render state/matrix fields, draws indexed primitives, frees consumed items, and clears the bucket head. |
| `0x00551920 CRenderQueue__BeginFrame` | Seeds default render-queue/world-matrix state, calls bucket recycle, then restores sampler/render states. |
| `0x005528b0 CRenderQueue__RenderAll` | Recycles/merges entries, emits immediate triangle strips via `CFastVB`, restores render state, and resets global tint. |
| `0x00553960 CRenderQueue__RenderMultipassLayerA` / `0x00554170 CRenderQueue__RenderMultipassLayerB` | Multipass terrain/material layers using global queue receiver `0x009c7550`. |
| `0x005545d0 CRenderQueue__BuildProjectedSprites` / `0x00554750 CRenderQueue__EmitBillboardStrip` | Static-shadow/projected-sprite builder and billboard strip writer through `CVBufTexture`. |
| `0x00554df0 CRenderQueue__RenderVBufTextureWithStateToggle` | Toggles state around `CVBufTexture__Render(*(this+0x5b8), reset_after_render=1)`. |

Evidence anchors:

- Wave1095 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-171413_post_wave1095_render_state_matrix_support_review_verified`.
- Wave1096 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-174618_post_wave1096_crenderqueue_core_multipass_review_verified`.
- Texture/render baseline anchors: `CDXTexture__LoadTextureFromFile_Core`, `CDXTexture__DecodeMemoryToTextureObject`, `CDXTexture__UploadDecodedBufferToSurface`, `CFastVB__RenderTriangleStripImmediate`, `CVBufTexture__DrawSpriteEx`, `CVBufTexture__Render`, `CRenderQueue__RenderMultipassLayerA`, and `CMeshRenderer__RenderMesh`.

## Mesh Registry And Resource Contract

Wave1099 re-read the CEngine/CMesh resource registry, load, deserialize, cache, texture-binding, optimization, and release surface. Wave1100 then re-read CMeshPart load/geometry/free/optimization rows.

| Address | Static contract |
| --- | --- |
| `0x004a5020 CMesh__Init` | Initializes a `0x174`-byte mesh object, allocates resource buffer, and links through global mesh list `DAT_00704ad8`. |
| `0x004a50b0 CMesh__FreeResourcesAndUnlink` | Unlinks from `DAT_00704ad8`, releases embedded resources, frees parts/emitters/index/texture arrays, and decrements chained mesh refcount field `+0x170`. |
| `0x004a5200 CMesh__InitStatic` | Initializes default embedded mesh/texture resource in `DAT_00704adc`, including `meshtex\default.tga`. |
| `0x004a52d0 CMesh__ClearOut` | Releases `DAT_00704adc` and frees global mesh-list entries with zero usage/ref marker. |
| `0x004a5970 CMesh__LoadByNameWithStatus` | Builds `data\Meshes\` path, opens a file mem-buffer, and calls `CMesh__Load`. |
| `0x004a5b70 CMesh__Load` | Main mesh stream loader: validates stream/version tokens, loads material/part tables, texture records, old/new part bodies, chained meshes, and optimization/link/cache paths. |
| `0x004aa6e0 CMesh__FindOrCreate` | Global mesh cache helper: scans by name, increments `+0x170` on hit, or allocates/loads/frees on miss/failure. |
| `0x004aab90 CMesh__Deserialize` | Chunk/resource deserialize path used by resource accumulator and FE goodies, including optional `data\resources\meshes\m_%s.aya` archive path and chained mesh recursion. |
| `0x004adf90 CMesh__ReleaseEmbeddedResources` | Releases 0x24-byte material/texture resource records and decrements HUD/DX counters. |
| `0x004ae0d0 CMesh__InitPartVBufTextureFormats` | Resolves `CVBufTexture__GetOrCreate` and applies observed VB/IB format constants for mesh material/part records. |

Evidence anchors:

- `DAT_00704ad8` global mesh list.
- `DAT_00704adc` default embedded mesh resource.
- `data\Meshes`.
- `data\resources\meshes\m_%s.aya`.
- Wave1099 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-193549_post_wave1099_cmesh_resource_registry_review_verified`.

## CMeshPart Geometry Contract

Wave1100 ties the CMeshPart loader/allocation/free rows around observed `0x13c` serialized record evidence, DVertex/PVertex/triangle allocation, old-style/new-style/skinned stream loaders, polybucket construction/search, material loading, clone/merge, and optimization predicates.

| Address | Static contract |
| --- | --- |
| `0x004a51f0 CMeshPart__FreeResources` | Frees cached positions/orientations, dynamic arrays, bone/link/influence-map runtime buffers, polybucket, helper records, and vtable-owned field `+0x138`. |
| `0x004ae2b0 CMeshPart__CreatePolyBucket` | Lazily allocates the `0xb8`-byte polybucket-style object at part `+0x100`, clones/optionally optimizes the part, and builds the bucket. |
| `0x004ae860 CMeshPart__AllocateGeometry` | Records DVertex/PVertex/triangle/texcoord/frame counts at `+0xa8/+0xac/+0xb0/+0xb8/+0xb4`, then allocates DVertex, PVertex, and triangle storage. |
| `0x004aede0 CMeshPart__LoadOldStyle_VersionA` | Old-style loader for `0x60`-byte vertex/material records, Z-negation, material clamp/init, transform, triangle pointer build, and normal/tangent rebuild. |
| `0x004af470 CMeshPart__LoadVerticesAndTriangles` | Non-skinned stream loader for DVertex/PVertex/triangle data, split-DVertex remap, material clamp, and normal/tangent rebuild. |
| `0x004afbb0 CMeshPart__LoadVerticesWithBones` | Skinned stream loader with parent mesh tables, bone/influence records, format-tag-specific fields, split-DVertex remap, and normal/tangent rebuild. |
| `0x004b27a0 CMeshPart__LoadFromStream` | Chunk-reader path for a `0x13c` CMeshPart record; reads materials, texcoords, keyframes, bones, weights, optional polybucket data, cache blocks, and `CDXMeshVB` data. |
| `0x004b31f0 CMeshPart__OptimizePolygons` | Uses `0.2`/`0.3` thresholds, neighborhood/normal comparison, triangle-index rewrite, and removed vertices/polys reporting. |
| `0x004b3b70 CMeshPart__Clone` | Duplicates transform/bounds/material/name/link metadata, arrays, and geometry data into a `0x13c` clone and remaps triangle DVertex pointers. |
| `0x004b4250 CMeshPart__Merge` | Merges source geometry, builds/interpolates pose transforms, transforms source vertices, remaps triangle pointers, and updates counts/pointers. |
| `0x004bae70 CMeshPart__CanOptimizePart_Strict` / `0x004bb040 CMeshPart__CanMergeInOptimizePass` | Optimization predicates preserving wheel/body/axle, buggy `CORE`/`x1`, turret/barrel, door, mech, tentacle, and barrel-spinner protection evidence. |

Evidence anchors:

- Debug path `[maintainer-local-source-export-root]\MeshPart.cpp`.
- Source-reference size token `resfile_cmeshpartsize`.
- Observed serialized record size `0x13c`.
- Wave1100 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

## Collision Bridge Contract

Wave1098 ties primitive line/cylinder/sphere forwarders and geometry helpers to MeshCollisionVolume swept-sphere and line-query paths.

| Address | Static contract |
| --- | --- |
| `0x004059a0 CCylinder__VFunc_01_004059a0` | CCylinder vtable forwarder to delegate vfunc `+0x8`. |
| `0x004098c0 CLine__VFunc_01_004098c0` | CLine vtable forwarder to delegate vfunc `+0x10`. |
| `0x00426320 CSphere__VFunc_01_00426320` | Sphere-adjacent forwarder to delegate vfunc `+0x0c`. |
| `0x0043fe20 CCylinder__ResolveCollisionVFunc02` | Cylinder collision resolver reached by sphere-as-cylinder proxy path. |
| `0x004e4d70 CSphere__VFunc02_ResolveCollisionAsCylinder` | Sphere/cylinder bridge before cylinder collision resolver. |
| `0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50` | MeshCollisionVolume slot `2`; builds local sphere-style record and dispatches through the collision-volume table. |
| `0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds` | Swept-sphere bounds test with the 8-triangle/24-entry direction-pointer table caveat preserved. |
| `0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart` | Iterates mesh-part triangle candidates and calls swept-sphere triangle core. |
| `0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore` | Triangle core using `Geometry__RaySphereEntryDistance` and closest-edge fallback before writing contact state. |
| `0x00478c20 Geometry__IntersectSegmentTriangleAndStoreHit` | Segment-triangle helper used by MeshCollisionVolume line-query vfunc. |
| `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830` | MeshCollisionVolume slot `4`; scans line-triangle buckets and calls segment-triangle hit helper. |

Evidence anchors:

- Wave1098 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified`.
- Hidden ABI caveat remains for `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord`.

## Asset Bridge Counts

The contract is grounded in the current public-safe asset/resource count posture from the baseline static reviews and extraction docs. These counts prove extraction/catalog coverage, not runtime render correctness.

| Asset signal | Current evidence |
| --- | ---: |
| PC resource archives | `301` |
| `goodie_*_res_PC.aya` archives | `232` |
| Loose textures exported | `847/847` |
| Loose meshes exported | `213/213` |
| Embedded packed mesh bodies exported | `139/139` |
| Packed `TEXT` refs resolved | `601/601` |
| Packed reference `MESH` refs resolved | `209/209` |
| `GDIE` texture refs resolved | `206/206` |
| `GDIE` mesh refs resolved | `42/42` |
| Model rows with material/texture-binding metadata | `352/352` |
| Model texture sidecar refs covered | `213/213` |

## Claim Boundaries

This contract proves static coherence across saved Ghidra names, signatures, comments, tags, xrefs, instructions, decompile rows, per-wave probes/readiness notes, and public-safe asset-count evidence. It does not prove these separate domains:

- Runtime texture decode pixels or GPU upload results.
- Runtime mesh loading, skinning, collision, culling, render, particle, water, or optimization behavior.
- Exact `CEngine`, `CDXEngine`, `D3DStateCache`, `CRenderQueue`, `CMesh`, `CMeshPart`, `CMeshCollisionVolume`, vertex, material, texture, matrix, primitive, contact, or Direct3D object layouts.
- Exact source-body identity.
- Native textured/animated WinUI rendering.
- In-game render correctness, animation behavior, material visual parity, camera/render-state fidelity, or collision/trace correctness.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Use this document as a static map for the next parser/schema/rebuild planning steps. Runtime probes, visual QA, gameplay validation, and clean-room rebuild parity remain later lanes after static contracts are explicit enough to test.

## Evidence Paths

- `reverse-engineering/binary-analysis/texture-render-static-review-2026-05-26.md`
- `reverse-engineering/binary-analysis/mesh-motion-world-particle-static-review-2026-05-26.md`
- `release/readiness/ghidra_cengine_core_bootstrap_review_wave1093_2026-06-04.md`
- `release/readiness/ghidra_cdxengine_frame_render_spine_review_wave1094_2026-06-04.md`
- `release/readiness/ghidra_render_state_matrix_support_review_wave1095_2026-06-04.md`
- `release/readiness/ghidra_crenderqueue_core_multipass_review_wave1096_2026-06-04.md`
- `release/readiness/ghidra_primitive_collision_bridge_review_wave1098_2026-06-04.md`
- `release/readiness/ghidra_cmesh_resource_registry_review_wave1099_2026-06-04.md`
- `release/readiness/ghidra_cmeshpart_load_geometry_review_wave1100_2026-06-04.md`
