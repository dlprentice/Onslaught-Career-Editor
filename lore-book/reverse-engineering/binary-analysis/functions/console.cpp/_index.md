# console.cpp - Function Mappings

Source file: `C:\dev\ONSLAUGHT2\console.cpp`
Debug string address: `0x00624d0c`

## Overview

The CConsole class implements an in-game developer console system with support for:
- Console commands (with callbacks)
- Console variables (cvars)
- Key bindings
- Command history
- Script execution
- Loading screen progress/range rendering helpers used by `CFrontEnd` and `CGame`

## CConsole Class Layout (Partial)

Based on member access patterns in the decompiled code:

| Offset | Type | Member | Notes |
|--------|------|--------|-------|
| 0x0004 | char[60][128] | Command history buffer | 60 entries, 128 chars each |
| 0x1E84 | char[10][128] | Recent commands | 10 entries, 128 chars each |
| 0x238C | byte | Unknown flag | |
| 0x238D | byte | Unknown flag | |
| 0x2390 | int | Console alpha | Background transparency (default: 200) |
| 0x2394 | CConsoleCmd* | Command list head | Linked list of registered commands |
| 0x2398 | CConsoleVar* | Variable list head | Linked list of registered variables |
| 0x239C | void* | Unknown pointer | |
| 0x23A0 | void* | Unknown pointer | |
| 0x23A4 | void* | Unknown pointer | |
| 0x23B0 | void* | Unknown pointer | |
| 0x23B4 | int | Unknown (-1 init) | |
| 0x23B8 | int | Unknown (1 init) | |
| 0x23BC | char[256][128] | Output line buffer | 256 lines, 128 chars each |
| 0xB3C0 | int | Unknown (-1 init) | |
| 0xB3C4 | byte | Unknown flag | |
| 0xB3C5 | byte | Unknown (set to 1) | |
| 0xB3C6 | byte | Unknown flag | |
| 0xB3C8 | int | Unknown | |
| 0xB3D0 | int | Unknown | |
| 0xB3D8 | float | mLoadingRangeMin | Loading progress range start (%) |
| 0xB3DC | float | mLoadingRangeMax | Loading progress range end (%) |
| 0xB3E0 | float | mLoadingCurrent | Current loading progress (%) |

## CConsoleCmd Structure (0xAC bytes)

| Offset | Type | Member | Notes |
|--------|------|--------|-------|
| 0x00 | char[32] | Name | Command name |
| 0x20 | char[128] | Description | Help text |
| 0xA0 | void* | Callback | Function pointer for command handler |
| 0xA4 | char | Flags | Command flags |
| 0xA8 | CConsoleCmd* | Next | Linked list pointer |

## CConsoleVar Structure (0xB0 bytes)

| Offset | Type | Member | Notes |
|--------|------|--------|-------|
| 0x00 | char[32] | Name | Variable name |
| 0x20 | char[128] | Description | Help text |
| 0xA0 | int | Type | Variable type |
| 0xA4 | void* | ValuePtr | Pointer to actual value storage |
| 0xA8 | char | Flags1 | |
| 0xA9 | char | Flags2 | |
| 0xAC | CConsoleVar* | Next | Linked list pointer |

## Functions (34 total)

