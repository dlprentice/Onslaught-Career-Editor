# game.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`); `0x00445010` comment correction; `0x0046e910` comment correction; `0x00541f00` → `CDXGame__dtor_thunk` (was `CDXGame__dtor`). Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Source File: game.cpp | Binary: BEA.exe

## Overview
> **Queue status (2026-05-31):** Ghidra export-contract closure **6223/6223** (Wave1003: every current function commented with clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Core game initialization and lifecycle management. This file handles setting up all game subsystems during startup.

2026-06-08 MissionScript Slot Command-Effect static proof: `missionscript-slot-command-effect-static-proof.md` and `missionscript-slot-command-effect.v1.json` preserve the CGame side of the slot bridge through `CGame__SetSlot`, `CGame__GetSlot`, `CGame+0x308`, `IScript__SetSlot`, `IScript__SetSlotSave`, `IScript__GetSlotBitValue`, `CCareer__SetSlot`, true-view save slot base `0x240A`, `6 slot-using level rows`, `18 detailed slot call rows`, `6 GetSlot`, `8 SetSlot`, and `4 SetSlotSave`. This is MissionScript Slot Command-Effect static bridge accounting only, not runtime command effects, runtime save behavior, runtime slot persistence, exact `CGame` layout, patch, Godot, rebuild, or no-noticeable-difference proof.

2026-06-08 MissionScript Objective/Outcome Command-Effect static proof: `missionscript-objective-outcome-command-effect-static-proof.md` and `missionscript-objective-outcome-command-effect.v1.json` preserve the CGame side of objective/outcome bridges through `CGame__FillOutEndLevelData`, `CGame__DeclareLevelWon`, `CGame__DeclareLevelLost`, `IScript__LevelWon`, `IScript__LevelLost`, `IScript__LevelLostString`, `IScript__PrimaryObjectiveComplete`, `IScript__SecondaryObjectiveComplete`, `IScript__PrimaryObjectiveFailed`, `IScript__SecondaryObjectiveFailed`, primary/secondary objective text/state arrays, `CCareer__Update`, and `CEndLevelData__IsAllSecondaryObjectivesComplete`. This is MissionScript Objective/Outcome Command-Effect static bridge accounting only, not runtime command effects, runtime objective UI, runtime level outcomes, runtime save/career behavior, exact `CGame` layout, patch, Godot, rebuild, or no-noticeable-difference proof.

Wave1188 (`wave1188-battleengine-walkerpart-support-current-risk-review`) re-read the `CGame__IsWalkerGroundedOrCollision` bridge in BattleEngine/WalkerPart support context with fresh Ghidra export evidence and saved comment/tag normalization. It accounts for `8 BattleEngine/WalkerPart support current-risk rows`: `CBattleEngine__dtor_base`, `CBattleEngine__scalar_deleting_dtor`, `CBattleEngine__UpdateWeaponEffect`, `CBattleEngine__SwapPrimarySecondaryPartReadersForState`, `CBattleEngine__AddProjectile`, `CGame__IsWalkerGroundedOrCollision`, `CBattleEngineWalkerPart__GetWeaponPhysicsName`, and `CBattleEngineWalkerPart__GetWeaponIconName`. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; Wave1108 current focused accounting is now `801/1179 = 67.94%`; current risk candidates: 6166; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 378; focused threshold `15`; not Wave911 reconstruction. Evidence verified `16 xref rows`, `478 instruction rows`, and `8 decompile rows`. Saved apply reported `updated=8 skipped=0`, `comment_only_updated=8`, `tags_added=128`, and final dry updated=0 skipped=8; no rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consult used; no Cursor/Composer. Static anchors include `CBattleEngine__HandleEvent`, `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`, `CGame__Update`, `CPlayer__ReceiveButtonAction`, `CBattleEngine__GetWeaponPhysicsName`, `CBattleEngine__GetWeaponIconName`, BattleEngine.cpp line 0x1f5, BattleEngine.cpp line 0x332, `this+0x294`, `this+0x5ec`, and `this+0x30`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-160404_post_wave1188_battleengine_walkerpart_support_current_risk_review_verified`. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference; exact BattleEngine/WalkerPart/CWeaponData/projectile-entry layouts, exact source-body identity, runtime weapon/effect/projectile/morph/reader/grounded behavior, `weapon_fire_breaks_stealth` closure, BEA patching behavior, gameplay/visual outcomes, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1188; wave1188-battleengine-walkerpart-support-current-risk-review; 801/1179 = 67.94%; 8 BattleEngine/WalkerPart support current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 378; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=8 skipped=0; comment_only_updated=8; tags_added=128; final dry updated=0 skipped=8; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CBattleEngine__dtor_base; CBattleEngine__scalar_deleting_dtor; CBattleEngine__UpdateWeaponEffect; CBattleEngine__SwapPrimarySecondaryPartReadersForState; CBattleEngine__AddProjectile; CGame__IsWalkerGroundedOrCollision; CBattleEngineWalkerPart__GetWeaponPhysicsName; CBattleEngineWalkerPart__GetWeaponIconName; CBattleEngine__HandleEvent; CBattleEngine__UpdateAutoTargetSetAndFireProjectiles; CGame__Update; CPlayer__ReceiveButtonAction; CBattleEngine__GetWeaponPhysicsName; CBattleEngine__GetWeaponIconName; BattleEngine.cpp line 0x1f5; BattleEngine.cpp line 0x332; this+0x294; this+0x5ec; this+0x30; 0 / 0 / 0; 6411/6411 = 100.00%; 16 xref rows; 478 instruction rows; 8 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-160404_post_wave1188_battleengine_walkerpart_support_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.

Wave1049 end-level objective/progression review (`endlevel-objective-progression-review-wave1049`) re-read the game-side objective snapshot, count, slot, and outro bridge with no mutation. Fresh primary evidence covers `0x0046d470 CGame__FillOutEndLevelData`, `0x00472670 CGame__GetNumPrimaryObjectives`, `0x00472690 CGame__GetNumSecondaryObjectives`, and `0x0046d9f0 CGame__RunOutroFMV`; context keeps `CGame__SetSlot`, `CGame__GetSlot`, `IScript__SetSlotSave`, and `IScript__GetSlotBitValue` tied to runtime/save slot bits. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-134936_post_wave1049_endlevel_objective_progression_review_verified`. Runtime objective UI behavior, runtime mission-script dispatch/argument behavior, runtime progression/save outcome behavior, runtime outro/cutscene behavior, runtime goodie unlock behavior, exact layouts, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1003 HUD head/render-state review (`hud-head-render-state-review-wave1003`) recovered `0x0046c990 CGame__Shutdown` as a source-backed `CGame::Shutdown` boundary after `CHud__ShutDown` caller review found `0x0046c9ac` outside any saved function. DATA refs `0x005dbbbc` and `0x005e50a4`, `0x0046c98e RET` before the orphan body, terminal `0x0046ca6b RET`, and source parity to `references/Onslaught/game.cpp:CGame::Shutdown` justified one function-boundary creation. Post exports verified the recovered `CGame__Shutdown` row plus the HUD head/render-state cluster (`0x00481400 CHud__ctor_base`, `0x00481b00 CHud__ShutDown`, `0x00482090 HudRenderState__ApplyOverlaySpriteState`, `0x004821b0 CDXCompass__ApplyRenderStateModulate`, and `0x00482210 CHud__RenderSegmentedMeterBar`) with `13` metadata rows, `13` tag rows, `32` xref rows, `1324` body-instruction rows, and `13` decompile rows. Queue closure is `6223/6223 = 100.00%`; Wave911 focused re-audit progress remains `472/1408 = 33.52%`; expanded static surface candidate-set progress is `641/1478 = 43.37%`, plus one newly recovered out-of-seed boundary; Wave911 top-500 risk-ranked coverage is `371/500 = 74.20%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-120949_post_wave1003_hud_head_render_state_review_verified`. Runtime shutdown behavior, runtime HUD behavior, exact source-body identity, concrete `CGame`/`CHud`/renderer/resource layouts, BEA patching, and rebuild parity remain separate proof.

Wave995 early high-signal residual review (`early-high-signal-residual-review-wave995`) corrected `0x00441e50 CDebugMarkers__Shutdown`, which is called by `CGame__ShutdownRestartLoop` at `0x0046cbe4`. Fresh instruction evidence shows the shutdown helper unlinks debug markers from `DAT_0066ffb0` and frees each marker directly through `CDXMemoryManager__Free` at `0x00549220` with memory-manager context `0x009c3df0`, correcting stale Wave364 `OID__FreeObject` wording. The pass preserved static closure `6222/6222 = 100.00%`, moved Wave911 focused re-audit progress to `464/1408 = 32.95%`, and moved expanded static surface progress to `569/1478 = 38.50%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-073718_post_wave995_early_high_signal_residual_review_verified`. Runtime marker behavior, exact debug-marker manager layout, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave861 render/HUD/platform tail static read-back (`render-hud-platform-tail-wave861`, `wave861-readback-verified`) hardened `0x00527990 CGame__DrawLocalCoopControllerPrompt` as important connective infrastructure. Probe token anchor: `Wave861 render/HUD/platform tail`; `render-hud-platform-tail-wave861`; `0x00523a70 CDXEngine__RenderMouseCursorSprite`; `0x00523b30 CVBufTexture__DestroyGlobalHudHandle89BD98`; `0x00527990 CGame__DrawLocalCoopControllerPrompt`; `0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag`; `0x00527f50 PCPlatform__AsyncMusicStreamWorkerMain`; `0x005282b0 PCPlatform__InitAsyncMusicStream`; `0x00528540 PCPlatform__KickAsyncMusicStreamRead`; `0x005285e0 PCPlatform__UpdateAsyncMusicStreamVolume`; important connective infrastructure; `0x0052a830 CD3DApplication__FindDepthStencilFormat`; `5802/6105 = 95.04%`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-141443_post_wave861_render_hud_platform_tail_verified`.

Static evidence ties the local co-op/controller prompt renderer to frontend, game render, and multiplayer-start render callers. The body compares controller ports through `CFrontEnd__GetPlayer0ControllerPort`, uses localized prompt text, computes wrapping/extent, draws a sprite background, and emits font text; exact hidden ABI/layout and runtime controller-prompt behavior remain deferred.

Wave799 PC utility microhelpers (`pc-utility-microhelpers-wave799`, `wave799-readback-verified`) added saved static comments/tags for two game-adjacent utility helpers: `0x00441b10 CGame__SetGlobalSelectionSnapshot` and `0x00441e40 CGame__ClearDwordValue`. The same wave moved the next raw commentless head to `0x00445010 CMCBuggy__GetTargetValueOrFallback`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-063302_post_wave799_pc_utility_microhelpers_verified`. Runtime screenshot/restart-loop behavior, exact field/global ownership, BEA patching, and rebuild parity remain deferred.

Wave802 static read-back (`frontend-save-multiplayer-wave802`, `wave802-readback-verified`) corrected the FMV playback wrapper reached by `CGame__RunIntroFMV` and `CGame__RunOutroFMV` to `0x00465640 CFMV__PlayFullscreenWithLoadingGate`. The wrapper gates non-interactive sections around the vtable-dispatched full-screen movie play call and conditionally forwards `g_LanguageIndex`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-081932_post_wave802_frontend_save_multiplayer_verified`. Runtime cutscene playback, exact CFMV layout/vtable contract, BEA patching, and rebuild parity remain deferred.

Wave803 static read-back (`game-slot-helpers-wave803`, `wave803-readback-verified`) saved comments/tags for `0x0046d3a0 CGame__SetSlot` and `0x0046d410 CGame__GetSlot`, the CGame runtime slot-bit helpers used by the IScript `SetSlot`, `SetSlotSave`, and `GetSlot` handlers. Both bodies operate on the slot bit array at `this+0x308`; `SetSlot` prints out-of-range string `0x0062434c`, and `GetSlot` prints out-of-range string `0x00624318`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-084656_post_wave803_game_slot_helpers_verified`. Next raw commentless row after Wave803 is `0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback`. Exact CGame layout beyond `this+0x308`, runtime mission-script behavior, runtime save/update behavior, BEA patching, and rebuild parity remain deferred.

Wave818 message voice pump static read-back (`message-voice-pump-wave818`, `wave818-readback-verified`) saved a comment/tag/signature correction for `0x004b7d90 CGame__PumpBinkVoiceSampleQueue` as `void __thiscall CGame__PumpBinkVoiceSampleQueue(void * this)`. Evidence ties the row to `CGame__Update` callsite `0x0046ea77`, Bink/audio queue globals `DAT_008073d0`, `DAT_0080738c`, and `DAT_00704e74`, `CBinkOpenThread__IsRunning`, `CPCSoundManager__CreateSampleFromData`, `CSoundManager__PlaySample`, `FatalError__ExitWithLocalizedPrefix_A`, and `CGenericActiveReader__SetReader`. Post-Wave818 queue telemetry is `5606/6098 = 91.93%`, with next raw commentless row `0x004bc2d0 CWorld__ClearDynamicOccupancySet`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-161634_post_wave818_message_voice_pump_verified`. Exact global names/layouts, exact source-body identity, runtime Bink/voice playback behavior, BEA patching, and rebuild parity remain deferred.

Wave907 (`frontend-input-game-loop-static-review-wave907`) records `CGame` as part of the `static-coherent frontend/input/game-loop core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only). The slice covers `436` rows across `33` families and includes `CGame__MainLoop`, `CGame__RunLevel`, `CGame__ReceiveButtonAction`, plus controller/frontend/player anchors such as `CFrontEnd__Run`, `CController__DoMappings`, and `CPlayer__AssignBattleEngine`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified`. Runtime menu/input/video behavior, visual QA, patch behavior, and rebuild parity remain separate proof.

Wave951 (`game-interface-lifecycle-wave951`) re-reviewed the CGame/GameInterface lifecycle bridge read-only with no mutation: `0x0046c210 CGame__ctor`, `0x0046c2d0 CGame__dtor`, `0x004729d0 CGameInterface__ctor_base`, `0x004729e0 CGameInterface__ResetMenuState`, and `0x00472ad0 CGameInterface__AdvanceMenuSelectionWithWrap`, plus caller context `0x0046c360 CGame__Init` and `0x0046c430 CGame__InitRestartLoop`. Wave911 focused re-audit progress after Wave951 is `271/1408 = 19.25%`; export-contract closure remains `6150/6150 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-083735_post_wave951_game_interface_lifecycle_review_verified`. Exact GameInterface source-body identity, concrete CGame/GameInterface layouts, runtime pause/menu/input/render behavior, BEA patching, and rebuild parity remain separate proof.

Wave1147 (`wave1147-frontend-game-shell-score20-current-risk-review`) re-read `0x0046c210 CGame__ctor`, `0x0046c2d0 CGame__dtor`, `0x004729e0 CGameInterface__ResetMenuState`, and `0x00472ad0 CGameInterface__AdvanceMenuSelectionWithWrap` in the frontend/game shell score20 current-risk review. Fresh exports kept these CGame/GameInterface lifecycle and menu-state rows static-consistent; no rename or signature change was made. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified`.

