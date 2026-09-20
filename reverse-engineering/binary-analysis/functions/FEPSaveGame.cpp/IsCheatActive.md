# IsCheatActive

Status: mixed — inherited cheat reference with scoped autoconfig identity correction
Last updated: 2026-09-19
Summary: retain the retail early-return behavior while separating autoconfig-test and developer-mode fields.
Source File: `references/Onslaught/FEPSaveGame.cpp` at `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` | Binary: pristine BEA.exe.original.backup, SHA-256 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750

> Address: 0x00465490 | Source: `references/Onslaught/FEPSaveGame.cpp`

## Autoconfig identity correction — September 19

The first read at `00465490` concerns `00662df4`, CLIParams `+3c`, cleared
by its initializer and set by `-autoconfigtest`. It is distinct from developer
selector `00662dd0` (`+18`). Nonzero still takes `004654a0 → 0046551c`, returning
one before index/name processing. The old `g_bDevModeEnabled` name was misleading;
the measured early-return behavior remains valid.

This flag also has automation consumers. On its gated counter branch,
`CGame__Update` clears it at `0046ea2e` and sets byte `00679ec1` at `0046ea34`.
That observation does not audit the complete automation sequence. Source
`FEPSaveGame.cpp`:545–564 has a different, PS2-only `mDevKit` bypass; it must
not supply the retail field identity by analogy.

Private `local-data/test-runs/cli-startup-20260919/selector-neighbors.json`
binds the complete enclosing bodies. This function's `[00465490,0046552b)`
bytes have SHA-256 `39aaeea83c1a3635708e30f6329e68af2435b9c4b7904f62d0d62b4e195dc4fe`.
The current saved signature is `int __thiscall IsCheatActive(void * this, int cheat_index)`;
no database metadata was changed here. The remaining historical cheat effects
and receiver-class interpretation below were not revalidated by this correction.

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes; current saved signature quoted above, without a proven concrete receiver class.
- **Verified vs Source:** Partially (mechanism confirmed, codes differ from source)

## Purpose

XOR-decrypts cheat codes stored in the binary and checks if the current save game name contains the specified cheat code. This is the core function that enables all cheat code functionality in the PC port.

## Historical source-shaped signature
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

- **TRUE (1)**: Query admitted by the name/code match or either early-return flag below
- **FALSE (0)**: Cheat is not active

## Algorithm

```
1. Check CLI autoconfig-test flag +3c (0x00662df4)
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
| 0x00662df4 | CLI autoconfig-test flag; nonzero bypasses name/code checks |
| 0x00679ec1 | g_bAllCheatsEnabled flag |

## Known Cheat Indices

| Index | Decrypted Code | Effect |
|-------|----------------|--------|
| 0 | MALLOY | All goodies (works without patch) |
| 1 | TURKEY | All levels |
| 2 | V3R5IOF | Version display (decoded from BEA.exe; no call sites found) |
| 3 | Maladim | God mode (visible toggle under `Controller Options`; real combat-damage effect confirmed) |
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
