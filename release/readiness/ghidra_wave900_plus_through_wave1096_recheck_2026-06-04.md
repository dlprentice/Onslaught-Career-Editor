# Ghidra Wave900+ Through Wave1096 Recheck Note

Status: aggregate validation passed
Date: 2026-06-04
Scope: `wave900-plus-through-wave1096-recheck`

This note extends the post-Wave900 recheck chain through Wave1096. The intended local validation gate is:

```powershell
npm run test:ghidra-wave900-plus-through-wave1096-recheck
```

Wave1096 (`crenderqueue-core-multipass-review-wave1096`) re-read seventeen saved `CRenderQueue` core, bucket, lifecycle, view-vector, depth-list, render-all, multipass, projected-sprite, and `CVBufTexture` handoff rows with no Ghidra mutation. The focused readiness note is [`ghidra_crenderqueue_core_multipass_review_wave1096_2026-06-04.md`](ghidra_crenderqueue_core_multipass_review_wave1096_2026-06-04.md).

Coverage anchors:

- Static function-quality closure remains `6410/6410 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress remains `1560/1560 = 100.00%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Representative rows include `0x005515a0 CDXEngine__InitConsoleVar_UseRenderQueue`, `0x005515e0 CRenderQueueBucket__RenderAndRecycle`, `0x00551920 CRenderQueue__BeginFrame`, `0x005528b0 CRenderQueue__RenderAll`, `0x00553960 CRenderQueue__RenderMultipassLayerA`, `0x00554170 CRenderQueue__RenderMultipassLayerB`, `0x005545d0 CRenderQueue__BuildProjectedSprites`, `0x00554750 CRenderQueue__EmitBillboardStrip`, and `0x00554df0 CRenderQueue__RenderVBufTextureWithStateToggle`.
- Fresh read-only exports verified `17` metadata rows, `17` tag rows, `22` xref rows, `3087` instruction rows, and `17` decompile rows.
- Caller context includes `CGame__Init`, `CGame__InitRestartLoop`, `CDXEngine__Render`, `CEngine__SetupLights`, `CVBufTexture__RenderDynamicUnitPass`, and `CRenderQueue__RenderAll`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-174618_post_wave1096_crenderqueue_core_multipass_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Runtime render output or visual ordering, exact `CRenderQueue` / bucket / entry / material / active-reader / `CVBufTexture` / D3D resource layouts, exact Direct3D enum names or vtable method semantics, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Validation result:

- `npm run test:ghidra-wave900-plus-through-wave1096-recheck`: PASS.
- Focused Wave1096 probe: PASS.
- Readiness notes: `199`.
- Covered waves: `197`.
- Package probe scripts: `195`.
- Evidence bases: `195`.
- Backup references: `197`.
- Apply scripts: `72`.
- Wave982-Wave1096 direct probes: `resultCount=115`, `passCount=1`, `failCount=114`, `disallowedFailureCount=0`.
- Current queue: `6410` total, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status `PASS`.

Probe token anchor: Wave1096; crenderqueue-core-multipass-review-wave1096; 0x005515a0 CDXEngine__InitConsoleVar_UseRenderQueue; 0x005515e0 CRenderQueueBucket__RenderAndRecycle; 0x00551920 CRenderQueue__BeginFrame; 0x005528b0 CRenderQueue__RenderAll; 0x00553960 CRenderQueue__RenderMultipassLayerA; 0x00554170 CRenderQueue__RenderMultipassLayerB; 0x005545d0 CRenderQueue__BuildProjectedSprites; 0x00554750 CRenderQueue__EmitBillboardStrip; 0x00554df0 CRenderQueue__RenderVBufTextureWithStateToggle; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-174618_post_wave1096_crenderqueue_core_multipass_review_verified; read-only review.
