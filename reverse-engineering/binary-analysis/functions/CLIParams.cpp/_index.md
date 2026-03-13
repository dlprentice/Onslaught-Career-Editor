# CLIParams.cpp Functions

> Source File: CLIParams.cpp | Binary: BEA.exe

## Overview

Command-line parameter parsing for the PC port. While Stuart's source shows internal dev parameters, the retail binary has a different (more limited) set.

## Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x00423bc0 | [CLIParams__ParseCommandLine](./CLIParams__ParseCommandLine.md) | Command-line parameter parsing |

## PC Port CLI Parameters (Verified via Ghidra)

These parameters ARE in BEA.exe and work in the retail Steam release:

| Parameter | Effect | Status |
|-----------|--------|--------|
| `-level N` | Start at specific level | Works |
| `-skipfmv` | Skip FMV cutscenes | Works |
| `-nomusic` | Disable music | Works |
| `-nosound` | Disable all sound | Works |
| `-showdebugtrace` | Enable debug trace output | Works |
| `-traceconsole` | Enable trace console | Works |
| `-playabledemo` | Enable demo mode | Works |
| `-res W H` | Set resolution (min 640x480) | Works |
| `-32bittextures` | Force 32-bit textures | Works |
| `-dxtntextures` | Force DXT textures | Works |
| `-landscape0/1/2` | Set landscape detail level | Works |
| `-e3` | E3 demo mode (special demo build) | Discovered Dec 2025 |
| `-cardid` | Force card ID mode | Discovered Dec 2025 |
| `-backbuffer2` | Double backbuffer | Discovered Dec 2025 |
| `-timeout N` | Set timeout value | Discovered Dec 2025 |
| `-soundbuffers N` | Set sound buffer count | Discovered Dec 2025 |
| `-autoconfigtest [path]` | Run auto-config test | Discovered Dec 2025 |
| `-getversion` | Print version and exit | Works |
| `-testeur` | Enable test mode | Discovered Dec 2025 |
| `-defaultoptionsname` | Set options filename | Works |
| `-findgoodwater` | Water detection mode | Works |
| `-findbadwater` | Water detection mode | Works |
| `-forcewindowed` | Force windowed mode | **GUARDED** |

## Critical: -forcewindowed Guard Flag is Build-Dependent

The `-forcewindowed` parameter is protected by `DAT_00662f3e`. This flag must be non-zero for the parameter to be processed. In the current canonical Steam hash used by this repo (`74154bfa...`), the byte is already `0x01`; some historical baselines were observed at `0x00`, which explains older reports that the parser path was unreachable.

**Practical guidance**:
- Guard-byte normalization (`0x262F3E: 00 -> 01`) is only relevant when analyzing or patching a variant binary that still carries the `0x00` baseline.
- For current repo binaries, the reliable user-facing path is the startup-flow patch set documented in [windowed-mode-analysis.md](../../windowed-mode-analysis.md): stable `0x12A644`, with optional experimental `0x12BB97` only if startup still flips back to fullscreen on that setup.

## Parameters NOT in Retail

These parameters from Stuart's source code are NOT present in the retail binary:

- `-devmode` - Developer mode
- `-record` / `-play` - Demo recording
- `-geforce2` / `-geforce3` - GPU forcing
- `-vshaders` / `-novshaders` - Shader toggle
- `-modelviewer` - Model viewer
- `-cutsceneeditor` - Cutscene editor
- `-GOD`, `-ALLLEV`, `-ALLGOODIES` - **DO NOT EXIST**

## Newly Documented Parameters (Dec 2025)

The following parameters were discovered via Ghidra analysis of `CLIParams__ParseCommandLine` at 0x00423bc0:

### -e3

**Purpose:** E3 demo mode - likely a special build mode for the E3 trade show demo.

**Effect:** Sets a global flag for E3-specific behavior. May restrict available levels, show demo-specific UI, or enable trade show features.

**Status:** Present in binary, untested. Likely vestigial from E3 2003 demo build.

### -cardid

**Purpose:** Force card identification mode for graphics card detection.

**Effect:** Forces the game to run card identification/detection routines, possibly for troubleshooting GPU compatibility issues.

**Status:** Present in binary, effect needs testing.

### -backbuffer2

**Purpose:** Double backbuffer mode for rendering.

**Effect:** Enables a second backbuffer for rendering, which can improve frame pacing and reduce tearing at the cost of slightly increased latency.

**Status:** Present in binary, likely works. Useful for systems with tearing issues.

### -timeout N

**Purpose:** Set a timeout value (integer parameter).

**Effect:** Sets a timeout threshold in the game engine. Exact purpose unclear - may relate to network timeouts, demo timeout, or other time-limited functionality.

**Status:** Present in binary, accepts integer argument. Effect needs testing.

### -soundbuffers N

**Purpose:** Configure the number of sound buffers.

**Effect:** Sets the number of DirectSound buffers used for audio playback. Higher values may improve audio stability on some systems but use more memory.

**Status:** Present in binary, accepts integer argument. Useful for troubleshooting audio issues.

### -autoconfigtest [path]

**Purpose:** Run automatic configuration test.

**Effect:** Executes the game's auto-configuration routine to detect optimal settings. Optional path argument may specify where to save results.

**Status:** Present in binary, accepts optional path argument. Used by the game's setup/detection system.

### -testeur

**Purpose:** Enable test mode (European test build flag?).

**Effect:** Enables a test mode flag. The name suggests this may have been for European QA testing ("testeur" is French for "tester").

**Status:** Present in binary, effect needs testing.

---
*Migrated from ghidra-analysis.md (Dec 2025)*
*7 additional parameters documented Dec 2025 via Inquisition analysis*
