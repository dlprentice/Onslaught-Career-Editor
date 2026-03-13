# BES Save File Format

## Key Insight (Feb 2026): Internal PC Build vs Retail/Steam Build

**Stuart's source code** = Internal PC build used during development (raw ints/floats)
**Steam release** = Later retail build (console-port lineage) with a different on-disk layout than Stuart's internal build

The internal build source is still extremely useful for **struct layouts and logic**, but the save-file bytes you patch must match what the retail `BEA.exe` actually reads/writes.

### “True Dword View” (Authoritative)

Retail `BEA.exe` treats the `.bes` as:
- a **16-bit version word** at file offset `0x0000` (value `0x4BD1`), then
- a bulk copy of `CCareer` bytes starting at `file + 0x0002` (`CCareer::Load/Save` use `source+2` / `dest+2`).

That means:

```text
file_offset = 0x0002 + career_offset
```

Many early docs described a “shift-16 encoding” (`value << 16`) because they were reading the file at 4-byte aligned offsets (`file_offset % 4 == 0`). Since the real dword boundaries are at offsets where `file_offset % 4 == 2`, that 4-byte-aligned view is **misaligned by 2 bytes** and makes small ints *appear* shifted.

### The Full Development Story (from GDM Post-Mortem, April 2003)

The Game Developer Magazine post-mortem (by Ben Carter) reveals the actual development flow:

```
PC Development Build (Stuart's code)
         |
         +---> Xbox Port ---> FINISHED FIRST (shared DirectX code)
         |         |
         |         +---> Windows Retail Release (published by Encore, Oct 2003; port work in-house at Lost Toys per Stuart)
         |                    |
         |                    +---> Steam Release (Ziggurat, 2020)
         |
         +---> PS2 Port ---> FINISHED LAST (complete graphics/sound rewrite)
```

**Key quotes from post-mortem:**

> "Even though we were targeting consoles (specifically the Xbox and Playstation 2) for the final game, **all of our development work was done on the PC**. It wasn't until late in development that we moved the code base over to the two consoles."

> "The Xbox port of the game had the advantage of being based on DirectX, and hence **the majority of the code was shared with the PC version**."

> "The Playstation 2 port, however, required **an entire graphics and sound engine to be coded from scratch**."

> "Until we deliberately split the code bases for final tweaking and testing, **the game could be built on all three supported platforms from one set of project files**."

### Why Values Look “Shift-16” In Hex Dumps

The post-mortem reveals the critical serialization approach:

> "The process relied on an incredibly risky system of **saving objects to disk by writing the entire contents of a C++ class structure** and then manually fixing up pointers and other information when it was reloaded."

This explains why the save looks like a raw class dump.

For the retail build specifically, the key nuance is **not** a fixed-point encoding: it’s that the serialized `CCareer` bytes start at `file+2` (after a 16-bit version), so dword boundaries are shifted by 2 bytes.

### Why Stuart's Source Doesn't Match Retail

1. **Stuart's code** = Pre-console-port PC development build
2. **Console ports** introduced:
   - Different save header/layout (16-bit version + CCareer bytes copied at `file+2`)
   - Struct compaction for memory (PS2 only had **28MB usable RAM**)
   - Possible field reordering for alignment
