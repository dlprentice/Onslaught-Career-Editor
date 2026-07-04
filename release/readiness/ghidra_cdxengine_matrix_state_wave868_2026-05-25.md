# Ghidra CDXEngine Matrix State Wave868 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cdxengine-matrix-state-wave868`

Wave868 CDXEngine matrix state saved comments and tags for five adjacent matrix/projection helpers from `0x005508a0 CDXEngine__ClearMatrixBlock` through `0x00550ca0 CDXEngine__SetWorldMatrixElements`. Existing clean signatures were reviewed and left unchanged. The pass made no renames, no function-boundary changes, and no executable-byte changes.

These rows are high-importance, low local-evidence-density renderer infrastructure. They sit under CDXEngine transform/cache initialization and fan out through world, HUD, frontend, mesh, landscape, water, tree, imposter, render-queue, debug-draw, and unit-shadow render paths.

Exact signature anchors: `void __fastcall CDXEngine__ClearMatrixBlock(void * dest)`, `void __fastcall CDXEngine__InitTransformCaches(void * this)`, `void __thiscall CDXEngine__SetProjectionMatrix(void * this, float near_z, float far_z, float viewport_w, float viewport_h)`, `void __thiscall CDXEngine__SetViewAndProjection(void * this, float * view_matrix, float * proj_matrix)`, and `void __thiscall CDXEngine__SetWorldMatrixElements(void * this, float m00, float m01, float m02, float m03, float m10, float m11, float m12, float m13, float m20, float m21, float m22, float m23, float m30, float m31, float m32, float m33)`.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005508a0 CDXEngine__ClearMatrixBlock` | Clears most dwords in an `0x58`-byte matrix/cache block while leaving `+0x10` and `+0x20` untouched; nearby global setup iterates eight `0x5c`-byte records from `0x009c65c0`. |
| `0x005508e0 CDXEngine__InitTransformCaches` | Initializes identity matrices at `this+0x354`, `this+0x394`, `this+0x3d4`, and `this+0x414`, fills the larger table beginning at `this+0x454`, and marks dirty/state bytes at `this+0xe28` through `this+0xe2e`. |
| `0x00550b10 CDXEngine__SetProjectionMatrix` | Builds a projection/depth matrix into `this+0x3d4`, marks `this+0xe2a`, and is called by CDXEngine render, HUD target overlay, compass overlay, frontend render, and FEPBEConfig projection setup. |
| `0x00550be0 CDXEngine__SetViewAndProjection` | Stages view/projection values, dispatches through the shared matrix helper visible as `CVertexShader__DispatchTableCall_656f78`, marks `this+0xe29`, and writes 16 floats to `this+0x394`. |
| `0x00550ca0 CDXEngine__SetWorldMatrixElements` | Writes the world transform to `this+0x354`, marks `this+0xe28`, and has broad xrefs from `CMeshRenderer__RenderMesh`, `CRenderQueue__BeginFrame`, `CRenderQueueBucket__RenderAndRecycle`, `CDXLandscape__Render`, `CDXTrees__Render`, `CWaterRenderSystem` passes, `CDXImposter__RenderAll`, HUD/compass overlays, debug draw, and unit shadow probes. |

Read-back evidence:

- `ApplyCDXEngineMatrixStateWave868.java dry`: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=5 missing=0 bad=0`
- `ApplyCDXEngineMatrixStateWave868.java apply`: `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=5 missing=0 bad=0`
- `ApplyCDXEngineMatrixStateWave868.java final dry`: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 5 metadata rows, 5 tag rows, 50 xref rows, 256 instruction rows, 5 decompile rows, and 1350 xref-site instruction rows.
- Queue after Wave868: 6105 total functions, 5828 commented, 277 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5828/6105 = 95.46%`, strict clean-signature proxy `5828/6105 = 95.46%`.
- Next raw commentless row: `0x00551200 CDXEngine__ApplyCachedLight`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-171842_post_wave868_cdxengine_matrix_state_verified`, 19 files, 172362631 bytes, `DiffCount=0`.

What this proves:

- The five target function rows exist in the saved Ghidra project.
- Existing signatures are clean and were preserved exactly.
- Saved comments and tags include `cdxengine-matrix-state-wave868`, `wave868-readback-verified`, and `important-connective-infrastructure`.
- The observed bodies and xrefs are static retail Ghidra evidence for CDXEngine matrix-state initialization and render transform/projection handoff.

What remains unproven:

- Exact CDXEngine field names and full layout.
- Exact row/column matrix convention.
- Exact camera/projection semantic naming beyond observed arithmetic and callers.
- Runtime rendering behavior.
- BEA patching behavior.
- Rebuild parity.
