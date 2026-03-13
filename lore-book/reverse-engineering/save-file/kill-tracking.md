# Kill Tracking System

## Kill Types (from source: EKilledType - Player.h)

**TK = "Thing Killed"** - Confirmed via `GetNumEnemyThingKilled()` and `KilledEnemyThing()` in Player.cpp. Categorizes enemy units destroyed by type. NOT "Team Kill" (no friendly fire tracking in codebase).

```cpp
enum EKilledType {
    TK_AIRCRAFT,      // 0 - CCareer offset 0x23F4 (file offset 0x23F6 in true dword view)
    TK_VEHICLES,      // 1 - CCareer offset 0x23F8 (file offset 0x23FA in true dword view)
    TK_EMPLACEMENTS,  // 2 - CCareer offset 0x23FC (file offset 0x23FE in true dword view)
    TK_INFANTY,       // 3 - CCareer offset 0x2400 (file offset 0x2402 in true dword view) (TYPO preserved from source!)
    TK_MECHS,         // 4 - CCareer offset 0x2404 (file offset 0x2406 in true dword view)
    TK_TOTAL,         // 5 - Marks end of SAVED counters

    TK_HACK_AGRADES,  // 6 - RUNTIME ONLY - counts total A-grades
    TK_HACK_SGRADES,  // 7 - RUNTIME ONLY - counts total S-grades
};
```

**CRITICAL (Dec 2025):** Only indices 0-4 are saved to the .bes file. Indices 6-7 are "virtual" counters used at runtime for grade-based goodie unlock checks. They're calculated on the fly by counting grades in the save, NOT stored as counters.

```cpp
// FEPGoodies.cpp usage:
switch (mT1) {
    case TK_HACK_AGRADES:
        num = COUNT_TOTAL_A_GRADES();  // Runtime calculation
        break;
    case TK_HACK_SGRADES:
        num = COUNT_TOTAL_S_GRADES();  // Runtime calculation
        break;
    default:
        num = CAREER.GetNumKilled(mT1);  // From save file
        break;
}
```

---

## TK_ Confirmed: "Thing Killed" NOT "Team Kill"

**User hypothesis tested:** TK might mean "Team Kill" (friendly fire).

**Evidence confirms TK = "Type/Thing Killed":**
- The function `KilledEnemyThing(CUnit* thing)` explicitly tracks kills of **enemy** units only
- Function name says "EnemyThing" - no friendly fire tracking anywhere
- Kill attribution uses `thing->IsA(THING_TYPE_*)` to determine unit category
- The array storing counts is `mThingsKilled` (line 100 of Player.h)
- The getter is `GetNumEnemyThingKilled(EKilledType type)`

**Conclusion:** TK_ stands for "Thing Killed" categorizing enemy units destroyed by type.

---

## Memory Layout

**CRITICAL FIX**: Kill counters live at **CCareer offset `0x23F4`** (5 dwords total), with true on-disk dwords at `0x23F6`, `0x23FA`, `0x23FE`, `0x2402`, `0x2406` (file = `career + 2`).

The previous offset (`0x23A4`) was wrong and lands inside reserved `CGoodie` entries 280-284. That legacy mistake caused goodie corruption.

**Important file-vs-memory nuance**: `CCareer__Load` validates a 16-bit version word at file offset `0x0000` and then bulk-copies the CCareer bytes from `source + 2` into memory. That makes many 32-bit fields appear **shifted by 2 bytes** in the on-disk file.

For kill counters, there are two common ways you’ll see offsets discussed:
- **True dword view (authoritative)**: dwords at `0x23F6`, `0x23FA`, ... which correspond to the actual in-memory dwords; these are what `BEA.exe` operates on directly.
- **Legacy aligned view (deprecated)**: dwords at `0x23F4`, `0x23F8`, ... (2 bytes earlier). In that view, values can appear as `dword >> 16`, but patching at those offsets can overlap adjacent true dwords and silently corrupt metadata.

### Canonical Interpretation (What BEA.exe Uses)

Binary checks and unlock logic use (in-memory dwords):
- `kills_payload = (kill_dword & 0x00FFFFFF)` (24-bit integer payload)
- `meta = (kill_dword >> 24)` (top byte, treated as signed-with-bias and clamped for the first two counters)

This matches `CCareer__Load` (clamps only the top byte and preserves the lower 24 bits) and `CCareer__UpdateGoodieStates` (masks with `& 0x00FFFFFF` before comparing to threshold ints like 25/50/75/100, 100/200/300/400, etc).

### File Offsets (On-Disk)

| Aligned Offset (Count = `>>16`) | True Dword Offset (Payload = `&0x00FFFFFF`) | Category | Goodie Unlock Thresholds |
|---------------------------------|--------------------------------------------|----------|--------------------------|
| 0x23F4 | 0x23F6 | Aircraft | 25, 50, 75, 100 kills |
| 0x23F8 | 0x23FA | Vehicles | 100, 200, 300, 400 kills |
| 0x23FC | 0x23FE | Emplacements | 25, 50 kills (75 appears in combined unlocks) |
| 0x2400 | 0x2402 | Infantry | 40, 80, 160 kills (no 120-based goodie in this build) |
| 0x2404 | 0x2406 | Mechs | 20, 40, 80 kills (40 is used by 2 goodies) |

**Encoding (true dword view)**: `stored_value = (kills_payload) | (meta << 24)`
- Typical observed meta value is `0x80` for the first two counters (i.e., neutral bias), so 95 kills often appears as `0x8000005F` at file offset `0x23F6`.

**Why patchers preserve metadata**: the binary uses the **top byte** as persistent metadata for at least the first two counters. Patchers should preserve that byte and only update the lower 24-bit payload.

