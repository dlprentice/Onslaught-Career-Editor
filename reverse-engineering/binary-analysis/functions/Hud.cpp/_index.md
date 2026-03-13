# Hud.cpp

> HUD (Heads-Up Display) functions from BEA.exe

## Overview

The CHud class manages the in-game heads-up display, including health bars, ammo counters, radar, and other UI elements displayed during gameplay.

**Debug Path**: `C:\dev\ONSLAUGHT2\Hud.cpp` (string at 0x0062ce78)

## Functions

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x00481450 | CHud__Init | RENAMED | Initializes HUD resources and loads textures |
| 0x00481f40 | CHud__SetHudComponent | RENAMED | Sets/switches HUD component objects |
| 0x004de3a0 | CHudComponent__ctor | RENAMED | Constructs 0x68-byte HUD component object |
| 0x004de6b0 | CHudComponent__GetPos | RENAMED | Writes 16 bytes from `this+0x0C` (mPos) into out buffer |
| 0x004de6e0 | CHudComponent__GetOrientation | RENAMED | Writes 0x30 bytes from `this+0x1C` (mOrientation / FoR matrix) into out buffer |
| 0x004de700 | Return1f | RENAMED | Shared virtual stub returning constant `1.0f` |
| 0x004de720 | CHudComponent__GetMesh | RENAMED | Returns dword/pointer at `this+0x54` (set during ctor resource init) |
| 0x004de730 | CHudComponent__scalar_deleting_dtor | RENAMED | Scalar deleting dtor wrapper |
| 0x004de760 | CHudComponent__dtor | RENAMED | Component destructor body |
| 0x004de7d0 | CHudComponent__HandleEvent | RENAMED | Handles scheduled event 4000 (fade/progress tick), reschedules, may delete on destroy flag |
| 0x004de850 | CHudComponent__RequestDestroy | RENAMED | Marks component for deferred destruction |
| 0x004de860 | CHudComponent__RenderPass | RENAMED | Per-component render/update pass |
| 0x004de8b0 | CHudComponent__GetAlpha | RENAMED | Returns float at `this+0x60` (alpha/progress) |

## Details

### CHud__Init (0x00481450)

- **Purpose**: Initializes the HUD system by allocating buffers and loading texture resources
- **Xref**: Found via debug path at 0x0062ce78 (lines 0x5d and 0x5f)
- **Called from**: FUN_0046c360 (likely game/level initialization)
- **Calling convention**: thiscall (ECX = this pointer)

**Behavior**:
1. Sets flag at offset 0x5c to 1 (likely "initialized" flag)
2. Allocates large buffer (0x3f14 = 16148 bytes) for HUD graphics data
3. Allocates secondary buffer (0x80 = 128 bytes)
4. Loads 8 texture/sprite resources via hash lookups:
   - 0x72a0936 -> stored at offset 0xb4
   - 0x6b91062 -> stored at offset 0xb8
   - 0x85574fc -> stored at offset 0xbc
   - 0x2b617f -> stored at offset 0xc4
   - 0x2b4ce2 -> stored at offset 0xc8
   - 0x396c8 -> stored at offset 0xc0
   - 0x31e12896 -> stored at offset 0xcc
   - 0x227a52ff -> stored at offset 0xd0

**CHud Class Layout (Partial)**:
```
Offset  Size  Field
0x30    4     Secondary buffer pointer
0x5c    4     Initialized flag
0x60    4     Main buffer pointer
0xb4    4     Texture resource 1
0xb8    4     Texture resource 2
0xbc    4     Texture resource 3
0xc0    4     Texture resource 6
0xc4    4     Texture resource 4
0xc8    4     Texture resource 5
0xcc    4     Texture resource 7
0xd0    4     Texture resource 8
```

---

### CHud__SetHudComponent (0x00481f40)

- **Purpose**: Creates or destroys HUD component objects based on mode
- **Xref**: Found via debug path at 0x0062ce78 (lines 0x137 and 0x13b)
- **Called from**:
  - FUN_0043f340 (unknown)
  - FUN_0043f420 (unknown)
  - CCutscene__Update (cutscene playback)
