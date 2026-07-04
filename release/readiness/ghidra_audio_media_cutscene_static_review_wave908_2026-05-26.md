# Ghidra Audio / Media / Cutscene Static Review Wave908 Readiness Note

Status: complete static review evidence
Date: 2026-05-26
Scope: `audio-media-cutscene-static-review-wave908`

Wave908 is a read-only post-100 system review. It makes no Ghidra metadata mutation, no executable-byte change, no save mutation, and no BEA launch. The wave records a `static-coherent audio/media/cutscene/camera core` after the loaded Ghidra function-quality queue reached `6113/6113 = 100.00%`.

Evidence summary:

- Selected function rows: `171` rows across `26` families, all commented and clean-signature.
- Cluster counts: audio core `36`, audio readers `28`, cutscene `27`, camera `31`, audio backend `24`, FMV / Bink `14`, music streaming `11`.
- Large family anchors: `CSoundManager` `34`, `CPCSoundManager` `20`, `CCutscene` `14`, `CRTCutscene` `12`, `CMusic` `11`, `CWaveSoundRead` `11`, `CMovieCamera` `10`, `COggFileRead` `9`, `CBinkOpenThread` `9`, `CPanCamera` `9`, `CDXFMV` `4`, and `CGenericCamera` `4`.
- Representative functions: `CSoundManager__Init`, `CSoundManager__CreateSample`, `CSoundManager__PlaySample`, `CSoundManager__FadeTo`, `CSoundManager__LoadCompressedSampleBank`, `CPCSoundManager__CreateSampleFromData`, `CPCSoundManager__CreateSoundBuffer`, `CPCSoundManager__DecodeADPCM`, `CMusic__Init`, `CMusic__UpdateStatus`, `CWaveSoundRead__Open`, `COggLoader__ThreadProc_ReadPathIntoBuffer`, `OggVorbisStream__ReadPcmSamples`, `COggFileRead__ReadDecodedPcm`, `CBinkOpenThread__WorkerMain`, `CDXFMV__ctor_base`, `CDXFMV__VFunc_06_0053f180`, `CFMV__PlayFullscreenWithLoadingGate`, `CCutscene__Load`, `CCutscene__Start`, `CCutscene__Update`, `CCutscene__SetTrackSlotByFlag`, `CRTCutscene__BuildCurrentFrameOutputs`, `CMovieCamera__GetPos`, `CMovieCamera__GetOrientation`, `CPanCamera__Update`, `CGenericCamera__GetPos`, and `CCamera__GetAspectRatio`.
- Verified read-only Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-113941_post_wave908_audio_media_cutscene_static_review_verified`, `19` files, `173247367` bytes, `DiffCount=0`.

What this proves:

- The selected audio/media/cutscene/camera owner-family rows are closed under the current function-quality proxy.
- The public docs now review sound-manager sample/event lifecycle, PC DirectSound backend sample creation and ADPCM conversion, music playlist/status rows, WAV and Ogg reader paths, Bink/voice/FMVs, cutscene load/start/update/track-slot rows, real-time cutscene render frame outputs, and camera accessor/update helpers as one static system slice.
- The claim is static coherence, not runtime audio/video/cutscene/camera behavior or visual/audio QA.

What remains unproven:

- Exact concrete object layouts.
- Runtime DirectSound playback, Ogg/WAV decode behavior, Bink voice/FMVs, music switching, cutscene playback/sync, camera switching, and visual/audio QA.
- BEA patch behavior.
- Clean-room rebuild parity.
