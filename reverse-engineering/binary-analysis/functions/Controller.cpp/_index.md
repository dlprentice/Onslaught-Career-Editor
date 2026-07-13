# Controller.cpp

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x0042e4d0` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Input controller handling functions from BEA.exe

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Controller.cpp handles input device management, including controller initialization and monitoring. The CController class manages input state, deadzone handling, and controller-to-player mapping.

**Debug Path**: `[maintainer-local-source-export-root]\Controller.cpp` (0x00625538)

Wave907 (`frontend-input-game-loop-static-review-wave907`) records controller and platform-input rows as part of the `static-coherent frontend/input/game-loop core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only). The slice covers `436` rows across `33` families and includes `CController__DoMappings`, `CController__SendButtonAction`, `PlatformInput__InitDirectInput`, `PlatformInput__PollPadState`, `CPCController__ReadControllerState`, and frontend/game anchors such as `CGame__ReceiveButtonAction` and `CFrontEnd__ReceiveButtonAction`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified`. Runtime controller/input behavior, visual QA, patch behavior, and rebuild parity remain separate proof.

Wave952 (`game-interface-menu-control-boundary-wave952`) recovered `0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput` from CGameInterface vtable `0x005dbc2c slot 3`. For this Controller.cpp boundary, the important static bridge is that the recovered GameInterface input receiver dispatches button/control IDs `0x2a..0x39`, calls `CGameInterface__AdvanceMenuSelectionWithWrap` and `CGameInterface__HandleMenuSelection`, and on the observed `0x39` path calls `CController__RelinquishControl(control_context)` before `CGame__UnPause(&DAT_008a9a98)`. Wave911 focused re-audit progress after Wave952 is `276/1408 = 19.60%`; export-contract closure is `6151/6151 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-091135_post_wave952_game_interface_menu_control_boundary_verified`. Exact source method name, individual button semantics, `0x00679fbc` meaning, runtime pause/menu/input behavior, BEA patching, and rebuild parity remain separate proof.

Wave1023 (`frontend-options-pause-menu-review-wave1023`) re-read the controller-owned bridge `0x004cdd70 GameControllers__RelinquishControlForTarget` with no mutation. Fresh metadata confirmed the saved `void __fastcall GameControllers__RelinquishControlForTarget(void * controlled_target)` signature and Wave479 bounded comment: it loops controller slots 0..1, compares each controller's current control target through `CController__GetToControl`, and calls `CController__RelinquishControl` when the target matches. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-233831_post_wave1023_frontend_options_pause_menu_review_verified`. Runtime controller/menu behavior, concrete control-target type, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave1179 (`wave1179-input-audio-support-current-risk-review`) re-read and tag-normalized `GameControllers__RelinquishControlForTarget` inside a `6 input/controller/audio support current-risk rows` slice. Fresh Ghidra export evidence verified `13 xref rows` and `152 instruction rows` across the slice; this row's xrefs are `CMessageLog__HandleInputCommand` and no-function close/back handler `0x0048ffcc`. The same slice also covers `Input__UpdateCursorCenterWithWindowScale`, `Input__ResetMouseTransientState`, `Audio__ReinitializeSoundAndRestoreMusic`, `CWaveSoundRead__ScalarDeletingDestructor`, and `CPCSoundManager__LoadSampleFromBuffer_StubFail`. Apply/read-back used `ApplyInputAudioSupportCurrentRiskWave1179.java`: `updated=6 skipped=0`, `tags_added=56`, no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change. Codex read-only consults used; one consult recommended four-row split, while Codex root final judgment kept the six-row input/audio support slice. No Cursor/Composer was used. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; Wave1108 current focused accounting is `721/1179 = 61.15%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 458; current risk candidates: 6166; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified`. Runtime input behavior, runtime controller/menu behavior, runtime audio/device-loss/sample-reader behavior, exact concrete input/controller/audio layouts, exact source-body identity, BEA patching behavior, visual/audio QA, gameplay outcomes, and rebuild parity remain separate proof. Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference. Probe token anchor: Wave1179; wave1179-input-audio-support-current-risk-review; 721/1179 = 61.15%; 6 input/controller/audio support current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 458; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=6 skipped=0; tags_added=56; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consults used; Codex root final judgment; consult recommended four-row split; root kept six-row input/audio support slice; no Cursor/Composer; 0 / 0 / 0; 6411/6411 = 100.00%; 13 xref rows; 152 instruction rows; Input__UpdateCursorCenterWithWindowScale; Input__ResetMouseTransientState; GameControllers__RelinquishControlForTarget; Audio__ReinitializeSoundAndRestoreMusic; CWaveSoundRead__ScalarDeletingDestructor; CPCSoundManager__LoadSampleFromBuffer_StubFail; [maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified; wave1108-current-risk-rank.