Wave952 (`game-interface-menu-control-boundary-wave952`) recovered `0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput` from CGameInterface vtable `0x005dbc2c slot 3`. For the CGame ownership boundary, the important static bridge is the recovered button/control IDs `0x2a..0x39` path that can call `CController__RelinquishControl`, toggle `0x00679fbc`, and call `CGame__UnPause(&DAT_008a9a98)`. The recovered body also calls `CGameInterface__AdvanceMenuSelectionWithWrap` and `CGameInterface__HandleMenuSelection`. Wave911 focused re-audit progress after Wave952 is `276/1408 = 19.60%`; export-contract closure is `6151/6151 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-091135_post_wave952_game_interface_menu_control_boundary_verified`. Exact source method name, individual button semantics, `0x00679fbc` meaning, runtime pause/menu/input behavior, BEA patching, and rebuild parity remain separate proof.

Wave962 (`game-menu-options-bridge-review-wave962`) re-reviewed the CGame/GameInterface edge of the pause-menu options bridge read-only. Fresh evidence keeps `0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput` tied to `0x005dbc2c slot 3`, and ties `CGameInterface__HandleMenuSelection` to `0x004d3020 CEngine__SetOptionValueAndNotifyTarget`; the same slice re-checks `0x004d0290 CControllerBackMenuItem__RenderBindingCapacityWarning` and `0x004d0e40 CGameMenu__InitBase`. Key instruction anchors are `0x004d02a5 PUSH 0xe8`, `0x004d02d7 PUSH 0xe9`, `0x004d0e49 MOV [EAX], 0x5dc72c`, `0x004d302e MOV [EAX*0x4 + 0x662ab0], EDI`, and vtable pointer `0x005dc72c`. No mutation was needed. Wave911 focused re-audit progress after Wave962 is `309/1408 = 21.95%`; static export-contract closure remains `6152/6152 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-132411_post_wave962_game_menu_options_bridge_review_verified`. Runtime pause-menu/controller-binding/options persistence behavior, exact layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave962; game-menu-options-bridge-review-wave962; 0x004d0290 CControllerBackMenuItem__RenderBindingCapacityWarning; 0x004d0e40 CGameMenu__InitBase; 0x004d3020 CEngine__SetOptionValueAndNotifyTarget; 0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput; 0x004d02a5 PUSH 0xe8; 0x004d02d7 PUSH 0xe9; 0x004d0e49 MOV [EAX], 0x5dc72c; 0x004d302e MOV [EAX*0x4 + 0x662ab0], EDI; 0x005dbc2c slot 3; 0x005dc72c; 309/1408 = 21.95%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-132411_post_wave962_game_menu_options_bridge_review_verified; no mutation.

