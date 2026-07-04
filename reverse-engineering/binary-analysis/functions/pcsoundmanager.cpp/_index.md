# pcsoundmanager.cpp - PC Sound Manager Implementation

**Source Path:** `[maintainer-local-source-export-root]\pcsoundmanager.cpp`
**Debug String:** `0x0063e46c`
**Functions Found:** 20+ static backend/sample rows across Wave562 and Wave853 evidence

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

PC-specific sound manager implementation that wraps DirectSound for the Windows platform. This class (`CPCSoundManager`) handles DirectSound initialization, sound device enumeration, audio buffer creation, and audio format conversion including IMA ADPCM decoding.

Wave853 SoundManager backend tail (`soundmanager-backend-tail-wave853`, `wave853-readback-verified`) corrected and hardened the adjacent PC audio backend tail. It established `0x005168d0 CPCSample__dtor` and `0x00516960 CPCSample__scalar_deleting_dtor` as CPCSample lifetime rows, not CPCSoundManager destructors, then corrected stale CSoundManager labels to source-backed CPCSoundManager backend helpers including `0x005171e0 CPCSoundManager__DeviceShutdown`, `0x00517260 CPCSoundManager__DeviceReset`, `0x00517290 CPCSoundManager__LoadSampleFromBuffer_StubFail`, `0x00517790 CPCSoundManager__PlaySound`, `0x00517960 CPCSoundManager__UnPauseSound`, `0x00517990 CPCSoundManager__PauseSound`, `0x005179b0 CPCSoundManager__StopSound`, `0x00517a20 CPCSoundManager__UpdateGlobals`, `0x00517ae0 CPCSoundManager__UpdateSound`, `0x00517c40 CPCSoundManager__UpdatesDone`, `0x00517c60 CPCSoundManager__GetSampleLength`, and `0x00517cb0 CPCSoundManager__FindFreeChannel`. It also hardened device enumeration helpers at `0x00516980` and `0x00516990`. Post-Wave853 queue telemetry is `5754/6098 = 94.36%`, with next raw commentless row `0x0051a6a0 CFastVB__RenderIndexedImmediate`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260525-101054_post_wave853_soundmanager_backend_tail_verified`. Runtime DirectSound playback, pause/unpause, shutdown/reset, listener/channel allocation behavior, exact backend/sample/event layouts, BEA patching, and rebuild parity remain deferred.

Wave908 audio/media/cutscene static review (`audio-media-cutscene-static-review-wave908`) re-audits the PC backend as part of the static-coherent audio/media/cutscene/camera core. The read-only evidence keeps `CPCSoundManager 20` with adjacent `CSample`/`CPCSample`/`CSoundManager` rows inside the `171` selected-row, `26` family slice. Anchors include `CPCSoundManager__CreateSampleFromData`, `CPCSoundManager__CreateSoundBuffer`, `CPCSoundManager__DecodeADPCM`, `CPCSoundManager__PlaySound`, `CPCSoundManager__UpdateSound`, and `CPCSoundManager__FindFreeChannel`, tying Bink voice/sample creation, DirectSound buffer setup, ADPCM decode tables, and event-channel updates into the audio core. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-113941_post_wave908_audio_media_cutscene_static_review_verified`. This remains static retail Ghidra evidence; runtime DirectSound playback/mixing, exact COM/layout identity, source-body identity, patch behavior, and rebuild parity remain separate.

Wave1179 (`wave1179-input-audio-support-current-risk-review`) re-read and tag-normalized `CPCSoundManager__LoadSampleFromBuffer_StubFail` inside a `6 input/controller/audio support current-risk rows` slice. Fresh Ghidra export evidence verified `13 xref rows` and `152 instruction rows` across the slice; this row is called by `CSoundManager__CreateSample` and remains the PC source-backed unimplemented buffer-load stub returning null. The same slice also covers `Input__UpdateCursorCenterWithWindowScale`, `Input__ResetMouseTransientState`, `GameControllers__RelinquishControlForTarget`, `Audio__ReinitializeSoundAndRestoreMusic`, and `CWaveSoundRead__ScalarDeletingDestructor`. Apply/read-back used `ApplyInputAudioSupportCurrentRiskWave1179.java`: `updated=6 skipped=0`, `tags_added=56`, no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change. Codex read-only consults used; one consult recommended four-row split, while Codex root final judgment kept the six-row input/audio support slice. No Cursor/Composer was used. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; Wave1108 current focused accounting is `721/1179 = 61.15%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 458; current risk candidates: 6166; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified`. Runtime input behavior, runtime controller/menu behavior, runtime audio/device-loss/sample-reader behavior, exact concrete input/controller/audio layouts, exact source-body identity, BEA patching behavior, visual/audio QA, gameplay outcomes, and rebuild parity remain separate proof. Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference. Probe token anchor: Wave1179; wave1179-input-audio-support-current-risk-review; 721/1179 = 61.15%; 6 input/controller/audio support current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 458; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=6 skipped=0; tags_added=56; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consults used; Codex root final judgment; consult recommended four-row split; root kept six-row input/audio support slice; no Cursor/Composer; 0 / 0 / 0; 6411/6411 = 100.00%; 13 xref rows; 152 instruction rows; Input__UpdateCursorCenterWithWindowScale; Input__ResetMouseTransientState; GameControllers__RelinquishControlForTarget; Audio__ReinitializeSoundAndRestoreMusic; CWaveSoundRead__ScalarDeletingDestructor; CPCSoundManager__LoadSampleFromBuffer_StubFail; [maintainer-local-ghidra-backup-root]\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified; wave1108-current-risk-rank.

