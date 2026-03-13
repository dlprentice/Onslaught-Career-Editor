# thing.cpp

> Base game object class (CThing) from BEA.exe

**Debug Path**: `C:\dev\ONSLAUGHT2\thing.cpp` at `0x006331c0`

## Overview

CThing is the base class for all game objects in Battle Engine Aquila. It provides fundamental functionality for:
- Collision detection and handling
- Object naming/identification
- Sound attachment
- Visual trail effects

This is a foundational class - most game entities (units, projectiles, buildings) inherit from CThing.

## Functions

| Address | Name | Status | Line | Notes |
|---------|------|--------|------|-------|
| 0x004f35d0 | CThing__InitRenderThing | RENAMED | 92 | Creates render-thing from class id and stores pointer at this+0x30 |
| 0x004f36d0 | CThing__Render | RENAMED | 133 | Invisibility/objective gating, render dispatch, optional debug cuboid draw |
| 0x004f3710 | CThing__RenderImposter | RENAMED | 150 | Calls render-thing imposter render path when renderable |
| 0x004f37c0 | CThing__DrawDebugCuboid | RENAMED | 207 | Debug draw helper for bounding cuboids/sphere overlays |
| 0x004f3970 | CThing__SetObjective | RENAMED | 269 | Adds/removes this from objective noticeboard and toggles objective flag |
| 0x004f3de0 | CThing__IsOverWater | RENAMED | 543 | Returns true when water level is above terrain collision height at current position |
| 0x004f4430 | CComplexThing__StartDieProcess | RENAMED | 728 | Base start-die path plus mission-script StartedDying callback |
| 0x004f4480 | CComplexThing__Hit | RENAMED | 748 | Mission-script hit callback when colliding with complex-thing target |
| 0x004f39c0 | CThing__AddCollision | RENAMED | 310 | Sets up collision object at this+0x38 |
| 0x004f4120 | CThing__SetName | RENAMED | 625 | Sets object name string at this+0x78 |
| 0x004f4230 | CThing__SetSound | RENAMED | 665 | Attaches sound/FX at this+0x74 |
| 0x004f44a0 | CThing__AddTrail | RENAMED | 767 | Adds visual trail effect at this+0x6c |
| 0x00403ba0 | CThing__Hit_TriggerDieOnDamageMaskA | RENAMED | n/a | Hit helper variant: death gate when incoming collision mask includes `0x10` or `0x2100000` |
| 0x00403bf0 | CThing__Hit_TriggerDieOnDamageMaskB | RENAMED | n/a | Hit helper variant: death gate when incoming collision mask includes `0x100000` |
| 0x00417540 | CThing__RenderAndUpdateStaticShadow | RENAMED | n/a | Render wrapper: calls `CThing__Render`, updates static-shadow visibility, and runs frame-gated callback |
| 0x004176c0 | CThing__InitRenderThingFromInitMeshName | RENAMED | n/a | Init-data-driven render object creation path using `%s.msh` naming and `this+0x30` bind |

## CThing Member Offsets

Based on function analysis:

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x30 | ptr | mMesh? | Mesh pointer (checked in AddCollision) |
| 0x38 | ptr | mCollision | Collision object pointer |
| 0x6c | ptr | mTrail | Trail effect object |
| 0x74 | ptr | mSound | Sound/FX object |
| 0x78 | char* | mName | Object name string |

## Details

### CThing__AddCollision (0x004f39c0)

- **Purpose**: Creates and attaches a collision object to the CThing
- **Source Line**: 310 (0x136)
- **Xref**: Found via debug path at 0x006331c0
- **Thiscall**: ECX = CThing pointer

**Behavior**:
1. Checks if param_1[2] != -1 (collision type check)
2. If this+0x38 (collision ptr) is null, allocates 0x38 bytes (56 bytes) for collision object
3. Initializes collision object vtable and members
4. If this+0x30 (mesh) is null AND param_1[6] == 2 (mesh collision type):
   - Logs warning: "Warning: Trying to do mesh collision on a object that has no mesh"
   - Downgrades collision type from 2 to 1
