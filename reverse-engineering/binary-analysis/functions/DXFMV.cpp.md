# DXFMV.CPP Functions

> Source File: DXFMV.CPP | Binary: BEA.exe
> Debug Path: 0x00650644 (`C:\dev\ONSLAUGHT2\DXFMV.CPP`)

## Overview

DirectX Full Motion Video playback implementation. Handles Bink video (.bik) playback for cutscenes and cinematics using the Bink Video SDK.

**Status: STUB - Functions not yet discovered via xref analysis.**

## Debug Path Location

- **Address**: 0x00650644
- **String**: `C:\dev\ONSLAUGHT2\DXFMV.CPP`

## Functions

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| - | - | No functions discovered | 0 xrefs found |

## Notes

- Referenced in the _index.md as having 8 functions (CDXFMV, CBinkOpenThread - Bink video playback, async loading)
- Part of the DX rendering subsystem
- Uses RAD Game Tools Bink Video SDK
- Functions may be inlined or require manual Ghidra analysis
- Related to: DXFrontEndVideo.cpp, Cutscene.cpp

## Expected Functionality

- CDXFMV class - main FMV player
- CBinkOpenThread - async video loading thread
- Bink SDK integration
- Video texture surface management
- Audio sync

## TODO

1. [ ] Find xrefs to debug path string 0x00650644
2. [ ] Analyze CDXFMV class
3. [ ] Document Bink SDK usage
4. [ ] Map threading model

---

*Stub created: 2025-12-16 - Pending xref discovery*
