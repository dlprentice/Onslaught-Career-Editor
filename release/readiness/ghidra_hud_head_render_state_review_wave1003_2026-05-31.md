# Ghidra HUD Head Render-State Review Wave1003 Readiness Note

Status: complete static read-back evidence; one boundary recovery
Date: 2026-05-31
Scope: `hud-head-render-state-review-wave1003`

Wave1003 re-reviewed the HUD head/render-state cluster around the prior Wave400 HUD corrections, then followed the `CHud__ShutDown` caller edge into a missed game lifecycle boundary. Fresh pre-context evidence showed `0x0046c990` was outside any saved Ghidra function even though DATA refs at `0x005dbbbc` and `0x005e50a4` point at it and the body is source-aligned with `references/Onslaught/game.cpp:CGame::Shutdown`. The wave created exactly one function object, `0x0046c990 CGame__Shutdown`, saved the source-backed signature/comment/tags, and made no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Read-back evidence |
| --- | --- |
| `0x0046c990 CGame__Shutdown` | New recovered function boundary. DATA refs `0x005dbbbc` and `0x005e50a4`; source parity with `CGame::Shutdown`; body calls `CHud__ShutDown`, `CGameInterface__Shutdown`, particle/static-shadow/imposter/engine/map/mesh/texture cleanup, memory-manager merge/cleanup, outro FMV, and console status/command cleanup before `0x0046ca6b RET`. |
| `0x00481b00 CHud__ShutDown` | Now has a direct call edge from `0x0046c9ac` inside `CGame__Shutdown`; existing Wave400 HUD shutdown metadata remains coherent. |
| `0x00481400 CHud__ctor_base` through `0x00482210 CHud__RenderSegmentedMeterBar` | Existing Wave400 HUD head and render-state rows re-read with expected names, signatures, comments, tags, xrefs, decompile, and instruction evidence. |

Fresh read-back evidence:

- Pre exports: `12` metadata rows, `12` tag rows, `30` xref rows, `1268` body-instruction rows, and `12` decompile rows for the HUD cluster.
- Boundary context exports: `0x0046c990` and `0x0046c9ac` were missing as function entries before the mutation, while `0x0046ca70 CGame__ShutdownRestartLoop` was already present; instruction context showed `0x0046c98e RET`, the orphan body from `0x0046c990` through `0x0046ca6b RET`, and the separate `0x0046ca70` function start.
- Apply script: `ApplyCGameShutdownBoundaryWave1003.java` dry/apply/final dry reported `updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=2 missing=0 bad=0`, then `updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=2 missing=0 bad=0`, then `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports: `13` metadata rows, `13` tag rows, `32` xref rows, `1324` body-instruction rows, and `13` decompile rows.
- Queue closure is `6223/6223 = 100.00%`, with `0` commentless functions, `0` exact-`undefined` signatures, and `0` `param_N` signatures.
- Wave911 focused re-audit progress remains `472/1408 = 33.52%`.
- Expanded static surface candidate-set progress is `641/1478 = 43.37%`, plus one newly recovered out-of-seed boundary.
- Wave911 top-500 risk-ranked coverage is `371/500 = 74.20%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-120949_post_wave1003_hud_head_render_state_review_verified`, `19` files, `173869959` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave1003; `hud-head-render-state-review-wave1003`; `0x0046c990 CGame__Shutdown`; `0x00481b00 CHud__ShutDown`; `0x00481400 CHud__ctor_base`; `0x00482090 HudRenderState__ApplyOverlaySpriteState`; `0x004821b0 CDXCompass__ApplyRenderStateModulate`; `0x00482210 CHud__RenderSegmentedMeterBar`; `472/1408 = 33.52%`; `641/1478 = 43.37%`; `371/500 = 74.20%`; `6223/6223 = 100.00%`; `G:\GhidraBackups\BEA_20260531-120949_post_wave1003_hud_head_render_state_review_verified`; function-boundary recovery.

What this proves:

- `0x0046c990` now exists in the saved Ghidra project as `CGame__Shutdown` with the expected source-backed `void __fastcall CGame__Shutdown(void * this)` signature, Wave1003 tags, and bounded comment.
- The recovered boundary connects the CGame lifecycle documentation to the previously saved `CHud__ShutDown` row through a direct call edge from `0x0046c9ac`.
- The reviewed HUD head/render-state rows remain coherent after fresh metadata, tag, xref, instruction, and decompile read-back.

What remains unproven:

- Exact source-body identity.
- Concrete `CGame`, `CHud`, renderer, texture, memory-manager, and lifecycle layouts.
- Runtime shutdown behavior.
- Runtime HUD behavior.
- BEA patching behavior.
- Rebuild parity.