| Address | Name | Description |
|---------|------|-------------|
| 0x00429bc0 | CConsole__Init | Initializes the console system |
| 0x00429ef0 | CConsole__RegisterBuiltinCommands | Registers all built-in console commands |
| 0x0042a410 | CConsole__ResetLayoutForWindowHeight | Recomputes console layout metrics from current window height |
| 0x0042af80 | CConsole__RegisterCommand | Registers a single console command |
| 0x0042b040 | CConsole__RegisterVariable | Registers a single console variable |
| 0x0042ad30 | CConsole__ExecScript | Loads and executes a console script file line-by-line |
| 0x0042a460 | CConsole__ListBinds | Enumerates key->bind mappings and prints formatted bind lines |
| 0x0042a540 | CConsoleVar__GetTypeName | Converts cvar type enum to printable type label |
| 0x0042a5f0 | CConsoleVar__FormatValueToString | Formats cvar value text by type and value pointer |
| 0x0042a770 | CConsole__FindCommandByName | Searches command list head (`this+0x2394`) via `stricmp` |
| 0x0042a4f0 | CConsole__ExecuteBufferedCommandSlot | Executes a buffered command/output line slot (`this+0x23BC`) when non-empty |
| 0x0042a7b0 | CConsole__SetVariableByName | Resolves a variable by name and writes parsed typed value text |
| 0x0042ae70 | CConsole__ShutdownAndFreeAllLists | Full teardown helper for command/var lists and owned aux pointers |
| 0x0042af20 | CConsole__ClearCommandAndVariableLists | Clears/frees command and variable lists only |
| 0x0042b9c0 | CConsole__ExecuteCommandLine | Tokenizes and dispatches a single console command line |
| 0x0042b120 | CConsole__HandleBind | Console input/bind key handler (toggle/history/tab-complete/dispatch paths) |
| 0x0042ba90 | CConsole__MenuUp | Console menu cursor up (selection decrement + clamp) |
| 0x0042bac0 | CConsole__MenuDown | Console menu cursor down (selection increment + clamp) |
| 0x0042bb30 | CConsole__MenuSelect | Console menu selection execute/apply path |
| 0x0042b840 | CConsole__AddString | Core variadic console text sink (format + append/split to rolling buffers) |
| 0x0042b500 | CConsole__Status | Begins a nested status section (`...` suffix) and increments status depth |
| 0x0042b650 | CConsole__StatusUpdateLine | Internal status-line rewrite helper used by status/progress completion flows |
| 0x0042b800 | CConsole__StatusDone | Completes a status section (success/fail) and decrements status depth |
| 0x0042bbc0 | CConsole__SetLoading | Enables/disables loading-screen mode and manages loading-screen texture lifecycle |
| 0x0042bcf0 | CConsole__InitKeyNameTable | Initializes key-name lookup table strings (Backspace/Return/Shift/arrows/num keys) |
| 0x0042c810 | CConsole__RenderLoadingScreen | Renders/updates loading screen and progress overlays |
| 0x0042cf40 | CConsole__SetLoadingRange | Sets loading progress interpolation range |
| 0x0042cf70 | CConsole__SetLoadingFraction | Sets loading progress fraction inside active range |
| 0x0042c750 | FatalError__ExitWithLocalizedPrefix_A | Fatal wrapper: builds localized prefix (`id 0xCC`) + message and exits process |
| 0x0042d0b0 | FatalError__ExitWithLocalizedPrefix_B | Fatal wrapper variant used by mesh/resource deserialization failures |
| 0x0042d310 | PlatformInput__InitMouse | Creates/acquires DirectInput mouse device and resets cursor/profiler state |
| 0x0042d3b0 | PlatformInput__ShutdownMouse | Unacquires/releases mouse device and snapshots cursor position |
| 0x0042d420 | PlatformInput__PollMouseMotion | Polls device state, updates cursor deltas/position, reacquires on loss |
| 0x0042d4d0 | PlatformInput__PollMouseState | Polls motion + button edge/hold states (`left/right/middle`) into globals |

### Options Entry Init Helpers (Recovered 2026-02-25)

Recovered from the previously deferred constructor-like trio after deeper caller disassembly on 0x00453420..0x00453840 and 0x00514180..0x00514660 showed repeated options-entry initialization patterns.

| Address | Final Name | Notes |
|---------|------------|-------|
| 0x0042d260 | OptionsEntries__InitSingleBindingEntry | `void * __thiscall`: initializes one options-entry binding slot (`active` byte, `entry_id`, slot-0 device/scan/vk) and returns `this`. |
| 0x0042d2b0 | OptionsEntries__InitDualBindingEntry | `void * __thiscall`: initializes dual-binding entry variants (slot-0 + slot-1 metadata) and returns `this`. |
| 0x0042d300 | OptionsEntries__InitSentinelEntry | `void __thiscall`: sentinel/reset helper used in the same options-entry initialization sequences. |
| 0x00453460 | OptionsEntries__InitDefaultDualBindingsTable | `void __cdecl`: table builder that writes default dual-binding entries into `DAT_00677af0` and appends sentinels. |
| 0x00514210 | OptionsEntries__InitDefaultSingleBindingsTable | `void __cdecl`: table builder that writes default single-binding entries into `DAT_008892d8` and appends a sentinel. |

---

## Function Details

### CConsole__Init (0x00429bc0)

**Signature:** `void __thiscall CConsole__Init(CConsole* this)`

**Purpose:** Initializes the CConsole object, setting up member variables, allocating command/variable list nodes, and clearing buffers.

**Key Operations:**
1. Initializes member variables to default values (alpha=200, various flags)
2. If `DAT_00662f30` is set, initializes 20 "Console Line %d" entries (debug mode)
3. Allocates and initializes 3 linked list nodes (purpose unclear)
4. Clears 256-entry output line buffer (0x80 bytes each)
5. Clears 60-entry command history buffer (0x80 bytes each)
6. Clears 10-entry recent commands buffer (0x80 bytes each)
7. Calls `CConsole__InitKeyNameTable` (`0x0042bcf0`) and `CConsole__AddString` (`0x0042b840`) for table/init output setup.

**Xrefs to console.cpp:** 3 (lines 0xF2, 0xF7, 0xF8 - memory allocations)

---

### CConsole__RegisterBuiltinCommands (0x00429ef0)

