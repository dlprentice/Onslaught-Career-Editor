# FEPCommon.cpp - Function Index

> Source File: FEPCommon.cpp | Category: Frontend/Common Video

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Wave1218 (wave1218-generic-shared-vfunc-thunk-tail-current-risk-review) re-read 0x00452da0 SharedVFunc__NoOp_Ret08 as part of the generic/shared vfunc-thunk tail current-risk review. The row remains owner-neutral shared RET 0x8 no-op evidence with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Verified backup: [maintainer-local-ghidra-backup-root]\BEA_20260607-222830_post_wave1218_generic_shared_vfunc_thunk_tail_current_risk_review_verified. Runtime frontend/media behavior, exact owner tables, exact layouts, and rebuild parity remain separate proof.

## Overview

Common frontend-page video helper surface used by multiple frontend pages. Wave 374 corrected the saved Ghidra ownership for the common background-video helpers after source/caller/vtable read-back: the Goodies FMV path calls the common CFEPCommon start/stop helpers, but those helpers are not owned by `CFEPGoodies`.

Wave1030 (`frontend-init-video-fade-review-wave1030`) re-reviewed the cross-file frontend init/video/fade bridge read-only. Primary anchors are `0x004662a0 CFrontEnd__Init`, `0x004679e0 CFrontEnd__RenderPreCommonFade`, and `0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow`; CFEPCommon context includes `0x00452b00 CFEPCommon__Init`, `0x00452b30 CFEPCommon__Shutdown`, `0x00452b60 CFrontEndPage__Process_NoOp`, and `0x00452da0 SharedVFunc__NoOp_Ret08`. Fresh exports verified 3 primary metadata rows, 3 tag rows, 9 xref rows, 481 body-instruction rows, 3 decompile rows, 10 context metadata rows, 10 context tag rows, 354 context xref rows, 221 context body-instruction rows, and 10 context decompile rows. No mutation was needed. Wave911 focused re-audit progress after Wave1030 is `621/1408 = 44.11%`; expanded static surface progress is `850/1493 = 56.93%`; top-500 coverage remains `500/500 = 100.00%`; export-contract closure remains `6238/6238 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-032415_post_wave1030_frontend_init_video_fade_review_verified`. Runtime frontend/video/fade behavior, exact layouts, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1030; frontend-init-video-fade-review-wave1030; 0x004662a0 CFrontEnd__Init; 0x004679e0 CFrontEnd__RenderPreCommonFade; 0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow; 621/1408 = 44.11%; 850/1493 = 56.93%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-032415_post_wave1030_frontend_init_video_fade_review_verified; no mutation.

Wave1147 (`wave1147-frontend-game-shell-score20-current-risk-review`) re-read `0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow` and `0x004679e0 CFrontEnd__RenderPreCommonFade` in the frontend/game shell score20 current-risk review. Fresh exports kept both rows static-consistent; the only saved Wave1147 mutation was a separate comment/tag correction on `GlobalListNode__ClearField4AndPushGlobalList`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified`.

## Functions

| Address | Function | Status | Description |
| --- | --- | --- | --- |
| `0x00452b00` | `CFEPCommon__Init` | Verified static Ghidra boundary | Created missing function object for the CFEPCommon vtable init slot; opens common frontend background video and returns true. |
| `0x00452b30` | `CFEPCommon__Shutdown` | Verified static Ghidra correction | Teardown vfunc that closes frontend video, frees owned `this+0x4` object when present, and clears the pointer. |
| `0x00452db0` | `CFEPCommon__StartVideo` | Verified static Ghidra correction | Corrects former `CFEPGoodies__OpenVideo` / helper labels; used by the Goodies FMV return path and another frontend call site. |
| `0x00452de0` | `CFEPCommon__StopVideo` | Verified static Ghidra correction | Corrects former `CFEPGoodies__CloseVideo` / helper labels; used by the Goodies FMV path. |

## Related Shared Targets

| Address | Function | Status | Description |
| --- | --- | --- | --- |
| `0x00452b60` | `CFrontEndPage__Process_NoOp` | Verified static Ghidra correction | Shared frontend-page process no-op; instruction body is `RET 0x4`. |
| `0x00452da0` | `SharedVFunc__NoOp_Ret08` | Verified static Ghidra correction | Shared no-op target reused by broad unrelated tables; instruction body is `RET 0x8`. |

## Wave 374 Evidence

- Headless dry/apply created `CFEPCommon__Init`, renamed four stale labels, and saved signatures/comments/tags for seven targets.
- Read-back exported metadata, decompile, xrefs, instructions, tags, and vtable slots under ignored `subagents/`.
- Focused probe `npm run test:ghidra-frontend-media-common-video` passed with `7` targets, `10` xref evidence hits, `13` instruction evidence hits, and `4` vtable evidence hits.
- Dependent Goodies read-back passed after refreshing the decompile exports, proving `CFEPGoodies__Process` now references `CFEPCommon__StopVideo` and `CFEPCommon__StartVideo`.

## Claim Boundary

This is static Ghidra evidence only. It does not prove exact CFEPCommon class layout, concrete locals/types, runtime frontend video playback, packaged app behavior, BEA launch behavior, game patching, or rebuild parity.
