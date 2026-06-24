# Audio / Media / Cutscene Static Review

Status: static-coherent system slice
Date: 2026-05-26
Scope: `audio-media-cutscene-static-review-wave908`

Wave908 reviews audio, music, Ogg/WAV readers, DirectSound backend rows, Bink/FMV helpers, cutscene playback rows, real-time cutscene render rows, and camera support after the loaded Ghidra function-quality queue reached `6113/6113 = 100.00%`. It ties `CSoundManager`, `CPCSoundManager`, sample/event lifetime rows, `CMusic`, `CWaveSoundRead`, `COggLoader`, `COggFileRead`, `OggVorbisStream`, `CBinkOpenThread`, `CDXFMV`, `CCutscene`, `CRTCutscene`, and camera families into one static classification.

Classification: `static-coherent audio/media/cutscene/camera core`.

Source/tool boundary: Stuart's source and AYAResourceExtractor remain useful architecture/name/logic/tooling evidence, but the authority for this review is the Steam retail binary as loaded in Ghidra plus current public-safe read-back docs. This review is not runtime audio, video, cutscene, or camera proof.

Transition planning note: [Audio / Media / Cutscene / Camera Proof Plan](audio-media-cutscene-camera-proof-plan.md) turns this Wave908 static-coherent surface plus Wave1015 Ogg/message lifecycle evidence, Wave1179 audio support current-risk evidence, and Wave1219 Ogg tail closure into copied-profile/app-owned proof lanes. The plan is not runtime proof and does not claim DirectSound playback, Ogg/WAV decode behavior, Bink/FMV behavior, music switching, cutscene sync, camera switching, visual/audio QA, patch behavior, rebuild parity, or no-noticeable-difference parity.

Wave1179 audio support update: Wave1179 (`wave1179-input-audio-support-current-risk-review`) accounts for `6 input/controller/audio support current-risk rows` with fresh Ghidra export evidence and tag-only normalization. In this audio/media slice, the directly relevant rows are `Audio__ReinitializeSoundAndRestoreMusic`, `CWaveSoundRead__ScalarDeletingDestructor`, and `CPCSoundManager__LoadSampleFromBuffer_StubFail`; the wave also ties back through `Input__UpdateCursorCenterWithWindowScale`, `Input__ResetMouseTransientState`, and `GameControllers__RelinquishControlForTarget` for options/menu input support. Apply/read-back used `ApplyInputAudioSupportCurrentRiskWave1179.java`: `updated=6 skipped=0`, `tags_added=56`, no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change. Codex read-only consults used; one consult recommended four-row split, while Codex root final judgment kept the six-row input/audio support slice. No Cursor/Composer was used. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; Wave1108 current focused accounting is `721/1179 = 61.15%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 458; current risk candidates: 6166; fresh exports verified `13 xref rows` and `152 instruction rows`. Verified backup: `G:\GhidraBackups\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified`. Runtime input behavior, runtime controller/menu behavior, runtime audio/device-loss/sample-reader behavior, exact concrete input/controller/audio layouts, exact source-body identity, BEA patching behavior, visual/audio QA, gameplay outcomes, and rebuild parity remain separate proof. Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference; actual no-noticeable-difference parity still requires later runtime, asset, visual, control, timing, save, patch, and rebuild proof. Probe token anchor: Wave1179; wave1179-input-audio-support-current-risk-review; 721/1179 = 61.15%; 6 input/controller/audio support current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 458; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=6 skipped=0; tags_added=56; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consults used; Codex root final judgment; consult recommended four-row split; root kept six-row input/audio support slice; no Cursor/Composer; 0 / 0 / 0; 6411/6411 = 100.00%; 13 xref rows; 152 instruction rows; Input__UpdateCursorCenterWithWindowScale; Input__ResetMouseTransientState; GameControllers__RelinquishControlForTarget; Audio__ReinitializeSoundAndRestoreMusic; CWaveSoundRead__ScalarDeletingDestructor; CPCSoundManager__LoadSampleFromBuffer_StubFail; G:\GhidraBackups\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Function-Family Surface

The Wave908 evidence snapshot covers `171` function rows across `26` selected owner families. Every selected row has a non-empty comment and a clean signature with no exact-`undefined` return and no `param_N` placeholders.

Cluster counts:

| Cluster | Rows |
| --- | ---: |
| Audio core | 36 |
| Audio readers | 28 |
| Cutscene | 27 |
| Camera | 31 |
| Audio backend | 24 |
| FMV / Bink | 14 |
| Music streaming | 11 |

Representative family counts:

| Family | Rows |
| --- | ---: |
| `CSoundManager` | 34 |
| `CPCSoundManager` | 20 |
| `CCutscene` | 14 |
| `CRTCutscene` | 12 |
| `CMusic` | 11 |
| `CWaveSoundRead` | 11 |
| `CMovieCamera` | 10 |
| `COggFileRead` | 9 |
| `CBinkOpenThread` | 9 |
| `CPanCamera` | 9 |
| `CDXFMV` | 4 |
| `CGenericCamera` | 4 |

Representative anchors include `CSoundManager__Init`, `CSoundManager__CreateSample`, `CSoundManager__PlaySample`, `CSoundManager__FadeTo`, `CSoundManager__LoadCompressedSampleBank`, `CPCSoundManager__CreateSampleFromData`, `CPCSoundManager__CreateSoundBuffer`, `CPCSoundManager__DecodeADPCM`, `CMusic__Init`, `CMusic__UpdateStatus`, `CWaveSoundRead__Open`, `COggLoader__ThreadProc_ReadPathIntoBuffer`, `OggVorbisStream__ReadPcmSamples`, `COggFileRead__ReadDecodedPcm`, `CBinkOpenThread__WorkerMain`, `CDXFMV__ctor_base`, `CDXFMV__VFunc_06_0053f180`, `CFMV__PlayFullscreenWithLoadingGate`, `CCutscene__Load`, `CCutscene__Start`, `CCutscene__Update`, `CCutscene__SetTrackSlotByFlag`, `CRTCutscene__BuildCurrentFrameOutputs`, `CMovieCamera__GetPos`, `CMovieCamera__GetOrientation`, `CPanCamera__Update`, `CGenericCamera__GetPos`, and `CCamera__GetAspectRatio`.

## Static Classification

- The selected audio/media/cutscene/camera owner families have no remaining function-quality queue debt.
- The current static documentation connects sound-manager sample/event lifecycle, PC DirectSound backend sample creation and ADPCM conversion, music playlist/status rows, WAV and Ogg reader paths, Bink/voice/FMVs, cutscene load/start/update/track-slot rows, real-time cutscene render frame outputs, and camera accessor/update helpers.
- The verified read-only Ghidra backup for this review is `G:\GhidraBackups\BEA_20260526-113941_post_wave908_audio_media_cutscene_static_review_verified`.

## What Remains Separate

- Exact concrete `CSoundManager`, `CPCSoundManager`, `CSample`, `CSoundEvent`, Ogg/WAV reader, FMV, cutscene, real-time cutscene, and camera object layouts.
- Runtime DirectSound playback, Ogg/WAV decode behavior, Bink voice/FMVs, music switching, cutscene playback/sync, camera switching, and visual/audio QA.
- BEA patch behavior.
- Clean-room rebuild parity.
