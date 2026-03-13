# Source Code Analysis - Index

> Curated analysis of the public source-reference material used alongside retail binary validation
> Last updated: 2026-02-11

## Overview

Stuart Gillam's source code is from the **internal PC build** used during development. The Steam PC release is a later retail build (console-port lineage) with a different on-disk save layout. Many values only *look* “shift-16” in 4-byte aligned hex dumps because retail `BEA.exe` copies `CCareer` bytes from/to `file + 2` after a 16-bit version word.

**Reference Corpus Snapshot:**
- The public `Onslaught` repository provides an internal PC-build source snapshot used as historical reference material for this appendix.
- The public `AYAResourceExtractor` repository provides the companion asset-tooling code referenced in game-asset documentation.

## 2026-02-11 Full Parse Refresh

Full-corpus inventory parse completed for both reference repositories:

- [`full-source-parse-2026-02-11.md`](full-source-parse-2026-02-11.md)
- [`stuart-source-file-manifest-2026-02-11.tsv`](stuart-source-file-manifest-2026-02-11.tsv)
- [`aya-resourceextractor-file-manifest-2026-02-11.tsv`](aya-resourceextractor-file-manifest-2026-02-11.tsv)

Refresh metrics:

| Corpus | Files | Notes |
|--------|------:|-------|
| `references/Onslaught` | 111 | 52 `.cpp`, 53 `.h`, full file-level hashes/line counts |
| `references/AYAResourceExtractor` | 75 | 54 source files parsed (`.cs/.cpp/.c/.h`) |

---

## Documentation Structure

### Core Systems

Low-level engine architecture and object hierarchies:

- **[thing-system.md](core/thing-system.md)** - Base game object system, CThing/CComplexThing hierarchy, THING_FLAGS, type system
- **[actor-system.md](core/actor-system.md)** - CActor class, movement, physics (20 FPS updates), kill tracking integration
- **[engine-system.md](core/engine-system.md)** - CEngine/CDXEngine/CPCEngine hierarchy, DirectX 8 rendering, VIEWPOINTS constant
- **[platform-system.md](core/platform-system.md)** - Platform abstraction layer (CPlatform), cross-platform routing, key codes

### Gameplay Systems

Player mechanics, progression, and combat:

- **[career-system.md](gameplay/career-system.md)** - CCareer class, nodes, links, grades, save structure, tech slots
- **[battle-system.md](gameplay/battle-system.md)** - CBattleEngine mech, walker/jet modes, god mode, configurations, weapon augmentation
- **[game-system.md](gameplay/game-system.md)** - Game loop (CGame), death/respawn, multiplayer levels, B4K42 cheat, EndLevelData

### Frontend Systems

Menus, UI, and input handling:

- **[fep-systems.md](frontend/fep-systems.md)** - All FEP* files, save/load pages, cheat codes, DXFrontend/PCFrontend, menu flow
- **[controller-system.md](frontend/controller-system.md)** - Input system, debug keys (V=god, U=win), virtual buttons, PCController

### I/O Systems

Data persistence, asset loading, and event scheduling:

- **[storage-system.md](io/storage-system.md)** - Save/load system, version stamps, DXMemBuffer, memory card abstraction
- **[chunker-system.md](io/chunker-system.md)** - AYA format, asset loading (Chunker), MKID macro, ResourceAccumulator
- **[event-system.md](io/event-system.md)** - Event scheduler, CActiveReader pattern, scheduled events

---

## Critical Discoveries

### B4K42 Cheat Mechanism (FEPSaveGame.cpp)

**Scope note:** This section reflects the **internal/source build** strings (`B4K42`, `!EVAH!`, `105770Y2`). The Steam PC port uses different cheat codes (`MALLOY`, `TURKEY`, `Maladim`), and Maladim has **no visible effect** in user testing (Dec 2025).

**Source/internal finding:** The B4K42 god mode cheat check uses `strstr()` against the **save game NAME** at runtime (substring match):