Wave1044 (`career-controller-residual-review-wave1044`) re-read the residual Controller rows `0x0042d640 CController__Init`, `0x0042d8a0 CController__StartRecording`, `0x0042d8c0 CController__StartPlayback`, `0x0042d8e0 CController__dtor`, and `0x004f00d0 CController__dtor_Thunk` with no mutation. Fresh evidence kept the saved names/signatures/comments coherent with source-shaped behavior and retail xrefs: `CController__Init` initializes `CSPtrSet`/`CDXMemBuffer`, registers the player active-reader deletion-list node at `player+0x04`, and stores input/config fields; `CController__StartRecording` sets flag `this+0x160` then calls `CDXMemBuffer__OpenWrite`; `CController__StartPlayback` sets flag `this+0x161` then calls `CDXMemBuffer__InitFromFile`; `CController__dtor` closes active buffers, calls `CMonitor__DeleteDeletionEvent`, frees reader nodes, clears the set, and runs `CDXMemBuffer__dtor_base`; `CController__dtor_Thunk` forwards directly to the destructor. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-103855_post_wave1044_career_controller_residual_review_verified`. Wave1044 overall keeps queue closure `6238/6238 = 100.00%`, Wave911 focused progress `735/1408 = 52.20%`, expanded static surface `977/1493 = 65.44%`, and top-500 coverage `500/500 = 100.00%`. Runtime controller/input/recording/playback behavior, concrete Controller/CPCController layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## 2026-05-25 Wave851 PC Platform/Controller Tail Read-Back

Wave851 PC platform/controller tail (`pc-platform-controller-tail-wave851`, `wave851-readback-verified`) saved comments/tags for the PC controller tail: `0x00514210 OptionsEntries__InitDefaultSingleBindingsTable`, `0x00514620 CPCController__scalar_deleting_dtor`, the CPCController button/key/analogue/POV vtable accessors from `0x00514640 CPCController__GetJoyAnalogueLeftX` through `0x00514900 CPCController__GetJoyPovY`, and adjacent platform wrappers. Probe token anchor: `Wave851 PC platform/controller tail`; `0x00514210 OptionsEntries__InitDefaultSingleBindingsTable`; `0x00514620 CPCController__scalar_deleting_dtor`; `0x00514640 CPCController__GetJoyAnalogueLeftX`; `CPCController__GetJoyButtonOnce`; `5729/6098 = 93.95%`; `0x00515ab0 D3DDevice__SetViewport`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-085618_post_wave851_pc_platform_controller_tail_verified`.

Static evidence ties `OptionsEntries__InitDefaultSingleBindingsTable` to 47 `OptionsEntries__InitSingleBindingEntry` calls and sentinel `DAT_008898b8`; the scalar deleting destructor to CPCController vtable slot 0, `CController__dtor_Thunk`, and optional `CDXMemoryManager__Free`; and the input methods to CPCController vtable slots 3-14 plus `PCController.cpp`/`.h` source-reference names. Runtime input behavior, exact pad/key table layouts, exact options-entry schema, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave850 D3D Shader/Input Tail Read-Back

