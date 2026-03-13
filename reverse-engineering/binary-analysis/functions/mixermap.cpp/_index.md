# mixermap.cpp - Audio Mixer Map System

**Source file:** `C:\dev\ONSLAUGHT2\mixermap.cpp`
**Debug string address:** `0x00640030`
**Functions identified:** 4

## Overview

The CMixerMap class manages audio channel mixing slots for the game's sound system. It allocates and manages a pool of mixer slots (0x1000 = 4096 entries) with 20-byte (0x14) slot structures for audio channel management.

## Memory Layout

The CMixerMap object has at minimum these members:
- `+0x00`: Pointer to slot array (4096 slots of 20 bytes each = 0x14000 bytes total)
- `+0x04`: Pointer to secondary buffer (0x40000 = 262144 bytes)

Each mixer slot (20 bytes) contains:
- `+0x04`: Pointer to additional data buffer (dynamically allocated based on slot count)

## Functions

| Address | Name | Purpose |
|---------|------|---------|
| `0x005232b0` | `CMixerMap__Init` | Initialize mixer map with 4096 slots |
| `0x00523190` | `CMixerMap__InitSlot` | Initialize/expand individual slot buffer |
| `0x00523230` | `CMixerMap__Destroy` | Full cleanup - frees all slots and buffers |
| `0x00523210` | `CMixerMap__DestroySlot` | Cleanup callback for individual slot |

## Function Details

### CMixerMap__Init (0x005232b0)

**Signature:** `void __thiscall CMixerMap__Init(CMixerMap* this, undefined4 param_1)`

Main initialization function for the mixer map system.

**Behavior:**
1. If existing slot array exists, destroys it (cleanup previous state)
2. Allocates 0x14004 bytes for slot array header + 0x1000 slots
3. Allocates 0x40000 (262144) bytes for secondary buffer
4. Loops 0x1000 times (4096 iterations), calling `CMixerMap__InitSlot` for each
5. Initializes secondary buffer with 1-byte pattern

**Memory allocations:**
- Line 246 (0xf6): 0x14004 bytes for slot array
- Line 247 (0xf7): 0x40000 bytes for secondary buffer

**Called from:** `FUN_00491060+0x81` (sound system initialization)

---

### CMixerMap__InitSlot (0x00523190)

**Signature:** `void __thiscall CMixerMap__InitSlot(CMixerMapSlot* this)`

Initializes or expands an individual mixer slot's buffer.

**Behavior:**
1. Performs validation/setup calls
2. If slot's buffer pointer is non-null:
   - Calculates new buffer size as `slot_count * 0x51` (81 bytes per entry)
   - Allocates new buffer
   - Initializes buffer with 1-byte pattern

**Memory allocation:**
- Line 134 (0x86): Dynamic size based on slot count

**Called from:** `CMixerMap__Init` in a loop (4096 times)

---

### CMixerMap__Destroy (0x00523230)

**Signature:** `void __thiscall CMixerMap__Destroy(CMixerMap* this)`

Complete cleanup of the mixer map, freeing all allocated memory.

**Behavior:**
1. If slot array exists:
   - Iterates through all 4096 slots (0x14000 bytes, 0x14 stride)
   - For each slot with a buffer at offset +4, frees it
2. Frees the slot array itself
3. Frees the secondary buffer at offset +4

**Called from:** `CUnitAI__ReleaseOwnedObjectsAndDestroyMixerMap+0xa` (via JMP - tail call optimization)

---

### CMixerMap__DestroySlot (0x00523210)

**Signature:** `void __thiscall CMixerMap__DestroySlot(CMixerMapSlot* this)`

Callback function for destroying individual slot data.

**Behavior:**
1. If buffer pointer at offset +4 is non-null:
   - Frees the buffer
   - Sets pointer to null

**Used by:**
- `CMixerMap__Init` - as destructor callback during reinitialization
- `CMixerMap__Destroy` - as callback for array cleanup

---

## Exception Handler

**Address:** `0x005d68f0` (Unwind@005d68f0)

Auto-generated SEH unwind handler for `CMixerMap__Init`. Called during stack unwinding if an exception occurs during initialization. Frees the partially allocated slot array.

## Call Graph

```
Sound System Init (0x00491060)
    |
    +---> CMixerMap__Init (0x005232b0)
              |
              +---> CMixerMap__DestroySlot (0x00523210) [callback for cleanup]
              |
              +---> CMixerMap__InitSlot (0x00523190) [x4096 iterations]

Sound System Shutdown (`CUnitAI__ReleaseOwnedObjectsAndDestroyMixerMap` @ `0x00490f40`)
    |
    +---> CMixerMap__Destroy (0x00523230) [tail call]
              |
              +---> CMixerMap__DestroySlot (0x00523210) [callback]
```

## Technical Notes

1. **Slot stride:** 0x14 (20 bytes) per slot
2. **Slot count:** 0x1000 (4096) slots
3. **Total slot array size:** 0x14000 (81920 bytes) + 4-byte header = 0x14004
4. **Secondary buffer:** 0x40000 (262144 bytes) - likely for audio sample mixing
5. **Per-entry size in slot buffers:** 0x51 (81 bytes) - purpose unknown

## Related Files

- Sound system initialization likely in `sound.cpp` or similar
- Caller `FUN_00491060` and `CUnitAI__ReleaseOwnedObjectsAndDestroyMixerMap` may be CSoundSystem methods
