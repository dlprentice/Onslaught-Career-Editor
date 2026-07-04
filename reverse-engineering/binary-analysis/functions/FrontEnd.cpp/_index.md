# FrontEnd.cpp - Function Index

> Source File: FrontEnd.cpp | Category: Frontend/Menu System

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Main frontend menu system controller. CFrontEnd is the master class that owns and coordinates all 24 frontend page (FEP) objects. It handles initialization, page transitions, and the main menu loop.

**Debug Path**: `[maintainer-local-source-export-root]\FrontEnd.cpp` at 0x00629df0

Wave802 static read-back (`frontend-save-multiplayer-wave802`, `wave802-readback-verified`) added two frontend-wide correction anchors: `0x0044d390 FEMessBox__Create` for the shared message-box create path and `0x00465640 CFMV__PlayFullscreenWithLoadingGate` for the full-screen FMV wrapper reached by frontend/game callsites. The FMV wrapper toggles `CController__SetNonInteractiveSection`, conditionally forwards `g_LanguageIndex`, dispatches vtable slot `+0x2c`, and clears the gate. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-081932_post_wave802_frontend_save_multiplayer_verified`. Runtime frontend dialog/video behavior, exact layouts, BEA patching, and rebuild parity remain deferred.

Wave907 (`frontend-input-game-loop-static-review-wave907`) records `CFrontEnd` and adjacent FEP/page/controller rows as part of the `static-coherent frontend/input/game-loop core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only). The slice covers `436` rows across `33` families and includes `CFrontEnd__Run`, `CFrontEnd__SetPage`, `CFrontEnd__ReceiveButtonAction`, `CFrontEnd__RenderCursorEndSceneAndAsyncSave`, `CFEPMultiplayerStart__Init`, `CFEPOptions__WriteDefaultOptionsFile`, and `CController__DoMappings`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified`. Runtime frontend navigation, input behavior, visual QA, patch behavior, and rebuild parity remain separate proof.

Wave951 (`game-interface-lifecycle-wave951`) re-reviewed the CGame/GameInterface lifecycle bridge read-only with no mutation: `0x0046c210 CGame__ctor`, `0x0046c2d0 CGame__dtor`, `0x004729d0 CGameInterface__ctor_base`, `0x004729e0 CGameInterface__ResetMenuState`, and `0x00472ad0 CGameInterface__AdvanceMenuSelectionWithWrap`, plus caller context `0x0046c360 CGame__Init` and `0x0046c430 CGame__InitRestartLoop`. Fresh static exports confirm the saved Wave382/GameInterface menu-state boundary and Wave385/CGame lifecycle boundary. Wave911 focused re-audit progress after Wave951 is `271/1408 = 19.25%`; export-contract closure remains `6150/6150 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-083735_post_wave951_game_interface_lifecycle_review_verified`. Exact GameInterface source-body identity, concrete CGame/GameInterface layouts, runtime pause/menu/input/render behavior, BEA patching, and rebuild parity remain separate proof.

Wave1118 (`wave1118-particle-message-current-risk-review`) re-read `0x004729d0 CGameInterface__ctor_base` as part of the score-26 particle/message current-risk head with a fresh read-only Ghidra export and no mutation. The row remains the constructor-style base body for the global GameInterface object: it initializes the base monitor/control field at `this+0x04` and installs vtable `0x005dbc2c`. Current focused accounting moves to `100/1179 = 8.48%`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260605-021103_post_wave1118_particle_message_current_risk_review_verified`. Runtime menu/input behavior, exact source-body identity, concrete layout, BEA patching, and rebuild parity remain separate proof.