Wave850 D3D shader/input tail (`d3d-shader-input-tail-wave850`, `wave850-readback-verified`) tightened the controller-to-platform key-query bridge. `0x00513a80 PlatformInput__GetKeyState3Core` is the held-state core used by `CPCController__GetKeyState3` / key-on style paths, returning `this+0x332e4+key`. `0x00513a90 PlatformInput__GetKeyOnceCore` is the one-shot core used by `CPCController__GetKeyOnce`, reading/clearing `this+0x331e4+key` and recording consumed keys through `0x00855424`. Probe token anchor: `Wave850 D3D shader/input tail`; `0x00513a80 PlatformInput__GetKeyState3Core`; `0x00513a90 PlatformInput__GetKeyOnceCore`; `CPCController__GetKeyOnce`; `5704/6098 = 93.54%`; `0x005140e0 CDXEngine__CaptureAviFrame`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-081702_post_wave850_d3d_shader_input_tail_verified`.

This is saved static retail/source-reference evidence only; exact key-table/queue layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x005145f0 | CPCController__ctor | RENAMED | PC controller ctor wrapper (installs vtable `0x005e48e0`); source-equivalent of Stuart `CPCController` ctor |
| 0x0042d9d0 | CController__Flush | RENAMED | Wave 373 saved as `void __thiscall`; copies current button fields to old fields, clears current fields, then calls vtable+`0x3c` (`DoMappings`). |
| 0x0042db40 | CController__DoMappings | RENAMED | Wave 373 saved as `void __thiscall`; main mapping engine with push-type dispatch, repeat timing, playback/record hooks, platform input cases, and `SendButtonAction`. |
| 0x005147b0 | CPCController__GetJoyButtonOnce | RENAMED | Joystick button edge `0 -> 1` using per-pad state tables (`old @ 0x00888fa4`, `current @ 0x00888f94`). |
| 0x005147f0 | CPCController__GetJoyButtonOn | RENAMED | Joystick button held state (current table `0x00888f94`). |
| 0x00514810 | CPCController__GetJoyButtonRelease | RENAMED | Joystick button edge `1 -> 0` using old/current tables. |
| 0x00514850 | CPCController__GetKeyOnce | RENAMED | Key edge query bridged by Wave850 to `0x00513a90 PlatformInput__GetKeyOnceCore` / consumed-key queue evidence. |
| 0x00514890 | CPCController__GetKeyOn | RENAMED | Key held query (no clear). Reads `0x00888c94[key]`. |
| 0x00514870 | CPCController__GetKeyState3 | RENAMED | Key held/state query bridged by Wave850 to `0x00513a80 PlatformInput__GetKeyState3Core`. |
| 0x00514640 | CPCController__GetJoyAnalogueLeftX | RENAMED | Reads joystick state `+0x00` and scales by `0.001`. |
| 0x00514670 | CPCController__GetJoyAnalogueLeftY | RENAMED | Reads joystick state `+0x04` and scales by `0.001`. |
| 0x005146a0 | CPCController__GetJoyAnalogueRightX | RENAMED | Reads joystick state `+0x08` and scales by `0.001`. |
| 0x005146d0 | CPCController__GetJoyAnalogueRightY | RENAMED | Reads joystick state `+0x14`, centers at `32768`, scales by `1/32768` (with guard). |
| 0x005148b0 | CPCController__GetJoyPovX | RENAMED | `sin(POV * 0.00017453294)`; returns 0 when POV is `-1`. |
| 0x00514900 | CPCController__GetJoyPovY | RENAMED | `-cos(POV * 0.00017453294)`; returns 0 when POV is `-1`. |
| 0x00514720 | CPCController__RecordControllerState | RENAMED | Writes `mButtons1/2/3` (offsets `+0x14/+0x18/+0x1c`) to `DXMemBuffer` (record/playback support). |
| 0x00514760 | CPCController__ReadControllerState | RENAMED | Reads `mButtons1/2/3`; on EOF closes buffer and clears playback flag (`this+0x161=0`). |
| 0x0042d640 | CController__Init | RENAMED | Base initializer called by `CPCController__ctor` (links controller to player monitor + stores config) |
| 0x0042d780 | CController__scalar_deleting_dtor | RENAMED | Scalar deleting destructor wrapper; calls `CController__dtor`, optionally frees `this`, and returns `this`. |
| 0x0042d7a0 | CController__ResetInactivityTimerConditional | RENAMED | Wave 373 saved as `void __cdecl`; source-parity inactivity reset helper with a retail non-interactive-section guard. |
| 0x0042d7d0 | CController__SetNonInteractiveSection | RENAMED | Source-parity noninteractive/inactivity timer helper; supersedes stale `CFrontEnd__SetLoadingTransitionGate`. |
| 0x0042d810 | CController__InactivityMeansQuitGame | RENAMED | Demo inactivity timeout quit guard (`Controller.cpp:87`) |
| 0x0042da00 | Input__UpdateCursorCenterWithWindowScale | RENAMED | Retail input/cursor-center helper called by CGame paths; exact Stuart source body remains unproven. |
| 0x0042e4b0 | CController__GetToControl | RENAMED | Returns current top-of-stack `IController*` |
| 0x0042e610 | CController__SetToControl | RENAMED | Push a monitored `IController*` onto `mToControlStack` |
| 0x0042e6e0 | CController__RelinquishControl | RENAMED | Pop current controller from `mToControlStack` |
| 0x0042e4d0 | CController__SendButtonAction | RENAMED | Routes button input to the top-of-stack `IController` (logs \"Nothing to Control !!\" if empty) |
| 0x0042e3d0 | CController__GetMappedInputValue | RENAMED | Mapping helper reached by `CController__DoMappings`; handles signed input-code families. |
| 0x0042e750 | CController__SetVibration | RENAMED | Source-parity vibration helper with gameplay and career-option gates; supersedes stale CGame owner label. |
| 0x004cdd70 | [GameControllers__RelinquishControlForTarget](./GameControllers__RelinquishControlForTarget.md) | SAVED | Wave479 corrected stale rocket-specific ownership. Loops controller slots 0..1 and relinquishes any controller whose top control target equals the supplied target pointer. |

## Control Bindings

The shipped PC/Steam build persists control bindings in the save/options file “options entries” block (`0x20*N` bytes at file offset `0x24BE`).

Wave841 Shared Default/False VFunc09 (`cvertexshader-shared-vfunc09-wave841`, `wave841-readback-verified`) records that `0x005019c0 VFuncSlot_09_005019c0` is now saved as `int __cdecl VFuncSlot_09_005019c0(void)`. For this Controller.cpp ownership area, the relevant RTTI-backed row is `CControllerDefinition` vtable `0x005db404` slot 7. The stub body is `XOR EAX,EAX; RET`; broader Wave841 evidence records `26 DATA pointer slots`, `49 RTTI-backed owner/slot rows`, `CVertexShader`, `CDXTrees`, queue proxy `5665/6098 = 92.90%`, next raw commentless row `0x0050ab60 CVBufTexture__RenderAndRestoreStateFlag4`, and verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260525-032940_post_wave841_cvertexshader_shared_vfunc09_verified`. Exact source virtual method names, caller-specific semantics, concrete class layouts, runtime behavior, BEA patching, and rebuild parity remain deferred.

