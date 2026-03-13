# CText__CopyFrom

> Address: 0x004f2660 | Source: text.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** No (source not available)

## Purpose
Copy constructor/assignment operator for CText. Copies all data from a source CText object to this object, allocating new memory for the text buffer and adjusting internal pointers.

## Signature
```c
// Thiscall convention (ECX = this)
void CText::CopyFrom(CText* source);
```

## Parameters
- `source` (param_1): Source CText object to copy from

## Key Observations

### Cleanup Before Copy
If `this->mBuffer` is non-null, calls `OID__FreeObject` (likely memory free) before copying.

### Fields Copied
The function copies these fields from source to destination:
- `mVersion` (offset 0x00)
- `mCount` (offset 0x10)
- `mLoaded` (offset 0x14)
- `mFileSize` (offset 0x18)
- `mLanguage` (offset 0x1C)

### Memory Allocation
Allocates a new backing buffer using `OID__AllocObject`:
- Size: `source->mFileSize`
- Type code: `0x72` (same type code as `CText__Init`)
- Debug string: `"C:\\dev\\ONSLAUGHT2\\text.cpp"`
- Line: `0x155`

### Buffer Copy
Performs optimized memory copy:
1. First loop: copies dwords (4 bytes at a time) for `size >> 2` iterations
2. Second loop: copies remaining bytes (1 byte at a time) for `size & 3` iterations

### Pointer Adjustment
After copying the buffer, adjusts internal pointers relative to new buffer:
```c
this->mTextPool = (source->mTextPool - source->mBuffer) + this->mBuffer;
this->mAudioPool = (source->mAudioPool - source->mBuffer) + this->mBuffer;
```

This maintains the correct offsets when the buffer is at a new memory location.

## Decompiled Code
```c
void CText__CopyFrom(CText* source) {
    // in_ECX = this pointer

    // Free existing buffer if any
    if (this->mBuffer != NULL) {
        FreeMemory(this->mBuffer);
        this->mBuffer = NULL;
    }

    // Reset state
    this->mBuffer = NULL;
    this->mLoaded = 0;
    this->mVersion = 0;
    this->mFileSize = 0;
    this->mLanguage = -1;

    // Copy fields from source
    this->mVersion = source->mVersion;
    this->mCount = source->mCount;
    this->mLoaded = source->mLoaded;
    this->mFileSize = source->mFileSize;
    this->mLanguage = source->mLanguage;

    // Allocate and copy buffer
    uint size = this->mFileSize;
    void* newBuffer = AllocMemory(size, 'r', "text.cpp", 341);
    this->mBuffer = newBuffer;

    // Copy data (optimized dword + byte copy)
    memcpy(newBuffer, source->mBuffer, size);

    // Adjust pointers relative to new buffer
    this->mTextPool = source->mTextPool - source->mBuffer + this->mBuffer;
    this->mAudioPool = source->mAudioPool - source->mBuffer + this->mBuffer;
}
```

## Notes
- Uses manual memcpy implementation rather than calling standard library
- The dual-loop pattern (dwords then bytes) is a common optimization
- Line number 0x155 (341) vs 0x80 (128) in Init suggests different source locations

## Related Functions
- [CText__Init](CText__Init.md) - Primary initialization function
- OID__FreeObject - Memory free function
- OID__AllocObject - Allocates the new backing buffer (type code 0x72, debug path + line)

## References
- Debug path string: 0x00632dd8
- Memory type code: 0x72 ('r' for "resource"?)