---

## Binary Evidence (BEA.exe)

- `CCareer__UpdateThingsKilled` (`0x0041c180`) updates `this + 0x23f4 + i*4` and logs totals using `value & 0xFFFFFF`.
- Per-level counts live in `g_LevelKillCounts` (`0x00672e30`) and are added into CCareer totals during `CCareer__UpdateThingsKilled`.
- Helper at `0x0041c160` returns `(*(this + 0x23f4 + idx*4) & 0x00FFFFFF)` (raw lower‑24‑bit value).
- `CCareer__UpdateGoodieStates` (`0x0041c470`) reads kill-related globals (e.g., `g_Career_mThingsKilled` at `0x00662a14` and adjacent addresses) to decide goodie unlocks.
- `CCareer__Load` (`0x00421200`) clamps the **top byte** for offsets `0x23f4` and `0x23f8`, preserving the lower 24 bits.
- `CCareer__GetKillCounterTopByte_23F8` (`0x00421900`) and setters at `0x00421910` / `0x00421940` manipulate only the top byte (bias 0x80).

These imply the binary treats kill totals as **lower 24-bit values**, with the top byte used for range/metadata (clamped to a signed-bias range around `0x80`).

**Observed save values (retail .bes):**
- Aligned view @ `0x23F4`: `0x005F0000` → 95 kills (`>> 16`)
- True dword view @ `0x23F6`: `0x8000005F` → 95 kills (`& 0x00FFFFFF`)

This reconciles the earlier “shift-16 vs 24-bit” mismatch: the aligned `>> 16` view is an artifact of the 2-byte version word shifting the CCareer dump in the file.

---

## Load-Time Clamp (Top Byte)

From `CCareer__Load` (0x00421200), the code validates and adjusts values at offsets 0x23F4 and 0x23F8:

```c
// Career object offsets:
in_ECX[0x8fd]  // = offset 0x23F4 - First kill counter
in_ECX[0x8fe]  // = offset 0x23F8 - Second kill counter

// Range validation:
iVar5 = ((uint)in_ECX[0x8fd] >> 0x18) - 0x80;
if ((iVar5 < -0x40) || (0x40 < iVar5)) {
    iVar5 = 0;  // Clamp out-of-range values
}
```

**Clarification (Feb 2026):** The load clamp only touches the **top byte** and preserves the lower 24 bits. BEA.exe uses the masked lower 24 bits as the integer kill count directly (e.g., `0x8000005F & 0x00FFFFFF == 95`). The `>> 16` interpretation only applies to the repo's historical *aligned file view* (because it is 2 bytes earlier than the true dword boundary).

---

## The "Top Byte" Is Persisted Metadata (Unknown UI Meaning)

The *top byte* of the first two kill counters (CCareer offsets `0x23F4` and `0x23F8`) is treated by the retail binary as **persistent options/metadata**, not as part of the kill count:

- `CCareer__GetKillCounterTopByte_23F4` (`0x004218f0`) / `CCareer__SetKillCounterTopByte_23F4` (`0x00421910`)
- `CCareer__GetKillCounterTopByte_23F8` (`0x00421900`) / `CCareer__SetKillCounterTopByte_23F8` (`0x00421940`)
- `CFEPOptions__GetKillCounterTopBytes_23F4_23F8` (`0x0051f470`) reads both values
- `CFEPOptions__SetKillCounterTopBytes_23F4_23F8` (`0x0051f490`) writes both values

**Practical consequence for patchers:** when writing kill counts (true view at `0x23F6..0x2409`), preserve the existing `meta` byte: `new = (old & 0xFF000000) | (kills & 0x00FFFFFF)`.

**Important:** This is *not* the Sound/Music volume system. The real audio volumes are IEEE-754 floats in CCareer at:
- `mSoundVolume` (true view `0x248E`)
- `mMusicVolume` (true view `0x2492`)

We have not yet confirmed what user-facing setting (if any) these kill-counter meta bytes correspond to in the options UI.

---

## Goodie Unlocks by Kill Count

For the complete list of which goodies unlock at each kill threshold, see **[goodies-system.md](goodies-system.md#kill-based-unlocks-source-of-truth)**.

**Summary of thresholds:**

| Category | Thresholds | Max Needed |
|----------|------------|------------|
| Infantry | 40, 80, 160 | 160 |
| Aircraft | 25, 50, 75, 100 | 100 |
| Vehicle | 100, 200, 300, 400 | 400 |
| Mech | 20, 40, 80 | 80 |
| Emplacement | 25, 50 | 50 |

---

## Implementation Notes

The patcher supports per-category overrides (C# and Python CLI) to match specific unlock requirements. If no overrides are provided, a single global value is applied to all five categories.

**Minimum effective values:**
- For all infantry unlocks: 160 kills
- For all aircraft unlocks: 100 kills
- For all vehicle unlocks: 400 kills
- For all mech unlocks: 80 kills
- For all emplacement standalone unlocks: 50 kills
- For the combined Emplacements+Vehicles goodie: 75 emplacements AND 100 vehicles (source/internal `FEPGoodies.cpp`; retail behavior appears consistent so far)

**Recommended default**: 400+ to unlock all kill-based goodies.

---

## Training Level Kill Exclusion

World 100 (Training) does NOT add to kill counters:
```cpp
// don't score on training level
if (END_LEVEL_DATA.mWorldFinished == 100) return;
```

---

## TK_INFANTY Typo Confirmed

The infantry kill type has a typo (missing 'R') preserved throughout the codebase:
```cpp
TK_INFANTY = 3  // NOT TK_INFANTRY
```
