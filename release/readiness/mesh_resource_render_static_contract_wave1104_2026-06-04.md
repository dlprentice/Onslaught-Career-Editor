# Mesh / Resource / Render Static Contract Wave1104 Readiness Note

Status: complete static documentation/probe consolidation
Date: 2026-06-04
Scope: `mesh-resource-render-static-contract-wave1104`

Wave1104 consolidated the saved mesh/resource/render Ghidra and asset-count evidence into `reverse-engineering/binary-analysis/mesh-resource-render-static-contract.md` and added a focused probe for the contract/mirror/index/package wiring. This wave made no Ghidra mutation, no executable-byte change, no BEA launch, and no installed-game or runtime-file mutation.

Static contract anchors:

| Area | Evidence |
| --- | --- |
| Baseline texture/render | Wave904 `texture-render-static-review-wave904`, including `CDXTexture__LoadTextureFromFile_Core`, `CDXTexture__DecodeMemoryToTextureObject`, `CFastVB__RenderTriangleStripImmediate`, `CVBufTexture__DrawSpriteEx`, `CRenderQueue__RenderMultipassLayerA`, and `CMeshRenderer__RenderMesh`. |
| Baseline mesh/world/particle | Wave905 `mesh-motion-world-particle-static-review-wave905`, including `CThing__InitRenderThingFromInitMeshName`, `CMesh__LoadByNameWithStatus`, `CMeshPart__PopulatePoseCacheRecursive`, `CWorld__InitOccupancyBitplanes`, and `CParticleSet__LoadFromArchive`. |
| Engine/frame render | Wave1093/1094 rows `0x004499d0 CEngine__Init`, `0x00449dc0 CEngine__LoadAllNamedMeshes`, `0x0046e460 CGame__Render`, `0x0053e220 CDXEngine__PreRender`, `0x0053e2e0 CDXEngine__Render`, and `0x0053ecc0 CDXEngine__PostRender`. |
| Render-state/queue | Wave1095/1096 rows `0x00513af0 D3DStateCache__SetSlotMode4or5`, `0x00551920 CRenderQueue__BeginFrame`, `0x005528b0 CRenderQueue__RenderAll`, `0x00553960 CRenderQueue__RenderMultipassLayerA`, and `0x00554df0 CRenderQueue__RenderVBufTextureWithStateToggle`. |
| Mesh registry/load | Wave1099 rows `0x004a5020 CMesh__Init`, `0x004a5970 CMesh__LoadByNameWithStatus`, `0x004a5b70 CMesh__Load`, `0x004aa6e0 CMesh__FindOrCreate`, `0x004aab90 CMesh__Deserialize`, `DAT_00704ad8`, `DAT_00704adc`, `data\Meshes`, and `data\resources\meshes\m_%s.aya`. |
| CMeshPart geometry | Wave1100 rows `0x004ae860 CMeshPart__AllocateGeometry`, `0x004af470 CMeshPart__LoadVerticesAndTriangles`, `0x004afbb0 CMeshPart__LoadVerticesWithBones`, `0x004b27a0 CMeshPart__LoadFromStream`, `0x004b31f0 CMeshPart__OptimizePolygons`, `resfile_cmeshpartsize`, and `0x13c`. |
| Collision bridge | Wave1098 rows `0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart`, `0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`, and `0x00478c20 Geometry__IntersectSegmentTriangleAndStoreHit`. |
| Asset counts | `847/847` loose textures, `213/213` loose meshes, `139/139` embedded packed mesh bodies, `352/352` model material/texture-binding rows, and `213/213` model texture sidecar refs. |

Read-back sources:

- Wave904 backup: `G:\GhidraBackups\BEA_20260526-101300_post_wave904_texture_render_static_review_verified`.
- Wave905 backup: `G:\GhidraBackups\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`.
- Wave1093 backup: `G:\GhidraBackups\BEA_20260604-155838_post_wave1093_cengine_core_bootstrap_review_verified`.
- Wave1094 backup: `G:\GhidraBackups\BEA_20260604-163255_post_wave1094_cdxengine_frame_render_spine_review_verified`.
- Wave1095 backup: `G:\GhidraBackups\BEA_20260604-171413_post_wave1095_render_state_matrix_support_review_verified`.
- Wave1096 backup: `G:\GhidraBackups\BEA_20260604-174618_post_wave1096_crenderqueue_core_multipass_review_verified`.
- Wave1098 backup: `G:\GhidraBackups\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified`.
- Wave1099 backup: `G:\GhidraBackups\BEA_20260604-193549_post_wave1099_cmesh_resource_registry_review_verified`.
- Latest completed Ghidra review backup remains Wave1100: `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Current dashboard context: static Ghidra function-quality closure `6410/6410 = 100.00%`; commentless / exact-undefined / `param_N` debt `0 / 0 / 0`; expanded post-100 static surface `1560/1560 = 100.00%`; Wave911 focused `812/1408 = 57.67%`; Wave911 top-500 `500/500 = 100.00%`.

What this proves:

- The mesh/resource/render evidence is now consolidated as a single static contract.
- The contract is linked from the binary-analysis indexes and mapped-system docs.
- The mirror and package-script wiring are machine-checked by `tools/mesh_resource_render_static_contract_probe.py`.

What remains unproven:

- Runtime texture decode pixels or GPU upload results.
- Runtime mesh loading, skinning, collision, culling, render, particle, water, or optimization behavior.
- Exact object layouts.
- Exact source-body identity.
- Native textured/animated WinUI rendering.
- In-game render correctness or visual parity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.
