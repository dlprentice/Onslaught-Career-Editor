# Platform System

> Analysis from Platform.cpp/h, PCPlatform.cpp/h, and d3dapp.cpp/h - December 2025

## Overview

**Purpose**: Platform abstraction layer that routes to platform-specific implementations (PC, Xbox, PS2). This enables the same game code to run across all target platforms by abstracting hardware differences.

---

## Architecture

The platform system uses a compile-time polymorphism pattern with a base class and platform-specific derived classes:

```
CPlatform (base class - Platform.h)
    ├── CPCPlatform     (PC implementation - DirectInput, Win32 API)
    ├── CPS2Platform    (PlayStation 2 - not in Stuart's dump)
    └── CXBOXPlatform   (Xbox - not in Stuart's dump)
```

### Platform Selection

From `Platform.h` lines 40-55:

```cpp
#if TARGET == PC
#include "PCPlatform.h"
extern CPCPlatform PLATFORM;

#elif TARGET == PS2
#include "PS2Platform.h"
extern CPS2Platform PLATFORM;

#elif TARGET == XBOX
#include "XBOXplatform.h"
extern CXBOXPlatform PLATFORM;
#endif
```

The global `PLATFORM` singleton provides access to the platform-specific implementation. Code throughout the game calls `PLATFORM.Method()` and gets the correct platform behavior automatically.

---

## CPlatform Base Class

The base class in `Platform.h` is remarkably minimal - it defines the common interface that all platforms must implement:

```cpp
class CPlatform {
public:
    void Flip(BOOL in_game = FALSE);
};
```

### Flip() Method - Emergency Stop Mechanism

From `Platform.cpp` lines 14-21:

```cpp
void CPlatform::Flip(BOOL in_game) {
    // Emergency stop mechanism - infinite loop if console signals halt
    while (CONSOLE.mStopEverything);

    // Otherwise, delegate to platform-specific frame flip
    PLATFORM.DeviceFlip(in_game);
}
```

The `Flip()` method handles frame buffer presentation. The `mStopEverything` check allows the debug console to halt the game loop entirely (useful for debugging crashes or inspecting state).

---

## Quit Types (EQuitType)

Returned by `CPlatform::Process()` to signal the game loop about desired state transitions:

| Constant | Value | Description |
|----------|-------|-------------|
| `QT_NONE` | 0 | No quit requested |
| `QT_QUIT_TO_FRONTEND` | 1 | Return to main menu |
| `QT_QUIT_TO_SYSTEM` | 2 | Exit to operating system |
| `QT_LOAD_ERROR` | 3 | Asset loading failure |
| `QT_RESTART_LEVEL` | 4 | Restart current mission |
| `QT_QUIT_TIMEOUT` | 5 | Inactivity timeout (idle detection) |
| `QT_USER_QUIT_TO_FRONTEND` | 6 | User-initiated menu exit |
| `QT_USER_QUIT_TO_TITLE_SCREEN` | 7 | User-initiated title exit |

---

## Font Types (EFontType)

| Constant | Value | Description |
|----------|-------|-------------|
| `FONT_NORMAL` | 0 | Standard game text (22pt bitmap) |
| `FONT_SMALL` | 1 | Small text (13pt bitmap) |
| `FONT_DEBUG` | 2 | Debug overlay (7pt system font "Terminal") |
| `FONT_TITLE` | 3 | Title/header text (32pt bitmap) |

The font system uses bitmap fonts loaded from TGA texture files. Each platform may use different font assets (PC vs Xbox have separate font files).

---

## Key Callback Type

```cpp
typedef void (*pKeyTrapper)(BYTE key, KeyEventType event);
```

This function pointer type is used for keyboard input handling. The `SetKeytrap()` method allows registering a callback for keyboard events.

---

## CPCPlatform Implementation (PC)

The PC platform implementation is the most comprehensive in the current reference snapshot.

### Class Structure

