# Ghidra HUD Lifecycle Render Support Review Wave1013 Readiness Note

Status: complete read-only static read-back evidence; no mutation
Date: 2026-05-31
Scope: `hud-lifecycle-render-support-review-wave1013`

Wave1013 re-reviewed a residual Wave911 top-500 HUD lifecycle/render-support tranche after Wave1012. Fresh read-only exports covered HUD init/reset/texture/component setup, selected HUD overlay helpers, CIBuffer configured-create/direct-lock helpers, and LevelBriefingLog lifecycle helpers. The saved project state remained coherent, so the wave made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Read-back evidence |
| --- | --- |
| `0x00481450 CHud__Init` | Called by `0x0046c360 CGame__Init`; initializes HUD-owned compass and BattleLine resources and calls `0x0053bd60 CDXCompass__InitFields`. |
| `0x004815c0 CHud__Reset` | Called by `0x0046c430 CGame__InitRestartLoop`; preserves the saved reset role for HUD flags, marker arrays, and objective/indicator state. |
| `0x00481650 CHud__LoadTextures` | Called by `0x0046e240 CGame__RunLevel`; preserves the saved texture-load role for crosshair/radar/weapon/objective/speaker HUD resources. |
| `0x00481af0 CHud__PostLoadProcess` | Called by `0x0046d040 CGame__PostLoadProcess`; preserved as an `int __thiscall` tail into BattleLine setup. |
| `0x00481f40 CHud__SetHudComponent` | Called by `CCutscene__Start`, `CCutscene__Stop`, and `CCutscene__Update`; preserves pending/current HUD component slot semantics. |
| `0x004821e0 CDXCompass__ApplyRenderStateAdditive` | Called by `0x00427210 CDXCompass__Render`; preserves additive HUD/compass render-state role. |
| `0x00483530` through `0x00486e00` HUD overlay helpers | Re-read as continuity/context with Wave1004; all remain callees of `0x004879e0 CHud__RenderOverlayForViewpoint`. |
| `0x00488330 CIBuffer__CreateConfigured` | `RET 0x10` body stores four stack arguments at CIBuffer offsets `+0x0c/+0x10/+0x14/+0x18`, then dispatches dynamic/static create through vtable slots `+0x04/+0x08`. |
| `0x004885e0 CIBuffer__LockDirect` | Locks the D3D index-buffer pointer at `+0x08`; usage flags at `+0x10` select `0x2800` or `0x800` lock flags. |
| `0x0048f540 CLevelBriefingLog__ctor` | Called by `CGame__InitRestartLoop`; installs vtable `0x005dc208`, clears lifecycle fields, and resolves `FrontEnd_v2/FE_Blank.tga`. |
| `0x0048f5a0` / `0x0048f5c0` | Scalar-deleting destructor wrapper and destructor body remain split correctly; the body releases the `+0x10` texture/ref handle and calls `CMonitor__Shutdown`. |

Fresh read-back evidence:

- Target exports: `16` metadata rows, `16` tag rows, `23` xref rows, `3829` body-instruction rows, and `16` decompile rows.
- Context exports: `9` metadata rows, `23` xref rows, `2075` body-instruction rows, and `9` decompile rows for `CHud__ctor_base`, `CHud__ShutDown`, `CHud__PromotePendingHudComponent`, `HudRenderState__ApplyOverlaySpriteState`, `CHud__RenderOverlay`, `CLevelBriefingLog__Render`, `CDXCompass__InitFields`, `CDXEngine__PostRender`, and `CDXCompass__Render`.
- Logs reported `targets=16 found=16 missing=0`, `rows=16 missing=0`, `Wrote 23 rows`, `Wrote 3829 function-body instruction rows`, `targets=16 dumped=16 missing=0 failed=0`, `targets=9 found=9 missing=0`, `Wrote 2075 function-body instruction rows`, and `targets=9 dumped=9 missing=0 failed=0`, with `REPORT: Save succeeded` and no `LockException`.
- Queue closure remains `6238/6238 = 100.00%`, with `0` commentless functions, `0` exact-`undefined` signatures, and `0` `param_N` signatures.
- Wave911 focused re-audit progress remains `505/1408 = 35.87%`.
- Expanded static surface progress advances to `718/1493 = 48.09%` after counting the eleven new non-Wave1004 top-500 rows in this tranche.
- Wave911 top-500 risk-ranked coverage advances to `420/500 = 84.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified`, `18` files, `173968263` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave1013; `hud-lifecycle-render-support-review-wave1013`; `0x00481450 CHud__Init`; `0x004815c0 CHud__Reset`; `0x00481650 CHud__LoadTextures`; `0x00481af0 CHud__PostLoadProcess`; `0x00481f40 CHud__SetHudComponent`; `0x004821e0 CDXCompass__ApplyRenderStateAdditive`; `0x00488330 CIBuffer__CreateConfigured`; `0x004885e0 CIBuffer__LockDirect`; `0x0048f540 CLevelBriefingLog__ctor`; `0x0048f5a0 CLevelBriefingLog__scalar_deleting_dtor`; `0x0048f5c0 CLevelBriefingLog__dtor`; `505/1408 = 35.87%`; `718/1493 = 48.09%`; `420/500 = 84.00%`; `6238/6238 = 100.00%`; `G:\GhidraBackups\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified`; no mutation.

What this proves:

- The selected HUD lifecycle/render-support rows exist in the saved Ghidra project with the expected names, signatures, comments, and prior static-readback tags.
- The current xref/decompile evidence preserves the CGame-to-HUD setup path, cutscene-driven HUD component swap path, CDXCompass render-state helper path, CIBuffer D3D index-buffer helper semantics, and LevelBriefingLog lifecycle split.
- Five HUD overlay helper rows were intentionally re-read as continuity with Wave1004 rather than counted as new correction targets.

What remains unproven:

- Exact source-body identity.
- Concrete `CHud`, `CDXCompass`, `CIBuffer`, `CLevelBriefingLog`, texture/ref, component, viewport, and D3D object layouts.
- Runtime HUD, briefing-log, compass, or index-buffer behavior.
- Runtime render ordering or visible HUD output.
- BEA patching behavior.
- Rebuild parity.
