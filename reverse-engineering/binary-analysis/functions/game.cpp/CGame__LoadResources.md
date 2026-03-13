# CGame__LoadResources

> Address: `0x0046cd30` | Source: `references/Onslaught/game.cpp:624`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int CGame__LoadResources(int aLevel, int inLoadedSounds)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::LoadResources`)

## Purpose
Loads per-level runtime resources:
- level resource bundle accumulation
- texture/mesh level resources
- particle set load and effect initialization
- loading-range progression based on `inLoadedSounds`

## Notes
- Binary signature does not currently expose `this` as an explicit parameter in decompile output.
- Returns non-zero on success and zero on load failure.
- Called from `CGame__RunLevel` before one-off and restart-loop resource setup.
