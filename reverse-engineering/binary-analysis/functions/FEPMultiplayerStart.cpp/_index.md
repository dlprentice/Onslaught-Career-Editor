# FEPMultiplayerStart.cpp - Function Analysis

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Wave1218 (wave1218-generic-shared-vfunc-thunk-tail-current-risk-review) re-read 0x00466290 CWaitingThread__dtor_thunk as part of the generic/shared vfunc-thunk tail current-risk review. The row remains a one-instruction waiting-thread cleanup thunk to 0x00528bf0 CWaitingThread__dtor_body with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Verified backup: G:\GhidraBackups\BEA_20260607-222830_post_wave1218_generic_shared_vfunc_thunk_tail_current_risk_review_verified. Runtime multiplayer/threading behavior, exact waiting-thread layout, and rebuild parity remain separate proof.

**Source File:** `FEPMultiplayerStart.cpp`
**Debug Path String:** `C:\dev\ONSLAUGHT2\FEPMultiplayerStart.cpp` at `0x0063fc24`
**Class:** `CFEPMultiplayerStart` (RTTI: `.?AVCFEPMultiplayerStart@@` string at `0x00629bd0`, type descriptor at `0x00629bc8`)
**Primary Vtable:** `0x005db8d0` (COL `0x00613830` at `0x005db8cc`)

FEP = Front End Page. This page handles the multiplayer setup/start flow in the front-end menu system.