**Signature:** `void __thiscall CConsole__RegisterBuiltinCommands(CConsole* this)`

**Purpose:** Registers all built-in console commands and variables.

**Registered Commands:**

| Command | Description | Handler |
|---------|-------------|---------|
| `?` | Displays a list of console commands | 0x00VhLKb (obfuscated) |
| `ShowCmds` | Displays a list of console commands | (same as ?) |
| `ShowVars` | Displays a list of console variables | LAB_004296b0 |
| `Get` | Displays the value of a console variable | LAB_00429720 |
| `Set` | Sets the value of a console variable | LAB_004297e0 |
| `Bind` | Binds a command to a key | LAB_00429850 |
| `ListBinds` | Lists the current key bindings | LAB_00429a40 |
| `Echo` | Echos text to the console | LAB_00429a50 |
| `Exec` | Executes a console script from disk | LAB_00429a80 |
| `UseConfiguration` | Switches the Battle Engine to the specified configuration | LAB_00429ad0 |
| `Exit` | Exits the game | LAB_00429ab0 |
| `Quit` | Exits the game | LAB_00429ab0 |
| `ToggleMenu` | Toggle menu | LAB_00429b30 |
| `MemStats` | Output current memory stats to file | LAB_00429b50 |
| `DumpMem` | Dump memory map data | LAB_00429b90 |

**Registered Variables:**

| Variable | Description | Default | Storage |
|----------|-------------|---------|---------|
| `cg_consolealpha` | Alpha of the console background | 0 | this+0x2390 |

**Xrefs to console.cpp:** 7 (all line 0x325 - command/variable allocations)

---

### CConsole__RegisterCommand (0x0042af80)

**Signature:** `void __thiscall CConsole__RegisterCommand(CConsole* this, char* name, char* description, void* callback, char flags)`

**Purpose:** Registers a console command by name with a callback function.

**Parameters:**
- `name` - Command name (max 32 chars)
- `description` - Help text (max 128 chars)
- `callback` - Function pointer called when command is executed
- `flags` - Command flags (purpose varies)

**Key Operations:**
1. Searches existing command list for duplicate name (using `stricmp` (0x00568390, was `FUN_00568390`))
2. If not found, allocates new CConsoleCmd (0xAC bytes) via `OID__AllocObject`
3. Links new command to head of command list at `this+0x2394`
4. Copies name to offset 0x00
5. Copies description to offset 0x20
6. Sets callback at offset 0xA0
7. Sets flags at offset 0xA4

**Xrefs to console.cpp:** 1 (line 0x325)

---

### CConsole__RegisterVariable (0x0042b040)

**Signature:** `void __thiscall CConsole__RegisterVariable(CConsole* this, char* name, char* description, int type, void* valuePtr, char flags1, char flags2)`

**Purpose:** Registers a console variable (cvar) with storage pointer.

**Parameters:**
- `name` - Variable name (max 32 chars)
- `description` - Help text (max 128 chars)
- `type` - Variable type identifier
- `valuePtr` - Pointer to the actual value storage
- `flags1` - First flag byte
- `flags2` - Second flag byte

**Key Operations:**
1. Searches existing variable list for duplicate name (using `stricmp` (0x00568390, was `FUN_00568390`))
2. If not found, allocates new CConsoleVar (0xB0 bytes) via `OID__AllocObject`
3. Links new variable to head of variable list at `this+0x2398`
4. Copies name to offset 0x00
5. Copies description to offset 0x20
6. Sets type at offset 0xA0
7. Sets valuePtr at offset 0xA4
8. Sets flags at offsets 0xA8 and 0xA9

**Xrefs to console.cpp:** 1 (line 0x33E)

---

### CConsole__ExecScript (0x0042ad30)

**Signature:** `void CConsole__ExecScript(void *this, char *script_path)`

**Purpose:** Implements `Exec` command behavior by reading a script file and executing each parsed line.

**Key Operations:**
1. Logs script execution start text (`"Executing script %s"`).
2. Opens script via `DXMemBuffer__OpenRead(...)`.
3. Reads file line-by-line until EOF.
4. Dispatches each line through `CConsole__ExecuteCommandLine`.
5. Logs file-not-found and completion paths.

---

### CConsole__ExecuteCommandLine (0x0042b9c0)

**Signature:** `void CConsole__ExecuteCommandLine(void *this, char *line)`

**Purpose:** Parses command token and dispatches to the matching registered callback in command list `this+0x2394`.

**Notes:**
- Uses `stricmp` against each command entry.
- On no match, emits `"Unknown command"`.

---

### CConsole__AddString (0x0042b840)

**Signature:** `void CConsole__AddString(void *this, char *format)`

**Purpose:** Core variadic string sink used across console/status/game systems to append text into rolling console buffers.

