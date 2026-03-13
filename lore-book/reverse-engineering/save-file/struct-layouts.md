# Struct Layouts Reference
> Complete memory map of BES save file format
> Compiled December 2025 from Ghidra analysis, source code, and testing

## BES File Structure (Steam Build, Fixed 10,004 Bytes)

```
+--------+------+-----------------------------------------+
| Offset | Size | Content                                 |
+--------+------+-----------------------------------------+
| 0x0000 |    2 | Version word (0x4BD1)                   |
| 0x0002 |    4 | new_goodie_count (CCareer +0x0000)      |
| 0x0006 | 6400 | CCareerNode[100] (64 bytes each)        |
| 0x1906 | 1600 | CCareerNodeLink[200] (8 bytes each)     |
| 0x1F46 | 1200 | CGoodie[300] (4 bytes each)             |
| 0x23F6 |   20 | Kill counters[5] (5 dwords)             |
| 0x240A |  128 | mSlots[32] tech slots (4 bytes each)    |
| 0x248A |    4 | mCareerInProgress                       |
| 0x248E |    4 | mSoundVolume (float)                    |
| 0x2492 |    4 | mMusicVolume (float)                    |
| 0x2496 |    4 | g_bGodModeEnabled (CCareer +0x2494)     |
| 0x249A |    4 | (unknown / unused in Steam)             |
| 0x249E |    4 | Invert Y (Flight/Jet) - Player 1        |
| 0x24A2 |    4 | Invert Y (Flight/Jet) - Player 2        |
| 0x24A6 |    4 | Invert Y (Walker) - Player 1            |
| 0x24AA |    4 | Invert Y (Walker) - Player 2            |
| 0x24AE |    4 | mVibration[0] - Player 1                |
| 0x24B2 |    4 | mVibration[1] - Player 2                |
| 0x24B6 |    4 | mControllerConfigurationNum[0] - P1     |
| 0x24BA |    4 | mControllerConfigurationNum[1] - P2     |
| 0x24BE | 0x20*16 (retail/Steam observed; general formula 0x20*N) | Options entries (N is enabled-entry count in save-size logic) |
| file_size-0x56 | 86 | Tail globals snapshot (OptionsTail_Write) |
+--------+------+-----------------------------------------+
| TOTAL  | 10,004 bytes (0x2714) | Steam build observed fixed size (do not resize) |
+--------+------+-----------------------------------------+
```

**Header note (Feb 2026)**: Ghidra shows `CCareer__Save` writes a **16-bit version word** and copies CCareer bytes into `dest + 2`. That makes the “true” dword boundaries in the file land at offsets where `file_offset % 4 == 2` (nodes start at `0x0006`).

**Options entries note (Feb 2026)**: The `0x24BE` options entries block is persisted **control bindings** (two binding slots per action), not arbitrary settings. See `reverse-engineering/save-file/save-format.md` and `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md`.

**Steam load semantics note (Mar 2026)**: options entries + tail are applied on `defaultoptions.bea` load (`CCareer::Load` flag=0) and skipped on career `.bes` load (`flag=1`).

**Controller config note (Feb 2026)**: `mControllerConfigurationNum[0/1]` values `1..4` select one of four controller layouts (analog stick mapping + Morph/Jets button swap). See `reverse-engineering/source-code/frontend/controller-system.md` and retail evidence notes in `reverse-engineering/save-file/save-format.md`.

---

## CCareerNode (64 bytes each)

```c
struct CCareerNode {
    /* +0x00 */ uint32_t state;           // Flags/legacy (not fully mapped). Preserve unless experimenting.
    /* +0x04 */ uint32_t mComplete;       // Raw BOOL/int (0/1 observed in retail saves)
    /* +0x08 */ int32_t  mLowerLink;      // Link index (into CCareerNodeLink[200])
    /* +0x0C */ int32_t  mHigherLink;     // Link index (into CCareerNodeLink[200])
    /* +0x10 */ int32_t  mWorldNumber;    // Level ID (100, 110, 200...)
    /* +0x14 */ int32_t  mBaseThingsExists[9];  // 288 persistence bits (level-specific; preserve)
    /* +0x38 */ int32_t  mNumAttempts;    // Attempt counter
    /* +0x3C */ uint32_t mRanking;        // Raw IEEE-754 float bits (see table below)
};
// Total: 64 bytes
```

