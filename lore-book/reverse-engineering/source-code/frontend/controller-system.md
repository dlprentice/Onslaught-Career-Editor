# Controller System

## PC Controller System (PCController.cpp/h)

> Analysis added December 2025

**Purpose**: Platform-specific input handling for PC, including gamepad/joystick support, keyboard mappings, and the debug key system that enabled developer cheats in internal builds.

### Class Structure

The controller system uses a platform abstraction pattern:

```
CController (base class, Controller.h/cpp)
    ├── CPCController (PC - DirectInput)
    ├── CPS2Controller (PlayStation 2)
    └── CXBOXController (Xbox)
```

**CPCController** inherits from **CController** and provides PC-specific implementations for:

| Virtual Method | PC Implementation |
|----------------|-------------------|
| `GetJoyButtonOnce()` | `LT.JoyButtonOnce()` - DirectInput single press |
| `GetJoyButtonOn()` | `LT.JoyButtonOn()` - DirectInput held state |
| `GetJoyButtonRelease()` | `LT.JoyButtonRelease()` - DirectInput release detect |
| `GetKeyOnce()` | `PLATFORM.KeyOnce()` - Keyboard single press |
| `GetKeyOn()` | `PLATFORM.KeyOn()` - Keyboard held state |
| `GetJoyAnalogueLeftX/Y()` | Joystick left stick (normalized -1.0 to 1.0) |
| `GetJoyAnalogueRightX/Y()` | Joystick right stick (normalized -1.0 to 1.0) |
| `RecordControllerState()` | Write input state to file |
| `ReadControllerState()` | Read input state from file |

### Retail (Steam) Confirmed Mappings (BEA.exe)

In the Steam `BEA.exe`, the PC controller vtable at `0x005e48e0` points to concrete helpers for joystick/keyboard queries and record/playback support.

Note: these are safe to re-verify via address-level read-back after any Ghidra restart/deadlock; do not assume symbol names persisted without checking.

| Address | Symbol | Behavior |
|---------|--------|----------|
| 0x005147b0 | `CPCController__GetJoyButtonOnce` | Returns true when `old == 0` and `current != 0` for `state[pad] + 0x30 + button` (`old @ 0x00888fa4`, `current @ 0x00888f94`) |
| 0x005147f0 | `CPCController__GetJoyButtonOn` | Returns true when `current != 0` for `state[pad] + 0x30 + button` (`current @ 0x00888f94`) |
| 0x00514810 | `CPCController__GetJoyButtonRelease` | Returns true when `old != 0` and `current == 0` for `state[pad] + 0x30 + button` (`old @ 0x00888fa4`, `current @ 0x00888f94`) |
| 0x00514850 | `CPCController__GetKeyOnce` | Returns+clears `0x00888d94[key]` (per-key one-shot/edge state) |
| 0x00514890 | `CPCController__GetKeyOn` | Returns `0x00888c94[key]` (per-key held state) |
| 0x00514870 | `CPCController__GetKeyState3` (TBD) | Returns `0x00888e94[key]` (third per-key state table; meaning still TBD) |
| 0x00514640 | `CPCController__GetJoyAnalogueLeftX` | Reads joystick state `+0x00` and scales by `0.001` |
| 0x00514670 | `CPCController__GetJoyAnalogueLeftY` | Reads joystick state `+0x04` and scales by `0.001` |
| 0x005146a0 | `CPCController__GetJoyAnalogueRightX` | Reads joystick state `+0x08` and scales by `0.001` |
| 0x005146d0 | `CPCController__GetJoyAnalogueRightY` | Reads joystick state `+0x14`, centers at `32768`, scales by `1/32768` (guarded) |
| 0x005148b0 | `CPCController__GetJoyPovX` | `sin(POV * 0.00017453294)`; returns 0 when POV is `-1` |
| 0x00514900 | `CPCController__GetJoyPovY` | `-cos(POV * 0.00017453294)`; returns 0 when POV is `-1` |
| 0x0042d9d0 | `CController__Flush` | Copies button bitfields into `Old`, clears current, calls `DoMappings` (vtable+`0x3c`) |
| 0x0042db40 | `CController__DoMappings` | Main mapping engine (push_type switch) that drives `SendButtonAction` |
| 0x00514720 | `CPCController__RecordControllerState` | Writes `mButtons1/2/3` into `DXMemBuffer` (3x4 bytes: `this+0x14/+0x18/+0x1c`) |
| 0x00514760 | `CPCController__ReadControllerState` | Reads `mButtons1/2/3`; on EOF closes buffer and clears `mPlaying` (`this+0x161=0`) |