## Functions

### Console Commands (Free Functions)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0046be10 | [con_map](./con_map.md) | Console command: `Map <n>` |
| 0x0046be80 | [con_resetmemsizes](./con_resetmemsizes.md) | Console command: `ResetMemSizes` |
| 0x0046bea0 | [con_dumptextures](./con_dumptextures.md) | Console command: `DumpTextures` |
| 0x0046bed0 | [con_dumptimerecords](./con_dumptimerecords.md) | Console command: `dumptimerecords` (disabled in this build) |
| 0x0046bef0 | [con_remotecameraon](./con_remotecameraon.md) | Console command: `RemoteCameraOn` |
| 0x0046c0b0 | [con_remotecameraoff](./con_remotecameraoff.md) | Console command: `RemoteCameraOff` |
| 0x0046c120 | [con_navmapon](./con_navmapon.md) | Console command: `NavMapOn` |
| 0x0046c150 | [con_navmapoff](./con_navmapoff.md) | Console command: `NavMapOff` |
| 0x0046c180 | [con_win](./con_win.md) | Console command: `Win` |
| 0x0046c200 | [con_lose](./con_lose.md) | Console command: `Lose` |

### Cutscene Helpers (Free Functions)

| Address | Name | Purpose |
|---------|------|---------|
| 0x00523120 | [lookup_FMV](./lookup_FMV.md) | Returns intro/outro FMV id from level->FMV lookup table (`index_type`: 0/1/2, `-1` when absent) |
| 0x0046d810 | [Cutscene_FormatPath_WithSmallFallback](./Cutscene_FormatPath_WithSmallFallback.md) | Builds `cutscenes\\%02d` and rewrites to `_small` variant when `data\\video\\<name>.vid` is missing |

