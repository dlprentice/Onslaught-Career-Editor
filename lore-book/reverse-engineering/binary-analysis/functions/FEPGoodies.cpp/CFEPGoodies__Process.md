# CFEPGoodies__Process

> Address: 0x0045d7e0 | Source: `references/Onslaught/FEPGoodies.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Partial

## Purpose

Frontend goodies gallery update/process loop. Notably computes cheat-derived flags used to override goodie gating/display behavior.

## Evidence

- Calls `IsCheatActive(&FRONTEND.mFEPSaveGame, idx)` at `0x0045d7f4` and `0x0045d80b`, then normalizes the result to `0/1`.
  - `IsCheatActive(0)` (MALLOY) is stored into `g_Cheat_MALLOY` at `0x006798b0`.
  - `IsCheatActive(5)` (decoded as `lat\xEAte`) is stored into `g_Cheat_LATETE` at `0x006798b4`.
- Subsequent goodies UI logic uses these globals to override the effective goody state read from:
  - `CCareer.mGoodies[]` at `0x00660620 + 0x1F44 = 0x00662564`
  - Example reads: `0x0045e4cb`, `0x0045e64e`

## Source Cross-Check

In Stuart's source (`references/Onslaught/FEPGoodies.cpp:1550`), `CFEPGoodies::Process()` computes a local `ischeatactive` using only `IsCheatActive(0)`. The ported binary extends this to a second cheat (index 5) and uses globals (`0x006798b0`, `0x006798b4`) to affect multiple UI paths.

## Notes

- Treat the mapping to `CFEPGoodies::Process` as **probable** until we finish signature/struct-offset verification in Ghidra.
