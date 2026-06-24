# HUD / Frontend Overlay Visual Runtime Proof Plan

Status: active public-safe proof plan, not runtime proof
Last updated: 2026-06-08
Scope: HUD/frontend overlay planning from the saved static contract

This plan is the next selected static-to-proof slice from `roadmap/static-to-proof-rebuild-transition-backlog.md` after the destroyable-segments proof-plan slice. It converts the static `hud-frontend-overlay-static-contract.md` evidence into a bounded visual/runtime proof plan only, with explicit capture targets, copied-profile guardrails, exact-layout unknowns, and stop conditions. No screenshot or runtime claim until app-owned capture is run. It does not launch BEA, mutate Ghidra, mutate the installed game, patch an executable, capture screenshots, start Godot work, or claim runtime HUD behavior, visible HUD output, visual QA, or rebuild parity.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; it is not the active completion gate.

The percentage front door remains `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md` and `reverse-engineering/binary-analysis/static-reaudit-progress.json`. This proof plan does not create a new static RE percentage.

Primary static contract source: `reverse-engineering/binary-analysis/hud-frontend-overlay-static-contract.md`.

Relevant retained evidence:

- Wave1158 HUD render/component review (`wave1158-hud-render-component-current-risk-review`): `20` HUD rows, `24` xref rows, `7335` instruction rows, and `20` decompile rows, with verified backup `G:\GhidraBackups\BEA_20260606-002152_post_wave1158_hud_render_component_current_risk_review_verified`.
- Wave1216 render/resource/texture/HUD tail review (`wave1216-render-resource-texture-hud-tail-current-risk-review`): `7` tail rows, `12` xref rows, `962` instruction rows, `7` decompile rows, `28` context xref rows, `1015` context instruction rows, `9` context decompile rows, `6` texture-context xref rows, `111` texture-context instruction rows, `6` texture-context decompile rows, and `13` data-xref rows, with verified backup `G:\GhidraBackups\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified`.
- Wave1141 CDXCompass/HUD review for `HudRenderState__ApplyOverlaySpriteState`, `CDXCompass__ApplyRenderStateModulate`, and `CDXCompass__ApplyRenderStateAdditive` context.
- Wave907 `frontend-input-game-loop-static-review-wave907` frontend/input/game-loop static review for broader frontend entry points and menu/game-loop context.

## Static Anchors

The proof plan is built around saved retail Ghidra evidence, not source-body identity. Stuart source labels are useful for planning, but exact source-body identity and concrete layouts remain unproven unless a later proof slice establishes them.

| Surface | Static anchor |
| --- | --- |
| Post-render spine | `0x0053ecc0 CDXEngine__PostRender` reaches `0x00487bc0 CHud__RenderOverlay`, `0x00487d10 CHud__RenderBattleline`, `0x00488090 CHud__RenderActiveHudComponentPass`, and `0x00482050 CHud__PromotePendingHudComponent`. |
| Lifecycle | `0x00481400 CHud__ctor_base`, `0x00481450 CHud__Init`, `0x004815c0 CHud__Reset`, `0x00481650 CHud__LoadTextures`, `0x00481af0 CHud__PostLoadProcess`, and `0x00481b00 CHud__ShutDown`. |
| Component slot handoff | `0x00481f40 CHud__SetHudComponent`, `0x00482050 CHud__PromotePendingHudComponent`, `0x004de860 CHudComponent__RenderPass`, `0x00488090 CHud__RenderActiveHudComponentPass`, and `0x0054b800 CHudComponent__RenderPassEntry`. |
| Per-viewpoint overlay dispatcher | `0x004879e0 CHud__RenderOverlayForViewpoint` dispatches target, objective, radar, slot, and world-target helpers. |
| Target overlays | `0x00482590 CHud__RenderTargetIndicatorOverlay`, `0x00484340 CHud__RenderTargetMarkers3D`, and `0x00486e00 CHud__RenderWorldTargetSprites`. |
| Objective/weapon panels | `0x00482210 CHud__RenderSegmentedMeterBar`, `0x004858d0 CHud__RenderObjectiveProgressGaugeAndHeadingNeedle`, `0x00485d50 CHud__RenderObjectiveStatusPanel`, and `0x00486940 CHud__RenderObjectiveSlotFillPanel`. |
| Radar/status panels | `0x00483530 CHud__RenderControllerSlotStatusPanel` and `0x00484c50 CHud__RenderTacticalRadarContacts`. |
| Battleline/message overlay | `0x00487d10 CHud__RenderBattleline`, `CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices`, and `CMessageBox__RenderOverlay`. |
| Texture/resource tail | `0x0054b800 CHudComponent__RenderPassEntry`, HUD texture refs in the `this+0x154` through `this+0x168` range, and Wave1216 texture-node label corrections. |
| Render-state setup | `0x004857e0 HudOverlay__DrawSpriteQuad`, `0x00482090 HudRenderState__ApplyOverlaySpriteState`, `0x004821b0 CDXCompass__ApplyRenderStateModulate`, and `0x004821e0 CDXCompass__ApplyRenderStateAdditive`. |
| Frontend/menu side | `0x004662a0 CFrontEnd__Init`, `0x004684d0 CFrontEnd__Run`, `0x00468200 CFrontEnd__Render`, `0x00468700 CFrontEnd__RenderCursorEndSceneAndAsyncSave`, `0x004679e0 CFrontEnd__RenderPreCommonFade`, `0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow`, `0x00465a20 TextLayout__WrapWideTextToFixedLines`, `0x004659a0 CDXFont__DrawTextScaledWithShadow`, `0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput`, and `0x00472f10 CGameInterface__Render`. |

