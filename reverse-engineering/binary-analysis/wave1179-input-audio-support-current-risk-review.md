# Wave1179 Input / Audio Support Current-Risk Review

Status: complete static tag-only normalization
Date: 2026-06-06
Scope: `wave1179-input-audio-support-current-risk-review`

Wave1179 accounts for `6 input/controller/audio support current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It performed tag-only normalization using `ApplyInputAudioSupportCurrentRiskWave1179.java`: no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation. Codex read-only consults were used for next-cluster and slice-shape sanity; one consult recommended a four-row frontend/input split, while Codex root kept the final six-row input/audio support slice after auditing the live metadata/tags/xrefs/decompile.

Current accounting after Wave1179:

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave911 focused | `812/1408 = 57.67%`, historical-retired/non-reconstructable |
| Wave911 top-500 risk-ranked | `500/500 = 100.00%` |
| Wave1108 current focused accounting | `721/1179 = 61.15%` |
| Current focused candidates | `1178` |
| Live regenerated current focused candidates | `1178` |
| Remaining active focused work | `458` |
| Current risk candidates | `6166` |

Fresh export evidence:

| Artifact | Rows |
| --- | ---: |
| Metadata | `6` |
| Tags | `6` |
| Xrefs | `13` |
| Function-body instructions | `152` |
| Decompile rows | `6` |

Ghidra tag-normalization evidence:

| Phase | Summary |
| --- | --- |
| Dry | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=56 missing=0 bad=0` |
| Apply | `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=56 missing=0 bad=0` |
| Final dry | `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |

Reviewed rows:

| Address | Saved name | Static read-back evidence |
| --- | --- | --- |
| `0x0042da00` | `Input__UpdateCursorCenterWithWindowScale` | Called by `CGame__InitRestartLoop` and `CGame__Update`; updates cached cursor-center/window-scale globals from platform window dimensions. |
| `0x00523db0` | `Input__ResetMouseTransientState` | Called by `PlatformInput__InitMouse`, `PlatformInput__ShutdownMouse`, `CFrontEnd__Process`, `CGame__MainLoop`, and raw callsites `0x0053f2dc` / `0x0053f306`; clears mouse click/cursor latches, wheel accumulator, and transient fields. |
| `0x004cdd70` | `GameControllers__RelinquishControlForTarget` | Called by `CMessageLog__HandleInputCommand` and raw close/back handler `0x0048ffcc`; loops controller slots and relinquishes matching control targets. |
| `0x004cddf0` | `Audio__ReinitializeSoundAndRestoreMusic` | `OptionsTail_Read` calls this after sound settings change; it reinitializes `CSoundManager` and restores frontend/current-level music. |
| `0x005054e0` | `CWaveSoundRead__ScalarDeletingDestructor` | DATA xref `0x005dfc4c`; wave-reader vtable slot 0 scalar-deleting destructor closes the reader and optionally frees `this`. |
| `0x00517290` | `CPCSoundManager__LoadSampleFromBuffer_StubFail` | `CSoundManager__CreateSample` calls the source-backed unimplemented PC buffer-load path; body returns null via `XOR EAX,EAX; RET 0x8`. |

Prior context:

- Wave480 corrected `Audio__ReinitializeSoundAndRestoreMusic`.
- Wave537 hardened `CWaveSoundRead__ScalarDeletingDestructor`.
- Wave567 corrected `Input__ResetMouseTransientState`.
- Wave853 hardened the PC sound backend tail and `CPCSoundManager__LoadSampleFromBuffer_StubFail`.
- Wave907 tied frontend/input/game-loop rows into a static-coherent system slice.
- Wave908 tied audio/media/cutscene rows into a static-coherent system slice.
- Wave1023 re-read `GameControllers__RelinquishControlForTarget` and `Audio__ReinitializeSoundAndRestoreMusic` read-only.

Backup:

`[maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified`

Backup verification: `19` files, `176098183` bytes, `DiffCount=0`, `HashDiffCount=0`.

Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference; actual no-noticeable-difference parity still requires later runtime, asset, visual, control, timing, save, patch, and rebuild proof.

What this proves:

- The six target function rows exist in the saved Ghidra database.
- Saved names/signatures/comments are stable under fresh metadata/decompile read-back.
- Wave1179 tags are present on all six target rows after apply/final-dry.
- The input/controller/audio support slice is now explicitly counted against the active Wave1108 current-risk denominator.

What remains separate proof:

- Runtime input behavior.
- Runtime controller/menu behavior.
- Runtime audio/device-loss/sample-reader behavior.
- Exact concrete input/controller/audio layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual/audio QA, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1179; wave1179-input-audio-support-current-risk-review; 721/1179 = 61.15%; 6 input/controller/audio support current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 458; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=6 skipped=0; tags_added=56; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consults used; Codex root final judgment; consult recommended four-row split; root kept six-row input/audio support slice; no Cursor/Composer; 0 / 0 / 0; 6411/6411 = 100.00%; 13 xref rows; 152 instruction rows; Input__UpdateCursorCenterWithWindowScale; Input__ResetMouseTransientState; GameControllers__RelinquishControlForTarget; Audio__ReinitializeSoundAndRestoreMusic; CWaveSoundRead__ScalarDeletingDestructor; CPCSoundManager__LoadSampleFromBuffer_StubFail; [maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
