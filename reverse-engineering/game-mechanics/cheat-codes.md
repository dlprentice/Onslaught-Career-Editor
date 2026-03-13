# Cheat Code Analysis
> Created December 2025
> Binary string search results, Ghidra analysis, and implementation findings

## MAJOR UPDATE: PC Port Uses Different Cheat Codes! (Dec 2025)

**Ghidra analysis of BEA.exe revealed the PC port uses DIFFERENT cheat codes than the original Lost Toys internal build!**

**CORRECTED (Dec 2025):** Stuart confirmed that **Jan** (ex-Mucky Foot developer, sat next to Stuart at Lost Toys) did the PC port work in-house. Encore Software was only the **publisher**. The Steam PC port’s cheat strings differ from the internal/source snapshot; the attribution/reason for those differences is not documented here (treat it as retail-port behavior unless new evidence appears).

### Actual PC Port Cheat Codes (XOR Decrypted)

| Index | Steam/PC Code | Effect | Source/Internal Code | Status |
|-------|---------------|--------|--------------------|--------|
| 0 | `MALLOY` | All goodies unlocked (as OLD) | `105770Y2` | ✅ **WORKS** (Dec 2025) |
| 1 | `TURKEY` | All campaign levels unlocked | `!EVAH!` | ✅ **WORKS** (Dec 2025) |
| 2 | `V3R5IOF` | Version display | `V3R5ION` | ⚠️ Decoded from BEA.exe (no call sites found yet) |
| 3 | `Maladim` | God mode toggle (see note) | `B4K42` | ❓ No visible effect |
| 4 | `Aurore` | Free camera toggle (debug button) | Unknown | ✅ Verified in binary (gates `BUTTON_TOGGLE_FREE_CAMERA`) |
| 5 | `lat\\xEAte` | Goodie state override + gating bypass | Unknown | ✅ Used in binary (sets `g_Cheat_LATETE`; forces displayed goodie state to `1`) |

**Note (Feb 2026)**: XOR decoding the cheat table in the current BEA.exe yields `V3R5IOF` (F) at index 2, not `V3R5ION` (N). Index 5 includes a non-ASCII byte (`lat\\xEAte`), which may render as `latête` depending on encoding/font. Treat string rendering differences as display/encoding, and treat effects as verified only when backed by call sites or in-game behavior.

**IMPORTANT: Maladim (God Mode) Behavior - MYSTERY**
Based on Ghidra analysis, the Maladim cheat SHOULD enable the god mode toggle option in the pause menu:
1. Create save with name containing "Maladim"
2. Start any mission
3. Open pause menu (ESC)
4. Look for "GOD MODE ON/OFF" toggle option

**User Testing (Dec 2025):** No visible god mode toggle appeared in the pause menu. This is under investigation. Possible causes:
- Case sensitivity issue (try different capitalizations)
- Additional conditions required
- Binary differs from analysis

**Key Finding**: Retail/Steam cheat strings differ from the source/internal set (`B4K42`, `!EVAH!`, `105770Y2`). Treat this as observed build divergence; specific ownership of the change is not confirmed here.

### Original Source Code Cheat Codes (NOT in PC Port)

These codes are in Stuart's source but **NOT in the Steam/PC executable**:

| Index | Code | Effect | Notes |
|-------|------|--------|-------|
| 0 | `105770Y2` | All goodies unlocked | Leetspeak: "LOSTTOYZ" |
| 1 | `!EVAH!` | All missions unlocked | "HAVE!" backwards |
| 2 | `V3R5ION` | Display version number | Leetspeak: "VERSION" |
| 3 | `B4K42` | God mode | Phonetic: "Baka" |

---

## Implementation Details (Core Mechanism Confirmed - Dec 2025)

Key parts of the implementation are confirmed via retail BEA.exe decompilation (XOR decode + substring match). Treat the C-like snippets below as a *summary* of decompiler output, not verbatim source.

### IsCheatActive Function (0x00465490)

The cheat checking function uses **XOR encryption** with key "HELP ME!!" stored at `0x00629a64`:

```c
// Pseudocode-style summary based on Ghidra decompilation
bool IsCheatActive(int cheatIndex) {
    // Early exit: dev mode or all-cheats flag bypasses checks
    if (g_bDevModeEnabled != 0 || g_bAllCheatsEnabled != 0) {
        return true;  // ALL cheats active!
    }

// XOR decrypt the cheat code (loop runs keyLen times)
char decrypted[256];
char* key = "HELP ME!!";
char* encrypted = &cheat_data[cheatIndex * 0x100];  // 0x00629464

int keyLen = strlen(key);  // "HELP ME!!" = 9 bytes
for (int i = 0; i < keyLen; i++) {
    decrypted[i] = encrypted[i] ^ key[i];
}

// Check if decrypted code is in career name
char* careerName = GetCareerName();
return strstr(careerName, decrypted) != NULL;
}
```

