# con_remotecameraon

> Address: 0x0046bef0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes (free function)
- **Signature Set:** Yes
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:129`)

## Purpose

Console command: `RemoteCameraOn` sets a remote camera on the unit under the crosshairs.

## Notes (Binary Evidence)

- Locates `what = GetUnitOverCrossHair()` via the current player/BattleEngine chain; if null prints:
  - `There is nothing under the crosshair!\n` (`0x0062bbc0`)
- Saves the existing camera as `GAME.mOldRemoteCamera` (`0x008a9e54`) if unset.
- Allocates a `CThingCamera` (RTTI string `.?AVCThingCamera@` at `0x0062bb94`) and assigns it to:
  - `GAME.mRemoteCamera` (`0x008a9e50`)
- Calls `CGame::SetCurrentCamera(player=0, camera, releaseOld=false)` at `0x004705e0`.
- Deletes the previous remote camera if one was already active.

## Related

- Registered in `CGame::InitRestartLoop()` (`CGame__InitRestartLoop`, `0x0046c430`):
  - Name `RemoteCameraOn` at `0x0062bec4`
  - Description `Set a remote camera on the thing under the crosshairs` at `0x0062bed4`
