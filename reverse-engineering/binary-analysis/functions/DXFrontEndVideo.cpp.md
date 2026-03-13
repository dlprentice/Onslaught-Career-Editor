# DXFrontEndVideo.cpp - Function Mappings

> DirectX front-end video playback using Bink library
> Source: `C:\dev\ONSLAUGHT2\DXFrontEndVideo.cpp`
> Debug path at: 0x00650744

## Overview

This file implements video playback for the front-end/menu system using the RAD Game Tools Bink video library. It handles FMV (Full Motion Video) playback for cutscenes and intro videos displayed during menus.

**Class Hierarchy:**
```
CFrontEndVideo (base class)
  |
  +-- CDXFrontEndVideo (DirectX implementation)
```

## Class Structure

### CDXFrontEndVideo

**Vtable:** 0x005e5084

| Offset | Member | Type | Description |
|--------|--------|------|-------------|
| 0x00 | vtable | ptr | Virtual function table |
| 0x08 | m_pBink | HBINK | Bink video handle |
| 0x0C | m_pTextures[0] | ptr | Double-buffered texture 0 |
| 0x10 | m_pTextures[1] | ptr | Double-buffered texture 1 |
| 0x14 | m_nCurrentTexture | int | Current texture index (0 or 1) |
| 0x18 | m_bFrameReady | bool | Frame decoded and ready |
| 0x1C | m_bCopyComplete | bool | Frame copied to texture |
| 0x20 | m_nWidth | int | Video/texture width |
| 0x24 | m_nHeight | int | Video/texture height |
| 0x28 | m_nParam | int | Parameter for callbacks |
| 0x2C | m_nFadeAlpha | int | Fade-in alpha (0-255) |

### CFrontEndVideo (Base Class)

**Vtable:** 0x005e5078

Base class for video playback abstraction. CFrontEndVideo provides the interface, CDXFrontEndVideo implements DirectX-specific rendering.

---

## Functions (12 total)

### CDXFrontEndVideo::CDXFrontEndVideo (Constructor)
| Property | Value |
|----------|-------|
| Address | 0x00541200 |
| Signature | `void __thiscall CDXFrontEndVideo::CDXFrontEndVideo(void)` |
| Returns | void |

**Purpose:** Initializes a CDXFrontEndVideo instance. Sets up vtable and zeroes member variables.

**Key Operations:**
- Sets vtable to 0x005e5084
- Clears Bink handle (this+0x08 = 0)
- Clears texture pointers (this+0x0C, this+0x10 = 0)
- Initializes flags (this+0x2C = 0)

---

### CDXFrontEndVideo::~CDXFrontEndVideo (Destructor)
| Property | Value |
|----------|-------|
| Address | 0x00541220 |
| Ghidra Name | CDXFrontEndVideo__dtor |
| Signature | `void __thiscall CDXFrontEndVideo::~CDXFrontEndVideo(byte flags)` |
| Returns | void |

**Purpose:** Scalar deleting destructor. Calls base destructor and optionally frees memory.

---

### CDXFrontEndVideo::SetDefaultSize
| Property | Value |
|----------|-------|
| Address | 0x00541240 |
| Signature | `int __thiscall CDXFrontEndVideo::SetDefaultSize(void)` |
| Returns | 1 (always) |

**Purpose:** Sets default video dimensions to 512x512.

**Key Operations:**
```cpp
this->m_nWidth = 0x200;   // 512
this->m_nHeight = 0x200;  // 512
return 1;
```

---

### CDXFrontEndVideo::Close
| Property | Value |
|----------|-------|
| Address | 0x00541260 |
| Signature | `void __thiscall CDXFrontEndVideo::Close(void)` |
| Returns | void |

**Purpose:** Closes the video and releases the Bink handle.

**Key Operations:**
- Calls CloseVideo() to release resources
- Clears Bink handle (this+0x08 = 0)

---

