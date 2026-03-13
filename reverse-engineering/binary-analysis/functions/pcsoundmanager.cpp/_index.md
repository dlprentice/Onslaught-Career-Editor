# pcsoundmanager.cpp - PC Sound Manager Implementation

**Source Path:** `C:\dev\ONSLAUGHT2\pcsoundmanager.cpp`
**Debug String:** `0x0063e46c`
**Functions Found:** 6 (3 confirmed via debug path, 3 helper functions)

## Overview

PC-specific sound manager implementation that wraps DirectSound for the Windows platform. This class (`CPCSoundManager`) handles DirectSound initialization, sound device enumeration, audio buffer creation, and audio format conversion including IMA ADPCM decoding.

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