Wave907 (`frontend-input-game-loop-static-review-wave907`) records `CFEPMultiplayerStart` as part of the `static-coherent frontend/input/game-loop core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only). The slice covers `436` rows across `33` families and includes `CFEPMultiplayerStart__Init`, `CFEPMultiplayerStart__ButtonPressed`, `CFrontEnd__Run`, `CFrontEnd__SetPage`, and `CController__SendButtonAction`. Verified backup: `G:\GhidraBackups\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified`. Runtime multiplayer-start/menu/input behavior, visual QA, patch behavior, and rebuild parity remain separate proof.

Correction (2026-02-13):
- The vtable at `0x005db7e0` is **not** `CFEPMultiplayerStart`; it is `CFEPLanguageTest` (RTTI `. ?AVCFEPLanguageTest@@`). See `FEPLanguageTest.cpp/_index.md`.

Correction (2026-05-14):
- Wave399 re-audited the embedded helper cluster at `0x005db4fc`. It preserves the offset-stable `SubObj39B8` and `SubObj8848` names because `FEPMultiplayerStart.cpp` is absent from the current Stuart source snapshot, corrects the constructor/init entries to ECX-this signatures, and corrects `RenderPreCommon` to the observed `RET 0x8` stack-argument shape: `void __stdcall CFEPMultiplayerStart__SubObj8848__RenderPreCommon(float transition, int dest)`.

Correction (2026-05-19):
- Wave569 hardened the queue-head frontend/reconnect tail around `0x00527960`. It saved `CFEPMultiplayerStart__SetCurrentSelection(void * this, int selection_state)`, `CFrontEnd__AdvanceStateAndRelinquishControl(void * this, void * controller, int caller_state_token)`, `CReconnectInterface__ctor(void * this, void * tweak_name, int default_index_one_based)`, and `CReconnectInterface__VFunc_07_00527d00(void * this, float tweak_value)`. This remains retail-static evidence only: `FEPMultiplayerStart.cpp` is absent from the current Stuart source snapshot, and runtime frontend/reconnect behavior remains unproven.

Correction (2026-05-24):
- Wave802 (`frontend-save-multiplayer-wave802`, `wave802-readback-verified`) kept `0x00465f10 CFEPMultiplayerStart__ctor` as the constructor, but corrected adjacent cleanup helper labels: `0x004661c0 DeviceObject__dtor_thunk`, `0x004661f0 CFEPMultiplayerStart__CleanupMissionScriptWaitingThread`, `0x00466290 CWaitingThread__dtor_thunk`, helper body `0x00512d50 DeviceObject__dtor_body`, and helper body `0x00528bf0 CWaitingThread__dtor_body`. The previous init/ctor-like wording for `0x004661f0` is superseded: static read-back shows it adds `0x0c` to `ECX` and jumps to the waiting-thread destructor body for the CMissionScriptObjectCode waiting-thread subobject. Verified backup: `G:\GhidraBackups\BEA_20260524-081932_post_wave802_frontend_save_multiplayer_verified`. Exact owner layout, runtime multiplayer/thread behavior, BEA patching, and rebuild parity remain deferred.

Correction (2026-05-25):
- Wave857 FEPMultiplayerStart runtime (`fepmultiplayerstart-runtime-wave857`, `wave857-readback-verified`) created three previously missing SubObj4034 vtable-slot function objects and saved comments/tags/signatures for eight important multiplayer-start frontend runtime helpers: `0x0051b600 CFEPMultiplayerStart__SubObj4034__ctor`, `0x0051b610 CFEPMultiplayerStart__SubObj4034__ResetFlags`, `0x0051b640 CFEPMultiplayerStart__SubObj4034__Init`, `0x0051b660 CFEPMultiplayerStart__SubObj4034__ButtonPressed`, `0x0051b6b0 CFEPMultiplayerStart__SubObj4034__Process`, `0x0051be70 CFEPMultiplayerStart__SubObj4034__InitRuntimeState`, `0x0051da60 CFEPMultiplayerStart__InitSelection`, and `0x0051ddd0 CFEPMultiplayerStart__HandleInput`. Static evidence ties the rows to SubObj4034 vtable `0x005e49b4`, owner `+0x4034`, FEPMultiplayerStart.cpp debug string `C:\dev\ONSLAUGHT2\FEPMultiplayerStart.cpp`, frontend page transition dispatch, runtime completion gates, primary selection initialization, and render-click input handling. Verified backup: `G:\GhidraBackups\BEA_20260525-121518_post_wave857_fepmultiplayerstart_runtime_verified`. Post-Wave857 queue telemetry is `6101` total, `5770` commented, `331` commentless, and strict proxy `5770/6101 = 94.57%`; next raw commentless row is `0x0051f370 CFEPOptions__GetState`. Exact source method identity, concrete CFEPMultiplayerStart/SubObj4034 layout, runtime multiplayer-start behavior, runtime frontend transition/movie/HUD/input behavior, BEA patching, and rebuild parity remain deferred.

Correction (2026-05-28):
- Wave955 (`fepmultiplayerstart-subobj8848-review-wave955`) re-reviewed the embedded `SubObj8848` multiplayer-start selection helper read-only after fresh serialized Ghidra exports. The pass covered primary Wave911 targets `0x00459920 CFEPMultiplayerStart__SubObj8848__ctor`, `0x004599a0 CFEPMultiplayerStart__SubObj8848__Init`, and `0x00459e50 CFEPMultiplayerStart__SubObj8848__RenderPreCommon`, plus context rows including `0x00459ee0 CFEPMultiplayerStart__SubObj8848__Render`, vtable `0x005db4fc`, and debug path `C:\dev\ONSLAUGHT2\FEPMultiplayerStart.cpp`. Fresh exports verified 15 metadata rows, 15 tag rows, 73 xref rows, 1581 instruction rows, 15 decompile rows, and 20 vtable rows. no mutation was needed: the prior Wave399 constructor/init/render-pre-common signature corrections still hold. Static closure remains `6151/6151 = 100.00%`; Wave911 focused re-audit progress is `286/1408 = 20.31%`. Verified backup: `G:\GhidraBackups\BEA_20260528-103114_post_wave955_fepmultiplayerstart_subobj8848_review_verified`. Runtime multiplayer-start behavior, runtime frontend navigation/rendering behavior, concrete `CFEPMultiplayerStart` and SubObj8848 layout names, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Correction (2026-06-01):
- Wave1030 (`frontend-init-video-fade-review-wave1030`) re-reviewed the frontend init/video/fade bridge read-only and included `0x00459e50 CFEPMultiplayerStart__SubObj8848__RenderPreCommon` as context for the shared video-quad caller. Primary anchors are `0x004662a0 CFrontEnd__Init`, `0x004679e0 CFrontEnd__RenderPreCommonFade`, and `0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow`; the CFEPMultiplayerStart context confirms the Wave399 `SubObj8848__RenderPreCommon` pre-common path still calls the shared video-quad helper without needing mutation. Fresh exports verified 3 primary metadata rows, 3 tag rows, 9 xref rows, 481 body-instruction rows, 3 decompile rows, 10 context metadata rows, 10 context tag rows, 354 context xref rows, 221 context body-instruction rows, and 10 context decompile rows. No mutation was needed. Wave911 focused re-audit progress after Wave1030 is `621/1408 = 44.11%`; expanded static surface progress is `850/1493 = 56.93%`; top-500 coverage remains `500/500 = 100.00%`; export-contract closure remains `6238/6238 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260601-032415_post_wave1030_frontend_init_video_fade_review_verified`. Runtime multiplayer-start/frontend/video/fade behavior, exact source-body identity, exact layouts, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1030; frontend-init-video-fade-review-wave1030; 0x004662a0 CFrontEnd__Init; 0x004679e0 CFrontEnd__RenderPreCommonFade; 0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow; 621/1408 = 44.11%; 850/1493 = 56.93%; 500/500 = 100.00%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-032415_post_wave1030_frontend_init_video_fade_review_verified; no mutation.
- Wave1032 (`tweak-reconnect-interface-review-wave1032`) re-reviewed the adjacent reconnect/tweak handoff rows read-only. It confirmed `0x00527c90 CReconnectInterface__ctor` and `0x00527d00 CReconnectInterface__VFunc_07_00527d00` still match the Wave569 bounded constructor/setter evidence; it also carried `0x00527c50 CFrontEnd__AdvanceStateAndRelinquishControl`, `0x004530a0 CTweak__dtor_base_thunk_004530a0`, `0x00528690 CTweak__ctor_base`, `0x005286b0 CTweak__dtor_base`, `0x00528b20 CTweakInt_SetNumViewpoints__ctor`, and stale non-function context `0x0054d4ac`. Fresh exports verified 5 primary metadata rows, 5 tag rows, 15 xref rows, 58 body-instruction rows, 5 decompile rows, 3 context metadata rows, 3 context tag rows, 53 context xref rows, 19 context body-instruction rows, 3 context decompile rows, 13 xref-site windows / 273 rows, and 3 table windows / 24 rows. No mutation was needed. Wave911 focused re-audit progress after Wave1032 is `631/1408 = 44.82%`; expanded static surface progress is `860/1493 = 57.60%`; top-500 coverage remains `500/500 = 100.00%`; export-contract closure remains `6238/6238 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260601-043550_post_wave1032_tweak_reconnect_interface_review_verified`. Runtime frontend reconnect, landscape-detail, viewpoint, tweak registration/cleanup behavior, exact source-body identity, exact layouts/table schemas, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1032; tweak-reconnect-interface-review-wave1032; 0x00527c90 CReconnectInterface__ctor; 0x00527d00 CReconnectInterface__VFunc_07_00527d00; 0x00528690 CTweak__ctor_base; 0x005286b0 CTweak__dtor_base; 0x00528b20 CTweakInt_SetNumViewpoints__ctor; 0x00527c50 CFrontEnd__AdvanceStateAndRelinquishControl; 0x004530a0 CTweak__dtor_base_thunk_004530a0; 0x0054d4ac; 631/1408 = 44.82%; 860/1493 = 57.60%; 500/500 = 100.00%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-043550_post_wave1032_tweak_reconnect_interface_review_verified; no mutation.

## Vtable Analysis (0x005db8d0)

RTTI CompleteObjectLocator:
- `0x005db8cc` -> `0x00613830`
- `0x00613830 + 0x0c` -> type descriptor `0x00629bc8` (`.?AVCFEPMultiplayerStart@@`)

Primary vtable at `0x005db8d0`:

| Slot | Address | Function | Status |
|------|---------|----------|--------|
| 0 | `0x0051dba0` | `CFEPMultiplayerStart__Init` | Recovered (manual UI `F`), renamed/signed |
| 1 | `0x0051dd90` | `CFEPMultiplayerStart__Shutdown` | Recovered (manual UI `F`), renamed/signed |
| 2 | `0x0051ded0` | `CFEPMultiplayerStart__Process` | Recovered (manual UI `F`), renamed/signed |
| 3 | `0x0051de60` | `CFEPMultiplayerStart__ButtonPressed` | Recovered (manual UI `F`), renamed/signed |
| 4 | `0x0051e120` | `CFEPMultiplayerStart__RenderPreCommon` | Recovered (manual UI `F`), renamed/signed |
| 5 | `0x0051e1b0` | `CFEPMultiplayerStart__Render` | Recovered (manual UI `F`), renamed/signed |
| 6 | `0x0051f350` | `CFEPMultiplayerStart__TransitionNotification` | Recovered (manual UI `F`), renamed/signed |
| 7 | `0x004014c0` | (inherited) | No function object currently |
| 8 | `0x00459990` | (inherited) | No function object currently |

### Embedded Subobject Vtable (0x005db4fc, this+0x8848)

Recovered in headless mode on 2026-02-25 (function-object creation + vtable-slot naming/signatures):

| Slot | Address | Function | Status |
|------|---------|----------|--------|
| 0 | `0x004599a0` | `CFEPMultiplayerStart__SubObj8848__Init` | Recovered (headless create), Wave399 signature/comment/tag hardened |
| 1 | `0x00460490` | `CFEPLevelSelect__SyncSelectionFromCurrentWorld` | Existing mapped helper |
| 2 | `0x00459b00` | `CFEPMultiplayerStart__SubObj8848__Process` | Recovered (headless create), Wave399 comment/tag hardened |
| 3 | `0x00459c10` | `CFEPMultiplayerStart__SubObj8848__ButtonPressed` | Recovered (headless create), Wave399 comment/tag hardened |
| 4 | `0x00459e50` | `CFEPMultiplayerStart__SubObj8848__RenderPreCommon` | Recovered (headless create), Wave399 signature/comment/tag hardened |
| 5 | `0x00459ee0` | `CFEPMultiplayerStart__SubObj8848__Render` | Recovered (headless create), Wave399 comment/tag hardened |
| 6 | `0x00459aa0` | `CFEPMultiplayerStart__SubObj8848__TransitionNotification` | Renamed from legacy `...__ResetSelectionGrid`; Wave399 comment/tag hardened |
| 7 | `0x00459a60` | `CFEPMultiplayerStart__SubObj8848__ActiveNotification` | Recovered (headless create), Wave399 comment/tag hardened |
| 8 | `0x00459990` | `CFrontEndPage__DeActiveNotification` | Inherited/base-style helper |

### Embedded Runtime Subobject Vtable (0x005e49b4, this+0x4034)

Wave857 created the missing function objects for slots 0, 2, and 3 after a clean create dry-run, then saved read-back comments, tags, and signatures for the SubObj4034 runtime helper cluster. The initial metadata apply exposed one fastcall read-back mismatch for `0x0051b640`; the corrective dry/apply/final-dry sequence fixed it and final read-back is clean.

| Slot | Address | Function | Status |
|------|---------|----------|--------|
| 0 | `0x0051b640` | `CFEPMultiplayerStart__SubObj4034__Init` | Wave857 created; clears `this+0x0c`, sets `this+0x14`, calls reset, returns `1` |
| 1 | `0x0040c640` | `DebugTrace` | Existing shared helper |
| 2 | `0x0051b6b0` | `CFEPMultiplayerStart__SubObj4034__Process` | Wave857 created; process gate/timeout/completion/mouse dispatch evidence |
| 3 | `0x0051b660` | `CFEPMultiplayerStart__SubObj4034__ButtonPressed` | Wave857 created; button `0x2c` frontend page transition evidence |

## Debug Path References (Asserts)

The debug path string at `0x0063fc24` is referenced from:
- `0x0051dbd9`
- `0x0051dcb2`

These addresses are within the `CFEPMultiplayerStart__Init` body at `0x0051dba0` (confirmed after manual function-object recovery).

## Known Helpers

| Address | Name | Notes |
|---------|------|------|
| `0x0051da60` | `CFEPMultiplayerStart__InitSelection` | Wave857 saved `void __thiscall ...(void * this, int mode)`. DATA xref `0x005db910`; initializes transition timing, clears an 0x12-dword selection/animation table, and seeds mode `0x0f` state. |
| `0x0051ddd0` | `CFEPMultiplayerStart__HandleInput` | Wave857 saved `void __thiscall ...(void * this, int button, int player_index)`. Called from `CFEPMultiplayerStart__Render` at `0x0051ee7b` / `0x0051ef9e`; handles per-player left/right config-index wraparound and selection pulse fields. |
| `0x00465f10` | `CFEPMultiplayerStart__ctor` | Signature normalized: `void * CFEPMultiplayerStart__ctor(void * this)`; page constructor wrapper setting vtable/members and embedded page helpers. |
| `0x004661d0` | `CFEPMultiplayerStart__ClearJoinedPlayerSet` | Wave 376 saved thiscall signature/comment/tag hardening; constructor/unwind tail-call wrapper adds `+0x20` and jumps to `CSPtrSet__Clear`. |
| `0x004661e0` | `CFEPMultiplayerStart__ClearSecondaryPlayerSet` | Wave 376 saved thiscall signature/comment/tag hardening; constructor/unwind tail-call wrapper adds `+0x28` and jumps to `CSPtrSet__Clear`. |
| `0x004661f0` | `CFEPMultiplayerStart__CleanupMissionScriptWaitingThread` | Wave802 constructor-unwind cleanup wrapper; adds `+0x0c` to ECX and jumps to `CWaitingThread__dtor_body` for the CMissionScriptObjectCode waiting-thread subobject. |
| `0x00512d50` | `DeviceObject__dtor_body` | Wave802 corrected helper body; installs the DeviceObject scalar-deleting destructor vtable and unlinks from global DeviceObject lists rooted at `DAT_00889074` and `DAT_00889078`. |
| `0x00528bf0` | `CWaitingThread__dtor_body` | Wave802 corrected helper body; signals shutdown, waits/closes thread/event handles, resets handle fields to `-1`, and unlinks from `DAT_0089c01c`. |
| `0x00459920` | `CFEPMultiplayerStart__SubObj8848__ctor` | Wave399 saved `void * __thiscall ...(void * this)`. Embedded helper constructor (ECX=`this+0x8848`) used by `CFEPMultiplayerStart__ctor`; sets vtable `0x005db4fc`, zeros compact selection tables, seeds default selection constants, sets row count at `+0x345c`, and clears the 300-entry highlight grid. |
| `0x00459aa0` | `CFEPMultiplayerStart__SubObj8848__TransitionNotification` | Embedded subobject transition-notification path; records timestamp then clears a 300-entry selection grid and sets mode-dependent default highlight (`from_page==5 || from_page==6`). |
| `0x004599a0` | `CFEPMultiplayerStart__SubObj8848__Init` | Wave399 saved `int __thiscall ...(void * this)`. Embedded subobject vtable slot 0 initializer scans the seeded level grid for `DAT_0089d94c`, stores selected row/column at `+0x3468/+0x346c`, computes scroll state, and refreshes timestamps. |
| `0x00459a60` | `CFEPMultiplayerStart__SubObj8848__ActiveNotification` | Embedded subobject active-notification hook (`from_page`); restores current highlight when entered from pages 5/6 and resets inactivity state. |
| `0x00459b00` | `CFEPMultiplayerStart__SubObj8848__Process` | Embedded subobject process hook (`menu_state`); eases scroll state, fades the selection/highlight grid, increments inactivity, and falls back to page `0x0c` after the timeout threshold. |
| `0x00459c10` | `CFEPMultiplayerStart__SubObj8848__ButtonPressed` | Embedded subobject button handler; handles horizontal/vertical navigation, select/back page transitions, sound feedback, selected-level update, clamping, and timestamp refresh. |
| `0x00459e50` | `CFEPMultiplayerStart__SubObj8848__RenderPreCommon` | Wave399 saved `void __stdcall ...(float transition, int dest)`, correcting the stale `void * this, float transition` shape. Instruction read-back shows `RET 0x8`, transition stack-argument use, no saved `this` use, and scaled video-quad backdrop rendering. |
| `0x00459ee0` | `CFEPMultiplayerStart__SubObj8848__Render` | Embedded subobject render hook (`transition`, `dest`); renders the selection grid/cell effects, selected level and episode text, `E3 2002` build/progress string, help prompts, overlay effects, and title bar. |
| `0x00459810` | `CFEPMultiplayerStart__SubObj39B8__QueuePageId` | Embedded helper method (ECX=`this+0x39b8`) that queues the startup page id (`DAT_0066304c`) during `CFrontEnd__Init`. |
| `0x0051b600` | `CFEPMultiplayerStart__SubObj4034__ctor` | Wave857 saved `void __fastcall ...(void * this)`. Constructor called from `CFEPMultiplayerStart__ctor` at `0x00466049`; installs vtable `0x005e49b4` and initializes the owner+0x4034 helper. |
| `0x0051b610` | `CFEPMultiplayerStart__SubObj4034__ResetFlags` | Wave857 saved `void __fastcall ...(void * this)`. Resets runtime flags at `this+0x0c/+0x10` and global gate `DAT_00677614`, with platform/global guard `DAT_0083d448`; called by the created init/process helpers. |
| `0x0051b640` | `CFEPMultiplayerStart__SubObj4034__Init` | Wave857 created the vtable-slot function object and saved `int __fastcall ...(void * this)`. Clears `this+0x0c`, sets `this+0x14`, calls `CFEPMultiplayerStart__SubObj4034__ResetFlags`, and returns `1`. |
| `0x0051b660` | `CFEPMultiplayerStart__SubObj4034__ButtonPressed` | Wave857 created the vtable-slot function object and saved `void __thiscall ...(void * this, int button, float val)`. Handles button `0x2c`, clears `DAT_006630cc`, selects page/time from `DAT_008a9ab4` and `DAT_0083d448`, calls `CFrontEnd__SetPage`, and plays frontend sound `1`. |
| `0x0051b6b0` | `CFEPMultiplayerStart__SubObj4034__Process` | Wave857 created the vtable-slot function object and saved `void __thiscall ...(void * this, int state)`. Checks state, movie/HUD gates, dev-mode timeout dispatch, completion globals `DAT_00677614/DAT_00677624/DAT_0067762c`, and mouse/full-window dispatch. |
| `0x0051be70` | `CFEPMultiplayerStart__SubObj4034__InitRuntimeState` | Wave857 saved `void __fastcall ...(void * this)`. Seeds runtime timestamp (`PLATFORM__GetSysTimeFloat`), clears transition/scene globals, calls `CFEPMultiplayerStart__SetCurrentSelection`, and clears subobject state at `+0x18`. |
| `0x00527960` | `CFEPMultiplayerStart__SetCurrentSelection` | Wave569 saved `void __thiscall ...(void * this, int selection_state)`. The body stores `selection_state` at `this+0x08`; `RET 0x4` confirms one explicit stack argument, and `CFEPMultiplayerStart__SubObj4034__InitRuntimeState` calls it for the `DAT_0089be50` / `DAT_0089be5c` slots. |
| `0x00527c50` | `CFrontEnd__AdvanceStateAndRelinquishControl` | Wave569 saved `bool __thiscall ...(void * this, void * controller, int caller_state_token)`. The helper advances state `1` to `2`, relinquishes `controller` and clears state when state is `3`, and consumes a second currently unread stack token proven by `RET 0x8`. |
| `0x00527c90` | `CReconnectInterface__ctor` | Wave569 saved `void * __thiscall ...(void * this, void * tweak_name, int default_index_one_based)`. The constructor calls `CTweak__ctor_base`, stores the name/key pointer, installs vtable `0x005e4a80`, stores `default_index_one_based - 1`, clears the explicit-set flag, and returns `this`. |
| `0x00527d00` | `CReconnectInterface__VFunc_07_00527d00` | Wave569 saved `void __thiscall ...(void * this, float tweak_value)`. The vtable/data-referenced setter rounds the float, stores it at `this+0x0c`, and marks `this+0x10`; direct CLI callers are the `-landscape0/-landscape1/-landscape2` parse paths. Exact class ownership remains bounded to current retail evidence. |

Naming note:
- The `SubObjXXXX` labels are intentional offset-stable names for embedded helpers where source-parity class names are not yet available in the reference drop.
- Wave 376 corrected `0x00452fd0`, `0x004530b0`, and `0x00453140` away from `CFEPMultiplayerStart`-only ownership to shared `FEPShared__RenderSelectionBrackets`, `FEPShared__RenderSelectionMarker`, and `FEPShared__RenderContextHelpPrompt` because xrefs span multiple frontend pages.

## Recovery Status

The vtable entrypoints were previously missing as Ghidra function objects and could not be created safely via MCP without risking UI deadlock/timeouts. They were recovered via manual CodeBrowser create (`F` in Listing) and then renamed/signed/commented via MCP with immediate read-back verification (2026-02-13).

Additional recovery (2026-02-25):
- Embedded subobject vtable `0x005db4fc` missing entrypoints (`0x004599a0`, `0x00459a60`, `0x00459b00`, `0x00459c10`, `0x00459e50`, `0x00459ee0`) were created in headless mode and then renamed/signed with decompile read-back verification.

Wave399 re-audit (2026-05-14):
- Serialized headless dry/apply/read-back updated comments/tags on all nine selected embedded helpers and corrected saved signatures for `0x00459920`, `0x004599a0`, and `0x00459e50`.
- Metadata/decompile/xref/tag/instruction/vtable read-back verified the saved state. Runtime multiplayer behavior, exact source identity, concrete layouts, locals/types, BEA launch, game patching, and rebuild parity remain unproven.

## Wave1151 Current-Risk Tag Normalization

Wave1151 tag-only normalization also covers `0x004661c0 DeviceObject__dtor_thunk` as a score21 current-risk row. It preserves the DeviceObject destructor-thunk evidence used by frontend video/startup cleanup and adds Wave1151/current-risk tags only. Verified backup: `G:\GhidraBackups\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