### Restart-Loop Local Helpers

| Address | Name | Purpose |
|---------|------|---------|
| 0x0046dbd0 | [CWaitForStart__ctor](./CWaitForStart__ctor.md) | Initializes temporary wait-sink object used during restart-loop flow (`vtable@+0x00`, zero field at `+0x04`) |

### CGame Methods

| Address | Name | Purpose |
|---------|------|---------|
| 0x0046c210 | `CGame__ctor` | Wave 385 corrected this from an `IController`-only constructor label; initializes CGame-shaped state after base controller setup and installs the CGame vtable. |
| 0x0046c2b0 | `CGame__scalar_deleting_dtor` | Wave 385 scalar-deleting destructor wrapper; calls `CGame__dtor` and optionally frees `this`. |
| 0x0046c2d0 | `CGame__dtor` | Wave 385 destructor body; restores the CGame vtable, unregisters active-reader style links, and calls `CMonitor__Shutdown`. |
| 0x00441b10 | `CGame__SetGlobalSelectionSnapshot` | Wave799 screen-dump snapshot helper; copies optional four-dword global snapshot around `0x0066eb80`, sets pending flag `0x0066ff74`, and stores mode byte `0x0066ff75`. |
| 0x00441e40 | `CGame__ClearDwordValue` | Wave799 restart-loop-adjacent dword clear helper called by `CGame__InitRestartLoop` at `0x0046c57d`; exact owning field remains unproven. |
| 0x0046c360 | [CGame__Init](./CGame__Init.md) | Core game startup init (engine/imposters/render queue/static shadows/interface/HUD) |
| 0x0046c430 | [CGame__InitRestartLoop](./CGame__InitRestartLoop.md) | Per-level/restart runtime init (state reset, event manager, UI/runtime allocations, command/CVar registration) |
| 0x0046c990 | [CGame__Shutdown](./CGame__Shutdown.md) | Wave1003 recovered source-backed top-level shutdown boundary; calls HUD/interface/resource/memory cleanup and outro/status helpers before restart-loop teardown |
| 0x0046ca70 | [CGame__ShutdownRestartLoop](./CGame__ShutdownRestartLoop.md) | Per-level/restart teardown (runtime frees, script/event cleanup, subsystem reset) |
| 0x0046cd30 | [CGame__LoadResources](./CGame__LoadResources.md) | Loads level resources (resource bundle, texture/mesh resources, particle set) |
| 0x0046cdf0 | [CGame__LoadLevel](./CGame__LoadLevel.md) | Loads world/level data and creates per-player runtime objects |
| 0x0046d040 | [CGame__PostLoadProcess](./CGame__PostLoadProcess.md) | Post-load world/player setup and readiness checks |
| 0x0046d3a0 | `CGame__SetSlot` | Wave803 runtime slot-bit setter; range-checks slot `0..255`, then sets/clears `this+0x308[(slot>>5)]` bit `1 << (slot & 31)` |
| 0x0046d410 | `CGame__GetSlot` | Wave803 runtime slot-bit getter; range-checks slot `0..255`, then returns the bit test from `this+0x308[(slot>>5)]` |
| 0x0046d470 | [CGame__FillOutEndLevelData](./CGame__FillOutEndLevelData.md) | Captures end-of-level summary/progression snapshot data |
| 0x0046d890 | [CGame__RunIntroFMV](./CGame__RunIntroFMV.md) | Intro cutscene flow (lookup, path fallback, unlock goodie, play FMV) |
| 0x0046d9f0 | [CGame__RunOutroFMV](./CGame__RunOutroFMV.md) | Outro cutscene flow with conditional variants and end-level credits trigger |
| 0x004726b0 | [CGame__RollCredits](./CGame__RollCredits.md) | End-credits loop (temporary control handlers + credits renderer until completion/skip) |
| 0x0046dc00 | [CGame__PlayMusicForCurrentLevel](./CGame__PlayMusicForCurrentLevel.md) | Level music selector (tutorial track for level 100, otherwise in-game track) |
| 0x0046dc30 | [CGame__RestartLoopRunLevel](./CGame__RestartLoopRunLevel.md) | Per-restart pass inside a level (load/process/prerun/main-loop/cleanup) |
| 0x0046e240 | [CGame__RunLevel](./CGame__RunLevel.md) | Top-level level driver (init, restart-loop orchestration, shutdown/quit return) |
| 0x0046e460 | [CGame__Render](./CGame__Render.md) | Main render path (viewport setup, split-screen cameras, post-render pass) |
| 0x0046e910 | [CGame__Update](./CGame__Update.md) | Core gameplay tick/update path (event manager/controller/game-state/fade handling) |
| 0x004b7d90 | `CGame__PumpBinkVoiceSampleQueue` | Wave818 singleton Bink/audio queue pump called by `CGame__Update` at `0x0046ea77`; creates/plays queued voice sample and clears active-reader state |
| 0x0046eee0 | [CGame__MainLoop](./CGame__MainLoop.md) | Per-frame game loop (process, update, render, timing/fraction management) |
| 0x0046f2c0 | [CGame__GetCamera](./CGame__GetCamera.md) | Returns `mCurrentCamera[number]` |
| 0x0046f2d0 | [CGame__SetCamera](./CGame__SetCamera.md) | Thin wrapper around `CGame__SetCurrentCamera(number, cam, false)` |
| 0x0046f2f0 | [CGame__DeclareLevelWon](./CGame__DeclareLevelWon.md) | Level-won transition path |
| 0x0046f360 | [CGame__MPDeclarePlayerWon](./CGame__MPDeclarePlayerWon.md) | Multiplayer winner declaration (player 1/2) |
| 0x0046f3e0 | [CGame__MPDeclareGameDrawn](./CGame__MPDeclareGameDrawn.md) | Multiplayer draw declaration |
| 0x0046f430 | [CGame__DeclareLevelLost](./CGame__DeclareLevelLost.md) | Level-lost transition path |
| 0x0046f550 | [CGame__DeclarePlayerDead](./CGame__DeclarePlayerDead.md) | Death handling + camera switch + respawn/loss routing |
| 0x0046f7e0 | [CGame__ReceiveButtonAction](./CGame__ReceiveButtonAction.md) | Debug button dispatcher (0..14); contains Aurore gate for free camera |
| 0x0046fae0 | [CGame__UnPause](./CGame__UnPause.md) | Clears pause state and deactivates pause menu path |
| 0x0046fb00 | [CGame__Pause](./CGame__Pause.md) | Pause entrypoint with optional pause-menu handoff |
| 0x0046fb80 | [CGame__ToggleDebugUnitForward](./CGame__ToggleDebugUnitForward.md) | Debug unit selection forward |
| 0x0046fc40 | [CGame__ToggleDebugUnitBackward](./CGame__ToggleDebugUnitBackward.md) | Debug unit selection backward |
| 0x0046fd40 | [CGame__ToggleDebugSquadBackward](./CGame__ToggleDebugSquadBackward.md) | Debug squad selection backward |
| 0x0046fe20 | [CGame__ToggleDebugSquadForward](./CGame__ToggleDebugSquadForward.md) | Debug squad selection forward |
| 0x0046fec0 | [CGame__StartPlayingState](./CGame__StartPlayingState.md) | Transitions game state to playing, posts script event |
| 0x0046ff10 | [CGame__HandleEvent](./CGame__HandleEvent.md) | Core event dispatcher for gameplay state/events |
| 0x00470120 | [CGame__RespawnPlayer](./CGame__RespawnPlayer.md) | Respawn flow and spawn-point selection |
| 0x00470430 | [CGame__ToggleFreeCameraOn](./CGame__ToggleFreeCameraOn.md) | Enable free camera for a player slot |
| 0x004705d0 | [CGame__GetController](./CGame__GetController.md) | Returns `mController[player]` |
| 0x004705e0 | [CGame__SetCurrentCamera](./CGame__SetCurrentCamera.md) | Assign active camera (current vs old depending on free-cam mode) |
| 0x0053ecc0 | `CDXEngine__PostRender` | Engine post-render overlay/state pass called from `CGame__Render` |

