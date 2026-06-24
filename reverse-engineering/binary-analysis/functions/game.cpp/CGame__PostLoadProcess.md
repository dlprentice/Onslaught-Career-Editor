# CGame__PostLoadProcess

> Address: `0x0046d040` | Source: `references/Onslaught/game.cpp:764`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int CGame__PostLoadProcess(void *this)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::PostLoadProcess`)

## Purpose
Runs post-load world validation and player/start setup:
- initializes/resets atmospherics and map state
- resolves/assigns player start positions
- finalizes post-load world sorting/setup stages
- returns success/failure before gameplay pass begins

## Notes
- Returns non-zero on success and zero on failure.
- Called by `CGame__RestartLoopRunLevel` after `CGame__LoadLevel`.