Details: `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md`

Key functions:

| Address | Name | Notes |
|---------|------|------|
| 0x0042db10 | OptionsEntries__FindById | Finds a persisted 0x20-byte entry by `entry_id` |
| 0x00453460 | OptionsEntries__InitDefaultDualBindingsTable | Wave 370 hardened the default dual-binding table initializer. |
| 0x00453970 | CControllerDefinition__InitDefaults | Wave 370 hardened the control-definition defaults/vtable initializer. |
| 0x00453ac0 | SharedVFunc__NoOp_Ret0C | Wave 370 corrected this away from a controller-specific label to shared `RET 0x0c` behavior. |
| 0x00453ad0 | CControllerDefinition__RenderBindingsAndPollRemapInput | Wave 370 hardened the render/poll helper that calls the binding-list renderer. |
| 0x00453780 | Controls__ApplyPreset | Applies preset; updates `g_ControlSchemeIndex` and entry contents |
| 0x00453f50 | Controls__DispatchRemap | Wave 372 hardened the remap action-code dispatch helper while preserving its current signature. |
| 0x004541e0 | Controls__RemapKey | Wave 372 hardened the high-level key-remap path that stores globals, dispatches writes, and clears duplicates. |
| 0x00454e00 | Controls__GetDeviceCategory | Wave 372 hardened the device/input category mapper used by remap and duplicate-binding logic. |
| 0x00454e90 | Controls__ClearDuplicateBinding | Wave 372 hardened duplicate-binding cleanup across binding entries/slots. |
| 0x00455010 | ControlsUI__RenderBindingsList | Wave 370 hardened thiscall binding-list renderer + click handler that triggers capture. |
| 0x00456080 | Controls__BeginRemapCapture | Starts capture; schedules remap callback |
| 0x004565d0 | OptionsEntries__SetBindingSlot | Writes one slot (field0, device_code, scan, vk) into an entry |
| 0x00456650 | Controls__FindFirstFreeBindingSlot | Wave 372 hardened the active binding-table free-slot search helper. |
| 0x00456610 | CControllerDefinition__GetWidth | Wave 370 hardened compact control-definition getter. |
| 0x00456620 | CControllerDefinition__GetRowHeight | Wave 370 hardened compact control-definition getter. |
| 0x00456630 | CControllerDefinition__GetFlag1C | Wave 370 hardened compact control-definition flag reader. |
| 0x00456640 | CControllerDefinition__ClearFlag1C | Wave 370 hardened compact control-definition flag clearer. |

## Wave746 Saved-Ghidra Controller Unwind Continuation (2026-05-22)

Serialized headless dry/apply/read-back hardened `void __cdecl Unwind@...(void)` signatures, comments, and tags for the Controller.cpp-adjacent cleanup callbacks at `0x005d1b10 Unwind@005d1b10`, `0x005d1b1b Unwind@005d1b1b`, `0x005d1b26 Unwind@005d1b26`, `0x005d1b3f Unwind@005d1b3f`, `0x005d1b70 Unwind@005d1b70`, `0x005d1b7b Unwind@005d1b7b`, `0x005d1b90 Unwind@005d1b90`, and `0x005d1ba9 Unwind@005d1ba9`. The allocation-cleanup rows use Controller.cpp debug path `0x00625538`, line `0x27`, memtype `0x3c7`, and DATA scope-table xrefs `0x0061a9ac` and `0x0061aa14`; adjacent rows call `CSPtrSet__Clear`, `CDXMemBuffer__dtor_base`, and `CGenericActiveReader__dtor`.

This is the Controller.cpp portion of the `unwind-continuation-wave746` tranche, which spans `0x005d1aa3 Unwind@005d1aa3` through `0x005d1cc0 Unwind@005d1cc0`, uses the `wave746-readback-verified` tag, and has verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260522-173500_post_wave746_unwind_continuation_verified`. The next high-signal queue head is `0x005d1cd9 Unwind@005d1cd9`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`. Runtime controller allocation cleanup behavior, exact parent source-body identity, BEA patching, and rebuild parity remain unproven.