### CDXGame Lifecycle (Wave 385)

| Address | Name | Purpose |
|---------|------|---------|
| 0x00541f00 | `CDXGame__dtor_thunk` | Unconditional jump to `CGame__dtor`; source and RTTI evidence support `CDXGame : CGame`. |
| 0x00541f10 | `CDXGame__ctor` | Corrects stale `CFrontEndVideo` constructor label; calls `CGame__ctor` and installs the CDXGame secondary vtable at `0x005e509c`. |
| 0x00541f30 | `CDXGame__scalar_deleting_dtor` | Corrects stale `CFrontEndVideo` scalar-destructor label; calls `CDXGame__dtor_thunk` and optionally frees `this`. |

## Wave751 Unwind Cleanup Evidence (2026-05-22)

Wave751 saved game.cpp-adjacent compiler-generated SEH unwind cleanup callbacks with the `unwind-continuation-wave751` and `wave751-readback-verified` tags. All rows are static retail Ghidra evidence only, saved as `void __cdecl Unwind@...(void)`, with no renames, no function-boundary changes, and no executable-byte changes.

Representative rows:

| Address | Evidence |
| --- | --- |
| `0x005d2780 Unwind@005d2780` | DATA scope-table xref `0x0061b5f4`; calls `OID__FreeObject_Callback` with game.cpp debug path `0x0062bba4`, line `0x26`, allocation/type value `0x108`, pointer `*(EBP-0x18)`. |
| `0x005d2799 Unwind@005d2799` | DATA scope-table xref `0x0061b5fc`; calls `CGenericCamera__dtor` on `*(EBP-0x18)`. |
| `0x005d27a1 Unwind@005d27a1` | DATA scope-table xref `0x0061b604`; calls `CGenericActiveReader__dtor` on `*(EBP-0x14)`. |
| `0x005d27d0 Unwind@005d27d0` | DATA scope-table xref `0x0061b634`; calls `CGenericCamera__dtor` on `*(EBP-0x10)`. |
| `0x005d27f0 Unwind@005d27f0` | DATA scope-table xref `0x0061b65c`; calls `CMonitor__Shutdown_Thunk` on `*(EBP-0x10)`. |
| `0x005d27f8 Unwind@005d27f8` | DATA scope-table xref `0x0061b664`; calls `CGenericActiveReader__dtor` on `(*(EBP-0x10))+0x9f8`. |
| `0x005d2810 Unwind@005d2810` through `0x005d28bf Unwind@005d28bf` | DATA scope-table refs `0x0061b68c` through `0x0061b6c4`; game.cpp `OID__FreeObject_Callback` cleanup rows with line/type values `0x2b/0x1f9`, `0x2b/0x1fa`, `0x29/0x1fb`, `0x2a/0x1fc`, `0x2a/0x1fd`, `0x78/0x1ff`, `0x2a/0x200`, and `0x80/0x201`. |
| `0x005d28f0 Unwind@005d28f0` and `0x005d2909 Unwind@005d2909` | DATA scope-table refs `0x0061b6ec` and `0x0061b6f4`; game.cpp allocation cleanup for `*(EBP+0x4)` with line/type values `0x28/0x353` and `0x27/0x366`. |
| `0x005d2930 Unwind@005d2930` | DATA scope-table xref `0x0061b71c`; calls `CMonitor__Shutdown_Thunk` on `EBP-0x114`. |
| `0x005d2950 Unwind@005d2950` | DATA scope-table xref `0x0061b744`; calls `CDXLandscape__ReleaseSurfaces` on `EBP-0x44`. |
| `0x005d2970 Unwind@005d2970`, `0x005d29a0 Unwind@005d29a0`, `0x005d29d0 Unwind@005d29d0`, and `0x005d29d8 Unwind@005d29d8` | DATA scope-table refs `0x0061b76c`, `0x0061b794`, `0x0061b7bc`, and `0x0061b7c4`; later game.cpp allocation/monitor cleanup rows, ending with line/type `0x27/0x11be` at `0x005d29d8`. |

