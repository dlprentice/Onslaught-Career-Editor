# CLIParams.cpp Functions

> Source File: CLIParams.cpp | Binary: BEA.exe

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Command-line parameter parsing for the PC port. While Stuart's source shows internal dev parameters, the retail binary has a different (more limited) set.

Wave 320 saved the retail parser signature as `void __thiscall CLIParams__ParseCommandLine(void * this, char * commandLine)` and added a bounded Ghidra comment. The pass proves parser structure and branch presence only; it does not prove every flag's runtime effect.

Wave799 PC utility microhelpers (`pc-utility-microhelpers-wave799`, `wave799-readback-verified`) corrected `0x00441730 CLIParams__SetField04` to `void __thiscall CLIParams__SetField04(void * this, int field04_value)`. Instruction evidence loads `[ESP+4]`, stores to `[ECX+4]`, and returns with `RET 0x4`, so the older `unused_flags` parameter was phantom. Stuart source layout suggests field `+4` may align with `mNoStaticShadows`, but retail field identity and runtime command-line behavior remain unproven. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-063302_post_wave799_pc_utility_microhelpers_verified`.

Wave1032 (`tweak-reconnect-interface-review-wave1032`) re-reviewed the `-landscape0/-landscape1/-landscape2` reconnect-interface setter calls in `CLIParams__ParseCommandLine` read-only. Xref-site windows confirm parser call sites `0x00423f45`, `0x00423f66`, and `0x00423f87` call `0x00527d00 CReconnectInterface__VFunc_07_00527d00`, which rounds the float argument and marks the reconnect/tweak record explicitly set. The same wave also re-read `0x00527c90 CReconnectInterface__ctor`, `0x00528690 CTweak__ctor_base`, `0x005286b0 CTweak__dtor_base`, `0x00528b20 CTweakInt_SetNumViewpoints__ctor`, `0x00527c50 CFrontEnd__AdvanceStateAndRelinquishControl`, `0x004530a0 CTweak__dtor_base_thunk_004530a0`, and stale non-function context `0x0054d4ac`. Fresh exports verified 5 primary metadata rows, 5 tag rows, 15 xref rows, 58 body-instruction rows, 5 decompile rows, 3 context metadata rows, 3 context tag rows, 53 context xref rows, 19 context body-instruction rows, 3 context decompile rows, 13 xref-site windows / 273 rows, and 3 table windows / 24 rows. No mutation was needed. Wave911 focused re-audit progress after Wave1032 is `631/1408 = 44.82%`; expanded static surface progress is `860/1493 = 57.60%`; top-500 coverage remains `500/500 = 100.00%`; export-contract closure remains `6238/6238 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-043550_post_wave1032_tweak_reconnect_interface_review_verified`. Runtime landscape-detail behavior, frontend reconnect behavior, exact source-body identity, exact layouts/table schemas, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1032; tweak-reconnect-interface-review-wave1032; 0x00527c90 CReconnectInterface__ctor; 0x00527d00 CReconnectInterface__VFunc_07_00527d00; 0x00528690 CTweak__ctor_base; 0x005286b0 CTweak__dtor_base; 0x00528b20 CTweakInt_SetNumViewpoints__ctor; 0x00527c50 CFrontEnd__AdvanceStateAndRelinquishControl; 0x004530a0 CTweak__dtor_base_thunk_004530a0; 0x0054d4ac; 631/1408 = 44.82%; 860/1493 = 57.60%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-043550_post_wave1032_tweak_reconnect_interface_review_verified; no mutation.

Wave1212 (`wave1212-options-detail-tweak-current-risk-review`) re-read the active current-risk `CReconnectInterface__VFunc_07_00527d00`, `CTweak__ctor_base`, `CTweak__dtor_base`, and `CTweak__dtor_base_thunk_004530a0` rows alongside the options/detail helpers. The saved static contract remains that `CLIParams__ParseCommandLine` routes `-landscape0/-landscape1/-landscape2` call sites through the reconnect-interface setter, while `CTweak__ctor_base`/`CTweak__dtor_base` link and unlink records from the global tweak list `DAT_0089c018`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-065722_post_wave1212_options_detail_tweak_current_risk_review_verified`. Runtime CLI/tweak behavior, exact CTweak layout, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x00423bc0 | [CLIParams__ParseCommandLine](./CLIParams__ParseCommandLine.md) | Command-line parameter parsing |
| 0x00441730 | CLIParams__SetField04 | Wave799 field+4 setter; `RET 0x4` proves one visible stack argument and removes the old phantom `unused_flags` signature artifact |

## PC Port CLI Parameters (Observed via Ghidra)

These parameter branches are present in `BEA.exe` and were statically re-confirmed through the saved `CLIParams__ParseCommandLine` signature/comment pass. Runtime behavior is proven only where a separate runtime note says so.

| Parameter | Effect | Status |
|-----------|--------|--------|
| `-level N` | Start at specific level | Parser-visible |
| `-skipfmv` | Skip FMV cutscenes | Parser-visible |
| `-nomusic` | Disable music | Parser-visible |
| `-nosound` | Disable all sound | Parser-visible |
| `-showdebugtrace` | Enable debug trace output | Parser-visible |
| `-traceconsole` | Enable trace console | Parser-visible |
| `-playabledemo` | Enable demo mode | Parser-visible |
| `-res W H` | Set resolution (min 640x480) | Parser-visible |
| `-32bittextures` | Force 32-bit textures | Parser-visible |
| `-dxtntextures` | Force DXT textures | Parser-visible |
| `-landscape0/1/2` | Set landscape detail level | Parser-visible |
| `-e3` | E3 demo mode (special demo build) | Discovered Dec 2025 |
| `-cardid` | Force card ID mode | Discovered Dec 2025 |
| `-backbuffer2` | Double backbuffer | Discovered Dec 2025 |
| `-timeout N` | Set timeout value | Discovered Dec 2025 |
| `-soundbuffers N` | Set sound buffer count | Discovered Dec 2025 |
| `-autoconfigtest [path]` | Run auto-config test | Discovered Dec 2025 |
| `-getversion` | Print version and exit | Parser-visible |
| `-testeur` | Enable test mode | Discovered Dec 2025 |
| `-defaultoptionsname` | Set options filename | Parser-visible |
| `-findgoodwater` | Water detection mode | Parser-visible |
| `-findbadwater` | Water detection mode | Parser-visible |
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
