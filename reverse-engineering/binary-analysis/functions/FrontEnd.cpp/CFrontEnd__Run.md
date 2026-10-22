# CFrontEnd__Run

> Address: 0x004684d0 | Source: `references/Onslaught/FrontEnd.cpp`

## Summary

The main frontend execution loop. Initializes the frontend via `CFrontEnd__Init`, then enters an infinite loop processing page updates and transitions until the user exits to gameplay or quits.

## Signature

```c
// thiscall - ECX = CFrontEnd* this
int CFrontEnd__Run(CFrontEnd* this, int entry, int in_loaded_system);
// Returns: mState value on exit (-1 = exit, -3 = timeout, other = world ID to load)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| this (ECX) | CFrontEnd* | The frontend object |
| entry | int | Source-bridged `EFrontEndEntry` value passed to `CFrontEnd__Init` |
| in_loaded_system | int | Source-bridged loaded-system/loading-range split flag passed to `CFrontEnd__Init` |

Wave467 hardened this saved Ghidra signature/comment from retail stack use plus source `CFrontEnd::Run(EFrontEndEntry, BOOL)`. Runtime frontend behavior and rebuild parity remain unproven.

## Return Values

| Value | Meaning |
|-------|---------|
| -1 | Exit/quit requested or init failed |
| -3 | Demo timeout (playable demo auto-exit) |
| Other | World ID to load (positive value) |

## Key Operations

### 1. Early Exit Check
If `mState` (`this+0xbe14`) is already `-1`, it returns `-1` at once.

*Decompiler listing removed from the public tree (private RE archive: `scrubbed-passages/reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Run.md`, block 1).*

### 2. Initialization
It calls `CFrontEnd__Init(this, entry, in_loaded_system)` and returns `-1` if that fails; otherwise it sets the front-end-active flag `0x00679b40` to `1`.

*Decompiler listing removed from the public tree (private RE archive: `scrubbed-passages/reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Run.md`, block 2).*

### 3. Main Loop
The loop runs until `mState` leaves `-2`. Each pass calls `CFrontEnd__Process`, then repeats `CFrontEnd__Render(0)` until it reports the transition finished. In the playable demo (`0x0083d454 > 0`) the elapsed timer at `this+0xbe18` ends the front end with state `-3` after 60 seconds in mode 3 and after 2 seconds otherwise. On exit it calls vtable slot 8 for cleanup, clears the active flag and returns `mState` (a world id or `-3`).

*Decompiler listing removed from the public tree (private RE archive: `scrubbed-passages/reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Run.md`, block 3).*

## State Machine

The frontend uses `mState` (at offset 0xbe14 from this+4, i.e. dword index 0x2f85) to control flow:

| State | Meaning | Behavior |
|-------|---------|----------|
| -2 | Running | Continue main loop, process updates |
| -1 | Exit | Return immediately, don't enter frontend |
| -3 | Demo Timeout | Exit due to inactivity in demo mode |
| >= 0 | World ID | Exit and load this world |

## Global Variables Used

| Address | Read/Write | Purpose |
|---------|------------|---------|
| DAT_00679b40 | W | Frontend active flag (1 = running, 0 = exited) |
| DAT_0083d454 | R | Playable demo timeout mode |

### Demo Timeout Modes (DAT_0083d454)

| Value | Timeout | Description |
|-------|---------|-------------|
| 0 | None | Normal mode, no timeout |
| 1-2 | 2.0s | Quick timeout (kiosk mode?) |
| 3 | 60.0s | Standard demo timeout |

## Called Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x004662a0 | CFrontEnd__Init | Initialize frontend |
| 0x00466ba0 | CFrontEnd__Process | Frontend per-frame processing (event manager/page/message-box/controller/video updates) |
| 0x00468200 | CFrontEnd__Render | Frontend render pass; loop waits until render succeeds |
| vtable+8 | method_8 | Cleanup on exit |

## Callers

This function is likely called from the main game loop when transitioning to the frontend menu system. The exact caller needs to be identified.

## Flow Diagram

```
CFrontEnd__Run
    |
    v
Check if mState == -1 -----> Return -1 (already exited)
    |
    v
Call CFrontEnd__Init -----> Return -1 (if init fails)
    |
    v
Set DAT_00679b40 = 1 (active)
    |
    v
+-------------------+
| Main Loop         |
|                   |
| if mState != -2:  |---> Exit loop, cleanup, return mState
|   - Cleanup       |
|   - Return        |
|                   |
| if mState == -2:  |
|   - CFrontEnd__Process()|---> Frontend per-frame processing
|   - Wait for      |
|     transitions   |
|   - Check demo    |
|     timeout       |---> Set mState = -3 on timeout
+-------------------+
    ^       |
    +-------+
```

## Notes

1. **Infinite Loop**: The function runs until something sets `mState` to a value other than -2
2. **Virtual Method Call**: Uses vtable method at offset 8 for cleanup, suggesting CFrontEnd has a virtual destructor or cleanup method
3. **Demo Mode**: Special timeout handling for playable demo builds (kiosk/trade show versions)
4. **Frontend Active Flag**: The global `DAT_00679b40` indicates whether the frontend is currently running, useful for other systems to check
