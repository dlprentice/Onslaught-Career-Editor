# Career System

> Analysis from Career.cpp/h, Array.h, and Controller.cpp - December 2025

## Overview

The Career system manages player progression through the campaign, tracking mission completion, ranks, unlocked goodies, and per-player settings. This is the primary persistent data saved to `.bes` files.

---

## Source Code Constants (Career.h)

Key constants that define the structure of career save files:

| Constant | Value | Notes |
|----------|-------|-------|
| `MAX_NODES` | 100 | Career node slots |
| `MAX_LINKS` | 200 | MAX_NODES × 2 |
| `MAX_NUM_GOODIES` | 300 | Goodie slots |
| `MAX_CAREER_SLOTS` | 32 | Tech slots (bitmap) |
| `NUM_LEVELS` | 43 | Actual campaign missions |
| `BASE_THINGS_EXISTS_SIZE` | 288 | Bits for objective tracking |
| `BASE_THINGS_EXISTS_MEM_REQ` | 9 | 288>>5 = 9 ints (36 bytes) |
| `NUM_LANGUAGES` | 5 | Localization count |
| `CAREER_VERSION` | 9 | Internal build version |

Many of these constants align between the source snapshot (internal build) and the retail/Steam build, but this is not a blanket 1:1 guarantee for persistence behavior. For the retail `.bes` format, many values only *look* “shift-16” in 4-byte aligned hex dumps because `BEA.exe` copies `CCareer` bytes from/to `file + 2` after a 16-bit version word (misaligned view).

---

## Console Version Stamp Formula

The version stamp saved to `.bes` files is calculated using this formula:

```cpp
static SWORD current_version_stamp() {
    return SWORD(CAREER_VERSION + (sizeof(CCareer) << 4));
}
// With CAREER_VERSION=9, this creates the 16-bit version word 0x4BD1
// (the first 4 bytes often *look* like 0x00004BD1 in hex dumps if the next 16 bits are zero).
```

**Notes (Feb 2026):**
- The retail/Steam `.bes` validates only the first **2 bytes** as the version word (`0x4BD1`).
- The source formula explains the provenance of the value, but the retail build effectively treats it as a 16-bit stamp.
- The retail save layout is not a simple `[stamp][sizeof(CCareer)]` blob: `CCareer` bytes start at `file+2` and the file tail includes persisted options entries plus a fixed 0x56-byte snapshot block.

---

## CSArray Template (Array.h)

**Critical insight**: `CSArray<T, size>` is just a thin wrapper around `T mItems[size]` with no vtable or metadata. This strongly explains the contiguous `CCareer` region in retail saves, but the full retail `.bes` envelope still includes extra options/tail blocks beyond that core struct dump.

```cpp
template <class T, int size>
class CSArray {
public:
    T mItems[size];  // That's it - just the array
    // ... methods for bounds checking, iteration
};
```

**Implication for Save Files:**

When the source code declares:
```cpp
CSArray<CCareerNode, MAX_NODES> mNodes;
CSArray<CCareerNodeLink, MAX_LINKS> mLinks;
CSArray<CGoodie, MAX_NUM_GOODIES> mGoodies;
```

The core CCareer region in retail saves contains:
```
CCareerNode[100] → 6400 bytes (100 × 64)
CCareerNodeLink[200] → 1600 bytes (200 × 8)
CGoodie[300] → 1200 bytes (300 × 4)
```

No array length prefix, no padding - just contiguous struct data within the CCareer core; retail `.bes` files also include options entries and tail snapshot blocks beyond this core.

---

## Level Structure Table

`level_structure[43][5]` defines the campaign tree as a directed graph:

| Field Index | Purpose |
|-------------|---------|
| `[0]` | World Number |
| `[1]` | Lower child node index |
| `[2]` | Higher child node index (-1 if none) |
| `[3]` | World to update if PRIMARY complete |
| `[4]` | World to update if SECONDARY complete |

**Higher child unlocks ONLY when ALL secondary objectives complete.**

### Sample Level Structure

43 actual levels, structured as a directed graph:

| Index | World | Lower Child | Higher Child | Notes |
|-------|-------|-------------|--------------|-------|
| 0 | 100 | 1 | -1 | Training |
| 1 | 110 | 2 | -1 | Tutorial |
| 2 | 200 | 3, 4 | - | Episode 2 start |
| ... | ... | ... | ... | ... |
| 42 | 800 | -1 | -1 | Final level |

The "Higher" link (alternate path) unlocks when all secondary objectives are completed on a mission.

**Key Mechanic:**
- Completing primary objectives unlocks the "Lower" child
- Completing ALL secondary objectives unlocks the "Higher" child (alternate/harder path)
- This creates branching campaign progression

---

## World 500 Special Branching

World 500 has unique branching logic based on tech slots (NOT secondary objectives):

```cpp
if (END_LEVEL_DATA.mWorldFinished == 500) {
    if (GetSlot(SLOT_500_ROCKET) && link == higher_link) complete = TRUE;
    if (GetSlot(SLOT_500_SUB) && link != higher_link) complete = TRUE;
}
```

**Tech Slot Constants:**
- `SLOT_500_ROCKET` = 61 (took higher/rocket path)
- `SLOT_500_SUB` = 62 (took lower/submarine path)

This means World 500 remembers which path the player took and gates progression accordingly. In retail `.bes` files, tech slots are stored as a 32-bit bitmap at offset **0x240A** (128 bytes = 32 ints; true-view mapping `file_off = career_off + 2`).