### Ranking Encoding (True View)

In the retail/Steam build, `mRanking` is stored directly as raw IEEE-754 float bits at `+0x3C` (no split-float on disk; that was the legacy misaligned view).

| Rank | Float | Bits |
|------|-------|------|
| S | 1.0 | 0x3F800000 |
| A | 0.8 | 0x3F4CCCCD |
| B | 0.6 | 0x3F19999A |
| C | 0.35 | 0x3EB33333 |
| D | 0.15 | 0x3E19999A |
| E | 0.0 | 0x00000000 |
| NONE | -1.0 | 0xBF800000 |

### mBaseThingsExists[9] - Objective State Tracking

The 288 bits (9 × 32-bit ints = 36 bytes) at offset +0x14 track which "base things" (objectives/objects) exist for each mission.

**From Career.cpp:**
```cpp
#define BASE_THINGS_EXISTS_SIZE 288  // must be a multiplier of 32
#define BASE_THINGS_EXISTS_MEM_REQ (BASE_THINGS_EXISTS_SIZE >> 5)  // = 9 ints

// Bit manipulation:
int i = offset >> 5;      // Which int (0-8)
int b = offset & 31;      // Which bit (0-31)
int m = 1 << b;
return ((mBaseThingsExists[i] & m) != 0);
```

**Purpose**: When a level is completed, `UpdateBaseWorldExistsStuffForNode()` copies `END_LEVEL_DATA.mBaseThingsLeft[]` into this field. Each bit represents a specific object/objective in the level.

**Pattern observations**:
- `0xFFFFFFFF...` = All bits set = Level not played or all objectives preserved
- Mixed patterns = Level played, some objectives destroyed

**Important**: DO NOT modify this field - it contains level-specific objective state that the game tracks.

---

## CCareerNodeLink (8 bytes each)

```c
struct CCareerNodeLink {
    /* +0x00 */ uint32_t mLinkType;  // ECNLinkType (raw; 0/1/2 observed in retail saves)
    /* +0x04 */ int32_t  mToNode;    // Destination node index (0xFFFFFFFF for unused)
};
// Total: 8 bytes
```

### Link Type Values

| Value | Meaning |
|-------|---------|
| 0x00000000 | NOT_COMPLETE |
| 0x00000001 | COMPLETE |
| 0x00000002 | COMPLETE_BROKEN |

`COMPLETE_BROKEN` is a campaign-graph bookkeeping state: when a link to a node becomes `COMPLETE`, the game walks the destination node’s *other* parent links and downgrades any other `COMPLETE` parent links to `COMPLETE_BROKEN` so only the active route remains “solid” in the mission tree UI. (Source: `references/Onslaught/Career.cpp` `CCareer::ReCalcLinks()`.)

Retail unlock gate note (Steam `BEA.exe`):
- `Career_IsWorldUnlocked` (`0x00461a50`) treats a world as unlocked if **any parent link** has `mLinkType == COMPLETE (1)`. A node with only `COMPLETE_BROKEN (2)` parent links will be treated as locked. See `reverse-engineering/save-file/career-graph.md`.

**Note**: Other `mLinkType` values may exist; preserve unknown values unless intentionally overriding.

---

## CGoodie (4 bytes each)

```c
struct CGoodie {
    /* +0x00 */ uint32_t state;  // EGoodieState (raw 0/1/2/3 in true dword view)
};
// Total: 4 bytes
```

### Goodie State Values

| Value (true view) | Legacy aligned view | State | Display |
|-------------------|---------------------|-------|---------|
| 0x00000000 | 0x00000000 | GS_UNKNOWN | Locked |
| 0x00000001 | 0x00010000 | GS_INSTRUCTIONS | Shows unlock hints |
| 0x00000002 | 0x00020000 | GS_NEW | Gold badge |
| 0x00000003 | 0x00030000 | GS_OLD | Blue badge |

