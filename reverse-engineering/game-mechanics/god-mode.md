# God Mode Investigation

## Current Understanding (Updated Feb 2026)

**CRITICAL CORRECTION**: Our previous hypothesis was WRONG. Offset `0x240C` is NOT god mode!

**Build scope note:** The cheat strings shown as `B4K42`/`!EVAH!`/`105770Y2` below come from the **source/internal build**. The Steam PC port uses different cheat codes (`MALLOY`, `TURKEY`, `Maladim`). Maladim showed **no visible effect** in limited user testing (Dec 2025), so treat Steam-build god-mode behavior as unconfirmed until re-tested.

**Ghidra Evidence (Dec 2025):**
- `PauseMenu.cpp` gates the menu option via `IsCheatActive(3)` and uses `g_bGodModeEnabled` as the pause-menu toggle state
- Retail `.bes` uses the **true dword view**:
  - 16-bit version word at `0x0000` (`0x4BD1`)
  - `CCareer::Load/Save` copies CCareer bytes from/to `file + 2`
  - File offset mapping: `file_off = 0x0002 + career_off`
- **Steam build correction:** the file offsets previously documented as `mIsGod[]` are **not** god mode persistence flags in the Steam build. They are used by the Controls UI for per-player/per-mode invert-Y (walker/flight) toggles.

**God Mode / Controls-Adjacent Fields** (file offsets, true dword view):
| File Offset | CCareer Offset | Size | Field | Purpose |
|-------------|----------------|------|-------|---------|
| 0x240A | 0x2408 | 128 | mSlots[32] | Tech slots array (32 ints) |
| 0x248A | 0x2488 | 4 | mCareerInProgress | Progress flag |
| 0x248E | 0x248C | 4 | mSoundVolume | Sound settings (float) |
| 0x2492 | 0x2490 | 4 | mMusicVolume | Music settings (float) |
| 0x2496 | 0x2494 | 4 | g_bGodModeEnabled | Pause-menu toggle state (cheat-gated) |
| 0x249A | 0x2498 | 4 | (unused/padding) | Observed 0; used as a base for 1-based indexing in invert logic |
| 0x249E | 0x249C | 4 | mInvertYFlightP1 | Player 1 flight/jet invert Y |
| 0x24A2 | 0x24A0 | 4 | mInvertYFlightP2 | Player 2 flight/jet invert Y |
| 0x24A6 | 0x24A4 | 4 | mInvertYWalkerP1 | Player 1 walker invert Y |
| 0x24AA | 0x24A8 | 4 | mInvertYWalkerP2 | Player 2 walker invert Y |
| 0x24AE | 0x24AC | 4 | mVibration[0] | Player 1 controller vibration toggle (`0=Off`, non-zero=On) |
| 0x24B2 | 0x24B0 | 4 | mVibration[1] | Player 2 controller vibration toggle (`0=Off`, non-zero=On) |
| 0x24B6 | 0x24B4 | 4 | mControllerConfigurationNum[0] | Player 1 controller config/preset index |
| 0x24BA | 0x24B8 | 4 | mControllerConfigurationNum[1] | Player 2 controller config/preset index |

**Runtime-address note:** `g_bGodModeEnabled` here refers to the persisted CCareer field at file `0x2496`. The runtime address commonly labeled `g_bGodModeEnabled` at `0x00662ab4` is the in-memory address used after load, not a second independent persisted storage location.

**Internal build note:** God mode was designed as per-player state (2-player support). In the Steam build, we have not identified a reliable per-player persisted flag in the `.bes` save format; behavior remains cheat-gated.

**Encoding note (Feb 2026):** In the true view, these flags are normal 32-bit values (0/1 observed). In the legacy 4-byte-aligned view, the same bytes can *appear* as `0x00010000`.
**WRONG Offset 0x240C**: This is actually `mSlots[1]` tech slot data, NOT god mode!

---

## Historical Context (Dec 2025)

### Previous Misunderstanding
The gold save file has `0x01000000` at offset 0x240C, which we now understand:
- **This is NOT god mode at all** - it's `mSlots[1]` in the tech slots array
- The value `0x01000000` represents tech slot bits, not a god mode flag
- Our patcher was writing to the wrong offset entirely