5. Calls virtual method at collision_vtable+0x0C to register collision

**Warning String** at 0x0063317c:
```
Warning: Trying to do mesh collision on a object that has no mesh
```

**Allocation**: Uses OID__AllocObject (memory allocator) with type=0xB

---

### CThing__SetName (0x004f4120)

- **Purpose**: Sets the name/identifier string for the object
- **Source Line**: 625 (0x271)
- **Xref**: Found via debug path at 0x006331c0
- **Thiscall**: ECX = CThing pointer

**Behavior**:
1. If this+0x78 (name ptr) is not null:
   - Calls CSPtrSet__Remove (unregister old name from global name set)
   - Frees old name via OID__FreeObject
   - Sets this+0x78 to null
2. If param_1 is non-empty string:
   - Calculates string length
   - Allocates memory for string (type=5)
   - Copies string via strncpy
   - Null-terminates
   - Calls CSPtrSet__AddToHead (register name in global name set)

**Allocation**: Uses OID__AllocObject with type=0x5

---

### CThing__SetSound (0x004f4230)

- **Purpose**: Attaches a sound effect to the object
- **Source Line**: 665 (0x299)
- **Xref**: Found via debug path at 0x006331c0
- **Thiscall**: ECX = CThing pointer

**Behavior**:
1. If this+0x74 (sound ptr) is not null:
   - Calls virtual destructor on existing sound object
   - Sets this+0x74 to null
2. If param_1 is non-null and non-empty:
   - Looks up sound via `CWorld__CloneScriptObjectCodeByName` (`0x0050abc0`) and clones the matched script object code
   - If found, allocates 0x3C bytes (60 bytes) for sound object (type=0x18)
   - Creates sound via FUN_005333b0
   - Stores at this+0x74
   - Triggers event 0x7D1 (2001) with float -1.0f via FUN_0044b370

**Note**: 0xbf800000 = -1.0f in IEEE 754 floating point

**Allocation**: Uses OID__AllocObject with type=0x18

---

### CThing__AddTrail (0x004f44a0)

- **Purpose**: Adds a visual trail effect (smoke, fire, etc.) to the object
- **Source Line**: 767 (0x2FF)
- **Xref**: Found via debug path at 0x006331c0
- **Thiscall**: ECX = CThing pointer

**Behavior**:
1. If this+0x6c (trail ptr) is null:
   - Allocates 0x24 bytes (36 bytes) for trail object (type=5)
   - Creates trail via FUN_004046d0
   - Stores at this+0x6c
2. Calls `CAtmospheric__ConfigureTrail` with params to configure trail

**Parameters**: Takes 3 parameters (likely trail configuration - color, size, duration?)

**Allocation**: Uses OID__AllocObject with type=0x5

---

## Related Functions

These functions were found but not renamed (exception handlers):

| Address | Name | Notes |
|---------|------|-------|
| 0x005d5220 | Unwind@005d5220 | Exception handler for thing.cpp |
| 0x005d5250 | Unwind@005d5250 | Exception handler for thing.cpp |

## Memory Allocation Types

The allocator OID__AllocObject uses type codes:

| Type | Size | Used By |
|------|------|---------|
| 0x05 | varies | Name strings, Trail objects |
| 0x0B | 0x38 | Collision objects |
| 0x18 | 0x3C | Sound objects |

## Cross-References

- OID__AllocObject - Memory allocator (appears in all functions)
- OID__FreeObject - Memory deallocator (in SetName)
- CConsole__Printf (`FUN_00441740`) - Debug/warning logger (in AddCollision)
- `CWorld__CloneScriptObjectCodeByName` (`0x0050abc0`) - Script-object-code lookup by name + clone (used by SetSound)
- FUN_005333b0 - Sound object constructor (in SetSound)
- FUN_0044b370 - Event trigger system (in SetSound)
- FUN_004046d0 - Trail object constructor (in AddTrail)
- `CAtmospheric__ConfigureTrail` - Trail configuration (in AddTrail)
- CSPtrSet__AddToHead - Name registration (in SetName)
- CSPtrSet__Remove - Name unregistration (in SetName)