### XOR Encryption Details

| Component | Address | Value |
|-----------|---------|-------|
| XOR Key | `0x00629a64` | "HELP ME!!" (9 bytes) |
| Encrypted Data | `0x00629464` | Cheat strings (256 bytes each) |
| Cheat 0 offset | `0x00629464` | MALLOY |
| Cheat 1 offset | `0x00629564` | TURKEY |
| Cheat 2 offset | `0x00629664` | V3R5IOF (decoded) |
| Cheat 3 offset | `0x00629764` | Maladim (GOD MODE) |
| Cheat 4 offset | `0x00629864` | Aurore (UNKNOWN) |
| Cheat 5 offset | `0x00629964` | latête (decoded, non-ASCII) |

**Implementation detail (from decomp)**: The loop runs for `keyLen` bytes (9 for `"HELP ME!!"`). We have not observed any reads of the remaining bytes in the 0x100-byte slot during the name-check path.

**Tooling:** `tools/cheat_table_decode.py` will decode the cheat table from the current `BEA.exe`.

### Global Cheat Flags

| Address | Name | Purpose |
|---------|------|---------|
| `0x00662df4` | `g_bDevModeEnabled` | If non-zero, ALL cheats active |
| `0x00679ec1` | `g_bAllCheatsEnabled` | If non-zero, ALL cheats active - **Runtime only (BSS - cannot file patch)** |
| `0x00662ab4` | `g_bGodModeEnabled` | Current god mode state |
| `0x006798b0` | `g_Cheat_MALLOY` | Set by IsCheatActive(0); used in goodie gating |
| `0x006798b4` | `g_Cheat_LATETE` | Set by IsCheatActive(5); used in goodie gating |

---

## Cheat Call Site Map (BEA.exe)

| Call Address | Cheat Index | Decoded Code | Effect | Notes |
|--------------|------------|--------------|--------|-------|
| `0x0045d7f4` | 0 | `MALLOY` | Goodie state override | Sets `g_Cheat_MALLOY`; used to bypass goodie gating near `0x0045d050`. Also overrides displayed goodie state to `3` in UI logic at `0x0045e4ba`. |
| `0x0045d80b` | 5 | `latête` | Goodie state override + gating bypass | Sets `g_Cheat_LATETE`; used to bypass goodie gating near `0x0045d048`. Also overrides displayed goodie state to `1` in UI logic at `0x0045e4a9`. |
| `0x00461a6f` | 1 | `TURKEY` | All levels unlocked | Bypasses episode availability check |
| `0x0046f835` | 4 | `Aurore` | Free camera toggle | Gates `BUTTON_TOGGLE_FREE_CAMERA` in `CGame::ReceiveButtonAction` (button=1). When active, toggles free camera on/off for each player. |
| `0x004ce31b` | 3 | `Maladim` | God mode toggle UI | Enables pause menu toggle (via `g_bGodModeEnabled`) |

**Note**: No call sites have been found yet for index 2 (`V3R5IOF`) in this BEA.exe build.
Index 4 (`Aurore`) currently has a single known check inside `CGame::ReceiveButtonAction` (`0x0046f7e0`), in the `BUTTON_TOGGLE_FREE_CAMERA` case (button=1). Additional call sites may exist.

---

## Binary Patch for All Cheats

### v2 Patch - Data Flag Approach

> **WARNING: DATA PATCH DOES NOT WORK!**
>
> The data flag patch at `0x00679ec1` **cannot work** because:
> - Address `0x00679ec1` is in **BSS (uninitialized memory section)**
> - BSS variables exist only at runtime, NOT in the executable file
> - Windows zero-initializes BSS when loading the executable
> - **Only the CODE patch at `0x004654a0` actually works** (but only enables TURKEY effect)
>
> See `patches/README.md` for full technical proof (PE section analysis).

**DISCOVERED Dec 2025**: Setting the `g_bAllCheatsEnabled` data flag would enable ALL cheats - but this flag is in BSS and cannot be file-patched.

| Patch | Address | Before | After | Purpose |
|-------|---------|--------|-------|---------|
| **Data Flag** | `0x00679ec1` | `00` | `01` | Sets `g_bAllCheatsEnabled` to TRUE |
| Code Jump | `0x004654a0` | `75 7A` (JNZ) | `EB 7A` (JMP) | Partial code patch (TURKEY-like only) |