**Notes:**
- Splits newline-delimited formatted text into line entries.
- Mirrors to `DebugTrace` when console trace flag is enabled.
- Used by status/reporting helpers and command handlers.

---

### CConsole__Status (0x0042b500)

**Signature:** `void CConsole__Status(void *this, char *status_line)`

**Purpose:** Starts a nested status section, emits a `"<indent><status> [...]"` style line, and increments nesting depth.

---

### CConsole__StatusDone (0x0042b800)

**Signature:** `void CConsole__StatusDone(void *this, char *status_line, char success)`

**Purpose:** Completes an active status section by updating its line to success/failure text and decrementing nesting depth.

---

### CConsole__SetLoading (0x0042bbc0)

**Signature:** `void CConsole__SetLoading(void *this, char enabled, int load_texture)`

**Purpose:** Toggles loading-screen mode.

**Notes:**
- Enable path stamps start time, optionally loads `loadingscreen.tga`, and resets loading progress fields.
- Disable path releases loading-screen texture and logs elapsed loading time.

---

### CConsole__RenderLoadingScreen (0x0042c810)

**Signature:** `void CConsole__RenderLoadingScreen(void *this, int render_now, char mode)`

**Purpose:** Draws and refreshes loading-screen state using the active loading range/fraction fields and localized loading text.

**Notes:**
- Called by `CConsole__SetLoadingRange` and `CConsole__SetLoadingFraction`.
- Widely used by `CFrontEnd__Init`, `CGame__LoadResources`, `CGame__RestartLoopRunLevel`, and `CGame__RunLevel`.

---

### CConsole__SetLoadingRange (0x0042cf40)

**Signature:** `void CConsole__SetLoadingRange(void *this, float min_percent, float max_percent)`

**Purpose:** Updates loading interpolation endpoints (`this+0xB3D8`, `this+0xB3DC`), resets current value to min, and refreshes the loading screen.

---

### CConsole__SetLoadingFraction (0x0042cf70)

**Signature:** `void CConsole__SetLoadingFraction(void *this, float t)`

**Purpose:** Interpolates `mLoadingCurrent` between range endpoints and refreshes the loading screen.

---

## Additional Helper Mappings (2026-02-25)

These were mapped from behavior + caller/xref evidence during the headless deep pass:

| Address | Name | Summary |
|---------|------|---------|
| 0x0042a410 | CConsole__ResetLayoutForWindowHeight | Recomputes console geometry/layout fields from current window height |
| 0x0042a540 | CConsoleVar__GetTypeName | Converts cvar type enum to printable type name |
| 0x0042a5f0 | CConsoleVar__FormatValueToString | Converts cvar value to text using enum-guided formatting |
| 0x0042a770 | CConsole__FindCommandByName | Searches command list (`this+0x2394`) by case-insensitive name |
| 0x0042ae70 | CConsole__ShutdownAndFreeAllLists | Full list/aux-pointer cleanup path |
| 0x0042af20 | CConsole__ClearCommandAndVariableLists | Command/variable list-only cleanup path |
| 0x0042ba90 | CConsole__MenuUp | Moves console menu selection up (with clamp) |
| 0x0042bac0 | CConsole__MenuDown | Moves console menu selection down (with clamp) |
| 0x0042bb30 | CConsole__MenuSelect | Executes/applies current console menu selection |

---

## Related Functions (Not in console.cpp)

These functions are called by console.cpp functions:

| Address | Likely Name | Purpose |
|---------|-------------|---------|
| 0x005490e0 | OID__AllocObject | Memory allocation wrapper (with debug info) |
| 0x00568390 | stricmp | Case-insensitive string compare |
| 0x0055de9b | sprintf | String formatting |
| 0x00515db0 | Unknown | String operation |
| 0x005159c0 | Unknown | Called during init |
| 0x0042bcf0 | CConsole__InitKeyNameTable | Initializes key-name table entries (Backspace/Return/Shift/num keys/etc.) |
| 0x0042b650 | CConsole__StatusUpdateLine | Internal status-line replacement helper used by `CConsole__StatusDone` and progress updates |

## Notes

1. **Debug String Usage:** The console.cpp path string is used for memory allocation tracking, appearing in calls to `OID__AllocObject` with line numbers (0xF2, 0xF7, 0xF8, 0x325, 0x33E).

2. **Linked List Pattern:** Both commands and variables use a singly-linked list pattern with the "next" pointer at the end of the structure.

3. **Global Flag:** `DAT_00662f30` controls debug console initialization - when set, creates numbered debug console lines.

4. **Console Alpha:** The `cg_consolealpha` variable controls background transparency, stored at offset 0x2390 with default 200.

5. **Command Handlers:** Many command handlers are at addresses like `LAB_004296b0` which are likely small thunks or direct implementations.
