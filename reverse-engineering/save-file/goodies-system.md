# Goodies System

## CGoodie Struct (4 bytes each)

| Value (true view) | Legacy aligned view | Enum | Visual |
|-------------------|---------------------|------|--------|
| 0 | 0x00000000 | GS_UNKNOWN | Locked, no hints |
| 1 | 0x00010000 | GS_INSTRUCTIONS | Locked, shows unlock hints |
| 2 | 0x00020000 | GS_NEW | Unlocked, gold badge |
| 3 | 0x00030000 | GS_OLD | Viewed, blue badge |

**Offset/encoding nuance:** BEA.exe bulk-copies CCareer from `source + 2`. In the "true dword view" (file offset `0x1F46`), goodie states appear as normal ints `0/1/2/3`. In the repo's historical 4-byte-aligned view (`0x1F44`), those same values appear shifted left 16 (`0x00010000`, `0x00020000`, ...). Both views refer to the same underlying bytes.

GS_INSTRUCTIONS is set per-episode based on `IsEpisodeAvailable()` - "teases" goodies.

---

## EGoodieType Enum (FEPGoodies.h)

```cpp
enum EGoodieType {
    GT_IMAGE = 0,   // Static image (bios, concept art)
    GT_MESH,        // 3D model viewer (units)
    GT_FMV,         // Video cutscene
    GT_LEVEL,       // Race level unlock
    GT_CHEAT        // Cheat unlock
};
```

---

## TOTAL_DISPLAYABLE_GOODIES = 233 (Retail Correction)

Retail UI behavior surfaces goodies 0-232 (233 total). The goodies[] array still has extra placeholders, and only 232 `goodie_XX_res_PC.aya` resource files exist:
- Indices 0-78: Specific unlock conditions (79 items)
- Indices 79-200: Concept art (122 items, share GOODIES_79 text ID)
- Indices 201-232: FMV cutscenes (32 displayable slots; slot 232 maps to cutscene 33)

**Note**: Game folder contains 232 goodie resource files (`goodie_00_res_PC.aya` through `goodie_231_res_PC.aya`). Slot 232 is still displayable in retail as an FMV mapping and is not an extra `goodie_232_res_PC.aya` resource.

**Save file storage (CGoodie[300])**:
- The `.bes` file stores **300** 32-bit entries. Historical aligned view base is `0x1F44`; true dword base is `0x1F46`.
- Indices **0–232** map to retail-displayable content; indices **233–299** are reserved and must be preserved.
- Patchers should write using the **true dword view** offsets and set the raw state value (`0/1/2/3`) directly.

**Goodie Grid Layout:**

| Row | X Range | Goodie Index | Content |
|-----|---------|--------------|---------|
| 0 | 0-7 | 0-7 | Character Bios |
| 0 | 8-12 | 66-70 | Race Levels |
| 0 | 13-17 | 74-78 | Developer Items |
| 1 | 0-57 | 8-65 | Units (BE + enemies) |
| 2 | 0-31 | 201-232 | FMV Cutscenes |
| 3 | 0-122 | 79-200 | Concept Art |

---

## Complete Goodies Unlock Conditions (FEPGoodies.cpp Analysis - Dec 2025)

### Character Bios (0-7) - SEQUENTIAL CHAIN REQUIRED

| Index | Character | Unlock Condition |
|-------|-----------|------------------|
| 0 | Hawk | Complete Level 100 |
| 1 | Tatianna | Level 110 >= C-Grade |
| 2 | Kramer | Goodie 1 unlocked + Level 200 >= C |
| 3 | Lorenzo | Goodie 2 unlocked + Level 231/232 >= C |
| 4 | Tara | Goodie 3 unlocked + Level 321/322 >= C |
| 5 | Billy | Goodie 4 unlocked + Level 321/322 >= C |
| 6 | Carver | Goodie 5 unlocked + Level 621/622 >= C |
| 7 | Surt | Goodie 6 unlocked + Level 741/742 >= C |

**CRITICAL**: Cannot unlock later bios without first unlocking all previous ones!

From FEPGoodies.cpp:
```cpp
if (COMPLETE_LEVEL(100)) SET_GOODIE_NEW(0);  // Hawk
if (GOODIE_UNLOCKED(1) && GRADE(200) >= C) SET_GOODIE_NEW(2);  // Kramer requires bio 1
// ...continues chaining through bio 7 (Surt)
```