**Why the data patch is essential:**
The game has TWO cheat checking mechanisms:
1. `IsCheatActive()` function - called from 5 locations
2. Direct `g_bAllCheatsEnabled` flag checks - used in 10+ locations

Many functions (goodies menu, god mode toggle, frontend flow) check the flag DIRECTLY without calling `IsCheatActive()`. The code patch alone only affects the 5 call sites.

### v1 Patch (PARTIAL - Historical)

> **CLARIFICATION (Dec 2025):** This section describes the behavior of the **v1 code-only binary patch**, NOT the native cheat codes. The native cheats MALLOY and TURKEY work correctly without any patch (confirmed Dec 2025 user testing). This patch was an attempt to enable dev-mode-style "all cheats active" behavior, which had limited success.

The original code-only patch at `0x004654a0` (JNZ→JMP) only enabled TURKEY-like effect via the dev mode path:
- TURKEY-like effect (levels): Works via patch
- MALLOY-like effect (goodies): Does NOT work via patch alone
- Maladim-like effect (god mode toggle): Does NOT work via patch alone

**Root cause**: Functions like `FUN_004662a0`, `FUN_004714c0`, `FUN_004bb530` check `g_bAllCheatsEnabled` directly, bypassing `IsCheatActive()`. The patch only affects the `IsCheatActive()` function, not direct flag checks.

**Native cheat codes (no patch required):** MALLOY and TURKEY work correctly when entered as save names - this was confirmed by user testing in Dec 2025. The patch was only needed if trying to enable cheats WITHOUT using the cheat code names.

### Global Cheat Flags Reference

| Address | Name | Purpose |
|---------|------|---------|
| `0x00662df4` | `g_bDevModeEnabled` | Dev mode flag (if set, all cheats active) |
| `0x00679ec1` | `g_bAllCheatsEnabled` | Checked directly by 10+ functions - **BSS (runtime only, cannot file patch)** |
| `0x00662ab4` | `g_bGodModeEnabled` | Current god mode state |

---

## strstr() Substring Matching (Confirmed)

Cheat codes are checked using `strstr()` - the **decrypted** code can appear anywhere in the save name:

```cpp
// Original source code pattern (conceptual)
if (strstr(saveName, decryptedCheatCode) != NULL) {
    ActivateCheat(cheatIndex);
}
```

### Key Behaviors

| Behavior | Details |
|----------|---------|
| **Substring matching** | Code can appear anywhere in name (e.g., "MyMALLOYSave" works in Steam retail) |
| **Case sensitive** | Must match exactly - "b4k42" won't work |
| **Multiple codes** | Can combine in one name (e.g., "MALLOYTURKEY" enables both in Steam retail) |
| **PS2 DevKit bypass** | Development hardware auto-enables all cheats |

### Why Binary Search Failed

In the PC port, cheat strings are **XOR-encrypted** (key `"HELP ME!!"`), so plaintext searches will fail.
To validate, search for the key string or the cheat table base (`0x00629464`) instead of plaintext codes.

---

## Binary String Search Results (Dec 2025)

**Search Target**: `BEA.exe` (Steam PC port)

### Cheat Codes NOT Found as Plaintext

Searched for all known cheat code strings in the executable:

| String | Result | Notes |
|--------|--------|-------|
| `B4K42` | **NOT FOUND** | God mode code |
| `!EVAH!` | **NOT FOUND** | Missions unlock code |
| `105770Y2` | **NOT FOUND** | Goodies unlock code |
| `TOYSTOBY` | **NOT FOUND** | Suspected developer cheat |

**Conclusion**: Cheat codes are NOT stored as plaintext strings in the binary (XOR-encrypted).

### Related Strings Found

Debug and script-related strings that reference god mode functionality:

| Address | String | Context |
|---------|--------|---------|
| `0x0062c558` | `"\nGOD mode Score = %0d"` | Debug output when god mode active |
| `0x0064f8c0` | `"SetVulnerable"` | Mission script function |
| `0x0064f444` | `"SetSegmentVulnerable"` | Mission script function |
| `0x0064f428` | `"SetAllSegmentsVulnerable"` | Mission script function |

**Important**: `SetVulnerable` is a **mission script function** for controlling unit vulnerability, NOT the player god mode implementation. God mode uses `CPlayer::SetIsGod()` which internally calls `mBattleEngine->SetVulnerable(FALSE)`.

---

## Implementation Theories (HISTORICAL - Now Resolved)