### CDXFrontEndVideo::Open
| Property | Value |
|----------|-------|
| Address | 0x005412e0 |
| Signature | `void __thiscall CDXFrontEndVideo::Open(char* filename, int width, int height, int param, int async, int callback)` |
| Returns | void |

**Purpose:** Opens a video file for playback using the Bink library.

**Key Operations:**
- Calls RADSetMemory to configure memory allocation
- Stores dimensions (this+0x20, this+0x24)
- Handles async loading via thread
- Copies filename to global buffers
- Calls InitVideo() for synchronous loading

**Related Strings:**
- Uses global filename buffer at 0x008a9834
- Uses backup filename buffer at 0x008a9938

---

### CDXFrontEndVideo::InitVideo
| Property | Value |
|----------|-------|
| Address | 0x00541430 |
| Signature | `void __thiscall CDXFrontEndVideo::InitVideo(void)` |
| Returns | void |

**Purpose:** Initializes video playback after file is opened. Creates textures and prepares first frame.

**Key Operations:**
- Gets Bink handle from global (DAT_008a9830)
- On failure: prints "failed to find file", triggers error handling
- Calls BinkDoFrame, BinkNextFrame to prepare first frame
- Allocates 2 UMTex objects for double buffering (via OID__AllocObject)
- Calculates power-of-2 texture dimensions (min 128, capped by display size)
- Sets m_bFrameReady = 1, m_bCopyComplete = 0

**Bink API Calls:**
- `_BinkDoFrame_4(hBink)` - Decode current frame
- `_BinkNextFrame_4(hBink)` - Advance to next frame

**Error Strings:**
- "failed to find file" (0x0065076c)
- "couldn't create UMTex %d" (0x00650728)

---

### CDXFrontEndVideo::CloseVideo
| Property | Value |
|----------|-------|
| Address | 0x00541650 |
| Signature | `void __thiscall CDXFrontEndVideo::CloseVideo(void)` |
| Returns | void |

**Purpose:** Closes video and releases all resources.

**Key Operations:**
- Prints "Closing FMV\n"
- Waits for async open thread if running ("Waiting for open thread")
- Releases both texture objects
- Gets playback summary via BinkGetSummary
- Prints stats: "%i frames played, %i frames skipped (%i%%)"
- Calls BinkClose to release handle
- Clears Bink handle (this+0x08 = 0)
- Prints "done."

**Bink API Calls:**
- `_BinkGetSummary_8(hBink, summary)` - Get playback statistics
- `_BinkClose_4(hBink)` - Close video handle

---

### CDXFrontEndVideo::GetWidth
| Property | Value |
|----------|-------|
| Address | 0x00541770 |
| Signature | `int __thiscall CDXFrontEndVideo::GetWidth(void)` |
| Returns | Video width |

**Purpose:** Returns the video width. Uses Bink handle if available, otherwise cached value.

```cpp
if (this->m_pBink == NULL)
    return this->m_nWidth;
return this->m_pBink->Width;  // Bink struct offset 0x00
```

---

### CDXFrontEndVideo::GetHeight
| Property | Value |
|----------|-------|
| Address | 0x00541780 |
| Signature | `int __thiscall CDXFrontEndVideo::GetHeight(void)` |
| Returns | Video height |

**Purpose:** Returns the video height. Uses Bink handle if available, otherwise cached value.

```cpp
if (this->m_pBink == NULL)
    return this->m_nHeight;
return this->m_pBink->Height;  // Bink struct offset 0x04
```

---

### CDXFrontEndVideo::Render
| Property | Value |
|----------|-------|
| Address | 0x00541790 |
| Signature | `int __thiscall CDXFrontEndVideo::Render(float x, float y, float z, float scaleX, float scaleY, uint color, int centered)` |
| Returns | 1 (always) |

**Purpose:** Renders the current video frame as a textured quad.

