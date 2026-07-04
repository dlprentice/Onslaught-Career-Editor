# Audio / Media / Cutscene / Camera Proof Plan

Status: active public-safe proof plan, not runtime proof
Last updated: 2026-06-08
Scope: `audio-media-cutscene-camera-proof-plan`

This plan is the next selected static-to-proof slice from `roadmap/static-to-proof-rebuild-transition-backlog.md` after the Save / Options Controller Byte-Preservation Proof Plan. It converts the saved audio, music, reader, FMV, cutscene, real-time cutscene, and camera static evidence into a bounded proof design for later copied-profile or app-owned media/cache work.

This plan does not launch BEA, mutate Ghidra, mutate the installed game, patch an executable, capture screenshots, transcode private media, start Godot work, play audio/video, or claim runtime DirectSound playback, runtime Ogg/WAV decode behavior, runtime Bink/FMV behavior, runtime music switching, runtime cutscene playback/sync, runtime camera switching, visual/audio QA, rebuild parity, or no-noticeable-difference parity.

The plan records static authorities, child proof lanes, copied-profile/media-cache guardrails, field/layout unknowns, and stop conditions before any executable proof work can start. The child-lane labels are audio sample lifecycle, reader framing, FMV/cache, cutscene sync, and camera behavior.

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

- `reverse-engineering/binary-analysis/audio-media-cutscene-static-review-2026-05-26.md`
- `reverse-engineering/binary-analysis/mapped-systems.md`
- `reverse-engineering/binary-analysis/functions/_index.md`
- `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`

Relevant retained evidence:

- Wave908 audio/media/cutscene static review (`audio-media-cutscene-static-review-wave908`): `171` function rows across `26` selected owner families after the loaded function-quality queue reached `6113/6113 = 100.00%`. It classified `CSoundManager`, `CPCSoundManager`, `CSample`, `CSoundEvent`, `CMusic`, `CWaveSoundRead`, `COggLoader`, `COggFileRead`, `OggVorbisStream`, `CBinkOpenThread`, `CDXFMV`, `CFMV`, `CCutscene`, `CRTCutscene`, `CMovieCamera`, `CPanCamera`, `CGenericCamera`, and `CCamera` rows as a static-coherent audio/media/cutscene/camera core. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-113941_post_wave908_audio_media_cutscene_static_review_verified`.
- Wave1015 Ogg/message lifecycle review (`ogg-message-lifecycle-review-wave1015`): read-only static read-back for `COggLoader__readerSubobject_dtor_body`, `COggLoader__ctor_base`, `COggLoader__ThreadProc_ReadPathIntoBuffer`, `COggLoader__readerSubobject_scalar_deleting_dtor`, `CMessage__ctor_base`, `CMessage__scalar_deleting_dtor`, and `CMessage__dtor_base`; it verified `7` metadata rows, `7` tag rows, `14` xref rows, `195` body-instruction rows, `7` decompile rows, and context exports for `COggFileRead`, `CWaitingThread`, `CMessageBox`, active-reader, pointer-set, and monitor lifecycle rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-192131_post_wave1015_ogg_message_lifecycle_review_verified`.
- Wave1179 input/audio support current-risk review (`wave1179-input-audio-support-current-risk-review`): retained the audio support rows `Audio__ReinitializeSoundAndRestoreMusic`, `CWaveSoundRead__ScalarDeletingDestructor`, and `CPCSoundManager__LoadSampleFromBuffer_StubFail` with `13 xref rows`, `152 instruction rows`, no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified`.
- Wave1219 final score16 current-risk review (`wave1219-final-score16-current-risk-review`): closed active current-risk accounting at `1179/1179 = 100.00%` and retained the final Ogg tail anchors `COggLoader__readerSubobject_dtor_body`, `COggLoader__ctor_base`, and `COggFileRead__scalar_deleting_dtor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Static Anchors

The proof plan is built around saved retail Ghidra evidence and public-safe static docs. Stuart source labels remain useful for class ownership and intent, but the loaded Steam retail binary remains authority for function names, call edges, and bounded comments.