**Why our tests failed initially**: We were patching tech slot data, not god mode. In the Steam build, the bytes at `0x249A/0x249E/...` are invert-Y toggles, not god mode persistence.

### The REAL Answer (Source/Internal Build): B4K42 Checks Save NAME, Not Flag

**From `FEPSaveGame.cpp` source code (Dec 2025 analysis):**

```cpp
// Cheat codes defined in FEPSaveGame.cpp
char cheatname[4][256];
strcpy(cheatname[0], "105770Y2");   // Index 0: All goodies unlocked
strcpy(cheatname[1], "!EVAH!");     // Index 1: All levels unlocked
strcpy(cheatname[2], "V3R5ION");    // Index 2: Show version number
strcpy(cheatname[3], "B4K42");      // Index 3: God mode available

// Called with the save name to check for cheat codes
BOOL CFEPSaveGame::IsCheatActive(int cheatno) {
    char mungedname[256];
    strcpy(mungedname, FromWCHAR(mSaveGameName));

    // On PS2 devkit, all cheats are active
    #if TARGET == PS2
    if (CLIPARAMS.mDevKit)
        return TRUE;
    #endif

    // Uses strstr() - code can appear ANYWHERE in the name!
    if (strstr(mungedname, cheatname[cheatno]) != NULL)
        return TRUE;
    else
        return FALSE;
}
```

**This explains the internal/source build behavior (and what we learned about Steam):**
1. The B4K42 cheat works by checking the **save game NAME string** at runtime via `strstr()`
2. The cheat code can appear **anywhere** in the save name (not just the full name)
3. In the internal build source, god mode is per-player runtime state (`CPlayer::mIsGod`) and `CPlayer::SetIsGod()` persists to `CCareer::mIsGod[2]`
4. In the Steam build, the on-disk dwords previously documented as `mIsGod[]` are used by the Controls UI for invert-Y toggles; we have **not** identified a per-player persisted god flag in `.bes` saves
5. In the Steam build, the pause menu uses `IsCheatActive(3)` for gating and uses `g_bGodModeEnabled` (file `0x2496`) as the menu toggle state, but Maladim shows no visible effect in testing
6. Practical implication: save patching the old "mIsGod" offsets is not a valid approach on Steam; any invincibility is still driven by runtime state and additional gating/conditions

**PC port note:** In the Steam build, `IsCheatActive(3)` uses the `Maladim` string (per Ghidra), but user testing shows no visible effect so far. This suggests the name check alone is not sufficient in that build.

**Why `mIsGod[]` exists in the internal source at all:**
- The internal build has split-screen support (2 players), so per-player arrays are common.
- In that source, `CPlayer::CPlayer()` loads `mIsGod` from `CAREER.GetIsGod(mNumber-1)`, implying persistence was intended for that build.
- The Steam PC port diverges: the corresponding on-disk region is used for controls settings (invert-Y), and per-player persisted god flags are currently unconfirmed.

---

## Source Code Implementation (Player.cpp - Dec 2025 Analysis)

**Full call chain when god mode is enabled:**
```cpp
void CPlayer::SetIsGod(BOOL val) {
    mIsGod = val;                        // Set player's runtime flag
    CAREER.SetIsGod(mNumber-1, val);     // Persist to career (1-indexed player)

    if (mBattleEngine.ToRead()) {
        if (mIsGod == TRUE) {
            mBattleEngine->SetVulnerable(FALSE);    // Disable damage
            mBattleEngine->SetInfinateEnergy(TRUE); // Infinite energy (typo preserved!)
        } else {
            mBattleEngine->SetVulnerable(TRUE);
            mBattleEngine->SetInfinateEnergy(FALSE);
        }
    }

    if (val)
        IncStat(PS_CHEATED, 1);  // Marks player as cheater!
}
```

**Storage in Career struct (Career.h):**
```cpp
CSArray<BOOL, 2> mIsGod;  // 2-player support, 8 bytes total
```

**God mode is loaded on player construction:**
```cpp
CPlayer::CPlayer(int number) : mNumber(number) {
    // ...
    mIsGod = CAREER.GetIsGod(mNumber-1);  // Load from saved career!
}
```

---

## Why Save Patching Didn't Work (Steam Build, Updated Feb 2026)

