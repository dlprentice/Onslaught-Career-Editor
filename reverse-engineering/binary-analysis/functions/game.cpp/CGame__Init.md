# CGame__Init

> Address: `0x0046c360` | Source: `references/Onslaught/game.cpp:246`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int CGame__Init(void *this)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::Init`)

## Purpose
Core startup initializer used by `CGame__RunLevel` before restart-loop setup:
- initializes core engine/render subsystems
- initializes HUD/interface primitives needed before per-level setup
- registers startup debug CVars
- returns success/failure for early startup gate

## Notes
- This is the source-parity mapping for `CGame::Init()`.
- This function is distinct from `CGame__InitRestartLoop` (`0x0046c430`), which performs per-level/restart state setup and object allocation.
