# Frontend System

## Save/Load Frontend Pages (FEPLoadGame.cpp/h, FEPSaveGame.cpp/h, PCFEPLoadGame.cpp/h, PCFEPSaveGame.cpp/h)

> Analysis added December 2025
> **Updated December 2025**: Added critical PCFEPLoadGame/PCFEPSaveGame stub analysis

The frontend save/load system reveals critical details about save validation, cheat code implementation, and **why Stuart's source code does NOT contain the retail PC save implementation**.

### Class Structure

```
CFrontEndPage (base class)
    ├── CFEPLoadGame (load game - console implementation)
    │       └── CPCFEPLoadGame (PC - EMPTY STUB!)
    └── CFEPSaveGame (save game - console implementation)
            └── CPCFEPSaveGame (PC - EMPTY STUB!)
```

The console implementations (`CFEPLoadGame`, `CFEPSaveGame`) contain full save/load logic, while the PC-specific subclasses (`CPCFEPLoadGame`, `CPCFEPSaveGame`) are empty/commented stubs in this source snapshot, suggesting this internal PC snapshot was not wired for shippable save UI through these classes.

---

### Load Process Flow

The load game flow is remarkably straightforward:

```
CFEPLoadGame::Load()
    │
    ├── Validate mSaveGameNumber != -1 (slot selected)
    │
    ├── Check memory card present and formatted
    │       └── MEMORYCARD.GetCardInfo()
    │
    ├── Allocate buffer via CAREER.SizeOfSaveGame()
    │       └── Returns sizeof(CCareer) + sizeof(SWORD) in the internal snapshot (numerically close to Steam’s observed 10,004-byte envelope, but not by itself a retail-proof size contract)
    │
    ├── Read via MEMORYCARD.ReadSave()
    │       └── Copies raw bytes into buffer
    │
    ├── Validate version via CAREER.Load()
    │       └── Checks 16-bit version word at offset 0
    │
    └── Enable autosave on success
            └── DX_FRONTEND.SetAutoSave(AUTO_SAVE_NORMAL)
```

---

### Save Validation: MINIMAL

**Current evidence (internal path + Steam behavior) indicates minimal validation:** the 16-bit version word at offset 0 is the only required check on the load path we’ve traced.

```cpp
// Conceptual flow from CAREER.Load()
BOOL CCareer::Load(void* buffer, int size) {
    SWORD version = *(SWORD*)buffer;  // Read first 2 bytes
    if (version != current_version_stamp()) {
        return FALSE;  // Version mismatch - reject
    }

    // NO CRC check
    // NO checksum validation
    // NO magic bytes verification

    memcpy(this, buffer + sizeof(SWORD), sizeof(CCareer));  // Copy entire struct (in retail, this is effectively buffer+2)
    return TRUE;
}
```

**What this means for save patching**:
- No integrity checking beyond version stamp
- In the internal/source path, CCareer is `memcpy`'d after version check; retail behavior must be confirmed in `BEA.exe` and includes extra persistence blocks.
- Any data that passes version validation is accepted
- **This helps explain why patching works**, but not as a full 1:1 model - in retail we preserve the version word `0x4BD1` **and** respect fixed size plus options/tail regions (the file often *looks* like `0x00004BD1` if you read the first 4 bytes as a dword and the next 16 bits are zero)

**Security implications**:
- Save files are trivially modifiable
- No anti-tampering measures
- Console ports typically have stricter validation (Xbox has XCALCSIG), but PC bypasses this

---

### CRITICAL: Cheat Codes are NAME-based

**Scope note:** The strings below are from the **source/internal build**. The Steam PC port uses different XOR-decrypted cheat strings (`MALLOY`, `TURKEY`, `V3R5IOF`, `Maladim`, `Aurore`, `latête`), and some effects are still unconfirmed in user testing. See `../game-mechanics/cheat-codes.md` for PC-port details.

**Source/internal behavior (FEPSaveGame.cpp):** Cheat codes are checked against the save game **NAME** using `strstr()`, so the code can appear anywhere in the name.

```cpp
// From FEPSaveGame.cpp (conceptual reconstruction)
static const char* cheat_codes[] = {
    "105770Y2",   // Index 0: All goodies unlocked
    "!EVAH!",     // Index 1: All levels unlocked
    "V3R5ION",    // Index 2: Display version number (NEW!)
    "B4K42"       // Index 3: God mode available
};

void CheckCheats(const char* saveName) {
    for (int i = 0; i < 4; i++) {
        if (strstr(saveName, cheat_codes[i]) != NULL) {
            // Cheat code found - activate corresponding effect
            ActivateCheat(i);
        }
    }
}
```