```cpp
class CPCPlatform : public CPlatform {
public:
    // Lifecycle
    BOOL Init();
    void Shutdown();
    EQuitType Process();

    // Rendering
    BOOL BeginScene();
    void EndScene();
    void DeviceFlip(BOOL in_game);
    void ClearScreen(DWORD col);

    // Screen dimensions
    SINT GetScreenWidth();
    SINT GetScreenHeight();
    int GetWindowWidth();
    int GetWindowHeight();

    // Timing
    float GetFPS();
    float GetSysTimeFloat();

    // Input
    BOOL UpdateJoystick(int joypad);
    BOOL KeyOn(SINT c);
    BOOL KeyOnce(SINT c);
    void FlushInputBuffers();
    void SetKeytrap(pKeyTrapper trap);

    // Rumble/vibration
    void TriggerRumble(int pad);
    void SetRumbleEnabled(BOOL aRumble);

    // Rendering features
    void SetVertexShadersEnabled(BOOL aShaders);
    void SetGeforce3(BOOL f);
    BOOL IsGeforce3();

    // Font access
    CBITMAPFONT* Font(EFontType aFontType);
    CBITMAPFONT* Font();
    CBITMAPFONT* DebugFont();
    CBITMAPFONT* SmallFont();
    CBITMAPFONT* TitleFont();

    // Viewport
    void SetViewport(CViewport *vp);
    void MakeD3DViewport(D3DVIEWPORT8 *out, CViewport *in);

    // Matrix conversion
    void FMatrixToD3DMatrix(D3DMATRIX *out, FMatrix *in);

    // User interaction
    BOOL Ask(char *msg);

    // Registry (volatile)
    void SetRegKey(char *keyname, char *value);
    void GetRegKey(char *keyname, char *value);

    // Serialization
    void Serialize(CChunker *c, CResourceAccumulator *ra);
    void Deserialize(CChunkReader *c);
    void InitFonts();
    void AccumulateResources(CResourceAccumulator *accumulator);

protected:
    CFrameTimer*    mFrameTimer;
    LARGE_INTEGER   mFrequency;
    float           mClockDivisor;
    BOOL            mGeforce3;
    long            mMemorySize;
    CBITMAPFONT*    mFont;
    CBITMAPFONT*    mDebugFont;
    CBITMAPFONT*    mSmallFont;
    CBITMAPFONT*    mTitleFont;
    CBITMAPFONT*    mXboxFont;
    CBITMAPFONT*    mSmallXboxFont;
};
```

---

## Initialization (Init)

The `Init()` method (`PCPlatform.cpp` lines 22-78) performs critical platform setup:

1. **Frame Timer**: Creates `CFrameTimer` for FPS tracking
2. **Performance Counter**: `QueryPerformanceFrequency()` for high-resolution timing
3. **Math Test**: Optional `MATHTEST.Run()` for floating-point validation (ifdef MATH_TEST)
4. **GPU Detection**: `LT.IsThisAGeForce3()` - checks for GeForce 3 hardware

### GeForce 3 Requirement

```cpp
mGeforce3 = LT.IsThisAGeForce3();

if (CLIPARAMS.mForcedCard) {
    mGeforce3 = CLIPARAMS.mGeforce3;  // CLI override (-geforce2/-geforce3)
} else {
    if (!mGeforce3) {
        LT.ForceToWindow();  // Fallback to windowed mode
        if (!PLATFORM.Ask("This game only runs on GeForce 3 cards.\n"
                          "Press OK if you have a GeForce 3 card installed."))
            exit(1);
        mGeforce3 = TRUE;  // User claims they have one
    }
}
```

The game was designed for GeForce 3 hardware (the first GPU with programmable vertex shaders). Non-GeForce 3 systems trigger a warning dialog and may run in degraded mode.

---

## Font System

Six font objects are managed (`PCPlatform.cpp` lines 82-129):

| Font | Texture File | Size | Purpose |
|------|--------------|------|---------|
| `mFont` | `font22.512.tga` | 32 | Normal text |
| `mDebugFont` | System "Terminal" | 7pt | Debug overlay |
| `mSmallFont` | `Font13PS.tga` | 16 | Small text |
| `mTitleFont` | `TitleFont.tga` | 32 | Titles |
| `mXboxFont` | `font22.512Xbox.tga` | 32 | Xbox-specific |
| `mSmallXboxFont` | `font13Xbox.tga` | 16 | Xbox small text |

### Character Swap Hack

`mFont->EnableCharSwapHack()` (JCL comment) - this suggests some characters in the font texture were repurposed for special glyphs (likely gamepad button icons).

