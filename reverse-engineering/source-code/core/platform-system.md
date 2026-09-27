# Platform System

Status: mixed — source architecture with bounded retail corrections
Last updated: 2026-09-27 (device lifecycle and startup shell rederived; earlier sections retain their evidence limits)
Summary: platform source reference with bounded retail font, device lifecycle, window-message and shell-helper corrections.
Evidence: MEASURED — static pristine font/device-lifecycle bodies, strings, callers and RTTI; SOURCE — the pinned platform implementation elsewhere below.
Specimen: pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Analysis from Platform.cpp/h, PCPlatform.cpp/h, and d3dapp.cpp/h - December 2025

Outside the explicitly dated retail corrections, this page remains inherited
source commentary, not a completed retail audit. In particular, its DirectX 8,
GeForce 3 and fixed-resolution discussion describes the partial source snapshot;
it does not establish retail requirements. Its broader input, registry and save
statements also need their own byte/caller and controlled-execution evidence.

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
| `FONT_DEBUG` | 2 | Debug overlay (system font "Terminal", size argument 7) |
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

The PC platform implementation is the most comprehensive in the provided source.

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

The pinned source initializes six font slots (`PCPlatform.cpp:77–131`). The
retail initializer `0x005155e0`, `CPCPlatform__InitFonts`, initializes four and
unconditionally clears the two Xbox slots. Its complete 457-byte body ends at
`0x005157a9`, SHA-256
`ec8ec8533b96948d5c4854cb3a1750b7eae3165945b77668129f33b781c9bfe0`.
This September 26 recheck corrects the earlier retail filename claim.

| Font | Texture File | Size | Purpose |
|------|--------------|------|---------|
| `mFont` / retail `+0x18` | `font22.512.tga` | 32 | Normal text |
| `mDebugFont` | System "Terminal" | Argument 7 | Debug overlay |
| `mSmallFont` | `Font13PS.tga` | 16 | Small text |
| `mTitleFont` | `TitleFont.tga` | 32 | Titles |
| `mXboxFont` | `font22.512Xbox.tga` in source; retail clears `+0x28` | 32 in source | Source-only initialization |
| `mSmallXboxFont` | `font13Xbox.tga` in source; retail clears `+0x2c` | 16 in source | Source-only initialization |

The actual string at `0x0063e178` is `font22.512.tga`; the former
`font22_512.tga` claim was wrong. Four independent null guards cover
`+0x18/+0x1c/+0x20/+0x24`. The main font gets `+0x168=1` at `0x00515659`.
The debug object installs vtable `0x005e4980` at `0x005156a7`; its RTTI
identifies `CDXBitmapDebugFont`, after the ordinary bitmap base constructor.
It receives `Terminal`, 7 and 0. The small/title strings are `Font13PS.tga`
and `TitleFont.tga`, with sizes 16 and 32. Stores `0x00515796/0x00515799`
clear the two Xbox fields even when their previous values were nonzero.

SYSTEM startup supplies receiver `0x0088a0a8` and calls at `0x004eff2d`
without an explicit argument. The function keeps its `void __thiscall(this)`
interface. Its allocation coordinates and ordered operations identify the source
method, but do not establish source parity. Initialization return values are
unchecked here. Resource availability, allocation-failure behavior, full object
layout and rendered glyphs were not executed or accepted by this static audit.

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

The provided source code is from the **internal PC build** used during development. The Steam release is a later retail build (console-port lineage) where Encore was the **publisher**; per Stuart, the Windows retail release work was done **in-house at Lost Toys** by Jan and possibly others. Compared to the internal build it has:

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
| `D3DRes.h` | Menu resource IDs (referenced, not provided) |
| `DX.H` | Platform routing (includes d3dapp.h for PC) |