**HISTORICAL BUG WARNING**: Early patching attempts wrote a progress flag at offset `0x22D4`, corrupting goodie state. In the legacy aligned view, `0x22D4` is **Goodie 228** (`0x1F44 + 228×4`). In the true view, goodie states start at `0x1F46` and Goodie 228 is at `0x22D6`. `mCareerInProgress` is at `0x248A` (file) / `0x2488` (CCareer).

---

## Kill Counters (20 bytes total)

```c
struct KillCounters {
    /* 0x23F6 */ uint32_t aircraft;     // packed: (meta<<24) | (kills & 0x00FFFFFF)
    /* 0x23FA */ uint32_t vehicles;     // packed
    /* 0x23FE */ uint32_t emplacements; // packed
    /* 0x2402 */ uint32_t infantry;     // packed
    /* 0x2406 */ uint32_t mechs;        // packed
};
```

**Important (Feb 2026):** BEA.exe bulk-copies CCareer from `source + 2`, so the **true in-memory dwords** for these counters live at file offsets `0x23F6/0x23FA/0x23FE/0x2402/0x2406`. The binary uses:
- `kills_payload = (dword & 0x00FFFFFF)` (24-bit integer count)
- `meta = (dword >> 24)` (top byte; clamped for the first two counters on load)

**Legacy aligned-view note:** If you view the file at 4-byte aligned offsets (`file_off % 4 == 0`), you’ll see these counters “starting” at `0x23F4` due to the 2-byte header shift. Do not interpret that view as an actual `value << 16` encoding.

### Goodie Unlock Thresholds

| Category | Index | Thresholds |
|----------|-------|------------|
| Aircraft | 0 | 25, 50, 75, 100 |
| Vehicles | 1 | 100, 200, 300, 400 |
| Emplacements | 2 | 25, 50 (75 appears only in combined unlocks) |
| Infantry | 3 | 40, 80, 160 (no standalone 120-based goodie in this build) |
| Mechs | 4 | 20, 40, 80 (40 is used by 2 goodies) |

---

## Tech Slots mSlots[32] (128 bytes)

```c
uint32_t mSlots[32];  // CCareer offset 0x2408 (file offset 0x240A in true dword view)
```

### Bit Addressing

**Range**: Source (`references/Onslaught/Career.cpp`) enforces `0 <= slot < MAX_CAREER_SLOTS * 8` (32 * 8 = 256). Only slots 0-255 are used; the save still reserves 32 dwords (1024 bits).

**On-disk offset nuance**: BEA.exe bulk-copies CCareer from `source + 2`, so the **true on-disk dword boundary** for `mSlots[0]` is `0x240A` (CCareer offset `0x2408` + 2). The historical 4-byte-aligned view at `0x2408/0x240C/...` is 2 bytes earlier and will mislead bit numbering.

```c
// To set slot N:
mSlots[N >> 5] |= (1 << (N & 31));

// To test slot N:
bool is_set = (mSlots[N >> 5] & (1 << (N & 31))) != 0;
```

### Known Slot Meanings

Slot IDs are *script-defined persistent flags*, not a single fixed “tech unlock” enum.

Primary source of truth: retail mission scripts (`game/data/MissionScripts/onsldef.msl`), plus per-level scripts that call `GetSlot` / `SetSlot` / `SetSlotSave`.

Observed in real saves so far (true dword view): `11`, `40`, `62`, `63..66`.

