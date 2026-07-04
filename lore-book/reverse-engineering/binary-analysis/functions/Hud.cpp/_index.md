# Hud.cpp

Wave1216 (`wave1216-render-resource-texture-hud-tail-current-risk-review`) re-read `CHudComponent__RenderPassEntry` as part of the HUD/render tail current-risk review. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified`. Runtime HUD behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

> HUD (Heads-Up Display) functions from BEA.exe

> **Queue status (2026-05-31):** Ghidra export-contract closure **6238/6238** (Wave1017: every current function commented with clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

The CHud class manages the in-game heads-up display, including health bars, ammo counters, radar, and other UI elements displayed during gameplay.

**Debug Path**: `[maintainer-local-source-export-root]\Hud.cpp` (string at 0x0062ce78)

Wave1158 (`wave1158-hud-render-component-current-risk-review`) re-read `20 HUD render/component current-risk rows` with fresh Ghidra export evidence as a read-only review and no mutation. Covered CHud lifecycle/component/render anchors include `CHud__ctor_base`, `CHud__Init`, `CHud__Reset`, `CHud__LoadTextures`, `CHud__PostLoadProcess`, `CHud__ShutDown`, `CHud__SetHudComponent`, `CHud__PromotePendingHudComponent`, `CHud__RenderSegmentedMeterBar`, `CHud__RenderTargetIndicatorOverlay`, `CHud__RenderControllerSlotStatusPanel`, `CHud__RenderTargetMarkers3D`, `CHud__RenderTacticalRadarContacts`, `CHud__RenderObjectiveProgressGaugeAndHeadingNeedle`, `CHud__RenderObjectiveStatusPanel`, `CHud__RenderObjectiveSlotFillPanel`, `CHud__RenderWorldTargetSprites`, `CHud__RenderOverlayForViewpoint`, `CHud__RenderBattleline`, and `CHud__RenderActiveHudComponentPass`. Fresh exports verified `20` metadata rows, `20` tag rows, `24 xref rows`, `7335 instruction rows`, and `20` decompile rows. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `485/1179 = 41.14%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 694; focused threshold `15`; not Wave911 reconstruction. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-002152_post_wave1158_hud_render_component_current_risk_review_verified`. Runtime HUD behavior, runtime render ordering, visible HUD output, exact concrete layouts, exact source-body identity, BEA patching behavior, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1158; wave1158-hud-render-component-current-risk-review; 485/1179 = 41.14%; 20 HUD render/component current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 694; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 24 xref rows; 7335 instruction rows; CHud__RenderOverlayForViewpoint; CHud__RenderBattleline; CHud__RenderActiveHudComponentPass; CHud__RenderTacticalRadarContacts; CHud__RenderObjectiveStatusPanel; CHud__SetHudComponent; [maintainer-local-ghidra-backup-root]\BEA_20260606-002152_post_wave1158_hud_render_component_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave1141 (`wave1141-cdxcompass-hud-current-risk-review`) re-read `13 current-risk rows` in the CDXCompass/HUD render-state current-risk cluster with fresh Ghidra export evidence as a read-only review and no mutation. Covered rows are `0x0053bd60 CDXCompass__InitFields`, `0x0053be40 CDXCompass__Init`, `0x0053c1d0 CDXCompass__BuildRingGeometry`, `0x00427110 CDXCompass__LoadTextures`, `0x00427190 CDXCompass__DestroyTextures`, `0x00427200 CDXCompass__Reset`, `0x004821b0 CDXCompass__ApplyRenderStateModulate`, `0x004821e0 CDXCompass__ApplyRenderStateAdditive`, `0x00481400 CHud__ctor_base`, `0x00481450 CHud__Init`, `0x00481650 CHud__LoadTextures`, `0x00481b00 CHud__ShutDown`, and `0x00482090 HudRenderState__ApplyOverlaySpriteState`. Primary exports verified `13` metadata rows, `13` tag rows, `28` xref rows, `1310` instruction rows, and `13` decompile rows; context exports verified `27` metadata rows, `27` tag rows, `45` xref rows, `8549` instruction rows, and `27` decompile rows. Current focused accounting is `251/1179 = 21.29%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 928; static closure `6411/6411 = 100.00%`; expanded static surface `1560/1560 = 100.00%`; Wave911 focused `812/1408 = 57.67%`; Wave911 top-500 `500/500 = 100.00%`; static debt `0 / 0 / 0`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-145724_post_wave1141_cdxcompass_hud_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`. This is static evidence only: runtime compass behavior, runtime HUD behavior, runtime rendering behavior, exact concrete layouts, BEA patching, visual QA, and rebuild parity remain separate proof.

Wave1017 (`hud-objective-marker-review-wave1017`) re-read three HUD objective/marker helper bodies with no mutation, narrowing the duplicate-proximate Wave411/Wave1004/Wave1013 evidence into a fresh direct body check. Fresh target evidence covered `0x00484340 CHud__RenderTargetMarkers3D`, `0x004858d0 CHud__RenderObjectiveProgressGaugeAndHeadingNeedle`, and `0x00486940 CHud__RenderObjectiveSlotFillPanel`; all three have direct call xrefs from `0x004879e0 CHud__RenderOverlayForViewpoint`. Target exports verified 3 metadata rows, 3 tag rows, 3 xref rows, 1267 body-instruction rows, and 3 decompile rows. Context exports verified 11 metadata rows, 26 xref rows, 4103 context body-instruction rows, and 11 context decompile rows across target-indicator, tactical radar, objective status, world-target, active-component, slot-render-mode, overlay root, and `0x0053ecc0 CDXEngine__PostRender` context. Queue closure remains `6238/6238 = 100.00%`; Wave911 focused re-audit progress remains `513/1408 = 36.43%`; expanded static surface progress is `742/1493 = 49.70%`; Wave911 top-500 risk-ranked coverage is `442/500 = 88.40%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-201957_post_wave1017_hud_objective_marker_review_verified`. Runtime HUD behavior, visible render ordering, exact source-body identity, concrete `CHud`/`BattleEngine`/texture/layout semantics, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1017; hud-objective-marker-review-wave1017; 0x00484340 CHud__RenderTargetMarkers3D; 0x004858d0 CHud__RenderObjectiveProgressGaugeAndHeadingNeedle; 0x00486940 CHud__RenderObjectiveSlotFillPanel; 0x004879e0 CHud__RenderOverlayForViewpoint; 513/1408 = 36.43%; 742/1493 = 49.70%; 442/500 = 88.40%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-201957_post_wave1017_hud_objective_marker_review_verified; no mutation.

Wave1013 (`hud-lifecycle-render-support-review-wave1013`) re-reviewed HUD lifecycle and render-support rows with no mutation. Fresh read-only evidence covered `0x00481450 CHud__Init`, `0x004815c0 CHud__Reset`, `0x00481650 CHud__LoadTextures`, `0x00481af0 CHud__PostLoadProcess`, `0x00481f40 CHud__SetHudComponent`, HUD overlay continuity rows `0x00483530`, `0x00484340`, `0x004858d0`, `0x00486940`, and `0x00486e00`, `0x004821e0 CDXCompass__ApplyRenderStateAdditive`, `0x00488330 CIBuffer__CreateConfigured`, `0x004885e0 CIBuffer__LockDirect`, `0x0048f540 CLevelBriefingLog__ctor`, `0x0048f5a0 CLevelBriefingLog__scalar_deleting_dtor`, and `0x0048f5c0 CLevelBriefingLog__dtor`. Target/context exports verified 16 metadata rows, 16 tag rows, 23 xref rows, 3829 body-instruction rows, 16 decompile rows, 9 context metadata rows, 23 context xref rows, 2075 context body-instruction rows, and 9 context decompile rows. Queue closure remains `6238/6238 = 100.00%`; Wave911 focused re-audit progress remains `505/1408 = 35.87%`; expanded static surface progress is `718/1493 = 48.09%`; Wave911 top-500 risk-ranked coverage is `420/500 = 84.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified`. Runtime HUD/compass/briefing-log/index-buffer behavior, exact source-body identity, concrete layouts, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1013; hud-lifecycle-render-support-review-wave1013; 0x00481450 CHud__Init; 0x004815c0 CHud__Reset; 0x00481650 CHud__LoadTextures; 0x00481af0 CHud__PostLoadProcess; 0x00481f40 CHud__SetHudComponent; 0x004821e0 CDXCompass__ApplyRenderStateAdditive; 0x00488330 CIBuffer__CreateConfigured; 0x004885e0 CIBuffer__LockDirect; 0x0048f540 CLevelBriefingLog__ctor; 0x0048f5a0 CLevelBriefingLog__scalar_deleting_dtor; 0x0048f5c0 CLevelBriefingLog__dtor; 505/1408 = 35.87%; 718/1493 = 48.09%; 420/500 = 84.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified; no mutation.

Wave1004 (`hud-render-body-review-wave1004`) re-reviewed the HUD render-body continuum from `0x00482590 CHud__RenderTargetIndicatorOverlay` through `0x004881e0 CHud__ResolveOverlaySlotRenderMode`, with `0x0053ecc0 CDXEngine__PostRender` context. Fresh exports verified `15` metadata rows, `15` tag rows, `30` xref rows, `6350` body-instruction rows, `15` decompile rows, `7` context metadata rows, and `7` context decompile rows. The re-read preserved the call spine from `CDXEngine__PostRender` to `0x00487bc0 CHud__RenderOverlay`, `0x00487d10 CHud__RenderBattleline`, and `0x00488090 CHud__RenderActiveHudComponentPass`; `CHud__RenderOverlay` to `0x004879e0 CHud__RenderOverlayForViewpoint`; and the per-viewpoint dispatcher to `0x00482590 CHud__RenderTargetIndicatorOverlay`, `0x00484c50 CHud__RenderTacticalRadarContacts`, `0x004857e0 HudOverlay__DrawSpriteQuad`, and adjacent objective/world-target/controller helpers. No Ghidra mutation was needed. Queue closure is `6223/6223 = 100.00%`; Wave911 focused re-audit progress is `485/1408 = 34.45%`; expanded static surface progress is `654/1478 = 44.25%`; Wave911 top-500 risk-ranked coverage is `380/500 = 76.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-124610_post_wave1004_hud_render_body_review_verified`. Runtime HUD behavior, runtime render ordering/visible HUD output, exact source-body identity, concrete `CHud`/`CDXEngine`/`CDXCompass`/`CDXBattleLine`/texture/component/viewport layouts, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1004; hud-render-body-review-wave1004; 0x00482590 CHud__RenderTargetIndicatorOverlay; 0x00484c50 CHud__RenderTacticalRadarContacts; 0x004857e0 HudOverlay__DrawSpriteQuad; 0x004879e0 CHud__RenderOverlayForViewpoint; 0x00487bc0 CHud__RenderOverlay; 0x00487d10 CHud__RenderBattleline; 0x00488090 CHud__RenderActiveHudComponentPass; 0x004881e0 CHud__ResolveOverlaySlotRenderMode; 0x0053ecc0 CDXEngine__PostRender; 485/1408 = 34.45%; 654/1478 = 44.25%; 380/500 = 76.00%; 6223/6223 = 100.00%.

Wave1003 (`hud-head-render-state-review-wave1003`) re-reviewed the Wave400 HUD head/render-state cluster and recovered the caller boundary `0x0046c990 CGame__Shutdown` after `0x0046c9ac` was found as an orphan call to `0x00481b00 CHud__ShutDown`. Fresh post exports verified `0x00481400 CHud__ctor_base`, `0x00481b00 CHud__ShutDown`, `0x00482090 HudRenderState__ApplyOverlaySpriteState`, `0x004821b0 CDXCompass__ApplyRenderStateModulate`, `0x00482210 CHud__RenderSegmentedMeterBar`, and the surrounding HUD head rows with `13` metadata rows, `13` tag rows, `32` xref rows, `1324` body-instruction rows, and `13` decompile rows. Queue closure is `6223/6223 = 100.00%`; Wave911 focused re-audit progress remains `472/1408 = 33.52%`; expanded static surface candidate-set progress is `641/1478 = 43.37%`, plus one newly recovered out-of-seed boundary; Wave911 top-500 risk-ranked coverage is `371/500 = 74.20%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-120949_post_wave1003_hud_head_render_state_review_verified`. Runtime shutdown behavior, runtime HUD behavior, exact source-body identity, concrete `CGame`/`CHud`/renderer/resource layouts, BEA patching, and rebuild parity remain separate proof.

Wave753 static read-back (`unwind-continuation-wave753`, `wave753-readback-verified`) saved comments/tags/signatures for Hud.cpp-adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d2d00 Unwind@005d2d00` through `0x005d2dd0 Unwind@005d2dd0`. Evidence includes Hud.cpp debug path `0x0062ce78`, DATA scope-table xrefs `0x0061bad4` through `0x0061bb9c`, four `OID__FreeObject_Callback` rows, four `CSPtrSet__Clear` stack-local set clears (`0x005d2d80 Unwind@005d2d80` through `0x005d2d98 Unwind@005d2d98`), and two bounded jumps to `DeviceObject__ctor_like_00512d50` where exact helper semantics remain unproven. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-221626_post_wave753_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