**Root Cause (Steam PC port)**: We were patching the wrong offsets. In the Steam build, the dwords at `0x249A/0x249E/...` are used for invert-Y controls settings, not per-player god flags. Any invincibility is runtime state and remains cheat-gated.

**Evidence trail (Steam build):**
1. **Cheat gating**: `PauseMenu__Init` gates the menu option via `IsCheatActive(3)` (PC port cheat string: `Maladim`)
2. **Toggle state**: the pause menu uses `g_bGodModeEnabled` (file `0x2496`) as the toggle state once the option is available
3. **Controls UI xrefs**: the `0x249E/0x24A2/0x24A6/0x24AA` dwords are accessed as per-player invert-Y toggles (walker/flight)
4. **User testing (Dec 2025)**: Maladim showed no visible effect in single-player; MP "invincibility" observations are runtime behavior and are not attributable to persisted per-player flags in Steam saves

---

## Internal Build Cheat Gating (B4K42) (Historical)

`IsCheatActive(3)` checks the **save game NAME** using substring matching. In the internal/source build the string is `B4K42`; in the Steam PC port, the decrypted cheat string for index 3 is `Maladim`. From `FEPSaveGame.cpp` (internal/source build):
```cpp
// Cheat code checking - uses strstr() for substring match
if (strstr(saveName, "B4K42") != NULL) {
    // God mode toggle enabled in pause menu
}
```

Additionally, from `PCController.cpp`, god mode was also a **runtime toggle** via debug keyboard shortcut in internal builds:

| Key | Action | Notes |
|-----|--------|-------|
| **V** | Toggle God Mode | Runtime only! Mapped to `BUTTON_TOGGLE_GOD_MODE` |
| **U** | Instant Win Level | Debug cheat (`BUTTON_WIN_LEVEL`) |
| **I** | Instant Lose Level | Debug cheat (`BUTTON_LOOSE_LEVEL`) |
| **S** | Save Career | Debug save |
| **L** | Load Career | Debug load |
| **Z** | Log Career State | Dumps career to log |
| **7** | Complete All Objectives | Debug skip (`BUTTON_COMPLETE_ALL_OBJECTIVES`) |

**BUTTON_TOGGLE_GOD_MODE Handler (game.cpp line 2572):**
```cpp
case BUTTON_TOGGLE_GOD_MODE:
    for (n = 0; n < MAX_PLAYERS; n++) {
        if (mPlayer[n]) {
            if (mPlayer[n]->IsGod())
                mPlayer[n]->SetIsGod(FALSE);
            else
                mPlayer[n]->SetIsGod(TRUE);
        }
    }
    break;
```

**Implication:** The debug keys were stripped from release builds, but god mode was designed as a runtime toggle, NOT a persistent save flag. This explains why patching the `mIsGod[]` flags in the save has no effect in single-player: the retail build uses save-name cheats at runtime.

---

## CORRECTED: Bit Flags at 0x240C Are Tech Slots, NOT God Mode (Dec 2025)

**Function `CCareer__ReCalcLinks` at 0x0041bdf0 checks bits 29-30:**

```c
// From decompiled code:
if ((*(uint *)(in_ECX + 0x240c) >> 0x1d & 1) != 0)  // Check bit 29 = Slot 61
if ((*(uint *)(in_ECX + 0x240c) >> 0x1e & 1) != 0)  // Check bit 30 = Slot 62
```

**CRITICAL CORRECTION**: These are NOT god mode flags! They are tech slot bits:

| Bit | Slot | Constant | Purpose |
|-----|------|----------|---------|
| 29 | 61 | `SLOT_500_ROCKET` | Controls higher tier path after mission 500 |
| 30 | 62 | `SLOT_500_SUB` | Controls lower tier path after mission 500 |

**From Career.cpp lines 468-481:**
```cpp
if (END_LEVEL_DATA.mWorldFinished == 500) {
    if ((GetSlot(SLOT_500_ROCKET)) && (link == CAREER.GetLink(finished_node->mHigherLink))) {
        complete=TRUE;  // Complete higher path link
    }
    if ((GetSlot(SLOT_500_SUB)) && (link != CAREER.GetLink(finished_node->mHigherLink))) {
        complete=TRUE;  // Complete lower path link
    }
}
```

