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

Wave 385 correction: the older base-class rows in this note overclaimed nearby constructor/destructor identities. Current RTTI/vtable read-back resolves `0x005e5078` to `CBinkOpenThread`, not `CFrontEndVideo`, and resolves `0x005e509c` to `CDXGame`. The exact `CFrontEndVideo` base lifecycle remains deferred; do not use the old `0x00541f10`, `0x00541f30`, or `0x00541120` labels as CFrontEndVideo evidence.

Base class behavior should be rechecked in a future media/Bink tranche before promoting new constructor/destructor claims.

Wave1003 (`hud-head-render-state-review-wave1003`) recovered the vtable slot-8 target `0x0046c990 CGame__Shutdown` as a source-backed `CGame::Shutdown` boundary while re-reading the HUD head/render-state cluster. This updates the CDXFrontEndVideo/CDXGame inherited vtable table below: slot 8 is no longer just an anonymous inherited pointer. Related Wave1003 anchors for cross-doc probes: `0x00481b00 CHud__ShutDown`; `0x00481400 CHud__ctor_base`; `0x00482090 HudRenderState__ApplyOverlaySpriteState`; `0x004821b0 CDXCompass__ApplyRenderStateModulate`; `0x00482210 CHud__RenderSegmentedMeterBar`; `472/1408 = 33.52%`; `641/1478 = 43.37%`; `371/500 = 74.20%`; `6223/6223 = 100.00%`; `G:\GhidraBackups\BEA_20260531-120949_post_wave1003_hud_head_render_state_review_verified`. Runtime shutdown behavior, exact layout/source identity, BEA patching, and rebuild parity remain separate proof.

---

## 2026-05-19 Wave594 CDXFMV Embedding Note

Wave594 does not mutate the saved `CDXFrontEndVideo` rows in this file, but it adds static read-back context for the lower-level FMV wrapper. The new `CDXFMV__ctor_base` row at `0x0053f0f0` constructs the embedded `CDXFrontEndVideo` object at `this+0x10` after installing the base `CFMV` vtable and before installing the `CDXFMV` vtable. The companion `CDXFMV__DestructorBody` row tears down that embedded object path before `CMonitor__Shutdown(this)`.

This links the `DXFMV.CPP` wrapper to the documented `DXFrontEndVideo.cpp` video object at the static Ghidra level only. Runtime FMV/Bink playback behavior, exact `CDXFMV` and `CDXFrontEndVideo` layouts, and rebuild parity remain deferred.

---

## 2026-05-19 Wave597 CDXFrontEndVideo Head Note

Wave597 saved clean signatures, comments, and `cdxfrontendvideo-head-wave597` tags for the CDXFrontEndVideo head cluster at `0x00541200` through `0x00541d30`. The pass renamed the older generic `CDXFrontEndVideo__dtor` label to `CDXFrontEndVideo__scalar_deleting_dtor`, because vtable `0x005e5084` slot 0 points at a `RET 0x4` delete-flag wrapper that conditionally frees `this` and returns it.

The wave covers constructor/lifecycle, default-size fallback, open/init/close, width/height accessors, render, and update. Static read-back ties the cluster to `CFEPMultiplayerStart__ctor`, `CDXFMV__ctor_base`, `CFEPCommon__Init/StartVideo/StopVideo/Shutdown`, `CFrontEnd__RenderVideoQuadScaledToWindow`, `CFrontEnd__Process`, and CDXFMV raw call sites. It also records the observed Bink handle at `this+0x08`, two texture slots at `this+0x0c/0x10`, current texture index at `this+0x14`, frame/copy flags at `this+0x18/0x1c`, fallback dimensions at `this+0x20/0x24`, and fade/callback-ish state at `this+0x28/0x2c`.

This is saved static Ghidra evidence only. Runtime Bink playback, async scheduling, Direct3D texture upload, frontend-visible video behavior, exact source identity, complete class layouts, BEA patching, and rebuild parity remain deferred.

---

## 2026-05-24 Wave799 Render Byte-Flag Microhelpers

