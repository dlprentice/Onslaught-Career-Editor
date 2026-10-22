# flexarray.cpp - Flexible Array Container

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x0044b290` → `CFlexArray__Free_thunk` (was `CFlexArray__Free`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the closeout (private RE archive: `reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md`); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

**Source File:** `[maintainer-local-source-export-root]\flexarray.cpp`
**Debug String Address:** `0x00629a9c`
**Functions Found:** 9 (including 1 thunk)

Wave 320 saved public-safe Ghidra signatures/comments for the full pointer-sized `CFlexArray` helper family on 2026-05-10. The pass proves static helper behavior and saved metadata quality; it does not prove every call-site element type, runtime ownership discipline, tags, local variable names, or rebuild parity.

## Overview

CFlexArray is a dynamic array template class used throughout the Battle Engine Aquila codebase. It provides automatic memory management with configurable growth strategies (linear or multiplicative).

## Class Structure

| Offset | Field | Meaning |
| --- | --- | --- |
| `+0x00` | `mData` | pointer to the element array |
| `+0x04` | `mCapacity` | allocated capacity |
| `+0x08` | `mCount` | elements in use |
| `+0x0C` | `mGrowth` | growth factor (positive additive, negative multiplicative) |

Total size 16 bytes (`0x10`).

### Growth Strategy

The `mGrowth` field controls how the array grows when capacity is exceeded:
- **Positive value (e.g., 16):** Add `mGrowth` to capacity (linear growth)
- **Negative value (e.g., -2):** Multiply capacity by `-mGrowth` (exponential growth)
- **Zero:** Array cannot grow (fixed size)

## Functions

| Address | Name | Signature | Description |
|---------|------|-----------|-------------|
| `0x00465530` | `CFlexArray__Init` | `void * __thiscall Init(void *this, int initialCapacity)` | Allocate initial storage and return `this` |
| `0x00465570` | `CFlexArray__Free` | `void __fastcall Free(void *this)` | Free allocated memory |
| `0x00465580` | `CFlexArray__Resize` | `void __thiscall Resize(void *this, uint newCapacity)` | Resize array, zero-fill new elements |
| `0x004241a0` | `CFlexArray__InitWithGrowth` | `void * __thiscall InitWithGrowth(void *this, int initialCapacity, int growth)` | Init with custom growth factor and return `this` |
| `0x004241e0` | `GenericOPtrSet__reset` | `void __fastcall Clear(void *this)` | Reset count to 0 (keep capacity) |
| `0x004241f0` | `CFlexArray__Add` | `void * __thiscall Add(void *this, void *element)` | Append element, grow if needed, return `this` |
| `0x00424260` | `GenericOPtrSet__insert_at` | `void * __thiscall InsertAt(void *this, int index, void *element)` | Insert at position, shift elements, return `this` |
| `0x00424360` | `GenericOPtrSet__remove` | `void __thiscall RemoveRange(void *this, int startIndex, int endIndex)` | Remove inclusive range `[startIndex, endIndex]` |
| `0x0044b290` | `CFlexArray__Free_thunk` | `void __fastcall Free_thunk(void *this)` | Jump thunk to `CFlexArray__Free` |

## Detailed Analysis

### CFlexArray__Init (0x00465530)

Behaviour: a requested capacity of zero becomes 16; the capacity is stored and
an array of that many 4-byte slots is taken from the engine allocator (debug
line `0x22`), and `this` is returned.

**Notes:**
- Default capacity is 16 elements if 0 is passed
- Uses engine memory allocator with debug info (file/line)
- Element size is 4 bytes (pointer/int array)

### CFlexArray__Free (0x00465570)

Behaviour: releases the element array through the engine allocator and nothing
else.

**Notes:**
- Simple memory deallocation
- Does not null the pointer or reset count/capacity

### CFlexArray__Resize (0x00465580)

Behaviour: reallocates the array to the new capacity, clears any slots beyond
the old capacity to null, and records the new capacity.

**Notes:**
- Reallocates memory to new size
- Zero-fills newly allocated space
- Preserves existing elements

### CFlexArray__InitWithGrowth (0x004241a0)

Behaviour: initialises through `CFlexArray__Init`, sets the count to zero and
derives `mGrowth` from the argument (positive values scaled by 16, negative
values lowered by one), then returns `this`.

**Notes:**
- Wrapper around Init that also sets growth strategy
- Positive growth is scaled by 16
- Negative growth is adjusted by -1

### CFlexArray__Clear (0x004241e0)

Behaviour: sets the count to zero.

**Notes:**
- Simply resets element count
- Does not deallocate memory
- Does not zero existing data

### CFlexArray__Add (0x004241f0)

Behaviour: when the array is full it grows (unless `mGrowth` is zero, in which
case the add is dropped) by repeated `CFlexArray__Resize` calls using the
additive or multiplicative rule, then stores the element at the end and bumps
the count; it returns `this`.

**Notes:**
- Auto-grows array when at capacity
- Supports both additive and multiplicative growth
- Returns silently if growth is disabled (mGrowth == 0)

### CFlexArray__InsertAt (0x00424260)

Behaviour: inserting at the current count is delegated to `CFlexArray__Add`;
otherwise it grows as `Add` does, moves the tail one slot right, writes the
element at the index and bumps the count; it returns `this`.

**Notes:**
- Optimized case for append (delegates to Add)
- Shifts existing elements to make room
- O(n) complexity for middle insertions

### CFlexArray__RemoveRange (0x00424360)

Behaviour: an invalid range (negative start, start past end, or end past the
last element) is ignored; a range ending at the last element just truncates the
count to the start; otherwise the elements after the range are moved down to
the start and the count drops by the range length.

**Notes:**
- Inclusive range [start, end]
- Optimized case for removing from end
- Shifts remaining elements to fill gap

## Cross-References

### Callers of CFlexArray functions:

**CFlexArray__Init:**
- `FUN_004241a0` (CFlexArray__InitWithGrowth)

**CFlexArray__Free:**
- `FUN_005391a0` - Unknown caller
- `FUN_00539510` - Unknown caller
- Thunk at `0x0044b290`

**CFlexArray__Resize:**
- `CFlexArray__Add` (0x004241f0)
- `CFlexArray__InsertAt` (0x00424260)

## Technical Notes

1. **Memory Allocator:** Uses custom engine allocator at `0x005490e0` with debug tracking
2. **Element Size:** Fixed at 4 bytes (stores pointers or 32-bit values)
3. **Template Instantiation:** Despite being a template in source, binary shows single instantiation for pointer-sized elements
4. **Calling Convention:** saved Ghidra signatures use `thiscall` for stack-argument helpers and `fastcall` for one-register helpers (`Clear`, `Free`, and `Free_thunk`), with `ECX` as the object pointer.
5. **Proof boundary:** this static pass does not prove exact template instantiations, every call-site element type, runtime behavior, tags, local variable names, or rebuild parity.

## Related Files

- Memory allocator: `mem.cpp` (inferred from allocation functions)
- Used by: Various game systems for dynamic collections
