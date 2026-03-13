# CGame__ToggleFreeCameraOn

> Address: 0x00470430 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Mostly (`references/Onslaught/game.cpp:CGame::ToggleFreeCameraOn`)

## Purpose
Enables free camera mode for a player:

- Saves the current camera into `mOldCamera[player]`
- Allocates a controllable camera and hands it to the controller
- Switches the current camera to the controllable camera
- Sets `mFreeCameraOn[player] = TRUE`
- Records whether the game was paused when free cam started (`mPauseOnWhenStartedFreeCam[player]`)

This is invoked from the debug button path in `CGame__ReceiveButtonAction` when Aurore is active.

## Signature
```c
// __thiscall, pops 0x4 (1 arg)
void CGame::ToggleFreeCameraOn(int player);
```

## Source Cross-Check
Matches `references/Onslaught/game.cpp:3240`:
```cpp
void CGame::ToggleFreeCameraOn(int playernumber) {
    mOldCamera[playernumber] = GetCurrentCamera(playernumber);
    // create CControllableCamera(...)
    mController[playernumber]->SetToControl(c);
    SetCurrentCamera(playernumber, c, false);
    mFreeCameraOn[playernumber] = TRUE;
    mPauseOnWhenStartedFreeCam[playernumber] = (mPause == TRUE);
}
```

## Related Functions
- `CGame__SetCurrentCamera` (`0x004705e0`)
- `CGame__ReceiveButtonAction` (`0x0046f7e0`) (Aurore-gated entry point)

