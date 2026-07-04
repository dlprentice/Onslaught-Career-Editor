# Ghidra CDXEngine Frame Render Spine Review Wave1094 Readiness Note

Status: complete static read-back and comment/tag normalization evidence
Date: 2026-06-04
Scope: `cdxengine-frame-render-spine-review-wave1094`

Wave1094 reviewed the CDXEngine frame/render spine that bridges `CGame__Render` into per-frame pre-render, per-view render, and post-render/overlay paths. The pass saved comment/tag normalization for four already existing function objects and made no renames, no signature changes, no function-boundary changes, no executable-byte changes, no BEA launch, and no installed-game/runtime-file mutation.

Normalized rows:

| Address | Evidence |
| --- | --- |
| `0x0053e220 CDXEngine__PreRender` | `CGame__Render` callsite `0x0046e5c3`; prepares per-frame engine/viewpoint state before the per-view render loop. |
| `0x0053e2e0 CDXEngine__Render` | `CGame__Render` callsites `0x0046e68b`, `0x0046e747`, `0x0046e785`, `0x0046e7d8`, and `0x0046e883`; drives per-view world rendering. |
| `0x0053ecc0 CDXEngine__PostRender` | `CGame__Render` callsite `0x0046e892`; reaches HUD/viewpoint overlays and `0x00487d10 CHud__RenderBattleline` through callsite `0x0053ed79`. |
| `0x0046e460 CGame__Render` | `CGame__MainLoop` callsite `0x0046f151`; coordinates split-screen/fullscreen viewport setup, `CEngine__SetViewpoint`, `CDXEngine__PreRender`, repeated `CDXEngine__Render`, and `CDXEngine__PostRender`. |

Representative render-spine context:

| Address | Evidence |
| --- | --- |
| `0x0053bb50 CDXEngine__RenderOptionalFullscreenEffectPass` | Called from `CDXEngine__Render` at `0x0053ec6a`. |
| `0x005441b0 CDXEngine__RenderKempyCubeFaces` | Called from `CDXEngine__Render` at `0x0053e629`. |
| `0x0054f7e0 CDXEngine__RenderParticleTexturePass` | Called from `CDXEngine__Render` at `0x0053ebe3`. |
| `0x00542a50 CDXEngine__BuildDirectionalSampleRing` | Called from `CDXEngine__Render` at `0x0053e5ae`. |
| `0x00441490 CDXEngine__UpdateWrappedThingPositionsAndDistance` | Called from `CDXEngine__Render` at `0x0053e56c`. |
| `0x004905f0 CDXEngine__UpdateOverlaySlotsFromCandidateList` | Called from `CDXEngine__Render` at `0x0053e5c0`; calls `0x004903a0 CDXEngine__BuildOverlaySlotFromSortedEntry`. |
| `0x00551920 CRenderQueue__BeginFrame` | Called from `CDXEngine__Render` at `0x0053e8cd` and `0x0053ec74`. |
| `0x005528b0 CRenderQueue__RenderAll` | Called from `CDXEngine__Render` at `0x0053e503`. |
| `0x00553960 CRenderQueue__RenderMultipassLayerA` | Called from `CDXEngine__Render` at `0x0053e692`. |
| `0x00554170 CRenderQueue__RenderMultipassLayerB` | Called from `CDXEngine__Render` at `0x0053e6af`. |
| `0x0055b6c0 CWaterRenderSystem__RenderMainPass` | Called twice from `CDXEngine__Render` at `0x0053e6f1` and `0x0053e803`. |

Read-back evidence:

- `ApplyCDXEngineFrameRenderSpineReviewWave1094.java` dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0`
- `ApplyCDXEngineFrameRenderSpineReviewWave1094.java` apply: `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0`, with `REPORT: Save succeeded`
- `ApplyCDXEngineFrameRenderSpineReviewWave1094.java` final dry: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Pre/post primary exports: `12` metadata rows, `12` tag rows, `17` xref rows, `2340` instruction rows, and `12` decompile rows.
- Pre/post context exports: `17` metadata rows, `17` tag rows, `36` xref rows, `5415` instruction rows, and `17` decompile rows.
- Queue closure remains `6410/6410 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, and `0` `param_N`.
- Expanded static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 risk-ranked remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-163255_post_wave1094_cdxengine_frame_render_spine_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

What this proves:

- The four normalized target function rows exist in the saved Ghidra project with their pre-existing names and signatures intact.
- The saved comments and tags include `cdxengine-frame-render-spine-review-wave1094`, `wave1094-readback-verified`, `comment-hardened`, and `tag-normalized`.
- The observed frame/render spine is static retail Ghidra evidence tied to metadata, tags, xrefs, instructions, decompile exports, apply logs, and a verified project backup.

What remains unproven:

- Runtime frame timing/device/render output.
- Exact `CGame`, `CDXEngine`, `CEngine`, `CViewport`, `CHud`, render-queue, water, particle, Kempy, and overlay layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1094; cdxengine-frame-render-spine-review-wave1094; 0x0053e220 CDXEngine__PreRender; 0x0053e2e0 CDXEngine__Render; 0x0053ecc0 CDXEngine__PostRender; 0x0046e460 CGame__Render; 0x0053bb50 CDXEngine__RenderOptionalFullscreenEffectPass; 0x005441b0 CDXEngine__RenderKempyCubeFaces; 0x0054f7e0 CDXEngine__RenderParticleTexturePass; 0x00542a50 CDXEngine__BuildDirectionalSampleRing; 0x00551920 CRenderQueue__BeginFrame; 0x005528b0 CRenderQueue__RenderAll; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-163255_post_wave1094_cdxengine_frame_render_spine_review_verified; comment/tag normalization.
