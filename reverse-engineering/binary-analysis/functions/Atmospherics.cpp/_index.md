# Atmospherics.cpp Functions

> Source File: Atmospherics.cpp | Binary: BEA.exe
> Debug Path: 0x00622ec4 (`C:\dev\ONSLAUGHT2\Atmospherics.cpp`)

## Overview

The Atmospherics system handles weather and environmental effects including rain, snow, lightning, and wind. It uses a linked list of atmospheric objects (stored at `DAT_006601a8`) that are updated and rendered each frame. The system registers console commands and variables for runtime tweaking of weather parameters.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00404a00 | Atmospherics__Init | Initialize atmospherics system, load textures, register console vars | ~400 bytes |
| 0x00404b90 | Atmospherics__ResetAndUpdate | Reset wind vector to zero, call update on all atmospheric objects | ~64 bytes |
| 0x00404bd0 | Atmospherics__UpdateAll | Iterate all atmospherics, call vtable method +0x08 (Update) | ~32 bytes |
| 0x00404bf0 | Atmospherics__RenderAll | Iterate all atmospherics, call vtable method +0x04 (Render) | ~32 bytes |
| 0x00404c10 | Atmospherics__Shutdown | Clean up all atmospheric objects and release texture | ~128 bytes |
| 0x00404c90 | Atmospherics__NotifyAll | Iterate all atmospherics, call vtable method +0x14 with parameter | ~48 bytes |

## Global Variables

| Address | Name | Type | Purpose |
|---------|------|------|---------|
| 0x00660188 | atm_lightningdensity | float | Lightning density (0-1) |
| 0x0066018c | atm_snowdensity | float | Snow density (0-1) |
| 0x00660190 | atm_raindensity | float | Rain density (0-1) |
| 0x00660198 | atm_windvector | vec3 | Prevailing wind vector (X, Y, Z) |
| 0x006601a8 | g_AtmosphericsList | ptr | Head of linked list of atmospheric objects |
| 0x006601ac | g_SnowTexture | CTexture* | Snow layer texture handle |

## Console Commands

| Command | Description |
|---------|-------------|
| `ListAtmospherics` | Displays a list of the atmospheric effects |

## Console Variables

| Variable | Type | Description |
|----------|------|-------------|
| `atm_windvector` | vec3 (type 5) | The prevailing wind vector |
| `atm_raindensity` | float (type 4) | Rain density (0-1) |
| `atm_snowdensity` | float (type 4) | Snow density (0-1) |
| `atm_lightningdensity` | float (type 4) | Lightning density (0-1) |

## Key Observations

1. **Linked List Structure**: Atmospheric objects form a singly-linked list with the next pointer at offset +0x04 from the object base.

2. **VTable Layout**: Each atmospheric object has a vtable pointer at offset 0. The vtable methods are:
   - +0x04: Render
   - +0x08: Update
   - +0x0C: Reset (called by ResetAndUpdate)
   - +0x10: Destructor
   - +0x14: Notify (takes parameter)

3. **Texture Loading**: The snow texture is loaded from `Atmospherics/Snow/SnowLayer.tga` during initialization.

4. **Memory Allocation**: Uses custom memory allocator (OID__AllocObject) with sizes 0x3a4 (932 bytes) and 0x334 (820 bytes) for different atmospheric types.

5. **Exception Handling**: Init and shutdown use structured exception handling (SEH) with unwind handlers at 0x005d0ff0 and 0x005d1006.

## Related Functions (Not in Atmospherics.cpp)

These functions interact closely with the Atmospherics system but are defined in other source files:

| Address | Name | Purpose |
|---------|------|---------|
| 0x00404960 | CAtmospheric__Unlink | Remove atmospheric object from linked list |
| 0x00404920 | CAtmospheric__Link | Add atmospheric object to linked list |
| 0x004046d0 | CAtmospheric__Constructor | Initialize base atmospheric object |
| 0x00404210 | CAtmospheric__Process | Main per-instance simulation/update path (target selection, orientation update, movement step, event scheduling) |
| 0x00404790 | CAtmospheric__UpdateBlendState | Advance/update atmospheric blend scalar state using mode gates and wrap behavior |
| 0x004048c0 | CAtmospheric__GetInterpolatedBlendValue | Return frame-interpolated blend scalar from previous/current values |
| 0x00404010 | CAtmospheric__Destructor | Clean up and unlink atmospheric object |

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
