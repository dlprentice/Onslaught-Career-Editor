# CGame__LoadLevel

> Address: `0x0046cdf0` | Source: `references/Onslaught/game.cpp:685`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int CGame__LoadLevel(void *this, int aLevel)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::LoadLevel`)

## Purpose
Loads the selected level and constructs runtime player-side objects:
- sets current level state
- loads world file/data
- creates per-player camera/controller/player object chain
- prepares geometry/tree build and load-screen state

## Notes
- Returns non-zero on success and zero on failure.
- Called from `CGame__RestartLoopRunLevel` and feeds into `CGame__PostLoadProcess`.
