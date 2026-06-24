# con_navmapoff

> Address: 0x0046c150 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes (free function)
- **Signature Set:** Yes
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:177`)

## Purpose

Console command: `NavMapOff` disables the navigation map display and forces a screen update.

## Notes (Binary Evidence)

- Sets `g_LandscapeNavDisplayEnabled` at `0x0089ce44` to `0`.
- Calls `ENGINE.UpdateArea(0,0,512,512)` (function at `0x0044a6b0`), passing `0x200` dimensions.

## Related

- Registered in `CGame::InitRestartLoop()` (`CGame__InitRestartLoop`, `0x0046c430`):
  - Name `NavMapOff` at `0x0062bdd4`
  - Description `Turn the navigation map off` at `0x0062bde0`