**Retail deltas vs Stuart header**:
- A third key-state vtable entry exists (`0x00514870`), which is not present in `references/Onslaught/Controller.h` (likely a release-edge table).
- POV hat helpers exist (`0x005148b0`/`0x00514900`) and compute sin/cos from DirectInput POV degrees.

### Debug Keyboard Shortcuts

**Source/internal mapping with Steam caveat:** These debug-key bindings exist in internal/source code; in the Steam retail build analyzed here, their gameplay handlers are not observed as active:

| Key | Virtual Button | Effect | Notes |
|-----|----------------|--------|-------|
| `V` | `BUTTON_TOGGLE_GOD_MODE` | Toggle god mode | **Internal builds only** |
| `A` | `BUTTON_TOGGLE_FREE_CAMERA` | Toggle free camera | Debug camera mode |
| `F` | `BUTTON_TOGGLE_FREE_CAMERA` | Toggle free camera | Alternate binding |
| `U` | `BUTTON_WIN_LEVEL` | Force win current level | Instant victory |
| `I` | `BUTTON_LOOSE_LEVEL` | Force lose current level | Instant defeat |
| `S` | `BUTTON_SAVE_CAREER` | Save career | Debug save hotkey |
| `L` | `BUTTON_LOAD_CAREER` | Load career | Debug load hotkey |
| `Z` | `BUTTON_LOG_CAREER` | Log career to debug output | Debug dump |
| `O` | `BUTTON_PAUSE` | Pause game | Alternate pause key |
| `7` | `BUTTON_COMPLETE_ALL_OBJECTIVES` | Complete all objectives | Skip to win state |
| `8` | `BUTTON_TOGGLE_DEBUG_SQUAD_BACKWARD` | Cycle debug squad backward | Debug visualization |
| `9` | `BUTTON_TOGGLE_DEBUG_SQUAD_FORWARD` | Cycle debug squad forward | Debug visualization |
| `4` | `BUTTON_TOGGLE_DEBUG_UNIT_BACKWARD` | Cycle debug unit backward | Debug visualization |
| `5` | `BUTTON_TOGGLE_DEBUG_UNIT_FORWARD` | Cycle debug unit forward | Debug visualization |

**Why V-key God Mode Doesn't Work in Retail:**

The `BUTTON_TOGGLE_GOD_MODE` mapping exists in source code, but in the Steam retail build analyzed here we have not observed an active `GAME.ReceiveButtonAction()` path for it; current evidence suggests that case is disabled or compiled out in retail.

### Virtual Button System

The controller uses a **virtual button abstraction** layer. Physical inputs (keys, gamepad buttons) map to virtual buttons, which are then dispatched to the appropriate game system.

**Debug Buttons (0-15)**: Special buttons that bypass normal control flow and go directly to `GAME.ReceiveButtonAction()`:

| Constant | Value | Purpose |
|----------|-------|---------|
| `BUTTON_TOGGLE_GOD_MODE` | 0 | Toggle invincibility |
| `BUTTON_TOGGLE_FREE_CAMERA` | 1 | Debug camera |
| `BUTTON_ADVANCE_ONE_FRAME` | 2 | Frame advance (paused) |
| `BUTTON_TOGGLE_DEBUG_SQUAD_FORWARD` | 3 | Debug visualization |
| `BUTTON_TOGGLE_DEBUG_SQUAD_BACKWARD` | 4 | Debug visualization |
| `BUTTON_TOGGLE_DEBUG_UNIT_FORWARD` | 5 | Debug visualization |
| `BUTTON_TOGGLE_DEBUG_UNIT_BACKWARD` | 6 | Debug visualization |
| `BUTTON_SKIP_CUTSCENE` | 7 | Skip cinematics |
| `BUTTON_CONSOLE_MENU_UP` | 8 | Console navigation |
| `BUTTON_CONSOLE_MENU_DOWN` | 9 | Console navigation |
| `BUTTON_CONSOLE_MENU_SELECT` | 10 | Console navigation |
| `BUTTON_WIN_LEVEL` | 11 | Force win |
| `BUTTON_LOOSE_LEVEL` | 12 | Force lose |
| `BUTTON_LOG_CAREER` | 13 | Career debug dump |
| `BUTTON_COMPLETE_ALL_OBJECTIVES` | 14 | Instant objective completion |

**Action Buttons (16+)**: Normal gameplay buttons that go to the controlled object:

| Constant | Value | Purpose |
|----------|-------|---------|
| `BUTTON_MECH_CHANGE_ZOOM_IN` | 16 | Zoom in |
| `BUTTON_MECH_CHANGE_ZOOM_OUT` | 17 | Zoom out |
| `BUTTON_MECH_FIRE_GUN_POD` | 18 | Fire weapon |
| `BUTTON_MECH_CHARGE_GUN_POD` | 19 | Charge weapon |
| `BUTTON_MECH_CHANGE_WEAPON` | 20 | Cycle weapons |
| `BUTTON_MECH_LANDING_JETS` | 21 | Landing jets |
| `BUTTON_MECH_JET_AFTERBURNER` | 22 | Afterburner |
| `BUTTON_MECH_YAW_LEFT` | 25 | Turn left |
| `BUTTON_MECH_PITCH_UP` | 26 | Pitch up |
| `BUTTON_MECH_YAW_RIGHT` | 27 | Turn right |
| `BUTTON_MECH_PITCH_DOWN` | 28 | Pitch down |
| `BUTTON_MECH_STRAFE_LEFT` | 29 | Strafe left |
| `BUTTON_MECH_STRAFE_RIGHT` | 30 | Strafe right |
| `BUTTON_MECH_FORWARD` | 31 | Move forward |
| `BUTTON_MECH_BACKWARD` | 32 | Move backward |
| `BUTTON_MECH_MORPH` | 33 | Transform walker/jet |
| `BUTTON_PAUSE` | 56 | Pause game |
| `BUTTON_HELP` | 57 | Help/objectives |
| `TOTAL_BUTTONS` | 67 | Max button count |

### Input Push Types

The mapping system supports multiple input detection modes:

| Type | Constant | Behavior |
|------|----------|----------|
| `BUTTON_ON` | 0 | True while held |
| `BUTTON_ONCE` | 1 | True on first press only |
| `BUTTON_RELEASE` | 2 | True on release |
| `BUTTON_REPEAT` | 3 | Auto-repeat while held |
| `ANALOGUE_PLUS` | 4 | Analog stick positive direction |
| `ANALOGUE_MINUS` | 5 | Analog stick negative direction |
| `ANALOGUE_PLUS_ACT_AS_BUTTON_REPEAT` | 6 | Analog as repeating button (positive) |
| `ANALOGUE_MINUS_ACT_AS_BUTTON_REPEAT` | 7 | Analog as repeating button (negative) |
| `KEY_ONCE` | 8 | Keyboard single press |
| `KEY_ON` | 9 | Keyboard held state |

### Controller Configurations (1-4)

The game supports 4 controller layouts, switchable in options. Each configuration remaps the analog sticks:

| Config | Left Stick | Right Stick | Morph | Landing Jets |
|--------|------------|-------------|-------|--------------|
| 1 | Strafe + Forward/Back | Yaw + Pitch | Button 2 | Button 1 |
| 2 | Yaw + Pitch | Strafe + Forward/Back | Button 2 | Button 1 |
| 3 | Strafe + Forward/Back | Yaw + Pitch | Button 1 | Button 2 |
| 4 | Yaw + Pitch | Strafe + Forward/Back | Button 1 | Button 2 |

