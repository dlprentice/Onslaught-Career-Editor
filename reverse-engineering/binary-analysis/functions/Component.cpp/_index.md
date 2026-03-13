# Component.cpp Functions

> Source File: Component.cpp | Binary: BEA.exe
> Debug Path: 0x006247f8

## Overview

Component system implementation for game entities. Handles creation and initialization of sub-components attached to units, particularly weapon systems like Fenrir guns and Carrier health pads. Uses a factory pattern to create different component types based on string matching.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00427cd0 | CComponent__CreateSubComponent1 | Creates small sub-component (0x14 bytes) at this+0x70 | ~128 bytes |
| 0x00427d50 | CComponent__CreateSubComponent2 | Creates sub-component (0x20 bytes) at this+0x208 | ~128 bytes |
| 0x00427dd0 | CComponent__CreateWeaponComponent | Factory for weapon components (Fenrir/Carrier) | ~304 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d19e0 | Unwind@005d19e0 | 77 | Cleanup for CreateSubComponent1 |
| 0x005d1a00 | Unwind@005d1a00 | 83 | Cleanup for CreateSubComponent2 |
| 0x005d1a20 | Unwind@005d1a20 | 92 | Cleanup for weapon component (Fenrir Bomb Launcher path) |
| 0x005d1a36 | Unwind@005d1a36 | 94 | Cleanup for weapon component (Fenrir Main Gun path) |
| 0x005d1a4c | Unwind@005d1a4c | 96 | Cleanup for weapon component (default path) |
| 0x005d1a62 | Unwind@005d1a62 | 99 | Cleanup for weapon component (Carrier Health Pad path) |

## Function Details

### CComponent__CreateSubComponent1 (0x00427cd0)

**Line**: 77

Allocates 0x14 (20) bytes via debug allocator and stores result at `this+0x70`. Uses `FUN_00495930` for secondary initialization if allocation succeeds.

```c
// Pseudocode
void CComponent::CreateSubComponent1() {
    void* obj = DebugAlloc(0x14, 0x1b, "Component.cpp", 77);
    if (obj) {
        this->field_70 = SomeInit(this != NULL ? this + 8 : 0);
    } else {
        this->field_70 = NULL;
    }
}
```

### CComponent__CreateSubComponent2 (0x00427d50)

**Line**: 83

Allocates 0x20 (32) bytes and stores at `this+0x208`. Calls `FUN_0047e290` for initialization and sets vtable pointer at `PTR_LAB_005d9654`.

```c
// Pseudocode
void CComponent::CreateSubComponent2() {
    void* obj = DebugAlloc(0x20, 0x17, "Component.cpp", 83);
    if (obj) {
        FUN_0047e290(this);
        obj->vtable = &vtable_005d9654;
        this->field_208 = obj;
    } else {
        this->field_208 = NULL;
    }
}
```

### CComponent__CreateWeaponComponent (0x00427dd0)

**Lines**: 92, 94, 96, 99

Factory function that creates different weapon component types based on string comparison. Uses `stricmp` (0x00568390, was `FUN_00568390`) for string matching against component names. All component types are 0x60 (96) bytes and use `CWarspite__Init` for initialization.

**String matching order**:
1. "Fenrir Bomb Launcher" (0x006248a0) - Line 92 - vtable 0x005d96b4
2. "Fenrir Main Gun" (0x00624890) - Line 94 - vtable 0x005d9680
3. "Carrier Health Pad" (0x0062487c) - Line 99 - special handling with field_14 = 0
4. Default - Line 96 - vtable 0x005d8e08

Result stored at `this+0x13c`.

```c
// Pseudocode
void CComponent::CreateWeaponComponent(param1) {
    char* typeName = *(this->field_164->field_B0);

    if (strcmp(typeName, "Fenrir Bomb Launcher") == 0) {
        void* obj = DebugAlloc(0x60, 0x16, "Component.cpp", 92);
        if (obj) {
            CWarspite::Init(this, param1);
            obj->vtable = &vtable_005d96b4;
            this->field_13c = obj;
        }
    }
    else if (strcmp(typeName, "Fenrir Main Gun") == 0) {
        // Similar with vtable_005d9680
    }
    else if (strcmp(typeName, "Carrier Health Pad") != 0) {
        // Default with vtable_005d8e08
    }
    else {
        // Carrier Health Pad - special: sets obj->field_14 = 0
    }
}
```

## Key Observations

- **Debug allocator** - Uses `OID__AllocObject` which takes size, type, filename, and line number
- **String comparison** - `stricmp` (0x00568390, was `FUN_00568390`) (returns 0 on match)
- **Warspite integration** - All weapon components are initialized via `CWarspite__Init`
- **Member offsets**:
  - `this+0x70` - SubComponent1 pointer
  - `this+0x13c` - Weapon component pointer
  - `this+0x164` - Pointer to parent/owner object
  - `this+0x208` - SubComponent2 pointer
- **VTables referenced**:
  - 0x005d9654 - SubComponent2 type
  - 0x005d96b4 - Fenrir Bomb Launcher
  - 0x005d9680 - Fenrir Main Gun
  - 0x005d8e08 - Default weapon component

## Related Files

- Carrier.cpp - Carrier entity that uses health pad component
- Warspite.cpp - CWarspite class that weapon components inherit from
- Unit.cpp - Base unit class that likely contains CComponent

## Related Classes

- **CFenrirMainGunAI** - RTTI at 0x00624840
- **CFenrirBehaviourType** - RTTI at 0x00627b50
- **CCarrier** - Uses Carrier Health Pad component

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