**Key Operations:**
- Handles async file loading completion
- Decodes next frame via BinkDoFrame/BinkNextFrame
- Double-buffer texture management (toggles between textures 0 and 1)
- Locks texture, copies frame via BinkCopyToBuffer
- Handles fade-in animation (m_nFadeAlpha increments by 0x11 per frame)
- Applies color modulation based on fade alpha
- Sets up D3D render states and draws quad primitive

**Bink API Calls:**
- `_BinkDoFrame_4(hBink)` - Decode frame
- `_BinkNextFrame_4(hBink)` - Advance frame
- `_BinkCopyToBuffer_28(hBink, dest, pitch, height, x, y, flags)` - Copy to texture

**Error Strings:**
- "Failed lock" (0x0065080c)
- "DXFEV: LockRect failed: %s" (0x006507f0)

---

### CDXFrontEndVideo::Update
| Property | Value |
|----------|-------|
| Address | 0x00541d30 |
| Signature | `int __thiscall CDXFrontEndVideo::Update(char waitForFrame)` |
| Returns | 0 = playing, 1 = finished, -1 = waiting |

**Purpose:** Updates video playback state, checks for completion.

**Key Operations:**
- Returns 0 if no video loaded
- Calls BinkWait to check if frame ready
- If waitForFrame and not ready, returns -1
- Advances frame if needed via BinkDoFrame/BinkNextFrame
- Checks completion by comparing current frame to total frames
- Returns 1 when video is complete

**Bink API Calls:**
- `_BinkWait_4(hBink)` - Check if ready for next frame
- `_BinkDoFrame_4(hBink)` - Decode frame
- `_BinkNextFrame_4(hBink)` - Advance frame

**Completion Check:**
```cpp
// Bink struct: offset 0x08 = current frame, 0x0C = total frames
if (pBink->CurrentFrame == pBink->TotalFrames)
    return 1;  // Video finished
return 0;      // Still playing
```

---

### CFrontEndVideo::CFrontEndVideo (Base Constructor)
| Property | Value |
|----------|-------|
| Address | 0x00541f10 |
| Signature | `void __thiscall CFrontEndVideo::CFrontEndVideo(void)` |
| Returns | void |

**Purpose:** Base class constructor. Sets up base vtable.

---

### CFrontEndVideo::~CFrontEndVideo (Base Destructor)
| Property | Value |
|----------|-------|
| Address | 0x00541120 |
| Ghidra Name | CFrontEndVideo__dtor |
| Signature | `void __thiscall CFrontEndVideo::~CFrontEndVideo(void)` |
| Returns | void |

**Purpose:** Base class destructor.

---

### CFrontEndVideo Scalar Deleting Destructor
| Property | Value |
|----------|-------|
| Address | 0x00541f30 |
| Ghidra Name | CFrontEndVideo__scalar_dtor |
| Signature | `void __thiscall CFrontEndVideo::scalar_deleting_dtor(byte flags)` |
| Returns | void |

**Purpose:** Scalar deleting destructor for base class.

---

## Vtable Layout

### CDXFrontEndVideo vtable (0x005e5084)
| Index | Offset | Address | Function |
|-------|--------|---------|----------|
| 0 | 0x00 | 0x00541220 | CDXFrontEndVideo::~CDXFrontEndVideo |
| 1 | 0x04 | 0x00405930 | (inherited) |
| 2 | 0x08 | 0x005019C0 | (inherited) |
| 3 | 0x0C | 0x00405930 | (inherited) |
| 4 | 0x10 | 0x00405930 | (inherited) |
| 5 | 0x14 | 0x00619AD0 | (inherited) |
| 6 | 0x18 | 0x0046FF10 | (inherited) |
| 7 | 0x1C | 0x00541F30 | CFrontEndVideo::scalar_deleting_dtor |
| 8 | 0x20 | 0x0046C990 | (inherited) |
| 9 | 0x24 | 0x0046F7E0 | (inherited) |
| 10 | 0x28 | 0x004014A0 | (inherited) |
| 11 | 0x2C | 0x004DB8C0 | (inherited) |

