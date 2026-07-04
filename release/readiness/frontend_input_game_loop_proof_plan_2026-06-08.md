# Frontend / Input / Game Loop Proof Plan Readiness Note

Status: proof plan complete, not runtime proof
Date: 2026-06-08
Scope: `frontend-input-game-loop-proof-plan`

This readiness note records a public-safe static-to-proof planning slice for the frontend/input/game-loop surface. It is not a new static re-audit wave, not a runtime test, not a screenshot/capture proof, not a native input proof, not a save/options mutation proof, not a frontend-video playback proof, not a BEA patch, not a Godot slice, and not a rebuild parity claim.

Primary static source: `frontend-input-game-loop-static-review-2026-05-26.md`. The plan records static authorities, child proof lanes, copied-profile/app-owned guardrails, layout unknowns, input boundaries, and stop conditions before any executable proof work can start.

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.

Static source evidence:

- Wave907 (`frontend-input-game-loop-static-review-wave907`): `436` selected rows across `33` families with clusters `Frontend pages 176`, `Game loop / player 69`, `Frontend core / video render 54`, `Menu widgets 51`, `Input / controller 48`, and `Pause / message 38`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified`.
- Wave922 (`frontend-text-layout-review-wave922`): frontend text wrapping and text-id/fallback resolution evidence. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260527-175851_post_wave922_frontend_text_layout_review_verified`.
- Wave1179 (`wave1179-input-audio-support-current-risk-review`): `Input__UpdateCursorCenterWithWindowScale`, `Input__ResetMouseTransientState`, `GameControllers__RelinquishControlForTarget`, and `Audio__ReinitializeSoundAndRestoreMusic`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified`.
- Wave1197 (`wave1197-fepbeconfig-frontend-residual-current-risk-review`): `CFEPBEConfig__Init`, `CFEPMultiplayerStart__SetConfigDescriptionByIndex`, `CFEPBEConfig__PlayWeaponSound`, and `CFEPBEConfig__PlayWeaponSoundAlt`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-211310_post_wave1197_fepbeconfig_frontend_residual_current_risk_review_verified`.

Representative anchors:

| Surface | Static anchor |
| --- | --- |
| Game loop/player | `0x0046eee0 CGame__MainLoop`, `0x0046e240 CGame__RunLevel`, `0x0046f7e0 CGame__ReceiveButtonAction`, `0x0046fb00 CGame__Pause`, `0x0046fae0 CGame__UnPause`, `0x0046cdf0 CGame__LoadLevel`, `0x004d3080 CPlayer__AssignBattleEngine` |
| Frontend core | `0x004684d0 CFrontEnd__Run`, `0x00466ae0 CFrontEnd__SetPage`, `0x004669a0 CFrontEnd__ReceiveButtonAction`, `0x00468700 CFrontEnd__RenderCursorEndSceneAndAsyncSave` |
| Page handlers | `CFEPMultiplayerStart__Init`, `CFEPMultiplayerStart__ButtonPressed`, `CFEPLevelSelect__ButtonPressed`, `CFEPMain__DoAction`, `0x00464c50 CFEPSaveGame__CreateSave`, `0x00461e20 CFEPLoadGame__DoLoad`, `CFEPOptions__WriteDefaultOptionsFile`, `0x0045d7e0 CFEPGoodies__Process` |
| Frontend config/text | `CFEPBEConfig__Init`, `CFEPMultiplayerStart__SetConfigDescriptionByIndex`, `CFEPBEConfig__PlayWeaponSound`, `CFEPBEConfig__PlayWeaponSoundAlt`, `TextLayout__WrapWideTextToFixedLines`, `CFrontEnd__ResolveEpisodeNameTextByIndex`, `FrontEndText__GetLocalizedOrFallbackTextByToken` |
| Input/controller | `0x0042db40 CController__DoMappings`, `0x0042e4d0 CController__SendButtonAction`, `0x00513120 PlatformInput__InitDirectInput`, `0x00513370 PlatformInput__PollPadState`, `0x00514760 CPCController__ReadControllerState`, `0x0042da00 Input__UpdateCursorCenterWithWindowScale`, `0x00523db0 Input__ResetMouseTransientState`, `0x004cdd70 GameControllers__RelinquishControlForTarget` |
| Pause/message | `0x004d06e0 CPauseMenu__ResumeGameAndPersistOptions`, `CPauseMenu__ButtonPressed`, `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`, `0x004b7ea0 CMessageBox__StartVoiceOrFallbackTextReveal`, `0x004b9ec0 CMessageLog__HandleInputCommand` |
| Frontend video | `0x005412e0 CDXFrontEndVideo__Open`, `0x00541790 CDXFrontEndVideo__Render` |

Proof-plan boundaries:

- The plan is limited to future copied-profile, copied-file, or app-owned artifact-root work.
- Any future proof must select one child lane at a time: game-loop route accounting, frontend page transition, input/controller mapping, save/load/options menu handoff, pause/message lifecycle, frontend-video wrapper, or Goodies/level/multiplayer page behavior.
- Any future proof must keep scoped native input, save/options writes, media/video playback, and visual output as separate claim lanes.
- Any future proof must record whether inputs are copied retail data, sanitized fixtures, or generated app-owned data.
- Any future proof must stop on installed-game mutation need, unscoped native input, ambiguous window focus, unexpected save/options mutation, private media leakage risk, frontend-video codec/tooling uncertainty, broad game-loop scope creep, or visual-output ambiguity.
- Stop on installed-game mutation need is an explicit gate, not a warning to handle later.

No runtime menu navigation, runtime input/controller behavior, runtime pause/message behavior, runtime save/load/defaultoptions behavior, runtime Goodies wall behavior, runtime frontend-video/Bink/FMV behavior, runtime voice/audio behavior, runtime gameplay/game-loop outcomes, visible frontend/HUD output, exact concrete layouts, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity claim is made.
