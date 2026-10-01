# HUD / frontend overlay static contract

Status: bounded retail static evidence; not visual proof
Last updated: 2026-09-30 (Goodies text rounding and scale-menu renderer; August HUD map retained)
Summary: the Goodies text call preserves fractional Y coordinates; the generic scale-menu renderer distinguishes current and committed values and preserves separate alpha products.
Evidence: MEASURED — September 30 original-code font cases and caller readback, plus the scale-menu full-section/relocation match; August HUD claims were not reverified in this pass.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Goodies text preserves fractional Y — September 30

The Goodies renderer at `0x0045e0d0` passes text flags `0x10` at `0x0045fe3d` to
the font wrapper `0x00540640`. That wrapper forwards the flags to `0x00540010`.
At `0x0054018c`, bit `0x10` selects the path that skips flooring the Y coordinate;
with the bit clear, `0x0054019e` calls the CRT floor routine `0x0055dfe7`. The
private reconstruction previously omitted the flags argument and therefore requested
the default rounding. Its call now passes `0x10`. The complete Goodies renderer
remains unmatched, so this correction does not close the rest of that body.

The lead reproduced 18 bounded original-code cases: two wrapper argument-forwarding
cases and eight finite Y values with the flag both clear and set. For example, clear
flags turn `-0.25` into `-1.0`, whereas `0x10` preserves `-0.25`. The tests execute
the original rounding slice and its actual CRT floor/control-word helpers, check
the exit point, floor-call count, stack and FPU state, and use FPU control word
`0x037f`. They do not execute drawing or a complete font call. Private evidence:
`bea-decomp/.worktrees/codex-frontend-20260930/local-data/frontend-matching-20260930/font_flag_probe.py`
(SHA-256 `dfb50f617d38a8b83a94dc4ba56ac47c1eadd9e65db71ef27be35b5bded7cb4f`);
the lead's reproduced receipt is
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/frontend-matching-20260930/font-flag-probe.json`
(SHA-256 `f34c1d4ccee9ea7a2aa557f801fc1d841d8849d6e4c5c5409667d850f76159d2`).

For reconstruction, preserve the fractional Y path at this call site. No retail or
Godot frame was inspected, and no visible jitter or general font parity is claimed.
A useful presentation falsifier is the same Goodies text at a known fractional Y
position with this bit toggled, keeping the viewport and font inputs fixed.

## Generic scale-menu rendering — September 30

`0x004a37c0` reads the current value at `+0x24`, committed value at `+0x28`, and step count at `+0x2c`.
For a step below both values it selects `0xff00a000`; below neither it keeps `0xff505050`.
A step below only one value enters the time-dependent blend (`0x004a394c`–`0x004a3974`). The
non-selected-item path first copies committed to current and calls the value-change hook
(`0x004a37e2` onward); selection and commit state therefore matter to whether the blend is reachable.

Within the blend, the retail alpha computation multiplies two complementary factors separately by
the **float32** 255.0 constant, then adds them (`0x004a39a7`, `0x004a39af`, `0x004a39b5`). Preserve that
operation structure; factoring the products or substituting a double-width constant did not reproduce
the compiled instructions. The private reconstruction now matches the complete 848-byte section
(843-byte body plus alignment) and all 42 relocations. Lead reproduction retained every earlier match
in the affected objects and full integrated score; receipts are
`bea-decomp/build/menu-render-root-check-20260930.txt` and
`bea-decomp/build/root-score-menu-namedmesh-20260930.log`.

This gives the rebuild a precise generic current-versus-committed rendering contract. It does not
establish a visible defect in its currently live-applied options bars, whose values may already be
committed each change. No fresh game or Godot rendering was inspected. A useful presentation falsifier
is a genuinely deferred bar with differing current/committed values, sampled at known platform times;
player-visible colors and timing remain runtime acceptance work.

## Retained August HUD map

The analyzed retail specimen maps `CHud` as a lifecycle, component-slot,
per-viewpoint overlay, battleline, and active-component render subsystem.

| Area | Representative static anchors |
| --- | --- |
| Lifecycle | `CHud__Init`, `CHud__Reset`, `CHud__LoadTextures`, `CHud__PostLoadProcess`, `CHud__ShutDown` |
| Component slots | `CHud__SetHudComponent`, `CHud__SwitchInOverlay`, `CHud__RenderOverlay`, `CHudComponent__RequestDestroy` |
| Viewpoint overlay | `CHud__RenderOverlayForViewpoint`, `CHud__RenderTargetIndicatorOverlay`, `CHud__RenderWorldTargetSprites`, `CHud__RenderTargetMarkers3D` |
| Objectives and weapons | `CHud__RenderObjectiveStatusPanel`, `CHud__RenderObjectiveSlotFillPanel`, `CHud__RenderSegmentedMeterBar` |
| Radar and status | `CHud__RenderTacticalRadarContacts`, `CHud__RenderControllerSlotStatusPanel`, `HudOverlay__DrawSpriteQuad` |
| Battleline/messages | `CHud__RenderBattleline`, `CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices`, `CMessageBox__RenderOverlay` |

High-level static calls connect game init/reset/load/shutdown to the HUD
lifecycle; cutscene start/stop/update to component selection; and
`CDXEngine__PostRender` to `CHud__Render`, battleline rendering,
`CHud__RenderOverlay`, and `CHud__SwitchInOverlay`, in that order. The three
corrected method identities and their bounded proof are owned by
[`hud-source-identity-correction-2026-08-12.md`](hud-source-identity-correction-2026-08-12.md).

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
