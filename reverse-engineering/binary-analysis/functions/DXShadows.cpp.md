# DXShadows.cpp Functions

> Source File: DXShadows.cpp | Binary: BEA.exe
> Debug Path: 0x00652410 (`C:\dev\ONSLAUGHT2\DXShadows.cpp`)

## Overview

DirectX shadow rendering implementation. Handles the game's shadow system including blob shadows for units and potentially shadow mapping for the terrain.

**Status: STUB - Functions not yet discovered via xref analysis.**

## Debug Path Location

- **Address**: 0x00652410
- **String**: `C:\dev\ONSLAUGHT2\DXShadows.cpp`

## Functions

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| - | - | No functions discovered | 0 xrefs found |

## Notes

- Referenced in the _index.md as having 3 functions (CDXShadows - shadow system, blob shadows)
- Part of the DX rendering subsystem
- Functions may be inlined or require manual Ghidra analysis
- Related to: StaticShadows.cpp, DXLandscape.cpp

## Expected Functionality

- CDXShadows class
- Blob shadow rendering for units
- Shadow projection onto terrain
- Shadow texture management
- Integration with StaticShadows for pre-computed shadows

## TODO

1. [ ] Find xrefs to debug path string 0x00652410
2. [ ] Analyze CDXShadows class
3. [ ] Document shadow projection method
4. [ ] Map integration with terrain system

---

*Stub created: 2025-12-16 - Pending xref discovery*
