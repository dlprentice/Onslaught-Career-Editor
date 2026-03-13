# Music.cpp

> Music/audio playback system functions from BEA.exe

**Source file**: `Music.cpp`
**Debug path**: `C:\dev\ONSLAUGHT2\Music.cpp` (at 0x00630a4c)
**Class**: `CMusic` (RTTI: `.?AVCMusic@@` at 0x0063dfc8)
**Related classes**: `CPCMusic` (RTTI: `.?AVCPCMusic@@` at 0x0063dfe0)

## Overview

The CMusic class manages background music playback in Battle Engine Aquila. It maintains a playlist of tracks loaded from the `data\music` directory and handles:
- Playlist management (linked list of tracks)
- Volume control with fade in/out
- Track selection (sequential, random, or by game state type)
- Dev mode override (forces BEA 08 track when dev mode enabled)

## Functions

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x004bb380 | CMusic__Init | RENAMED | Initialize music system, set default volumes |
| 0x004bb400 | CMusic__Shutdown | RENAMED | Stop playback, free playlist memory |
| 0x004bb450 | CMusic__Play | RENAMED | Start music playback |
| 0x004bb490 | CMusic__Stop | RENAMED | Stop music playback |
| 0x004bb4b0 | CMusic__UpdateVolumeFade | RENAMED | Handle smooth volume transitions |
| 0x004bb530 | CMusic__Update | RENAMED | Main update loop, handles playlist cycling |
| 0x004bb6b0 | CMusic__AddToPlaylist | RENAMED | Add track to playlist (sorted linked list) |
| 0x004bb7c0 | CMusic__LoadPlaylistFromDir | RENAMED | Load all tracks from directory |
| 0x004bb7e0 | CMusic__PlayTrack | RENAMED | Play specific track or random selection |
| 0x004bb8c0 | CMusic__PlayTrackByType | RENAMED | Play track based on game state type |
| 0x004bba10 | CMusic__SetMasterVolume | RENAMED | Set master music volume (0.0-1.0 -> 0-127) |

## Details

### CMusic__AddToPlaylist (0x004bb6b0)

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

### CMusic__SetMasterVolume (0x004bba10)

- **Purpose**: Set the master music volume
- **Parameter**: float volume (0.0 to 1.0)
- **Conversion**: `intVolume = round(floatVolume * 127.0)`
- **Debug output**: Same as Init - "input vol = %2.8f, master music volume = %d"
- **Storage**: Volume stored at ECX+0x2c and global DAT_00662ab0

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

### CMusic__UpdateVolumeFade (0x004bb4b0)

- **Purpose**: Smooth volume transitions between tracks
- **Mechanism**:
  - Adjusts current volume toward target volume by +/-5 per frame
  - When volume reaches 0 during fade-out, triggers track change
  - When volume reaches target, resets to master volume

### CMusic__Update (0x004bb530)

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
- **Mechanism**: Calls vtable directory enumeration with callback to AddToPlaylist

### CMusic__PlayTrack (0x004bb7e0)

- **Purpose**: Start playing a specific track or random selection
- **Parameters**:
  - param_1: Track pointer (0 = random selection)
  - param_2: Crossfade flag (1 = fade out current first)
- **Logic**:
  - If crossfade and already playing: sets pending track, fades out
  - If track is 0: random selection from playlist
  - Dev mode override: Forces BEA 08 track

### CMusic__PlayTrackByType (0x004bb8c0)

- **Purpose**: Select and play track based on game state
- **Parameter**: Game state type (0-4)
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
| 0x00630a4c | "C:\dev\ONSLAUGHT2\Music.cpp" | AddToPlaylist (memory alloc) |
| 0x00630a34 | "Added %s to playlist\n" | AddToPlaylist |
| 0x00630a08 | "input vol = %2.8f, master music volume = %d" | Init, SetMasterVolume |
| 0x00630a68 | "Playing Track: %d\n" | PlayTrackByType |
| 0x006309e4 | "data\music\BEA 08(Master).wma" | Dev mode override track |
| 0x0063dff0 | "data\music" | Default music directory |

## Notes

1. **Dev Mode Music Override**: When dev mode or cheats are enabled, ALL music playback is forced to use "BEA 08(Master).wma" - likely for faster testing or to avoid licensing issues during development.

2. **Track Entry Structure**: Each playlist entry is 268 bytes: 256-byte filename buffer, 4-byte next pointer at offset 0x104, and 4-byte field at offset 0x108 (initialized to -1).

3. **Volume System**: Internal volume uses 0-127 range (MIDI-style). Float input (0.0-1.0) is converted via multiplication by 127.

4. **Platform Abstraction**: CMusic is an abstract base class. CPCMusic (at 0x0063dfe0 RTTI) is the Windows/PC implementation using Windows Media Audio (.wma) files.