**Retail evidence (Steam build, Feb 2026):** UI/control-hint rendering in `FUN_0047fb50` checks `mControllerConfigurationNum[1]` against `3` and `4`, consistent with configs where Morph/Landing-Jets bindings are swapped (and thus prompt mapping differs).

**Configuration -1**: Applies to ALL configurations (shared bindings like debug keys, menu navigation).

### Gamepad Button Numbers

The source code uses numeric button indices that map to standard PC gamepad layouts:

| Button # | Typical Mapping | Usage in BEA |
|----------|-----------------|--------------|
| 0 | A / Cross | Menu select (alternate) |
| 1 | B / Circle | Menu select, Landing jets |
| 2 | X / Square | Morph |
| 3 | Y / Triangle | Help, Menu back |
| 4 | LB / L1 | Change weapon (alternate) |
| 5 | RB / R1 | Fire/charge weapon (alternate) |
| 6 | LT / L2 | Change weapon, Cheat combo |
| 7 | RT / R2 | Fire/charge weapon, Cheat combo |
| 8 | Select/Back | Select button |
| 9 | Start | Afterburner (held) |
| 10 | L3 | - |
| 11 | R3 | Pause/Start |
| 12 | D-Pad Up | Menu up, Zoom in |
| 13 | D-Pad Right | Config up |
| 14 | D-Pad Down | Menu down, Zoom out |
| 15 | D-Pad Left | Config down |

### Analog Stick Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `ANALOGUE_X1` | -1 | Left stick horizontal |
| `ANALOGUE_Y1` | -2 | Left stick vertical |
| `ANALOGUE_X2` | -3 | Right stick horizontal |
| `ANALOGUE_Y2` | -4 | Right stick vertical |
| `ANALOGUE_X_DEAD` | 0.36f | Horizontal deadzone (36%) |
| `ANALOGUE_Y_DEAD` | 0.36f | Vertical deadzone (36%) |
| `ANALOGUE_BUTTON_DEAD` | 0.3f | Analog-as-button threshold |
| `ANALOGUE_ACT_AS_DIGITAL_THRESHOLD` | 0.9f | Analog to digital conversion |

**Note**: The Xbox controllers required "really huge dead zones" (0.36) according to the source code comment.

### Input Recording/Playback System

The controller includes a demo recording system for QA and attract modes:

```cpp
// From Controller.cpp
void CController::StartRecording(char *filename) {
    mRecording = true;
    mDataFile.InitFromMem(filename);
}

void CController::StartPlayback(char *filename) {
    mPlaying = true;
    mDataFile.InitFromFile(filename);
}
```

**Recorded State** (per frame):

| Data | Size | Description |
|------|------|-------------|
| `mButtons1` | 4 bytes | Button bits 0-31 |
| `mButtons2` | 4 bytes | Button bits 32-63 |
| `mButtons3` | 4 bytes | Button bits 64-95 |
| `mAnaloguex1` | 4 bytes | Left stick X |
| `mAnaloguey1` | 4 bytes | Left stick Y |
| `mAnaloguex2` | 4 bytes | Right stick X |
| `mAnaloguey2` | 4 bytes | Right stick Y |

**Total**: 28 bytes per frame of input recording.

This system is used by:
- `-record FILENAME` CLI parameter (record gameplay)
- `-play FILENAME` CLI parameter (playback demo)
- Attract mode (auto-play when idle)

### Cheat Combo Detection

The controller implements a shoulder button combo for activating the cheat input screen:

```cpp
// From Controller.cpp DoMappings()
#ifdef E3BUILD
if (IsButtonSet(BUTTON_LEFT1_FOR_TOGGLE) &&
    IsButtonSet(BUTTON_RIGHT1_FOR_TOGGLE) &&
    mAnaloguex1 < -0.6f &&
    mAnaloguex2 >  0.6f)
#else
if (IsButtonSet(BUTTON_LEFT1_FOR_TOGGLE) &&
    IsButtonSet(BUTTON_RIGHT1_FOR_TOGGLE))
#endif
{
    SendButtonAction(BUTTON_FRONTEND_CHEAT, 0.0f);
}
```

