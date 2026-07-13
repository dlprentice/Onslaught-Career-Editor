# Frontend / Input / Game Loop Static Review

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x0046e910` comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: static-coherent system slice
Date: 2026-05-26
Scope: `frontend-input-game-loop-static-review-wave907`

Wave907 reviews the frontend, menu-page, controller/input, pause/message, player-view, frontend-video, and game-loop surface after the loaded Ghidra function-quality queue reached `6113/6113 = 100.00%`. It ties `CGame`, `CFrontEnd`, frontend page objects, menu-item widgets, controller mapping, PC input bridges, pause/menu persistence, message-box/log display, player view handoff, and frontend video playback into one static classification.

Classification: `static-coherent frontend/input/game-loop core`.

Static-to-proof planning: `frontend-input-game-loop-proof-plan.md` records the bounded copied-profile/app-owned child proof lanes for this Wave907 surface. It is a planning artifact only, not runtime menu/input behavior, save/load/defaultoptions behavior, frontend-video playback, visual QA, patch behavior, rebuild parity, or no-noticeable-difference proof.

Source boundary: Stuart's source remains useful architecture/name/logic evidence, but the authority for this review is the Steam retail binary as loaded in Ghidra plus current public-safe read-back docs. This review is not runtime UI, input, audio, video, or visual proof.

Wave1179 input/controller bridge update: Wave1179 (`wave1179-input-audio-support-current-risk-review`) accounts for `6 input/controller/audio support current-risk rows` with fresh Ghidra export evidence and tag-only normalization. In this frontend/input/game-loop slice, the directly relevant rows are `Input__UpdateCursorCenterWithWindowScale`, `Input__ResetMouseTransientState`, `GameControllers__RelinquishControlForTarget`, and the options-tail audio bridge `Audio__ReinitializeSoundAndRestoreMusic`; the same wave also carries `CWaveSoundRead__ScalarDeletingDestructor` and `CPCSoundManager__LoadSampleFromBuffer_StubFail` for the audio support side. Apply/read-back used `ApplyInputAudioSupportCurrentRiskWave1179.java`: `updated=6 skipped=0`, `tags_added=56`, no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change. Codex read-only consults used; one consult recommended four-row split, while Codex root final judgment kept the six-row input/audio support slice. No Cursor/Composer was used. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; Wave1108 current focused accounting is `721/1179 = 61.15%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 458; current risk candidates: 6166; fresh exports verified `13 xref rows` and `152 instruction rows`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified`. Runtime input behavior, runtime controller/menu behavior, runtime audio/device-loss/sample-reader behavior, exact concrete input/controller/audio layouts, exact source-body identity, BEA patching behavior, visual/audio QA, gameplay outcomes, and rebuild parity remain separate proof. Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference; actual no-noticeable-difference parity still requires later runtime, asset, visual, control, timing, save, patch, and rebuild proof. Probe token anchor: Wave1179; wave1179-input-audio-support-current-risk-review; 721/1179 = 61.15%; 6 input/controller/audio support current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 458; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=6 skipped=0; tags_added=56; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consults used; Codex root final judgment; consult recommended four-row split; root kept six-row input/audio support slice; no Cursor/Composer; 0 / 0 / 0; 6411/6411 = 100.00%; 13 xref rows; 152 instruction rows; Input__UpdateCursorCenterWithWindowScale; Input__ResetMouseTransientState; GameControllers__RelinquishControlForTarget; Audio__ReinitializeSoundAndRestoreMusic; CWaveSoundRead__ScalarDeletingDestructor; CPCSoundManager__LoadSampleFromBuffer_StubFail; [maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Function-Family Surface

The Wave907 evidence snapshot covers `436` function rows across `33` selected owner families. Every selected row has a non-empty comment and a clean signature with no exact-`undefined` return and no `param_N` placeholders.

Cluster counts:

| Cluster | Rows |
| --- | ---: |
| Frontend pages | 176 |
| Game loop / player | 69 |
| Frontend core / video render | 54 |
| Menu widgets | 51 |
| Input / controller | 48 |
| Pause / message | 38 |

Representative family counts:

| Family | Rows |
| --- | ---: |
| `CGame` | 56 |
| `CFrontEnd` | 41 |
| `CFEPMultiplayerStart` | 40 |
| `CMenuItem` | 25 |
| `CController` | 18 |
| `CFEPBEConfig` | 16 |
| `PlatformInput` | 15 |
| `CPCController` | 15 |
| `CMessageBox` | 14 |
| `CDXFrontEndVideo` | 13 |
| `CPauseMenu` | 13 |
| `CFEPVirtualKeyboard` | 13 |
| `CPlayer` | 13 |
| `CFEPOptions` | 13 |

Representative anchors include `CGame__MainLoop`, `CGame__RunLevel`, `CGame__ReceiveButtonAction`, `CGame__Pause`, `CGame__UnPause`, `CGame__LoadLevel`, `CFrontEnd__Run`, `CFrontEnd__SetPage`, `CFrontEnd__ReceiveButtonAction`, `CFrontEnd__RenderCursorEndSceneAndAsyncSave`, `CFEPMultiplayerStart__Init`, `CFEPMultiplayerStart__ButtonPressed`, `CFEPOptions__WriteDefaultOptionsFile`, `CFEPGoodies__Process`, `CFEPLevelSelect__ButtonPressed`, `CFEPMain__DoAction`, `CFEPSaveGame__CreateSave`, `CFEPLoadGame__DoLoad`, `CMenuItem__ButtonPressed`, `CController__DoMappings`, `CController__SendButtonAction`, `PlatformInput__InitDirectInput`, `PlatformInput__PollPadState`, `CPCController__ReadControllerState`, `CPauseMenu__ResumeGameAndPersistOptions`, `CPauseMenu__ButtonPressed`, `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`, `CMessageBox__StartVoiceOrFallbackTextReveal`, `CMessageLog__HandleInputCommand`, `CDXFrontEndVideo__Open`, `CDXFrontEndVideo__Render`, and `CPlayer__AssignBattleEngine`.

## Static Classification

- The selected frontend/input/game-loop owner families have no remaining function-quality queue debt.
- The current static documentation connects game startup/load/run/update/render loops, frontend page transition and render paths, FEP page action handlers, save/load/options/goodies menu handlers, input mapping and PC input bridges, pause menu persistence, message-box/log rendering, player view handoff, and frontend video wrapper rows.
- The verified read-only Ghidra backup for this review is `[maintainer-local-ghidra-backup-root]\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified`.

## What Remains Separate

- Exact concrete frontend, controller, input, player, message, pause, and video object layouts.
- Runtime menu navigation, controller/input behavior, pause behavior, save/load menu behavior, Goodies wall behavior, voice/message playback, Bink/frontend-video behavior, and visual QA.
- BEA patch behavior.
- Clean-room rebuild parity.