### Battle Engine Units (8-11)

| Index | Content | Unlock |
|-------|---------|--------|
| 8 | BE v1 | Complete 100 |
| 9 | BE v2 | Complete 211/212 |
| 10 | BE v3 | Complete 400 |
| 11 | BE v4 | Complete 710 |

### Kill-Based Unit Goodies (33-57)

| Index | Category | Threshold | Content |
|-------|----------|-----------|---------|
| 33 | Infantry | 40 | Muspell Grunt |
| 34 | Infantry | 160 | Firebreather |
| 35 | Infantry | 80 | Commando |
| 36 | Aircraft | 25 | ATF |
| 37 | Aircraft | 100 | Bomber |
| 38 | Aircraft | 50 | Ground Attack |
| 39 | Aircraft | 75 | Dropship |
| 40 | Aircraft+Infantry | 25+80 | Dropship v2 |
| 41 | Aircraft+Infantry | 50+100 | M Light Tank |
| 42 | Vehicles | 100 | M Tank |
| 43 | Vehicles | 400 | SAM Launcher |
| 44 | Vehicles | 300 | Artillery |
| 45 | Vehicles | 200 | M Truck |
| 47 | Mechs | 20 | Gunwalker |
| 48 | Mechs | 40 | Gunwalker 2 |
| 49 | Mechs | 80 | Guncrab |
| 51 | Mechs | 40 | Arachnid |
| 53 | Emplace+Aircraft | 50+25 | SAM Turret (M) |
| 54 | Emplacements | 50 | Laser Turret |
| 55 | Emplacements | 25 | MG Turret |
| 56 | Emplace+Vehicles | 75+100 | Artillery Turret |
| 57 | Emplace+Aircraft | 25+25 | Flak Turret |

### Boss Units (58-65)

| Index | Boss | Unlock |
|-------|------|--------|
| 58 | Thunderhead | Level 331/332 >= A |
| 59 | Warspite | Level 431/432 >= A |
| 60 | Submarine | Complete 523/524 |
| 61 | Hive | Level 521/522 >= A |
| 62 | Gill-M | Level 523/524 >= A |
| 63 | Carver's Plane | 100 aircraft + Level 621/622 >= C |
| 64 | Fenrir | Level 731/732 >= A |
| 65 | Sentinel | Level 800 >= A |

### Race Levels (66-70)

| Index | World | Unlock |
|-------|-------|--------|
| 66 | 901 | 26+ A-Grades (via TK_HACK_AGRADES) |
| 67-70 | 902-905 | **SCRIPTED** (not unlock function) |

```cpp
case 66: return(901);  // Race 1
case 67: return(902);  // Race 2
case 68: return(903);  // Race 3
case 69: return(904);  // Race 4
case 70: return(905);  // Race 5
```

### Developer Items (74-78) - S-GRADE BASED

| Index | Content | S-Grades Required |
|-------|---------|-------------------|
| 74 | Ashley (Dev photo) | 20 |
| 75 | Foresti High FMV | 40 |
| 76 | Team Photo | 43 (ALL levels!) |
| 77 | Dev Video "UsTheMovie" | 43 |
| 78 | Unknown (S-grade unlock) | 43 |

**Note**: Goodie 78 was undocumented in source comments but uses `CGoodieData(GOODIES_78, -1, 43, -1, TK_HACK_SGRADES)` - same 43 S-grade requirement as goodie 77.

### Concept Art (79-200)

- 79-120: C-Grade tier (one per level)
- 121-163: B-Grade tier (one per level)
- 164-200: A-Grade tier (one per level)

### FMV Cutscenes (201-232)

- NOT unlocked via UpdateGoodieStates()
- Unlocked at **runtime** when the cutscene is watched during gameplay
- Runtime handlers: `CGame__RunIntroFMV` (0x0046d890) and `CGame__RunOutroFMV` (0x0046d9f0) set `g_Career_mGoodies[cutscene+200]` to `GS_NEW` when not already `GS_NEW/GS_OLD`.

**FMV slot 232 maps to cutscene file 33** - Gap in sequence (no cutscene 32 file).

**6 FMVs are NOT localized:** 209, 212, 213, 214, 215, 216 (likely action sequences).