## Wave 373 Saved-Ghidra Controller Base Signature / Comment Hardening (2026-05-13)

Serialized headless dry/apply/read-back hardened signatures, comments, and tags for `3` already named CController base helpers in this ownership area. The pass keeps the current names for `CController__ResetInactivityTimerConditional`, `CController__Flush`, and `CController__DoMappings`, corrects the reset helper to `void __cdecl ...`, and corrects `Flush` / `DoMappings` to `void __thiscall ...`.

Validation verified `3` metadata rows, `3` decompile exports, `5` xref rows, `1365` instruction rows, `3` tag rows, and focused probe status `PASS` with `5` xref evidence hits, `13` instruction evidence hits, `0` stale signature hits, and `0` overclaim hits. Runtime input behavior, exact class layout, exact Stuart-source method identity for every retail branch, locals/types, BEA launch, game patching, and rebuild parity remain unproven.

## Wave 372 Saved-Ghidra Controls Remap Comment Hardening (2026-05-13)

Serialized headless dry/apply/read-back hardened comments/tags for `5` already named controls-remap helpers in this ownership area. The pass preserves current names/signatures for `Controls__DispatchRemap`, `Controls__RemapKey`, `Controls__GetDeviceCategory`, `Controls__ClearDuplicateBinding`, and `Controls__FindFirstFreeBindingSlot`.

Validation verified `5` metadata rows, `5` decompile exports, `93` xref rows, `1305` instruction rows, `5` tag rows, and focused probe status `PASS` with `10` xref evidence hits, `16` instruction evidence hits, `0` stale token hits, and `0` overclaim hits. Runtime remap/input behavior, exact source identities, concrete options-entry/controller layouts or field types, raw callback boundary ownership, BEA launch, game patching, and rebuild parity remain unproven.

## Wave 370 Saved-Ghidra Frontend Controls Corrections (2026-05-13)

Serialized headless dry/apply/read-back hardened `13` frontend controls/control-binding targets in this ownership area. `0x00453ac0` is now `SharedVFunc__NoOp_Ret0C`, not a controller-specific vfunc; `0x00455010` is saved as the thiscall binding-list renderer; `0x00456080` begins remap capture; `0x004565d0` writes one persisted binding slot; and the compact helpers at `0x00456610` through `0x00456640` now have proof-boundary signatures/comments.

Validation verified `13` metadata rows, `13` decompile exports, `26` xref rows, `2145` instruction rows, `13` tag rows, `64` vtable-slot rows, `252` callsite-instruction rows, and focused probe status `PASS`. Runtime remap/frontend behavior, concrete layouts/types, BEA launch, game patching, and rebuild parity remain unproven.

## Wave 327 Saved-Ghidra Controller / Input Corrections (2026-05-12)

Serialized headless dry/apply/read-back corrected five controller/input/vibration targets in this file's ownership area. This is saved static Ghidra name/signature/comment/tag evidence only; it does not prove runtime input, inactivity, cursor, force-feedback, concrete layout, local-variable/type recovery, BEA launch, game patching, or rebuild parity.

| Address | Current saved Ghidra signature | Evidence summary |
|---------|--------------------------------|------------------|
| 0x0042d780 | `void * __thiscall CController__scalar_deleting_dtor(void * this, uint flags)` | Compiler wrapper: calls `CController__dtor`, optionally dispatches `OID__FreeObject`, returns `this`, and ends with `RET 0x4`. |
| 0x0042d7d0 | `void __cdecl CController__SetNonInteractiveSection(bool nonInteractive)` | Source parity with `references/Onslaught/Controller.cpp` lines around `CController::SetNonInteractiveSection`; updates noninteractive/inactivity timer and attract-mode-related globals. |
| 0x0042da00 | `void __cdecl Input__UpdateCursorCenterWithWindowScale(bool recenterNow)` | Retail input/cursor-center helper called by `CGame` init/update paths; uses platform window dimensions and cursor-center globals. Exact Stuart source identity is not proven. |
| 0x0042e3d0 | `float __thiscall CController__GetMappedInputValue(void * this, int padNumber, int inputCode)` | Mapping helper used by `CController__DoMappings`; negative input codes route through analog-style vtable slots while non-negative codes return button/key style values. |
| 0x0042e750 | `void __thiscall CController__SetVibration(void * this, float inValue, int playerIndex)` | Source parity with `CController::SetVibration`; evidence includes game-state/options gates and device vibration dispatch context. |

The full tranche read-back verified `7/7` metadata rows, `7/7` decompile exports, `42` xref rows, `735` instruction rows, `7` tag rows, `4` renamed targets, and a refreshed quality queue of `5884` functions, `796` commented functions, `5088` commentless functions, `1989` undefined signatures, and `2269` `param_N` signatures.

