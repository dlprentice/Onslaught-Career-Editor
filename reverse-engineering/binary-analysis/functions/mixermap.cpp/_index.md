# mixermap.cpp - Audio Mixer Map System

**Source file:** `[maintainer-local-source-export-root]\mixermap.cpp`
**Debug string address:** `0x00640030`
**Functions identified:** 4

Wave566 status: saved static retail Ghidra signatures/comments/tags, not runtime audio or terrain behavior proof. The retail binary carries the `mixermap.cpp` debug path, but no matching source file is present in `references/Onslaught`; no `source-parity` tag was applied.

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

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
| `0x005232b0` | `CMixerMap__Init` | Initialize mixer map from a chunk reader with 4096 slots |
| `0x00523190` | `CMixerMap__InitSlot` | Read one 0x14-byte slot record and optional payload from a chunk reader |
| `0x00523230` | `CMixerMap__Destroy` | Full cleanup - frees all slots and buffers |
| `0x00523210` | `CMixerMap__DestroySlot` | Cleanup callback for individual slot |

## Function Details

### CMixerMap__Init (0x005232b0)

**Signature:** `void __thiscall CMixerMap__Init(void * this, void * chunk_reader)`

Main initialization function for the mixer map system. `RET 0x4` plus the `CHeightField__DeserializeMapAndInitResources` callsite prove one explicit `chunk_reader` stack argument after the receiver.

**Behavior:**
1. If existing slot array exists, destroys it (cleanup previous state)
2. Allocates 0x14004 bytes for slot array header + 0x1000 slots
3. Allocates 0x40000 (262144) bytes for secondary buffer
4. Consumes a chunk-reader tag, loops 0x1000 times (4096 iterations), and calls `CMixerMap__InitSlot(slot, chunk_reader)` for each 0x14-byte slot
5. Consumes another chunk-reader tag and reads the 0x40000 secondary payload

**Memory allocations:**
- Line 246 (0xf6): 0x14004 bytes for slot array
- Line 247 (0xf7): 0x40000 bytes for secondary buffer

**Called from:** `CHeightField__DeserializeMapAndInitResources+0x81` (Wave426-corrected MAP deserialize/resource-init path)

---

### CMixerMap__InitSlot (0x00523190)

**Signature:** `void __thiscall CMixerMap__InitSlot(void * this, void * chunk_reader)`

Initializes or expands an individual mixer slot's buffer. `RET 0x4`, prologue `MOV ESI,ECX`, and the caller at `0x0052337f` / `0x00523381` prove a slot receiver plus one `chunk_reader` argument.

**Behavior:**
1. Consumes two chunk-reader tags
2. Reads a 0x14-byte slot record into `this`
3. If slot's buffer pointer is non-null:
   - Calculates new buffer size as `slot_count * 0x51` (81 bytes per entry)
   - Allocates new buffer
   - Stores it at slot offset `+0x04`
   - Reads `slot_count * 0x51` bytes from the chunk reader into the payload

**Memory allocation:**
- Line 134 (0x86): Dynamic size based on slot count

**Called from:** `CMixerMap__Init` in a loop (4096 times)

---

### CMixerMap__Destroy (0x00523230)

**Signature:** `void __thiscall CMixerMap__Destroy(void * this)`

Complete cleanup of the mixer map, freeing all allocated memory.

**Behavior:**
1. If slot array exists:
   - Iterates through all 4096 slots (0x14000 bytes, 0x14 stride)
   - For each slot with a buffer at offset +4, frees it
2. Frees the slot array itself
3. Frees the secondary buffer at offset +4

**Called from:** `CHeightField__ShutdownAndDestroyMixerMap+0xa` (via JMP - tail call optimization; Wave426 supersedes the stale `CUnitAI` owner label)

---

### CMixerMap__DestroySlot (0x00523210)

**Signature:** `void __thiscall CMixerMap__DestroySlot(void * this)`

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

Sound System Shutdown (`CHeightField__ShutdownAndDestroyMixerMap` @ `0x00490f40`)
    |
    +---> CMixerMap__Destroy (0x00523230) [tail call]
              |
              +---> CMixerMap__DestroySlot (0x00523210) [callback]
```

## Wave566 Evidence

- Apply script: `tools/ApplyFEPMixerMapWave566.java`
- Probe: `tools/ghidra_fep_mixermap_wave566_probe.py`
- Artifacts: `subagents/ghidra-static-reaudit/wave566-cvbuftexture-mixermap-005230e0/`

Read-back summary: dry `updated=0 skipped=5 renamed=0 would_rename=1 missing=0 bad=0`; apply `updated=5 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`; final dry `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `CMixerMap__InitSlot`, `CMixerMap__DestroySlot`, `CMixerMap__Destroy`, and `CMixerMap__Init` metadata, tags, xrefs, instructions, and decompiles. Queue refresh after the combined FEP/MixerMap tranche reports `6089` functions, `2811` commented, `3278` commentless, `1494` exact-undefined signatures, and `1179` `param_N` signatures.

## Technical Notes

1. **Slot stride:** 0x14 (20 bytes) per slot
2. **Slot count:** 0x1000 (4096) slots
3. **Total slot array size:** 0x14000 (81920 bytes) + 4-byte header = 0x14004
4. **Secondary buffer:** 0x40000 (262144 bytes) - likely for audio sample mixing
5. **Per-entry size in slot buffers:** 0x51 (81 bytes) - purpose unknown

## Related Files

- Sound system initialization likely in `sound.cpp` or similar
- Wave426 corrected the callers to MAP/heightfield context: `CHeightField__DeserializeMapAndInitResources` and `CHeightField__ShutdownAndDestroyMixerMap`. This is static Ghidra evidence only and does not prove runtime mixer/audio behavior.