### Scripted Goodies (unlocked via mission scripts, not kill/grade)

- **Indexing nuance:** Mission scripts call `GetGoodieState(index)` / `SetGoodieState(index,state)` with **1-based** indices (verified in `BEA.exe` via `IScript__GetGoodieState` / `IScript__SetGoodieState`). That means: `script_index = save_goodie_index + 1`; `save_file_offset = 0x1F46 + (script_index - 1) * 4`; and `script_index = 0` is invalid (would underflow and scribble into the last `CCareerNodeLink` dword).

- 50: Gnat mech
- 52: M Battleship v2
- 67-70: Race levels 902-905
- Script call sites (1-based indices): `SetGoodieState(51, ...)` (goodie 50) in `game/data/MissionScripts/level521/LevelScript.msl` and `.../level522/LevelScript.msl`; `SetGoodieState(53, ...)` (goodie 52) in `game/data/MissionScripts/level421/Level421script.msl` and `.../level422/Level422script.msl`; `SetGoodieState(68..71, ...)` (goodies 67..70) in `game/data/MissionScripts/level901..904/LapMonitor.msl`.

### Additional Discoveries

**Goodie 46 is unlockable**: `CCareer::UpdateGoodieStates()` unlocks it via `COMPLETE_LEVEL(500)` (matches BEA.exe `CCareer__UpdateGoodieStates` disassembly; see `0x0041d6a4` writing `this+0x1FFC`).

**A-grade counting includes S-grades:**
```cpp
if (CGrade(...) >= a_grade) found++;  // Uses >=, not ==
```
So "26 A-grades" means "26 missions at A or better" including S-ranks.

**Cheat code bypasses save state at runtime:**
```cpp
if (ischeatactive) return(GS_OLD);  // All goodies appear unlocked!
```
In Steam retail, the `MALLOY` cheat overrides goodie state at runtime in memory (not by patching). The older `105770Y2` code is from internal/source-era builds.

---

## Kill-Based Unlocks (Source of Truth)

Kill-based unlocks are represented as explicit `CGoodieData(...)` entries in `references/Onslaught/FEPGoodies.cpp` and are recalculated by BEA.exe in `CCareer__UpdateGoodieStates` (`0x0041c470`).

Use the tables above (Kill-Based Unit Goodies, Boss Units, Race Levels, Developer Items) rather than trying to infer additional "kill buckets" that are not present in the `goodies[]` table.

---

## Episode Availability Controls MP Levels

From Career.cpp - this explains why some MP levels require campaign progress:

```cpp
BOOL CCareer::IsEpisodeAvailable(SINT ep) {
    switch (ep) {
        case 0: case 1: return TRUE;  // Always available
        case 2: return COMPLETE_LEVEL(110);
        case 3: return COMPLETE_LEVEL(231) || COMPLETE_LEVEL(232);
        case 4: return COMPLETE_LEVEL(331) || COMPLETE_LEVEL(332);
        case 5: return COMPLETE_LEVEL(431) || COMPLETE_LEVEL(432);
        case 6: return COMPLETE_LEVEL(521-524);  // Any of four
        case 7: return COMPLETE_LEVEL(621) || COMPLETE_LEVEL(622);
        case 8: return COMPLETE_LEVEL(741) || COMPLETE_LEVEL(742);
    }
}
```

---

## Critical Bug Fix: Goodie 228 Overlap

**Problem**: Offset 0x22D4 was documented as `mCareerInProgress` flag, but it's actually Goodie 228!

```
Legacy aligned view (deprecated):
GOODIE_BASE_ALIGNED = 0x1F44
Goodie 228 *appears* at 0x1F44 + (228 x 4) = 0x22D4  (misaligned by 2 bytes)

True dword view (authoritative):
GOODIE_BASE_TRUE = 0x1F46
Goodie 228 is at 0x1F46 + (228 x 4) = 0x22D6
mCareerInProgress is at 0x248A (file) / 0x2488 (CCareer)
```

Writing `buf[0x22D4] = 1` after writing goodies corrupted Goodie 228 from `0x00020000` to `0x00020001`.

**Solution**:
- Patch goodies using the **true dword view** offsets (base `0x1F46`, raw states `0/1/2/3`).
- If you must patch `mCareerInProgress`, patch it at `0x248A` (true view), not `0x22D4`.