### Per-Platform Serialization

From lines 366-393:

```cpp
if (ra->GetTargetPlatform() == XBOX) {
    mXboxFont->Serialize(c, ra);
    // ... Xbox fonts
} else if (ra->GetTargetPlatform() == PS2) {
    mFont->Serialize(c, ra);
    // ... PS2 fonts (note: reuses mSmallFont twice - possible bug)
} else {
    mFont->Serialize(c, ra);
    // ... PC fonts
}
```

---

## High-Resolution Timing

The `GetSysTimeFloat()` method (lines 241-261) provides precise timing using Windows Performance Counter:

```cpp
float CPCPlatform::GetSysTimeFloat() {
    LARGE_INTEGER ts;
    static BOOL fs_done = FALSE;
    static LARGE_INTEGER first_seen;

    if (mFrequency.QuadPart) {
        QueryPerformanceCounter(&ts);
        if (!fs_done) {
            first_seen.QuadPart = ts.QuadPart;
            fs_done = TRUE;
        }
        // JCL - think about floating point inaccuracies here!!!!!
        return float(ts.QuadPart - first_seen.QuadPart) /
               (float(mFrequency.QuadPart) * mClockDivisor);
    }
    return float(timeGetTime()) / 1000.0f;  // Fallback to millisecond timer
}
```

**JCL's Comment**: The developer was concerned about floating-point precision loss. Subtracting from `first_seen` prevents precision degradation on systems with high uptime where the counter would be very large.

---

## Registry Access (Volatile)

**CRITICAL DISCOVERY**: PC settings use the Windows registry with `REG_OPTION_VOLATILE` flag (lines 464-503).

### Registry Path

```
HKEY_CURRENT_USER\Software\Lost Toys\Battle Engine Aquila
```

### Implementation

```cpp
void CPCPlatform::SetRegKey(char *keyname, char *value) {
    HKEY key;
    DWORD disposition;
    RegCreateKeyEx(HKEY_CURRENT_USER,
                   "Software\\Lost Toys\\Battle Engine Aquila",
                   0, "REG_SZ",
                   REG_OPTION_VOLATILE,  // NOT persisted across reboots!
                   KEY_ALL_ACCESS, NULL, &key, &disposition);
    RegSetValueEx(key, keyname, 0, REG_SZ, (unsigned char *)value, strlen(value)+1);
    RegCloseKey(key);
}
```

### Volatile Flag Implications

The `REG_OPTION_VOLATILE` flag means registry settings exist **only in memory** and are **NOT persisted across reboots**. This is unusual for game settings and suggests the registry was used for:

- Inter-process communication (editor tools)
- Session-only state
- Debug/developer settings

**Permanent** settings are stored in game-generated files, not the volatile registry:
- Global options are stored in `defaultoptions.bea` (retail-observed 10,004-byte envelope with a `CCareer` core plus options/tail blocks).
- Career saves (`.bes`) use the same retail envelope shape, but in the Steam build they load via `CCareer::Load(..., flag=1)` which does **not** apply options entries/tail snapshot and preserves pre-load Sound/Music floats (so `.bes` is not a reliable persistence vehicle for those settings).
- The only persisted god-related field we track in this build is `g_bGodModeEnabled` (but it remains cheat-gated at runtime).

---

## Input Handling

| Method | Purpose |
|--------|---------|
| `KeyOn(c)` | Returns TRUE if key `c` is currently held |
| `KeyOnce(c)` | Returns TRUE only on key press (not repeat) |
| `FlushInputBuffers()` | Clear all pending input |
| `UpdateJoystick(joypad)` | Poll gamepad state |
| `SetKeytrap(trap)` | Register keyboard callback |

These delegate to the `LT` global (Lost Toys shell/framework).

---

## PC Key Code Constants

From `PCPlatform.h` lines 6-52:

| Constant | Windows VK |
|----------|-----------|
| `KEYCODE_BACK` | VK_BACK |
| `KEYCODE_TAB` | VK_TAB |
| `KEYCODE_RETURN` | VK_RETURN |
| `KEYCODE_SHIFT` | VK_SHIFT |
| `KEYCODE_CONTROL` | VK_CONTROL |
| `KEYCODE_ESCAPE` | VK_ESCAPE |
| `KEYCODE_SPACE` | VK_SPACE |
| `KEYCODE_LEFT/RIGHT/UP/DOWN` | VK_LEFT/RIGHT/UP/DOWN |
| `KEYCODE_F1` - `KEYCODE_F12` | VK_F1 - VK_F12 |
| `KEYCODE_NUMPAD0` - `KEYCODE_NUMPAD9` | VK_NUMPAD0 - VK_NUMPAD9 |

These are used throughout the codebase for platform-independent key references.

---

## Cross-Platform Constants Comparison

| Feature | PC | Xbox | PS2 |
|---------|-----|------|-----|
| Graphics API | DirectX 8 | DirectX subset | DMA lists |
| Font files | font22.512.tga | font22.512Xbox.tga | (shared with PC) |
| Registry | Volatile HKCU | N/A | N/A |
| Vertex shaders | Optional (GeForce 3) | Required | N/A |
| Controller ports | 4 (via LT shell) | 4 (native) | 2 (native) |
| Save location | HDD | Memory Unit + HDD | Memory Card |

---

## Relevance to Save Editing

**NONE directly** - The platform abstraction handles runtime graphics, input, and timing. It does NOT affect save file format or career data.

### Architecture Insights

However, understanding the platform system explains:

1. **Why PC and console saves differ**: Platform-specific code paths diverge at the storage layer
2. **Why there's no PC save implementation in source**: Internal snapshot shows incomplete PC save wiring via this path; do not treat `CPCPlatform`/`PCMemoryCard` stubs as retail implementation evidence.
3. **Registry volatility**: These registry keys are session-only, which helps explain why persistent settings are kept in save/options files rather than this registry path
4. **Font differences**: Xbox uses separate font files, may affect save file icon rendering

### Stuart's Internal Build vs Steam Release

The source reference used here is from the **internal PC build** used during development. The Steam release is a later retail build (console-port lineage) where Encore was the **publisher** and the Windows retail conversion work appears to have been handled in-house at Lost Toys. Compared to the internal build it has:

- Different on-disk save layout (CCareer dump begins at `file+2` after a 16-bit version word; legacy aligned views can look “shift-16”)
- Stubbed PC-specific features
- Different PC-specific implementation paths (the internal source snapshot shows stubs, while the retail binary uses separate working paths)

This explains why directly applying source code logic to Steam saves requires careful verification.

---

## Files Analyzed

| File | Purpose |
|------|---------|
| `Platform.cpp` | Base class Flip() implementation |
| `Platform.h` | Platform routing, EQuitType, EFontType, pKeyTrapper |
| `PCPlatform.cpp` | PC implementation - fonts, timing, input, registry |
| `PCPlatform.h` | CPCPlatform class, key code constants |
| `d3dapp.cpp` | CD3DApplication implementation (1929 lines) |
| `d3dapp.h` | Class definition, data structures (217 lines) |
| `D3DRes.h` | Menu resource IDs (referenced, not present in the current snapshot) |
| `DX.H` | Platform routing (includes d3dapp.h for PC) |