```cpp
// From FEPSaveGame.cpp - IsCheatActive()
if (strstr(saveName, "B4K42") != NULL) {
    // God mode enabled - "MyB4K42Save" would also work
}
```

This explains why:
- Save patching per-player god flags from the internal source doesn't reliably enable god mode in the Steam build (cheat-gated; Steam save offsets previously labeled `mIsGod[]` are invert-Y settings)
- Earlier "P2 god flag on disk" conclusions from `.bes` bytes were based on that mislabeling and should be treated as invalid for Steam until re-tested with corrected field mapping
- RAM trainers work (they bypass the save-load path)

### EndLevelData is Runtime-Only

**EndLevelData is NOT saved to .bes files.** It's a runtime-only struct that gets consumed by `CCareer::Update()` and discarded. The historically labeled "mystery region" at 0x24CC is NOT cached EndLevelData; that area falls in the options entries/tail/global-settings region and remaining reserved bytes.

See [gameplay/career-system.md](gameplay/career-system.md) for detailed analysis.

### Internal Build CLI Parameters

Core internal/source parameters confirmed in `CLIParams.cpp` include:

| Parameter | Purpose |
|-----------|---------|
| `-devmode` | Enable developer mode |
| `-forcewindowed` | Run in windowed mode |
| `-skipfmv` | Skip FMV/cutscenes |
| `-level N` | Start at specific level |
| `-record FILE` / `-play FILE` | Demo recording/playback |
| `-geforce2` / `-geforce3` | GPU compatibility mode |
| `-modelviewer` / `-cutsceneeditor` | Internal tools (DEV_VERSION) |

**No -GOD flag exists (in source/internal build).** God mode is via save-name checks (B4K42 in source; Maladim in the PC port, with no confirmed effect).

---

## Quick Reference

### Source Constants (Career.h)

| Constant | Value | Notes |
|----------|-------|-------|
| `NUM_LEVELS` | 43 | Campaign missions |
| `MAX_NODES` | 100 | Node slots in save file |
| `MAX_LINKS` | 200 | Link slots (MAX_NODES × 2) |
| `MAX_NUM_GOODIES` | 300 | Goodie slots |
| `MAX_CAREER_SLOTS` | 32 | Tech slots |
| `CAREER_VERSION` | 9 | Internal build version |

### Version Stamp Formula

```cpp
static SWORD current_version_stamp() {
    return SWORD(CAREER_VERSION + (sizeof(CCareer) << 4));
}
// In source/internal builds this formula uses CAREER_VERSION=9 (e.g., 0x4BC9 for sizeof(CCareer)=0x4BC); retail Steam runtime uses BASE_VERSION=0x11, yielding 0x4BD1.
// Many hex dumps show the first 4 bytes as 0x00004BD1
// because that's the version word plus the next 16 bits of CCareer (often zero).
```

### Retail Save Encoding Note

Retail `.bes` contains a `CCareer` core copied from/to `file + 2` after a 16-bit version word (`0x4BD1`), plus retail-only options entries/tail blocks that are not represented 1:1 by the internal source snapshot:

```text
file_offset = 0x0002 + career_offset
```

If you view the file at 4-byte aligned offsets (`% 4 == 0`), values can appear “shift-16”, but that’s a 2-byte misaligned view. Patchers/docs should use the true dword view offsets (`% 4 == 2`).

---

## Developer Notes

### Typos Preserved in Source