### CFrontEndVideo vtable (0x005e5078)
| Index | Offset | Address | Function |
|-------|--------|---------|----------|
| 0 | 0x00 | 0x00541140 | CFrontEndVideo destructor (code block) |
| 1 | 0x04 | 0x00469C40 | (inherited) |
| 2 | 0x08 | 0x00619A78 | (inherited) |

---

## Bink Video Library Integration

The game uses RAD Game Tools' Bink video codec (binkw32.dll) for FMV playback.

**Imported Functions:**
| Function | Parameters | Purpose |
|----------|------------|---------|
| BinkOpen | (filename, flags) | Open video file |
| BinkClose | (hBink) | Close video |
| BinkDoFrame | (hBink) | Decode current frame |
| BinkNextFrame | (hBink) | Advance to next frame |
| BinkWait | (hBink) | Check timing |
| BinkCopyToBuffer | (hBink, dest, pitch, h, x, y, flags) | Copy frame to buffer |
| BinkGetSummary | (hBink, summary) | Get playback stats |
| BinkSetVolume | (hBink, track, volume) | Set audio volume |
| BinkSetSoundTrack | (tracks, trackIDs) | Configure audio |
| BinkSetSoundSystem | (open, param) | Set sound output |
| BinkOpenDirectSound | (hwnd) | DirectSound output |

**BINK Structure (partial):**
```cpp
struct BINK {
    DWORD Width;          // 0x00
    DWORD Height;         // 0x04
    DWORD TotalFrames;    // 0x08
    DWORD CurrentFrame;   // 0x0C
    // ... more fields
};
```

---

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x00650744 | "C:\\dev\\ONSLAUGHT2\\DXFrontEndVideo.cpp" | Debug path |
| 0x0065076c | " failed to find file" | Error message |
| 0x00650728 | "couldn't create UMTex %d" | Texture allocation error |
| 0x00650784 | "Bink video closing. %i frames played, %i frames skipped (%i%%)\n" | Stats |
| 0x006507c4 | "Waiting for open thread" | Async loading |
| 0x006507e0 | "Closing FMV\n" | Close message |
| 0x0065080c | "Failed lock" | Texture lock error |
| 0x006507f0 | "DXFEV: LockRect failed: %s" | D3D error |

---

## Related Classes

- **CDXFMV** - Lower-level FMV wrapper (RTTI at 0x00650620)
- **CFMV** - Base FMV class (RTTI at 0x00650638)
- **CBinkOpenThread** - Async video loading thread (RTTI at 0x006506D0)
- **CUMTexture** - Unmanaged texture class used for video frames (RTTI at 0x0062d8a8)

---

## Global Variables

| Address | Type | Description |
|---------|------|-------------|
| 0x008a9830 | HBINK | Global Bink handle |
| 0x008a982c | char | Async loading flag |
| 0x008a9834 | char[100] | Video filename buffer |
| 0x008a9938 | char[100] | Backup filename buffer |
| 0x008a97d0 | char[52] | Pending filename buffer |
| 0x008a9804 | int | Async param 1 |
| 0x008a9808 | int | Async param 2 |
| 0x008a9a40 | int | Callback parameter |
| 0x008a9a3c | int | Loading parameter |
| 0x008a9a54 | int | 32-bit texture mode flag |

---

## Notes

1. **Double Buffering:** Uses two textures to avoid frame tearing during playback
2. **Power-of-2 Textures:** Texture dimensions are rounded up to nearest power of 2 (min 128)
3. **Async Loading:** Supports background file loading via thread
4. **Fade-In:** Videos fade in gradually (alpha increments by 17 per frame)
5. **Memory Management:** Uses RADSetMemory callback for custom allocator integration

---

## Cross-References

- Called from CFrontEnd during menu FMV playback
- Uses CTexture::FindTexture for fallback placeholder texture
- Related to -skipfmv command line parameter