**Explanation**: Mission 500 has a branching path. When you complete it:
- If you took the "rocket" path, `SLOT_500_ROCKET` is set, enabling the higher tier link
- If you took the "sub" path, `SLOT_500_SUB` is set, enabling the lower tier link

This is mission progression logic, NOT invincibility.

---

## Tech Slots Layout (True File Offsets)

For save patching, use true file offsets (`file_off = 0x0002 + career_off`):

| mSlots Index | File Offset (true view) | CCareer Offset | Slot Numbers |
|--------------|--------------------------|----------------|--------------|
| mSlots[0] | 0x240A | 0x2408 | 0-31 |
| mSlots[1] | 0x240E | 0x240C | 32-63 |
| mSlots[2] | 0x2412 | 0x2410 | 64-95 |
| ... | ... | ... | ... |

`0x2408/0x240C/...` are CCareer/aligned-view references and are not authoritative on-disk patch offsets.

---

## Executable Analysis

**CFeatureInvincible** class exists (RTTI at 0x00627548) but implementation is obfuscated.

Related strings found:
- `"GOD mode Score = %0d"` at 0x0062c558 (debug display)
- `"SetVulnerable"` at 0x0064f8c0 (script command)
- `"SetAllSegmentsVulnerable"` at 0x0064f428
- `"SetSegmentVulnerable"` at 0x0064f444

**Why god mode patching has not worked (UPDATED)**: We were patching the WRONG offset (0x240C = tech slots). Also, in the **Steam build**, the bytes at `0x249A/0x249E/...` are used by the Controls UI for invert-Y (walker/flight) toggles, not god mode persistence.

God mode also requires:
1. Runtime feature flags (CFeatureInvincible instantiation)
2. Player state updates (SetVulnerable calls)
3. The save flag to be read on player construction (may be disabled in console port)

The B4K42 cheat code (entered as save game NAME when starting new game) works because it triggers runtime gating in the internal/source build. In Steam/retail, use the retail cheat table and treat behavior as build-specific.

---

## PS_CHEATED Stat

From `Player.cpp` - enabling god mode increments a cheat counter:

```cpp
void CPlayer::SetIsGod(BOOL val) {
    mIsGod = val;
    CAREER.SetIsGod(mNumber-1, val);
    if (val) IncStat(PS_CHEATED, 1);  // Marks player as cheated!
}
```

This may affect grade eligibility or goodie unlocks.

---

## IN-GAME TEST RESULTS (Dec 12, 2025) (Historical; Re-evaluate for Steam Build)

**Test saves used:**
- `test_godmode_correct_p1_shift16.bes` - P1 ON, P2 ON
- `test_godmode_correct_both_shift16.bes` - P1 ON, P2 ON

**Results:**

| Finding | Status |
|---------|--------|
| God mode works in multiplayer | ⚠️ **Historical** (pre-correction; do not treat as Steam-confirmed) |
| God mode works in single-player | ❓ **Unverified** on Steam build |
| Player 2 invincibility (multiplayer) | ⚠️ **Historical** (pre-correction; do not treat as Steam-confirmed) |
| Player 1 invincibility (single-player) | ❓ **Unverified** on Steam build |
| Unlimited ammo | ❌ **NOT INCLUDED** |
| Environmental hazards bypass | ❌ Water still kills |

**What "god mode" actually does:**
- Shields and health do NOT drop from weapon/enemy damage
- Does NOT grant infinite ammo (energy depletes normally)
- Does NOT protect from environmental hazards (water is still lethal)

**Key insight (Steam build correction):** Earlier notes referenced a “P2 god mode flag” at `0x249E`, but in the Steam build that offset is used for **flight/jet invert Y (P1)**. Treat any conclusions derived from those offsets as invalid for Steam until re-tested with updated field mapping.

**Why P1 god mode might not work:**
- Single-player may follow different initialization/toggle code paths than multiplayer
- The console port may have disabled the save-load path for P1
- Runtime flag may need to be triggered differently for P1

---

## Investigation Status (Core Mechanism Resolved; Steam Behavior Still Under Test)

**Internal/source resolution:** `B4K42` is save-name substring gating in source snapshots.  
**Steam/retail status:** index-3 cheat string is `Maladim`; menu-gating callsite is identified, but in-game effect remains partially unverified.

