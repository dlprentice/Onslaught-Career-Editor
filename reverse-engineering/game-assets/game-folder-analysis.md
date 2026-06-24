# Game Folder Analysis
> Complete documentation of Battle Engine Aquila Steam release file structure
> Generated: December 2025

## Overview

| Property | Value |
|----------|-------|
| **Total Size** | 680 MB |
| **Platform** | Windows PC (Steam) |
| **Steam App ID** | 1346400 |
| **Game Executable** | BEA.exe (2.4 MB, PE32 Intel 80386) |

---

## Root Directory Files

### Executables & Libraries

| File | Size | Type | Purpose |
|------|------|------|---------|
| `BEA.exe` | 2.5 MB | PE32 GUI | Main game executable |
| `Message.exe` | 36 KB | PE32 GUI | Error dialog utility |
| `binkw32.dll` | 367 KB | PE32 DLL | Bink video codec (RAD Game Tools) |
| `ogg.dll` | 48 KB | PE32 DLL | Ogg container format |
| `vorbis.dll` | 952 KB | PE32 DLL | Vorbis audio codec |
| `zlib.dll` | 62 KB | PE32 DLL | Compression library |

### Configuration & Data Files

| File | Size | Purpose |
|------|------|---------|
| `defaultoptions.bea` | 10,004 bytes | **Global options baseline/snapshot** - Same retail envelope as .bes saves |
| `cardid.txt` | 18 KB | GPU compatibility database (by Jan Svarovsky) |
| `setuphistory.txt` | 8.7 KB | Runtime log (D3D init, sound setup) |
| `OnslaughtException.txt` | 0 bytes | Crash log (empty) |
| `INSTALL.LOG` | 502 KB | Ghost Installer manifest |
| `steam_appid.txt` | 9 bytes | "1346400" |

### Key Discovery: defaultoptions.bea

`defaultoptions.bea` is the global-options baseline/snapshot (same 10,004-byte retail envelope as `.bes`), not just a one-time template.

- Boot loads it with `CCareer::Load(flag=0)` to apply options entries + tail.
- Frontend load/save flows can overwrite it from loaded/current buffers.
- Career `.bes` loads (`flag=1`) skip immediate options/tail apply.
- Version word is `0x4BD1` (16-bit; the first 4 bytes often *look* like `0x00004BD1` in 4-byte aligned hex dumps).

---

## Directory Structure

```
game/
├── BEA.exe                     # Main executable
├── defaultoptions.bea          # Global options baseline/snapshot (.bea; same 10,004-byte envelope as .bes)
├── Manuals/                    # HTML documentation (2.8 MB)
│   ├── English/
│   ├── French/
│   ├── German/
│   ├── Italian/
│   ├── Spanish/
│   └── Images/
├── data/                       # Game assets (673 MB)
│   ├── MissionScripts/         # Level scripts (4.1 MB)
│   ├── Music/                  # Soundtrack (38 MB)
│   ├── ParticleSets/           # VFX definitions (712 KB)
│   ├── language/               # String tables (1.7 MB)
│   ├── resources/              # Models, textures (149 MB)
│   ├── sounds/                 # Audio files (144 MB)
│   ├── textures/               # Loose textures (776 KB)
│   └── video/                  # FMVs and cutscenes (337 MB)
└── savegames/                  # User save directory (empty)
```

---

## data/MissionScripts/ (4.1 MB)

### Level Numbering System

**97 level directories** with the following patterns:

| Range | Description | Count |
|-------|-------------|-------|
| 000-030 | Early campaign | ~10 |
| 100-110 | Mid campaign (Island 1?) | ~5 |
| 200-232 | Campaign branch A (x11/x12/x21/x22 variants) | ~15 |
| 300-332 | Campaign branch B | ~15 |
| 400-432 | Campaign branch C | ~15 |
| 500-524 | Late campaign (includes Mission 500 branching) | ~10 |
| 600-622 | Late game content | ~10 |
| 700-742 | End game missions | ~15 |
| 800, 850-866 | Bonus/Evo levels | ~8 |
| 888 | Special level | 1 |
| 900-905 | Multiplayer (901+ = versus/skirmish) | ~6 |
| 956, 958 | Unknown special levels | 2 |

