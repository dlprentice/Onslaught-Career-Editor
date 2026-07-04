# Music.cpp

> Music/audio playback system functions from BEA.exe

**Source file**: `Music.cpp`
**Debug path**: `[maintainer-local-source-export-root]\Music.cpp` (at 0x00630a4c)
**Class**: `CMusic` (RTTI: `.?AVCMusic@@` at 0x0063dfc8)
**Related classes**: `CPCMusic` (RTTI: `.?AVCPCMusic@@` at 0x0063dfe0)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

The CMusic class manages background music playback in Battle Engine Aquila. Wave454 saved retail Ghidra names, signatures, comments, and tags for the contiguous `CMusic` cluster at `0x004bb380-0x004bba10`. Stuart's source is useful name/logic evidence, but the retail binary remains authority; runtime audio playback, exact class layouts, and rebuild parity remain unproven.

The retail cluster maintains a playlist of tracks loaded from the `data\music` directory and handles:
- Playlist management (linked list of tracks)
- Volume control with fade in/out
- Track selection (sequential, random, or by game state type)
- Dev mode override (forces BEA 08 track when dev mode enabled)

## 2026-05-25 Wave851 PC Platform/Controller Tail Read-Back

Wave851 PC platform/controller tail (`pc-platform-controller-tail-wave851`, `wave851-readback-verified`) saved comments/tags for `0x00515320 PCPlatform__InitMusicPlaylist`, the PC platform/music bridge that initializes async music streaming and calls `CMusic__LoadPlaylistFromDir(this,"data\music")`. Probe token anchor: `Wave851 PC platform/controller tail`; `0x00515320 PCPlatform__InitMusicPlaylist`; `CMusic__LoadPlaylistFromDir`; `data\music`; `5729/6098 = 93.95%`; `0x00515ab0 D3DDevice__SetViewport`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-085618_post_wave851_pc_platform_controller_tail_verified`.

The row is a platform connector, not a replacement for the older Wave454 CMusic body work. Runtime audio playback, exact music vtable owner/layout, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x004bb380 | CMusic__Init | SAVED | Wave454 saved static signature/comment; initializes volume, playlist head, play type, and platform device state |
| 0x004bb400 | CMusic__Shutdown | SAVED | Wave454 saved static signature/comment; stops playback when active and frees playlist entries |
| 0x004bb450 | CMusic__Play | SAVED | Wave454 corrected `char * filename` stack argument and play-device call path |
| 0x004bb490 | CMusic__Stop | SAVED | Wave454 saved stop path through platform vtable `+0x0c` when `+0x08` playing flag is set |
| 0x004bb4b0 | CMusic__FadeVolumes | SAVED | Wave454 corrected source-parity name; handles volume stepping and queued-song transition |
| 0x004bb530 | CMusic__UpdateStatus | SAVED | Wave454 corrected source-parity name; per-frame platform update, fade, volume clamp, and track-finished mode handling |
| 0x004bb6b0 | CMusic__AddToPlayList | SAVED | Wave454 corrected source-parity spelling; sorted playlist insertion and duplicate rejection |
| 0x004bb7c0 | CMusic__LoadPlaylistFromDir | SAVED | Wave454 corrected `char * directory_path`; behavior-bounded retail extension-wrapper call |
| 0x004bb7e0 | CMusic__PlayFromList | SAVED | Wave454 corrected source-parity name/signature; plays specific, queued, or random playlist entry |
| 0x004bb8c0 | CMusic__PlaySelection | SAVED | Wave454 corrected source-parity name/signature; maps music selection to retail track index and mode 3 replay |
| 0x004bba10 | CMusic__SetVolume | SAVED | Wave454 corrected source-parity name/signature; retail linear 0.0-1.0 -> 0-127 conversion |

## Details

### CMusic__AddToPlayList (0x004bb6b0)

- **Purpose**: Adds a music track filename to the playlist
- **Xref**: Found via debug path string at 0x00630a4c (line 0x13e = 318)
- **Debug output**: "Added %s to playlist\n" (0x00630a34)
- **Mechanism**:
  - Allocates 0x10c (268) byte track entry
  - Entry contains 0x100 (256) byte filename + 4-byte next pointer + 4-byte unknown
  - Maintains sorted linked list (uses string comparison `stricmp` (0x00568390, was `FUN_00568390`))
  - Duplicate filenames are rejected (early return if already in list)

### CMusic__Init (0x004bb380)

- **Purpose**: Initialize the music system
- **Debug output**: "input vol = %2.8f, master music volume = %d" (0x00630a08)
- **Actions**:
  - Sets default volume to 0x7f (127) - max volume
  - Converts float volume (0.0-1.0) to integer (0-127)
  - Stores volume in global DAT_00662ab0
  - Clears playlist pointer

### CMusic__SetVolume (0x004bba10)

- **Purpose**: Set the master music volume
- **Parameter**: float volume (0.0 to 1.0)
- **Conversion**: `intVolume = round(floatVolume * 127.0)`
- **Debug output**: Same as Init - "input vol = %2.8f, master music volume = %d"
- **Storage**: Volume stored at ECX+0x2c and global DAT_00662ab0
- **Wave454 caveat**: Retail uses this linear conversion; the PC source tangent-volume path differs and runtime loudness behavior is not proven.

### CMusic__Shutdown (0x004bb400)

- **Purpose**: Clean up music system
- **Actions**:
  - Stops playback if active (via vtable call)
  - Frees all playlist entries (walks linked list, calls OID__FreeObject)
  - Clears playlist head pointer

### CMusic__Play (0x004bb450)

- **Purpose**: Start playing the current track
- **Actions**:
  - Stops any current playback first
  - Sets volume to master volume
  - Calls vtable play function
  - Sets playing flag to 1

### CMusic__Stop (0x004bb490)

- **Purpose**: Stop music playback
- **Actions**:
  - Calls vtable stop function if currently playing
  - Clears playing flag

### CMusic__FadeVolumes (0x004bb4b0)

- **Purpose**: Smooth volume transitions between tracks
- **Mechanism**:
  - Adjusts current volume toward target volume by +/-5 per frame
  - When volume reaches 0 during fade-out, triggers track change
  - When volume reaches target, resets to master volume

### CMusic__UpdateStatus (0x004bb530)

- **Purpose**: Main per-frame update for music system
- **Called by**: Game main loop
- **Logic**:
  - Calls vtable update function (platform-specific)
  - Updates volume fade
  - Clamps volume to 0-127 range
  - When track finishes, handles next track based on play mode:
    - Mode 0: Stop after single track
    - Mode 1: Sequential playlist (loop to start)
    - Mode 2: Random shuffle
    - Mode 3: Play by game state type
- **Dev mode override**: When `g_bDevModeEnabled` or `g_bAllCheatsEnabled`, forces "data\music\BEA 08(Master).wma"

### CMusic__LoadPlaylistFromDir (0x004bb7c0)

- **Purpose**: Load all music files from a directory
- **Parameter**: Directory path (typically "data\music")
- **Mechanism**: Retail body is a platform `DeviceAddDirectoryExts`-style wrapper at vtable `+0x18` with `directory_path` plus extension token `0x00630a04`, then `ret 0x4`.
- **Wave454 caveat**: Kept behavior-bounded because the retail body is not the full PC source `AddDirectoryToPlaylist` body.

### CMusic__PlayFromList (0x004bb7e0)

- **Purpose**: Start playing a specific track or random selection
- **Parameters**:
  - `song_entry`: Track pointer (0 = random selection)
  - `fade`: Crossfade flag (1 = fade out current first)
- **Logic**:
  - If crossfade and already playing: sets pending track, fades out
  - If track is 0: random selection from playlist
  - Dev mode override: Forces BEA 08 track

### CMusic__PlaySelection (0x004bb8c0)

- **Purpose**: Select and play track based on game state
- **Parameters**:
  - `music_selection`: Game state/music-selection type (0-4)
  - `fade`: Crossfade flag
- **Track selection**:
  - Type 0: Track 8 (or 1 if DAT_0083d448 set)
  - Type 1: Track 7
  - Type 2: Track 3
  - Type 3/4: Random track 0-6 (skipping 7, using 9 instead)
- **Debug output**: "Playing Track: %d\n" (0x00630a68)

## Class Structure (CMusic)

Based on member access patterns in the decompiled code:

```cpp
class CMusic {
    /* 0x00 */ void* vtable;           // Virtual function table
    /* 0x04 */ int mPlayMode;          // 0=single, 1=sequential, 2=random, 3=byType
    /* 0x08 */ bool mIsPlaying;        // Currently playing flag
    /* 0x0c */ void* mPlaylistHead;    // Head of track linked list
    /* 0x10 */ void* mCurrentTrack;    // Currently playing track
    /* ... */
    /* 0x28 */ int mTargetVolume;      // Volume fading toward
    /* 0x2c */ int mMasterVolume;      // Master volume (0-127)
    /* 0x30 */ void* mPendingTrack;    // Track to play after fade
    /* 0x34 */ int mCurrentVolume;     // Current volume during fade
    /* 0x38 */ bool mFadeEnabled;      // Volume fading active
    /* 0x3c */ int mTrackType;         // For PlayTrackByType
};
```

## Virtual Function Table

The CMusic class uses virtual functions for platform-specific operations:

| Offset | Purpose |
|--------|---------|
| 0x00 | Platform init |
| 0x04 | Platform shutdown |
| 0x08 | Play file |
| 0x0c | Stop |
| 0x10 | IsFinished |
| 0x14 | SetVolume |
| 0x18 | LoadDirectory (with callback) |
| 0x1c | Crossfade to file |
| 0x20 | Update |

## Related Strings

| Address | String | Used By |
|---------|--------|---------|
| 0x00630a4c | "[maintainer-local-source-export-root]\Music.cpp" | AddToPlayList (memory alloc) |
| 0x00630a34 | "Added %s to playlist\n" | AddToPlayList |
| 0x00630a08 | "input vol = %2.8f, master music volume = %d" | Init, SetVolume |
| 0x00630a68 | "Playing Track: %d\n" | PlaySelection |
| 0x006309e4 | "data\music\BEA 08(Master).wma" | Dev mode override track |
| 0x0063dff0 | "data\music" | Default music directory |

## Notes

1. **Dev Mode Music Override**: When dev mode or cheats are enabled, ALL music playback is forced to use "BEA 08(Master).wma" - likely for faster testing or to avoid licensing issues during development.

2. **Track Entry Structure**: Each playlist entry is 268 bytes: 256-byte filename buffer, 4-byte next pointer at offset 0x104, and 4-byte field at offset 0x108 (initialized to -1).

3. **Volume System**: Internal volume uses 0-127 range. Retail float input (0.0-1.0) is converted linearly via multiplication by 127; this differs from the PC source tangent-volume path.

4. **Platform Abstraction**: CMusic is an abstract base class. CPCMusic (at 0x0063dfe0 RTTI) is the Windows/PC implementation using Windows Media Audio (.wma) files.

5. **Wave454 Boundary**: The saved Ghidra tranche is static retail-binary evidence. Runtime music playback, directory enumeration, track-selection behavior, concrete `CMusic`/`CSong`/`CPCMusic` layouts, exact source identities, BEA launch, game patching, and rebuild parity remain unproven.