## Details

### CController__ResetInactivityTimerConditional (0x0042d7a0)

- **Saved signature**: `void __cdecl CController__ResetInactivityTimerConditional(void)`.
- **Purpose**: Source-parity inactivity timer reset helper with an extra retail non-interactive-section guard.
- **Source parity**: Adjacent to Stuart `CController::ResetInactivityTimer()` behavior, but the retail guard means the saved name intentionally keeps the conditional boundary explicit.

**Behavior**:
1. Checks the retail non-interactive-section guard before refreshing inactivity state.
2. Reads platform time and updates the inactivity baseline used by the timeout/quit guard.
3. Has no `this` receiver in the saved retail signature.

### CController__SetNonInteractiveSection (0x0042d7d0)

- **Purpose**: Sets the global noninteractive state and resets the inactivity timer when returning to interactive mode.
- **Source parity**: `references/Onslaught/Controller.cpp`, `CController::SetNonInteractiveSection(bool onoff)`.

**Behavior**:
1. Stores the requested noninteractive state.
2. Uses platform time to refresh the inactivity baseline when interaction resumes.
3. Updates attract-mode/inactivity related globals used by the timeout guard.
4. Is called from loading/frontend/game transition paths; this corrects the stale `CFrontEnd__SetLoadingTransitionGate` owner label.

### Input__UpdateCursorCenterWithWindowScale (0x0042da00)

- **Purpose**: Updates retail cursor-center globals from current platform window dimensions.
- **Source parity**: Not proven as an exact Stuart source method body.

**Behavior**:
1. Reads platform window width/height.
2. Updates cursor center globals used by mouse/input paths.
3. Has CGame caller context, but the body is owner-neutral input support rather than a proven `CGame` method.

### CController__InactivityMeansQuitGame (0x0042d810)

- **Purpose**: Returns whether gameplay/frontend should auto-quit due to user inactivity timeout.
- **Source parity**: `references/Onslaught/Controller.cpp:87` (`CController::InactivityMeansQuitGame()`).

**Behavior**:
1. Exits early with `false` unless demo/inactivity gating globals are enabled.
2. Exits early when non-interactive mode is active.
3. Exits early when inactive-timeout config is `<= 0`.
4. Computes elapsed seconds via `PLATFORM__GetSysTimeFloat()` and compares against timeout (ms).
5. Logs timeout trace and returns `true` when threshold is exceeded.

**Called by**:
- `CGame__MainLoop` (`0x0046eee0`)
- `CFrontEnd__Process` (`0x00466ba0`)

### CController__Init (0x0042d640)

- **Purpose**: Initializes a `CController` instance (called by `CPCController__ctor`)
- **Calling Convention**: thiscall (ECX = this pointer)
- **Xref**: Found via debug path at 0x00625538, line 0x3C7 (967)
- **Called From**: `CPCController__ctor` (0x005145f0)

**Behavior**:
1. Sets vtable pointer to 0x005d977c
2. Initializes member fields at offsets 0x04, 0x2C
3. Allocates 4 bytes via memory manager (OID__AllocObject)
4. May allocate additional 16-byte monitor structure (references monitor.h)
5. Initializes controller state fields:
   - Offsets 0x14-0x28: Zeroed (6 dwords - likely axis/button state)
   - Offset 0x160: Byte set to 0
   - Offset 0x161: Byte set to 0
   - Offset 0x164: Float -1.0f (0xBF800000) - possibly deadzone or invalid state
   - Offset 0x168: Float 0.1f (0x3DCCCCCD) - possibly deadzone threshold
   - Offset 0x16C: `input_device` stored
   - Offset 0x170: Set to 0
   - Offset 0x174: `controller_config` stored

**Memory Layout** (partial CController struct):
```
+0x000: vtable pointer (0x005d977c)
+0x004: mToControlStack (CSPtrSet, 0x10 bytes: mFirst/mLast/mIterator/mSize)
+0x014: Input state array[6] (zeroed)
+0x02C: Secondary object (initialized via FUN_00547d70)
+0x160: Byte flag
+0x161: Byte flag
+0x164: Float (default -1.0f)
+0x168: Float (default 0.1f - deadzone?)
+0x16C: input_device
+0x170: Dword (zeroed)
+0x174: controller_config
```

### CPCController__ctor (0x005145f0)

- **Purpose**: PC controller constructor wrapper used by `CGame__LoadLevel` when creating player controllers.

**Behavior**:
1. Calls `CController__Init(this, player, input_device, controller_config)`
2. Overwrites vtable pointer to the final vtable (`0x005e48e0`)
3. Returns `this`

### CPCController__RecordControllerState (0x00514720)

- **Purpose**: Record controller button-bitfield state to the active `DXMemBuffer` (record/playback support).