- [x] Compare gold save 0x240C region byte-by-byte with patched saves - **DONE**: Gold save has `0x01000000` - now understood as tech slot data, not god mode
- [x] Test if 0x01000000 (gold save value) enables god mode - **DONE**: It doesn't - because it's not god mode! It's `mSlots[1]` tech slot bits
- [x] **CORRECTED**: Offset 0x240C is `mSlots[1]`, NOT `mIsGod[0]` - bits 29-30 control mission 500 branching paths
- [x] Check if PS_CHEATED stat is stored in save file - **DONE**: Documented in "Player Stats (Career.h)" section. Stored at `mStats` array in career save.
- [x] Look for cheat code input handlers in the binary - **DONE**: Debug keys documented in "God Mode Mystery SOLVED" section (PCController.cpp). Stripped from release builds.
- [ ] Re-test god mode persistence for Steam build with corrected field mapping (note: `0x249A/0x249E/...` are invert-Y toggles)
- [x] **SOLVED via FEPSaveGame.cpp**: B4K42 checks `strstr(saveName, "B4K42")` using `IsCheatActive(3)`
- [ ] Why Maladim shows no visible effect in the Steam build - **OPEN**: likely additional gating/conditions beyond name-match
- [x] Why save patching old `mIsGod[]` offsets doesn't work (Steam build) - **EXPLAINED**: those offsets are used for invert-Y, and runtime god behavior is cheat-gated; the pause-menu toggle uses the persisted field at file `0x2496`

**Remaining (low priority, informational only):**
- [ ] Test single-player with `Maladim` to verify whether the pause-menu god-mode toggle appears and whether runtime invincibility engages in Steam build
- [ ] Verify if multiplayer P2 can get god mode via any mechanism (no cheat code triggers P2)

---

## Complete Player Stats (PS_*) System

| Stat | Index | Purpose | Encoding |
|------|-------|---------|----------|
| `PS_UNITSDESTROYED` | 0 | Total units destroyed | Standard |
| `PS_ROUNDSFIRED` | 1 | Ammunition expended | Standard |
| `PS_ROUNDSHIT` | 2 | Shots that connected | Standard |
| `PS_CHEATED` | 3 | Cheat usage counter | Incremented by SetIsGod() |
| `PS_TIMEASJET` | 4 | Time in jet mode | Seconds |
| `PS_TIMEASWALKER` | 5 | Time in walker mode | Seconds |
| `PS_DAMAGETAKEN` | 6 | Damage received | **x256 multiplier** (fixed-point) |
| `PS_NUM_PLAYERSTATS` | 7 | Sentinel/count | N/A |

**Note:** `PS_DAMAGETAKEN` uses x256 encoding (NOT shift-16) because damage is floating-point. Different encoding than career integers.

---

## In-Game Cheat Codes

Enter as save game name when creating a new game:

**ORIGINAL codes (Stuart's source):**
| Code | Effect |
|------|--------|
| `B4K42` | God mode (runtime only - patching doesn't work) |
| `!EVAH!` | All missions unlocked |
| `105770Y2` | All goodies unlocked |

**PC PORT codes (Steam/retail):**
| Code | Effect |
|------|--------|
| `Maladim` | God mode (NO VISIBLE EFFECT - needs investigation) |
| `TURKEY` | All missions unlocked |
| `MALLOY` | All goodies unlocked |

**NOTE:** Steam/retail cheat strings differ from source/internal strings; MALLOY and TURKEY are confirmed working in Steam without patching, while Maladim behavior remains under investigation. Treat change ownership as unconfirmed here.

**See [cheat-codes.md](cheat-codes.md)** for detailed analysis of cheat code storage (not plaintext in binary), obfuscation theories, and activation flow.

---

## Cheat Activation Mechanism

From `Controller.cpp`:
- **Release build**: L1 + R1 triggers `BUTTON_FRONTEND_CHEAT` (45)
- **E3 build**: L1 + R1 + left stick left + right stick right (harder combo)

The actual cheat validation uses build-specific frontend strings (source/internal: B4K42/!EVAH!/105770Y2; Steam PC port: MALLOY/TURKEY/Maladim/Aurore/latête). **See [cheat-codes.md](cheat-codes.md)** for binary analysis findings.
