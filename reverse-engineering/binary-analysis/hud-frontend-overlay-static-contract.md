# HUD / Frontend Overlay Static Contract

Historical Wave1216 and Wave1158 anchors below are at-wave snapshots; their older active current-risk counters are preserved as evidence provenance, not current status.

Wave1216 measured anchor: unique-address accounting governs active current-risk progress. Probe token anchor: Wave1216; wave1216-render-resource-texture-hud-tail-current-risk-review; 1145/1179 = 97.12%; 7 render/resource/texture/HUD tail current-risk rows; CThing__InitRenderThingFromInitMeshName; CPDMesh__dtor_base; CWaterRenderSystem__ResetAndMarkSourceFlag; CAtmosphericsProfile__ResetAndInitSnowResources; CHudComponent__RenderPassEntry; CTexture__NodeType11_Ctor_WithDescriptorCopy; CTexture__NodeType12_Ctor_WithStackScalars; CTexture__NodeType11_Dtor_DeleteOnFlag_Body; CTexture__NodeType11_Dtor_DeleteOnFlag; 6411/6411 = 100.00%; 0 / 0 / 0; 12 xref rows; 962 instruction rows; 7 decompile rows; 28 context xref rows; 1015 context instruction rows; 9 context decompile rows; 6 texture-context xref rows; 111 texture-context instruction rows; 6 texture-context decompile rows; 13 data-xref rows; current focused candidates: 1127; live regenerated current focused candidates: 1127; remaining active focused work: 34; current risk candidates: 6166; fresh Ghidra export; texture label correction; 4 renamed; 4 comments updated; 25 tags added; no signature change; no function-boundary change; no executable-byte change; unique-address accounting; Codex read-only consults used; no Cursor/Composer; legacy additive counter is deprecated (`1176/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md; mesh-resource-render-static-contract.md; texture-resource-decode-static-contract.md; continuity denominator; G:\GhidraBackups\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

Status: active static contract map
Last updated: 2026-06-07
Latest review: Wave1158 (`wave1158-hud-render-component-current-risk-review`)

Wave1220 static closeout acceptance: active current-risk focused accounting is `1179/1179 = 100.00%`; remaining active focused work: 0. This is static Ghidra/read-back/system-map acceptance for the current-risk lane, not runtime HUD behavior, runtime render ordering, visible output proof, exact layout proof, exact source-body identity, BEA patching proof, rebuild parity, or no-noticeable-difference parity.

Static-to-proof handoff: [HUD / Frontend Overlay Visual Runtime Proof Plan](hud-frontend-overlay-visual-runtime-proof-plan.md) records the bounded copied-profile proof design, expected capture evidence set, exact-layout unknowns, stop conditions, and non-claims. It is a planning artifact only; it does not launch BEA, capture screenshots, patch an executable, or prove runtime HUD/menu/render behavior.

MissionScript HUD/display command bridge: [MissionScript HUD / Display Command-Effect Static Proof](missionscript-hud-display-command-effect-static-proof.md) and [missionscript-hud-display-command-effect.v1.json](missionscript-hud-display-command-effect.v1.json) bind descriptor rows `33 HighlightHudPart`, `34 UnHighlightHudPart`, `75 InitVariable`, `76 SetVariable`, and `77 ShutdownVariable` to raw entries `&LAB_00535d70`, `&LAB_00535e60`, `&LAB_00536210`, `&LAB_00536230`, and `&LAB_00536260`; loose-MSL counts `13 / 13 / 77 / 146 / 26`; HUD anchors `CHud__SetHudComponent`, `CHud__RenderOverlayForViewpoint`, `CHudComponent__RenderPass`; and CWorld world-text anchors `CWorld__PushWorldTextSlot`, `CWorld__UpdateWorldTextSlotTiming`, `CWorld__ClearWorldTextSlot`, and `CWorld__GetWorldTextSlotTimerValue`. This is static HUD/display command-effect schema proof complete, not runtime proof.

Probe token anchor: Wave1158; wave1158-hud-render-component-current-risk-review; 485/1179 = 41.14%; 20 HUD render/component current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 694; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 24 xref rows; 7335 instruction rows; CHud__RenderOverlayForViewpoint; CHud__RenderBattleline; CHud__RenderActiveHudComponentPass; CHud__RenderTacticalRadarContacts; CHud__RenderObjectiveStatusPanel; CHud__SetHudComponent; G:\GhidraBackups\BEA_20260606-002152_post_wave1158_hud_render_component_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Static Contract

The retail static evidence maps `CHud` as a lifecycle, component-slot, per-viewpoint overlay, battleline, and active-component render subsystem. The source debug path is `C:\dev\ONSLAUGHT2\Hud.cpp` at `0x0062ce78`; the source labels are useful but exact source-body identity and concrete layouts remain separate proof.

Observed roles:

| Area | Static anchors |
| --- | --- |
| Lifecycle | `CHud__ctor_base`, `CHud__Init`, `CHud__Reset`, `CHud__LoadTextures`, `CHud__PostLoadProcess`, `CHud__ShutDown`. |
| Component slots | `CHud__SetHudComponent`, `CHud__PromotePendingHudComponent`, `CHud__RenderActiveHudComponentPass`, `CHudComponent__RequestDestroy`, `CHudComponent__RenderPass`. |
| Per-viewpoint overlay | `CHud__RenderOverlay`, `CHud__RenderOverlayForViewpoint`, `CHud__RenderTargetIndicatorOverlay`, `CHud__RenderWorldTargetSprites`, `CHud__RenderTargetMarkers3D`. |
| Objective and weapon HUD | `CHud__RenderObjectiveProgressGaugeAndHeadingNeedle`, `CHud__RenderObjectiveStatusPanel`, `CHud__RenderObjectiveSlotFillPanel`, `CHud__RenderSegmentedMeterBar`. |
| Radar and status panels | `CHud__RenderTacticalRadarContacts`, `CHud__RenderControllerSlotStatusPanel`, `CHud__SelectMarkerTextureIndexByUnitFlags`, `HudOverlay__DrawSpriteQuad`. |
| Battleline and message overlays | `CHud__RenderBattleline`, `CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices`, `CMessageBox__RenderOverlay`. |
| Render-state setup | `HudRenderState__ApplyOverlaySpriteState`, `CDXCompass__ApplyRenderStateModulate`, `CDXCompass__ApplyRenderStateAdditive`. |

## Call Graph

Fresh Wave1158 xrefs pin the high-level call graph:

| Caller | HUD path |
| --- | --- |
| `CGame__Init` | `CHud__Init` |
| `CGame__InitRestartLoop` | `CHud__Reset` |
| `CGame__RunLevel` | `CHud__LoadTextures` |
| `CGame__PostLoadProcess` | `CHud__PostLoadProcess` |
| `CGame__Shutdown` | `CHud__ShutDown` |
| `CCutscene__Start`, `CCutscene__Stop`, `CCutscene__Update` | `CHud__SetHudComponent` |
| `CDXEngine__PostRender` | `CHud__PromotePendingHudComponent`, `CHud__RenderBattleline`, `CHud__RenderActiveHudComponentPass` |
| `CHud__RenderOverlay` | `CHud__RenderOverlayForViewpoint` |
| `CHud__RenderOverlayForViewpoint` | target indicator, controller status, 3D marker, objective, slot fill, tactical radar, and world-target helper rows |

## Rebuild-Facing Field Hypotheses

Treat these as static field-role hypotheses, not final C++ layout names:

| Offset / slot | Static role |
| --- | --- |
| `this+0x30` | BattleLine/HUD post-load setup target in current comments. |
| `this+0x50`, `this+0x54`, `this+0x58` | Active target/viewpoint context used by per-viewpoint overlay helpers. |
| `this+0x5c` | Initialized/lifecycle flag seeded by init/reset paths. |
| `this+0x68`, `this+0x94`, `this+0x98`, `this+0xac` | Controller/status panel animation fields. |
| `this+0x9c` | Active-reader cell region initialized by the constructor. |
| `this+0x154`, `this+0x158`, `this+0x160`, `this+0x164`, `this+0x168` | HUD texture references used by segmented meter and target indicator paths. |
| `this+0x1fc` | Active HUD component slot. |
| `this+0x200` | Pending HUD component slot. |

## Evidence Boundary

This map is static retail Ghidra evidence suitable for clean-room planning, UI/HUD schema planning, and future copied-EXE patch candidate scoping. It does not prove runtime HUD behavior, runtime render ordering, visible HUD output, exact concrete `CHud`/viewport/component/radar/target/BattleEngine layouts, exact source-body identity, BEA patching behavior, visual QA, or rebuild parity.