Wave1147 (`wave1147-frontend-game-shell-score20-current-risk-review`) re-read frontend/game shell rows including `0x004662a0 CFrontEnd__Init`, `0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow`, `0x004679e0 CFrontEnd__RenderPreCommonFade`, `0x004729e0 CGameInterface__ResetMenuState`, and `0x00472ad0 CGameInterface__AdvanceMenuSelectionWithWrap`. The only saved mutation was the adjacent `GlobalListNode__ClearField4AndPushGlobalList` comment/tag correction to `ParticleEffectLink__PushGlobalList`; the FrontEnd/GameInterface rows remained static-consistent. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified`.

Wave952 (`game-interface-menu-control-boundary-wave952`) recovered `0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput` from CGameInterface vtable `0x005dbc2c slot 3` after pre-metadata proved no function object at that entry. Static evidence ties the recovered body to button/control IDs `0x2a..0x39`, `RET 0x0c`, selection motion through `CGameInterface__AdvanceMenuSelectionWithWrap`, selection execution through `CGameInterface__HandleMenuSelection`, controller unwinding through `CController__RelinquishControl`, and unpause through `CGame__UnPause`. Wave911 focused re-audit progress after Wave952 is `276/1408 = 19.60%`; export-contract closure is `6151/6151 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-091135_post_wave952_game_interface_menu_control_boundary_verified`. Exact source method name, individual button semantics, `0x00679fbc` meaning, runtime pause/menu/input behavior, BEA patching, and rebuild parity remain separate proof.

Wave953 (`cfepmain-menu-review-wave953`) re-reviewed the retail CFEPMain main-menu page cluster read-only with fresh metadata/tags/xref/instruction/decompile/vtable exports. It verified `0x004621d0 CFEPMain__GetMenuType`, `0x004621e0 CFEPMain__GetActionCount`, `0x00462b70 CFEPMain__RenderPreCommon`, and `0x00462c90 CFEPMain__Update` from the Wave911 focused candidates plus the full eleven-row CFEPMain Wave401 slice and frontend context anchors. Fresh evidence preserved the vtable correction that `0x005dbae4` is the full CFEPMain dispatch slice, `0x005dbaf0` starts with `CFEPMain__ButtonPressed`, and `0x005dbb00` starts with `CFEPMain__ActiveNotification`; debug string `0x00629414` remains `[maintainer-local-source-export-root]\FEPMain.cpp`. No mutation was needed. Wave911 focused re-audit progress after Wave953 is `280/1408 = 19.89%`; export-contract closure remains `6151/6151 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-093826_post_wave953_cfepmain_menu_review_verified`. Runtime main-menu behavior, exact source identity, concrete CFEPMain layout, BEA patching, and rebuild parity remain separate proof.

Wave956 (`cfepdemo-main-review-wave956`) re-reviewed the compact `CFEPDemoMain` demo-menu vtable slice read-only with fresh metadata/tags/xref/instruction/decompile/vtable exports. It verified `0x00457ec0 CFEPDemoMain__GetMenuType`, `0x00457ed0 CFEPDemoMain__GetActionCount`, `0x00457ee0 CFEPDemoMain__DoAction`, and `0x00457f20 CFEPDemoMain__Update`, plus CFEPMain/frontend context anchors `0x004623e0 CFEPMain__DoAction`, `0x004644d0 CFEPMain__TransitionNotification`, `0x00464520 CFEPMain__ActiveNotification`, `0x00466ae0 CFrontEnd__SetPage`, `0x004679e0 CFrontEnd__RenderPreCommonFade`, and `0x00468770 CFrontEnd__PlaySound`. Fresh evidence preserved the vtable `0x005db7c0` slots 3-6 mapping and the mixed data-table pointer `0x005e4a78`; no mutation was needed. Wave911 focused re-audit progress after Wave956 is `290/1408 = 20.60%`; export-contract closure remains `6151/6151 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-105733_post_wave956_cfepdemo_main_review_verified`. Runtime demo-menu behavior, runtime frontend navigation/rendering behavior, concrete `CFEPDemoMain` layout names, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave957 (`cfepdevelopment-world-list-review-wave957`) re-reviewed the `CFEPDevelopment` world-list/storage-device slice read-only with fresh metadata/tags/xref/instruction/decompile exports. It verified primary Wave911 targets `0x004584d0 CFEPDevelopment__Render` and `0x00458ce0 CFEPDevelopment__ResolveActiveStorageDevice`, plus context anchors `0x00458050 CFEPDevelopment__CompareWorldFileNamePtrs`, `0x00458090 CFEPDevelopment__EnumerateWorldFiles`, stale-boundary guard `0x00458100`, `0x004583c0 CFEPDevelopment__RenderWorldListEntries`, `0x00458710 CFEPDevelopment__RefreshWorldListCore`, `0x004589f0 CFEPDevelopment__RefreshWorldList`, `0x00459580 CFEPDevelopment__ScheduleWorldListRefresh`, `0x004623e0 CFEPMain__DoAction`, `0x00466ae0 CFrontEnd__SetPage`, and `0x00468770 CFrontEnd__PlaySound`. Fresh evidence preserved the Wave384 boundary and calling-convention corrections; no mutation was needed. Layout notes stay mode-qualified because world-file listing, storage/save refresh, and timer scheduling share offsets. Wave911 focused re-audit progress after Wave957 is `292/1408 = 20.74%`; export-contract closure remains `6151/6151 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-111610_post_wave957_cfepdevelopment_world_list_review_verified`. Runtime development-menu reachability, runtime world-list/storage-device/save-dialog behavior, exact source-body identity, concrete `CFEPDevelopment` layout names, BEA patching, and rebuild parity remain separate proof.

Wave1030 (`frontend-init-video-fade-review-wave1030`) re-reviewed the frontend init/video/fade bridge read-only with fresh metadata/tags/xref/instruction/decompile exports. It verified `0x004662a0 CFrontEnd__Init`, `0x004679e0 CFrontEnd__RenderPreCommonFade`, and `0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow`, plus context in `0x00466ae0 CFrontEnd__SetPage`, `0x00468770 CFrontEnd__PlaySound`, `0x00462b70 CFEPMain__RenderPreCommon`, `0x00459e50 CFEPMultiplayerStart__SubObj8848__RenderPreCommon`, and CFEPCommon/CDXFrontEndVideo helper rows. Fresh exports verified 3 primary metadata rows, 3 tag rows, 9 xref rows, 481 body-instruction rows, 3 decompile rows, 10 context metadata rows, 10 context tag rows, 354 context xref rows, 221 context body-instruction rows, and 10 context decompile rows. No mutation was needed. Wave911 focused re-audit progress after Wave1030 is `621/1408 = 44.11%`; expanded static surface progress is `850/1493 = 56.93%`; top-500 coverage remains `500/500 = 100.00%`; export-contract closure remains `6238/6238 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-032415_post_wave1030_frontend_init_video_fade_review_verified`. Runtime frontend behavior, runtime video behavior, runtime transition visuals, exact CFrontEnd/CFEPCommon/CFEPMain/CFEPMultiplayerStart/CDXFrontEndVideo layouts, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1030; frontend-init-video-fade-review-wave1030; 0x004662a0 CFrontEnd__Init; 0x004679e0 CFrontEnd__RenderPreCommonFade; 0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow; 621/1408 = 44.11%; 850/1493 = 56.93%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-032415_post_wave1030_frontend_init_video_fade_review_verified; no mutation.

Wave1032 (`tweak-reconnect-interface-review-wave1032`) re-reviewed the CTweak / CReconnectInterface / frontend handoff cluster read-only. It confirmed `0x00527c50 CFrontEnd__AdvanceStateAndRelinquishControl`, `0x004530a0 CTweak__dtor_base_thunk_004530a0`, `0x00527c90 CReconnectInterface__ctor`, `0x00527d00 CReconnectInterface__VFunc_07_00527d00`, `0x00528690 CTweak__ctor_base`, `0x005286b0 CTweak__dtor_base`, `0x00528b20 CTweakInt_SetNumViewpoints__ctor`, and stale non-function context `0x0054d4ac` with no mutation. Fresh exports verified 5 primary metadata rows, 5 tag rows, 15 xref rows, 58 body-instruction rows, 5 decompile rows, 3 context metadata rows, 3 context tag rows, 53 context xref rows, 19 context body-instruction rows, 3 context decompile rows, 13 xref-site windows / 273 rows, and 3 table windows / 24 rows. Wave911 focused re-audit progress after Wave1032 is `631/1408 = 44.82%`; expanded static surface progress is `860/1493 = 57.60%`; top-500 coverage remains `500/500 = 100.00%`; export-contract closure remains `6238/6238 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-043550_post_wave1032_tweak_reconnect_interface_review_verified`. Runtime frontend reconnect, landscape-detail, viewpoint, tweak registration/cleanup behavior, exact source-body identity, exact layouts/table schemas, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1032; tweak-reconnect-interface-review-wave1032; 0x00527c90 CReconnectInterface__ctor; 0x00527d00 CReconnectInterface__VFunc_07_00527d00; 0x00528690 CTweak__ctor_base; 0x005286b0 CTweak__dtor_base; 0x00528b20 CTweakInt_SetNumViewpoints__ctor; 0x00527c50 CFrontEnd__AdvanceStateAndRelinquishControl; 0x004530a0 CTweak__dtor_base_thunk_004530a0; 0x0054d4ac; 631/1408 = 44.82%; 860/1493 = 57.60%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-043550_post_wave1032_tweak_reconnect_interface_review_verified; no mutation.

## Functions

| Address | Function | Status | Description |
|---------|----------|--------|-------------|
| 0x004662a0 | [CFrontEnd__Init](./CFrontEnd__Init.md) | RENAMED | Initialize all 24 frontend pages and set initial state |
| 0x00466980 | [CFrontEnd__GetPlayer0ControllerPort](./CFrontEnd__GetPlayer0ControllerPort.md) | RENAMED | Returns player-0 controller port (normalizes unset sentinel) |
| 0x004669a0 | [CFrontEnd__ReceiveButtonAction](./CFrontEnd__ReceiveButtonAction.md) | RENAMED | Frontend controller button dispatch, controller selection, cheat-button, modal/page routing |
| 0x00466990 | [CFrontEnd__NumControllersPresent](./CFrontEnd__NumControllersPresent.md) | RENAMED | Returns number of controller ports available to frontend |
| 0x00466ab0 | [CFrontEnd__SetLanguage](./CFrontEnd__SetLanguage.md) | RENAMED | Switch frontend text/language resource set |
| 0x00466ae0 | [CFrontEnd__SetPage](./CFrontEnd__SetPage.md) | RENAMED | Page transition helper (immediate or timed transition) |
| 0x00466ba0 | [CFrontEnd__Process](./CFrontEnd__Process.md) | RENAMED | Per-frame frontend update body (event manager, controllers, pages, message box) |
| 0x00466de0 | [CFrontEnd__DrawLine](./CFrontEnd__DrawLine.md) | RENAMED | Draws line sprite between two points |
| 0x00466e70 | [CFrontEnd__DrawBox](./CFrontEnd__DrawBox.md) | RENAMED | Draws box via four edge lines |
| 0x00467010 | [CFrontEnd__DrawPanel](./CFrontEnd__DrawPanel.md) | RENAMED | Draws clamped blank-panel rectangle |
| 0x004670b0 | [CFrontEnd__DrawBarGraph](./CFrontEnd__DrawBarGraph.md) | RENAMED | Draws panel-backed proportional bar fill |
| 0x00467200 | [CFrontEnd__DrawSlidingTextBordersAndMask](./CFrontEnd__DrawSlidingTextBordersAndMask.md) | RENAMED | Transition bracket/mask animation renderer |
| 0x004679a0 | [FrontEnd__HasStandardSlidingTextBordersAndMaskPage](./FrontEnd__HasStandardSlidingTextBordersAndMaskPage.md) | RENAMED | Source-static page-style predicate used by border/mask renderer |
| 0x004679e0 | [CFrontEnd__RenderPreCommonFade](./CFrontEnd__RenderPreCommonFade.md) | RENAMED | Clamps transition alpha and renders pre-common full-window fade |
| 0x00467ae0 | [CFrontEnd__DrawBar](./CFrontEnd__DrawBar.md) | RENAMED | Draws segmented header/title bar |
| 0x00467bd0 | [CFrontEnd__DrawTitleBar](./CFrontEnd__DrawTitleBar.md) | RENAMED | Draws animated title-bar visuals and text |
| 0x004681c0 | [CFrontEnd__EnableAdditiveAlpha](./CFrontEnd__EnableAdditiveAlpha.md) | RENAMED | Sets additive blend mode (ONE/ONE) |
| 0x004681e0 | [CFrontEnd__EnableModulateAlpha](./CFrontEnd__EnableModulateAlpha.md) | RENAMED | Sets alpha-modulate blend mode (SRCALPHA/INVSRCALPHA) |
| 0x00468200 | [CFrontEnd__Render](./CFrontEnd__Render.md) | RENAMED | Frontend render pass used by Run's `while (!Render())` loop |
| 0x004684d0 | [CFrontEnd__Run](./CFrontEnd__Run.md) | RENAMED | Main frontend loop - runs Init then calls `CFrontEnd__Process` |
| 0x004685a0 | [CFrontEnd__UpdateCamera](./CFrontEnd__UpdateCamera.md) | RENAMED | Source-bridged frontend camera view/projection update |
| 0x004685f0 | [CFrontEnd__RenderStart](./CFrontEnd__RenderStart.md) | RENAMED | Source-bridged frontend render-start vfunc reached from CDXFrontEnd |
| 0x00468700 | [CFrontEnd__RenderCursorEndSceneAndAsyncSave](./CFrontEnd__RenderCursorEndSceneAndAsyncSave.md) | RENAMED | Renders cursor, optionally ends scene, and schedules async career save |
| 0x00468730 | [CFrontEnd__GetShadowOffsetX](./CFrontEnd__GetShadowOffsetX.md) | RENAMED | Computes animated X shadow offset |
| 0x00468750 | [CFrontEnd__GetShadowOffsetY](./CFrontEnd__GetShadowOffsetY.md) | RENAMED | Computes animated Y shadow offset |
| 0x00468770 | [CFrontEnd__PlaySound](./CFrontEnd__PlaySound.md) | RENAMED | UI sound helper (move/select/back) |
| 0x004691c0 | [CFrontEnd__ReleaseParticleHudWaypointResources](./CFrontEnd__ReleaseParticleHudWaypointResources.md) | RENAMED | Releases frontend particle, HUD handle, waypoint, mesh, and texture resources |
| 0x00469390 | [CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture](./CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture.md) | RENAMED | Modal mouse gate and rectangle dispatch helper |
| 0x004693d0 | [CFrontEnd__GetCursorStateInRect](./CFrontEnd__GetCursorStateInRect.md) | RENAMED | Modal mouse gate wrapper around cursor-state rectangle query |
| 0x00469400 | [CFrontEnd__GetClickStateInRect](./CFrontEnd__GetClickStateInRect.md) | RENAMED | Modal mouse gate wrapper around click-state rectangle query |
| 0x00469430 | [CFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady](./CFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady.md) | RENAMED | Directory-page cursor-state consume wrapper |
| 0x00469550 | [CFrontEnd__ResolveLevelNameTextByCode](./CFrontEnd__ResolveLevelNameTextByCode.md) | RENAMED | Resolves level code to localized wide text with fallback |

## Wave751 Unwind Cleanup Evidence (2026-05-22)

Wave751 saved two FrontEnd.cpp-adjacent compiler-generated SEH unwind cleanup callbacks with the `unwind-continuation-wave751` and `wave751-readback-verified` tags. Both are static retail Ghidra evidence only, saved as `void __cdecl Unwind@...(void)`, with no renames, no function-boundary changes, and no executable-byte changes.

| Address | Evidence |
| --- | --- |
| `0x005d2730 Unwind@005d2730` | DATA scope-table xref `0x0061b5a4`; calls `OID__FreeObject_Callback` with FrontEnd.cpp debug path `0x00629df0`, line `0x27`, allocation/type value `0xb3`, pointer `*(EBP-0x24)`. |
| `0x005d2760 Unwind@005d2760` | DATA scope-table xref `0x0061b5cc`; calls `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on stack-local descriptors at `EBP-0x434`. |

