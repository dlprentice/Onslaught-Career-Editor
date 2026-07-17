# HUD / frontend overlay static contract

Status: bounded retail static evidence; not visual proof

The analyzed retail specimen maps `CHud` as a lifecycle, component-slot,
per-viewpoint overlay, battleline, and active-component render subsystem.

| Area | Representative static anchors |
| --- | --- |
| Lifecycle | `CHud__Init`, `CHud__Reset`, `CHud__LoadTextures`, `CHud__PostLoadProcess`, `CHud__ShutDown` |
| Component slots | `CHud__SetHudComponent`, `CHud__PromotePendingHudComponent`, `CHud__RenderActiveHudComponentPass`, `CHudComponent__RequestDestroy` |
| Viewpoint overlay | `CHud__RenderOverlayForViewpoint`, `CHud__RenderTargetIndicatorOverlay`, `CHud__RenderWorldTargetSprites`, `CHud__RenderTargetMarkers3D` |
| Objectives and weapons | `CHud__RenderObjectiveStatusPanel`, `CHud__RenderObjectiveSlotFillPanel`, `CHud__RenderSegmentedMeterBar` |
| Radar and status | `CHud__RenderTacticalRadarContacts`, `CHud__RenderControllerSlotStatusPanel`, `HudOverlay__DrawSpriteQuad` |
| Battleline/messages | `CHud__RenderBattleline`, `CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices`, `CMessageBox__RenderOverlay` |

High-level static calls connect game init/reset/load/shutdown to the HUD
lifecycle; cutscene start/stop/update to component selection; and
`CDXEngine__PostRender` to pending-component promotion, battleline rendering,
and the active component pass.

Observed field-role hypotheses include active/pending component slots at
`this+0x1fc` / `this+0x200`, an initialized flag at `this+0x5c`, active
target/viewpoint context around `this+0x50..0x58`, and texture references around
`this+0x154..0x168`. These are not final class-layout names.

MissionScript command-name/handler evidence for HUD and variable operations is
owned by [`missionscript-iscript-static-contract.md`](missionscript-iscript-static-contract.md).
It does not prove visible flashing, variable display, or command effects.

This map supports reconstruction planning and scoped runtime questions. It does
not prove runtime ordering, visible HUD output, exact concrete layouts,
source-body identity, patch behavior, visual fidelity, or rebuild parity.