**Tech Slot Bit Manipulation:**
```cpp
// Set a slot
mSlots[slot >> 5] |= (1 << (slot & 31));

// Check a slot
BOOL GetSlot(int slot) {
    return (mSlots[slot >> 5] & (1 << (slot & 31))) != 0;
}
```

**No shift-16 encoding** - tech slots use standard bit manipulation.

---

## Link Type: CN_COMPLETE_BROKEN

When a node is reached via multiple paths, alternate paths are marked `CN_COMPLETE_BROKEN` (value 2) to indicate they're no longer the active route.

**Link Completion States:**

| Value | Constant | Meaning |
|-------|----------|---------|
| 0 | `CN_NOT_COMPLETE` | Link not yet traversed |
| 1 | `CN_COMPLETE` | Link successfully traversed |
| 2 | `CN_COMPLETE_BROKEN` | Alternate path (node reached via different link) |

This is beyond the documented binary complete/incomplete states and explains why some links in save files have value 2 in their link-state field (legacy 4-byte-aligned dumps may show it in the “upper 16 bits” due to the 2-byte misalignment).

---

## Per-Player Career Settings

From `Controller.cpp`, the internal build stores some settings PER-PLAYER in the career:

```cpp
CAREER.SetInvertYAxis(player, val);  // Y-axis look inversion
CAREER.GetVibration(player);         // Controller vibration on/off
```

**Struct Layout from Career.h:**
```cpp
CSArray<BOOL, 2> mIsGod;                    // 8 bytes (per player)
CSArray<BOOL, 2> mInvertYAxis;              // 8 bytes
CSArray<BOOL, 2> mVibration;                // 8 bytes
CSArray<int, 2> mControllerConfigurationNum; // 8 bytes
```

**Retail/Steam note (Feb 2026):**
- Current Steam-build evidence identifies `mCareerInProgress`, `mSoundVolume`, `mMusicVolume`, `g_bGodModeEnabled`, per-player invert-Y toggles (flight/jet + walker), `mVibration[2]`, and `mControllerConfigurationNum[2]` in the fixed CCareer region of retail/Steam `.bes` files (true view offsets `0x248A..0x24BA`).
- Retail startup defaults for these fields are set by `CCareer__StaticInitDefaults` (`0x0041b6a0`, `g_InitFuncTable[3]`): sound/music `0.8/0.9`, vibration/config `1`, invert-Y `0`. These values align with Stuart’s `CCareer::CCareer()` defaults.
- Stuart’s internal build includes `mPendingExtraGoodies`, but we have **not** found a standalone persisted dword for it in the Steam build’s fixed CCareer region; earlier docs incorrectly labeled `0x24BA` as pending extra goodies (it is used as Player 2 controller config in retail).
- `mIsGod[2]` exists in the internal build source, but the Steam build does **not** appear to persist per-player god flags in the save; older writeups that labeled file offsets `0x249A/0x249E` as `mIsGod[]` were incorrect (those dwords are used for invert-Y settings in the retail binary/UI).
- Separate from CCareer, the retail `.bes` also contains a fixed-size options entries block (16 slots; active/used count can vary) and a fixed 0x56-byte tail snapshot holding additional global settings.
- Do not assume any “shift-16 encoding” in retail `.bes`; that behavior came from interpreting the file at 4-byte aligned offsets even though the `CCareer` blob begins at `file + 2`. Use the true view mapping: `file_off = 0x0002 + career_off`.

Authoritative retail offsets and the current “known/unknown” map live in:
- [../../save-file/save-format.md](../../save-file/save-format.md)
- [../../game-mechanics/god-mode.md](../../game-mechanics/god-mode.md)

---

## Relevance to Save Editing

**DIRECT (core semantics), WITH CAVEAT** - The Career system defines most save semantics, but retail `.bes` persistence is not a strict 1:1 replay of the internal source layout.

Understanding the Career system is critical because:

1. **Save File Layout**: CSArray explains contiguous layout in the core `CCareer` region (retail adds options/tail data outside that core)
2. **Version Detection**: The version stamp formula explains the 16-bit version word `0x4BD1` at offset `0x0000` (the first 4 bytes often *look* like `0x00004BD1` if the next 16 bits are zero)
3. **Tech Slots**: World 500 branching explains why slots 61/62 matter
4. **Link States**: CN_COMPLETE_BROKEN explains value 2 in link data
5. **Per-Player Settings**: Explains which settings exist in the internal build (retail persistence may differ)
6. **Level Structure**: The directed graph determines valid progression paths

**Key Discovery (retail/Steam):** many values only *look* like “shift-16” in 4-byte-aligned hex dumps because the serialized `CCareer` bytes begin at `file + 2` after a 16-bit version word. The bytes themselves are raw dwords; the apparent shift is a misaligned view.

---

## Files Analyzed

| File | Purpose |
|------|---------|
| `Career.cpp` | CCareer implementation, save/load, version stamp |
| `Career.h` | CCareer class definition, constants, struct layouts |
| `Array.h` | CSArray template - confirms flat binary layout |
| `Controller.cpp` | Per-player settings integration |

---

## See Also

- [../../save-file/save-format.md](../../save-file/save-format.md) - Complete .bes file structure
- [../../game-mechanics/god-mode.md](../../game-mechanics/god-mode.md) - God mode flag analysis
- [../../save-file/save-format.md](../../save-file/save-format.md) - Save file offset reference
- [../io/storage-system.md](../io/storage-system.md) - Save/load implementation

---

*Last updated: February 2026*
