# Ghidra Frontend / Input / Game Loop Static Review Wave907 Readiness Note

Status: complete static review evidence
Date: 2026-05-26
Scope: `frontend-input-game-loop-static-review-wave907`

Wave907 is a read-only post-100 system review. It makes no Ghidra metadata mutation, no executable-byte change, no save mutation, and no BEA launch. The wave records a `static-coherent frontend/input/game-loop core` after the loaded Ghidra function-quality queue reached `6113/6113 = 100.00%`.

Evidence summary:

- Selected function rows: `436` rows across `33` families, all commented and clean-signature.
- Cluster counts: frontend pages `176`, game loop / player `69`, frontend core / video render `54`, menu widgets `51`, input / controller `48`, pause / message `38`.
- Large family anchors: `CGame` `56`, `CFrontEnd` `41`, `CFEPMultiplayerStart` `40`, `CMenuItem` `25`, `CController` `18`, `CFEPBEConfig` `16`, `PlatformInput` `15`, `CPCController` `15`, `CMessageBox` `14`, `CDXFrontEndVideo` `13`, `CPauseMenu` `13`, `CFEPVirtualKeyboard` `13`, `CPlayer` `13`, and `CFEPOptions` `13`.
- Representative functions: `CGame__MainLoop`, `CGame__RunLevel`, `CGame__ReceiveButtonAction`, `CFrontEnd__Run`, `CFrontEnd__SetPage`, `CFrontEnd__ReceiveButtonAction`, `CFEPMultiplayerStart__Init`, `CFEPOptions__WriteDefaultOptionsFile`, `CFEPGoodies__Process`, `CMenuItem__ButtonPressed`, `CController__DoMappings`, `CController__SendButtonAction`, `PlatformInput__InitDirectInput`, `PlatformInput__PollPadState`, `CPCController__ReadControllerState`, `CPauseMenu__ResumeGameAndPersistOptions`, `CMessageBox__StartVoiceOrFallbackTextReveal`, `CDXFrontEndVideo__Open`, `CDXFrontEndVideo__Render`, and `CPlayer__AssignBattleEngine`.
- Additional probe anchors: `CGame__Pause`, `CGame__UnPause`, `CGame__LoadLevel`, `CFrontEnd__RenderCursorEndSceneAndAsyncSave`, `CFEPMultiplayerStart__ButtonPressed`, `CFEPLevelSelect__ButtonPressed`, `CFEPMain__DoAction`, `CFEPSaveGame__CreateSave`, `CFEPLoadGame__DoLoad`, `CPauseMenu__ButtonPressed`, `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`, and `CMessageLog__HandleInputCommand`.
- Verified read-only Ghidra backup: `G:\GhidraBackups\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified`, `19` files, `173247367` bytes, `DiffCount=0`.

What this proves:

- The selected frontend/input/game-loop owner-family rows are closed under the current function-quality proxy.
- The public docs now review game startup/load/run/update/render loops, frontend page transitions, FEP page action handlers, save/load/options/goodies menu handlers, controller mapping, PC input bridges, pause persistence, message display, player view handoff, and frontend video wrappers as one static system slice.
- The claim is static coherence, not runtime frontend/input/video behavior or visual QA.

What remains unproven:

- Exact concrete object layouts.
- Runtime menu navigation, controller/input behavior, pause behavior, save/load menu behavior, Goodies wall behavior, voice/message playback, Bink/frontend-video behavior, and visual QA.
- BEA patch behavior.
- Clean-room rebuild parity.