Wave799 PC utility microhelpers (`pc-utility-microhelpers-wave799`, `wave799-readback-verified`) saved static comments/tags for two byte-flag helpers called by `CDXFrontEndVideo__Render`: `0x00441e20 CDXFrontEndVideo__ClearByteFlag` and `0x00441e30 CDXFrontEndVideo__SetByteFlagAndReturnOld`. The clear helper writes zero to the byte pointed to by `ECX`; the set helper reads the old low byte at `[ECX]`, writes `1`, and returns the old value in `AL` while the upper `EAX` bits remain semantically unproven. Verified backup: `G:\GhidraBackups\BEA_20260524-063302_post_wave799_pc_utility_microhelpers_verified`. Exact owning field offset, runtime Bink/video behavior, BEA patching, and rebuild parity remain deferred.

---

## Functions (12 total)

### CDXFrontEndVideo::CDXFrontEndVideo (Constructor)
| Property | Value |
|----------|-------|
| Address | 0x00541200 |
| Ghidra Name | `CDXFrontEndVideo__CDXFrontEndVideo` |
| Signature | `void __fastcall CDXFrontEndVideo__CDXFrontEndVideo(void * this)` |
| Returns | void |

**Purpose:** Initializes a CDXFrontEndVideo instance. Sets up vtable and zeroes member variables.

**Key Operations:**
- Sets vtable to 0x005e5084
- Clears Bink handle (this+0x08 = 0)
- Clears texture pointers (this+0x0C, this+0x10 = 0)
- Initializes flags (this+0x2C = 0)

---

### CDXFrontEndVideo Scalar Deleting Destructor
| Property | Value |
|----------|-------|
| Address | 0x00541220 |
| Ghidra Name | `CDXFrontEndVideo__scalar_deleting_dtor` |
| Signature | `void * __thiscall CDXFrontEndVideo__scalar_deleting_dtor(void * this, byte delete_flags)` |
| Returns | this |

**Purpose:** Scalar deleting destructor wrapper. Vtable `0x005e5084` slot 0 points here; `RET 0x4` proves one stack argument after `this`, and the body conditionally frees memory when `delete_flags & 1` is set.

---

### CDXFrontEndVideo::SetDefaultSize
| Property | Value |
|----------|-------|
| Address | 0x00541240 |
| Ghidra Name | `CDXFrontEndVideo__SetDefaultSize` |
| Signature | `int __fastcall CDXFrontEndVideo__SetDefaultSize(void * this)` |
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
| Ghidra Name | `CDXFrontEndVideo__Close` |
| Signature | `void __fastcall CDXFrontEndVideo__Close(void * this)` |
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
| Ghidra Name | `CDXFrontEndVideo__Open` |
| Signature | `void __thiscall CDXFrontEndVideo__Open(void * this, char * video_path, int fallback_width, int fallback_height, int open_flags, int async_open, int callback_cookie)` |
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
| Ghidra Name | `CDXFrontEndVideo__InitVideo` |
| Signature | `void __fastcall CDXFrontEndVideo__InitVideo(void * this)` |
| Returns | void |

**Purpose:** Initializes video playback after file is opened. Creates textures and prepares first frame.

**Key Operations:**
- Gets Bink handle from global (DAT_008a9830)
- On failure: prints "failed to find file", triggers error handling
- Calls BinkDoFrame, BinkNextFrame to prepare first frame
- Allocates 2 `CUMTexture` objects for double buffering (via `OID__AllocObject` and `CUMTexture__ctor_base`)
- Calculates power-of-2 texture dimensions (min 128, capped by display size)
- Calls `CUMTexture__ConfigureByMode(texture, selected_size, 5 - (DAT_008a9a54 != 0), 1)` after Wave522 corrected the CUMTexture signature shape
- Sets m_bFrameReady = 1, m_bCopyComplete = 0

Wave522 note: the `CUMTexture` allocation/configuration evidence is saved static Ghidra read-back only. It does not prove runtime Bink texture upload behavior, runtime GPU behavior, or rebuild parity.

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
| Ghidra Name | `CDXFrontEndVideo__CloseVideo` |
| Signature | `void __fastcall CDXFrontEndVideo__CloseVideo(void * this)` |
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
| Ghidra Name | `CDXFrontEndVideo__GetWidth` |
| Signature | `int __fastcall CDXFrontEndVideo__GetWidth(void * this)` |
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
| Ghidra Name | `CDXFrontEndVideo__GetHeight` |
| Signature | `int __fastcall CDXFrontEndVideo__GetHeight(void * this)` |
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
| Ghidra Name | `CDXFrontEndVideo__Render` |
| Signature | `int __thiscall CDXFrontEndVideo__Render(void * this, float x, float y, float z, float scale_x, float scale_y, uint packed_argb, int centered)` |
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
| Ghidra Name | `CDXFrontEndVideo__Update` |
| Signature | `int __thiscall CDXFrontEndVideo__Update(void * this, char wait_for_frame)` |
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