### Source/Internal Cheat Code Table

| Index | Code | Effect | Notes |
|-------|------|--------|-------|
| 0 | `105770Y2` | All goodies unlocked | Leetspeak for "LOSTTOYZ" |
| 1 | `!EVAH!` | All levels unlocked | "HAVE!" backwards |
| 2 | `V3R5ION` | Display version number | Source/internal string; Steam build decrypts to `V3R5IOF` and remains unconfirmed (no call sites found yet) |
| 3 | `B4K42` | God mode available | Runtime only, see god-mode.md |

**PC Port Note:** In the Steam build, the XOR-decrypted cheat table yields `V3R5IOF` at index 2 (not `V3R5ION`), and includes additional strings like `Aurore` (free camera) and `latête` (goodie UI override). Call sites for index 2 have not been found yet (treat “version display” as unconfirmed in this build).

**Version-display cheat (unconfirmed in Steam build):** Source/internal docs list `V3R5ION` (leetspeak for "VERSION"). The Steam build’s XOR-decrypted cheat table yields `V3R5IOF` at this index, but no call sites have been found yet, so treat the “display version number” behavior as unverified in this build.

**Important behaviors**:
- Uses `strstr()` - code can appear **anywhere** in the save name
- Case sensitive - must match exactly
- Multiple cheats can be activated with a single name (e.g., "B4K42!EVAH!" enables both)
- PS2 DevKit has all cheats enabled automatically (via `#ifdef PS2DEVKIT`)

---

### PS2 DevKit Automatic Cheat Activation

```cpp
#ifdef PS2DEVKIT
    // All cheats automatically enabled on PS2 development hardware
    for (int i = 0; i < NUM_CHEATS; i++) {
        ActivateCheat(i);
    }
#endif
```

Development kits bypass the name check entirely, enabling all cheats unconditionally.

---

### Memory Card Error Codes

Save/load operations use these error codes (from MemoryCard.h):

| Constant | Value | Description |
|----------|-------|-------------|
| `MCE_SUCCESS` | 0 | Operation completed successfully |
| `MCE_FAILURE` | 1 | Generic failure |
| `MCE_NOCARD` | 2 | No memory card present |
| `MCE_UNFORMATTED` | 3 | Card is unformatted |
| `MCE_CORRUPT` | 4 | Save file is corrupt |
| `MCE_CARDFULL` | 5 | Card is full |
| `MCE_FILEEXISTS` | 6 | File already exists (when creating) |
| `MCE_NOFILE` | 7 | File does not exist (when reading) |
| `MCE_TOO_MANY_SAVES` | 8 | Maximum save count reached |

---

### CRITICAL: Internal Source vs Retail/Steam

Stuart's source code is from the **internal PC development build** used during development. The retail/Steam build is a later retail build (console-port lineage) with a different **persistence layer** and a different **on-disk layout** for `.bes` (true dword view is `file_off = 0x0002 + career_off`).

Encore Software was the **publisher** for the Windows release. Public recollections indicate the Windows retail release work was done **in-house at Lost Toys** by Jan (ex-Mucky Foot) and possibly others.

#### Evidence: PCFEPLoadGame / PCFEPSaveGame Stubs (Internal Source)

The PC-specific save/load frontend pages in the internal source are stubs:

```cpp
// PCFEPLoadGame.h - ENTIRE FILE
class CPCFEPLoadGame : public CFrontEndPage {
public:
    // NO METHODS DECLARED - everything commented out
    // CPCFEPLoadGame();
    // ~CPCFEPLoadGame();
    // void Process();
    // void Render();
    // void OnPageActivated();
    // ... all methods commented out
};

// PCFEPSaveGame.h - ENTIRE FILE
class CPCFEPSaveGame : public CFrontEndPage {
public:
    // SAME - NO METHODS DECLARED
    // Everything commented out
};
```

The implementations (`.cpp`) also contain no logic in this internal snapshot.

#### Evidence from CPCMemoryCard

```cpp
class CPCMemoryCard : public CMemoryCard {
public:
    // All methods are no-ops or return success immediately
    BOOL IsHDDAvailable() { return FALSE; }  // Always FALSE!
    int GetNumCards(int *num) { *num = 0; return MCE_SUCCESS; }

    // These do NOTHING:
    int ReadSave(...) { return MCE_SUCCESS; }   // No-op
    int WriteSave(...) { return MCE_SUCCESS; }  // No-op

    // Card info always reports unavailable:
    int GetCardInfo(int card, CCardInfo* info) {
        info->mPresent = FALSE;
        info->mFormatted = FALSE;
        return MCE_SUCCESS;
    }
};
```