3. **Retail PC** = Port of Xbox code (not Stuart's original PC build)

### Stuart's Confirmation (Discord, April 2025)
> "I noticed the Career class and .bes file don't completely match which seems to suggest attributes were added to the class in the full PC release version."

He also noted goodies map to bytes `0x1F47` onwards in his testing. In the retail true view, goodies begin at `0x1F46` (legacy aligned view: `0x1F44`). Small offset differences like this are expected between builds.

**From Stuart's April 10, 2025 message**:
- The 'Save' method in Career.cpp does a memory dump of the Career class instance
- Goodie class is enumeration (4 bytes). Retail values are: `0=Unknown`, `1=Instructions`, `2=New`, `3=Old` (verified via `game/data/MissionScripts/onsldef.msl` and `save-attempts/haha-cannon-goes-brrrrr.bes`); Stuart's internal build description used `1..4`.
- Internal/source build stores a god-mode-related boolean in the Career class, but do **not** treat that as retail on-disk proof; retail Steam persistence/gating is documented in `game-mechanics/god-mode.md`
- Display setup in `d3dapp.cpp` and `ltshell.cpp` - hardcoded to **640x480**, assumes **GeForce 3** card

### Does This Explain Our Patching Issues?

| Issue | What We Now Know |
|-------|------------------|
| **“Shift-16 encoding”** | A 2-byte misaligned *view* of the same bytes (true dwords are at `file_off % 4 == 2`). |
| **Offset mismatches** | Retail `BEA.exe` copies `CCareer` from/to `file+2`; map offsets with `file_off = 0x0002 + career_off`. |
| **Level crashes** | Historically caused by patching at the wrong offsets (overlapping adjacent true dwords / unknown fields). |
| **Grade display** | Rank is a raw IEEE-754 float in `CCareerNode.mRanking` (no “split-float” on disk; that was the misaligned view). |
| **mBaseThingsExists** | Still level-specific persistence bits; preserve unless intentionally experimenting. |

**Bottom line**: Stuart's source gives us the *logic* but not the exact *binary layout* of the retail save format. The console porting process modified struct layouts for memory/compatibility reasons.

---

## Aligned View vs True View

Two ways you’ll see offsets/values discussed:

- **True dword view (authoritative)**: treat dwords as starting at offsets where `file_offset % 4 == 2` and use `file_off = 0x0002 + career_off`.
- **Legacy aligned view (deprecated)**: treat dwords as starting at offsets where `file_offset % 4 == 0`. This view is 2 bytes earlier than what `BEA.exe` uses, so values often appear as `value << 16`.

Patchers and docs should use the **true view**.

---

## Source to Port Struct Mapping

### CCareerNode (64 bytes each)

| Offset | Type (Retail) | Name | Notes |
|--------|----------------|------|------|
| +0x00 | uint32 | state | Flags/legacy field; meaning not fully mapped. Preserve unless experimenting. |
| +0x04 | uint32 | mComplete | Raw bool/int (0 or 1 in observed saves). |
| +0x08 | int32 | mLowerLink | Link index into link array. |
| +0x0C | int32 | mHigherLink | Link index into link array. |
| +0x10 | int32 | mWorldNumber | Level ID (100, 110, 200...). |
| +0x14 | int32[9] | mBaseThingsExists | 288 persistence bits (level-specific). Preserve. |
| +0x38 | int32 | mNumAttempts | Attempt counter (often 0 in patched saves). |
| +0x3C | float bits | mRanking | Raw IEEE-754 float bits (e.g., S = `0x3F800000`, NONE = `0xBF800000`). |

### CCareerNodeLink (8 bytes each)

| Offset | Type (Retail) | Name | Notes |
|--------|----------------|------|------|
| +0x00 | uint32 | mLinkType | Link state/type. Observed: `0` (not complete), `1` (complete), `2` (complete-broken alternate parent path). |
| +0x04 | int32 | mToNode | Destination node index (`0xFFFFFFFF` means unused). |

### CGoodie (4 bytes each)

| Value (true view) | Enum | Meaning |
|-------------------|------|---------|
| 0 | GS_UNKNOWN | Locked, no hints |
| 1 | GS_INSTRUCTIONS | Locked, shows unlock hints |
| 2 | GS_NEW | Unlocked, gold badge |
| 3 | GS_OLD | Viewed, blue badge |

---

## File Layout (Steam Build, Fixed 10,004 Bytes) - COMPLETE MAP

| Offset | Size | Content | Status |
|--------|------|---------|--------|
| 0x0000 | 2 | Version word (0x4BD1) | Understood |
| 0x0002 | 4 | `new_goodie_count` (CCareer +0x0000) | Understood |
| 0x0006 | 6400 | CCareerNode[100] (64 bytes x 100) | Understood |
| 0x1906 | 1600 | CCareerNodeLink[200] (8 bytes x 200) | Understood |
| 0x1F46 | 1200 | CGoodie[300] (4 bytes x 300; indices 0-232 displayable, 233-299 reserved/preserve) | Understood |
| 0x23F6 | 20 | Kill counters (5 dwords; lower 24 bits are kill payload, top byte is confirmed metadata for the first two counters; preserve top byte on all five counters conservatively) | Mostly understood |
| 0x240A | 128 | mSlots[32] - Tech slots bit array (32 x 4 bytes = 1024 bits) | Understood |
| 0x248A | 4 | mCareerInProgress | Understood |
| 0x248E | 4 | mSoundVolume | Understood |
| 0x2492 | 4 | mMusicVolume | Understood |
| 0x2496 | 4 | `g_bGodModeEnabled` (CCareer +0x2494) | Understood |
| 0x249A | 4 | (unused/padding) | Observed |
| 0x249E | 4 | Invert Y (Flight/Jet) (P1) | Understood |
| 0x24A2 | 4 | Invert Y (Flight/Jet) (P2) | Understood |
| 0x24A6 | 4 | Invert Y (Walker) (P1) | Understood |
| 0x24AA | 4 | Invert Y (Walker) (P2) | Understood |
| 0x24AE | 4 | mVibration[0] (P1) | Understood |
| 0x24B2 | 4 | mVibration[1] (P2) | Understood |
| 0x24B6 | 4 | mControllerConfigurationNum[0] (P1) | Understood |
| 0x24BA | 4 | mControllerConfigurationNum[1] (P2) | Understood |
| 0x24BE | 0x20 * 16 (retail/Steam observed; general formula 0x20 * N) | Options entries (N = enabled entries in save-size logic) | Observed |
| `file_size - 0x56` | 0x56 | Tail globals/options snapshot (OptionsTail_Write) | Observed |
| **TOTAL** | **10,004 bytes** (`0x2714`) | Steam build observed fixed size (do not resize) | |

**CRITICAL CORRECTION (Dec 2025)**: Offset `0x240C` was previously misidentified as "god mode flag". It is within the tech-slot bitset region (and does **not** correspond to a standalone dword in the true-dword view). See Tech Slots section below for details.

**CRITICAL BUG FIX (Dec 2025)**: Kill counts were previously documented at 0x23A4 - **THIS WAS WRONG!**
- 0x23A4 is inside reserved CGoodie entries 280-284 (legacy aligned-view arithmetic: `0x1F44 + 280*4`)
- The **aligned view** for kill counters begins at 0x23F4 (the **true dword view** begins at 0x23F6)
- **Proof**: `save-attempts/haha-cannon-goes-brrrrr.bes` has 3,221/9,738/3,002/3,953/1,024 kills at 0x23F6 (true view)
- **Proof**: `save-attempts/me-actually-playing-the-game-to-get-ranks.bes` has 95/150/2/151/0 kills at 0x23F6 (true view)
- **Proof**: Writing "kill counts" to 0x23A4 corrupts goodies because 0x23A4 is inside the goodies array region

**Note**: In the true dword view, kill counters are stored as `count | (meta << 24)` and the binary uses `count = (value & 0x00FFFFFF)`. On load, `CCareer__Load` clamps `meta` only for the first two counters (`CCareer+0x23F4` / `CCareer+0x23F8`) and preserves the lower 24 bits.

**Note**: The base CCareer copy is **fixed at 0x24BC bytes** and ends at file offset **0x24BD**. Everything after 0x24BD is the options entries region (16×0x20 bytes) plus a fixed 0x56-byte tail snapshot.

### Header + Size Calculation (Ghidra Feb 2026)

Recent Ghidra analysis adds the following details:

- **Header is a 16-bit version word**: `CCareer__Save` writes a 16-bit version word (`MOV word ptr [EAX], CX`) and copies `0x92F` dwords (`0x24BC` bytes) into `dest + 2`. `CCareer__Load` validates only the 16-bit version word and reads from `source + 2`.
- **On-disk header still looks 4 bytes**: Many retail saves begin with `0x00004BD1` if you read the first 4 bytes as a dword. This is the 16-bit version word (`0x4BD1`) plus the first 16 bits of the next CCareer dword (often zero).
- **Node array starts at 0x0006**: `CCareerNode[0]` begins at `file_off = 0x0002 + 0x0004 = 0x0006`. Older docs that used `0x0004` were using the legacy aligned view.
- **Save size computation**: `CCareer__GetSaveSize` can be expressed as `0x2514 + 0x20 * N`, where `N` is the count of enabled entries in `DAT_008892d8`. For the retail/Steam format targeted by this repo and current tooling, observed and supported files are fixed at `N = 16` (`0x2714`, 10,004 bytes).
- **Tail block is structured**: `OptionsTail_Write` writes a `0x56`-byte block of globals/options into the tail and returns `param + 0x56`. This aligns with the `0x56` added in `GetSaveSize`, indicating the end of the save is a structured options snapshot rather than random data.

**Interpretation (for this repo)**: treat `.bes` as **fixed at 10,004 bytes** and do not resize/reserialize saves. If a future build is observed writing a different size, capture that as a separate build-specific format note before changing tooling.

---

## Reserved / Unmapped Regions (Dec 2025 Investigation)

With the kill-count offset bug fixed (it was writing inside the goodies array at `0x23A4` instead of the kill-counter region), the remaining reserved/unmapped regions were re-analyzed.

**Update (Feb 2026):** The former “CCareerUnknown” block at `0x24A2-0x24BD` is now mostly mapped (per-player invert Y for walker/flight modes, vibration, controller config, plus one legacy/unknown dword). Two previously-unknown dwords are now identified:
- `0x0002-0x0005`: `new_goodie_count` (source name: `new_goodie_count`)
- `0x2496-0x2499`: `g_bGodModeEnabled` (pause-menu god mode toggle state; cheat-gated)

### Tech Slots (mSlots) - CCareer +0x2408 (file 0x240A-0x2489, 128 bytes) - **CORRECTED Dec 2025**

**Location**: Immediately after kill counters (true view counters end at 0x2409)  
**Size**: 128 bytes = 32 x 4-byte integers

This region is a bitset used by `CCareer::GetSlot()` / `CCareer::SetSlot()` in `references/Onslaught/Career.cpp`.

**Important range detail:** The source checks `num < MAX_CAREER_SLOTS * 8`, meaning only **256 slot IDs (0-255)** are used by the game. The save reserves 32 dwords (1024 bits), but only the **first 8 dwords** matter in practice.

**CRITICAL CORRECTION:** Offset `0x240C` was previously misidentified as a "god mode flag". This was WRONG. It's within the tech-slot bitset region. For accurate bit numbering, use the **true dword view** described below.

#### Aligned vs True Dword View

BEA.exe reads/writes dwords at `this + 0x2408` (CCareer offset). Because CCareer bytes are copied from `source + 2`, the **true on-disk dword boundary** is:
- `mSlots[0]` starts at file offset **`0x240A`** (not 0x2408)

If you view the file at the historical 4-byte-aligned offsets (`0x2408`, `0x240C`, ...), you're looking **2 bytes earlier** than the real dword boundaries and you will misinterpret bit positions.

**True dword layout (what BEA.exe uses):**
```
mSlots[0] @ 0x240A  (slots 0-31)
mSlots[1] @ 0x240E  (slots 32-63)
mSlots[2] @ 0x2412  (slots 64-95)
...
mSlots[7] @ 0x2426  (slots 224-255)
```

**Bit Addressing** (from `CCareer::GetSlot/SetSlot`):
```cpp
// To set a slot:
mSlots[slot >> 5] |= (1 << (slot & 31));

// To test a slot:
bool is_set = mSlots[slot >> 5] & (1 << (slot & 31));

// Example: Slot 40
//   slot >> 5 = 40 >> 5 = 1     // mSlots[1]
//   slot & 31 = 40 & 31 = 8     // Bit 8
```

**Source Code Reference** (Mission 500 special-case uses slot flags):
```cpp
if (END_LEVEL_DATA.mWorldFinished == 500) {
    if ((GetSlot(SLOT_500_ROCKET)) && (link == CAREER.GetLink(finished_node->mHigherLink))) {
        complete=TRUE;
    }
    if ((GetSlot(SLOT_500_SUB)) && (link != CAREER.GetLink(finished_node->mHigherLink))) {
        complete=TRUE;
    }
}
```

`SLOT_500_ROCKET` / `SLOT_500_SUB` are the world-500 branch flags:
- `SLOT_500_ROCKET` = **61** (rocket path / higher-link case)
- `SLOT_500_SUB` = **62** (submarine path / lower-link case)

Other script-defined slot IDs (retail scripts `game/data/MissionScripts/onsldef.msl`):
- Fenrir component bits: `SLOT_F_731_*` = `1..30`, `SLOT_F_732_*` = `31..60`
- Tutorial completion flags: `SLOT_TUTORIAL_1..4` = `63..66`

See `reverse-engineering/save-file/struct-layouts.md` for the full slot mapping table.

Evidence:
- Source-level docs: `reverse-engineering/source-code/gameplay/career-system.md`
- Retail/Steam decompile: `CCareer__ReCalcLinks` (`0x0041bdf0`) checks bits 29-30 of `mSlots[1]` which correspond to slots 61/62.

**Observed set slots (true dword view):**
- Gold save (`haha-cannon-goes-brrrrr.bes`): slots `[11, 40, 62, 63, 64, 65, 66]`
- Played save (`me-actually-playing-the-game-to-get-ranks.bes`): slots `[63, 64, 65, 66]`

**Encoding**: Slot bits use standard bit manipulation as shown above. If you view the file at 4-byte aligned offsets, the values may *appear* shifted; that is just the legacy misaligned view.

### Known Fields (True View): 0x248A - 0x24A1 (24 bytes) - **MAPPED Dec 2025**

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x248A | 4 | mCareerInProgress | Raw int/bool |
| 0x248E | 4 | mSoundVolume | IEEE-754 float |
| 0x2492 | 4 | mMusicVolume | IEEE-754 float |
| 0x2496 | 4 | g_bGodModeEnabled | God mode toggle state (pause-menu display; cheat-gated) |
| 0x249A | 4 | (unused/padding) | Observed 0 in sampled retail saves; treat as reserved/unknown and preserve |
| 0x249E | 4 | mInvertYFlightP1 | Player 1 flight/jet invert Y (raw int/bool; 0/1 observed) |

**Note**: These are **file offsets** in the true dword view. The corresponding CCareer offsets are 2 bytes earlier (`career_off = file_off - 0x0002`). God mode is runtime-cheat gated via save-name checks; in the retail build, the pause menu uses `g_bGodModeEnabled` as a toggle state once the cheat is active.

**Steam build nuance (verified in BEA.exe):**
- `CCareer__Load` at `0x00421200` loads only the fixed `0x24BC` CCareer block from `source + 0x0002` (file offset `0x0002`).
- When loading a career `.bes` save, the game calls `CCareer::Load(..., flag=1)` which **preserves** the pre-load values of `mSoundVolume` and `mMusicVolume` by saving them before the memcpy and restoring them after.
- When `flag != 0`, `CCareer::Load` also **skips** applying the persisted options entries (`0x24BE`) and options tail snapshot (`file_size - 0x56`) to runtime globals.
- When `flag == 0` (boot path for `defaultoptions.bea`), `CCareer::Load` copies the options entries starting at `source + 0x24BE` into the in-memory options table (`DAT_008892d8`), then calls `OptionsTail_Read` (`0x00420d70`) on the tail pointer immediately after the entries.
- When you load a career save in the frontend (`CFEPLoadGame__DoLoad` at `0x00461e20`), the game may write `defaultoptions.bea` from the loaded save buffer via `CFEPOptions__WriteDefaultOptionsFile(source, size)` when `DAT_0082b5b0 == 0`.
  - This persists the save’s options entries + tail snapshot for the **next boot** (since boot calls `CCareer::Load(flag=0)` on `defaultoptions.bea`).
  - It does **not** mean keybinds/tail are applied immediately in the current session (the `flag=1` path still skips them).
- When the game later saves career progress (`CCareer__Save` / `CCareer__SaveWithFlag`), it serializes the **current in-memory options table** (loaded at boot from `defaultoptions.bea`) back into the `.bes` buffer.
  - Practical effect: if you load a career save and then trigger a save, the `.bes` file’s options entries/tail can “snap” to whatever your current global options were, even if the `.bes` initially contained different bindings.

### Region 2: 0x24A2 - 0x24BD (28 bytes) - **MAPPED Feb 2026**

**Location**: After known fields, before the options block

These 7 dwords line up exactly with the tail end of Stuart’s `CCareer` layout in `references/Onslaught/Career.h`:

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x24A2 | 4 | mInvertYFlightP2 | Player 2 flight/jet invert Y (raw int/bool; 0/1 observed) |
| 0x24A6 | 4 | mInvertYWalkerP1 | Player 1 walker invert Y (raw int/bool; 0/1 observed) |
| 0x24AA | 4 | mInvertYWalkerP2 | Player 2 walker invert Y (raw int/bool; 0/1 observed) |
| 0x24AE | 4 | mVibration[0] | Player 1 controller vibration toggle (`0=Off`, non-zero=On) |
| 0x24B2 | 4 | mVibration[1] | Player 2 controller vibration toggle (`0=Off`, non-zero=On) |
| 0x24B6 | 4 | mControllerConfigurationNum[0] | Player 1 controller config/preset index |
| 0x24BA | 4 | mControllerConfigurationNum[1] | Player 2 controller config/preset index |

**Observed defaults (gold + played baselines)**:
- `mInvertYFlightP1/P2` and `mInvertYWalkerP1/P2` are `0/1` depending on in-game controller options
  - **Steam build semantics (verified on flight/jet path)**: `0 = Off` (default), non-zero = On.
    - Evidence: `FUN_00407540` (`0x00407540`) applies mouse-look pitch using `if invert == 0 then pitch -= delta else pitch += delta`.
- `mVibration = [1, 1]` (enabled)
- `mControllerConfigurationNum = [1, 1]`
  - Evidence: `CCareer__StaticInitDefaults` (`0x0041b6a0`) sets both controller configs to `1` during startup defaults initialization.

**Controller configuration values (1-4)**:

These values select one of four controller layouts. Source reference: `references/Onslaught/PCController.cpp` (summarized in `reverse-engineering/source-code/frontend/controller-system.md`).

Retail/Steam evidence: `FUN_0047fb50` checks `mControllerConfigurationNum[1]` against `3` and `4`, consistent with configs where Morph/Landing-Jets bindings are swapped.

| Value | Left Stick | Right Stick | Morph | Landing Jets |
|------:|------------|-------------|-------|--------------|
| 1 | Strafe + Forward/Back | Yaw + Pitch | Button 2 | Button 1 |
| 2 | Yaw + Pitch | Strafe + Forward/Back | Button 2 | Button 1 |
| 3 | Strafe + Forward/Back | Yaw + Pitch | Button 1 | Button 2 |
| 4 | Yaw + Pitch | Strafe + Forward/Back | Button 1 | Button 2 |

Recommendation: keep values in `1..4`; other values are undefined in retail/Steam.
Implementation note: current C#/Python patchers accept raw `uint32` values and do not clamp this field automatically.

**Notes**:
- This is distinct from the tail snapshot’s `g_InvertXAxisFlag`, which is a runtime/global flag persisted in the options tail (and affects camera/input handling), not CCareer.
- Because these fields are within the fixed `0x24BC` CCareer copy, they must be preserved when patching unrelated save data.
  - Internal-build note: Stuart’s `CCareer` includes `mPendingExtraGoodies`, but we have **not** identified a standalone persisted dword for it in the Steam build’s fixed CCareer region (earlier docs incorrectly labeled `0x24BA` as pending extra goodies). Treat it as **not persisted / unknown** in retail unless/until a codepath proves otherwise.

### Region 3: Options Block + Tail (Options Entries + Tail Snapshot)

**Location**: Starts immediately after the fixed CCareer copy (which ends at **0x24BD**).

**Steam build behavior (important):** This block is applied by the game when loading `defaultoptions.bea` (`CCareer::Load(flag=0)`), but is **ignored** when loading a career `.bes` save (`CCareer::Load(flag=1)`).

**Structure**:
- **Options entries**: 16 slots (`0x20 * 16` bytes) starting at **0x24BE**. Internally the game tracks an active/used count `N`, but the Steam build save file is observed fixed-size.
- **Tail snapshot**: a fixed **0x56-byte** block written by `OptionsTail_Write`, located immediately after the options entries block.

**Options entries are control bindings** (confirmed by BEA.exe static analysis + decoding on-disk data in `game/defaultoptions.bea` and `save-attempts/*.bes`):
- Each entry is **0x20 bytes** (8 dwords), and stores **two binding slots** for one action.
- On disk they live in the save/options file, not just runtime memory.
- The same 16 entry IDs appear across presets, but bindings differ by preset (see `g_ControlSchemeIndex` below).

**Per-entry layout (8 dwords)**:
- `dword0`: active flag in low byte (non-zero => entry is enabled/serialized by `CCareer__GetSaveSize` logic)
- `dword1`: `entry_id` (sentinel `-1` terminates the in-memory table used by `OptionsEntries__FindById`)
- `dword2..dword4`: slot 0 = `(field0, device_code, packed_key)`
- `dword5..dword7`: slot 1 = `(field0, device_code, packed_key)`

**Packed key encoding**:
- `packed_key = (vk << 16) | scan`
- For letter keys, `vk` matches ASCII/VK (e.g. `W` => `0x57`) and `scan` matches the keyboard scan/DIK-like code (e.g. `0x11`).
- For arrow keys, `vk` is often `0`, while `scan` is set (e.g. left arrow commonly shows `scan=0xCB`).

**Observed entry IDs (retail N=16)**:
`[0x19, 0x1B, 0x1A, 0x1C, 0x1D, 0x1E, 0x1F, 0x20, 0x3B, 0x21, 0x13, 0x12, 0x14, 0x10, 0x11, 0x15]`

**Preset interaction**:
- `g_ControlSchemeIndex` (tail offset `+0x08`, low-16 bits of `0x00677d70`) selects which preset is in effect.
- The same `entry_id` can map to different physical keys depending on the preset (e.g. `scheme=0` vs `scheme=1` observed in saves).

**Steam build note:** The observed retail/Steam saves use `N = 16`, so offsets like `0x26BE` (tail start) are stable in this build. If a different build is observed writing a different `N`, re-evaluate offsets using the size formula before changing tooling.

**Example (N = 16, retail saves)**:
- Options block: `0x24BE - 0x26BD`
- Tail: `0x26BE - 0x2713`

### Recommendations

1. Prefer preserving `new_goodie_count` (`0x0002`) and `g_bGodModeEnabled` (`0x2496`) unless you are validating a specific behavior.
2. **Do NOT modify options entries or tail** unless you are targeting a specific known field.
3. **If crashes persist**: Consider copying the **options entries + tail block** from a gold save (and preserve all CCareer dwords you are not intentionally changing).

---

## Serialization Details from Executable Analysis

From Ghidra analysis of FUN_004213c0:

```
Save Buffer Layout (written by CCareer::SaveToFile):

[0x0000-0x0001] Version word (0x4BD1)
[0x0002-0x24BD] CCareer copy (0x24BC bytes total)
[0x24BE-...]    Options entries (0x20 * N bytes; retail/Steam observed N = 16)
[...-+0x56]     Tail snapshot (0x56 bytes)
```

Total (Steam build): 10,004 bytes (0x2714). Internally computed as `0x2514 + 0x20 * N` with observed `N = 16`.

**Note**: The CCareer copy begins at file offset `0x0002`. `CCareerNode[0]` begins at file offset `0x0006` (`0x0002 + 0x0004`).

### Tail Section Contents (OptionsTail_Write)

The final 86 bytes (0x56) contain a snapshot of runtime globals. Offsets below are **relative to tail start**:

| Offset | Size | Source Global | Notes |
|--------|------|---------------|-------|
| 0x00 | 4 | `g_Options_UnknownFloat0` | Options tail float (default ~0.7) |
| 0x04 | 4 | `g_MouseSensitivity` | Mouse sensitivity scalar (input/camera + UI) |
| 0x08 | 2 | `g_ControlSchemeIndex` | Control preset index (Controls__ApplyPreset) |
| 0x0A | 2 | `g_LanguageIndex` | Language index for localization |
| 0x0C | 4 | `g_MeshQualityDistance` | Mesh quality distance scalar (CRTMesh__GetQualityLevel) |
| 0x10 | 4 | `g_MeshLodBias` | `cg_meshlodbias` console variable |
| 0x14 | 4 | `g_MeshQualityScaleFactor` | Mesh quality scale (CRTMesh__SetQualityLevel) |
| 0x18 | 4 | `g_MeshQualityLodTable` | Mesh LOD table (CRTMesh__SetQualityLevel, FUN_00476fe0) |
| 0x1C | 4 | `g_LandscapeLowresGeom` | CVar: `"LANDSCAPE_LOWRES_GEOM"` (object @ `0x008aa990`, value @ `0x008aa99c`) |
| 0x20 | 4 | `g_ScreenShape` | Screen shape (0=4:3, 1=16:9, 2=1:1) |
| 0x24 | 4 | `g_DisallowMipMapping` | CVar: RENDERSTATE_DISALLOW_MIPMAPPING (0=allow, 1=disallow) |
| 0x28 | 4 | `g_D3DDeviceIndex` | Selected adapter/device index (CD3DApplication__BuildDeviceList) |
| 0x2C | 4 | `g_TryLockableBackbuffer` | TRY_LOCKABLE_BB flag (D3D init `FUN_0052af00`) |
| 0x30 | 4 | `g_LandscapeMaxLevelsUser` | CVar: `"LANDSCAPE_MAXLEVELS_USER"` (object @ `0x008aa950`, value @ `0x008aa95c`) |
| 0x34 | 4 | `g_UserTextureResLossShift` | CVar: `"USER_TEXTURE_RES_LOSS_SHIFT"` (object @ `0x009cc0f8`, value @ `0x009cc104`) |
| 0x38 | 4 | `g_UserTextureAllow32Bit` | CVar: `"USER_TEXTURE_ALLOW_32_BIT"` (object @ `0x009cc0d8`, value @ `0x009cc0e4`) |
| 0x3C | 4 | `g_ProfileMultisampleType` | Per-profile multisample override (D3DMULTISAMPLE_*). -1 => use `g_SuggestMultisampleType` |
| 0x40 | 4 | `g_InvertXAxisFlag` | Negates X component in FUN_004e1360 (invert flag) |
| 0x44 | 4 | `g_SoundEnabledFlag` | Master sound enable flag (CPCSoundManager) |
| 0x48 | 4 | `g_SoundSampleRateIndex` | Sample rate/bit depth index (CPCSoundManager) |
| 0x4C | 4 | `g_SoundDeviceIndex` | Sound device index (CPCSoundManager) |
| 0x50 | 4 | `g_Sound3DMethod` | 3D sound method (CPCSoundManager) |
| 0x54 | 1 | `g_LandscapeDetailLevel2` | Landscape detail level (enum part). If nonzero, `LandscapeDetail_GetLevel()` returns 2 |
| 0x55 | 1 | `g_LandscapeDetailLevel1` | Landscape detail level (enum part). Used when level2 == 0 |

### Version Stamp Calculation

| Platform | Version Field | Calculation | Size |
|----------|---------------|-------------|------|
| PC (internal) | Raw integer | `CAREER_VERSION` (= 9) | 4 bytes |
| Console (shipped) | Computed stamp | `BASE_VERSION + (sizeof(CCareer) << 4)` (source/internal `CAREER_VERSION=9`; retail Steam runtime `BASE_VERSION=17`) | 2 bytes (SWORD) |

The Steam PC release uses the **console formula** (console-port lineage). This explains why the on-disk **version word** is `0x4BD1` (19409) rather than just `9`.

Note: Many hex dumps show the first 4 bytes as `0x00004BD1` because that's the 16-bit version word plus the next 16 bits of CCareer (often zero). Retail `BEA.exe` copies CCareer bytes from/to `file + 2`, so the true dword boundaries are at offsets where `file_offset % 4 == 2`.

From executable analysis:
```c
// Version check on load:
if (*param_1 != (short)((short)DAT_00623e24 + 0x4bc0)) {
    return 0;  // Version mismatch
}

// DAT_00623e24 = 0x11 (17) at runtime
// 0x11 + 0x4BC0 = 0x4BD1 (19409) = our version stamp!
```

The version is computed as: `BASE_VERSION (17) + 0x4BC0 (19392) = 0x4BD1 (19409)`