**Not Provided** (mentioned in source but not in Stuart's dump):
- `PS2Platform.cpp/h` - PlayStation 2 implementation
- `XBOXplatform.cpp/h` - Xbox implementation

---

## Retail device lifecycle — September 27 correction

This section is a static re-derivation from the pristine specimen above and
source pin `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. The surviving
`ltshell.cpp` has SHA-256
`a83952e2a6822d9d74f26f07116308f28b1f623a34e24008d81fa02232c93513`.
Its `DeviceObject` class declaration is missing; no header layout was invented.

The complete `0x00512d50` body installs the RTTI-bound `DeviceObject` table
`0x005e48c8` at the receiver, then walks and unlinks that receiver from the two
lists headed at `0x00889074` and `0x00889078`, following node member `+4`.
The complete `0x00512ca0` body inserts its stack-supplied node at the first head;
`0x00513d20` moves a found node from that list to the second. Those byte operations
bind the receivers; the saved helper labels are not used as evidence of a shader
owner or a free-list role.

| Retail wrapper | DeviceObject slot | Independently distinguished source identity |
| --- | --- | --- |
| `0x005126f0` | 1 | `PCLTShell::InitDeviceObjects`, `ltshell.cpp:807–841`; literal at `0x0063dde8`, matching input-buffer allocation and active-flag writes |
| `0x00512990` | 2 | `PCLTShell::RestoreDeviceObjects`, `ltshell.cpp:850–864`; shell slot 9 is called after device reset by `0x0052b760` |
| `0x005129f0` | 3 | `PCLTShell::InvalidateDeviceObjects`, `ltshell.cpp:869–879`; shell slot 5 is called before reset by the same caller |
| `0x00512b30` | 4 | `PCLTShell::DeleteDeviceObjects`, `ltshell.cpp:885–909`; clears/frees the same input-buffer fields, releases input objects and clears the active flag |

Each inspected list dispatch supplies `ECX=node`, loads its vtable from `[node]`,
pushes no explicit argument and advances through `[node+4]`. Ordinary callee
register/stack preservation and the node remaining readable after its callback
are premises, not lifetime guarantees proved by this pattern.

**Retail differs from the source.** The source walks one list. Retail
initialization walks `0x00889078` for slot 1 and then slot 2, walks
`0x00889074` for slot 1, calls `0x0054fde0`, then walks that second list for
slot 2. In `0x0052af00`, the successful call through shell slot 8 returns
without the source's separate restore call. Source D3D8 declarations must not
be applied wholesale to retail's D3D9 interfaces.

The ancillary `0x0042c810` calls take constant arguments. These wrappers do not
pass the lifecycle result to that call; invalidation and deletion even overwrite
`AL` with the byte at `0x0063dc20` before testing it. Calling it a lifecycle
result handler would therefore be unsupported.

The existing name-evidence tool checks these reviewed correspondences, both
list transports, unique fixed primary ancestry, every known RTTI holder,
aligned non-code pointer cells, complete-body return cleanup and naming
collisions. The current packet admits 31 resource-method identities across
40 holder occurrences. Shared bodies `0x00405930` and `0x005019c0` span several
methods and remain excluded. `0x00557a90` remains excluded by the automated
switch grammar; that refusal is not proof of a retail defect.

These identities locate the initialization, reset and teardown methods the
rebuild must consult. They do not establish each resource algorithm, exact
return type, device-loss behavior, callback lifetime or visible results.
The cheapest runtime falsifier is a controlled copy with traced lifecycle
calls around initial creation and one device reset, comparing list order and
resource changes. No retail or Godot launch was made for this audit.

Private byte pins, disassembly, source witnesses and refusal tests:
`local-data/test-runs/re-audit-20260926/device-lifecycle/`. The exact Ghidra
cohort and readbacks belong to
`local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/device-lifecycle-v2/`.

## Retail startup shell — September 27 correction

The pristine specimen and source pin above establish partial interface
correspondences, not a complete port of the D3D8 source framework. Both source
classes have 13 virtual methods under the explicit six-undefine analysis profile
(`EDITORBUILD`, `EDITORBUILD2`, `RESBUILDER`, `_DEBUG`, `OPTIMISED_DEBUG`,
`LT_DEBUG`). Retail has 14 slots and a different lifecycle order. The profile
selects source declarations; it does not recover the historical compiler flags.
RTTI independently binds `PCLTShell` to a fixed zero-offset `CD3DApplication` base.

The four lifecycle wrapper identities in the preceding table are now part of
the [eight-name shell correction](../../ghidra/README.md#re-audit-startup-shell-identities--september-27),
along with `FinalCleanup` at `0x00512c30`, `MsgProc` at `0x00512e40`,
`AdjustWindowForChange` at `0x0052bb40` and `AddDeviceObject` at `0x00512ca0`.
Existing prototypes were preserved, not certified by those name corrections.
FinalCleanup clears the byte at shell `+0x330c8` and returns zero; cleanup
caller `0x0052c430` invokes its slot 7 after optional device/interface release.
AdjustWindowForChange selects the stored window style or `0x90080000`, passing
it to `SetWindowLongA` with index −16, then returns zero.

The existing `Create` identity at `0x005290a0` was also rechecked, but is not
counted as a new promoted name disposition. Its 596-byte body registers the
window class via `RegisterClassA` at `0x005291a4` and calls `CreateWindowExA` at
`0x00529230`, using style `0x90ce0000`, which includes visibility. Neither
`ShowWindow` nor `UpdateWindow` is imported or directly called. The source's
release-profile `ToggleFullscreen` branch is absent from this body. These
findings must not become claims that the entire game never changes window mode.

The class registration supplies callback `0x00529070`. That 34-byte original
body dispatches through application slot 12, forwarding four arguments with
16-byte callee cleanup. Its missing saved function boundary remains a separate
structural correction. The existing [controller contract](../../binary-analysis/cpccontroller-vtable-semantics-2026-08-11.md#september-27-window-message-producer-experiment)
records 68 original-code message cases, five separate helper cases and two
counterfactual controls. It distinguishes scan-code indexing, console virtual-key
arguments, trap behavior, release production, suppression and base forwarding.
No Windows dispatch, actual device or desktop acceptance is implied.

`AddDeviceObject` prepends its stack node to head `0x00889074` through member
`+4`; ten direct callers supply the shell singleton in ECX. The initializer at
`0x00512010` and constructor chain `0x00512670` → `0x00528f80` bind that
singleton at `0x00855bb0`. See its [corrected note](../../binary-analysis/functions/CShaderBase.cpp/CShaderBase__Init.md).

### Constant BPP helper: identity and physical interface

The complete eight-byte body at `0x00513640` sets EAX to 32 and uses `RET 4`.
Its former no-argument cdecl signature was contradicted by the bytes and eight
direct callers; all supply one DWORD format argument plus the shell singleton
in ECX. The body itself reads neither argument nor receiver. Call pairs at
`0x005571db` / `0x005571fb`, `0x005582cc` / `0x005582f0`,
`0x005583e7` / `0x00558407` and `0x00559f60` / `0x00559f81`
use the result in texture diagnostics and dimension products divided by eight.
This identifies the BPP helper role; it does not measure actual GPU allocation.

Pinned `ltshell.h:330` and `ltshell.cpp:1723–1737` name `PCLTShell::GetBPP`.
The first source condition includes an un-compared `D3DFMT_Q8W8V8U8` term.
That enum is 63, so the expression always takes the 32 result under the
[documented Direct3D definition](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dformat).
This explains the observed constant body without inventing a sensible format
conversion. The historical header/compiler inputs are unavailable, and no
GetBPP caller survives in the pinned source; retail callers supply the independent
use evidence. The five original-code helper cases confirm 32 for several format
values, including zero and an unknown value. The
[GetBPP correction](../../ghidra/README.md#re-audit-getbpp-identity-and-interface--september-27)
records `int __thiscall PCLTShell__GetBPP(void * this, undefined4 format)`.
The automatic ECX receiver expresses the source-correlated, caller-supplied
member interface; this body does not require a meaningful receiver. The
generic four-byte format retains uncertainty about enum typing and signedness.
The existing source-supported `int` return and EAX:4 storage are preserved;
constant 32 by itself cannot discriminate signed from unsigned result types.
The existing four-byte stack purge, all locals and code bytes are unchanged.
The misleading engine-owner and signature-hardened tags are removed, with the
old note retained as an explicitly fallible lead. These are analysis metadata
changes, not an executable patch or a repair of the retail constant behavior.

Exact fresh decodes, source/RTTI witnesses, revised excluded-Create evidence and
original-code artifacts remain in `local-data/test-runs/re-audit-20260926/startup-shell/`.

## D3D Application Framework (source d3dapp.cpp/h)

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
| `D3DRes.h` | Menu resource IDs (referenced, not provided) |
| `DX.H` | Platform routing (includes d3dapp.h for PC) |

---

## See Also

- [engine-system.md](engine-system.md) - Rendering pipeline
- [../frontend/controller-system.md](../frontend/controller-system.md) - Input handling
- [../io/storage-system.md](../io/storage-system.md) - Save file I/O

---

*Last updated: December 2025*