#### What This Means (Careful Interpretation)

| Finding | Implication |
|---------|-------------|
| PC FE save pages are stubs in internal source | This snapshot likely wasn't wired up for a shippable PC save UI via these classes |
| `CPCMemoryCard` is stubbed | Internal PC build probably did not use the "memory card" abstraction for persistence on Windows in this snapshot |
| CCareer logic exists in source | Useful guide for many struct layouts/unlock rules, but each persistence claim still needs retail binary validation |

**Practical takeaway:** Use Stuart's source for **struct layouts and logic**, but validate the retail persistence details (layout, tail/options, and any port-specific behavior) against `BEA.exe` and real saves.

#### Platform Constants

| Constant | Value | Platform |
|----------|-------|----------|
| `MAX_MEMORY_CARD_SAVES` | 4096 | Xbox limit (from MemoryCard.h) |
| `MAX_PC_SAVES` | N/A | Unlimited (file system) |
| `SAVE_GAME_SIZE` | ~10004 | Steam retail observed (not guaranteed cross-build/platform) |

Xbox had a hard limit of 4096 saves due to memory card constraints. The retail Windows build removes this limitation entirely.

#### Summary: Why This Matters

| Question | Answer |
|----------|--------|
| Why reverse engineer the binary? | Stuart's source has **no PC save implementation** |
| Why does source code differ from binary? | Different builds/teams: internal dev snapshot vs retail/porting layer |
| Can we trust struct layouts? | **Partially** - many core `CCareer` fields align, but retail persistence is not 1:1 and the **on-disk serialization** differs (true dword view + extra blocks) |
| Can we trust I/O code? | **No** - validate persistence behavior against the retail binary |
| Is the “shift-16” encoding real? | **No** - retail `.bes` values are raw dwords; the “shift-16” look came from a 2-byte misaligned hex-dump view (CCareer begins at `file + 2`) |

**Bottom line**: Stuart's source is invaluable for understanding struct layouts, game logic, and constants. But the actual retail save/load I/O path exists only in the compiled binary and must be reverse engineered there.

---

### Save Size Calculation

```cpp
int CCareer::SizeOfSaveGame() {
    return sizeof(CCareer) + sizeof(SWORD);
    // sizeof(CCareer) ≈ 10000 bytes
    // sizeof(SWORD) = 2 bytes (16-bit version word)
    // Internal-build intuition: ~10002 bytes
}
```

**Retail/Steam note (Feb 2026):** the on-disk `.bes` size is **observed fixed at 10,004 bytes** in the Steam build, and includes additional “options + tail” data beyond the fixed CCareer dump. Retail `BEA.exe`:
- writes a 16-bit version word at file offset `0x0000`,
- bulk-copies `0x24BC` bytes of CCareer to `dest + 2`, then
- appends `0x20 * N` options entries and a fixed `0x56`-byte tail snapshot.

Total size formula: `0x2514 + 0x20*N` with observed `N=16` in the Steam build (`0x2714` = 10,004 bytes). For this repo/tooling, treat `.bes` as fixed-size and do not resize.

---

### AutoSave Behavior

After successful load:
```cpp
if (CAREER.Load(buffer, bytesread) == TRUE) {
    DX_FRONTEND.SetAutoSave(AUTO_SAVE_NORMAL);  // Enable autosave
}
```

AutoSave modes (from DXFrontend.h):
| Mode | Value | Description |
|------|-------|-------------|
| `AUTO_SAVE_NOT` | 0 | Disabled |
| `AUTO_SAVE_NORMAL` | 1 | Standard autosave |
| `AUTO_SAVE_PRETEND` | 2 | Debug mode (simulate) |

---

### Files Analyzed for This Section

| File | Purpose |
|------|---------|
| `FEPLoadGame.cpp` | Load game frontend page (Xbox/PS2 implementation) |
| `FEPLoadGame.h` | Load game class definition |
| `FEPSaveGame.cpp` | Save game frontend page, **cheat code array**, Jan's debug generator |
| `FEPSaveGame.h` | Save game class definition |
| `PCFEPLoadGame.cpp` | **EMPTY STUB** - no implementation |
| `PCFEPLoadGame.h` | **EMPTY STUB** - all methods commented out |
| `PCFEPSaveGame.cpp` | **EMPTY STUB** - no implementation |
| `PCFEPSaveGame.h` | **EMPTY STUB** - all methods commented out |
| `PCMemoryCard.cpp` | **NO-OP** - all operations return success without doing anything |
| `PCMemoryCard.h` | `IsHDDAvailable()` always returns FALSE |

