# Ghidra Wave900+ Through Wave1094 Recheck Note

Status: aggregate validation passed
Date: 2026-06-04
Scope: `wave900-plus-through-wave1094-recheck`

This note extends the post-Wave900 recheck chain through Wave1094. The intended local validation gate is:

```powershell
npm run test:ghidra-wave900-plus-through-wave1094-recheck
```

Wave1094 (`cdxengine-frame-render-spine-review-wave1094`) reviewed the CDXEngine frame/render spine and saved comment/tag normalization for `0x0053e220 CDXEngine__PreRender`, `0x0053e2e0 CDXEngine__Render`, `0x0053ecc0 CDXEngine__PostRender`, and `0x0046e460 CGame__Render`. The focused readiness note is [`ghidra_cdxengine_frame_render_spine_review_wave1094_2026-06-04.md`](ghidra_cdxengine_frame_render_spine_review_wave1094_2026-06-04.md).

Coverage anchors:

- Static function-quality closure remains `6410/6410 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress remains `1560/1560 = 100.00%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Representative rows include `0x0053e220 CDXEngine__PreRender`, `0x0053e2e0 CDXEngine__Render`, `0x0053ecc0 CDXEngine__PostRender`, `0x0046e460 CGame__Render`, `0x0053bb50 CDXEngine__RenderOptionalFullscreenEffectPass`, `0x005441b0 CDXEngine__RenderKempyCubeFaces`, `0x0054f7e0 CDXEngine__RenderParticleTexturePass`, and `0x00542a50 CDXEngine__BuildDirectionalSampleRing`.
- Render-queue context includes `0x00551920 CRenderQueue__BeginFrame`, `0x005528b0 CRenderQueue__RenderAll`, `0x00553960 CRenderQueue__RenderMultipassLayerA`, and `0x00554170 CRenderQueue__RenderMultipassLayerB`.
- Verified backup: `G:\GhidraBackups\BEA_20260604-163255_post_wave1094_cdxengine_frame_render_spine_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Runtime frame timing/device/render output, exact CGame/CDXEngine/CEngine/render-queue/water/particle/Kempy/overlay layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Validation result:

- `npm run test:ghidra-wave900-plus-through-wave1094-recheck`: PASS.
- Focused Wave1094 probe: PASS.
- Readiness notes: `197`.
- Covered waves: `195`.
- Package probe scripts: `193`.
- Evidence bases: `193`.
- Backup references: `195`.
- Apply scripts: `71`.
- Wave982-Wave1094 direct probes: `resultCount=113`, `passCount=1`, `failCount=112`, `disallowedFailureCount=0`.
- Current queue: `6410` total, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status `PASS`.

Probe token anchor: Wave1094; cdxengine-frame-render-spine-review-wave1094; 0x0053e220 CDXEngine__PreRender; 0x0053e2e0 CDXEngine__Render; 0x0053ecc0 CDXEngine__PostRender; 0x0046e460 CGame__Render; 0x0053bb50 CDXEngine__RenderOptionalFullscreenEffectPass; 0x005441b0 CDXEngine__RenderKempyCubeFaces; 0x0054f7e0 CDXEngine__RenderParticleTexturePass; 0x00542a50 CDXEngine__BuildDirectionalSampleRing; 0x00551920 CRenderQueue__BeginFrame; 0x005528b0 CRenderQueue__RenderAll; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-163255_post_wave1094_cdxengine_frame_render_spine_review_verified; comment/tag normalization.