The same Wave751 tranche spans `0x005d2730 Unwind@005d2730` through `0x005d29d8 Unwind@005d29d8`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-204801_post_wave751_unwind_continuation_verified`. Next high-signal queue head is `0x005d29f1 Unwind@005d29f1`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`. Exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Wave752 Unwind Cleanup Evidence (2026-05-22)

Wave752 saved the next game.cpp-adjacent compiler-generated SEH unwind cleanup callback with the `unwind-continuation-wave752` and `wave752-readback-verified` tags. The game.cpp row is static retail Ghidra evidence only, saved as `void __cdecl Unwind@...(void)`, with no renames, no function-boundary changes, and no executable-byte changes.

| Address | Evidence |
| --- | --- |
| `0x005d29f1 Unwind@005d29f1` | DATA scope-table xref `0x0061b7cc`; calls `OID__FreeObject_Callback` with game.cpp debug path `0x0062bba4`, line `0x27`, allocation/type value `0x11bf`, pointer `*(EBP-0x1c)`. |

The full Wave752 tranche spans `0x005d29f1 Unwind@005d29f1` through `0x005d2c40 Unwind@005d2c40` across game.cpp, GillM.cpp, GillMHead.cpp, GroundAttackAircraft.cpp, GroundUnit.cpp, and GroundVehicle.cpp cleanup evidence. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-212829_post_wave752_unwind_continuation_verified`. Next high-signal queue head is `0x005d2c48 Unwind@005d2c48`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`. Exact parent source-body identity, runtime game cleanup behavior, BEA patching, and rebuild parity remain deferred.

