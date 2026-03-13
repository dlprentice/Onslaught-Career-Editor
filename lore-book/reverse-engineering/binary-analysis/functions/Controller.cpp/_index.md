# Controller.cpp

> Input controller handling functions from BEA.exe

## Overview

Controller.cpp handles input device management, including controller initialization and monitoring. The CController class manages input state, deadzone handling, and controller-to-player mapping.

**Debug Path**: `C:\dev\ONSLAUGHT2\Controller.cpp` (0x00625538)

## Functions

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x005145f0 | CPCController__ctor | RENAMED | PC controller ctor wrapper (installs vtable `0x005e48e0`); source-equivalent of Stuart `CPCController` ctor |
| 0x0042d9d0 | CController__Flush | RENAMED | Copies `mButtons{1,2,3} -> Old`, clears current, then calls vtable+`0x3c` (`DoMappings`). |
| 0x0042db40 | CController__DoMappings | RENAMED | Main mapping engine (push_type switch; drives `CController__SendButtonAction`). |
| 0x005147b0 | CPCController__GetJoyButtonOnce | RENAMED | Joystick button edge `0 -> 1` using per-pad state tables (`old @ 0x00888fa4`, `current @ 0x00888f94`). |
| 0x005147f0 | CPCController__GetJoyButtonOn | RENAMED | Joystick button held state (current table `0x00888f94`). |
| 0x00514810 | CPCController__GetJoyButtonRelease | RENAMED | Joystick button edge `1 -> 0` using old/current tables. |
| 0x00514850 | CPCController__GetKeyOnce | RENAMED | Key edge query (read+clear). Reads `0x00888d94[key]` then clears. |
| 0x00514890 | CPCController__GetKeyOn | RENAMED | Key held query (no clear). Reads `0x00888c94[key]`. |
| 0x00514870 | CPCController__GetKeyState3 | RENAMED | Reads third per-key table `0x00888e94[key]` (semantics TBD). |
| 0x00514640 | CPCController__GetJoyAnalogueLeftX | RENAMED | Reads joystick state `+0x00` and scales by `0.001`. |
| 0x00514670 | CPCController__GetJoyAnalogueLeftY | RENAMED | Reads joystick state `+0x04` and scales by `0.001`. |
| 0x005146a0 | CPCController__GetJoyAnalogueRightX | RENAMED | Reads joystick state `+0x08` and scales by `0.001`. |
| 0x005146d0 | CPCController__GetJoyAnalogueRightY | RENAMED | Reads joystick state `+0x14`, centers at `32768`, scales by `1/32768` (with guard). |
| 0x005148b0 | CPCController__GetJoyPovX | RENAMED | `sin(POV * 0.00017453294)`; returns 0 when POV is `-1`. |
| 0x00514900 | CPCController__GetJoyPovY | RENAMED | `-cos(POV * 0.00017453294)`; returns 0 when POV is `-1`. |
| 0x00514720 | CPCController__RecordControllerState | RENAMED | Writes `mButtons1/2/3` (offsets `+0x14/+0x18/+0x1c`) to `DXMemBuffer` (record/playback support). |
| 0x00514760 | CPCController__ReadControllerState | RENAMED | Reads `mButtons1/2/3`; on EOF closes buffer and clears playback flag (`this+0x161=0`). |
| 0x0042d640 | CController__Init | RENAMED | Base initializer called by `CPCController__ctor` (links controller to player monitor + stores config) |
| 0x0042d810 | CController__InactivityMeansQuitGame | RENAMED | Demo inactivity timeout quit guard (`Controller.cpp:87`) |
| 0x0042e4b0 | CController__GetToControl | RENAMED | Returns current top-of-stack `IController*` |
| 0x0042e610 | CController__SetToControl | RENAMED | Push a monitored `IController*` onto `mToControlStack` |
| 0x0042e6e0 | CController__RelinquishControl | RENAMED | Pop current controller from `mToControlStack` |
| 0x0042e4d0 | CController__SendButtonAction | RENAMED | Routes button input to the top-of-stack `IController` (logs \"Nothing to Control !!\" if empty) |

## Control Bindings

The shipped PC/Steam build persists control bindings in the save/options file “options entries” block (`0x20*N` bytes at file offset `0x24BE`).

Details: `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md`

Key functions:

| Address | Name | Notes |
|---------|------|------|
| 0x0042db10 | OptionsEntries__FindById | Finds a persisted 0x20-byte entry by `entry_id` |
| 0x00453780 | Controls__ApplyPreset | Applies preset; updates `g_ControlSchemeIndex` and entry contents |
| 0x00453f50 | Controls__DispatchRemap | Maps UI action_code to entry_id(s) and calls a write-callback |
| 0x004541e0 | Controls__RemapKey | High-level remap path (sets globals used by callbacks) |
| 0x00454e90 | Controls__ClearDuplicateBinding | Clears duplicates across entries/slots |
| 0x00455010 | ControlsUI__RenderBindingsList | UI renderer + click handler that triggers capture |
| 0x00456080 | Controls__BeginRemapCapture | Starts capture; schedules remap callback |
| 0x004565d0 | OptionsEntries__SetBindingSlot | Writes one slot (field0, device_code, scan, vk) into an entry |

## Details

### CController__InactivityMeansQuitGame (0x0042d810)

- **Purpose**: Returns whether gameplay/frontend should auto-quit due to user inactivity timeout.
- **Source parity**: `references/Onslaught/Controller.cpp:87` (`CController::InactivityMeansQuitGame()`).

**Behavior**:
1. Exits early with `false` unless demo/inactivity gating globals are enabled.
2. Exits early when non-interactive mode is active.
3. Exits early when inactive-timeout config is `<= 0`.
4. Computes elapsed seconds via `PLATFORM__GetSysTimeFloat()` and compares against timeout (ms).
5. Logs timeout trace and returns `true` when threshold is exceeded.

**Called by**:
- `CGame__MainLoop` (`0x0046eee0`)
- `CFrontEnd__Process` (`0x00466ba0`)

### CController__Init (0x0042d640)

- **Purpose**: Initializes a `CController` instance (called by `CPCController__ctor`)
- **Calling Convention**: thiscall (ECX = this pointer)
- **Xref**: Found via debug path at 0x00625538, line 0x3C7 (967)
- **Called From**: `CPCController__ctor` (0x005145f0)

**Behavior**:
1. Sets vtable pointer to 0x005d977c
2. Initializes member fields at offsets 0x04, 0x2C
3. Allocates 4 bytes via memory manager (OID__AllocObject)
4. May allocate additional 16-byte monitor structure (references monitor.h)
5. Initializes controller state fields:
   - Offsets 0x14-0x28: Zeroed (6 dwords - likely axis/button state)
   - Offset 0x160: Byte set to 0
   - Offset 0x161: Byte set to 0
   - Offset 0x164: Float -1.0f (0xBF800000) - possibly deadzone or invalid state
   - Offset 0x168: Float 0.1f (0x3DCCCCCD) - possibly deadzone threshold
   - Offset 0x16C: `input_device` stored
   - Offset 0x170: Set to 0
   - Offset 0x174: `controller_config` stored

**Memory Layout** (partial CController struct):
```
+0x000: vtable pointer (0x005d977c)
+0x004: mToControlStack (CSPtrSet, 0x10 bytes: mFirst/mLast/mIterator/mSize)
+0x014: Input state array[6] (zeroed)
+0x02C: Secondary object (initialized via FUN_00547d70)
+0x160: Byte flag
+0x161: Byte flag
+0x164: Float (default -1.0f)
+0x168: Float (default 0.1f - deadzone?)
+0x16C: input_device
+0x170: Dword (zeroed)
+0x174: controller_config
```

### CPCController__ctor (0x005145f0)

- **Purpose**: PC controller constructor wrapper used by `CGame__LoadLevel` when creating player controllers.

**Behavior**:
1. Calls `CController__Init(this, player, input_device, controller_config)`
2. Overwrites vtable pointer to the final vtable (`0x005e48e0`)
3. Returns `this`

### CPCController__RecordControllerState (0x00514720)

- **Purpose**: Record controller button-bitfield state to the active `DXMemBuffer` (record/playback support).

**Behavior**:
1. `DXMemBuffer__WriteBytes(this + 0x14, 4)`
2. `DXMemBuffer__WriteBytes(this + 0x18, 4)`
3. `DXMemBuffer__WriteBytes(this + 0x1c, 4)`

### CPCController__ReadControllerState (0x00514760)

- **Purpose**: Read controller button-bitfield state from the active `DXMemBuffer` (playback support).

**Behavior**:
1. `DXMemBuffer__ReadBytes(this + 0x14, 4)`
2. `DXMemBuffer__ReadBytes(this + 0x18, 4)`
3. `DXMemBuffer__ReadBytes(this + 0x1c, 4)`
4. If `DXMemBuffer__IsEOF()` is true: closes the buffer and clears playback flag (`this+0x161=0`).

### CController__Flush (0x0042d9d0)

- **Purpose**: Per-frame flush step that captures old button state and triggers mapping.

**Behavior**:
1. Copies `mButtons{1,2,3}` into `mButtons{1,2,3}Old`
2. Clears current `mButtons{1,2,3}`
3. Calls `this->vtable[0xf]()` (`DoMappings`, vtable+`0x3c`)

### CController__DoMappings (0x0042db40)

- **Purpose**: Main controller mapping engine (push_type switch) that emits virtual button actions.

**Notes**:
- Uses a static controller-mapping table (base `0x008892dc`) and per-pad triples (pad0/pad1) within each entry.
- Calls into vtable slots for joystick buttons, key states, and analogue getters, then forwards results to `CController__SendButtonAction`.

### CPCController__GetJoyButtonOnce (0x005147b0)

- **Purpose**: Low-level joystick query for “pressed once” (edge detect).

**Behavior**:
1. Reads old state table pointer from `0x00888fa4[pad_number]`
2. Reads current state table pointer from `0x00888f94[pad_number]`
3. Loads button byte from `state + 0x30 + button`
4. Returns `true` when `old == 0` and `current != 0`

### CPCController__GetJoyButtonOn (0x005147f0)

- **Purpose**: Low-level joystick query for “held” (current pressed state).

**Behavior**:
1. Reads current state table pointer from `0x00888f94[pad_number]`
2. Returns whether `*(state + 0x30 + button) != 0`

### CPCController__GetJoyButtonRelease (0x00514810)

- **Purpose**: Low-level joystick query for “released” (edge detect).

**Behavior**:
1. Reads old/current state tables as above
2. Returns `true` when `old != 0` and `current == 0`

### CController__SetToControl (0x0042e610)

- **Purpose**: Push a new `IController*` onto the controller stack (uses monitor.h deletion tracking)
- **Calling Convention**: thiscall (ECX = `CController* this`)
- **Parameters**: 1 parameter - `IController* to_control`
- **Xref**: Found via debug path at 0x00625538, line 0x3C7 (967)
- **Called From**: Multiple locations including:
  - CGame__RestartLoopRunLevel (0x0046df82)
  - CGame__Update (0x0046ee1b, 0x0046ee49, 0x0046ee60)
  - CGame__Pause (0x0046fb75)
  - CGame__ToggleFreeCameraOn (0x0047057c)
  - FUN_00472b40 (0x00472c02, 0x00472c5c)
  - FUN_004d0810 (0x004d0b00, 0x004d0bd7, 0x004d0d20)

**Behavior**:
1. Allocates a heap `CActiveReader<IController>` (4-byte `mToRead` cell) via `OID__AllocObject`
2. Stores `to_control` in the reader cell (`*reader = to_control`)
3. If `to_control != NULL`, registers the reader in `to_control`'s deletion list:
   - Lazily allocates `to_control->mDeletionEventList` at `to_control + 4` as a `CSPtrSet` (debug path `monitor.h`)
   - `CSPtrSet__AddToHead(to_control->mDeletionEventList, reader)`
   - This is equivalent to the monitor helper `CMonitor__AddDeletionEvent` (`0x00401040`) documented in `reverse-engineering/binary-analysis/functions/monitor.h/_index.md`
4. Pushes the reader onto `this->mToControlStack` via `CSPtrSet__AddToHead(this + 4, reader)`

**Notable Callers**:
- `CGame__Update` calls this function 3 times, suggesting it sets up monitoring for multiple controller/control-handoff paths during gameplay state transitions.

### CController__GetToControl (0x0042e4b0)

- **Purpose**: Returns the currently controlled target (`IController*`) from the top of `mToControlStack`.
- **Source parity**: `references/Onslaught/Controller.cpp:437`.

**Behavior**:
1. Reads stack head pointer at `this+0x04`.
2. Caches head in `this+0x0C` (iterator/cache slot used by subsequent stack helpers).
3. Returns `head->mValue` (`CActiveReader<IController>::ToRead()`), or null when head is null.

### CController__RelinquishControl (0x0042e6e0)

- **Purpose**: Pop the current `IController` from the stack and free its `CActiveReader`
- **Calling Convention**: thiscall (ECX = `CController* this`)

**Behavior**:
1. Reads `mToControlStack.mFirst->mValue` (a `CActiveReader<IController>*`)
2. Removes it from `mToControlStack` (`CSPtrSet__Remove(this+4, value)`)
3. Unlinks from the monitored controller deletion list (`CGenericActiveReader__dtor(value)`)
4. Frees the reader (`OID__FreeObject(value)`)
5. Validates stack is still non-empty (fatal logs if empty)

### CController__SendButtonAction (0x0042e4d0)

- **Purpose**: Main input dispatch for button actions and analogue values
- **Parameters**: `int button`, `float ana_val` (type of `ana_val` inferred; passed through to dispatch)

**Behavior (high level)**:
1. Updates internal per-range button bitfields at `this+0x14/0x18/0x1c`
2. If `mToControlStack.First() == NULL`, logs `"Nothing to Control !!"` and returns
3. Otherwise resolves `to_send = mToControlStack.First()->ToRead()` and dispatches:
   - `button < 0x10`: calls `CommandDispatcher__Handle(this, button, ana_val)` (command/debug path)
   - Otherwise routes to `to_send->ReceiveButtonAction(...)` with reconnect/pause gating

## Related Symbols

- **Vtable**: 0x005d977c (PTR_FUN_005d977c)
- **Vtable (PC controller)**: 0x005e48e0
- **Debug path (Controller.cpp)**: 0x00625538
- **Debug path (monitor.h)**: 0x0062551c
- **Memory manager instance**: 0x009c3df0
- **CSPtrSet__Init**: Lock/monitor initialization
- **CSPtrSet__AddToHead**: Monitor registration
- **CMonitor__AddDeletionEvent**: Lazily allocates/uses `to_control+0x04` deletion list and registers a reader cell (`0x00401040`)
- **CGenericActiveReader__SetReader**: Canonical helper for moving a reader to a new monitor (`0x00401000`)
- **CGenericActiveReader__dtor**: Unregisters an active reader from its monitored object's deletion list (used before freeing)
- **FUN_00547d70**: Secondary initialization routine
- **OID__AllocObject**: Memory allocation (takes size, type, debug_file, line)

## Notes

1. The memory allocator OID__AllocObject signature appears to be: `void* Alloc(size, type_id, debug_file, line_number)`
2. Monitor.h is also referenced, suggesting a separate monitoring/synchronization system
3. The float constants (-1.0f and 0.1f) suggest deadzone or threshold handling for analog inputs
4. CController struct is at least 0x178 bytes based on field accesses
