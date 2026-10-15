# CController__InactivityMeansQuitGame

> Address: `0x0042d810` | Source: `references/Onslaught/Controller.cpp:87`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`int CController__InactivityMeansQuitGame(void)`)
- **Verified vs Source:** Yes (high-confidence structural match to `CController::InactivityMeansQuitGame()`)

## Purpose
Determines whether the game/frontend should auto-quit due to user inactivity timeout.

## Behavior Summary
- Checks demo/inactivity gating globals first.
- Returns `0` when inactivity quitting is disabled, timeout is non-positive, or non-interactive mode is active.
- Uses `PLATFORM__GetSysTimeFloat` to compute elapsed time since last input.
- Returns `1` and emits timeout trace text when elapsed ms exceeds configured timeout.

## Callers
- `CGame__MainLoop` (`0x0046eee0`)
- `CFrontEnd__Process` (`0x00466ba0`)