### CDXGame::CDXGame (Owner Correction)
| Property | Value |
|----------|-------|
| Address | 0x00541f10 |
| Ghidra Name | CDXGame__ctor |
| Signature | `void * __fastcall CDXGame__ctor(void * this)` |
| Returns | this |

**Purpose:** Wave 385 corrects the older `CFrontEndVideo` constructor label. The function calls `CGame__ctor`, then installs the `CDXGame` secondary vtable at `0x005e509c`; RTTI resolves that vtable to `CDXGame`, and Stuart source defines `CDXGame : CGame`.

---

### CBinkOpenThread::CBinkOpenThread (Owner Correction)
| Property | Value |
|----------|-------|
| Address | 0x00541120 |
| Ghidra Name | CBinkOpenThread__ctor |
| Signature | `void * __fastcall CBinkOpenThread__ctor(void * this)` |
| Returns | this |

**Purpose:** Wave 385 corrects the older `CFrontEndVideo` destructor label. The function calls the waiting-thread constructor at `0x00528bc0`, installs vtable `0x005e5078`, and RTTI for that vtable resolves to `CBinkOpenThread`. The adjacent `0x00541140` vtable-slot body remains deferred.

Wave571 update: `0x00528bc0` is now saved as `CWaitingThread__ctor_base`, not the older `CWaitingThread__ctor_like_00528bc0` placeholder. Adjacent saved helpers now cover `CBinkOpenThread__WorkerMain`, `CBinkOpenThread__Init`, `CBinkOpenThread__WaitForThread`, `CBinkOpenThread__StartAsync`, `CBinkOpenThread__RunSync`, `CBinkOpenThread__IsRunning`, `CBinkOpenThread__Lock`, and `CBinkOpenThread__Unlock`. Xrefs tie the cluster to `CDXFrontEndVideo__Open/Update/InitVideo/CloseVideo/Render`, Bink voice queue pumping, Goodies loading polling, mission object-code async loading, and message-box voice/text reveal. This is saved static Ghidra evidence only; runtime Bink/media/thread scheduling behavior, exact class layouts, source identity, BEA patching, and rebuild parity remain deferred.

---

### CDXGame Scalar Deleting Destructor (Owner Correction)
| Property | Value |
|----------|-------|
| Address | 0x00541f30 |
| Ghidra Name | CDXGame__scalar_deleting_dtor |
| Signature | `void * __thiscall CDXGame__scalar_deleting_dtor(void * this, byte flags)` |
| Returns | this |

**Purpose:** Wave 385 corrects the older `CFrontEndVideo` scalar-destructor label. The function calls `CDXGame__dtor_thunk`, checks the delete flag, optionally frees `this`, and returns `this`.

---

## Vtable Layout

### CDXFrontEndVideo vtable (0x005e5084)
| Index | Offset | Address | Function |
|-------|--------|---------|----------|
| 0 | 0x00 | 0x00541220 | CDXFrontEndVideo__scalar_deleting_dtor (Wave597) |
| 1 | 0x04 | 0x00405930 | (inherited) |
| 2 | 0x08 | 0x005019C0 | (inherited) |
| 3 | 0x0C | 0x00405930 | (inherited) |
| 4 | 0x10 | 0x00405930 | (inherited) |
| 5 | 0x14 | 0x00619AD0 | (inherited) |
| 6 | 0x18 | 0x0046FF10 | (inherited) |
| 7 | 0x1C | 0x00541F30 | CDXGame::scalar_deleting_dtor (Wave 385 owner correction; this table needs future media-specific revalidation before interpreting inheritance) |
| 8 | 0x20 | 0x0046C990 | CGame__Shutdown (Wave1003 boundary recovery; inherited CDXGame/CGame shutdown target) |
| 9 | 0x24 | 0x0046F7E0 | (inherited) |
| 10 | 0x28 | 0x004014A0 | (inherited) |
| 11 | 0x2C | 0x004DB8C0 | (inherited) |

### CBinkOpenThread vtable (0x005e5078, Wave 385 RTTI correction)
| Index | Offset | Address | Function |
|-------|--------|---------|----------|
| 0 | 0x00 | 0x00541140 | Deferred CBinkOpenThread vtable-slot body |
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
