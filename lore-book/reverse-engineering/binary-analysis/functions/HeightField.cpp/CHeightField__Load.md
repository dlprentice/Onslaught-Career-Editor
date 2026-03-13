# CHeightField__Load

> Address: 0x0047f750 | Source: HeightField.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** No (source file not present in the current public reference snapshot)

## Purpose
Loads heightfield terrain data from a serialized level resource. Validates expected size (0x13dc = 5084 bytes), allocates height buffer, processes color/lighting data, and reads height samples in 9x9 tile blocks.

## Signature
```c
// Thiscall convention (ECX = this)
void CHeightField::Load(int* pSizePtr);
```

## Decompiled Analysis

### Memory Allocation
```c
// Frees existing buffers
if (this->pUnknown1 != NULL) {
    CMemoryManager::Free(this->pUnknown1);
    this->pUnknown1 = NULL;
}
if (this->pHeightData != NULL) {
    CMemoryManager::Free(this->pHeightData);
    this->pHeightData = NULL;
}

// Allocate new height buffer
// 0xa2000 = 663,552 bytes = 331,776 height samples (16-bit)
this->pHeightData = CMemoryManager::Alloc(0xa2000, 0x22,
    "C:\\dev\\ONSLAUGHT2\\HeightField.cpp", 0x880);
```

### Size Validation
```c
if (*pSizePtr != 0x13dc) {
    sprintf(buffer, "Got size %d, expected %d", *pSizePtr, 0x13dc);
    DebugPrint(buffer);
}
```

### Color Processing
The function processes ARGB color values at offsets 0x107c and 0x108c, extracting RGB channels and normalizing them to prevent overflow past 0xFF.

### Height Data Reading
Height data is read in nested loops:
- Outer: until 0xa2000 bytes read
- 64 iterations (0x40)
- 9x9 = 81 height values per tile
- Each value is 2 bytes (16-bit short)

```c
do {
    for (i = 0x40; i != 0; i--) {
        for (j = 9; j != 0; j--) {
            for (k = 9; k != 0; k--) {
                ReadStream(&heightValue, 2, 1);
                *(short*)(offset + this->pHeightData) = heightValue;
                offset += 2;
            }
        }
    }
} while (offset < 0xa2000);
```

### Color Gradient Post-Processing
After loading, the function doubles color values in the gradient table and clamps to maximum values (RGB565-like encoding).

## Cross-References

### Called By
| Address | Function | Context |
|---------|----------|---------|
| 0x004910d6 | FUN_00491060 | Map deserialization - "Deserializing map" |

### Calls
| Address | Function | Purpose |
|---------|----------|---------|
| 0x00549220 | CMemoryManager::Free | Free existing buffers |
| 0x005490e0 | CMemoryManager::Alloc | Allocate height buffer |
| 0x00423910 | StreamReader::GetTag | Stream reading |
| 0x00423960 | StreamReader::Read | Read data from stream |
| 0x0047e8e0 | CHeightField__InitColorGradient | Initialize color gradient table |
| 0x0055de9b | sprintf | Format error messages |
| 0x0040c640 | DebugPrint | Debug output |

## Key Values
- **Struct Size:** 0x13dc (5084 bytes)
- **Height Buffer Size:** 0xa2000 (663,552 bytes)
- **Height Samples:** 331,776 (16-bit values)
- **Tiles per Load:** 64 (0x40)
- **Tile Size:** 9x9 = 81 height values
- **Alloc Debug Line:** 0x880 (2176 decimal)

## Notes
- Uses thiscall convention (ECX = this pointer)
- Migrated from debug string xref analysis (Dec 2025)
- The 9x9 tile structure suggests terrain patches for LOD
- Color processing suggests fog/ambient color blending
- Related to CResourceAccumulator level loading system

## Related Functions
- [CHeightField__InitColorGradient](CHeightField__InitColorGradient.md) - Called during load