The same Wave751 tranche continues through game.cpp and monitor.h cleanup evidence from `0x005d2730 Unwind@005d2730` through `0x005d29d8 Unwind@005d29d8`. Read-back backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-204801_post_wave751_unwind_continuation_verified`. Next high-signal queue head is `0x005d29f1 Unwind@005d29f1`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`. Exact parent source-body identity, runtime frontend cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Wave750 Unwind Cleanup Evidence (2026-05-22)

Wave750 saved twelve FrontEnd.cpp-adjacent compiler-generated SEH unwind cleanup callbacks with the `unwind-continuation-wave750` and `wave750-readback-verified` tags. All are static retail Ghidra evidence only, saved as `void __cdecl Unwind@...(void)`, with no renames, no function-boundary changes, and no executable-byte changes.

| Address | Evidence |
| --- | --- |
| `0x005d2680 Unwind@005d2680` | DATA scope-table xref `0x0061b504`; calls `CMonitor__Shutdown_Thunk` with `*(EBP-0x14)`. |
| `0x005d2688 Unwind@005d2688` | DATA scope-table xref `0x0061b50c`; calls `CGenericCamera__dtor` on `(*(EBP-0x14))+0x8`. |
| `0x005d2693 Unwind@005d2693` | DATA scope-table xref `0x0061b514`; dispatches `DeviceObject__ctor_like_00512d50` with ECX derived from `(*(EBP-0x14))+0x1c4`. |
| `0x005d26a1 Unwind@005d26a1` | DATA scope-table xref `0x0061b51c`; calls `CFEPMultiplayerStart__ClearJoinedPlayerSet` on `(*(EBP-0x14))+0x2bc`. |
| `0x005d26af Unwind@005d26af` | DATA scope-table xref `0x0061b524`; calls `CFEPMultiplayerStart__ClearSecondaryPlayerSet` on `(*(EBP-0x14))+0x2ec`. |
| `0x005d26bd Unwind@005d26bd` | DATA scope-table xref `0x0061b52c`; dispatches `CWaitingThread__ctor_like_00528bf0` with ECX derived from `(*(EBP-0x10))+0xc`. |
| `0x005d26c8 Unwind@005d26c8` | DATA scope-table xref `0x0061b534`; dispatches `CFEPMultiplayerStart__InitWaitingThreadSubsystem` with ECX derived from `(*(EBP-0x14))+0x37dc`. |
| `0x005d26e0 Unwind@005d26e0` | DATA scope-table xref `0x0061b55c`; calls `CMonitor__Shutdown_Thunk` with `*(EBP-0x10)`. |
| `0x005d26e8 Unwind@005d26e8` | DATA scope-table xref `0x0061b564`; calls `CGenericCamera__dtor` on `(*(EBP-0x10))+0x8`. |
| `0x005d26f3 Unwind@005d26f3` | DATA scope-table xref `0x0061b56c`; dispatches `DeviceObject__ctor_like_00512d50` with ECX derived from `(*(EBP-0x10))+0x1c4`. |
| `0x005d2701 Unwind@005d2701` | DATA scope-table xref `0x0061b574`; calls `CFEPMultiplayerStart__ClearJoinedPlayerSet` on `(*(EBP-0x10))+0x2bc`. |
| `0x005d270f Unwind@005d270f` | DATA scope-table xref `0x0061b57c`; calls `CFEPMultiplayerStart__ClearSecondaryPlayerSet` on `(*(EBP-0x10))+0x2ec`. |

