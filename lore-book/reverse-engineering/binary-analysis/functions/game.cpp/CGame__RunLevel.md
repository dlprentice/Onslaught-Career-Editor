# CGame__RunLevel

> Address: `0x0046e240` | Source: `references/Onslaught/game.cpp:1573`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int CGame__RunLevel(void *this, int aLevel)`)
- **Verified vs Source:** Yes (high-confidence structural match to `CGame::RunLevel`)

## Purpose
Top-level level runner:
- initializes run state and loading flow
- performs init/resource setup
- orchestrates restart-loop iterations
- shuts down and returns final quit code

## Notes
- Calls `CGame__Init`, `CGame__InitRestartLoop`, `CGame__LoadResources`, and `CHud__LoadTextures` during setup.
- Calls `CGame__RestartLoopRunLevel` (`0x0046dc30`) inside a `play_level` loop while handling restart outcomes.
- Handles first-time/restart flags (`mFirstTimeRound`, `mRestarting`) and final shutdown.
- This is the parent driver for one full level run (including retries).
