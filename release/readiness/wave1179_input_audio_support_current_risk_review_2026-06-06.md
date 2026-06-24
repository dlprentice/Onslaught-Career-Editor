# Wave1179 Input / Audio Support Current-Risk Review Readiness Note

Status: complete static tag-only normalization
Date: 2026-06-06
Scope: `wave1179-input-audio-support-current-risk-review`

Wave1179 accounts for `6 input/controller/audio support current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra metadata, tag, xref, instruction, and decompile exports. It performed tag-only normalization for all six rows: no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0042da00 Input__UpdateCursorCenterWithWindowScale` | Called by `CGame__InitRestartLoop` and `CGame__Update`; updates cached cursor-center/window-scale state from platform window dimensions. |
| `0x00523db0 Input__ResetMouseTransientState` | Called by `PlatformInput__InitMouse`, `PlatformInput__ShutdownMouse`, `CFrontEnd__Process`, `CGame__MainLoop`, and raw no-function render-tail callsites `0x0053f2dc` / `0x0053f306`; clears click/cursor latches and wheel/transient fields. |
| `0x004cdd70 GameControllers__RelinquishControlForTarget` | Called by `CMessageLog__HandleInputCommand` and raw close/back handler `0x0048ffcc`; loops controller slots and relinquishes a controller whose current control target matches the supplied pointer. |
| `0x004cddf0 Audio__ReinitializeSoundAndRestoreMusic` | Called by `OptionsTail_Read`; reinitializes `CSoundManager` after sound-option changes, then restores frontend music or current-level music depending on `frontend_music_after_reset`. |
| `0x005054e0 CWaveSoundRead__ScalarDeletingDestructor` | DATA xref `0x005dfc4c`; vtable slot 0 scalar-deleting destructor closes the wave reader and optionally frees `this`. |
| `0x00517290 CPCSoundManager__LoadSampleFromBuffer_StubFail` | Called by `CSoundManager__CreateSample`; PC buffer-load path is the source-backed `XOR EAX,EAX; RET 0x8` stub returning null. |

Read-back evidence:

- `ApplyInputAudioSupportCurrentRiskWave1179.java` dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=56 missing=0 bad=0`.
- `ApplyInputAudioSupportCurrentRiskWave1179.java` apply: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=56 missing=0 bad=0`.
- `ApplyInputAudioSupportCurrentRiskWave1179.java` final dry: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post exports: `6` metadata rows, `6` tag rows, `13` xref rows, `152` instruction rows, and `6` decompile rows.
- Queue/accounting after Wave1179: `6411` total functions, `6411` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, `721/1179 = 61.15%` current focused accounting, and `458` remaining active focused rows.
- Verified backup: `G:\GhidraBackups\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified`, `19` files, `176098183` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The six target function rows exist in the saved Ghidra project and match the saved names/signatures/comments.
- Wave1179 tags are present after read-back for all six target rows.
- Fresh xref, instruction, and decompile exports support a bounded static input/controller/audio support slice.
- The rows are now explicitly counted against the active Wave1108 current-risk denominator.

Consult note:

- Codex read-only consults were used. One consult proposed a future `CInfantryUnit` lifecycle/vfunc cluster, and one consult recommended splitting the Wave1179 slice to four frontend/input rows. Codex root final judgment kept the six-row bounded input/audio support slice after auditing the live metadata/tags/xrefs/decompile. No Cursor/Composer consults were used.

What remains unproven:

- Runtime input behavior, runtime controller/menu behavior, runtime audio/device-loss/sample-reader behavior, exact concrete input/controller/audio layouts, exact source-body identity, BEA patching behavior, visual/audio QA, gameplay outcomes, and rebuild parity.

Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference; actual no-noticeable-difference parity still requires later runtime, asset, visual, control, timing, save, patch, and rebuild proof.

Probe token anchor: Wave1179; wave1179-input-audio-support-current-risk-review; 721/1179 = 61.15%; 6 input/controller/audio support current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 458; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=6 skipped=0; tags_added=56; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consults used; Codex root final judgment; consult recommended four-row split; root kept six-row input/audio support slice; no Cursor/Composer; 0 / 0 / 0; 6411/6411 = 100.00%; 13 xref rows; 152 instruction rows; Input__UpdateCursorCenterWithWindowScale; Input__ResetMouseTransientState; GameControllers__RelinquishControlForTarget; Audio__ReinitializeSoundAndRestoreMusic; CWaveSoundRead__ScalarDeletingDestructor; CPCSoundManager__LoadSampleFromBuffer_StubFail; G:\GhidraBackups\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