- **Calling convention**: thiscall (ECX = this pointer)
- **Parameters**:
  - param_1: Component ID or mode value
  - param_2: Boolean flag (0 = use offset 0x200, non-0 = use offset 0x1fc)

**Behavior**:
1. If existing component at target offset is non-null, marks it for deferred destruction via `CHudComponent__RequestDestroy`
2. Allocates new component object (0x68 = 104 bytes)
3. Initializes component via `CHudComponent__ctor` with `param_1` (component name/id)
4. Stores component pointer at offset 0x1fc or 0x200 based on param_2

**CHud Class Layout (Additional)**:
```
Offset   Size  Field
0x1fc    4     HUD component pointer 1 (when param_2 != 0)
0x200    4     HUD component pointer 2 (when param_2 == 0)
```

This function appears to manage two interchangeable HUD component slots, possibly for transitioning between different HUD states (e.g., normal gameplay vs cutscene overlay).

---

### CHudComponent Helpers (0x004de3a0 cluster)

- `CHudComponent__ctor` (`0x004de3a0`)
  - Initializes monitor/vtable state for a 0x68-byte object.
  - Sets two vtable pointers:
    - `this+0x00` -> `0x005dec20` (pos/orientation/mesh/alpha getters)
    - `this+0x04` -> `0x005dec10` (monitor/event handler + deleting dtor)
  - Builds `<component_name> + ".msh"` and loads/caches Effect mesh/resource handles.
  - Schedules event `4000` via `CEventManager__AddEvent_AtTime` when resource setup is valid.

- `CHudComponent__RequestDestroy` (`0x004de850`)
  - Sets byte flags at `+0x64` and `+0x65` to request deferred destroy.
  - The HUD render path checks `+0x64` and then executes virtual cleanup/free.

- `CHudComponent__RenderPass` (`0x004de860`)
  - Fetches sub-item table from owned object at `+0x4C`.
  - Iterates count at `+0x15C`, dispatching each entry through `CHudComponent__RenderPassEntry(entry, this, 0)`.

- `CHudComponent__dtor` / `CHudComponent__scalar_deleting_dtor`
  - Releases owned object at `+0x48`, runs `CMonitor__Shutdown`, and conditionally frees memory in scalar deleting wrapper.

---

## Exception Handlers

The following Unwind functions are exception cleanup handlers associated with Hud.cpp:

| Address | Name | Notes |
|---------|------|-------|
| 0x005d2d00 | Unwind@005d2d00 | Cleanup for CHud__Init allocation 1 |
| 0x005d2d16 | Unwind@005d2d16 | Cleanup for CHud__Init allocation 2 |
| 0x005d2d40 | Unwind@005d2d40 | Cleanup for CHud__SetHudComponent |
| 0x005d2d59 | Unwind@005d2d59 | Cleanup for CHud__SetHudComponent |

These are automatically generated by the compiler for structured exception handling and call `OID__FreeObject_Callback` (wrapper around `OID__FreeObject`) to clean up partially constructed objects if an exception occurs.

## Related Functions

- **FUN_004f2580**: Resource/texture loader (takes hash, returns resource pointer)
- **OID__AllocObject**: Memory allocator (takes size, alignment, file, line)
- **CHudComponent__RequestDestroy (0x004de850)**: Deferred-destroy mark helper
- **CHudComponent__ctor (0x004de3a0)**: Component constructor/initializer
- **CHudComponent__RenderPass (0x004de860)**: Component render/update loop
- **FUN_0053bd60**: Unknown initializer (called after first allocation in Init)
- **FUN_00539f00**: Unknown initializer (called after second allocation in Init)

## Discovery Notes

- Found via xref search to debug path string at 0x0062ce78
- The string has a "Y?" prefix at 0x0062ce76, actual path starts at 0x0062ce78
- Debug path references include source line numbers (0x5d=93, 0x5f=95, 0x137=311, 0x13b=315)
- CHudComponent vtable targets (`0x004de6b0`, `0x004de6e0`, `0x004de700`, `0x004de720`, `0x004de7d0`, `0x004de8b0`) were recovered on 2026-02-13 via manual CodeBrowser function creation (`F`) followed by MCP rename/signature/comment with read-back verification.
