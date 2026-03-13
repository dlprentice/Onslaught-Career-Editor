# SoundManager.cpp Functions

> Source File: SoundManager.cpp | Binary: BEA.exe
> Debug Path: 0x00632428

## Overview

Audio system implementation. CSoundManager handles sound playback, 3D audio positioning, streaming, and volume control with DirectSound backend.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004e00d0 | CSoundManager__Init (TODO) | Initialize sound system | ~500 bytes |
| 0x004e2530 | CSoundManager__LoadSoundDefinitions (TODO) | Parse sounds.sfx file | ~600 bytes |

## Related Functions (No Debug Ref)

| Address | Name | Purpose |
|---------|------|---------|
| 0x004e0300 | CSoundManager__UpdateAllSoundVolumes | Distance-based attenuation |
| 0x004e04c0 | CSoundManager__SetMasterVolume | Set master volume |
| 0x004e06b0 | CSoundManager__StopAllStreams | Stop all streaming sounds |
| 0x004e06e0 | CSoundManager__Shutdown | Full cleanup |
| 0x004e0820 | CSoundDefinition__Destructor | Removes definition from global list; optionally frees |
| 0x004e0890 | CSoundManager__CreateSample | Create sound from file |
| 0x004e0a00 | CSoundManager__GetOrCreateSample | Find-or-create sample (optionally reload if already present) |
| 0x004e0a90 | CSoundManager__PlayNamedSample | Lookup by name then play (wrapper around PlaySample/core playback path) |
| 0x004e0b30 | CSoundManager__PlaySample | Playback wrapper (once-only suppression + event launch) |
| 0x004e0bd0 | CSoundManager__PlaySound | Main playback function |
| 0x004e0f70 | CSoundManager__StopSoundEvent | Stop/cleanup one event (callback + channel release + reader clear) |
| 0x004e1040 | CSoundManager__SortEventList | Priority sort + channel allocation/release pass |
| 0x004e1130 | CSoundManager__KillSamplesForThing | Stop all active events owned by one thing |
| 0x004e1190 | CSoundManager__KillSample | Stop active events matching owner + sample pair |
| 0x004e12b0 | CSoundManager__KillAllSamples | Stop all active events |
| 0x004e1300 | CSoundManager__PauseAllSamples | Pause all active events/channels |
| 0x004e1330 | CSoundManager__UnPauseAllSamples | Unpause active events/channels |
| 0x004e1360 | CSoundManager__UpdateSoundPosition | Recompute event position/pan/attenuation from camera and tracking mode |
| 0x004e18d0 | CSoundManager__SetPitch | Set desired pitch multiplier + fade-time ticks on an event |
| 0x004e0fb0 | CSoundManager__AllocateSoundEvent | Get free event from pool |
| 0x004e1b20 | [CSoundManager__UpdateStatus](./CSoundManager__UpdateStatus.md) | Per-frame sound-event update (camera state, attenuation, fades, cleanup) |
| 0x004e2360 | CSoundManager__GetDebugMenuText | Build debug text line for nth active sound event |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d4bf0 | Unwind@005d4bf0 | 90 | Cleanup for Init allocation |

## Key Observations

- **256 sound event slots** - Pre-allocated pool
- **3D attenuation** - 50-meter max range
- **Console variables** - Debug controls
- **Dual path system** - "sounds\\" and "music\\" directories
- **DirectSound units** - Volume in hundredths of dB

## Console Variables

| CVar | Description | Default |
|------|-------------|---------|
| snd_frozen | Are sounds frozen? | 0 |
| snd_visible | Are sounds visible? | 0 |
| snd_radiomessagevolume | Radio message volume | 0.42 |
| snd_hudmessagevolume | HUD message volume | 0.45 |

## Console Commands

| Command | Description |
|---------|-------------|
| playsound | Play the named sample or stream |

## Sound Event Structure (136 bytes / 0x88)

| Offset | Field | Notes |
|--------|-------|-------|
| 0x04 | mSoundHandle | Handle |
| 0x08 | mIsPlaying | Playing flag |
| 0x10 | mIs3D | 3D positioning |
| 0x14 | mChannelType | 1=sound, else=music |
| 0x18 | mIsLooping | Loop flag |
| 0x1C | mBaseVolume | Base volume |
| 0x44-0x4C | mPosition | x,y,z position |
| 0x74 | mNext | Linked list |
| 0x78 | mPrev | Linked list |

## Sound Definition Structure (220 bytes / 0xDC)

| Offset | Size | Field |
|--------|------|-------|
| 0x00 | 64 | mName |
| 0x40 | 64 | mFilePath |
| 0x80 | 64 | mAltPath |
| 0xD4 | 4 | mDuplicateNext |
| 0xD8 | 4 | mNext |

## Key Globals

| Address | Name | Purpose |
|---------|------|---------|
| 0x0083cfe8 | g_pSoundDefinitionListHead | Head of linked list of sound definitions (0xDC-byte nodes) |

## Related Files

- Music.cpp - Music playback
- engine.cpp - Engine initialization

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