| Slot | Script Macro | Notes |
|------|-------------|-------|
| 1 | `SLOT_F_731_TURRET_1` | Fenrir (world 731) component |
| 2 | `SLOT_F_731_TURRET_2` | Fenrir (world 731) component |
| 3 | `SLOT_F_731_TURRET_3` | Fenrir (world 731) component |
| 4 | `SLOT_F_731_TURRET_4` | Fenrir (world 731) component |
| 5 | `SLOT_F_731_TURRET_5` | Fenrir (world 731) component |
| 6 | `SLOT_F_731_TURRET_6` | Fenrir (world 731) component |
| 7 | `SLOT_F_731_TURRET_7` | Fenrir (world 731) component |
| 8 | `SLOT_F_731_TURRET_8` | Fenrir (world 731) component |
| 9 | `SLOT_F_731_TURRET_9` | Fenrir (world 731) component |
| 10 | `SLOT_F_731_TURRET_10` | Fenrir (world 731) component |
| 11 | `SLOT_F_731_MAINGUN_11` | Fenrir (world 731) component |
| 12 | `SLOT_F_731_LAUNCHER_12` | Fenrir (world 731) component |
| 13 | `SLOT_F_731_LAUNCHER_13` | Fenrir (world 731) component |
| 14 | `SLOT_F_731_LAUNCHER_14` | Fenrir (world 731) component |
| 15 | `SLOT_F_731_LAUNCHER_15` | Fenrir (world 731) component |
| 16 | `SLOT_F_731_LAUNCHER_16` | Fenrir (world 731) component |
| 17 | `SLOT_F_731_LAUNCHER_17` | Fenrir (world 731) component |
| 18 | `SLOT_F_731_BOMBBAY_18` | Fenrir (world 731) component |
| 19 | `SLOT_F_731_BOMBBAY_19` | Fenrir (world 731) component |
| 20 | `SLOT_F_731_BOMBBAY_20` | Fenrir (world 731) component |
| 21 | `SLOT_F_731_BOMBBAY_21` | Fenrir (world 731) component |
| 22 | `SLOT_F_731_BOMBBAY_22` | Fenrir (world 731) component |
| 23 | `SLOT_F_731_BOMBBAY_23` | Fenrir (world 731) component |
| 24 | `SLOT_F_731_ENGINE_24` | Fenrir (world 731) component |
| 25 | `SLOT_F_731_ENGINE_25` | Fenrir (world 731) component |
| 26 | `SLOT_F_731_ENGINE_26` | Fenrir (world 731) component |
| 27 | `SLOT_F_731_ENGINE_27` | Fenrir (world 731) component |
| 28 | `SLOT_F_731_BACKDOOR_TOP_28` | Fenrir (world 731) component |
| 29 | `SLOT_F_731_BACKDOOR_BOT_29` | Fenrir (world 731) component |
| 30 | `SLOT_F_731_FRONTDOOR_30` | Fenrir (world 731) component |
| 31 | `SLOT_F_732_TURRET_1` | Fenrir (world 732) component |
| 32 | `SLOT_F_732_TURRET_2` | Fenrir (world 732) component |
| 33 | `SLOT_F_732_TURRET_3` | Fenrir (world 732) component |
| 34 | `SLOT_F_732_TURRET_4` | Fenrir (world 732) component |
| 35 | `SLOT_F_732_TURRET_5` | Fenrir (world 732) component |
| 36 | `SLOT_F_732_TURRET_6` | Fenrir (world 732) component |
| 37 | `SLOT_F_732_TURRET_7` | Fenrir (world 732) component |
| 38 | `SLOT_F_732_TURRET_8` | Fenrir (world 732) component |
| 39 | `SLOT_F_732_TURRET_9` | Fenrir (world 732) component |
| 40 | `SLOT_F_732_TURRET_10` | Fenrir (world 732) component |
| 41 | `SLOT_F_732_MAINGUN_11` | Fenrir (world 732) component |
| 42 | `SLOT_F_732_LAUNCHER_12` | Fenrir (world 732) component |
| 43 | `SLOT_F_732_LAUNCHER_13` | Fenrir (world 732) component |
| 44 | `SLOT_F_732_LAUNCHER_14` | Fenrir (world 732) component |
| 45 | `SLOT_F_732_LAUNCHER_15` | Fenrir (world 732) component |
| 46 | `SLOT_F_732_LAUNCHER_16` | Fenrir (world 732) component |
| 47 | `SLOT_F_732_LAUNCHER_17` | Fenrir (world 732) component |
| 48 | `SLOT_F_732_BOMBBAY_18` | Fenrir (world 732) component |
| 49 | `SLOT_F_732_BOMBBAY_19` | Fenrir (world 732) component |
| 50 | `SLOT_F_732_BOMBBAY_20` | Fenrir (world 732) component |
| 51 | `SLOT_F_732_BOMBBAY_21` | Fenrir (world 732) component |
| 52 | `SLOT_F_732_BOMBBAY_22` | Fenrir (world 732) component |
| 53 | `SLOT_F_732_BOMBBAY_23` | Fenrir (world 732) component |
| 54 | `SLOT_F_732_ENGINE_24` | Fenrir (world 732) component |
| 55 | `SLOT_F_732_ENGINE_25` | Fenrir (world 732) component |
| 56 | `SLOT_F_732_ENGINE_26` | Fenrir (world 732) component |
| 57 | `SLOT_F_732_ENGINE_27` | Fenrir (world 732) component |
| 58 | `SLOT_F_732_BACKDOOR_TOP_28` | Fenrir (world 732) component |
| 59 | `SLOT_F_732_BACKDOOR_BOT_29` | Fenrir (world 732) component |
| 60 | `SLOT_F_732_FRONTDOOR_30` | Fenrir (world 732) component |
| 61 | `SLOT_500_ROCKET` | World 500 branch gating |
| 62 | `SLOT_500_SUB` | World 500 branch gating |
| 63 | `SLOT_TUTORIAL_1` | Tutorial completion flag |
| 64 | `SLOT_TUTORIAL_2` | Tutorial completion flag |
| 65 | `SLOT_TUTORIAL_3` | Tutorial completion flag |
| 66 | `SLOT_TUTORIAL_4` | Tutorial completion flag |