| Typo | Location | Should Be |
|------|----------|-----------|
| `TK_INFANTY` | Player.h | TK_INFANTRY |
| `BUTTON_LOOSE_LEVEL` | Controller.h | BUTTON_LOSE_LEVEL |
| `SetInfinateEnergy` | Player.cpp | SetInfiniteEnergy |
| `mPreferedControlView` | Player.cpp | mPreferredControlView |
| `BUTTON_CAMERA_MOVE_FORAWRD` | Controller.h | BUTTON_CAMERA_MOVE_FORWARD |
| `InfleunceMap` | MemoryManager | InfluenceMap |
| `barrell roll` | BattleEngineJetPart.cpp:441 | barrel roll |
| `GetCurrentAccleration` | BattleEngineWalkerPart | GetCurrentAcceleration |
| `sepecial` | BattleEngineWalkerPart | special |
| `mInfinateEnergy` | BattleEngineWalkerPart | mInfiniteEnergy |
| `Horible hack` | DXEngine.cpp | Horrible hack |
| `schuled event` | EventManager.cpp | scheduled event |
| `witch offset buffer` | EventManager.cpp | which offset buffer |
| `previus_num_events_called` | EventManager.cpp | previous_num_events_called |

### Code Bugs Found

#### Controller Recording Bug

Copy-paste error in `RecordControllerState()`:
```cpp
mDataFile.Write(&mAnaloguex1, sizeof(mAnaloguex2));  // Wrong sizeof!
mDataFile.Write(&mAnaloguey1, sizeof(mAnaloguex2));  // Wrong sizeof!
```

#### Music.cpp Assignment Bug

Line 448 uses assignment (`=`) instead of comparison (`==`):
```cpp
if (condition = value)  // Should be: if (condition == value)
```
Classic C/C++ bug that compiles but produces incorrect behavior.

### Developer Initials Found

- **SRG** - Stuart R. Gillam (lead programmer)
- **JCL** - Unknown (memory manager, Camera.cpp)
- **Jan** - Unknown (thread-safety)
- **led** - Unknown (Camera.cpp)
- **kempy** - Unknown (skybox "kempy cube")

### Internal Codename

The game was internally called "Onslaught":
- Window title: "Battle Engine Aquila"
- Crash dumps: `OnslaughtException.txt`
- Default memory: 96 MB heap

---

## Reference Corpus Summary

This appendix tracks the currently analyzed reference corpus rather than a transfer history.

- `references/Onslaught`: internal PC-build source snapshot used for historical cross-reference
- `references/AYAResourceExtractor`: companion public repo for AYA asset tooling

Current authoritative totals are tracked in `full-source-parse-2026-02-11.md` and the two manifest TSV files (111 files in `references/Onslaught`, 75 files in `references/AYAResourceExtractor`).

---

## Cross-Reference: Game Folder Analysis (December 2025)

This section documents findings from comparing Stuart's source code against the actual Steam game folder (see [game-folder-analysis.md](../game-assets/game-folder-analysis.md)).

### Level Numbering: mWorldNumber Mapping

**CONFIRMED**: The `mWorldNumber` field in `CCareerNode` directly maps to the `level###/` folders in `data/MissionScripts/`.

Complete mapping from `level_structure[43][5]` in Career.cpp:

| Node Index | mWorldNumber | Level Folder | Episode | Notes |
|------------|--------------|--------------|---------|-------|
| 0 | 100 | level100/ | 1 | Training mission |
| 1 | 110 | level110/ | 1 | Tutorial |
| 2 | 200 | level200/ | 2 | Episode 2 start |
| 3 | 211 | level211/ | 2 | Branch A |
| 4 | 212 | level212/ | 2 | Branch B |
| 5 | 221 | level221/ | 2 | |
| 6 | 222 | level222/ | 2 | |
| 7 | 231 | level231/ | 2 | Episode 3 unlock trigger |
| 8 | 232 | level232/ | 2 | Episode 3 unlock trigger |
| 9 | 300 | level300/ | 3 | Episode 3 start |
| 10 | 311 | level311/ | 3 | |
| 11 | 312 | level312/ | 3 | |
| 12 | 321 | level321/ | 3 | |
| 13 | 322 | level322/ | 3 | |
| 14 | 331 | level331/ | 3 | Episode 4 unlock trigger |
| 15 | 332 | level332/ | 3 | Episode 4 unlock trigger |
| 16 | 400 | level400/ | 4 | Episode 4 start |
| 17 | 411 | level411/ | 4 | |
| 18 | 412 | level412/ | 4 | |
| 19 | 421 | level421/ | 4 | |
| 20 | 422 | level422/ | 4 | |
| 21 | 431 | level431/ | 4 | Episode 5 unlock trigger |
| 22 | 432 | level432/ | 4 | Episode 5 unlock trigger |
| 23 | 500 | level500/ | 5 | **BRANCHING MISSION** (rocket/sub) |
| 24 | 511 | level511/ | 5 | Rocket path |
| 25 | 512 | level512/ | 5 | Submarine path |
| 26 | 521 | level521/ | 5 | |
| 27 | 522 | level522/ | 5 | |
| 28 | 523 | level523/ | 5 | Episode 6 unlock trigger |
| 29 | 524 | level524/ | 5 | Episode 6 unlock trigger |
| 30 | 600 | level600/ | 6 | Episode 6 start |
| 31 | 611 | level611/ | 6 | |
| 32 | 612 | level612/ | 6 | |
| 33 | 621 | level621/ | 6 | Episode 7 unlock trigger |
| 34 | 622 | level622/ | 6 | Episode 7 unlock trigger |
| 35 | 700 | level700/ | 7 | Episode 7 start |
| 36 | 710 | level710/ | 7 | |
| 37 | 720 | level720/ | 7 | |
| 38 | 731 | level731/ | 7 | |
| 39 | 732 | level732/ | 7 | |
| 40 | 741 | level741/ | 7 | Has hack.msl |
| 41 | 742 | level742/ | 7 | Has hack.msl, Episode 8 unlock trigger |
| 42 | 800 | level800/ | 8 | **FINAL LEVEL** |

**Episode Unlock Logic** (from `IsEpisodeAvailable()` in Career.cpp):
- Episodes 0-1: Always available
- Episode 2: Complete level 110
- Episode 3: Complete level 231 OR 232
- Episode 4: Complete level 331 OR 332
- Episode 5: Complete level 431 OR 432
- Episode 6: Complete level 521, 522, 523, OR 524
- Episode 7: Complete level 621 OR 622
- Episode 8: Complete level 741 OR 742

**Non-Campaign Levels** (in game folder but NOT in level_structure):
- level800 variants: 850-866 (Evo/bonus levels)
- level888: Unknown special level
- level900: Multiplayer base
- level901-905: Versus/skirmish modes
- level956, level958: Unknown purpose

---

### MSL Scripting Language

**CONFIRMED**: Source code directly includes MSL files.

From Career.cpp line 11:
```cpp
#include "data\MissionScripts\onsldef.msl"
```

From FEPGoodies.cpp line 7:
```cpp
#include "data\MissionScripts\text\text.stf"
```

This indicates (from source includes):
1. `.msl` files are parsed at compile time (included as headers)
2. `onsldef.msl` contains global mission script definitions
3. `text.stf` contains compiled string table data

**Scripted Goodies** (from Career.cpp lines 740-758):
```cpp
// goodie 50 is scripted
// goodie 52 is scripted
// goodies 67 to 70 race ones done in script
```

This means goodies 50, 52, and 67-70 have unlock conditions defined in level MSL scripts rather than in FEPGoodies.cpp.

---

### Goodie Resource Files: Count Verification

**CONFIRMED**: 232 goodie resource files match source code expectations.

| Source | Count | Notes |
|--------|-------|-------|
| Game folder | 232 | `goodie_00_res_PC.aya` through `goodie_231_res_PC.aya` |
| FEPGoodies.cpp goodies[] array | 234 | Lines 152-385 in source |
| Career.h MAX_NUM_GOODIES | 300 | Save file capacity |

**Analysis**:
- The goodies[] array has 234 entries in source, but retail UI behavior uses slot 232 for FMV cutscene 33.
- 232 actual `goodie_XX_res_PC.aya` resources exist (0-231); slot 232 is displayable without a `goodie_232` resource.
- Save file reserves 300 slots for future expansion