## Class: CPCSoundManager

The CPCSoundManager class provides the Windows-specific implementation of the game's sound system using DirectSound8.

### Class Layout (Partial)

| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| 0x00BC | int | m_3DSoundMethod | 3D sound algorithm selection |
| 0x00C0 | IDirectSound8* | m_pDirectSound | Main DirectSound interface |
| 0x00C4 | void*[64] | m_soundBuffers | Array of sound buffer pointers |
| 0x02C4 | IDirectSound3DListener* | m_pListener | 3D audio listener interface |
| 0x02C8 | CWaveSoundRead* | m_pWaveReader | WAV file reader object |
| 0x02CC | int | m_numVoices | Number of sound voices (max 64) |

## Functions

## Wave 853 SoundManager Backend Tail Note (2026-05-25)

Wave853 saved the following important PC backend and sample lifetime rows in Ghidra:

| Address | Current saved Ghidra state | Notes |
| --- | --- | --- |
| `0x005168d0` | `void __fastcall CPCSample__dtor(void * this)` | Corrects stale `CPCSoundManager__dtor`; frees sample data at `this+0x78`, releases DirectSound buffer at `this+0x80`, and chains to `CSample__DestructorBody`. |
| `0x00516960` | `void * __thiscall CPCSample__scalar_deleting_dtor(void * this, uchar free_flag)` | CPCSample vtable slot 0 at `0x005e4988`; calls `CPCSample__dtor` and conditionally frees `this`. |
| `0x005171e0` | `void __fastcall CPCSoundManager__DeviceShutdown(void * this)` | Releases DS3D buffers, DirectSound buffers, DirectSound object, and wave-reader/helper. |
| `0x00517260` | `void __fastcall CPCSoundManager__DeviceReset(void * this)` | Stops non-null DirectSound buffers without releasing them. |
| `0x00517290` | `void * __stdcall CPCSoundManager__LoadSampleFromBuffer_StubFail(void * mem_buffer, int music)` | Unimplemented PC buffer-load path: `XOR EAX,EAX; RET 0x8`. |
| `0x00517790` | `void __thiscall CPCSoundManager__PlaySound(void * this, void * sound_event)` | Duplicates sample buffer into an event channel, queries DS3D, updates position/params, seeks, starts playback, and marks the event playing. |
| `0x00517960` / `0x00517990` / `0x005179b0` | `CPCSoundManager__UnPauseSound`, `CPCSoundManager__PauseSound`, `CPCSoundManager__StopSound` | Source-backed pause/unpause/stop-and-release channel helpers. |
| `0x00517a20` / `0x00517c40` | `CPCSoundManager__UpdateGlobals`, `CPCSoundManager__UpdatesDone` | DirectSound3D listener update and deferred commit helpers. |
| `0x00517ae0` | `void __thiscall CPCSoundManager__UpdateSound(void * this, void * sound_event, int first_time)` | Updates DS3D position/velocity, volume, frequency, and completion state for an event channel. |
| `0x00517c60` / `0x00517cb0` | `CPCSoundManager__GetSampleLength`, `CPCSoundManager__FindFreeChannel` | Sample duration and channel allocation helpers over active events and DirectSound buffer slots. |

This is static retail/source-reference evidence only. Runtime DirectSound behavior, concrete backend/sample/event layouts, exact COM interface identity, BEA patching, and rebuild parity remain unproven.

## Wave 562 PC Sound Signature Note (2026-05-18)

Wave562 saved the current Ghidra signatures/comments/tags for all six CPCSoundManager backend functions in this file:

