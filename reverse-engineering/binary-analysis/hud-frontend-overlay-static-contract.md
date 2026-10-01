# HUD / frontend overlay static contract

Status: bounded retail static evidence; not visual proof
Last updated: 2026-10-01 (menu title snapshot and message construction; August HUD map retained)
Summary: menu title return preserves a pointer from before callbacks; message construction and Goodies requirement text match exactly; bounded font and scale-menu contracts remain.
Evidence: MEASURED — October 1 isolated menu-tail runs and full-section/relocation matches, plus September 30 font and scale-menu readback; August HUD claims were not reverified in this pass.
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

## Options-list title return — October 1

At the options-list renderer `0x004a4810`, DeferredRender returns at `0x004a4c53`.
The load at `0x004a4c57` saves `this+4` (the title pointer) into EDI before the
confirmation query and button-action callbacks. Both return paths (`0x004a4c91`
and `0x004a4cbc`) return that saved pointer. The reconstruction previously reread
the field after those calls; it now snapshots it at the retail boundary.

The lead reproduced 27 isolated x86 integer-tail runs: nine scenarios on each of
the original, previous and corrected tails. Explicit callback substitutions either
leave the title unchanged or replace it during confirmation/action handling. Six
changing-dependency cases distinguish the old reread; the corrected result agrees
with retail in every case. Callback receivers, arguments, ordering, final memory,
stack balance and canaries agree. Earlier rendering, floating-point calculations
and real callback implementations are excluded; their code is not executed by the
probe. This demonstrates the consequence of the ordering under intervention, not
that a live retail callback changes or invalidates the title.

The full renderer remains unmatched (1,232-byte section, 39 relocations); all 18
prior exact controls and 22 other callable sections/relocation destinations are
preserved. Lead private evidence is
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/menu-title-root-20261001/`,
particularly `root-readback.json` and `tail/receipt.json` (SHA-256
`fa3b7e716f5a129c655e69ebfa96b6d0eeeef01eba70de58b2ec31701aae381e`).
For implementation, preserve the snapshot boundary. The cheapest remaining
reachability check traces actual confirmation/action implementations and their
title ownership; no player-visible menu defect is claimed from this probe alone.

## Message construction and Goodies requirement text — October 1

The radio-message constructor `0x004b71e0` now matches all 288 section bytes,
including its 16 relocations (277-byte retail body). Selecting the first speaker's
portrait through the frame member already assigned zero restores the observed
late table load. A different flat-storage source form yields the same exact body,
so the result proves compiled behavior rather than unique original source text.
The table read still precedes its clear; these checks do not establish prior
allocation contents or what later rendering observes. All 35 previous exact
address/symbol pairs and 44 other callable sections are preserved.

The Goodies requirement-text builder `0x0045a940` also matches its full 736-byte
section and 60 relocations (726-byte body). Both text lookups call `0x004f2580`;
using the existing direct PC lookup removes a forwarding wrapper without changing
the targets. The separate Goodies renderer remains unmatched. Lead private owners
in `bea-decomp/.worktrees/codex-equiv-20260930/local-data/` are
`messagebox-ctor-root-20261001/` and `goodies-match-root-20261001/`, each with a
fresh compiled `final-readback.json`. These checks do not establish visual or
audio acceptance.

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
