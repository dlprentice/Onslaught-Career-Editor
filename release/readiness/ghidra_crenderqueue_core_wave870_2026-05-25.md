# Ghidra CRenderQueue Core Wave870 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `crenderqueue-core-wave870`

Wave870 CRenderQueue core saved comments and tags for 13 renderer queue helpers from `0x005515a0 CDXEngine__InitConsoleVar_UseRenderQueue` through `0x005528b0 CRenderQueue__RenderAll`. Existing clean signatures were reviewed and left unchanged. The pass made no renames, no function-boundary changes, and no executable-byte changes.

These rows are important renderer infrastructure, not low-importance filler. The local evidence density varies by helper, but the tranche connects game init, CDXEngine render, queued dynamic-unit insertion, active-reader lifetime, state-cache restoration, static-shadow sampling, and immediate fast-vertex-buffer draw output.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005515a0 CDXEngine__InitConsoleVar_UseRenderQueue` | Registers `cg_userenderqueue` / `Use the render queue`; xrefs from `CGame__Init` and `CGame__InitRestartLoop`. |
| `0x005515e0 CRenderQueueBucket__RenderAndRecycle` | Walks bucket items, updates cached shader/texture/render/matrix state, calls `CEngine__DrawIndexedPrimitives`, frees consumed items, and clears the bucket head. |
| `0x00551920 CRenderQueue__BeginFrame` | Called twice from `CDXEngine__Render`; seeds default queue/world-matrix state, calls `CRenderQueueBucket__RenderAndRecycle`, then restores sampler/render states. |
| `0x00551f20 CRenderQueue__ctor` / `0x00551fe0 CRenderQueue__dtor` | Vector-constructs/destructs active-reader arrays at `this+0x0c` and `this+0x10c` and wraps the `DeviceObject` base lifetime. |
| `0x005526c0 CRenderQueue__InsertSortedByDepth` | Inserts an item into the sorted depth array when `DAT_0089d680` is clear; xrefs from `CVBufTexture__RenderDynamicUnitPass` and `CRenderQueue__InsertIfDepthBelowIndexedLimit`. |
| `0x00552740 CRenderQueue__RecycleInactiveItems` / `0x00552800 CRenderQueue__MergePendingItems` | Maintain the active/free/pending reader lists and frame-age state used by the render pass. |
| `0x005528b0 CRenderQueue__RenderAll` | Top-level queue render pass: computes frame delta, recycles/merges active entries, samples static-shadow height, drives D3D vtable calls, emits immediate triangle strips through `CFastVB__LockAligned` / `CFastVB__RenderTriangleStripImmediate`, restores render state, and resets global tint with `CDXEngine__SetGlobalTintColorOpaque(0xe7)`. |

Read-back evidence:

- `ApplyCRenderQueueCoreWave870.java dry`: `updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=13 missing=0 bad=0`
- `ApplyCRenderQueueCoreWave870.java apply`: `updated=13 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=13 missing=0 bad=0`
- `ApplyCRenderQueueCoreWave870.java final dry`: `updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 13 metadata rows, 13 tag rows, 29 xref rows, 1594 instruction rows, 13 decompile rows, and 757 xref-site instruction rows.
- Queue after Wave870: 6105 total, 5851 commented, 254 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5851/6105 = 95.84%`, strict clean-signature proxy `5851/6105 = 95.84%`.
- Next raw commentless row: `0x00551c90 CScreenFx__InitZoomEffectCvar`.
- Verified backup: `G:\GhidraBackups\BEA_20260525-180844_post_wave870_crenderqueue_core_verified`, 19 files, 172460935 bytes, `DiffCount=0`.

What this proves:

- The 13 target function rows exist in the saved Ghidra project.
- The saved comments and tags include `crenderqueue-core-wave870` and `wave870-readback-verified`.
- The existing clean signatures remain stable after dry/apply/final-dry read-back.
- The observed queue behavior is static retail Ghidra metadata/decompile/xref/instruction evidence.

What remains unproven:

- Exact CRenderQueue/entry/bucket/active-reader concrete layouts.
- Exact Direct3D vtable and render-state enum semantics beyond observed slots/constants.
- Runtime visual behavior.
- Runtime queue toggle behavior.
- BEA patching behavior.
- Rebuild parity.
