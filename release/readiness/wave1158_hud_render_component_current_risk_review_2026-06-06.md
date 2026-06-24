# Wave1158 HUD Render Component Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-06
Tag: `wave1158-hud-render-component-current-risk-review`

Wave1158 re-read twenty HUD render/component current-risk rows from the `wave1108-current-risk-rank` active focused denominator with fresh Ghidra exports. The pass made no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

Probe token anchor: Wave1158; wave1158-hud-render-component-current-risk-review; 485/1179 = 41.14%; 20 HUD render/component current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 694; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 24 xref rows; 7335 instruction rows; CHud__RenderOverlayForViewpoint; CHud__RenderBattleline; CHud__RenderActiveHudComponentPass; CHud__RenderTacticalRadarContacts; CHud__RenderObjectiveStatusPanel; CHud__SetHudComponent; G:\GhidraBackups\BEA_20260606-002152_post_wave1158_hud_render_component_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Reviewed anchors:

| Address | Function | Static role |
| --- | --- | --- |
| `0x00481400` | `CHud__ctor_base` | Initializes active-reader cells, component/compass slots, and HUD flags. |
| `0x00481450` | `CHud__Init` | Allocates compass/BattleLine HUD subobjects and loads text ids. |
| `0x004815c0` | `CHud__Reset` | Resets HUD flags, marker arrays, and objective/indicator state. |
| `0x00481650` | `CHud__LoadTextures` | Loads HUD texture refs and delegates compass/BattleLine texture load. |
| `0x00481af0` | `CHud__PostLoadProcess` | Tail-jumps through the BattleLine object setup path. |
| `0x00481b00` | `CHud__ShutDown` | Releases compass/BattleLine allocations and HUD texture refs. |
| `0x00481f40` | `CHud__SetHudComponent` | Cutscene-driven pending/current HUD component slot replacement. |
| `0x00482050` | `CHud__PromotePendingHudComponent` | Promotes pending HUD component into active slot after render pass. |
| `0x00482210` | `CHud__RenderSegmentedMeterBar` | Draws segmented meter pieces for status/message overlays. |
| `0x00482590` | `CHud__RenderTargetIndicatorOverlay` | Draws target-indicator sprites and health bars. |
| `0x00483530` | `CHud__RenderControllerSlotStatusPanel` | Draws controller-slot timer/status text and meters. |
| `0x00484340` | `CHud__RenderTargetMarkers3D` | Draws 3D target marker sprites from BattleEngine auto-aim position. |
| `0x00484c50` | `CHud__RenderTacticalRadarContacts` | Partitions visible units and renders tactical radar contacts. |
| `0x004858d0` | `CHud__RenderObjectiveProgressGaugeAndHeadingNeedle` | Draws objective progress gauge and heading needle. |
| `0x00485d50` | `CHud__RenderObjectiveStatusPanel` | Draws objective/weapon status text and icons. |
| `0x00486940` | `CHud__RenderObjectiveSlotFillPanel` | Draws weapon energy/ammo slot fill or ammo count. |
| `0x00486e00` | `CHud__RenderWorldTargetSprites` | Draws world-space target/lock sprites. |
| `0x004879e0` | `CHud__RenderOverlayForViewpoint` | Per-viewpoint dispatcher for target, objective, radar, and slot overlays. |
| `0x00487d10` | `CHud__RenderBattleline` | CDXEngine post-render battleline/message-box/influence overlay path. |
| `0x00488090` | `CHud__RenderActiveHudComponentPass` | Active HUD component render pass and deferred component cleanup. |

Read-back evidence:

- Exports: `20` metadata rows, `20` tag rows, `24` xref rows, `7335` instruction rows, and `20` decompile rows.
- Xref graph: lifecycle calls from `CGame__Init`, `CGame__InitRestartLoop`, `CGame__RunLevel`, `CGame__PostLoadProcess`, and `CGame__Shutdown`; cutscene component calls from `CCutscene__Start`, `CCutscene__Stop`, and `CCutscene__Update`; post-render calls from `CDXEngine__PostRender`; overlay helper calls from `CHud__RenderOverlayForViewpoint`.
- Verified backup: `G:\GhidraBackups\BEA_20260606-002152_post_wave1158_hud_render_component_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave1108 current focused accounting after Wave1158 is `485/1179 = 41.14%`; current risk candidates: `6166`; current focused candidates: `1178`; live regenerated current focused candidates: `1178`; remaining active focused work: `694`; focused threshold `15`; not Wave911 reconstruction.

What this proves:

- The twenty HUD lifecycle/component/render rows exist in the saved Ghidra project with clean signatures, comments, tags, decompile exports, body-instruction exports, and xref evidence.
- The observed static call graph ties HUD lifecycle to `CGame`, HUD component changes to `CCutscene`, HUD overlay/render passes to `CDXEngine__PostRender`, and per-viewpoint overlay helpers to `CHud__RenderOverlayForViewpoint`.
- The HUD subsystem now has a rebuild-facing static contract map at `reverse-engineering/binary-analysis/hud-frontend-overlay-static-contract.md`.

What remains separate:

- Runtime HUD behavior.
- Runtime render ordering and visible HUD output.
- Exact concrete `CHud`, `CDXBattleLine`, `CDXCompass`, viewport, component, texture, radar, target, and BattleEngine layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA.
- Clean-room rebuild parity.
