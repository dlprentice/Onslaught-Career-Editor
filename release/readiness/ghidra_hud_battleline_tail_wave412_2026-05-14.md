# Ghidra HUD Battleline Tail Correction - 2026-05-14

Status: public-safe static Ghidra evidence note

This note records a serialized saved-Ghidra metadata correction for three HUD battleline/render-tail helpers in the Steam retail `BEA.exe` project. The pass used read-only metadata, tag, xref, decompile, instruction, and source-caller review before a headless dry/apply mutation, then verified the saved project with read-back exports and focused probes.

## Corrected Targets

| Address | Previous saved label | Saved state | Evidence |
| --- | --- | --- | --- |
| `0x00487d10` | `CDXEngine__RenderBattleLineAndInfluenceOverlay` | `void __thiscall CHud__RenderBattleline(void * this, void * viewport)` | Called from `CDXEngine__PostRender`; source caller says `HUD.RenderBattleline(viewport)`; instruction read-back sets `ECX=0x8aa4e8` and pushes one viewport argument; body draws battleline/message-box sprites and dispatches influence-map BattleLine render path. |
| `0x00488090` | `CDXEngine__RenderActiveHudComponentPass` | `void __thiscall CHud__RenderActiveHudComponentPass(void * this)` | Called from `CDXEngine__PostRender` with HUD singleton; active component `+0x1fc`, alpha-sprite state, `CHudComponent__RenderPass`, and cleanup on component `+0x64` done flag. |
| `0x004881e0` | `CVBufTexture__ResolveBlendModeSelector` | `int __thiscall CHud__ResolveOverlaySlotRenderMode(void * this, int slot_index)` | Called by `CDXBattleLine__RenderWorldSpaceOverlay`, `CDXCompass__Render`, and `CVBufTexture__UpdateDynamicOverlayTexture`; every checked callsite sets `ECX=0x8aa4e8` and supplies one slot argument; body reads `+0x34 + slot_index*4`, returns `0`, `1`, or `+0x4c`. |

## Validation Summary

- Headless dry/apply script: `tools/ApplyHudBattlelineTailWave412.java`.
- Focused proof guard: `tools/ghidra_hud_battleline_tail_wave412_probe.py`.
- Focused tests: `tools/ghidra_hud_battleline_tail_wave412_probe_test.py`.
- Package script: `test:ghidra-hud-battleline-tail-wave412`.
- Dry run result: `updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`.
- Apply result: `updated=3 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`.
- Both dry and apply logs included `REPORT: Save succeeded`.
- Read-back verified `3` metadata rows, `3` tag rows, `9` xref rows, `3` target decompile exports, `1` `CDXEngine__PostRender` caller decompile export, `66` PostRender callsite instruction rows, and `133` overlay-slot callsite instruction rows.
- Focused probes passed through both direct Python and the package-script wrapper.
- Refreshed queue telemetry reports `6028` total functions, `1577` commented functions, `4451` commentless functions, `1909` undefined signatures, and `1840` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1577/6028 = 26.16%`; strict clean-signature `1514/6028 = 25.12%`.
- The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260514_101618_post_wave412_hud_battleline_tail_verified` with `19` files, `154831751` bytes, and `HashDiffCount=0`.

## Claim Boundary

This note does not prove runtime HUD behavior, concrete `CHud`/BattleLine/component layouts, exact source-body identity, local-variable or structure recovery, rebuild parity, BEA launch behavior, or game patching. It records saved static Ghidra name/signature/comment/tag correction plus public-safe caller/xref/decompile/instruction evidence.