- **Normal builds**: Hold L1+R1 simultaneously
- **E3 Build**: L1+R1 + push both sticks outward (harder to trigger accidentally)

This explains how `!EVAH!` and `105770Y2` cheat codes are entered - the shoulder combo brings up a text input screen.

### Inactivity Timer

The controller tracks user inactivity for attract mode:

| Constant/Member | Purpose |
|-----------------|---------|
| `mLastTimeAnythingPressed` | Timestamp of last input |
| `mNonInteractiveSection` | True during cutscenes (pauses timer) |
| `CLIPARAMS.mInactiveTimeout` | Timeout in milliseconds |
| `InactivityMeansQuitGame()` | Returns true when timeout exceeded |

Used in **Playable Demo** builds to return to attract mode when no input is detected.

### Button Repeat System

Auto-repeat for held buttons (menu navigation):

| Constant | Value | Purpose |
|----------|-------|---------|
| `INITIAL_REPEAT_DELAY` | 0.5f | Delay before first repeat |
| `REPEAT_DELAY` | 0.12f | Delay between subsequent repeats |

### Connection to God Mode Investigation

**Summary of Debug Key System Findings:**

1. The `V` key is mapped to `BUTTON_TOGGLE_GOD_MODE` (virtual button 0)
2. Debug buttons (0-15) are routed to `GAME.ReceiveButtonAction()` directly
3. The handler in `CGame::ReceiveButtonAction()` processes the god mode toggle
4. **In the Steam retail build analyzed here**, this handler is not currently observed as active (likely disabled/compiled out)

Current evidence indicates that:
- God mode WAS toggleable via `V` key in internal builds
- The input mapping survived, but the handler did not
- In the **source/internal build**, B4K42 save-name check is the only confirmed god mode path
- In the Steam PC port, the equivalent name check is `Maladim`, but it shows **no visible effect** in user testing (Dec 2025)
- Memory trainers work because they bypass the input system entirely

### Files Analyzed for This Section

| File | Purpose |
|------|---------|
| `PCController.cpp` | PC controller implementation, button mappings table |
| `PCController.h` | CPCController class definition |
| `Controller.cpp` | Base controller class, input dispatch logic |
| `Controller.h` | Virtual button constants, push types, mapping struct |

---

## Complete Virtual Button Constants (0-67)

### Debug Buttons (0-15)

| Constant | Value | Mapped Key |
|----------|-------|------------|
| `BUTTON_TOGGLE_GOD_MODE` | 0 | V |
| `BUTTON_TOGGLE_FREE_CAMERA` | 1 | A, F |
| `BUTTON_ADVANCE_ONE_FRAME` | 2 | - |
| `BUTTON_TOGGLE_DEBUG_SQUAD_FORWARD` | 3 | 9 |
| `BUTTON_TOGGLE_DEBUG_SQUAD_BACKWARD` | 4 | 8 |
| `BUTTON_TOGGLE_DEBUG_UNIT_FORWARD` | 5 | 5 |
| `BUTTON_TOGGLE_DEBUG_UNIT_BACKWARD` | 6 | 4 |
| `BUTTON_SKIP_CUTSCENE` | 7 | Space |
| `BUTTON_WIN_LEVEL` | 11 | U |
| `BUTTON_LOOSE_LEVEL` | 12 | I |
| `BUTTON_LOG_CAREER` | 13 | Z |
| `BUTTON_COMPLETE_ALL_OBJECTIVES` | 14 | 7 |

### NEW Debug Keys Not Previously Documented

- `O` = Pause (keyboard alternative)
- `A` and `F` = Free camera toggle (two bindings!)
- `8`/`9` = Debug squad cycling
- `4`/`5` = Debug unit cycling
- Numpad 2/8 = Debug console navigation

---
