# CFrontEnd__Run

> Address: 0x004684d0 | Source: `references/Onslaught/FrontEnd.cpp`

## Summary

The main frontend execution loop. Initializes the frontend via `CFrontEnd__Init`, then enters an infinite loop processing page updates and transitions until the user exits to gameplay or quits.

## Signature

```c
// thiscall - ECX = CFrontEnd* this
int CFrontEnd__Run(CFrontEnd* this, int param_1, int param_2);
// Returns: mState value on exit (-1 = exit, -3 = timeout, other = world ID to load)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| this (ECX) | CFrontEnd* | The frontend object |
| param_1 | int | Start mode (passed to CFrontEnd__Init) |
| param_2 | int | Progress bar mode (passed to CFrontEnd__Init) |

## Return Values

| Value | Meaning |
|-------|---------|
| -1 | Exit/quit requested or init failed |
| -3 | Demo timeout (playable demo auto-exit) |
| Other | World ID to load (positive value) |

## Key Operations

### 1. Early Exit Check
```c
if (this->field_0xbe14 == -1) {  // mState == -1
    return -1;
}
```

### 2. Initialization
```c
int result = CFrontEnd__Init(this, param_1, param_2);
if (result == 0) {
    return -1;  // Init failed
}
DAT_00679b40 = 1;  // Frontend is now active
```

### 3. Main Loop
```c
do {
    if (mState != -2) {
        // Exit loop - call cleanup via vtable
        (*this->vtable->method_8)();
        DAT_00679b40 = 0;  // Frontend no longer active
        return mState;  // Return final state (world ID or -3)
    }

    // Process frontend update
    CFrontEnd__Process();  // Frontend per-frame processing

    // Handle transition waiting
    if (mState == -2) {
        while (CFrontEnd__Render(0) == 0) {
            // Wait for transition to complete
        }
    }

    // Playable demo timeout handling
    if (DAT_0083d454 > 0) {
        if (DAT_0083d454 == 3) {
            if (this->field_0xbe18 > 60.0f) {
                this->field_0xbe14 = -3;  // 60-second timeout
            }
        } else {
            if (this->field_0xbe18 > 2.0f) {
                this->field_0xbe14 = -3;  // 2-second timeout
            }
        }
    }
} while (true);
```

## State Machine

The frontend uses `mState` (at offset 0xbe14 from this+4, so 0x2f85*4 in the decompiled code) to control flow:

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
