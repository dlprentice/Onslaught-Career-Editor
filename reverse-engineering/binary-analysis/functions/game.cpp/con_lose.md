# con_lose

> Address: 0x0046c200 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes (free function)
- **Signature Set:** Yes
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:190`)

## Purpose

Console command: `Lose` declares the level lost.

## Notes (Binary Evidence)

- Calls `0x0046f430` with `(0,0)` (likely `CGame::DeclareLevelLost()` / lose flow).

## Related

- Registered in `CGame::InitRestartLoop()` (`CGame__InitRestartLoop`, `0x0046c430`):
  - Name `Lose` at `0x0062be6c`
  - Description `Lose this level` at `0x0062be74`
