# CGame__Shutdown

> Address: `0x0046c990` | Source: `references/Onslaught/game.cpp:414`

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void __fastcall CGame__Shutdown(void * this)`)
- **Verified vs Source:** Source-aligned (`references/Onslaught/game.cpp:CGame::Shutdown`)
- **Wave:** Wave1003 (`hud-head-render-state-review-wave1003`)

## Purpose

Top-level level/game shutdown path before restart-loop teardown:

- stops music when enabled
- shuts down HUD and game-interface state
- clears particle, shadow, imposter, engine, map, mesh, texture, and waypoint resources
- toggles memory-manager merge behavior and runs cleanup
- runs outro FMV handling
- updates console shutdown status and clears command/variable lists

## Evidence

Wave1003 recovered this function boundary after `CHud__ShutDown` caller review found `0x0046c9ac` outside any saved Ghidra function. Static read-back evidence:

- DATA refs at `0x005dbbbc` and `0x005e50a4` point to `0x0046c990`.
- Pre-context instructions show `0x0046c98e RET` ending `CGame__InitRestartLoop`, orphan instructions from `0x0046c990` through `0x0046ca6b RET`, and the separate `0x0046ca70 CGame__ShutdownRestartLoop` entry.
- Post-read-back decompile shows calls to `CMusic__Stop`, `CHud__ShutDown`, `CGameInterface__Shutdown`, particle/static-shadow/imposter/engine/map/mesh/texture cleanup, `MEM_MANAGER__Cleanup`, `CGame__RunOutroFMV`, and console status/clear helpers.
- Apply script `ApplyCGameShutdownBoundaryWave1003.java` dry/apply/final dry passed, created one function object, and saved `hud-head-render-state-review-wave1003` / `wave1003-readback-verified` tags.
- Verified backup: `G:\GhidraBackups\BEA_20260531-120949_post_wave1003_hud_head_render_state_review_verified`.

Probe token anchor: Wave1003; `hud-head-render-state-review-wave1003`; `0x0046c990 CGame__Shutdown`; `0x00481b00 CHud__ShutDown`; `0x00481400 CHud__ctor_base`; `0x00482090 HudRenderState__ApplyOverlaySpriteState`; `0x004821b0 CDXCompass__ApplyRenderStateModulate`; `0x00482210 CHud__RenderSegmentedMeterBar`; `472/1408 = 33.52%`; `641/1478 = 43.37%`; `371/500 = 74.20%`; `6223/6223 = 100.00%`; `G:\GhidraBackups\BEA_20260531-120949_post_wave1003_hud_head_render_state_review_verified`.

## Boundary

This is static retail Ghidra evidence. Exact source-body identity, concrete `CGame`/HUD/engine/resource layouts, runtime shutdown behavior, BEA patching behavior, and rebuild parity remain separate proof.
