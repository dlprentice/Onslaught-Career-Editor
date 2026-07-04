# Ghidra HUD Render-Body Review Wave1004 Readiness Note

Status: complete read-only static read-back evidence; no mutation
Date: 2026-05-31
Scope: `hud-render-body-review-wave1004`

Wave1004 re-reviewed the HUD render-body continuum that follows the Wave1003 HUD head/render-state boundary recovery. Fresh read-only exports covered the prior Wave410, Wave411, Wave412, Wave789, Wave923, and Wave990 HUD overlay/render rows from `0x00482590 CHud__RenderTargetIndicatorOverlay` through `0x004881e0 CHud__ResolveOverlaySlotRenderMode`, with `0x0053ecc0 CDXEngine__PostRender` and compass/viewpoint/HUD-state context. The saved project state remained coherent, so the wave made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Read-back evidence |
| --- | --- |
| `0x004879e0 CHud__RenderOverlayForViewpoint` | Dispatches `CHud__RenderWorldTargetSprites`, `CHud__RenderTargetIndicatorOverlay`, `CHud__RenderControllerSlotStatusPanel`, `CHud__RenderTargetMarkers3D`, `CHud__RenderObjectiveProgressGaugeAndHeadingNeedle`, `CHud__RenderObjectiveStatusPanel`, `CHud__RenderObjectiveSlotFillPanel`, and `CHud__RenderTacticalRadarContacts`. |
| `0x00484c50 CHud__RenderTacticalRadarContacts` | Calls `0x004857e0 HudOverlay__DrawSpriteQuad` seven times and `0x00485830 CHud__SelectMarkerTextureIndexByUnitFlags` four times in the saved xref export. |
| `0x00487bc0 CHud__RenderOverlay` | Called by `0x0053ecc0 CDXEngine__PostRender` at `0x0053ed01`, matching the HUD overlay post-render position. |
| `0x00487d10 CHud__RenderBattleline` | Called by `0x0053ecc0 CDXEngine__PostRender` at `0x0053ed79`; prior Wave412/Wave923/Wave990 battleline evidence remains coherent. |
| `0x00488090 CHud__RenderActiveHudComponentPass` | Called by `0x0053ecc0 CDXEngine__PostRender` at `0x0053ef26`; the active HUD component pass remains distinct from the overlay dispatcher and battleline path. |
| `0x004881e0 CHud__ResolveOverlaySlotRenderMode` | Reached by `CDXCompass__RenderWorldSpaceOverlay`, `CDXCompass__UpdateDynamicOverlayTexture`, and `CDXCompass__Render`, preserving the HUD slot-index render-mode role. |

Fresh read-back evidence:

- Target exports: `15` metadata rows, `15` tag rows, `30` xref rows, `6350` body-instruction rows, and `15` decompile rows.
- Context exports: `7` metadata rows and `7` decompile rows for `0x0053ecc0 CDXEngine__PostRender`, `0x00482050 CHud__PromotePendingHudComponent`, `0x00482090 HudRenderState__ApplyOverlaySpriteState`, `0x0044a0d0 CEngine__SelectViewpoint`, `0x0053cd30 CDXCompass__RenderWorldSpaceOverlay`, `0x0053c510 CDXCompass__UpdateDynamicOverlayTexture`, and `0x00427210 CDXCompass__Render`.
- Logs reported `targets=15 found=15 missing=0`, `rows=15 missing=0`, `Wrote 30 rows`, `Wrote 6350 function-body instruction rows`, `targets=15 dumped=15 missing=0 failed=0`, `targets=7 found=7 missing=0`, and `targets=7 dumped=7 missing=0 failed=0`, with `REPORT: Save succeeded`.
- Queue closure remains `6223/6223 = 100.00%`, with `0` commentless functions, `0` exact-`undefined` signatures, and `0` `param_N` signatures.
- Wave911 focused re-audit progress advanced to `485/1408 = 34.45%`.
- Expanded static surface progress advanced to `654/1478 = 44.25%`.
- Wave911 top-500 risk-ranked coverage advanced to `380/500 = 76.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-124610_post_wave1004_hud_render_body_review_verified`, `19` files, `173869959` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave1004; `hud-render-body-review-wave1004`; `0x00482590 CHud__RenderTargetIndicatorOverlay`; `0x00484c50 CHud__RenderTacticalRadarContacts`; `0x004857e0 HudOverlay__DrawSpriteQuad`; `0x004879e0 CHud__RenderOverlayForViewpoint`; `0x00487bc0 CHud__RenderOverlay`; `0x00487d10 CHud__RenderBattleline`; `0x00488090 CHud__RenderActiveHudComponentPass`; `0x004881e0 CHud__ResolveOverlaySlotRenderMode`; `0x0053ecc0 CDXEngine__PostRender`; `485/1408 = 34.45%`; `654/1478 = 44.25%`; `380/500 = 76.00%`; `6223/6223 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260531-124610_post_wave1004_hud_render_body_review_verified`; no mutation.

What this proves:

- The selected HUD render-body rows exist in the saved Ghidra project with the expected names, signatures, comments, and static-readback tags from the earlier correction waves.
- The current decompile and xref exports preserve the post-render call spine from `CDXEngine__PostRender` into HUD overlay, battleline, active component pass, and pending component promotion.
- The per-viewpoint overlay dispatcher still reaches the previously corrected target, controller-slot, 3D marker, objective, slot-fill, world-target, tactical-radar, sprite, and marker-selector rows.

What remains unproven:

- Exact source-body identity.
- Concrete `CHud`, `CDXEngine`, `CDXCompass`, `CDXBattleLine`, texture, component, and viewport layouts.
- Runtime HUD behavior.
- Runtime render ordering or visible HUD output.
- BEA patching behavior.
- Rebuild parity.
