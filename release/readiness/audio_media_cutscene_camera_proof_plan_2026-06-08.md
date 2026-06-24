# Audio / Media / Cutscene / Camera Proof Plan Readiness Note

Status: proof plan complete, not runtime proof
Date: 2026-06-08
Scope: `audio-media-cutscene-camera-proof-plan`

This readiness note records a public-safe static-to-proof planning slice for the audio/media/cutscene/camera surface. It is not a new static re-audit wave, not a runtime test, not a screenshot/capture proof, not a DirectSound playback proof, not an Ogg/WAV decode proof, not a Bink/FMV playback proof, not a BEA patch, not a Godot slice, and not a rebuild parity claim.

Primary static source: `audio-media-cutscene-static-review-2026-05-26.md`. The plan records static authorities, child proof lanes, copied-profile/media-cache guardrails, field/layout unknowns, and stop conditions before any executable proof work can start.

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.

Static source evidence:

- Wave908 (`audio-media-cutscene-static-review-wave908`): `171` function rows across `26` selected owner families, including `CSoundManager`, `CPCSoundManager`, `CMusic`, `CWaveSoundRead`, `COggLoader`, `COggFileRead`, `OggVorbisStream`, `CBinkOpenThread`, `CDXFMV`, `CFMV`, `CCutscene`, `CRTCutscene`, `CMovieCamera`, `CPanCamera`, `CGenericCamera`, and `CCamera`. Verified backup: `G:\GhidraBackups\BEA_20260526-113941_post_wave908_audio_media_cutscene_static_review_verified`.
- Wave1015 (`ogg-message-lifecycle-review-wave1015`): retained Ogg loader and queued-message lifecycle read-back for `COggLoader__readerSubobject_dtor_body`, `COggLoader__ctor_base`, `COggLoader__ThreadProc_ReadPathIntoBuffer`, `COggLoader__readerSubobject_scalar_deleting_dtor`, `CMessage__ctor_base`, `CMessage__scalar_deleting_dtor`, and `CMessage__dtor_base`. Verified backup: `G:\GhidraBackups\BEA_20260531-192131_post_wave1015_ogg_message_lifecycle_review_verified`.
- Wave1179 (`wave1179-input-audio-support-current-risk-review`): retained audio support rows `Audio__ReinitializeSoundAndRestoreMusic`, `CWaveSoundRead__ScalarDeletingDestructor`, and `CPCSoundManager__LoadSampleFromBuffer_StubFail` with no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change. Verified backup: `G:\GhidraBackups\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified`.
- Wave1219 (`wave1219-final-score16-current-risk-review`): closed active current-risk accounting at `1179/1179 = 100.00%` and retained final Ogg tail anchors `COggLoader__readerSubobject_dtor_body`, `COggLoader__ctor_base`, and `COggFileRead__scalar_deleting_dtor`. Verified backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Representative anchors:

| Surface | Static anchor |
| --- | --- |
| Sound manager core | `CSoundManager__Init`, `CSoundManager__CreateSample`, `CSoundManager__PlaySample`, `CSoundManager__FadeTo`, `CSoundManager__LoadCompressedSampleBank` |
| PC DirectSound backend | `CPCSoundManager__CreateSampleFromData`, `CPCSoundManager__CreateSoundBuffer`, `CPCSoundManager__DecodeADPCM`, `CPCSoundManager__LoadSampleFromBuffer_StubFail` |
| Music switching | `CMusic__Init`, `CMusic__UpdateStatus`, `Audio__ReinitializeSoundAndRestoreMusic` |
| WAV/Ogg readers | `CWaveSoundRead__Open`, `CWaveSoundRead__ScalarDeletingDestructor`, `COggLoader__ThreadProc_ReadPathIntoBuffer`, `COggFileRead__ReadDecodedPcm`, `COggFileRead__scalar_deleting_dtor`, `OggVorbisStream__ReadPcmSamples` |
| FMV/Bink | `CBinkOpenThread__WorkerMain`, `CDXFMV__ctor_base`, `CDXFMV__VFunc_06_0053f180`, `CFMV__PlayFullscreenWithLoadingGate` |
| Cutscene | `CCutscene__Load`, `CCutscene__Start`, `CCutscene__Update`, `CCutscene__SetTrackSlotByFlag`, `CRTCutscene__BuildCurrentFrameOutputs` |
| Camera | `CMovieCamera__GetPos`, `CMovieCamera__GetOrientation`, `CPanCamera__Update`, `CGenericCamera__GetPos`, `CCamera__GetAspectRatio` |

Proof-plan boundaries:

- The plan is limited to future copied-profile or app-owned artifact-root work.
- Any future proof must select one child lane at a time: audio sample lifecycle, reader framing, FMV/cache, cutscene sync, or camera behavior.
- Any future proof must keep private media and resource bytes out of public release scope.
- Any future proof must record whether inputs are copied retail data, sanitized fixtures, or generated app-owned data.
- Any future proof must stop on private media leakage risk, ambiguous media identity, codec/tooling uncertainty, installed-game mutation need, broad runtime scope creep, unexpected file mutation, or mismatch outside the selected lane.
- Stop on private media leakage risk is an explicit gate, not a warning to handle later.
- The plan explicitly does not include runtime DirectSound playback, runtime Ogg/WAV decode behavior, runtime Bink/FMV behavior, runtime music switching, runtime cutscene playback/sync, runtime camera switching, visual/audio QA, patch behavior, rebuild parity, or no-noticeable-difference parity.

No runtime DirectSound playback, runtime Ogg/WAV decode behavior, runtime Bink/FMV behavior, runtime music switching, runtime cutscene playback/sync, runtime camera switching, exact concrete layouts, exact source-body identity, BEA patching behavior, visual/audio QA, Godot parity, rebuild parity, or no-noticeable-difference parity claim is made.