---

## Frontend System (FrontEnd.cpp/FrontEnd.h)

> Analysis added December 2025

The frontend system provides the menu infrastructure, page management, and player controller assignment for Battle Engine Aquila.

### Class Hierarchy

```
CFrontEnd : IController (base class - implements controller interface)
    ├── CDXFrontEnd (DirectX implementation)
    │       └── CPCFrontEnd (PC-specific extensions)
    └── CPS2FrontEnd (PlayStation 2 implementation - not present in the current reference snapshot)
```

**Platform Selection:**
- PC builds use `CPCFrontEnd` extending `CDXFrontEnd`
- Xbox builds use `CDXFrontEnd` directly
- PS2 builds use `CPS2FrontEnd` (not present in the current reference snapshot)

---

### Frontend Pages (EFrontEndPage)

Complete enumeration of all frontend page types:

| Page | Purpose |
|------|---------|
| `FEP_MAIN` | Main menu screen |
| `FEP_DEVELOPMENT` | Development/debug menu |
| `FEP_COMMON` | Common UI elements |
| `FEP_BE_CONFIG` | Battle Engine configuration |
| `FEP_WINGMEN` | Wingmen selection screen |
| `FEP_BRIEFING` | Mission briefing screen |
| `FEP_DEBRIEFING` | Post-mission results |
| `FEP_LEVEL_SELECT` | Campaign level selection |
| `FEP_GOODIES` | Unlockables gallery |
| `FEP_DEVSELECT` | Developer level selection |
| `FEP_LOADGAME` | Load game screen |
| `FEP_SAVEGAME` | Save game screen |
| `FEP_INTRO` | Game intro sequence |
| `FEP_MULTIPLAYER` | Multiplayer menu |
| `FEP_MULTIPLAYER_START` | Multiplayer match setup |
| `FEP_OPTIONS` | Options/settings menu |
| `FEP_CREDITS` | Credits screen |
| `FEP_CONTROLLER` | Controller configuration |
| `FEP_VIRTUAL_KEYBOARD` | On-screen keyboard (console) |
| `FEP_DIRECTORY` | Directory browser |
| `FEP_E3_LEVEL_SELECT` | E3 demo level selection |
| `FEP_LANGUAGE_TEST` | Language/localization testing |
| `FEP_DEMOMAIN` | Demo main menu |

---

### Page Transition System

Frontend pages use a state machine for transitions:

| State | Value | Description |
|-------|-------|-------------|
| `FEPS_INACTIVE` | 0 | Page is not visible |
| `FEPS_ACTIVE` | 1 | Page is fully visible and interactive |
| `FEPS_TRANSITIONING_FROM` | 2 | Page is fading out |
| `FEPS_TRANSITIONING_TO` | 3 | Page is fading in |

**SetPage(page, time):**
```cpp
void CFrontEnd::SetPage(EFrontEndPage page, float time) {
    // If time == 0: instant switch (no animation)
    // If time > 0: animated transition over 'time' seconds
    if (time == 0.0f) {
        // Immediate state change
        mCurrentPage->SetState(FEPS_INACTIVE);
        mNextPage->SetState(FEPS_ACTIVE);
    } else {
        // Start animated transition
        mCurrentPage->SetState(FEPS_TRANSITIONING_FROM);
        mNextPage->SetState(FEPS_TRANSITIONING_TO);
        mTransitionTime = time;
    }
}
```

---

### AutoSave Modes

| Mode | Value | Purpose |
|------|-------|---------|
| `AUTO_SAVE_NOT` | 0 | Explicit save only (user must save manually) |
| `AUTO_SAVE_NORMAL` | 1 | Auto-save after level completion |
| `AUTO_SAVE_PRETEND` | 2 | Simulate save for stress testing (debug) |

---

### Controller Assignment

First player to press START or MENU_SELECT becomes Player 0:

```cpp
// Controller assignment logic
void CFrontEnd::HandleControllerInput() {
    for (int controller = 0; controller < MAX_CONTROLLERS; controller++) {
        if (IsPressed(controller, BUTTON_FRONTEND_MENU_SELECT) ||
            IsPressed(controller, BUTTON_START)) {
            if (mPlayer0Controller == -1) {
                // First press assigns Player 0
                mPlayer0Controller = controller;
            }
        }
    }
}
```

This "press to join" system is common in console games and ensures the correct controller is assigned to Player 1 regardless of physical port.

---

### Level Number Ranges