**Behavior**:
1. `DXMemBuffer__WriteBytes(this + 0x14, 4)`
2. `DXMemBuffer__WriteBytes(this + 0x18, 4)`
3. `DXMemBuffer__WriteBytes(this + 0x1c, 4)`

### CPCController__ReadControllerState (0x00514760)

- **Purpose**: Read controller button-bitfield state from the active `DXMemBuffer` (playback support).

**Behavior**:
1. `DXMemBuffer__ReadBytes(this + 0x14, 4)`
2. `DXMemBuffer__ReadBytes(this + 0x18, 4)`
3. `DXMemBuffer__ReadBytes(this + 0x1c, 4)`
4. If `DXMemBuffer__IsEOF()` is true: closes the buffer and clears playback flag (`this+0x161=0`).

### CController__Flush (0x0042d9d0)

- **Saved signature**: `void __thiscall CController__Flush(void * this)`.
- **Purpose**: Per-frame flush step that captures old button state and triggers mapping.

**Behavior**:
1. Copies `mButtons{1,2,3}` into `mButtons{1,2,3}Old`
2. Clears current `mButtons{1,2,3}`
3. Calls `this->vtable[0xf]()` (`DoMappings`, vtable+`0x3c`)

### CController__DoMappings (0x0042db40)

- **Saved signature**: `void __thiscall CController__DoMappings(void * this)`.
- **Purpose**: Main controller mapping engine (push_type switch) that emits virtual button actions.

**Notes**:
- Uses a static controller-mapping table (base `0x008892dc`) and per-pad triples (pad0/pad1) within each entry.
- Calls into vtable slots for joystick buttons, key states, and analogue getters, then forwards results to `CController__SendButtonAction`.

### CController__GetMappedInputValue (0x0042e3d0)

- **Purpose**: Resolves one mapping-table input code into a float value for `CController__DoMappings`.

**Behavior**:
1. Handles negative input-code families through controller vtable calls for analog/pov-style inputs.
2. Handles non-negative button/key-style codes as binary values.
3. Returns `1.0` for active digital inputs and scaled float values for analog inputs.
4. Ends with `RET 0x8`, matching `padNumber` and `inputCode` stack arguments.

### CController__SetVibration (0x0042e750)

- **Purpose**: Applies controller vibration while respecting gameplay and career option gates.
- **Source parity**: `references/Onslaught/Controller.cpp`, `CController::SetVibration(float inValue, int player)`.

**Behavior**:
1. Gates nonzero vibration outside active gameplay state.
2. Checks the career vibration option for the requested player.
3. Dispatches to the device vibration path when vibration remains enabled.
4. This corrects the stale `CGame__DispatchVibrationWithCareerGate` owner label.

### CPCController__GetJoyButtonOnce (0x005147b0)

- **Purpose**: Low-level joystick query for “pressed once” (edge detect).

**Behavior**:
1. Reads old state table pointer from `0x00888fa4[pad_number]`
2. Reads current state table pointer from `0x00888f94[pad_number]`
3. Loads button byte from `state + 0x30 + button`
4. Returns `true` when `old == 0` and `current != 0`

### CPCController__GetJoyButtonOn (0x005147f0)

- **Purpose**: Low-level joystick query for “held” (current pressed state).

**Behavior**:
1. Reads current state table pointer from `0x00888f94[pad_number]`
2. Returns whether `*(state + 0x30 + button) != 0`

### CPCController__GetJoyButtonRelease (0x00514810)

- **Purpose**: Low-level joystick query for “released” (edge detect).

**Behavior**:
1. Reads old/current state tables as above
2. Returns `true` when `old != 0` and `current == 0`

### CController__SetToControl (0x0042e610)

- **Purpose**: Push a new `IController*` onto the controller stack (uses monitor.h deletion tracking)
- **Calling Convention**: thiscall (ECX = `CController* this`)
- **Parameters**: 1 parameter - `IController* to_control`
- **Xref**: Found via debug path at 0x00625538, line 0x3C7 (967)
- **Called From**: Multiple locations including:
  - CGame__RestartLoopRunLevel (0x0046df82)
  - CGame__Update (0x0046ee1b, 0x0046ee49, 0x0046ee60)
  - CGame__Pause (0x0046fb75)
  - CGame__ToggleFreeCameraOn (0x0047057c)
  - CGameInterface__HandleMenuSelection (0x00472c02, 0x00472c5c; Wave 382 corrected the older generic label and narrowed the handler to one explicit controller parameter)
  - FUN_004d0810 (0x004d0b00, 0x004d0bd7, 0x004d0d20)