Read-back backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-193422_post_wave750_unwind_continuation_verified`. Exact parent source-body identity, constructor/unwind direction for the constructor-like dispatches, runtime frontend cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Headless Semantic Wave118 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x00452ce0 | CFrontEnd__RenderVideoQuadScaledToWindow | Pre-common render helper that resolves default window-scaled center coordinates and renders the frontend video quad (`CDXFrontEndVideo__Render`); Wave 374 hardened the saved signature to `scale`, `argb`, `center_x`, and `center_y`. |
| 0x00469390 | CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture | Input gate wrapper: returns mouse-ready mask when active, otherwise dispatches frontend click actions through the Wave567 lower-level input rectangle helper; Wave 377 hardened the saved rectangle/context signature. |
| 0x00469550 | CFrontEnd__ResolveLevelNameTextByCode | Maps level/world numeric codes to localized text IDs with fallback to `\"Unnamed Level\"`; Wave 377 hardened the saved wide-text return signature. |

## Wave567 Input/Cursor Callee Refinement (2026-05-18)

Wave567 refined the lower-level cursor/click callees reached by the frontend wrappers. Treat the frontend rectangle arguments as left/top/right/bottom bounds. The saved lower-level helpers are `CDXEngine__GetCursorStateInRect`, `Input__DispatchClickInRect`, `Input__GetClickStateInRect`, and `Input__GetCursorStateInRectAndConsume`. This remains static Ghidra evidence only; runtime mouse/frontend behavior remains unproven.

## Headless Semantic Wave119 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x004691c0 | CFrontEnd__ReleaseParticleHudWaypointResources | Cleanup helper that destroys particle-manager state, clears HUD-owned handles, frees waypoint/mesh transient resources, and nulls retained pointers. |

## Headless Semantic Wave121 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x00469c20 | CFrontEnd__ResolveEpisodeNameTextByIndex | Resolves episode indices (`1..8`) to localized episode-name strings with fallback to `\"Unnamed Episode\"`. |
| 0x00469cf0 | CFrontEnd__ResolveLevelNameTextIdByCode | Resolves level/world numeric code to localized text-id; returns `-1` when unmapped. |
| 0x0046a210 | FrontEnd__GetBriefingLevelListTextColor | Wave 378 supersedes the old fallback text-id label; the body returns `0xffffdf5f`, and caller context treats it as a draw-color value. |

