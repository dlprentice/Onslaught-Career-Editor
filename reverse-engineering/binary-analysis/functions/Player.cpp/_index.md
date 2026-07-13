# Player.cpp Function Mappings

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x004d2b40` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Functions from `references/Onslaught/Player.cpp` mapped to `BEA.exe`.

> **Queue status (2026-05-28):** Ghidra export-contract closure **6211/6211** (Wave974: every function object commented with clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview
- **Functions Mapped:** 13
- **Status:** ACTIVE (Wave472 hardened AssignBattleEngine stack-argument signature)
- **Class:** `CPlayer`

Wave907 (`frontend-input-game-loop-static-review-wave907`) records `CPlayer` as part of the `static-coherent frontend/input/game-loop core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only). The slice covers `436` rows across `33` families and includes `CPlayer__AssignBattleEngine`, `CGame__RunLevel`, `CGame__MainLoop`, `CFrontEnd__Run`, and `CController__DoMappings`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified`. Runtime player-view/input behavior, visual QA, patch behavior, and rebuild parity remain separate proof.

## Function List

| Address | Name | Status | Link |
|---------|------|--------|------|
| 0x004d2780 | CPlayer__ctor | NAMED/SIGNATURED | [View](CPlayer__ctor.md) |
| 0x004d2810 | CPlayer__scalar_deleting_dtor | NAMED/SIGNATURED | [View](CPlayer__dtor.md) |
| 0x004d2830 | CPlayer__dtor_base | NAMED/SIGNATURED | [View](CPlayer__dtor.md) |
| 0x004d28a0 | CPlayer__Init | NAMED/SIGNATURED | [View](CPlayer__ViewHelpers.md) |
| 0x004d28c0 | CPlayer__GotoFPView | NAMED/SIGNATURED | [View](CPlayer__ViewHelpers.md) |
| 0x004d29c0 | CPlayer__Goto3rdPersonView | NAMED/SIGNATURED | [View](CPlayer__ViewHelpers.md) |
| 0x004d2a50 | CPlayer__GotoControlView | NAMED/SIGNATURED | [View](CPlayer__ViewHelpers.md) |
| 0x004d2a70 | CPlayer__GetCurrentViewPoint | NAMED/SIGNATURED | [View](CPlayer__SnapshotHelpers.md) |
| 0x004d2ae0 | CPlayer__GetCurrentViewOrientation | NAMED/SIGNATURED | [View](CPlayer__SnapshotHelpers.md) |
| 0x004d2b40 | CPlayer__GetOldCurrentViewPoint | NAMED/SIGNATURED | [View](CPlayer__SnapshotHelpers.md) |
| 0x004d2bb0 | CPlayer__GetOldCurrentViewOrientation | NAMED/SIGNATURED | [View](CPlayer__SnapshotHelpers.md) |
| 0x004d2c10 | CPlayer__GotoPanView | NAMED | [View](CPlayer__GotoPanView.md) |
| 0x004d3080 | CPlayer__AssignBattleEngine | NAMED/SIGNATURED | [View](CPlayer__AssignBattleEngine.md) |
| 0x004d3110 | CPlayer__ReceiveButtonAction | Wave974 source-backed boundary recovery | static note below |

## Notes
- Wave974 (`battleengine-jet-animation-review-wave974`) recovered `0x004d3110 CPlayer__ReceiveButtonAction` as a source-backed function-boundary recovery while re-reading BattleEngine/JetPart input anchors `0x00409e80 CBattleEngine__AutoZoomOut`, `0x0040eeb0 CBattleEngine__FinishedPlayingCurrentAnimation`, `0x0040ef20 CBattleEngine__GroundParticleEffect`, `0x00410310 CBattleEngineJetPart__Thrust`, `0x00410490 CBattleEngineJetPart__Turn`, and `0x00410670 CBattleEngineJetPart__Pitch`. Static evidence ties the row to `references/Onslaught/Player.cpp` lines 283-511, `RET 0x0c`, DATA pointer `0x005de77c`, reverse-look Y-axis inversion, nonlinear tan response curve, walker part `+0x578` dispatch, and jet part `+0x57c` dispatch to `CBattleEngineJetPart__Turn/Pitch/YawLeft/YawRight/Thrust`. Final post exports verified 7 metadata rows, 7 tag rows, 10 xref rows, 749 body-instruction rows, and 7 decompile rows. Wave911 focused re-audit progress is `356/1408 = 25.28%`; expanded static surface progress is `415/1467 = 28.29%`; export-contract closure is `6211/6211 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-210511_post_wave974_battleengine_jet_animation_review_verified`. Exact `CPlayer`, `CController`, `CBattleEngine`, walker-part, and jet-part layouts, exact button enum names, runtime controller/input behavior, camera behavior, jet flight feel, animation behavior, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave974; battleengine-jet-animation-review-wave974; 0x004d3110 CPlayer__ReceiveButtonAction; 0x00410310 CBattleEngineJetPart__Thrust; 0x00410490 CBattleEngineJetPart__Turn; 0x00410670 CBattleEngineJetPart__Pitch; 356/1408 = 25.28%; 415/1467 = 28.29%; 6211/6211 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-210511_post_wave974_battleengine_jet_animation_review_verified; function-boundary recovery.
- Wave24 corrected prior mislabels where `0x004d28c0`/`0x004d29c0` were incorrectly tracked as ctor/dtor.
- Wave470 corrected the remaining stale constructor/destructor docs, saved signatures/comments/tags for `0x004d2780` through `0x004d2a50`, and tied the lifecycle/view helpers back to `Player.cpp` / `Player.h` source evidence.
- Wave471 hardened the four current/old view point/orientation snapshot helpers to explicit hidden-return/output pointer signatures and documented the 16-byte vector / 48-byte matrix fallback paths.
- Wave472 hardened `CPlayer__AssignBattleEngine` to one stack argument (`battle_engine`) from `[ESP + 0x4]`, `RET 0x4`, and four caller callsites.
- Camera-mode selectors and current/old view snapshot accessors are now explicitly separated in symbol names.
- Wave262 saved `CPlayer__AssignBattleEngine` after source/decompile/xref read-back; Wave472 resolved its stale extra parameter but field types and runtime behavior remain deferred.
- Runtime camera/player behavior, exact `CPlayer`/`CBattleEngine` layout, BEA launch, game patching, and rebuild parity remain deferred beyond this static correction.

## Wave764 Player.cpp Unwind Continuation

Wave764 static read-back (`unwind-continuation-wave764`, `wave764-readback-verified`) saved comments/tags/signatures for Player.cpp-adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d46c8 Unwind@005d46c8` through `0x005d47d2 Unwind@005d47d2` as `void __cdecl Unwind@...(void)` rows. Evidence includes Player.cpp debug path `0x00631690`, DATA scope-table xrefs `0x0061cf4c` through `0x0061d04c`, active-reader cleanup, monitor shutdown thunks, `CGenericCamera__dtor(*(EBP-0x14))`, and Player.cpp allocation-cleanup rows with line/allocation tokens `0x3a/0x26`, `0x43/0x26`, `0xa0/0x28`, `0xbc/0x28`, and `0xbe/0x26`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-152957_post_wave764_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime player/camera cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

## Related
- Source: `references/Onslaught/Player.cpp`
- Header: `references/Onslaught/Player.h`
- Parent: [../_index.md](../_index.md)
