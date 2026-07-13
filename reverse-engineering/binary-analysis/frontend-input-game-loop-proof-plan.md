# Frontend / Input / Game Loop Proof Plan

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x0042e4d0` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: active public-safe proof plan, not runtime proof
Last updated: 2026-06-08
Scope: `frontend-input-game-loop-proof-plan`

This plan is the next selected static-to-proof slice from `roadmap/static-to-proof-rebuild-transition-backlog.md` after the Engine / Platform / Math / Memory Support Proof Plan. It converts the saved frontend, input/controller, pause/message, player handoff, frontend-video, and game-loop static evidence into bounded child proof lanes for later copied-profile or app-owned work.

This plan does not launch BEA, mutate Ghidra, mutate the installed game, patch an executable, capture screenshots, drive native input, write saves/options files, play frontend video, run Goodies-wall behavior, start Godot work, or claim runtime menu behavior, runtime input/controller behavior, runtime save/load/options behavior, runtime pause/message behavior, runtime frontend-video behavior, visual QA, rebuild parity, or no-noticeable-difference parity.

The plan records static authorities, child proof lanes, copied-profile/app-owned guardrails, layout unknowns, user-input boundaries, and stop conditions before any executable proof work can start. The child-lane labels include game-loop route accounting, frontend page transition design, input/controller mapping design, save/load/options menu handoff design, pause/message lifecycle design, frontend-video wrapper design, player handoff design, Goodies/level/multiplayer page behavior design, and stop conditions.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; it is not the active completion gate.

The percentage front door remains `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md` and `reverse-engineering/binary-analysis/static-reaudit-progress.json`. This proof plan does not create a new static RE percentage.

Primary static contract sources:

- `reverse-engineering/binary-analysis/frontend-input-game-loop-static-review-2026-05-26.md`
- `reverse-engineering/binary-analysis/mapped-systems.md`
- `reverse-engineering/binary-analysis/functions/_index.md`
- `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`

Relevant retained evidence:

- Wave907 frontend/input/game-loop static review (`frontend-input-game-loop-static-review-wave907`): `436` selected function rows across `33` families after queue closure `6113/6113 = 100.00%`, with clusters `Frontend pages 176`, `Game loop / player 69`, `Frontend core / video render 54`, `Menu widgets 51`, `Input / controller 48`, and `Pause / message 38`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified`.
- Wave922 frontend text/layout review (`frontend-text-layout-review-wave922`): retained static evidence for frontend text wrapping, episode/level text id resolution, multiplayer level descriptions, localized/fallback token handling, and briefing color selection. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260527-175851_post_wave922_frontend_text_layout_review_verified`.
- Wave1179 input/controller/audio support current-risk review (`wave1179-input-audio-support-current-risk-review`): retained input/controller rows `Input__UpdateCursorCenterWithWindowScale`, `Input__ResetMouseTransientState`, `GameControllers__RelinquishControlForTarget`, and the options-tail bridge `Audio__ReinitializeSoundAndRestoreMusic`; no rename, no signature change, no executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified`.
- Wave1197 FEPBEConfig/frontend residual current-risk review (`wave1197-fepbeconfig-frontend-residual-current-risk-review`): retained frontend configuration rows `CFEPBEConfig__Init`, `CFEPMultiplayerStart__SetConfigDescriptionByIndex`, `CFEPBEConfig__PlayWeaponSound`, and `CFEPBEConfig__PlayWeaponSoundAlt`; comment/tag normalization only. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-211310_post_wave1197_fepbeconfig_frontend_residual_current_risk_review_verified`.
- HUD/frontend overlay proof planning is already separate at `hud-frontend-overlay-visual-runtime-proof-plan.md`; this Wave907 plan is broader frontend/input/game-loop routing, not HUD rendering proof.

## Static Anchors

The proof plan is built around saved retail Ghidra evidence and public-safe static docs. Stuart source remains useful for names and architecture, but the loaded Steam retail binary remains authority for function names, call edges, comments, and bounded signatures.

| Surface | Static anchor |
| --- | --- |
| Game loop and player handoff | `0x0046eee0 CGame__MainLoop`, `0x0046e240 CGame__RunLevel`, `0x0046f7e0 CGame__ReceiveButtonAction`, `0x0046fb00 CGame__Pause`, `0x0046fae0 CGame__UnPause`, `0x0046cdf0 CGame__LoadLevel`, and `0x004d3080 CPlayer__AssignBattleEngine`. |
| Frontend core routing | `0x004684d0 CFrontEnd__Run`, `0x00466ae0 CFrontEnd__SetPage`, `0x004669a0 CFrontEnd__ReceiveButtonAction`, and `0x00468700 CFrontEnd__RenderCursorEndSceneAndAsyncSave`. |
| Frontend page handlers | `CFEPMultiplayerStart__Init`, `CFEPMultiplayerStart__ButtonPressed`, `CFEPLevelSelect__ButtonPressed`, `CFEPMain__DoAction`, `0x00464c50 CFEPSaveGame__CreateSave`, `0x00461e20 CFEPLoadGame__DoLoad`, `CFEPOptions__WriteDefaultOptionsFile`, and `0x0045d7e0 CFEPGoodies__Process`. |
| Frontend config/text | `CFEPBEConfig__Init`, `CFEPMultiplayerStart__SetConfigDescriptionByIndex`, `CFEPBEConfig__PlayWeaponSound`, `CFEPBEConfig__PlayWeaponSoundAlt`, `TextLayout__WrapWideTextToFixedLines`, `CFrontEnd__ResolveEpisodeNameTextByIndex`, and `FrontEndText__GetLocalizedOrFallbackTextByToken`. |
| Menu widgets | `CMenuItem__ButtonPressed` and `CFEPVirtualKeyboard` family rows from the Wave907 family surface. |
| Input and controller mapping | `0x0042db40 CController__DoMappings`, `0x0042e4d0 CController__SendButtonAction`, `0x00513120 PlatformInput__InitDirectInput`, `0x00513370 PlatformInput__PollPadState`, `0x00514760 CPCController__ReadControllerState`, `0x0042da00 Input__UpdateCursorCenterWithWindowScale`, `0x00523db0 Input__ResetMouseTransientState`, and `0x004cdd70 GameControllers__RelinquishControlForTarget`. |
| Pause and message surfaces | `0x004d06e0 CPauseMenu__ResumeGameAndPersistOptions`, `CPauseMenu__ButtonPressed`, `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`, `0x004b7ea0 CMessageBox__StartVoiceOrFallbackTextReveal`, and `0x004b9ec0 CMessageLog__HandleInputCommand`. |
| Frontend video wrapper | `0x005412e0 CDXFrontEndVideo__Open`, `0x00541790 CDXFrontEndVideo__Render`, and the Wave907 frontend-video family rows. |

## Child Proof Lanes

Later executable work should select one child lane at a time. Do not combine menu routing, input injection, save writes, frontend video playback, Goodies behavior, and game-loop runtime behavior into one proof slice.

| Row | Planned proof item | Required evidence | Public-safe result |
| --- | --- | --- |
| 1 | Static frontend/input contract extraction | Produce a compact implementation-facing static contract from Wave907, Wave922, Wave1179, and Wave1197 anchors. | Function-family checklist, page-route notes, input path notes, layout unknowns, and claim boundaries. |
| 2 | Game-loop route accounting design | Select a non-mutating path such as startup/front-end loop state accounting before any BEA launch proof. | Expected route/call checklist and no gameplay outcome claim. |
| 3 | Frontend page transition design | Select one menu page transition or action path with page identity and side effects explicit. | Page transition checklist and stop conditions for ambiguous menu state. |
| 4 | Input/controller mapping design | Select one controller mapping or PC input bridge path with scoped input guardrails. | Mapping/input checklist; no runtime input behavior claim until observed on a copied profile. |
| 5 | Save/load/options menu handoff design | Select one copied-file menu handoff path and reuse the save/options byte-preservation guardrails. | App-owned/copied-file handoff checklist; no runtime save/load/defaultoptions claim. |
| 6 | Pause/message lifecycle design | Select one pause/menu or message-box/log text reveal path with visible-output and audio side effects separated. | Message/pause checklist and no voice/audio/visual claim. |
| 7 | Frontend-video wrapper design | Select one frontend-video open/render wrapper path without decoding/playback proof. | Wrapper/call-edge checklist and no Bink/FMV playback claim. |
| 8 | Goodies/level/multiplayer page design | Select one page behavior path with static page handler anchors and explicit save/profile side effects. | Page behavior checklist and no Goodies-wall/runtime unlock claim. |
| 9 | Stop conditions | Stop on installed-game mutation need, unscoped native input, ambiguous window focus, unexpected save/options mutation, private media leakage risk, frontend-video codec/tooling uncertainty, broad game-loop scope creep, or visual-output ambiguity. | Documented blocked/deferred status instead of widening scope. |
| 10 | Rebuild handoff | Translate proven child-lane behavior into clean-room frontend/input/game-loop notes only after a later proof result identifies what was observed. | Static-to-runtime contract notes with exact runtime and layout gaps marked. |

## Copied/App-Owned Guardrails

Any later proof execution must:

- Use copied profiles, copied saves/options, copied files, or app-owned artifact roots for generated outputs, logs, captures, patches, saves, caches, or harness data.
- Never mutate the installed Steam game directory or original executable.
- Keep input authority scoped to a managed/copied BEA window or non-runtime harness; do not send broad desktop input.
- Keep save/options writes behind copied-file allowlists and byte-diff checks.
- Keep frontend-video/media proof separate from private media leakage.
- Keep public notes aggregate and sanitized.
- Select one child lane at a time and preserve static/runtime/rebuild claim boundaries.
- Record whether the input is copied retail data, a sanitized fixture, or generated app-owned data.
- Stop if the proof requires broad game-loop/runtime behavior before the static child lane is explicit.

## Not Claimed

This plan is a static-to-proof planning artifact only. It does not prove:

- Runtime menu navigation.
- Runtime input/controller behavior.
- Runtime pause/message behavior.
- Runtime save/load/options/defaultoptions behavior.
- Runtime Goodies wall or unlock behavior.
- Runtime frontend-video, Bink, or FMV behavior.
- Runtime voice/audio behavior.
- Runtime gameplay/game-loop outcomes.
- Visible frontend or HUD output.
- Exact concrete frontend, input, controller, pause, message, player, or video layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Exit Gate For This Planning Slice

This planning slice is complete only when:

- This document and its lore-book mirror match.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `reverse-engineering/binary-analysis/_index.md`, and `reverse-engineering/RE-INDEX.md` point to this plan.
- `reverse-engineering/binary-analysis/frontend-input-game-loop-static-review-2026-05-26.md` points from the Wave907 static review to this plan.
- `release/readiness/frontend_input_game_loop_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/frontend_input_game_loop_proof_plan_probe.py --check` passes.
- Static closeout probes still pass without changing `static-reaudit-progress.json` or `static-reaudit-current-risk-ledger.json`.