## Headless Semantic Wave122 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x00472ad0 | CGameInterface__AdvanceMenuSelectionWithWrap | Wave 382 supersedes the older `UISelectionList__AdvanceToNextEnabledWithWrap` label; advances the GameInterface selected menu entry with wrap-around, disabled-entry checks, and move SFX when selection changes. |

## Wave 382 GameInterface / Pause Menu Corrections (2026-05-13)

| Address | Name | Notes |
|---------|------|-------|
| 0x004729d0 | CGameInterface__ctor_base | Constructor-style global GameInterface base body that installs the `0x005dbc2c` vtable and initializes monitor/control state. |
| 0x004729e0 | CGameInterface__ResetMenuState | Resets menu fade/selection/menu-active state, enables six menu entries, enables background rendering, and sets menu mode `1`. |
| 0x00472a10 | CGameInterface__InitResources | Source-parity resource init for joypad and menu-background textures. |
| 0x00472a50 | CGameInterface__Shutdown | Source-parity texture release/slot-clear body followed by monitor shutdown core logic. |
| 0x00472a90 | CGameInterface__ToggleMenuDisplay | Source-parity menu toggle that changes menu-active state, selects first enabled entry, and switches mouse input state. |
| 0x00472ad0 | CGameInterface__AdvanceMenuSelectionWithWrap | Corrected GameInterface selection-advance helper with wrap-around and disabled-entry checks. |
| 0x00472b40 | CGameInterface__HandleMenuSelection | Corrected pause-menu selection handler; callsite evidence shows one explicit controller parameter, not the older three-parameter decompiler artifact. |
| 0x00472d50 | CGameInterface__VFunc_03_HandleMenuControlInput | Wave952 recovered CGameInterface vtable `0x005dbc2c slot 3`; dispatches button/control IDs `0x2a..0x39`, calls selection advance/execute, `CController__RelinquishControl`, and `CGame__UnPause`; exact runtime behavior remains separate proof. |
| 0x00472f10 | CGameInterface__Render | Corrected GameInterface pause/menu render-process body called from `CDXEngine::PostRender`. |

These are saved static Ghidra name/signature/comment/tag refinements. Runtime pause-menu/input/options/text/render behavior, exact layouts, locals/types, and rebuild parity remain unproven.

## Wave 368 Modal Panel Signature Pass (2026-05-13)

| Address | Name | Notes |
|---------|------|-------|
| 0x0044d6f0 | CFrontEnd__RenderAndProcessModalPanel | Saved `void * frontend` receiver signature; draws modal panel context, processes modal type state, and calls the modal button handler. |
| 0x0044dd60 | CFrontEnd__HandleModalPanelButton | Corrects the older helper-only reference to a saved two-stack-argument modal button handler signature. |
| 0x0044dea0 | CFrontEnd__IsMouseInputReady | Saved boolean modal/mouse-input readiness predicate. |

These are saved static Ghidra signatures/comments/tags only. Exact widget layout, runtime frontend behavior, and rebuild parity remain unproven.

## Wave 374 Frontend/Common Video Correction (2026-05-13)

| Address | Name | Notes |
|---------|------|-------|
| 0x00452b00 | CFEPCommon__Init | Created missing CFEPCommon vtable init-slot function object. |
| 0x00452b30 | CFEPCommon__Shutdown | Saved teardown vfunc signature/comment/tag. |
| 0x00452b60 | CFrontEndPage__Process_NoOp | Saved shared frontend-page process no-op signature. |
| 0x00452ce0 | CFrontEnd__RenderVideoQuadScaledToWindow | Hardened four-stack-argument render helper signature. |
| 0x00452da0 | SharedVFunc__NoOp_Ret08 | Corrected older slot-specific label to shared `RET 0x8` no-op behavior. |
| 0x00452db0 | CFEPCommon__StartVideo | Corrected former Goodies-owned open-video helper to CFEPCommon ownership. |
| 0x00452de0 | CFEPCommon__StopVideo | Corrected former Goodies-owned close-video helper to CFEPCommon ownership. |

These are saved static Ghidra boundary/name/signature/comment/tag refinements. Runtime frontend video playback, exact CFEPCommon layout, and rebuild parity remain unproven.

## Wave 376 Shared Frontend Helper Corrections (2026-05-13)

| Address | Name | Notes |
|---------|------|-------|
| 0x00452fd0 | FEPShared__RenderSelectionBrackets | Corrected from old `CFEPMultiplayerStart`-only ownership; shared bracket renderer called by multiple frontend pages. |
| 0x004530b0 | FEPShared__RenderSelectionMarker | Corrected from old `CFEPMultiplayerStart`-only ownership; shared marker renderer with x/y/scale/alpha arguments. |
| 0x00453140 | FEPShared__RenderContextHelpPrompt | Corrected from old selection-only helper wording; renders localized context help from an integer help token and transition/progress argument. |
| 0x00465a20 | TextLayout__WrapWideTextToFixedLines | Corrected from old `CFEPLanguageTest`-only ownership; shared wide-text line wrapper used by frontend dialogs, language test, overlays, and prompts. |

These are saved static Ghidra name/signature/comment/tag refinements. Runtime UI rendering/text behavior, concrete layouts, locals/types, and rebuild parity remain unproven.

Wave922 re-reviewed the shared frontend text/layout cluster read-only. Fresh metadata, tags, xrefs, instructions, and decompile exports verified `TextLayout__WrapWideTextToFixedLines` plus the Wave378 frontend text-token helpers; no Ghidra mutation was needed.

## Wave 377 Frontend Core Helper Corrections (2026-05-13)