### CGame Helpers (2026-02-25 Semantic Tranche; Wave 381 Refined)

| Address | Name | Purpose |
|---------|------|---------|
| 0x004080f0 | [CGame__IsWalkerGroundedOrCollision](./CGame__IsWalkerGroundedOrCollision.md) | Checks walker-state plus ground/collision gate used by movement/camera logic |
| 0x00470650 | [CGame__DrawDebugStuff](./CGame__DrawDebugStuff.md) | Wave 381 supersedes the older debug-memory label; source-parity debug overlay path |
| 0x004714c0 | [CGame__DrawGameStuff](./CGame__DrawGameStuff.md) | Wave 405 supersedes stale `FrontendUpdate_CheatChecks`; source-parity game overlay/status path |
| 0x00472570 | [CGame__DoWeWantMesh](./CGame__DoWeWantMesh.md) | Mesh-name filter for player cockpit and wingman mesh resource loading |
| 0x004725d0 | [CGame__IsMultiplayer](./CGame__IsMultiplayer.md) | Wave 406 supersedes stale `CExplosionInitThing__CheckValueRange_852_899`; source-parity current-level range check for `850..899` |
| 0x004725f0 | [CGame__GetPlayerLives](./CGame__GetPlayerLives.md) | Returns player-1 or player-2 lives counter |
| 0x00472650 | [CGame__IsRunningResources](./CGame__IsRunningResources.md) | Compares current level with the last resource-loaded level global |
| 0x00472670 | [CGame__GetNumPrimaryObjectives](./CGame__GetNumPrimaryObjectives.md) | Wave 381 supersedes `CGame__CountActiveSlots_A`; counts defined primary objective rows at `+0x4c` |
| 0x00472690 | [CGame__GetNumSecondaryObjectives](./CGame__GetNumSecondaryObjectives.md) | Wave 381 supersedes `CGame__CountActiveSlots_B`; counts defined secondary objective rows at `+0x9c` |
| 0x004eb1e0 | [CGame__ResetRenderStateForWorldRender](./CGame__ResetRenderStateForWorldRender.md) | Reinitializes D3D render-state defaults before world rendering |