Fresh Wave1158 xrefs keep the runtime-proof target bounded:

- `CGame__Init`, `CGame__InitRestartLoop`, `CGame__RunLevel`, `CGame__PostLoadProcess`, and `CGame__Shutdown` call HUD lifecycle rows.
- `CCutscene__Start`, `CCutscene__Stop`, and `CCutscene__Update` call `CHud__SetHudComponent`.
- `CDXEngine__PostRender` calls `CHud__PromotePendingHudComponent`, `CHud__RenderBattleline`, and `CHud__RenderActiveHudComponentPass`.
- `CHud__RenderOverlay` calls `CHud__RenderOverlayForViewpoint`.
- `CHud__RenderOverlayForViewpoint` calls target-indicator, controller-status, target-marker, tactical-radar, objective, slot-fill, and world-target helpers.

## Static Field Roles To Preserve

These are static role labels for proof planning. Do not promote them to final C++ field names until exact layout proof exists.

| Offset / slot | Planned role in later proof |
| --- | --- |
| `this+0x30` | BattleLine/HUD post-load setup target in current comments. |
| `this+0x50`, `this+0x54`, `this+0x58` | Active target/viewpoint context used by per-viewpoint overlay helpers. |
| `this+0x5c` | Initialized/lifecycle flag seeded by init/reset paths. |
| `this+0x68`, `this+0x94`, `this+0x98`, `this+0xac` | Controller/status panel animation fields. |
| `this+0x9c` | Active-reader cell region initialized by the constructor. |
| `this+0x154`, `this+0x158`, `this+0x160`, `this+0x164`, `this+0x168` | HUD texture references used by segmented meter and target-indicator paths. |
| `this+0x1fc` | Active HUD component slot. |
| `this+0x200` | Pending HUD component slot. |

## Future Proof Checklist

The first executable proof after this plan should be scoped and copied-profile only. This plan records the expected evidence shape; it does not run that proof.

| Row | Planned proof item | Required evidence | Public-safe result |
| --- | --- | --- | --- |
| 1 | Candidate scene/viewpoint selection | Identify one narrow selected scenario, such as main frontend render plus one copied-profile in-level HUD overlay that shows target/objective/radar surfaces and a stable viewpoint without broad gameplay proof. | Sanitized level/state description, or a deferred note if no safe candidate is selected. |
| 2 | Static-to-runtime arm points | Choose one or two non-invasive observation anchors, preferably `CHud__RenderOverlayForViewpoint`, `CHud__RenderBattleline`, `CHud__RenderActiveHudComponentPass`, or `CHudComponent__RenderPassEntry`. | VA/function anchor and why it is scoped. |
| 3 | Capture design | Define a reversible app-owned capture path for one frame set or short bounded clip from a copied profile. | Capture plan only; no screenshot claim until capture is actually run. |
| 4 | Expected visual surfaces | Separately check target indicator, objective/status panel, radar/contact markers, weapon/slot fill, battleline/message overlay, and active HUD component pass. | Per-surface planned pass/fail rows, not a single broad HUD claim. |
| 5 | Texture/resource boundary | Tie visible HUD surfaces back to HUD texture refs and Wave1216 texture-node corrections only when later capture plus static refs agree. | Texture linkage claim remains separate from runtime pixel correctness. |
| 6 | Layout restraint | Keep offsets as static role labels until runtime/layout evidence proves concrete fields. | Unknown-layout table remains explicit. |
| 7 | Stop conditions | Stop on crash, non-reproducible state, ambiguous viewpoint/object identity, blank capture, missing HUD surface, unverified patch bytes, private artifact leakage, unexpected file mutation, or any need to touch the installed game. | Documented blocked/deferred status instead of widening scope. |
| 8 | Rebuild handoff | Translate proven static-only behavior into HUD overlay pseudocode only after the future proof result says which rows were observed. | Static pseudocode with runtime and visual gaps marked. |

## Copied-Profile Guardrails

Any later runtime/proof execution must:

- Use copied profiles or app-owned artifact roots only.
- Never mutate the installed Steam game directory or the original `BEA.exe`.
- Verify byte/specimen assumptions before any patch candidate is considered.
- Keep screenshots, frames, videos, memory dumps, debugger logs, and patch outputs out of public release scope unless separately sanitized.
- Keep raw CDB/debugger output and private file paths in ignored evidence.
- Use a single selected level/state/viewpoint target; do not broaden into full frontend, game-loop, Unit/BattleEngine, render-device, or texture-decode proof.

## Not Claimed

This plan is a static-to-proof planning artifact only. It does not prove:

- No screenshot/capture proof.
- Runtime HUD behavior.
- Runtime menu behavior.
- Runtime render ordering.
- Visible HUD output.
- Target/radar/objective/battleline visual correctness.
- Runtime texture or GPU upload behavior.
- Exact concrete `CHud`, viewport, component, texture, radar, target, BattleEngine, `CDXBattleLine`, or `CDXCompass` layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Exit Gate For This Planning Slice

This planning slice is complete only when:

- This document and its lore-book mirror match.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `reverse-engineering/binary-analysis/_index.md`, and `reverse-engineering/RE-INDEX.md` point to this plan.
- `reverse-engineering/binary-analysis/hud-frontend-overlay-static-contract.md` points to this plan without changing its static claim boundary.
- `release/readiness/hud_frontend_overlay_visual_runtime_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/hud_frontend_overlay_visual_runtime_proof_plan_probe.py --check` passes.
- Static closeout probes still pass without changing `static-reaudit-progress.json` or `static-reaudit-current-risk-ledger.json`.