| Address | Name | Notes |
|---------|------|-------|
| 0x00466980 | CFrontEnd__GetPlayer0ControllerPort | Hardened source-parity signature/comment for player-0 controller-port sentinel normalization. |
| 0x004669a0 | CFrontEnd__ReceiveButtonAction | Corrected from generic vtable-slot wording to frontend button dispatch with controller, button, and value arguments. |
| 0x00466ab0 | CFrontEnd__SetLanguage | Hardened language-index signature/comment for frontend text-set copy. |
| 0x00467200 | CFrontEnd__DrawSlidingTextBordersAndMask | Hardened transition/destination-page signature/comment. |
| 0x004679a0 | FrontEnd__HasStandardSlidingTextBordersAndMaskPage | Corrected older `CFrontEnd` instance-method wording to source-static page predicate ownership. |
| 0x00467bd0 | CFrontEnd__DrawTitleBar | Hardened wide-title-text, transition, and destination-page signature/comment. |
| 0x00468700 | CFrontEnd__RenderCursorEndSceneAndAsyncSave | Corrected generic vtable-slot wording to cursor render, optional end-scene, and async career-save behavior. |
| 0x004691c0 | CFrontEnd__ReleaseParticleHudWaypointResources | Hardened frontend cleanup helper signature/comment. |
| 0x00469390 | CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture | Hardened modal mouse gate and dispatch rectangle signature/comment. |
| 0x004693d0 | CFrontEnd__GetCursorStateInRect | Hardened cursor-state rectangle wrapper signature/comment. |
| 0x00469400 | CFrontEnd__GetClickStateInRect | Hardened click-state rectangle wrapper signature/comment. |
| 0x00469430 | CFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady | Corrected old directory check label to cursor-state consume wrapper behavior. |
| 0x00469550 | CFrontEnd__ResolveLevelNameTextByCode | Hardened localized level-name wide-text return signature/comment. |

These are saved static Ghidra name/signature/comment/tag refinements. Runtime frontend input, rendering, cursor, save, localization behavior, concrete layouts, locals/types, and rebuild parity remain unproven.

## Wave 467 CFrontEnd Render / Source-Bridge Hardening (2026-05-16)

| Address | Name | Notes |
|---------|------|-------|
| 0x004662a0 | [CFrontEnd__Init](./CFrontEnd__Init.md) | Hardened source-bridged `CFrontEnd::Init(EFrontEndEntry, BOOL)` signature/comment for loading ranges, page wiring, controller allocation, initial page selection, text-set init, and music start. |
| 0x00466990 | [CFrontEnd__NumControllersPresent](./CFrontEnd__NumControllersPresent.md) | Hardened method signature and documented the retail PC fixed return `2`, which differs from the broader source counting body. |
| 0x00466de0 | [CFrontEnd__DrawLine](./CFrontEnd__DrawLine.md) | Hardened source-backed line-sprite helper signature: endpoints, ARGB, width, depth, and percent length. |
| 0x00466e70 | [CFrontEnd__DrawBox](./CFrontEnd__DrawBox.md) | Hardened source-backed box helper signature; retail body inlines four line-sprite draws. |
| 0x00467010 | [CFrontEnd__DrawPanel](./CFrontEnd__DrawPanel.md) | Hardened source-backed blank-panel helper signature and clamp/wrap state comment. |
| 0x004670b0 | [CFrontEnd__DrawBarGraph](./CFrontEnd__DrawBarGraph.md) | Hardened source-backed bar-graph signature for bounds, value/max, depth, and colors. |
| 0x004679e0 | [CFrontEnd__RenderPreCommonFade](./CFrontEnd__RenderPreCommonFade.md) | Hardened static fade-helper signature for transition, ARGB, and destination page. |
| 0x00467ae0 | [CFrontEnd__DrawBar](./CFrontEnd__DrawBar.md) | Hardened source-backed segmented title/header bar signature. |
| 0x004681c0 | [CFrontEnd__EnableAdditiveAlpha](./CFrontEnd__EnableAdditiveAlpha.md) | Hardened source-backed additive blend-state helper signature/comment. |
| 0x004681e0 | [CFrontEnd__EnableModulateAlpha](./CFrontEnd__EnableModulateAlpha.md) | Hardened source-backed alpha-modulate blend-state helper signature/comment. |
| 0x004684d0 | [CFrontEnd__Run](./CFrontEnd__Run.md) | Hardened source-bridged `CFrontEnd::Run(EFrontEndEntry, BOOL)` signature/comment. |
| 0x004685a0 | [CFrontEnd__UpdateCamera](./CFrontEnd__UpdateCamera.md) | Corrected old `SetRenderViewAndProjection` label to source-bridged `UpdateCamera`. |
| 0x004685f0 | [CFrontEnd__RenderStart](./CFrontEnd__RenderStart.md) | Corrected old vfunc-slot label to source-bridged `RenderStart`, reached from `CDXFrontEnd::RenderStart`. |
| 0x00468730 | [CFrontEnd__GetShadowOffsetX](./CFrontEnd__GetShadowOffsetX.md) | Hardened float return signature for sine-based animated shadow X offset. |
| 0x00468750 | [CFrontEnd__GetShadowOffsetY](./CFrontEnd__GetShadowOffsetY.md) | Hardened float return signature for cosine-based animated shadow Y offset. |

This is saved static retail-binary/source-bridge evidence only. Runtime frontend rendering/controller/camera behavior, exact CFrontEnd/page/render-state layouts, exact platform-specific source identities, and rebuild parity remain unproven.

## Wave596 CDXFrontEnd wrapper hardening (2026-05-19)

Wave596 hardened the adjacent CDXFrontEnd construction, teardown, and render wrapper rows that bridge the frontend render loop into the CFrontEnd implementation:

| Address | Name | Notes |
|---------|------|-------|
| 0x00540b60 | CDXFrontEnd__DestructorBody | Non-freeing destructor body called by `CDXFrontEnd__scalar_deleting_dtor`; unwinds waiting-thread/SPtrSet/device-object style members, installs the fallback vtable at `this+8`, and calls `CMonitor__Shutdown(this)`. |
| 0x00540bf0 | CDXFrontEnd__Constructor | Constructor wrapper called from raw startup/init code; runs `CFEPMultiplayerStart__ctor`, installs the CDXFrontEnd vtable at `0x005e5054`, and returns `this`. |
| 0x00540c10 | CDXFrontEnd__scalar_deleting_dtor | CDXFrontEnd vtable `0x005e5054` slot 1; `RET 0x4` proves one stack argument after `this`, and `delete_flags` bit 0 gates the `CDXMemoryManager__Free` call. |
| 0x00540f70 | CDXFrontEnd__RenderStart | CDXFrontEnd vtable `0x005e5054` slot 6; reached by `CFrontEnd__Render`, resets render state, clears the screen, enables render state `0x1b`, and forwards `this` into `CFrontEnd__RenderStart`. |
| 0x00540fb0 | CDXFrontEnd__VFunc_07_00540fb0 | CDXFrontEnd vtable `0x005e5054` slot 7; `RET 0x4` proves the `render_particles` stack parameter before optional `CDXFrontEnd__SetupRenderMatricesAndProjection` and `CFrontEnd__RenderCursorEndSceneAndAsyncSave`. |