**Behavior**:
1. Allocates a heap `CActiveReader<IController>` (4-byte `mToRead` cell) via `OID__AllocObject`
2. Stores `to_control` in the reader cell (`*reader = to_control`)
3. If `to_control != NULL`, registers the reader in `to_control`'s deletion list:
   - Lazily allocates `to_control->mDeletionEventList` at `to_control + 4` as a `CSPtrSet` (debug path `monitor.h`)
   - `CSPtrSet__AddToHead(to_control->mDeletionEventList, reader)`
   - This is equivalent to the monitor helper `CMonitor__AddDeletionEvent` (`0x00401040`) documented in `reverse-engineering/binary-analysis/functions/monitor.h/_index.md`
4. Pushes the reader onto `this->mToControlStack` via `CSPtrSet__AddToHead(this + 4, reader)`

**Notable Callers**:
- `CGame__Update` calls this function 3 times, suggesting it sets up monitoring for multiple controller/control-handoff paths during gameplay state transitions.

### CController__GetToControl (0x0042e4b0)

- **Purpose**: Returns the currently controlled target (`IController*`) from the top of `mToControlStack`.
- **Source parity**: `references/Onslaught/Controller.cpp:437`.

**Behavior**:
1. Reads stack head pointer at `this+0x04`.
2. Caches head in `this+0x0C` (iterator/cache slot used by subsequent stack helpers).
3. Returns `head->mValue` (`CActiveReader<IController>::ToRead()`), or null when head is null.

### CController__RelinquishControl (0x0042e6e0)

- **Purpose**: Pop the current `IController` from the stack and free its `CActiveReader`
- **Calling Convention**: thiscall (ECX = `CController* this`)

**Behavior**:
1. Reads `mToControlStack.mFirst->mValue` (a `CActiveReader<IController>*`)
2. Removes it from `mToControlStack` (`CSPtrSet__Remove(this+4, value)`)
3. Unlinks from the monitored controller deletion list (`CGenericActiveReader__dtor(value)`)
4. Frees the reader (`OID__FreeObject(value)`)
5. Validates stack is still non-empty (fatal logs if empty)

### GameControllers__RelinquishControlForTarget (0x004cdd70)

- **Purpose**: Owner-neutral helper that releases any player controller currently controlling a supplied target object.
- **Saved signature**: `void __fastcall GameControllers__RelinquishControlForTarget(void * controlled_target)`.
- **Wave479 correction**: Supersedes stale `CRocket__RelinquishControllerOwnership`; callers include `CMessageLog__HandleInputCommand` and a raw close/back handler, so the helper is not rocket-specific.

**Behavior**:
1. Uses `ECX` as `controlled_target`.
2. Iterates controller indices `0` and `1` through `CGame__GetController(&DAT_008a9a98, number)`.
3. Compares each controller's `CController__GetToControl()` result against `controlled_target`.
4. Calls `CController__RelinquishControl()` on matching controllers.

Static evidence only; exact source identity, concrete target type, runtime menu/input behavior, and rebuild parity remain unproven.

### CController__SendButtonAction (0x0042e4d0)

- **Purpose**: Main input dispatch for button actions and analogue values
- **Parameters**: `int button`, `float ana_val` (type of `ana_val` inferred; passed through to dispatch)

**Behavior (high level)**:
1. Updates internal per-range button bitfields at `this+0x14/0x18/0x1c`
2. If `mToControlStack.First() == NULL`, logs `"Nothing to Control !!"` and returns
3. Otherwise resolves `to_send = mToControlStack.First()->ToRead()` and dispatches:
   - `button < 0x10`: calls `CommandDispatcher__Handle(this, button, ana_val)` (command/debug path)
   - Otherwise routes to `to_send->ReceiveButtonAction(...)` with reconnect/pause gating

## Related Symbols

- **Vtable**: 0x005d977c (PTR_FUN_005d977c)
- **Vtable (PC controller)**: 0x005e48e0
- **Debug path (Controller.cpp)**: 0x00625538
- **Debug path (monitor.h)**: 0x0062551c
- **Memory manager instance**: 0x009c3df0
- **CSPtrSet__Init**: Lock/monitor initialization
- **CSPtrSet__AddToHead**: Monitor registration
- **CMonitor__AddDeletionEvent**: Lazily allocates/uses `to_control+0x04` deletion list and registers a reader cell (`0x00401040`)
- **CGenericActiveReader__SetReader**: Canonical helper for moving a reader to a new monitor (`0x00401000`)
- **CGenericActiveReader__dtor**: Unregisters an active reader from its monitored object's deletion list (used before freeing)
- **FUN_00547d70**: Secondary initialization routine
- **OID__AllocObject**: Memory allocation (takes size, type, debug_file, line)

## Notes

1. The memory allocator OID__AllocObject signature appears to be: `void* Alloc(size, type_id, debug_file, line_number)`
2. Monitor.h is also referenced, suggesting a separate monitoring/synchronization system
3. The float constants (-1.0f and 0.1f) suggest deadzone or threshold handling for analog inputs
4. CController struct is at least 0x178 bytes based on field accesses