| Address | Current saved Ghidra state | Notes |
| --- | --- | --- |
| `0x005169b0` | `bool __thiscall CPCSoundManager__Init(void * this)` | DirectSound device enumeration/init, caps, voice-count selection, primary-buffer format setup, and listener query. |
| `0x005172a0` | `void * __stdcall CPCSoundManager__CreateSampleFromFile(void * sample_source, int channel_type, void * reusable_sample)` | `RET 0x0c` proves three stack arguments; reads compressed data, creates/refreshes a sample, decodes ADPCM, converts quality-dependent output, and fills a DirectSound buffer. |
| `0x00517440` | `void * __cdecl CPCSoundManager__CreateSoundBuffer(void * out_ds_buffer, uint source_byte_count)` | Builds the PCM format/buffer descriptor, creates a secondary DirectSound buffer, locks it, and returns the write pointer or null. |
| `0x00517600` | `void __cdecl CPCSoundManager__ConvertAudioFormat(void * destination, short * source_pcm16, uint source_byte_count)` | Quality-dependent PCM copy/downsample/8-bit conversion helper. |
| `0x005176d0` | `void * __stdcall CPCSoundManager__CreateSampleFromData(void * pcm_data, uint byte_count, int unused_arg, void * reusable_sample)` | `RET 0x10` proves four stack arguments; called from the Bink voice sample queue and preserves the third argument as unused in retail. |
| `0x00517fa0` | `void __cdecl CPCSoundManager__DecodeADPCM(char * source_adpcm, short * destination_pcm16, uint sample_count, short * decoder_state)` | IMA ADPCM decoder over tables `0x0063e85c` and `0x0063e89c`, updating predictor/step-index state. |

This is static retail Ghidra evidence only. Runtime DirectSound behavior, sample playback, Bink voice playback, ADPCM decode quality, exact CPCSoundManager/CPCSample layouts, BEA launch behavior, patching, and rebuild parity remain unproven.

### CPCSoundManager__Init
| Property | Value |
|----------|-------|
| Address | `0x005169b0` |
| Returns | `BOOL` (1=success, 0=failure) |
| Calling Convention | thiscall (ECX=this) |

**Purpose:** Initializes the DirectSound subsystem for the game.

**Behavior:**
1. Sets default voice count to 12
2. Creates CWaveSoundRead helper object for WAV file parsing
3. Clears sound buffer array (64 slots)
4. Enumerates sound devices via `DirectSoundEnumerateA`
5. Creates DirectSound8 device via `DirectSoundCreate8`
6. Sets cooperative level (DSSCL_PRIORITY)
7. Queries device capabilities (DSCAPS)
8. Checks for DSCAPS_CONTINUOUSRATE support
9. Configures 3D sound method (0, 1, or 2)
10. Determines voice count based on device caps (max 64)
11. Creates primary sound buffer with 3D capability
12. Sets primary buffer format (44.1kHz/22kHz/11kHz based on quality setting)
13. Obtains IDirectSound3DListener interface

**Global Variables Referenced:**
- `DAT_00896ca0` - Sound device count
- `g_SoundDeviceIndex` - Selected sound device index
- `g_SoundSampleRateIndex` - Sound quality setting (0=high, 1=medium, else low)
- `g_Sound3DMethod` - 3D sound method override (-1=auto)
- `DAT_00663088` - Voice count override (-1=auto)
- `g_SoundEnabledFlag` - Sound enabled flag (controls DAT_00896c58)
- `DAT_008964d0` - Device has continuous rate capability
- `DAT_00888a44` - Main window HWND (for SetCooperativeLevel)

**Sample Rates by Quality:**
- Quality 0 (High): 44100 Hz (0xAC44)
- Quality 1 (Medium): 22050 Hz (0x5622)
- Quality 2 (Low): 11025 Hz (0x2B11)

---

### CPCSoundManager__CreateSampleFromFile
| Property | Value |
|----------|-------|
| Address | `0x005172a0` |
| Returns | `CSample*` (sound sample object or NULL) |
| Calling Convention | cdecl |

**Purpose:** Creates a sound sample by loading and decoding audio data from a file.

**Parameters:**
- `param_1` - Unknown (possibly file handle)
- `param_2` - Unknown (possibly format info)
- `param_3` - Existing sample to reuse (or NULL to create new)

**Behavior:**
1. Reads 4-byte size header from file
2. Allocates or reuses CSample object (0x84 bytes)
3. Allocates temporary buffer for compressed audio
4. Reads compressed audio data
5. Creates DirectSound buffer via CreateSoundBuffer helper
6. Decodes audio based on quality setting:
   - Quality 0: Direct copy (16-bit stereo)
   - Quality 1+: Allocates temp buffer, decodes ADPCM, converts format
7. Locks buffer and copies decoded audio data
8. Returns sample object

---

### CPCSoundManager__CreateSampleFromData
| Property | Value |
|----------|-------|
| Address | `0x005176d0` |
| Returns | `CSample*` (sound sample object or NULL) |
| Calling Convention | cdecl |

**Purpose:** Creates a sound sample from raw PCM data already in memory.

**Parameters:**
- `param_1` - Pointer to raw audio data
- `param_2` - Size of audio data in bytes
- `param_3` - Unknown
- `param_4` - Existing sample to reuse (or NULL to create new)

