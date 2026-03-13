# flexarray.cpp - Flexible Array Container

**Source File:** `C:\dev\ONSLAUGHT2\flexarray.cpp`
**Debug String Address:** `0x00629a9c`
**Functions Found:** 8 (including 1 thunk)

## Overview

CFlexArray is a dynamic array template class used throughout the Battle Engine Aquila codebase. It provides automatic memory management with configurable growth strategies (linear or multiplicative).

## Class Structure

```cpp
struct CFlexArray {
    void*  mData;       // +0x00: Pointer to element array
    int    mCapacity;   // +0x04: Current allocated capacity
    int    mCount;      // +0x08: Number of elements in use
    int    mGrowth;     // +0x0C: Growth factor (positive = additive, negative = multiplicative)
};
// Total size: 16 bytes (0x10)
```

### Growth Strategy

The `mGrowth` field controls how the array grows when capacity is exceeded:
- **Positive value (e.g., 16):** Add `mGrowth` to capacity (linear growth)
- **Negative value (e.g., -2):** Multiply capacity by `-mGrowth` (exponential growth)
- **Zero:** Array cannot grow (fixed size)

## Functions

| Address | Name | Signature | Description |
|---------|------|-----------|-------------|
| `0x00465530` | `CFlexArray__Init` | `void Init(int initialCapacity)` | Allocate initial storage |
| `0x00465570` | `CFlexArray__Free` | `void Free()` | Free allocated memory |
| `0x00465580` | `CFlexArray__Resize` | `void Resize(uint newCapacity)` | Resize array, zero-fill new elements |
| `0x004241a0` | `CFlexArray__InitWithGrowth` | `void InitWithGrowth(int capacity, int growth)` | Init with custom growth factor |
| `0x004241e0` | `CFlexArray__Clear` | `void Clear()` | Reset count to 0 (keep capacity) |
| `0x004241f0` | `CFlexArray__Add` | `void Add(void* element)` | Append element, grow if needed |
| `0x00424260` | `CFlexArray__InsertAt` | `void InsertAt(int index, void* element)` | Insert at position, shift elements |
| `0x00424360` | `CFlexArray__RemoveRange` | `void RemoveRange(int start, int end)` | Remove elements [start, end] |
| `0x0044b290` | `CFlexArray__Free_thunk` | (thunk) | Jump to Free |

## Detailed Analysis

### CFlexArray__Init (0x00465530)

```cpp
void CFlexArray::Init(int initialCapacity) {
    if (initialCapacity == 0) {
        initialCapacity = 16;  // Default capacity
    }
    this->mCapacity = initialCapacity;
    this->mData = MemAlloc(initialCapacity * 4, 0x12, "flexarray.cpp", 0x22);
}
```

**Notes:**
- Default capacity is 16 elements if 0 is passed
- Uses engine memory allocator with debug info (file/line)
- Element size is 4 bytes (pointer/int array)

### CFlexArray__Free (0x00465570)

```cpp
void CFlexArray::Free() {
    MemFree(this->mData);
}
```

**Notes:**
- Simple memory deallocation
- Does not null the pointer or reset count/capacity

### CFlexArray__Resize (0x00465580)

```cpp
void CFlexArray::Resize(uint newCapacity) {
    uint oldCapacity = this->mCapacity;
    this->mData = MemRealloc(this->mData, newCapacity * 4);

    // Zero-initialize new elements
    if (oldCapacity < newCapacity) {
        void** ptr = (void**)this->mData + oldCapacity;
        for (int i = newCapacity - oldCapacity; i > 0; i--) {
            *ptr++ = NULL;
        }
    }
    this->mCapacity = newCapacity;
}
```

**Notes:**
- Reallocates memory to new size
- Zero-fills newly allocated space
- Preserves existing elements

### CFlexArray__InitWithGrowth (0x004241a0)

```cpp
void CFlexArray::InitWithGrowth(int capacity, int growth) {
    Init(capacity);
    this->mCount = 0;

    if (growth > 0) {
        this->mGrowth = growth * 16;  // Scaled additive growth
    } else if (growth < 0) {
        this->mGrowth = growth - 1;   // Multiplicative growth factor
    }
}
```

**Notes:**
- Wrapper around Init that also sets growth strategy
- Positive growth is scaled by 16
- Negative growth is adjusted by -1

### CFlexArray__Clear (0x004241e0)

```cpp
void CFlexArray::Clear() {
    this->mCount = 0;
}
```

**Notes:**
- Simply resets element count
- Does not deallocate memory
- Does not zero existing data

### CFlexArray__Add (0x004241f0)

```cpp
void CFlexArray::Add(void* element) {
    if (this->mCapacity <= this->mCount) {
        // Need to grow
        if (this->mGrowth == 0) return;  // Cannot grow

        while (this->mCapacity < this->mCount + 1 && this->mData != NULL) {
            int newSize;
            if (this->mGrowth < 1) {
                newSize = -(this->mGrowth * this->mCapacity);  // Multiplicative
            } else {
                newSize = this->mGrowth + this->mCapacity;     // Additive
            }
            Resize(newSize);
        }
    }

    if (this->mData == NULL) return;

    ((void**)this->mData)[this->mCount] = element;
    this->mCount++;
}
```

**Notes:**
- Auto-grows array when at capacity
- Supports both additive and multiplicative growth
- Returns silently if growth is disabled (mGrowth == 0)

### CFlexArray__InsertAt (0x00424260)

```cpp
void CFlexArray::InsertAt(int index, void* element) {
    if (index == this->mCount) {
        // Insert at end - same as Add
        Add(element);
        return;
    }

    // Ensure capacity (same growth logic as Add)
    // ... growth code ...

    // Shift elements right
    void** ptr = (void**)this->mData + this->mCount;
    while (ptr > (void**)this->mData + index) {
        *ptr = *(ptr - 1);
        ptr--;
    }

    ((void**)this->mData)[index] = element;
    this->mCount++;
}
```

**Notes:**
- Optimized case for append (delegates to Add)
- Shifts existing elements to make room
- O(n) complexity for middle insertions

### CFlexArray__RemoveRange (0x00424360)

```cpp
void CFlexArray::RemoveRange(int start, int end) {
    if (start < 0 || start > end || end >= this->mCount) {
        return;  // Invalid range
    }

    if (end == this->mCount - 1) {
        // Removing from end - just truncate
        this->mCount = start;
        return;
    }

    // Shift elements left
    void** dst = (void**)this->mData + start;
    void** src = (void**)this->mData + end + 1;
    while (src < (void**)this->mData + this->mCount) {
        *dst++ = *src++;
    }

    this->mCount += (start - end) - 1;  // Reduce count
}
```

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
4. **Calling Convention:** thiscall (ECX = this pointer)

## Related Files

- Memory allocator: `mem.cpp` (inferred from allocation functions)
- Used by: Various game systems for dynamic collections