Wave923 (`hud-radar-pause-render-review-wave923`) re-reviewed `0x00487d10 CHud__RenderBattleline` as part of a HUD/radar/pause/sprite/D3D visible-render support slice. Fresh metadata/tags/xref/instruction/decompile evidence kept the Wave412 source-aligned HUD singleton and viewport-argument claim intact; no mutation was needed. Wave911 focused re-audit progress after this slice is `86/1408 = 6.11%`, while export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260527-210516_post_wave923_hud_radar_pause_render_review_verified`. Runtime HUD behavior, concrete CHud/BattleLine layout, exact source-body identity, patch behavior, and rebuild parity remain separate proof.

Wave990 (`hud-battleline-objective-overlay-review-wave990`) re-audited the objective-panel and battleline overlay join after the Wave900-Wave989 recheck gate. Fresh post exports tie `0x00485d50 CHud__RenderObjectiveStatusPanel` to `0x0040dda0 CUnitAI__RefreshGridCooldownFromOccupiedCells` at `0x004862af`, and tie `0x00487d10 CHud__RenderBattleline` to `0x00414cb0 CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices` at `0x00488071`. The pass saved comment/tag normalizations on the two callee rows only, replacing stale grid wording at `0x0040dda0` with `0x0044c720 CFearGrid__GetOccupancyAtWorldVector` evidence. Wave911 focused re-audit progress is `441/1408 = 31.32%`; expanded static surface progress is `517/1478 = 34.98%`; export-contract closure remains `6222/6222 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-041618_post_wave990_hud_battleline_objective_overlay_verified`. Runtime HUD behavior, runtime battleline/objective rendering behavior, exact `CHud` layout, exact source-body identity, patch behavior, and rebuild parity remain separate proof.

## Functions

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x00481400 | CHud__ctor_base | SAVED | Wave400 corrected older CDXEngine owner label; initializes reader cells, component slots, compass slot, and six HUD flags |
| 0x00481450 | CHud__Init | SAVED | Wave400 saved ECX-this init signature; allocates compass/BattleLine HUD subobjects and text ids |
| 0x004815c0 | CHud__Reset | SAVED | Wave400 saved ECX-this reset signature; resets HUD flags, marker arrays, and objective/indicator state |
| 0x00481650 | CHud__LoadTextures | SAVED | Wave400 saved ECX-this texture-load signature for crosshair/radar/weapon/objective/speaker HUD textures |
| 0x00481af0 | CHud__PostLoadProcess | SAVED | Wave400 saved ECX-this return-bearing post-load signature that dispatches through BattleLine setup |
| 0x00481b00 | CHud__ShutDown | SAVED | Wave400 saved ECX-this shutdown signature; releases compass/BattleLine allocations and HUD texture refs |
| 0x00481f40 | CHud__SetHudComponent | SAVED | Wave400 saved component-name and slot-flag signature for cutscene caller-driven component swaps |
| 0x00482050 | CHud__PromotePendingHudComponent | SAVED | Wave400 corrected older CDXEngine owner label; promotes pending HUD component into the active slot |
| 0x00482090 | HudRenderState__ApplyOverlaySpriteState | SAVED | Wave400 corrected older narrow CExplosionInitThing owner label to shared HUD/message/compass/battleline overlay state |
| 0x004821b0 | CDXCompass__ApplyRenderStateModulate | SAVED | Wave400 saved plain cdecl compass render-state helper for the 2/2 state pair |
| 0x004821e0 | CDXCompass__ApplyRenderStateAdditive | SAVED | Wave400 saved plain cdecl compass render-state helper for the 5/6 state pair |
| 0x00482210 | CHud__RenderSegmentedMeterBar | SAVED | Wave400 corrected older CDXEngine owner label; draws segmented objective/message meter pieces using CHud texture refs |
| 0x00482590 | CHud__RenderTargetIndicatorOverlay | SAVED | Wave410 corrected older CExplosionInitThing owner label; draws target-indicator texture/projection/health-bar overlay state |
| 0x00483530 | CHud__RenderControllerSlotStatusPanel | SAVED | Wave411 corrected older CExplosionInitThing owner label; renders controller-slot timer/status panel through CHud meter/text paths |
| 0x00484340 | CHud__RenderTargetMarkers3D | SAVED | Wave411 corrected older CExplosionInitThing owner label; renders 3D target marker sprites using CHud fields and BattleEngine auto-aim position |
| 0x00484c50 | CHud__RenderTacticalRadarContacts | SAVED | Wave411 corrected older CExplosionInitThing owner label; partitions visible contacts, selects marker textures, draws radar markers, and clears temporary sets |
| 0x004857e0 | HudOverlay__DrawSpriteQuad | SAVED | Wave411 corrected older CExplosionInitThing owner label to owner-neutral cdecl sprite wrapper around CVBufTexture__DrawSpriteEx |
| 0x00485830 | CHud__SelectMarkerTextureIndexByUnitFlags | SAVED | Wave411 corrected older CExplosionInitThing owner label and stale extra-argument shape; one stack unit argument, RET 0x4 |
| 0x004858d0 | CHud__RenderObjectiveProgressGaugeAndHeadingNeedle | SAVED | Wave411 corrected older CExplosionInitThing owner label; draws objective gauge sprites and heading needle context |
| 0x00485d50 | CHud__RenderObjectiveStatusPanel | SAVED | Wave411 corrected older CExplosionInitThing owner label; renders objective and weapon status text/icon context |
| 0x00486940 | CHud__RenderObjectiveSlotFillPanel | SAVED | Wave411 corrected older CExplosionInitThing owner label; renders weapon energy/ammo fill and count context |
| 0x00486e00 | CHud__RenderWorldTargetSprites | SAVED | Wave411 corrected older CExplosionInitThing owner label; renders world-space target and lock sprites |
| 0x004879e0 | CHud__RenderOverlayForViewpoint | SAVED | Wave410 corrected older CExplosionInitThing owner label; per-viewpoint dispatcher for target indicators, controller slots, objective panels, slot fill, radar, and related overlay helpers |
| 0x00487bc0 | CHud__RenderOverlay | SAVED | Wave410 corrected older CDXEngine owner label; called from CDXEngine__PostRender with HUD singleton where source calls HUD.RenderOverlay() |
| 0x00487d10 | CHud__RenderBattleline | SAVED | Wave412 corrected older CDXEngine owner label; source-aligned HUD.RenderBattleline(viewport), HUD singleton ECX plus one viewport stack arg; battleline/influence overlay dispatch |
| 0x00488090 | CHud__RenderActiveHudComponentPass | SAVED | Wave412 corrected older CDXEngine owner/signature; active component slot +0x1fc render/pass cleanup |
| 0x004881e0 | CHud__ResolveOverlaySlotRenderMode | SAVED | Wave412 corrected older CVBufTexture owner/extra-param signature; HUD slot-index render-mode helper |
| 0x004de3a0 | CHudComponent__ctor | RENAMED | Constructs 0x68-byte HUD component object |
| 0x004de6b0 | CHudComponent__GetPos | RENAMED | Writes 16 bytes from `this+0x0C` (mPos) into out buffer |
| 0x004de6e0 | CHudComponent__GetOrientation | RENAMED | Writes 0x30 bytes from `this+0x1C` (mOrientation / FoR matrix) into out buffer |
| 0x004de700 | Return1f | RENAMED | Shared virtual stub returning constant `1.0f` |
| 0x004de720 | CHudComponent__GetMesh | RENAMED | Returns dword/pointer at `this+0x54` (set during ctor resource init) |
| 0x004de730 | CHudComponent__scalar_deleting_dtor | RENAMED | Scalar deleting dtor wrapper |
| 0x004de760 | CHudComponent__dtor | RENAMED | Component destructor body |
| 0x004de7d0 | CHudComponent__HandleEvent | RENAMED | Handles scheduled event 4000 (fade/progress tick), reschedules, may delete on destroy flag |
| 0x004de850 | CHudComponent__RequestDestroy | RENAMED | Marks component for deferred destruction |
| 0x004de860 | CHudComponent__RenderPass | RENAMED | Per-component render/update pass |
| 0x004de8b0 | CHudComponent__GetAlpha | RENAMED | Returns float at `this+0x60` (alpha/progress) |
| 0x0054b800 | CHudComponent__RenderPassEntry | SAVED | Wave608 saved cdecl mesh-entry/component signature; renders type-1 2D mesh triangles through CVBufTexture and emits DebugTrace for unsupported/unknown mesh types |

## Details

### Wave753 Hud.cpp Unwind Continuation (0x005d2d00-0x005d2dd0)

Wave753 hardened ten Hud.cpp-adjacent unwind callbacks as `void __cdecl Unwind@...(void)` without renames, function-boundary changes, or executable-byte changes. Representative rows:

| Address | Evidence |
| --- | --- |
| 0x005d2d00 | DATA xref `0x0061bad4`; `OID__FreeObject_Callback` on `*(EBP-0x10)` with Hud.cpp line token `0x38` and allocation/type value `0x5d`. |
| 0x005d2d16 | DATA xref `0x0061badc`; `OID__FreeObject_Callback` on `*(EBP-0x10)` with allocation/type value `0x5f`. |
| 0x005d2d40 | DATA xref `0x0061bb04`; `OID__FreeObject_Callback` on `*(EBP+0x8)` with allocation/type value `0x137`. |
| 0x005d2d59 | DATA xref `0x0061bb0c`; `OID__FreeObject_Callback` on `*(EBP+0x8)` with allocation/type value `0x13b`. |
| 0x005d2d80 | DATA xref `0x0061bb34`; `CSPtrSet__Clear(EBP-0x4c)`. |
| 0x005d2d88 | DATA xref `0x0061bb3c`; `CSPtrSet__Clear(EBP-0x2c)`. |
| 0x005d2d90 | DATA xref `0x0061bb44`; `CSPtrSet__Clear(EBP-0x3c)`. |
| 0x005d2d98 | DATA xref `0x0061bb4c`; `CSPtrSet__Clear(EBP-0x5c)`. |
| 0x005d2db0 | DATA xref `0x0061bb74`; loads `ECX` from `*(EBP-0x10)` and jumps to `DeviceObject__ctor_like_00512d50`. |
| 0x005d2dd0 | DATA xref `0x0061bb9c`; same bounded device-object helper pattern as `0x005d2db0`. |

### Wave608 HUD Component Render Entry (0x0054b800)

Wave608 serialized headless dry/apply/read-back hardened `CHudComponent__RenderPassEntry` with signature `void __cdecl CHudComponent__RenderPassEntry(void * mesh_entry, void * hud_component)`. Direct caller evidence from `CHudComponent__RenderPass` shows the first argument is the sub-item pointer loaded from the owned mesh table at `+0x160`, and the second argument is the `CHudComponent` `this` pointer. The target body is plain cdecl ending in `RET c3`.

The body reads the mesh-entry type at `+0x8c`, skips types `2` and `4`, renders type `1` 2D mesh triangles through `CVBufTexture__SetVBFormat`, `CVBufTexture__SetIBFormat`, `CVBufTexture__AddVertices`, `CVBufTexture__AddIndices`, and `CVBufTexture__Render`, and emits `DebugTrace` for type `3` or unknown mesh types.

Validation recorded `1` metadata row, `1` tag row, `1` xref row, `512` instruction rows, `488` target-function instruction rows, `1` decompile row, focused probe status `PASS`, refreshed queue telemetry of `6093` functions / `3117` comments / `2976` commentless / `1304` exact-undefined signatures / `1064` `param_N` signatures, and actual Ghidra backup `[maintainer-local-ghidra-backup-root]\BEA_20260519-214647_post_wave608_hud_component_render_entry_verified`. This is static Ghidra metadata evidence only: source-body identity, exact mesh-entry/component layouts, runtime HUD behavior, concrete render output, BEA patching, and rebuild parity remain unproven. The next queue head is `0x0054bf80 CDXMeshVB__ctor_like_0054bf80`.

### Wave412 HUD Battleline/Render-Tail Correction (0x00487d10-0x004881e0)

Wave412 serialized headless dry/apply/read-back corrected three HUD battleline/render-tail labels after the HUD overlay root/helper corrections. `CDXEngine__PostRender` now calls `CHud__RenderBattleline` with HUD singleton `ECX=0x8aa4e8` plus one viewport stack argument, matching the Stuart source caller `HUD.RenderBattleline(viewport);`. The body records battleline/message-box sprite context and dispatches BattleLine influence-map rendering through the existing CDXBattleLine path. `CHud__RenderActiveHudComponentPass` is the following HUD singleton active-component pass: it checks slot `+0x1fc`, applies alpha-sprite state, calls `CHudComponent__RenderPass`, and clears/deletes the component when the done flag at `+0x64` is set. `CHud__ResolveOverlaySlotRenderMode` was corrected away from the older CVBufTexture owner label because every checked callsite sets HUD singleton `ECX` and passes one slot argument; the helper indexes HUD slot state at `+0x34 + slot_index*4`.

Validation recorded `3` metadata rows, `3` tag rows, `9` xref rows, `3` target decompile exports, `1` caller decompile export, `66` PostRender callsite instruction rows, `133` overlay-slot callsite instruction rows, focused probe status `PASS`, refreshed queue telemetry of `6028` functions / `1577` comments / `4451` commentless / `1909` undefined signatures / `1840` `param_N` signatures, and actual Ghidra backup `[maintainer-local-ghidra-backup-root]\BEA_20260514_101618_post_wave412_hud_battleline_tail_verified`. This is static Ghidra metadata evidence only: runtime HUD behavior, concrete CHud/BattleLine/component layouts, exact source-body identity, locals/types, BEA launch, game patching, and rebuild parity remain unproven.

### Wave411 HUD Overlay Helper Correction (0x00483530-0x00486e00)

Wave411 serialized headless dry/apply/read-back corrected nine neighboring HUD overlay helper labels after the Wave410 dispatcher/root correction. `CHud__RenderOverlayForViewpoint` now directly dispatches `CHud__RenderWorldTargetSprites`, `CHud__RenderControllerSlotStatusPanel`, `CHud__RenderTargetMarkers3D`, `CHud__RenderObjectiveProgressGaugeAndHeadingNeedle`, `CHud__RenderObjectiveStatusPanel`, `CHud__RenderObjectiveSlotFillPanel`, and `CHud__RenderTacticalRadarContacts`. The tactical radar helper then calls `HudOverlay__DrawSpriteQuad` and `CHud__SelectMarkerTextureIndexByUnitFlags`; the marker selector was corrected to a one-stack-argument `RET 0x4` signature instead of the older extra-parameter shape.

Validation recorded `9` metadata rows, `9` tag rows, `18` xref rows, `9` target decompile exports, `1` caller decompile export, focused probe status `PASS`, refreshed queue telemetry of `6028` functions / `1574` comments / `4454` commentless / `1909` undefined signatures / `1843` `param_N` signatures, and actual Ghidra backup `[maintainer-local-ghidra-backup-root]\BEA_20260514_094034_post_wave411_hud_overlay_helpers_verified`. This is static Ghidra metadata evidence only: runtime HUD behavior, concrete CHud/unit/radar layouts, exact source-body identity, locals/types, BEA launch, game patching, and rebuild parity remain unproven.

### Wave410 HUD Overlay Correction (0x00482590, 0x004879e0, 0x00487bc0)

Wave410 serialized headless dry/apply/read-back corrected the HUD overlay root and two direct helper labels. `CDXEngine__PostRender` now calls `CHud__RenderOverlay(&DAT_008aa4e8)` where Stuart's `DXEngine.cpp` source calls `HUD.RenderOverlay();`. `CHud__RenderOverlay` loops active viewpoints and dispatches `CHud__RenderOverlayForViewpoint`; Wave411 now certifies the neighboring overlay helper ownership/signature context reached from that dispatcher. `CHud__RenderTargetIndicatorOverlay` handles active/last target context, split-screen placement, CHud texture refs, Thunderhead miniature context, generic projection sphere context, and target health bars.

Validation recorded `3` metadata rows, `3` tag rows, `3` xref rows, `3` target decompile exports, `1` outer-caller decompile export, focused probe status `PASS`, refreshed queue telemetry of `6028` functions / `1565` comments / `4463` commentless / `1909` undefined signatures / `1852` `param_N` signatures, and actual Ghidra backup `[maintainer-local-ghidra-backup-root]\BEA_20260514_090320_post_wave410_hud_overlay_verified`. This is static Ghidra metadata evidence only: runtime HUD behavior, concrete CHud layout, neighboring overlay helper ownership, locals/types, BEA launch, game patching, and rebuild parity remain unproven.

### Wave400 HUD Head Correction (0x00481400-0x00482210)

Wave400 serialized headless dry/apply/read-back corrected or hardened twelve HUD-head and early HUD render-state targets. Wave1003 re-read the same cluster while recovering `0x0046c990 CGame__Shutdown`; it corrected older `CDXEngine` labels to bounded `CHud` ownership where the caller passes the HUD singleton, corrected `0x00482090` from an overly narrow explosion-owner label to shared overlay render-state setup, and hardened the `CHud` / `CDXCompass` signatures listed above.

Validation recorded `12` metadata rows, `12` decompile exports, `30` xref rows, `12` tag rows, `1452` instruction rows, and focused probe status `PASS`. This is static Ghidra metadata evidence only: runtime HUD behavior, concrete `CHud` layout, concrete locals/types, BEA launch, game patching, and rebuild parity remain unproven.

### CHud__Init (0x00481450)

- **Purpose**: Initializes the HUD system by allocating buffers and loading texture resources
- **Xref**: Found via debug path at 0x0062ce78 (lines 0x5d and 0x5f)
- **Called from**: `CGame__Init`
- **Calling convention**: thiscall (ECX = this pointer)

**Behavior**:
1. Sets flag at offset 0x5c to 1 (likely "initialized" flag)
2. Allocates large buffer (0x3f14 = 16148 bytes) for HUD graphics data
3. Allocates secondary buffer (0x80 = 128 bytes)
4. Loads 8 texture/sprite resources via hash lookups:
   - 0x72a0936 -> stored at offset 0xb4
   - 0x6b91062 -> stored at offset 0xb8
   - 0x85574fc -> stored at offset 0xbc
   - 0x2b617f -> stored at offset 0xc4
   - 0x2b4ce2 -> stored at offset 0xc8
   - 0x396c8 -> stored at offset 0xc0
   - 0x31e12896 -> stored at offset 0xcc
   - 0x227a52ff -> stored at offset 0xd0

**CHud Class Layout (Partial)**:
```
Offset  Size  Field
0x30    4     Secondary buffer pointer
0x5c    4     Initialized flag
0x60    4     Main buffer pointer
0xb4    4     Texture resource 1
0xb8    4     Texture resource 2
0xbc    4     Texture resource 3
0xc0    4     Texture resource 6
0xc4    4     Texture resource 4
0xc8    4     Texture resource 5
0xcc    4     Texture resource 7
0xd0    4     Texture resource 8
```

---

### CHud__SetHudComponent (0x00481f40)

- **Purpose**: Creates or destroys HUD component objects based on mode
- **Xref**: Found via debug path at 0x0062ce78 (lines 0x137 and 0x13b)
- **Called from**:
  - `CCutscene__Start`
  - `CCutscene__Stop`
  - `CCutscene__Update`
- **Calling convention**: thiscall (ECX = this pointer)
- **Parameters**:
  - `component_name`: component name/id passed to `CHudComponent__ctor`
  - `slot_flag`: boolean-like slot selector (0 = use offset 0x200, non-0 = use offset 0x1fc)

**Behavior**:
1. If existing component at target offset is non-null, marks it for deferred destruction via `CHudComponent__RequestDestroy`
2. Allocates new component object (0x68 = 104 bytes)
3. Initializes component via `CHudComponent__ctor` with `param_1` (component name/id)
4. Stores component pointer at offset 0x1fc or 0x200 based on param_2

**CHud Class Layout (Additional)**:
```
Offset   Size  Field
0x1fc    4     HUD component pointer 1 (when param_2 != 0)
0x200    4     HUD component pointer 2 (when param_2 == 0)
```

This function appears to manage two interchangeable HUD component slots, possibly for transitioning between different HUD states (e.g., normal gameplay vs cutscene overlay).

---

### CHudComponent Helpers (0x004de3a0 cluster)

- `CHudComponent__ctor` (`0x004de3a0`)
  - Initializes monitor/vtable state for a 0x68-byte object.
  - Sets two vtable pointers:
    - `this+0x00` -> `0x005dec20` (pos/orientation/mesh/alpha getters)
    - `this+0x04` -> `0x005dec10` (monitor/event handler + deleting dtor)
  - Builds `<component_name> + ".msh"` and loads/caches Effect mesh/resource handles.
  - Schedules event `4000` via `CEventManager__AddEvent_AtTime` when resource setup is valid.

- `CHudComponent__RequestDestroy` (`0x004de850`)
  - Sets byte flags at `+0x64` and `+0x65` to request deferred destroy.
  - The HUD render path checks `+0x64` and then executes virtual cleanup/free.

- `CHudComponent__RenderPass` (`0x004de860`)
  - Fetches sub-item table from owned object at `+0x4C`.
  - Iterates count at `+0x15C`, dispatching each entry through `CHudComponent__RenderPassEntry(entry, this)`.

- `CHudComponent__dtor` / `CHudComponent__scalar_deleting_dtor`
  - Releases owned object at `+0x48`, runs `CMonitor__Shutdown`, and conditionally frees memory in scalar deleting wrapper.

---

## Exception Handlers

The following Unwind functions are exception cleanup handlers associated with Hud.cpp:

| Address | Name | Notes |
|---------|------|-------|
| 0x005d2d00 | Unwind@005d2d00 | Cleanup for CHud__Init allocation 1 |
| 0x005d2d16 | Unwind@005d2d16 | Cleanup for CHud__Init allocation 2 |
| 0x005d2d40 | Unwind@005d2d40 | Cleanup for CHud__SetHudComponent |
| 0x005d2d59 | Unwind@005d2d59 | Cleanup for CHud__SetHudComponent |

These are automatically generated by the compiler for structured exception handling and call `OID__FreeObject_Callback` (wrapper around `OID__FreeObject`) to clean up partially constructed objects if an exception occurs.

## Related Functions

- **FUN_004f2580**: Resource/texture loader (takes hash, returns resource pointer)
- **CDXMemoryManager__Alloc**: Memory allocator reached through object helpers and corrected in Wave607
- **CHudComponent__RequestDestroy (0x004de850)**: Deferred-destroy mark helper
- **CHudComponent__ctor (0x004de3a0)**: Component constructor/initializer
- **CHudComponent__RenderPass (0x004de860)**: Component render/update loop
- **FUN_0053bd60**: Unknown initializer (called after first allocation in Init)
- **FUN_00539f00**: Unknown initializer (called after second allocation in Init)

## Discovery Notes

- Found via xref search to debug path string at 0x0062ce78
- The string has a "Y?" prefix at 0x0062ce76, actual path starts at 0x0062ce78
- Debug path references include source line numbers (0x5d=93, 0x5f=95, 0x137=311, 0x13b=315)
- CHudComponent vtable targets (`0x004de6b0`, `0x004de6e0`, `0x004de700`, `0x004de720`, `0x004de7d0`, `0x004de8b0`) were recovered on 2026-02-13 via manual CodeBrowser function creation (`F`) followed by MCP rename/signature/comment with read-back verification.