This is saved static retail-binary evidence only. Runtime frontend construction/teardown/render behavior, exact CDXFrontEnd/CFrontEnd/page layouts, full vtable boundaries past the observed slots, BEA patching, and rebuild parity remain unproven.

## Wave 378 Frontend Localization/Text Corrections (2026-05-13)

| Address | Name | Notes |
|---------|------|-------|
| 0x00469c20 | CFrontEnd__ResolveEpisodeNameTextByIndex | Hardened wide-text return signature for episode-name resolution with `Unnamed Episode` fallback. |
| 0x00469cf0 | CFrontEnd__ResolveLevelNameTextIdByCode | Hardened parameter/comment for level/world code to text-id mapping with `-1` unmapped return. |
| 0x0046a1f0 | FrontEndText__GetLevelNameTextAfterCode | Corrected stale `CUnitAI` ownership; forwards level-code resolution into `CText__GetStringByIdAfter`. |
| 0x0046a210 | FrontEnd__GetBriefingLevelListTextColor | Corrected older fallback text-id label; returns `0xffffdf5f` and caller treats it as draw color. |
| 0x0046a220 | FrontEndText__GetMultiplayerLevelDescriptionByType | Corrected stale `CUnitAI` ownership; resolves multiplayer level-description text with fallback. |
| 0x0046a2a0 | FrontEndText__GetLocalizedOrFallbackTextByToken | Corrected save-game-specific ownership to broad frontend text-token resolver. |
| 0x0046b1e0 | FrontEndText__GetAsciiFallbackTextByToken | Corrected save-game-specific ownership and return type for shared ASCII fallback text-token resolver. |

These are saved static Ghidra name/signature/comment/tag refinements. Runtime frontend localization, briefing rendering, fallback-toggle behavior, concrete layouts, locals/types, and rebuild parity remain unproven.

## Wave 379 Frontend Preview/Camera Corrections (2026-05-13)

| Address | Name | Notes |
|---------|------|-------|
| 0x00466130 | CGenericCamera__ctor | Corrected old constructor-like suffix label to the CGenericCamera constructor body that installs the frontend preview camera vtable. |
| 0x00466140 | CGenericCamera__GetPos | Hardened output-position signature/comment for the four-dword copy from receiver offsets `+0x34` through `+0x40`. |
| 0x00466170 | CGenericCamera__scalar_deleting_dtor | Hardened scalar deleting destructor signature with `free_flag` and conditional free behavior. |
| 0x004661b0 | CGenericCamera__dtor | Hardened destructor-base comment for resetting the receiver to the base CGenericCamera table. |
| 0x0046b950 | CFEPMultiplayerStart__LoadPreviewMeshFromConfig | Hardened preview config argument and recorded preview object creation at `+0x58` plus animation/timer field initialization. |
| 0x0046ba90 | CFrontEndThing__dtor_base | Corrected old constructor-like label; static cleanup evidence releases preview object pointer `+0x58`. |
| 0x0046bab0 | CFEPMultiplayerStart__SetPreviewAnimationByName | Hardened animation-name argument and recorded `FindAnimationIndex`/preview duration update context. |
| 0x0046bc20 | CFEPMultiplayerStart__StopPreviewAnimation | Hardened no-stack-argument signature for preview-object stop dispatch. |
| 0x0046c030 | CThingCamera__scalar_deleting_dtor | Corrected old vfunc label to scalar deleting destructor behavior. |
| 0x0046c050 | CThingCamera__dtor_base | Corrected old constructor-like label; destructor-base cleanup removes linked reader cell and resets to the base CGenericCamera vtable. |

These are saved static Ghidra name/signature/comment/tag refinements. Runtime frontend preview mesh, preview animation, camera behavior, concrete layouts, locals/types, source identity, and rebuild parity remain unproven.

## Wave 380 Frontend Briefing/Tweak Corrections (2026-05-13)

| Address | Name | Notes |
|---------|------|-------|
| 0x00452430 | CFEPBriefing__TransitionNotification | Wave975 supersedes the older timer-reset label; this is the CFEPBriefing vtable slot-6 transition notification that refreshes a timer from system time plus a static constant, stores it at `this+0x04`, clears `this+0x08`, and consumes the observed `from_page` stack argument. |
| 0x004530a0 | CTweak__dtor_base_thunk_004530a0 | Corrected duplicate CTweak destructor-body label to a one-instruction jump thunk to `CTweak__dtor_base` at `0x005286b0`. |

These are saved static Ghidra name/signature/comment/tag refinements. Runtime frontend briefing behavior, runtime tweak cleanup behavior, concrete layouts, locals/types, source identity, and rebuild parity remain unproven.

Wave975 recovered the missing CFEPBriefing vtable slots `0x00451b70 CFEPBriefing__Init`, `0x00451b80 CFEPBriefing__Process`, `0x00451c20 CFEPBriefing__ButtonPressed`, `0x00451c90 CFEPBriefing__RenderPreCommon`, `0x00451d50 CFEPBriefing__Render`, and `0x00452460 CFEPBriefing__ActiveNotification`, while renaming/hardening `0x00452430 CFEPBriefing__TransitionNotification`. The pass verified CFEPBriefing slots 0 and 2-7 through the vtable at `0x005db9e8`; runtime frontend input/render/video behavior remains separate proof.

## Wave 381 Frontend Wide-Text Helper Correction (2026-05-13)

| Address | Name | Notes |
|---------|------|-------|
| 0x00472270 | [Frontend__XorWideTextBlock100BytesToScratch](./Frontend__XorWideTextBlock100BytesToScratch.md) | Corrected old `CGame__XorBlock64Words` label; XORs a `0x64` byte wide-text block into `DAT_00679e18` for the now-corrected `CGame__DrawGameStuff` overlay path. |

This is saved static Ghidra name/signature/comment/tag refinement. Runtime frontend text behavior, concrete text-table ownership, locals/types, and rebuild parity remain unproven.

## CFrontEnd Class Layout

Based on analysis of `CFrontEnd__Init`, the class contains pointers to 24 frontend page objects at offset 0x214:

