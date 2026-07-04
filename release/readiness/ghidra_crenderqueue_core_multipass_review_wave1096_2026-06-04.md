# Ghidra CRenderQueue Core Multipass Review Wave1096 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-04
Scope: `crenderqueue-core-multipass-review-wave1096`

Wave1096 re-read seventeen saved `CRenderQueue` core, bucket, lifecycle, view-vector, depth-list, render-all, multipass, projected-sprite, and `CVBufTexture` handoff rows as a focused post-100 static system review. The pass was read-only: no Ghidra names, signatures, comments, tags, function boundaries, or executable bytes were changed; BEA was not launched; no installed-game/runtime file was mutated.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005515a0 CDXEngine__InitConsoleVar_UseRenderQueue` | Xrefs from `CGame__Init` and `CGame__InitRestartLoop`; initializes `cg_userenderqueue` console storage. |
| `0x005515e0 CRenderQueueBucket__RenderAndRecycle` | Called by `CRenderQueue__BeginFrame`; walks bucket-linked render items, updates cached render state/matrix fields, draws indexed primitives, frees consumed items, and clears the bucket head. |
| `0x00551920 CRenderQueue__BeginFrame` | Two xrefs from `CDXEngine__Render`; seeds default render-queue/world-matrix state, calls `CRenderQueueBucket__RenderAndRecycle`, then restores sampler/render states. |
| `0x00551f20 CRenderQueue__ctor` / `0x00551fe0 CRenderQueue__dtor` | Constructor/destructor manage `DeviceObject` plus active-reader arrays at `this+0x0c` and `this+0x10c`. |
| `0x00552410 CRenderQueue__ResetOrCreateField6C0Resource` / `0x00552470 CRenderQueue__ReleaseField6C0Resource` | Vtable-resource helpers for field `this+0x6c0`, with DATA/vtable context from prior Wave872. |
| `0x005524a0 CRenderQueue__UpdateViewVectorAndMatrix` | Xref from `CEngine__SetupLights`; updates render-queue view-vector fields and copies a matrix block with 100.0 scale constants. |
| `0x005526c0 CRenderQueue__InsertSortedByDepth` | Xrefs from `CVBufTexture__RenderDynamicUnitPass` and `CRenderQueue__InsertIfDepthBelowIndexedLimit`; maintains depth-sorted active-reader slots. |
| `0x00552740 CRenderQueue__RecycleInactiveItems` / `0x00552800 CRenderQueue__MergePendingItems` | Called by `CRenderQueue__RenderAll`; maintain active/free/pending reader entries and frame-age state. |
| `0x005528b0 CRenderQueue__RenderAll` | Xref from `CDXEngine__Render`; computes frame delta, recycles/merges entries, emits immediate triangle strips via `CFastVB`, restores render state, and resets global tint. |
| `0x00553960 CRenderQueue__RenderMultipassLayerA` / `0x00554170 CRenderQueue__RenderMultipassLayerB` | Xrefs from `CDXEngine__Render`; multipass terrain/material layers using global queue receiver `0x009c7550`. |
| `0x005545d0 CRenderQueue__BuildProjectedSprites` / `0x00554750 CRenderQueue__EmitBillboardStrip` | Xrefs from `CVBufTexture__RenderDynamicUnitPass` and projected-sprite builder; sample static-shadow height and write vertices/indices through `CVBufTexture`. |
| `0x00554df0 CRenderQueue__RenderVBufTextureWithStateToggle` | Xref from `CDXEngine__Render`; toggles state around `CVBufTexture__Render(*(this+0x5b8), reset_after_render=1)`. |

Read-back evidence:

- Fresh exports verified `17` metadata rows, `17` tag rows, `22` xref rows, `3087` instruction rows, and `17` decompile rows.
- Export logs reported `targets=17 found=17 missing=0`, `rows=17 missing=0`, `Wrote 22 rows`, `Wrote 3087 function-body instruction rows`, and `targets=17 dumped=17 missing=0 failed=0`.
- Static function-quality closure remains `6410/6410 = 100.00%`, expanded static surface remains `1560/1560 = 100.00%`, Wave911 focused progress remains `812/1408 = 57.67%`, and Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-174618_post_wave1096_crenderqueue_core_multipass_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

What this proves:

- The seventeen target function rows exist in the saved Ghidra project with saved names, signatures, comments, and tags.
- The observed bodies and caller relationships are static retail Ghidra metadata/tag/xref/instruction/decompile evidence for the `CRenderQueue` core and multipass handoff surface.
- This wave connects the Wave1094 `CDXEngine__Render` frame spine and Wave1095 render-state/matrix support surface to queue-owned frame, depth, multipass, projected-sprite, and `CVBufTexture` handoff helpers.

What remains unproven:

- Runtime render output or visual ordering.
- Exact `CRenderQueue`, bucket, entry, material, active-reader, `CVBufTexture`, or D3D resource layouts.
- Exact Direct3D enum names or vtable method semantics beyond observed constants/callers.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1096; crenderqueue-core-multipass-review-wave1096; 0x005515a0 CDXEngine__InitConsoleVar_UseRenderQueue; 0x005515e0 CRenderQueueBucket__RenderAndRecycle; 0x00551920 CRenderQueue__BeginFrame; 0x005528b0 CRenderQueue__RenderAll; 0x00553960 CRenderQueue__RenderMultipassLayerA; 0x00554170 CRenderQueue__RenderMultipassLayerB; 0x005545d0 CRenderQueue__BuildProjectedSprites; 0x00554750 CRenderQueue__EmitBillboardStrip; 0x00554df0 CRenderQueue__RenderVBufTextureWithStateToggle; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-174618_post_wave1096_crenderqueue_core_multipass_review_verified; read-only review.
