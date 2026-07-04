# LevelBriefingLog.cpp

> Retail static evidence bucket for `CLevelBriefingLog` lifecycle and render helpers in `BEA.exe`.

## Overview

> **Queue status (2026-05-31):** Ghidra export-contract closure **6238/6238** (Wave1013: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

The current repo snapshot of Stuart's source does not provide a directly matching `LevelBriefingLog.cpp` body. These entries are therefore saved retail Ghidra metadata corrections, with source-adjacent owner corroboration where noted, not exact source-body identity proof. Wave808 level-briefing render corrected the render row that sits after `CMessageLog__Render` and before `CPauseMenu__Render` in `CDXEngine__PostRender`; exact anchor: `0x0048f620 CLevelBriefingLog__Render`.

Wave1013 (`hud-lifecycle-render-support-review-wave1013`) re-read the LevelBriefingLog lifecycle split with no mutation. Fresh evidence preserved `0x0048f540 CLevelBriefingLog__ctor` as the vtable/field clear plus `FrontEnd_v2/FE_Blank.tga` texture/ref setup row, `0x0048f5a0 CLevelBriefingLog__scalar_deleting_dtor` as the flag-tested scalar-deleting wrapper, and `0x0048f5c0 CLevelBriefingLog__dtor` as the texture/ref release plus `CMonitor__Shutdown` body. Queue closure remains `6238/6238 = 100.00%`; Wave911 focused re-audit progress remains `505/1408 = 35.87%`; expanded static surface progress is `718/1493 = 48.09%`; Wave911 top-500 risk-ranked coverage is `420/500 = 84.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified`. Runtime briefing-log behavior, exact source-body identity, concrete layout, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1013; hud-lifecycle-render-support-review-wave1013; 0x00481450 CHud__Init; 0x004815c0 CHud__Reset; 0x00481650 CHud__LoadTextures; 0x00481af0 CHud__PostLoadProcess; 0x00481f40 CHud__SetHudComponent; 0x004821e0 CDXCompass__ApplyRenderStateAdditive; 0x00488330 CIBuffer__CreateConfigured; 0x004885e0 CIBuffer__LockDirect; 0x0048f540 CLevelBriefingLog__ctor; 0x0048f5a0 CLevelBriefingLog__scalar_deleting_dtor; 0x0048f5c0 CLevelBriefingLog__dtor; 505/1408 = 35.87%; 718/1493 = 48.09%; 420/500 = 84.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified; no mutation.

## Functions

| Address | Name | Status | Notes |
| --- | --- | --- | --- |
| `0x0048f540` | `CLevelBriefingLog__ctor` | SAVED | Wave423 corrected constructor-like wording; installs vtable `0x005dc208`, clears `+0x04/+0x08/+0x0c`, resolves `FrontEnd_v2/FE_Blank.tga`, stores the texture/ref handle at `+0x10`, and returns `this`. |
| `0x0048f5a0` | `CLevelBriefingLog__scalar_deleting_dtor` | SAVED | Wave423 corrected generic vfunc wording; calls `CLevelBriefingLog__dtor`, checks flags bit `0`, optionally frees `this` through `OID__FreeObject`, and returns `this` with `RET 0x4`. |
| `0x0048f5c0` | `CLevelBriefingLog__dtor` | SAVED | Wave423 corrected constructor-like wording; restores vtable `0x005dc208`, releases the `+0x10` texture/ref handle through `CTexture__DecrementRefCountFromNameField` on `handle+0x08` when present, clears `+0x10`, then calls `CMonitor__Shutdown`. |
| `0x0048f620` | `CLevelBriefingLog__Render` | SAVED | Wave808 corrected stale `CDXEngine__RenderPostMissionOverlayAndMenu` to `CLevelBriefingLog__Render` and saved `void __thiscall CLevelBriefingLog__Render(void * this, void * viewport)`. `CDXEngine__PostRender` callsite `0x0053ee12` loads `ECX` from `DAT_008a9d94`, `0x0053ee18` pushes the viewport/render context, and `0x0053ee19` calls this row; the callee moves `ECX` to `EDI` and exits with `RET 0x4`. |

## Wave808 Render Evidence Boundary

Wave808 (`level-briefing-render-wave808`, `wave808-readback-verified`) saved the render row with read-back artifacts under `subagents/ghidra-static-reaudit/wave808-engine-postmission-overlay/` and public-safe readiness evidence at `release/readiness/ghidra_level_briefing_render_wave808_2026-05-24.md`.

Post-apply decompile/read-back shows `CDXEngine__PostRender` calling `CMessageLog__Render(DAT_008a9d88, ...)`, then `CLevelBriefingLog__Render(DAT_008a9d94, ...)`, then `CPauseMenu__Render(DAT_008a9d8c)`. Stuart-source context in `references/Onslaught/DXEngine.cpp` has the matching post-HUD overlay order: `GAME.GetMessageLog()->Render(viewport)`, `GAME.GetLevelBriefingLog()->Render(viewport)`, and `GAME.GetPauseMenu()->Render()`.

Post-Wave808 queue telemetry is `6098` total, `5583` commented, `515` commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5583/6098 = 91.55%`, strict proxy `5583/6098 = 91.55%`, and next raw commentless row `0x004901e0 MathMatrix3x4__AssignFromEightScalars`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-113054_post_wave808_level_briefing_render_verified`.

Exact concrete layout, exact text-table semantics, runtime level briefing/post-mission overlay behavior, BEA patching, and rebuild parity remain deferred.

## Wave423 Evidence Boundary

Wave423 used fresh metadata, decompile, xref, instruction, and tag read-back before and after the saved Ghidra apply. The dry/apply summaries were:

- Dry: `updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`
- Apply: `updated=4 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`

Post-apply read-back verified `4` metadata rows, `4` tag rows, `5` xref rows, `484` instruction rows, `4` decompile exports, focused probe status `PASS`, and a live Ghidra backup at `[maintainer-local-ghidra-backup-root]\BEA_20260514_163227_post_wave423_level_briefing_messagebox_verified`.

Runtime briefing-log rendering, exact concrete layout, local variable recovery, BEA launch behavior, game patching, and rebuild parity remain unproven.