**Goodie Resource Loading** (FEPGoodies.cpp lines 1251-1295):
```cpp
CResourceAccumulator::GetFileName(name, -1000 - goodie_number, TARGET);
// For goodie 0: -1000 - 0 = -1000 -> "goodie_00_res_PC.aya"
// For goodie 231: -1000 - 231 = -1231 -> "goodie_231_res_PC.aya"
```

The negative index `-1000 - N` maps to `goodie_N_res_PC.aya` files.

**Goodie Categories by Index**:
| Range | Content | Count |
|-------|---------|-------|
| 0-7 | Character bios | 8 |
| 8-12 | Race level unlocks | 5 |
| 13-65 | Kill-based & grade-based | 53 |
| 66-70 | Scripted race goodies | 5 |
| 71-77 | Grade totals (A/S ranks) | 7 |
| 78-153 | Concept art (per-level C grades) | 76 |

**Retail mapping note:** Do not treat source-array bucket ranges here as retail UI truth. For authoritative retail ranges use `reverse-engineering/save-file/goodies-system.md`: `0-78` specific unlocks, `79-200` concept art, `201-232` FMV slots.
| 154-199 | Movies (cutscene unlocks) | 46 |
| 200-232 | FMV/tail goodies (retail includes slot 232) | 33 |

---

### defaultoptions.bea: NOT in Source Code

**Result**: No reference to `defaultoptions.bea` found in Stuart's source code.

This file is likely:
1. Generated by a separate build tool
2. Possibly added by the retail/porting layer (not present in the internal source tree); treat ownership as a working hypothesis until retail writer paths are fully traced
3. A default save/template baseline candidate: CCareer dump plus additional options data

The 10,004-byte size and version word (`0x4BD1`, 16-bit at file offset `0x0000`) are consistent with our BES model, making “default template for new career saves” a strong Steam-build hypothesis rather than a confirmed cross-build fact.

Note: Many hex dumps show the first 4 bytes as `0x00004BD1` because that’s the version word plus the next 16 bits of CCareer (often zero if `new_goodie_count` is 0). Don’t validate saves by comparing the 32-bit “dword view”.

---

### File Format References

**AYA Format**:
- `CResourceAccumulator` class handles `.aya` resource loading
- Uses `WriteResources()` and `ReadResources()` with level/goodie indices
- Platform-specific: `*_res_PC.aya`, `*_res_PS2.aya`, `*_res_XBOX.aya`

**No direct references found for**:
- `.vid` (Bink video) - handled externally by binkw32.dll
- `.xap` (voice packs) - format proprietary to the audio system
- `.ogg` (audio) - handled by vorbis.dll

**Memory Type Allocations** (MemoryManager.cpp):
```cpp
MT_SCRIPT        // Script memory
MT_VM_SCRIPT     // VM script memory
MT_INST_SCRIPT   // Script instance memory
MEMTYPE_SCRIPT   // Additional script allocation
```

This confirms scripts are loaded into dedicated memory pools at runtime.

---

### worldheaders.dat Cross-Reference

The file `data/worldheaders.dat` (4.8 KB) in the game folder likely contains the binary equivalent of `level_structure[43][5]` plus additional per-world metadata. No direct reference found in available source, but the name suggests it defines world/level header information loaded at game start.

---

## See Also

- [../save-file/save-format.md](../save-file/save-format.md) - .bes file structure
- [../game-mechanics/god-mode.md](../game-mechanics/god-mode.md) - God mode investigation
- [../save-file/grade-system.md](../save-file/grade-system.md) - Ranking system analysis
- [../../lore/](../../lore/) - Development history, team roster
- [../../roadmap/ROADMAP-INDEX.md](../../roadmap/ROADMAP-INDEX.md) - Project planning

---

*Last updated: 2026-02-11*