**Not Provided** (mentioned in source but not in Stuart's dump):
- `PS2Platform.cpp/h` - PlayStation 2 implementation
- `XBOXplatform.cpp/h` - Xbox implementation

---

## D3D Application Framework (d3dapp.cpp/h)

The D3D Application Framework provides the DirectX 8 initialization, device management, and window handling for the PC build. This is based on the Microsoft DirectX 8 SDK sample framework (copyright 1998-2000) with Lost Toys modifications.

### Overview

The `CD3DApplication` class is the base class for all DirectX 8 applications in Battle Engine Aquila. The game's main application class inherits from this and overrides virtual methods for game-specific functionality.

**Source File Context:**
```cpp
#if TARGET == PC
// Entire file wrapped in PC-only conditional
#endif
```

This code only compiles for PC builds - Xbox and PS2 use different application frameworks.

### Class Structure

```cpp
class CD3DApplication {
protected:
    // Adapter/Device Management
    D3DAdapterInfo    m_Adapters[10];     // Support up to 10 adapters
    DWORD             m_dwNumAdapters;
    DWORD             m_dwAdapter;         // Current adapter index

    // Window State
    HWND              m_hWnd;              // Main app window
    HWND              m_hWndFocus;         // Focus window (usually same)
    BOOL              m_bWindowed;
    BOOL              m_bActive;
    BOOL              m_bReady;

    // D3D Objects
    LPDIRECT3D8       m_pD3D;              // D3D8 object
    LPDIRECT3DDEVICE8 m_pd3dDevice;        // D3D8 device
    D3DCAPS8          m_d3dCaps;           // Device capabilities
    D3DPRESENT_PARAMETERS m_d3dpp;         // Presentation parameters

    // Timing
    FLOAT             m_fTime;
    FLOAT             m_fElapsedTime;
    FLOAT             m_fFPS;

public:
    virtual HRESULT Create(HINSTANCE hInstance);
    virtual LRESULT MsgProc(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam);
    HRESULT ToggleFullscreen();
    // ... more methods
};
```

### Hardcoded Resolution: 640x480

**CRITICAL**: The display resolution is hardcoded to 640x480.

```cpp
#define DX_SCREEN_WIDTH     640
#define DX_SCREEN_HEIGHT    480
```

During device enumeration, the framework specifically searches for 640x480 modes and prefers 32-bit color formats.

**Stuart's Comment (Discord)**: "The display is hardcoded to 640x480 and assumes a GeForce 3."

### Display Format Priority

The framework prefers 32-bit color modes over 16-bit:

| Priority | Format | Bit Depth |
|----------|--------|-----------|
| 1 | `D3DFMT_R8G8B8` | 24-bit (rarely used) |
| 2 | `D3DFMT_A8R8G8B8` | 32-bit with alpha |
| 3 | `D3DFMT_X8R8G8B8` | 32-bit no alpha |
| 4 | Any 16-bit format | 16-bit (fallback) |

This suggests the game was originally designed for 16-bit display but was updated to prefer 32-bit.

### Device Enumeration

The framework enumerates display adapters and devices on startup:

- Filter out resolutions below 640x400
- Try device types: HAL first, REF as fallback

#### Device Types

| Type | Description | Performance |
|------|-------------|-------------|
| `D3DDEVTYPE_HAL` | Hardware Acceleration Layer | Fast (GPU) |
| `D3DDEVTYPE_REF` | Reference Rasterizer | Slow (CPU) |
| `D3DDEVTYPE_SW` | Software device | Medium |

### Vertex Processing Modes

The framework tries vertex processing modes in this order:

1. Pure hardware (fastest) - `D3DCREATE_HARDWARE_VERTEXPROCESSING | D3DCREATE_PUREDEVICE`
2. Hardware vertex processing - `D3DCREATE_HARDWARE_VERTEXPROCESSING`
3. Mixed vertex processing - `D3DCREATE_MIXED_VERTEXPROCESSING`
4. Software vertex processing (slowest fallback) - `D3DCREATE_SOFTWARE_VERTEXPROCESSING`

**Debug Mode FPU Preservation:**
```cpp
#ifdef _DEBUG
    fpumode |= D3DCREATE_FPU_PRESERVE;
#endif
```

### Window/Fullscreen Mode

#### Automatic Fullscreen Toggle

In release builds, the game automatically switches to fullscreen:

**Build Configuration Matrix:**

| Build Type | Default Mode | Notes |
|------------|--------------|-------|
| `_DEBUG` | Windowed | Always windowed for debugging |
| `OPTIMISED_DEBUG` | Windowed | Optimized debug stays windowed |
| `DEV_VERSION` | Windowed* | Fullscreen unless modelviewer/cutsceneeditor |
| Release | Fullscreen | Auto-fullscreen unless `-forcewindowed` |

#### Fullscreen Presentation

**Key Settings:**
- `D3DPRESENT_INTERVAL_ONE` - VSync enabled in fullscreen
- `D3DSWAPEFFECT_DISCARD` - Swap chain mode
- `BackBufferCount = 2` - Triple buffering

### Backbuffer Lockable Flag

```cpp
m_d3dpp.Flags |= D3DPRESENTFLAG_LOCKABLE_BACKBUFFER;
```

This flag enables CPU access to the backbuffer, required for:
- Screen capture functionality (`F8` screenshots)
- Video recording via `CCAPTURE` class
- Blur effects for pause menu

### Menu System Integration

The framework includes menu handling for development builds:

| Menu Command | Action |
|--------------|--------|
| `IDM_CHANGEDEVICE` | Open device selection dialog |
| `IDM_TOGGLEFULLSCREEN` | Toggle fullscreen/windowed |
| `IDM_EXIT` | Quit application |
| `IDM_CAPTUREOPTIONS` | Video capture settings |
| `IDM_CAPTURESTART` | Begin video capture |
| `IDM_STOPCAPTURE` | End video capture |

Context menus are disabled in the retail build but were available in development builds for model viewer and cutscene editor access.

### Error Handling

The framework provides detailed error messages for D3D failures:

| Error Code | Message Summary |
|------------|-----------------|
| `D3DAPPERR_NODIRECT3D` | Could not initialize Direct3D |
| `D3DAPPERR_NOCOMPATIBLEDEVICES` | No compatible D3D devices found |
| `D3DAPPERR_NOWINDOWABLEDEVICES` | Cannot run in desktop window |
| `D3DAPPERR_NOHARDWAREDEVICE` | No hardware-accelerated devices |
| `D3DAPPERR_HALNOTCOMPATIBLE` | HAL doesn't meet requirements |
| `D3DAPPERR_RESIZEFAILED` | Could not reset D3D device |
| `D3DAPPERR_NONZEROREFCOUNT` | D3D object leak detected |

### Integration with Game Systems

The D3D application framework integrates with Lost Toys systems:

| System | Integration Point |
|--------|-------------------|
| `CLIPARAMS` | Command-line parameter checking (`mForceWindowed`, `mModelViewer`, `mCutsceneEditor`) |
| `LT` | Quit trigger (`LT.TriggerQuit()` on WM_CLOSE) |
| `CCAPTURE` | Video capture system |
| `DXUtil_Timer` | Frame timing utilities |

**Quit Flow:**
```cpp
case WM_CLOSE:
    LT.TriggerQuit();  // Signal Lost Toys main loop to exit
    return 0;
```

The framework doesn't destroy resources directly on WM_CLOSE - it signals the main game loop which handles cleanup in proper order.

### Virtual Methods for Game Override

The framework provides virtual methods that the game overrides:

| Method | Purpose |
|--------|---------|
| `ConfirmDevice()` | Validate device meets game requirements |
| `OneTimeSceneInit()` | One-time initialization |
| `InitDeviceObjects()` | Create D3D resources |
| `RestoreDeviceObjects()` | Restore after device reset |
| `FrameMove()` | Update game logic |
| `Render()` | Render the scene |
| `InvalidateDeviceObjects()` | Release before device reset |
| `DeleteDeviceObjects()` | Clean up D3D resources |
| `FinalCleanup()` | Final cleanup on exit |

### GeForce 3 Assumption

As Stuart mentioned, the game "assumes GeForce 3" hardware. This is evident in:

1. **CLIPARAMS integration**: `-geforce2` and `-geforce3` flags force compatibility modes
2. **Vertex shader preference**: Hardware T&L and pure device modes are tried first
3. **Texture format assumptions**: 32-bit preferred over 16-bit
4. **No software T&L fallback warnings**: The game expects GPU-accelerated vertex processing

The GeForce 3 (released March 2001) was the high-end GPU during Battle Engine Aquila's development (2001-2003), featuring:
- Hardware transform and lighting
- Programmable vertex shaders
- 64MB video memory

### Files Analyzed

| File | Purpose |
|------|---------|
| `d3dapp.cpp` | CD3DApplication implementation (1929 lines) |
| `d3dapp.h` | Class definition, data structures (217 lines) |
| `D3DRes.h` | Menu resource IDs (referenced, not present in the current snapshot) |
| `DX.H` | Platform routing (includes d3dapp.h for PC) |

---

## See Also

- [engine-system.md](engine-system.md) - Rendering pipeline
- [../frontend/controller-system.md](../frontend/controller-system.md) - Input handling
- [../io/storage-system.md](../io/storage-system.md) - Save file I/O

---

*Last updated: December 2025*