Wave 381 also corrected `0x00472240` out of `game.cpp` to `console.cpp` as `CConsole__AppendToStatusBufferV`, and corrected `0x00472270` out of `game.cpp` to `FrontEnd.cpp` as `Frontend__XorWideTextBlock100BytesToScratch`. Wave 405 restored `0x004714c0` to `game.cpp` as `CGame__DrawGameStuff` after caller read-back showed the `CDXEngine__PostRender` sequence `CGame__DrawDebugStuff(&DAT_008a9a98)` then `CGame__DrawGameStuff(&DAT_008a9a98)`. Wave 406 restored `0x004725d0` to `game.cpp` as `CGame__IsMultiplayer` after source/read-back showed the same `850..899` current-level predicate and cross-cutting `CGame` singleton callers. Wave510 corrected stale `CGame` ownership for `0x004eaf20` and `0x004eb130`; these are now documented as `CStart__SpawnBattleEngine` and `CStart__Available` under [`SpawnPoint.cpp`](../SpawnPoint.cpp/_index.md) because `CGame__RespawnPlayer` calls them through start-point fallback flow.

## Key Observations

- Game initialization is a critical entry point for understanding how subsystems are configured
- Main-loop helper call chain is now partially named and source-aligned:
  - `CProfiler__ResetAll` (`0x00523db0`)
  - `PLATFORM__Process` (`0x00515880`)
  - `CController__InactivityMeansQuitGame` (`0x0042d810`)
  - `CSoundManager__UpdateStatus` (`0x004e1b20`)
- Cutscene helper alignment:
  - `lookup_FMV` (`0x00523120`) resolves intro/outro FMV ids from the level lookup table.
  - `Cutscene_FormatPath_WithSmallFallback` (`0x0046d810`) centralizes `%02d` vs `%02d_small` path fallback used by cutscene-award/playback paths.
  - `CGame__RunIntroFMV` (`0x0046d890`) and `CGame__RunOutroFMV` (`0x0046d9f0`) now carry source-aligned naming and signatures.
  - `CGame__RollCredits` (`0x004726b0`) drives the interactive credits sequence used by final-level outro routes.
- Restart-loop local helper alignment:
  - `CWaitForStart__ctor` (`0x0046dbd0`) initializes the temporary wait object consumed by restart-loop scheduling logic.
- Related to Career, Script, World, and other core systems

## Related Files

- Career.cpp - Career/save system
- World.cpp - Level loading
- Script.cpp - Scripting system

---
*Migrated from ghidra-analysis.md (Dec 2025)*
