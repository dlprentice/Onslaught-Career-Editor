# Wave1141 CDXCompass/HUD Current-Risk Review

Wave1141 (`wave1141-cdxcompass-hud-current-risk-review`) re-read thirteen Wave1108 current-risk rows in the CDXCompass/HUD render-state current-risk cluster with fresh Ghidra metadata, tag, xref, instruction, context, and decompile exports.

This moves Wave1108 current focused accounting to `251/1179 = 21.29%`. Static closure remains `6411/6411 = 100.00%`; static debt remains `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`. Current risk candidates: `6166`; current focused candidates: `1178`; live regenerated current focused candidates: `1178`; remaining active focused work: `928`.

Probe token anchor: Wave1141; wave1141-cdxcompass-hud-current-risk-review; `251/1179 = 21.29%`; 13 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 928; current risk candidates: 6166; CDXCompass/HUD render-state current-risk cluster; fresh Ghidra export; read-only review; no mutation; `0 / 0 / 0`; `6411/6411 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260605-145724_post_wave1141_cdxcompass_hud_current_risk_review_verified`; `[maintainer-local-ghidra-backup-root]\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`.

## Primary Evidence

| Address | Name | Static evidence |
| --- | --- | --- |
| `0x0053bd60` | `CDXCompass__InitFields` | `CHud__Init` call xref `0x0048149a`; calls `CDXCompass__Reset`, clears two ring texture pairs at `this+0x3c00/+0x3c04` and `this+0x3f04/+0x3f08`, clears byte-sprite/dynamic slots, and returns `this`. |
| `0x0053be40` | `CDXCompass__Init` | `CDXCompass__InitMarkerArrays` call xref `0x00427106`; allocates/loads the byte sprite, clamps ring texture dimensions against GPU caps, allocates two ring texture pairs and two CVBuffers, then builds outer/inner ring geometry. |
| `0x0053c1d0` | `CDXCompass__BuildRingGeometry` | `CDXCompass__Init` call xrefs `0x0053c0f3` and `0x0053c18a`; fills a compass ring vertex strip from texture dimensions, segment count, thickness percent, and UV scale. |
| `0x00427110` | `CDXCompass__LoadTextures` | `CHud__LoadTextures` call xref `0x00481ad3`; loads ThreatFlash, DamageFlash, BarLine, and CompassObjectiveMarker texture references into compass slots. |
| `0x00427190` | `CDXCompass__DestroyTextures` | `CHud__ShutDown` call xref `0x00481b1a`; releases and clears the four compass texture references at `this+0x3ef4` through `this+0x3f00`. |
| `0x00427200` | `CDXCompass__Reset` | `CDXCompass__InitFields` call xref `0x0053bd63`; clears compass render/state flag `this+0x3c10`. |
| `0x004821b0` | `CDXCompass__ApplyRenderStateModulate` | `CDXCompass__Render` call xref `0x0042722c`; applies render states `0x13/0x14` as `2/2` before pending render-state application. |
| `0x004821e0` | `CDXCompass__ApplyRenderStateAdditive` | `CDXCompass__Render` call xref `0x00427911`; applies render states `0x13/0x14` as `5/6` before pending render-state application. |
| `0x00481400` | `CHud__ctor_base` | `CDXEngine__InitLandscapeTextureTables` call xref `0x00542743`; initializes active-reader cells, component/compass slots, and HUD state flags. |
| `0x00481450` | `CHud__Init` | `CGame__Init` call xref `0x0046c3d8`; allocates compass and BattleLine HUD subobjects, sets initialized state, and loads text ids. |
| `0x00481650` | `CHud__LoadTextures` | `CGame__RunLevel` call xref `0x0046e367`; resolves crosshair, radar, weapon, objective, and speaker HUD textures, then delegates compass and battleline texture loading. |
| `0x00481b00` | `CHud__ShutDown` | `CGame__Shutdown` call xref `0x0046c9ac`; clears BattleLine state, destroys compass textures, frees compass/BattleLine allocations, and releases HUD texture references. |
| `0x00482090` | `HudRenderState__ApplyOverlaySpriteState` | `CDXCompass__Render` call xref `0x00427222` plus HUD/message/battleline callers; applies shared overlay sprite render state used by HUD, message, compass, and battleline render paths. |

## Context Evidence

Wave1141 also exported 27 context rows around the reviewed compass/HUD cluster: `0x00406040 CDXCompass__GetTrackedPositionX`, `0x0040c630 CDXCompass__GetTrackedPositionY`, `0x004270e0 CDXCompass__InitMarkerArrays`, `0x00427210 CDXCompass__Render`, `0x004815c0 CHud__Reset`, `0x00481af0 CHud__PostLoadProcess`, `0x00481f40 CHud__SetHudComponent`, `0x00482050 CHud__PromotePendingHudComponent`, `0x00482210 CHud__RenderSegmentedMeterBar`, `0x00482590 CHud__RenderTargetIndicatorOverlay`, `0x00483530 CHud__RenderControllerSlotStatusPanel`, `0x00484340 CHud__RenderTargetMarkers3D`, `0x00484c50 CHud__RenderTacticalRadarContacts`, `0x00485830 CHud__SelectMarkerTextureIndexByUnitFlags`, `0x004858d0 CHud__RenderObjectiveProgressGaugeAndHeadingNeedle`, `0x00485d50 CHud__RenderObjectiveStatusPanel`, `0x00486940 CHud__RenderObjectiveSlotFillPanel`, `0x00486e00 CHud__RenderWorldTargetSprites`, `0x004879e0 CHud__RenderOverlayForViewpoint`, `0x00487bc0 CHud__RenderOverlay`, `0x00487d10 CHud__RenderBattleline`, `0x00488090 CHud__RenderActiveHudComponentPass`, `0x004881e0 CHud__ResolveOverlaySlotRenderMode`, `0x0053bda0 CDXCompass__ReleaseDynamicResources`, `0x0053c2e0 CDXCompass__BuildByteSpriteOverlayTexture`, `0x0053c510 CDXCompass__UpdateDynamicOverlayTexture`, and `0x0053cd30 CDXCompass__RenderWorldSpaceOverlay`.

## Evidence Counts

- Primary exports: `13` metadata rows, `13` tag rows, `28` xref rows, `1310` instruction rows, and `13` decompile rows.
- Context exports: `27` metadata rows, `27` tag rows, `45` xref rows, `8549` instruction rows, and `27` decompile rows.
- Queue refresh: `6411/6411 = 100.00%`; static debt `0 / 0 / 0`.
- Current-risk refresh: current risk candidates `6166`; current focused candidates `1178`; focused threshold `15`; not Wave911 reconstruction.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-145724_post_wave1141_cdxcompass_hud_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`.

## Boundary

This is static Ghidra evidence only. Runtime compass behavior, runtime HUD behavior, runtime rendering behavior, exact concrete `CHud`/`CDXCompass`/BattleEngine/render-resource layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