Evidence (binary, Feb 2026):
- `CCareer__SetSlot` (`0x004214e0`) is invoked by the `SetSlotSave` script handler (`IScript__SetSlotSave` @ `0x00533900`).
- `CGame__GetSlot` (`0x0046d410`) / `CGame__SetSlot` (`0x0046d3a0`) operate on the runtime slot-bitset at `CGame + 0x308` (copied into END_LEVEL_DATA, then persisted into CCareer on LevelWon).
- Command strings `GetSlot` / `SetSlot` / `SetSlotSave` (`0x0064f338` / `0x0064f340` / `0x0064f2c0`) are registered in `FUN_0052ff30`.

---

## God Mode / Invert-Y (Steam Correction)

Older docs (and Stuart’s internal source) refer to a per-player `mIsGod[2]` persistence array. In the Steam build, those same offsets were incorrectly reused in earlier writeups:

- `0x249E/0x24A2/0x24A6/0x24AA` are **invert-Y toggles** (walker + flight/jet per player). Steam stores them as normal booleans: `0 = Off` (default), non-zero = On.
- `0x249A` is always `0` in observed retail saves and is currently treated as **unknown/unused**.

God mode in the Steam build is primarily runtime-cheat gated (save-name substring checks). See `reverse-engineering/game-mechanics/god-mode.md`.

---

## Audio Settings

| Offset | Field | Type |
|--------|-------|------|
| 0x248E | mSoundVolume | float (raw IEEE-754) |
| 0x2492 | mMusicVolume | float (raw IEEE-754) |

---

## Encoding Rules Summary

| Type | Encoding | Example |
|------|----------|---------|
| Integer | Raw little-endian 32-bit at true view offsets (`file_off % 4 == 2`) | 7 -> 0x00000007 |
| Boolean | Raw 0/1 (often stored as 32-bit ints) | TRUE = 0x00000001 |
| Float | Raw IEEE-754 | 0.7f = 0x3F333333 |
| Kill counters | `stored = (meta<<24) | (kills & 0x00FFFFFF)` | 95 kills -> 0x8000005F |
| Slot bits | Standard bit manipulation | `mSlots[i] |= (1 << b)` |

---

## Version Stamp Calculation

```
VERSION_STAMP = BASE_VERSION + 0x4BC0
             = 17 + 19392
             = 19409
             = 0x4BD1
```

The console port uses BASE_VERSION=17. The internal PC build used 9.

---

## Related Documentation

- [save-format.md](save-format.md) - Detailed format analysis
- [../game-mechanics/god-mode.md](../game-mechanics/god-mode.md) - God mode investigation
- [grade-system.md](grade-system.md) - Ranking calculation
- [kill-tracking.md](kill-tracking.md) - Kill categories and thresholds
- [../binary-analysis/functions/_index.md](../binary-analysis/functions/_index.md) - Function catalog
- [../binary-analysis/README.md](../binary-analysis/README.md) - Binary analysis overview

---

*Last updated: February 2026*