| Range | Type | Notes |
|-------|------|-------|
| 100-799 | Campaign levels | Standard single-player missions |
| 850-879 | Multiplayer levels | Versus, co-op, skirmish modes |
| 900-905 | Race levels | Unlockable via goodies |

**Multiplayer Detection:**
```cpp
BOOL IsMultiplayerLevel(int worldNumber) {
    return (worldNumber >= 850 && worldNumber <= 879);
}
```

---

### PC Debug Keys (FrontEnd)

Available only in development builds:

| Button Constant | Value | Function |
|-----------------|-------|----------|
| `BUTTON_SAVE_CAREER` | - | Direct career save (bypasses menu) |
| `BUTTON_LOAD_CAREER` | - | Direct career load (bypasses menu) |
| `BUTTON_LOG_CAREER` | 13 | Dump career struct to debug log |

These allow developers to quickly save/load without navigating menus during testing.

---

### Frontend Button Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `BUTTON_FRONTEND_MENU_UP` | 42 | Navigate menu up |
| `BUTTON_FRONTEND_MENU_DOWN` | 43 | Navigate menu down |
| `BUTTON_FRONTEND_MENU_SELECT` | 44 | Confirm selection |
| `BUTTON_FRONTEND_CHEAT` | 45 | Cheat code entry mode |
| `BUTTON_FRONTEND_BACK` | 46 | Go back / cancel |
| `BUTTON_FRONTEND_LEFT` | 54 | Navigate left |
| `BUTTON_FRONTEND_RIGHT` | 55 | Navigate right |
| `BUTTON_FRONTEND_SKIP` | 60 | Skip cutscene / intro |
| `BUTTON_FRONTEND_SPECIAL` | 63 | Context-sensitive action |

These virtual buttons are mapped to different physical inputs per platform (keyboard keys, gamepad buttons).

---

### Files Analyzed for This Section

| File | Purpose |
|------|---------|
| `FrontEnd.cpp` | Frontend system implementation |
| `FrontEnd.h` | Class definitions, enums, constants |

---

## DirectX Frontend (DXFrontend.cpp/h)

Menu system and frontend rendering.

**Frontend Pages (23+ identified):**
| Page Class | Purpose |
|------------|---------|
| `CFEPMain` | Main menu |
| `CFEPGoodies` | Unlockables gallery |
| `CFEPLoadGame` | Load game screen |
| `CFEPSaveGame` | Save game screen |
| `CFEPOptions` | Settings menu |
| ... | And 18+ more |

**Background Color:** `0x001f1f3f` (dark blue-purple)

**AutoSave Modes:**
| Mode | Value | Purpose |
|------|-------|---------|
| `AUTO_SAVE_NOT` | 0 | AutoSave disabled |
| `AUTO_SAVE_NORMAL` | 1 | Standard AutoSave |
| `AUTO_SAVE_PRETEND` | 2 | Simulate save (debug) |

---

## PC Frontend (PCFrontend.cpp/h)

> Analysis added December 2025

### Dual Frontend Implementations

Two frontend classes inherit from `CFrontEnd`:

| Class | Macro | Platform |
|-------|-------|----------|
| `CDXFrontEnd` | `_DIRECTX` | Primary PC/Xbox path |
| `CPCFrontEnd` | `TARGET==PC` | Alternative PC implementation |

The `_DIRECTX` path appears to be the primary path in the Steam retail build analyzed for this repo.

### Virtual Resolution

All frontend rendering uses a **fixed 640x480 virtual coordinate system**, regardless of actual display resolution. UI elements are positioned using these virtual coordinates and scaled at render time.

### Platform-Specific Differences

| Setting | PC (CPCFrontEnd) | Xbox/DX (CDXFrontEnd) |
|---------|------------------|----------------------|
| Texture filtering | `D3DTEXF_NONE` | `D3DTEXF_POINT` |
| Clear color | `0x000f0f2f` | `0x001f1f3f` |
| AutoSave UI | Skipped (direct to debriefing) | Full UI flow |

### Controller Port Limits

| Platform | Max Ports |
|----------|-----------|
| PC/Xbox | 4 |
| PS2 | 2 |

### GeForce 3 GPU Requirement

The game was designed targeting GeForce 3 hardware. On other GPUs, it forces windowed mode as a fallback for compatibility.

### Debug Keys (PC Build Only)

Available in internal/developer builds; not observed as active in the Steam retail build analyzed here:

| Key | Action |
|-----|--------|
| `S` | Save career |
| `L` | Load career |
| `Z` | Log career to debug output |
| `V` | Toggle god mode |
| `U` | Force win current level |
| `I` | Force lose current level |

---
