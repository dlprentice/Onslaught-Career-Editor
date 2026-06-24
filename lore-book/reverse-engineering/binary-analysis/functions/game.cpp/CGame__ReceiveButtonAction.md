# CGame__ReceiveButtonAction

> Address: 0x0046f7e0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__ReceiveButtonAction(void *this, void *from_controller, int button)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::ReceiveButtonAction`, `references/Onslaught/Controller.h` button IDs)

## Purpose
Handles **debug button** actions (button IDs `0..14`) and routes them to game/debug behaviors (god mode, free camera, console menu navigation, win/lose level, etc).

This is the binary entry point that contains the **Aurore (cheat index 4)** gate for free camera toggling in the PC port.

## Signature
```c
// Source has (from_controller, button, float val); retail binary currently decompiles with
// button-dispatch usage and no explicit float-val usage.
void CGame__ReceiveButtonAction(void *this, void *from_controller, int button);
```

## Button Map (BEA.exe)
Button IDs come from `references/Onslaught/Controller.h` ("Debug buttons").

| Button | Define | Jump Target | Behavior (Observed) | Notes |
|--------|--------|-------------|---------------------|------|
| 0 | `BUTTON_TOGGLE_GOD_MODE` | `0x0046f7fa` | Toggle `mPlayer[n]->IsGod()` for all players | Matches source switch body. |
| 1 | `BUTTON_TOGGLE_FREE_CAMERA` | `0x0046f82e` | Toggle free camera on/off for all players | **Gated by** `IsCheatActive(4)` (Aurore) in this build. |
| 2 | `BUTTON_ADVANCE_ONE_FRAME` | `0x0046f8bd` | Set `mAdvanceFrame = TRUE` | Writes `this+0x9CC = 1`. |
| 3 | `BUTTON_TOGGLE_DEBUG_SQUAD_FORWARD` | `0x0046f90d` | `ToggleDebugSquadForward()` | Calls `0x0046fe20`. |
| 4 | `BUTTON_TOGGLE_DEBUG_SQUAD_BACKWARD` | `0x0046f91b` | `ToggleDebugSquadBackward()` | Calls `0x0046fd40`. |
| 5 | `BUTTON_TOGGLE_DEBUG_UNIT_FORWARD` | `0x0046f929` | `ToggleDebugUnitForward()` | Calls `0x0046fb80`. |
| 6 | `BUTTON_TOGGLE_DEBUG_UNIT_BACKWARD` | `0x0046f937` | `ToggleDebugUnitBackward()` | Calls `0x0046fc40`. |
| 7 | `BUTTON_SKIP_CUTSCENE` | `0x0046f8ce` | Skip current cutscene | Calls `0x0043fcd0` (likely `CCutscene::SkipCutscene`). |
| 8 | `BUTTON_CONSOLE_MENU_UP` | `0x0046f8da` | `CONSOLE.MenuUp()` | Calls `0x0042ba90` with `ECX=0x00663498` (CONSOLE global). |
| 9 | `BUTTON_CONSOLE_MENU_DOWN` | `0x0046f8eb` | `CONSOLE.MenuDown()` | Calls `0x0042bac0`. |
| 10 | `BUTTON_CONSOLE_MENU_SELECT` | `0x0046f8fc` | `CONSOLE.MenuSelect()` | Calls `0x0042bb30`. |
| 11 | `BUTTON_WIN_LEVEL` | `0x0046f945` | Developer-mode win level | Randomizes `mScore` within `[mDGradeScore..mSGradeScore)`, sets end-of-level countdown, calls pause/menu flow. |
| 12 | `BUTTON_LOOSE_LEVEL` | `0x0046fa39` | Developer-mode lose level | Similar gating to win-level, then calls a lose-level handler (`0x0046f430`). |
| 13 | `BUTTON_LOG_CAREER` | `0x0046fa88` | Unimplemented in this build | Falls through to the default "unknown command" handler. |
| 14 | `BUTTON_COMPLETE_ALL_OBJECTIVES` | `0x0046f9f3` | Mark all objectives complete | Prints `"Completing all Objectives"`, then writes objective state arrays. |

Out-of-range `button > 14` prints: `"ERROR: Unknown command sent to onslaught demo"`.

## Aurore Gate (PC Port Difference)
In Stuart's source, `BUTTON_TOGGLE_FREE_CAMERA` is not gated by a cheat code. In this BEA.exe build, the case begins with:

- `IsCheatActive(4)` (Aurore) at `0x0046f835`
- If inactive: returns without toggling free camera.

This is why Aurore is described as a "debug command gate" in earlier notes: it unlocks a debug-only button action.

## Related Functions
- `0x00465490` `IsCheatActive` (Aurore gate)
- `0x00470430` `CGame__ToggleFreeCameraOn` (called when turning free camera on)
- `0x004705e0` `CGame__SetCurrentCamera` (used when turning free camera off)
- `0x004705d0` `CGame__GetController` (used for vibration control and free-cam control handoff)