**Behavior:**
1. Allocates or reuses CSample object (0x84 bytes)
2. Creates DirectSound buffer via CreateSoundBuffer helper
3. Converts audio format via ConvertAudioFormat
4. Locks buffer and copies converted audio data
5. Returns sample object

---

### CPCSoundManager__CreateSoundBuffer
| Property | Value |
|----------|-------|
| Address | `0x00517440` |
| Returns | `int` (bytes per sample, or 0 on failure) |
| Calling Convention | cdecl |

**Purpose:** Creates a DirectSound secondary buffer for a sound sample.

**Parameters:**
- `param_1` - Output pointer for IDirectSoundBuffer8*
- `param_2` - Buffer size in samples

**Behavior:**
1. Sets up WAVEFORMATEX structure based on quality setting
2. Configures DSBUFFERDESC with appropriate flags:
   - DSBCAPS_CTRLVOLUME
   - DSBCAPS_CTRLPAN
   - DSBCAPS_CTRLFREQUENCY
   - DSBCAPS_CTRL3D (if 3D sound enabled)
3. Sets 3D algorithm GUID based on DAT_00896a44 setting
4. Adjusts buffer size based on quality (downsampling)
5. Calls IDirectSound8::CreateSoundBuffer
6. Locks buffer for writing
7. Returns bytes per sample

**3D Algorithm Selection:**
- Setting 0: DS3DALG_DEFAULT (0xC2413340)
- Setting 1: DS3DALG_NO_VIRTUALIZATION (0xC2413342)
- Setting 2: DS3DALG_HRTF_FULL (0xC241333F)

---

### CPCSoundManager__ConvertAudioFormat
| Property | Value |
|----------|-------|
| Address | `0x00517600` |
| Returns | `void` |
| Calling Convention | cdecl |

**Purpose:** Converts audio data between formats based on quality setting (downsampling/bit-depth conversion).

**Parameters:**
- `param_1` - Destination buffer
- `param_2` - Source buffer (16-bit samples)
- `param_3` - Number of bytes to process

**Behavior by Quality Setting:**
- **Quality 0 (High):** Direct memcpy (16-bit stereo passthrough)
- **Quality 1 (Medium):** Downsamples 2:1, averages stereo pairs to mono 16-bit
- **Quality 2 (Low):** Downsamples 4:1, averages 4 samples, converts to 8-bit unsigned

---

### CPCSoundManager__DecodeADPCM
| Property | Value |
|----------|-------|
| Address | `0x00517fa0` |
| Returns | `void` |
| Calling Convention | cdecl |

**Purpose:** Decodes IMA ADPCM compressed audio to 16-bit PCM.

**Parameters:**
- `param_1` - Source ADPCM data (4-bit nibbles)
- `param_2` - Destination buffer (16-bit samples)
- `param_3` - Number of samples to decode
- `param_4` - Decoder state (predictor + step index)

**Algorithm:** Standard IMA ADPCM decoding:
1. Uses step table at `DAT_0063e89c` (89 entries)
2. Uses index table at `DAT_0063e85c` (16 entries)
3. Processes nibbles alternately (high then low)
4. Clamps output to [-32768, 32767]
5. Updates decoder state for streaming

## Global Data

| Address | Type | Name | Purpose |
|---------|------|------|---------|
| 0x00663074 | int | g_soundFlag | Unknown sound configuration flag |
| 0x00663078 | int | g_selectedDevice | Selected sound device index |
| 0x00663080 | int | g_soundQuality | Sound quality (0=high, 1=med, 2=low) |
| 0x00663084 | int | g_3DSoundMethod | 3D sound method override |
| 0x00663088 | int | g_voiceCountOverride | Voice count override |
| 0x008964d0 | bool | g_hasContinuousRate | Device supports continuous rate |
| 0x00896a44 | int | g_3DAlgorithm | Current 3D algorithm setting |
| 0x00896a48 | IDirectSound8* | g_pDirectSound | Global DirectSound pointer |
| 0x00896ca0 | int | g_deviceCount | Enumerated sound device count |
| 0x0063e85c | int[16] | g_adpcmIndexTable | ADPCM index adjustment table |
| 0x0063e89c | int[89] | g_adpcmStepTable | ADPCM step size table |

## Related Classes

- **CWaveSoundRead** - WAV file parser helper class (constructor at referenced location)
- **CSample** - Sound sample object (0x84 bytes, vtable at 0x005e4988)

## Notes

1. The PC port supports three quality levels that affect sample rate and bit depth
2. ADPCM decoding is used for compressed game audio assets
3. 3D positional audio is supported via DirectSound3D
4. Maximum of 64 simultaneous sound voices
5. The Unwind function at `0x005d67d0` is an exception handler, not a regular method