> **UPDATE Dec 2025**: Source code analysis revealed the actual implementation uses `strstr()` substring matching with plaintext strings. See "Implementation Details" section above.

The following theories were proposed before source code was available:

### Theory 1: Hash Comparison - **DISPROVEN**

Cheat codes are NOT hashed. They use direct string comparison via `strstr()`.

### Theory 2: Character-by-Character - **DISPROVEN**

Not used. The source uses standard C string functions.

### Theory 3: XOR Obfuscation - **POSSIBLY TRUE for PC Port**

While Lost Toys' original code uses plaintext, the retail/porting layer may have obfuscated the strings during the Windows retail work. This would explain why a naive binary search of `BEA.exe` doesn't find the cheat strings in plaintext.

### Theory 4: Removed in Console Port - **DISPROVEN**

Cheats are confirmed working in the Steam version. They were not removed.

---

## Cheat Code Etymology

| Code | Possible Meaning |
|------|------------------|
| `B4K42` | Phonetic: "Baka 42" (Japanese for idiot) or "Before 42" |
| `!EVAH!` | "HAVE!" backwards with exclamation marks |
| `105770Y2` | Leetspeak: "LOSTTOYZ" (Lost Toys studio name) |
| `TOYSTOBY` | "Toby" + "Toys" - may reference a Lost Toys developer |

---

## Cheat Activation Flow

From `Controller.cpp` analysis:

### Console Button Combo
- **Release build**: L1 + R1 triggers `BUTTON_FRONTEND_CHEAT` (45)
- **E3 build**: L1 + R1 + left stick left + right stick right (harder combo)

### Activation Path
1. Player enters name on new game screen
2. Button combo (or keyboard equivalent) triggers cheat validation
3. Name compared against decrypted cheat codes using substring matching (`strstr(saveName, code)`)
4. If match found, appropriate cheat flag is set

---

## Investigation Roadmap

### Completed
- [x] Plaintext string search for all known cheat codes
- [x] Document related strings (`SetVulnerable`, debug output)
- [x] Analyze source code for cheat activation flow
- [x] **SOLVED: Implementation mechanism** - `strstr()` substring matching (Dec 2025)
- [x] **DISCOVERED: V3R5IOF cheat string** - Claimed version display (decoded from BEA.exe; no call sites found yet) (Dec 2025)
- [x] **CONFIRMED: Exact cheat order** - Index 0-3 from FEPSaveGame.cpp (Dec 2025)
- [x] **CONFIRMED: PS2 DevKit bypass** - Auto-enables all cheats (Dec 2025)
- [x] **FOUND: IsCheatActive function** at `0x00465490` (Dec 2025)
- [x] **SOLVED: XOR obfuscation** - Key "HELP ME!!" at `0x00629a64` (Dec 2025)
- [x] **DISCOVERED: PC port uses DIFFERENT cheat codes** - MALLOY, TURKEY, Maladim (Dec 2025)
- [x] **FOUND: Binary patch** - Single byte at `0x004654a0` enables **partial** cheat behavior (TURKEY-like only) (Dec 2025)
- [x] **MAPPED: Global flags** - `g_bDevModeEnabled`, `g_bAllCheatsEnabled` (Dec 2025)

### Next Steps
- [x] Test the PC cheat codes (MALLOY, TURKEY, Maladim) in game - **DONE Dec 2025**: MALLOY=goodies (works), TURKEY=levels (works), Maladim=no visible effect (needs investigation)
- [ ] Verify Maladim shows god mode toggle in pause menu during mission
- [ ] Test binary patch on actual BEA.exe
- [x] Calculate exact file offset for binary patch byte (see `patches/README.md` and `binary-patching/SKILL.md`)
- [x] Document what cheats 0, 1, 2 actually do when activated - **DONE Dec 2025**

### Low Priority
- [ ] Compare Xbox/PS2 executable for different cheat implementation
- [ ] Determine if console versions use the original B4K42/!EVAH!/105770Y2 codes

---

## Related Documentation

- [god-mode.md](god-mode.md) - God mode save patching investigation (why B4K42 effect can't be replicated)
- [../binary-analysis/executable-analysis.md](../binary-analysis/executable-analysis.md) - BEA.exe Ghidra analysis
- [../source-code/_index.md](../source-code/_index.md) - Stuart's source code reference

---

## Attribution

- **String search**: Ghidra analysis of BEA.exe (Dec 2025)
- **Cheat codes**: Community documentation, various online sources
- **Source code references**: Stuart Gillam's Lost Toys internal build
