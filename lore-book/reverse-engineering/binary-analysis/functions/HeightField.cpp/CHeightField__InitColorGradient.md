# CHeightField__InitColorGradient

> Address: 0x0047e8e0 | Source: HeightField.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** No (source file not present in the current public reference snapshot)

## Purpose
Initializes the terrain color gradient table (64 entries) used for distance-based fog/shading. Calculates dimension masks and creates a smooth color transition from base color to fog color based on distance bands.

## Signature
```c
// Thiscall convention (ECX = this)
void CHeightField::InitColorGradient(void);
```

## Decompiled Analysis

### Dimension Setup
```c
// Calculate terrain dimensions from shift values
int xSize = 1 << this->xShift;
int zSize = 1 << this->zShift;

this->xSize = xSize;
this->xMask = xSize - 1;
this->zSize = zSize;
this->zMask = zSize - 1;
this->xzMask = (zSize - 1) << this->xShift;
```

### Color Extraction
The function extracts RGB channels from colorBase (0x107c) and colorMod (0x108c):

```c
uint colorMod = this->colorMod;      // 0x108c - fog/distance color
uint colorBase = this->colorBase;    // 0x107c - base terrain color

// Extract RGB channels
byte modR = (colorMod >> 16) & 0xFF;
byte modG = (colorMod >> 8) & 0xFF;
byte modB = colorMod & 0xFF;

byte baseR = (colorBase >> 16) & 0xFE;  // Note: mask to even
byte baseG = (colorBase >> 8) & 0xFE;
byte baseB = colorBase & 0xFE;
```

### Gradient Calculation
Creates 64 color gradient entries with smooth interpolation:

```c
int* gradient = &this->colorGradient[1];  // Start at offset 0x10d4
for (int i = 64; i > 0; i--) {
    // Red channel: packed in high bits (16-bit position)
    gradient[-1] = (rAccum >> 8) << 16;

    // Green channel: packed in mid bits (11-bit position)
    gradient[0] = (gAccum >> 8) << 11;

    // Blue channel: packed in low bits (5-bit position)
    gradient[1] = (bAccum >> 3) & 0xFFFFFFE0;

    // Interpolate toward fog color
    rAccum += (0xFF - modR) * 4;
    gAccum += (0xFF - modG) * 4;
    bAccum += (0xFF - modB) * 4;

    gradient += 3;
}
```

### Fog Color Copy
```c
// Copy source fog colors to destination
this->fogColorDst[0] = this->fogColorSrc[0];  // 0x13d0 = 0x13c4
this->fogColorDst[1] = this->fogColorSrc[1];  // 0x13d4 = 0x13c8
this->fogColorDst[2] = this->fogColorSrc[2];  // 0x13d8 = 0x13cc
```

## Cross-References

### Called By
| Address | Function | Context |
|---------|----------|---------|
| 0x0047f7ea | CHeightField__Load | During heightfield loading |

### Calls
None - pure computation function.

## Key Values
- **Gradient Entries:** 64 (0x40)
- **Gradient Array Offset:** 0x10d0
- **Entry Size:** 12 bytes (3 ints per entry)
- **Total Gradient Size:** 768 bytes (64 * 12)

## Color Packing Format
The gradient uses RGB565-like packing:
- **Red:** Bits 16-23 (8 bits in position 16)
- **Green:** Bits 11-16 (6 bits in position 11)
- **Blue:** Bits 5-10 (5 bits in position 5)

This matches common 16-bit texture formats used in early 2000s rendering.

## Algorithm
1. Extract RGB from base and modifier colors
2. Start with modifier color (close distance)
3. For each of 64 bands, interpolate toward white (0xFF)
4. Pack into RGB565-like format for fast lookup
5. Copy fog colors for runtime blending

## Notes
- Uses thiscall convention (ECX = this pointer)
- Discovered via CHeightField__Load call analysis (Dec 2025)
- The &0xFE mask on base color channels ensures even values (alignment?)
- Gradient creates distance fog effect for terrain rendering
- 64 bands provides smooth transition over viewing distance

## Related Functions
- [CHeightField__Load](CHeightField__Load.md) - Calls this during initialization
