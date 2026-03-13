# IsCheatActive

> Address: 0x00465490 | Source: `references/Onslaught/FEPSaveGame.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Partially (mechanism confirmed, codes differ from source)

## Purpose

XOR-decrypts cheat codes stored in the binary and checks if the current save game name contains the specified cheat code. This is the core function that enables all cheat code functionality in the PC port.

## Signature
```c
// thiscall convention - ECX = CCareer* this
bool __thiscall CCareer::IsCheatActive(int cheatIndex);
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| this (ECX) | CCareer* | Pointer to career instance (contains save name) |
| cheatIndex | int | Index into cheat table (0-5 known in retail BEA.exe) |

## Return Value

- **TRUE (1)**: Cheat is active (code found in save name OR dev mode enabled)
- **FALSE (0)**: Cheat is not active

## Algorithm

```
1. Check g_bDevModeEnabled (0x00662df4)
   - If set, return TRUE (all cheats enabled)

2. Check g_bAllCheatsEnabled (0x00679ec1)
   - If set, return TRUE (all cheats enabled)

3. Calculate cheat code address:
   - codePtr = 0x00629464 + (cheatIndex * 256)

4. XOR decrypt cheat code:
   - key = "HELP ME!!" (at 0x00629a64)
   - The binary XOR-decrypts only the first `keyLen` bytes (9) of the 0x100-byte block:
     decrypted[i] = encrypted[i] ^ key[i]  for i in [0..keyLen)
   - Remaining bytes in the 0x100-byte block are ignored

5. Get current save name from CCareer

6. Use strstr(saveName, decryptedCode)
   - If found (non-NULL), return TRUE
   - If not found (NULL), return FALSE
```

## Memory References

| Address | Purpose |
|---------|---------|
| 0x00629464 | Encrypted cheat code table |
| 0x00629a64 | XOR key "HELP ME!!" |
| 0x00662df4 | g_bDevModeEnabled flag |
| 0x00679ec1 | g_bAllCheatsEnabled flag |

## Known Cheat Indices

| Index | Decrypted Code | Effect |
|-------|----------------|--------|
| 0 | MALLOY | All goodies (works without patch) |
| 1 | TURKEY | All levels |
| 2 | V3R5IOF | Version display (decoded from BEA.exe; no call sites found) |
| 3 | Maladim | God mode (no visible effect - needs investigation) |
| 4 | Aurore | Free camera toggle (debug input) |
| 5 | latête | Goodie gating bypass + state override |

## Callers

- `CFEPGoodies::Initialize` (0x0045c870) - checks index 0 (MALLOY)
- `PauseMenu` - checks index 3 (Maladim) for god mode toggle
- Various game systems

## Important Discovery

**B4K42 is NOT checked by IsCheatActive!**

The source code (`FEPSaveGame.cpp`) shows `B4K42` in the internal/source table, while Ghidra analysis of the Steam binary shows `Maladim` at index 3. Current canonical interpretation is build divergence (source/internal vs Steam retail table), with no confirmed separate retail `B4K42` path.

## Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- The cheat codes use **substring matching** - "MyMALLOYSave" would match MALLOY
- XOR encryption is trivially reversible - the key is stored in plaintext
- This function is a **thiscall** - first parameter is in ECX register