| Surface | Static anchor |
| --- | --- |
| Sound manager core | `CSoundManager__Init`, `CSoundManager__CreateSample`, `CSoundManager__PlaySample`, `CSoundManager__FadeTo`, `CSoundManager__LoadCompressedSampleBank`, and sample/event lifetime rows. |
| PC DirectSound backend | `CPCSoundManager__CreateSampleFromData`, `CPCSoundManager__CreateSoundBuffer`, `CPCSoundManager__DecodeADPCM`, and `CPCSoundManager__LoadSampleFromBuffer_StubFail`. |
| Music switching | `CMusic__Init`, `CMusic__UpdateStatus`, and `Audio__ReinitializeSoundAndRestoreMusic`. |
| WAV reader | `CWaveSoundRead__Open` and `CWaveSoundRead__ScalarDeletingDestructor`. |
| Ogg reader | `COggLoader__ctor_base`, `COggLoader__ThreadProc_ReadPathIntoBuffer`, `COggLoader__readerSubobject_dtor_body`, `COggFileRead__ReadDecodedPcm`, `COggFileRead__scalar_deleting_dtor`, and `OggVorbisStream__ReadPcmSamples`. |
| FMV / Bink | `CBinkOpenThread__WorkerMain`, `CDXFMV__ctor_base`, `CDXFMV__VFunc_06_0053f180`, and `CFMV__PlayFullscreenWithLoadingGate`. |
| Cutscene runtime dataflow | `CCutscene__Load`, `CCutscene__Start`, `CCutscene__Update`, and `CCutscene__SetTrackSlotByFlag`. |
| Real-time cutscene render | `CRTCutscene__BuildCurrentFrameOutputs`. |
| Camera support | `CMovieCamera__GetPos`, `CMovieCamera__GetOrientation`, `CPanCamera__Update`, `CGenericCamera__GetPos`, and `CCamera__GetAspectRatio`. |
| Message/voice context | `CMessage__ctor_base`, `CMessage__dtor_base`, `CMessageBox__StartVoiceOrFallbackTextReveal`, and `CMessageBox__StopVoicePlaybackIfNotInCutscene` remain context anchors only. |

## Child Proof Lanes

Later executable work should select one child lane at a time. Do not combine audio playback, video playback, cutscene sync, and camera parity into one broad runtime slice.

| Row | Planned proof item | Required evidence | Public-safe result |
| --- | --- | --- |
| 1 | Static contract extraction | Produce a compact audio/media/camera static contract from Wave908, Wave1015, Wave1179, and Wave1219 anchors. | Function-family checklist, call-edge notes, field-role unknowns, and runtime gaps. |
| 2 | Copied-profile guard | Prepare a copied profile or app-owned artifact root before any future BEA launch, cache generation, patching, screenshot, frame, audio, or video output. | Sanitized artifact-root proof and no installed-game mutation. |
| 3 | Audio sample lifecycle probe design | Select one non-private sample path or synthetic app-owned fixture only after static sample-manager/backend anchors are checked. | Expected sample creation/play/fade/read events and explicit DirectSound runtime unknowns. |
| 4 | Ogg/WAV reader proof design | Select copied resource bytes or a sanitized fixture and verify reader framing without claiming playback. | Reader open/read/close accounting and raw-byte preservation notes. |
| 5 | FMV/Bink proof design | Select copied media/cache workflow only if private media boundaries and codec licensing/tooling boundaries are explicit. | Cache/transcode plan with no private media in public docs and no visible playback claim until captured. |
| 6 | Cutscene sync proof design | Select one cutscene sequence only after FMV/audio/camera dependencies are scoped. | Expected track-slot, update, and frame-output evidence checklist. |
| 7 | Camera behavior proof design | Select one camera mode, such as movie, pan, or generic camera, with explicit position/orientation/aspect anchors. | Expected position/orientation/aspect capture checklist and layout unknowns. |
| 8 | Stop conditions | Stop on private media leakage risk, ambiguous media identity, codec/tooling uncertainty, installed-game mutation need, broad runtime scope creep, unexpected file mutation, or mismatch outside the selected lane. | Documented blocked/deferred status instead of widening scope. |
| 9 | Rebuild handoff | Translate proven child-lane behavior into clean-room subsystem notes only after a later proof result identifies what was observed. | Static-to-runtime contract notes with exact runtime and layout gaps marked. |

## Copied-Profile And Media Guardrails

Any later proof execution must:

- Use a copied profile or app-owned artifact root for any generated outputs, screenshots, frames, caches, audio, video, logs, patches, or saves.
- Never mutate the installed Steam game directory or original executable.
- Keep private media and resource bytes out of public release scope.
- Keep public notes aggregate and sanitized.
- Select one child lane at a time and preserve static/runtime/rebuild claim boundaries.
- Record whether the input is copied retail data, a sanitized fixture, or generated app-owned data.
- Stop if the proof requires broad BEA runtime behavior before the static child lane is explicit.

## Not Claimed

This plan is a static-to-proof planning artifact only. It does not prove:

- Runtime DirectSound playback.
- Runtime Ogg/WAV decode behavior.
- Runtime Bink voice or FMV behavior.
- Runtime music switching.
- Runtime cutscene playback or sync.
- Runtime camera switching.
- Exact concrete `CSoundManager`, `CPCSoundManager`, `CSample`, `CSoundEvent`, Ogg/WAV reader, FMV, cutscene, real-time cutscene, or camera object layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual/audio QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Exit Gate For This Planning Slice

This planning slice is complete only when:

- This document and its lore-book mirror match.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `reverse-engineering/binary-analysis/_index.md`, and `reverse-engineering/RE-INDEX.md` point to this plan.
- `reverse-engineering/binary-analysis/audio-media-cutscene-static-review-2026-05-26.md` points from the Wave908 static review to this plan.
- `release/readiness/audio_media_cutscene_camera_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/audio_media_cutscene_camera_proof_plan_probe.py --check` passes.
- Static closeout probes still pass without changing `static-reaudit-progress.json` or `static-reaudit-current-risk-ledger.json`.