### Level Directory Contents

Each level folder typically contains:

```
level###/
├── LevelScript.msl       # Main mission script
├── English.txt           # English mission text
├── Global.txt            # Language-neutral text
├── text.stf              # String table file
└── [additional .msl]     # Support scripts
```

See [mission-scripts-index.md](mission-scripts-index.md) for a per-level inventory of loose scripts.
See [mission-text-index.md](mission-text-index.md) for token → text mapping extracted from English/Global files.
See [mission-message-usage.md](mission-message-usage.md) for message call usage from loose MSL.
See [mission-thing-usage.md](mission-thing-usage.md) for object references/spawns from loose MSL.
See [mission-speaker-index.md](mission-speaker-index.md) for global speaker token mappings.

### MSL Scripting Language

Mission scripts use a custom `.msl` format. Key functions observed:

```msl
// Level completion
LevelWon()
LevelLost()

// Objective system
ObjectiveComplete(id)
ObjectiveFailed(id)

// Special scripts found:
hack.msl                  # In level741, level742 - hacking gameplay?
LapMonitor.msl            # In level901 - race/checkpoint logic
Level500script.msl        # Special script for branching mission
```

### Special Files

| File | Purpose |
|------|---------|
| `onsldef.msl` | Master script definitions |
| `text/english.txt` | Global English strings |
| `text/global.txt` | Language-neutral strings |
| `text/text.stf` | Compiled string table |
| `text/textlist.h` | String ID header (dev artifact!) |

---

## data/resources/ (149 MB)

### AYA Resource Format

Proprietary archive format, extractable with AYAResourceExtractor.

| Pattern | Count | Purpose |
|---------|-------|---------|
| `###_res_PC.aya` | ~80 | Level-specific resources |
| `goodie_##_res_PC.aya` | 232 | Gallery item resources |
| `base_res_PC.aya` | 1 | Base game resources |
| `Frontend_res_PC.aya` | 1 | Menu resources |
| `Loading_res_PC.aya` | 1 | Loading screen resources |

### Subdirectories

| Directory | Count | Contents |
|-----------|-------|----------|
| `dxtntextures/` | 800 | DXT-compressed textures |
| `meshes/` | 213 | Model files (.msh.aya) |
| `textures/` | 47 | UI elements, fonts, impostors |

### Goodie Resource Files

232 files (`goodie_00` through `goodie_231`) - matches our documentation:
- 300 save file slots, 233 displayable goodies in retail (indices 0-232)
- Remaining slots (233-299) are reserved in save storage
- Slot 232 maps to FMV cutscene 33 (displayable without a `goodie_232_res_PC.aya` resource)

---

## data/sounds/ (144 MB)

### Audio Archives

| File | Size | Contents |
|------|------|----------|
| `sounds.sfx` | 14 KB | Sound effect definitions |
| `sounds_english_pc.xap` | 5.4 MB | English voice pack |
| `sounds_french_pc.xap` | 5.6 MB | French voice pack |
| `sounds_german_pc.xap` | 5.6 MB | German voice pack |
| `sounds_italian_pc.xap` | 5.6 MB | Italian voice pack |
| `sounds_spanish_pc.xap` | 5.6 MB | Spanish voice pack |

### XAP Format

Voice pack archives - magic header needs analysis.

### MessageBox Voice Files

`sounds/english/MessageBox/` contains **619 .ogg files**:

Naming pattern: `{level}_{event}.ogg`
- `110_enemy_engaged.ogg`
- `200_objective_complete.ogg`
- etc.

---

## data/video/ (337 MB)

### Video Format

All videos use `.vid` extension (Bink video format).

### Root Videos

| File | Size | Purpose |
|------|------|---------|
| `OpeningFMV.vid` | 20.3 MB | Intro cinematic |
| `UsTheMovie.vid` | 5.2 MB | Credits/outro |
| `LTLogo.vid` | 1.8 MB | Lost Toys logo |
| `FEBack128.vid` | 1.4 MB | Menu background |
| `TWIMTBP_GefFX_640x480_Audio.vid` | 1.6 MB | NVIDIA logo |
| `gill_m_on_a_fork.vid` | 2.9 MB | **Easter egg?** (investigate!) |

### Briefings (29 files)

