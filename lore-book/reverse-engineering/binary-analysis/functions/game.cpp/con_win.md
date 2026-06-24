# con_win

> Address: 0x0046c180 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes (free function)
- **Signature Set:** Yes
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:184`)

## Purpose

Console command: `Win` declares the level won.

## Notes (Binary Evidence)

- Implements (or inlines) `CGame::DeclareLevelWon()` behavior:
  - Sets game state `g_GameState` at `0x008a9ac0` to `5`.
  - Calls `0x0046fb00` with `(0,0)` (likely `DeclareLevelWon` / win flow).

## Related

- Registered in `CGame::InitRestartLoop()` (`CGame__InitRestartLoop`, `0x0046c430`):
  - Name `Win` at `0x0062be84`
  - Description `Win this level` at `0x0062be88`