| Offset | Index | Page Class | Notes |
|--------|-------|------------|-------|
| 0x214 | 0 | CFEPage (base) | Points to 0x278 |
| 0x218 | 1 | CFEPage | Points to 0x29c |
| 0x21c | 2 | CFEPage | Points to 0x2b0 |
| 0x220 | 3 | CFEPage | Points to 0x2bc (700 decimal) |
| 0x224 | 4 | CFEPage | Points to 0x2ec |
| 0x228 | 5 | CFEPage | Points to 0x324 |
| 0x22c | 6 | CFEPage | Points to 0x338 - Main menu? |
| 0x230 | 7 | CFEPage | Points to 0x360 |
| 0x234 | 8 | CFEPage | Points to 0x37dc |
| 0x238 | 9 | CFEPage | Points to 0x39b8 |
| 0x23c | 10 | CFEPage | Points to 0x39d0 |
| 0x240 | 11 | CFEPage | Points to 0x3c1c |
| 0x244 | 12 | CFEPage | Points to 0x4034 |
| 0x248 | 19 | CFEPage | Points to 0x413c |
| 0x24c | 20 | CFEPage | Points to 0x4834 |
| 0x250 | 15 | CFEPage | Points to 0x40b8 |
| 0x254 | 13 | CFEPage | Points to 0x4050 |
| 0x258 | 14 | CFEPage | Points to 0x40ec |
| 0x25c | 16 | CFEPage | Points to 0x4118 |
| 0x260 | 17 | CFEPage | Points to 0x4124 |
| 0x264 | 21 | CFEPage | Points to 0x8848 |
| 0x268 | 22 | CFEPage | Points to 0xbcc8 |
| 0x26c | 23 | CFEPage | Points to 0xbde0 |
| 0x270 | 24 | CFEPage (null) | Points to 0xbe04 (default null page) |

### Key CFrontEnd Members

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x1f8 | int | mCurrentPage | Page index to display (-1 = use mPreviousPage) |
| 0x200 | int | mPreviousPage | Previous page index |
| 0x1f4 | int | mLastWorld | World ID (500+ range for campaign) |
| 0x214-0x270 | ptr[] | mPages[24] | Frontend page object pointers |
| 0xbe0c | ptr[2] | mUnknown | Two objects allocated at line 0xb3 (179) |
| 0xbe14 | int | mState | State (-2 = running, -1 = exit, etc.) |
| 0xbe18 | int | mUnknown2 | Unknown state |
| 0xbe1c | int | mFromOutro | Non-zero after outro/victory |
| 0xbe20 | float | mUnknown3 | Initialized to -100.0f |
| 0xbe2c | int | mPlayType | 2 = something special |
| 0xbf34 | int | mNextPage | Used with timed transitions |
| 0xbf38 | int | mTransitionTimer | Timer for page transitions |

## Page Index Constants

Based on code flow analysis in `CFrontEnd__Init`:

| Index | Probable Page | Evidence |
|-------|---------------|----------|
| 0x00 (0) | Legal/Splash | First page after load |
| 0x06 (6) | Main Menu | Default fallback, set at offset 0x22c |
| 0x08 (8) | ? | Special case for worlds 0x385-0x389 |
| 0x0b (11) | ? | Used with timed transition |
| 0x0c (12) | ? | Intro/demo mode start |
| 0x10 (16) | ? | Special case for worlds 0x352-0x36f |
| 0x17 (23) | ? | Transition page, set before `CFrontEnd__SetPage` calls |

## Global Variables Referenced

| Address | Name | Purpose |
|---------|------|---------|
| 0x00662f40 | DAT_00662f40 | If non-zero, calls `CSoundManager__ReloadLanguageSampleBank` during init |
| 0x0066304c | DAT_0066304c | Level override (-1 = none, else jump to level) |
| 0x00662dd0 | DAT_00662dd0 | Demo/intro flag |
| 0x00662dcc | DAT_00662dcc | If non-zero, calls FUN_004bb8c0 at end |
| 0x006630cc | DAT_006630cc | Special mode flag |
| 0x0083d448 | DAT_0083d448 | Demo state |
| 0x0083d454 | DAT_0083d454 | Playable demo timeout control |
| 0x008a9ab4 | DAT_008a9ab4 | Init complete flag |
| 0x008a9580 | DAT_008a9580 | Unknown flag set during transitions |
| 0x008a9584 | DAT_008a9584 | Unknown flag set during transitions |
| 0x008a9aac | DAT_008a9aac | Cleared to 0 after page init |
| 0x00679b40 | DAT_00679b40 | Frontend active flag (1 during Run loop) |

## Cross-References

### Calls To
- `CCareer__Update` - Update career progress
- `CConsole__SetLoading` - Loading-screen enable/disable toggle used around frontend init/load phases
- `CConsole__SetLoadingRange` / `CConsole__SetLoadingFraction` - Progress bar range/value updates
- `CFrontEnd__LoadSharedResources` - Resource loading (returns 0 on failure)
- `CFrontEndPage__Init_ReturnTrue` - Resource loading gate helper (returns non-zero success)
- `CDXFrontEndVideo__SetDefaultSize` - Frontend video default-size setup (returns non-zero success)
- `CFrontEnd__SetPage` - Page transition function
- `OID__AllocObject` - Memory allocation (size 0x178, align 0x27)
- `CPCController__ctor` - Controller object construction

### Called By
- `FUN_00XXXXXX` (main game loop - not yet identified)

## Discovery Method

Found via xrefs to debug path string `[maintainer-local-source-export-root]\FrontEnd.cpp` at 0x00629df0:
- 0x00466578 in CFrontEnd__Init (line 179 / 0xb3)
- 0x005d2735 in Unwind@005d2730 (exception handler)

## Notes

1. **24 Frontend Pages**: The system initializes 24 page pointers (0x18 in hex), iterating with format string "FEP %d..." during loading
2. **Page Virtualization**: Each page object has a vtable with methods at offsets 0x00 (init), 0x18 (activate?), 0x1c (show?)
3. **Dev Mode Checks**: Several paths check `g_bDevModeEnabled` and `g_bAllCheatsEnabled` for special behavior
4. **World ID Ranges**: Certain world IDs (0x352-0x36f, 0x385-0x389) trigger specific page selections

## Migration Notes

- Created Dec 2025 during systematic FrontEnd.cpp analysis
- Debug path xref discovery method

## Wave1151 Current-Risk Tag Normalization

Wave1151 tag-only normalization also covers `0x0046a220 FrontEndText__GetMultiplayerLevelDescriptionByType` as a score21 current-risk row. It preserves the multiplayer description text resolver evidence and adds Wave1151/current-risk tags only. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