Pattern: `PC_###_exact.vid` (1.4-4 MB each)

Mission briefing videos for campaign levels.

### Cutscenes (33 files)

Pattern: `##.vid` (1-32 MB each)

Story cutscenes numbered 01-33.

---

## data/Music/ (38 MB)

10 Ogg Vorbis tracks by **Richard Jacques**:

| File | Size |
|------|------|
| BEA_01(Master).ogg | 4.4 MB |
| BEA_02(Master).ogg | 2.8 MB |
| BEA_03(Master).ogg | 4.4 MB |
| BEA_04(Master).ogg | 4.6 MB |
| BEA_05(Master).ogg | 4.4 MB |
| BEA_06(Master).ogg | 4.6 MB |
| BEA_07(Master).ogg | 2.8 MB |
| BEA_08(Master).ogg | 2.9 MB |
| BEA_09(Master).ogg | 3.1 MB |
| BEA_10(Master).ogg | 4.8 MB |

---

## data/language/ (1.7 MB)

Localization string tables (binary .dat format):

| File | Size |
|------|------|
| american.dat | 280 KB |
| english.dat | 280 KB |
| french.dat | 300 KB |
| german.dat | 309 KB |
| italian.dat | 303 KB |
| spanish.dat | 295 KB |

---

## data/ParticleSets/ (712 KB)

| File | Size | Purpose |
|------|------|---------|
| Frontend.par | 28 KB | Menu particle effects |
| MainSet.par | 685 KB | In-game particle effects |
| ModelViewer.par | 3.5 KB | Model viewer effects |

---

## data/ Root Files

| File | Size | Purpose |
|------|------|---------|
| `Dial.raw` | 8 KB | HUD dial graphics? |
| `battle engine configurations.dat` | 1.5 KB | Battle engine parameters |
| `default physics.dat` | 172 KB | Physics configuration |
| `worldheaders.dat` | 4.8 KB | World/level header definitions |

---

## cardid.txt - GPU Compatibility Database

Credit: **Jan Svarovsky** (originally from StarTopia at Mucky Foot)

Comprehensive GPU compatibility database with per-card and per-driver tweaks:

**Supported Vendors:**
- SiS
- ATI (Radeon, Rage series)
- 3Dlabs
- 3dfx (Voodoo series)
- Matrox
- NVIDIA (Riva, GeForce series)
- PowerVR
- S3
- Intel

Contains rendering workarounds and capability flags for era-specific graphics issues.

---

## RE Implications

### Save System Confirmation

1. `defaultoptions.bea` proves our BES format understanding is correct
2. New games copy this template and modify it
3. Same 10,004 byte format, same version stamp

### Level Numbering for Node Mapping

The level directory numbers should map to `mWorldNumber` in CCareerNode:

| Level Dir | Likely Node ID |
|-----------|----------------|
| level100 | 100 |
| level110 | 110 |
| level200 | 200 |
| ... | ... |

This could help decode the node structure in save files.

### Mission 500 Branching

`Level500script.msl` exists - confirms this is where the rocket/submarine path split happens. Relevant to `SLOT_500_ROCKET` and `SLOT_500_SUB` tech slots.

### hack.msl Scripts

Found in level741 and level742 - these levels have special "hacking" gameplay. May be relevant to understanding additional game mechanics.

### Easter Egg Video

`gill_m_on_a_fork.vid` - unusual name, possibly cut content or developer easter egg. Worth investigating.

---

## File Format Summary

| Extension | Format | Tool |
|-----------|--------|------|
| `.bes` / `.bea` | Shared 10,004-byte CCareer envelope (`.bes` career saves; `defaultoptions.bea` global options baseline/snapshot) | Our patcher |
| `.aya` | Resource archive | AYAResourceExtractor |
| `.vid` | Bink video | RAD Video Tools |
| `.ogg` | Vorbis audio | Standard players |
| `.xap` | Voice pack archive | Unknown |
| `.msl` | Mission script | Text-based, readable |
| `.stf` | String table | Binary |
| `.dat` | Various binary data | Per-file analysis needed |
| `.par` | Particle definitions | Unknown |
| `.sfx` | Sound definitions | Unknown |

---

*Document generated from automated analysis - December 2025*
