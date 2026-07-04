# CDXEngine__PostRender

> Address: `0x0053ecc0` | Source: `references/Onslaught/DXEngine.cpp:1279`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int CDXEngine__PostRender(void *this, void *viewport)`)
- **Verified vs Source:** High confidence (`ENGINE.PostRender(&fullscreen)` callsite parity from `CGame__Render`)

## Purpose
Post-render overlay/UI stage:
- renders HUD/shared HUD
- renders message logs/briefing/pause overlays
- applies post-pass render-state cleanup
- performs end-of-frame UI/debug/front-end checks

## Notes
- Called once per rendered frame after per-view `CDXEngine__Render` calls.
- Closely matches the DXEngine post-render responsibilities in Stuart source.
- Wave410 read-back shows this function calls `CHud__RenderOverlay(&DAT_008aa4e8)` at the source-aligned `HUD.RenderOverlay();` point, then later calls `CHud__PromotePendingHudComponent(&DAT_008aa4e8)`. This is caller/static alignment only; runtime HUD behavior and concrete `CHud` layout remain unproven.
- Wave1013 (`hud-lifecycle-render-support-review-wave1013`) re-read `0x0053ecc0 CDXEngine__PostRender` as context for HUD lifecycle/render-support rows with no mutation. Fresh context exports preserved the post-render HUD/briefing path while target exports re-read `0x00481450 CHud__Init`, `0x004815c0 CHud__Reset`, `0x00481650 CHud__LoadTextures`, `0x00481af0 CHud__PostLoadProcess`, `0x00481f40 CHud__SetHudComponent`, `0x004821e0 CDXCompass__ApplyRenderStateAdditive`, `0x00488330 CIBuffer__CreateConfigured`, `0x004885e0 CIBuffer__LockDirect`, `0x0048f540 CLevelBriefingLog__ctor`, `0x0048f5a0 CLevelBriefingLog__scalar_deleting_dtor`, and `0x0048f5c0 CLevelBriefingLog__dtor`. Queue closure remains `6238/6238 = 100.00%`; Wave911 focused re-audit progress remains `505/1408 = 35.87%`; expanded static surface progress is `718/1493 = 48.09%`; Wave911 top-500 risk-ranked coverage is `420/500 = 84.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified`. Runtime HUD/render ordering/briefing-log/index-buffer behavior, exact source-body identity, concrete layouts, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1013; hud-lifecycle-render-support-review-wave1013; 0x00481450 CHud__Init; 0x004815c0 CHud__Reset; 0x00481650 CHud__LoadTextures; 0x00481af0 CHud__PostLoadProcess; 0x00481f40 CHud__SetHudComponent; 0x004821e0 CDXCompass__ApplyRenderStateAdditive; 0x00488330 CIBuffer__CreateConfigured; 0x004885e0 CIBuffer__LockDirect; 0x0048f540 CLevelBriefingLog__ctor; 0x0048f5a0 CLevelBriefingLog__scalar_deleting_dtor; 0x0048f5c0 CLevelBriefingLog__dtor; 505/1408 = 35.87%; 718/1493 = 48.09%; 420/500 = 84.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified; no mutation.
- Wave1004 (`hud-render-body-review-wave1004`) re-read the HUD render-body call spine with fresh context exports for `0x0053ecc0 CDXEngine__PostRender`. The context decompile preserves calls to `0x00487bc0 CHud__RenderOverlay`, `0x00487d10 CHud__RenderBattleline`, `0x00488090 CHud__RenderActiveHudComponentPass`, and `CHud__PromotePendingHudComponent`, while target exports preserve `0x00482590 CHud__RenderTargetIndicatorOverlay`, `0x00484c50 CHud__RenderTacticalRadarContacts`, `0x004857e0 HudOverlay__DrawSpriteQuad`, `0x004879e0 CHud__RenderOverlayForViewpoint`, and `0x004881e0 CHud__ResolveOverlaySlotRenderMode`. Wave1004 verified `15` metadata rows, `15` tag rows, `30` xref rows, `6350` body-instruction rows, `15` decompile rows, `7` context metadata rows, and `7` context decompile rows with no mutation. Queue closure remains `6223/6223 = 100.00%`; progress is `485/1408 = 34.45%`, `654/1478 = 44.25%`, and `380/500 = 76.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-124610_post_wave1004_hud_render_body_review_verified`. Runtime HUD behavior, runtime render ordering or visible HUD output, exact source-body identity, concrete `CHud`/`CDXEngine`/`CDXCompass`/`CDXBattleLine`/texture/component/viewport layouts, BEA patching, and rebuild parity remain separate proof.
