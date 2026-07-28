Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Onslaught skills during the skill clean-slate pass.
Summary: Engine singleton and subsystem ownership lookup.
# Onslaught Engine Singletons Reference

This document provides detailed reference for the global singleton instances used throughout the Onslaught engine.

## PLATFORM (CPCPlatform)

**Header:** `PCPlatform.h` (include via `Platform.h`)

The platform abstraction singleton. Provides unified interface for platform-specific functionality.

### Key Methods

**Rendering:**
- `BeginScene()` / `EndScene()` - Frame rendering brackets
- `DeviceFlip(BOOL in_game)` - Present backbuffer
- `ClearScreen(DWORD col)` - Clear render target
- `SetViewport(CViewport *vp)` - Set rendering viewport

**Display:**
- `GetScreenWidth()` / `GetScreenHeight()` - Render target dimensions
- `GetWindowWidth()` / `GetWindowHeight()` - Window dimensions
- `MakeD3DViewport(D3DVIEWPORT8 *out, CViewport *in)` - Convert viewport

**Input:**
- `UpdateJoystick(int joypad)` - Poll controller
- `KeyOn(SINT c)` - Key held down
- `KeyOnce(SINT c)` - Key just pressed
- `FlushInputBuffers()` - Clear input state
- `SetKeytrap(pKeyTrapper trap)` - Set key callback

**Timing:**
- `GetFPS()` - Current frame rate
- `GetSysTimeFloat()` - System time via QueryPerformanceCounter

**Fonts:**
- `Font()` - Normal font
- `DebugFont()` - Debug font
- `SmallFont()` - Small font
- `TitleFont()` - Title font

**Rumble:**
- `TriggerRumble(int pad)` - Trigger force feedback
- `SetRumbleEnabled(BOOL aRumble)` - Enable/disable rumble

**Settings:**
- `SetRegKey(char *keyname, char *value)` - Write registry
- `GetRegKey(char *keyname, char *value)` - Read registry

**GPU Detection:**
- `IsGeforce3()` - Check for GeForce 3 hardware
- `SetGeforce3(BOOL f)` - Set GPU flag
- `SetVertexShadersEnabled(BOOL aShaders)` - Toggle vertex shaders

---

## LT (PCLTShell)

**Header:** `ltshell.h`

The DirectX 8 shell singleton. Inherits from `CD3DApplication` (D3D8 framework class). Manages the D3D device and low-level rendering state.

### Key Members

**D3D Objects:**
- `m_pd3dDevice` - IDirect3DDevice8 pointer
- `m_pD3D` - IDirect3D8 pointer

**Render State Caching:**
```cpp
// references/Onslaught/ltshell.h:48-49, 59-60
#define N_RENDERSTATES        172
#define N_TEXTURESTAGESTATES   30

static DWORD mRenderStates[N_RENDERSTATES];
static DWORD mTextureStageStates[8][N_TEXTURESTAGESTATES];
```

### Key Methods

**Cached State Setters:**
- `SRS(D3DRENDERSTATETYPE state, DWORD value)` - Cached SetRenderState (`ltshell.h:175`)
- `STS(DWORD stage, D3DTEXTURESTAGESTATETYPE type, DWORD val)` - Cached SetTextureStageState (`ltshell.h:190`)
- `D3D_SetVertexShaderConstant(DWORD Register, CONST void* pConstantData, DWORD ConstantCount)` - Vertex shader constant wrapper (`ltshell.h:256`)

**Display:**
- `m_dwCreationWidth` / `m_dwCreationHeight` - Window dimensions (`d3dapp.h:175-176`)

**GPU:**
- `IsThisAGeForce3()` - Detect GeForce 3 hardware (declared `ltshell.h:331`, defined `ltshell.cpp:1742`)

**CORRECTED 2026-07-28 — six identifiers in this section did not exist.**

`grep -rn 'mRenderStateCache\|mTextureStageStateCache\|CheckForGeforce3\|SVSS\|STSS' references/Onslaught/`
returns **zero hits**, and neither `GetWidth` nor `GetHeight` is declared in
`ltshell.h` or `d3dapp.h`. The withdrawn text is quoted in full below so that a
reader who memorised any of it can tell it was corrected rather than lost, and so
that nobody wastes time grepping for a name this document invented:

| Withdrawn (did not exist) | Real declaration |
| --- | --- |
| `DWORD mRenderStateCache[256];` | `static DWORD mRenderStates[N_RENDERSTATES];` — `ltshell.h:59`, bound 172 not 256 |
| `DWORD mTextureStageStateCache[8][32];` | `static DWORD mTextureStageStates[8][N_TEXTURESTAGESTATES];` — `ltshell.h:60`, second bound 30 not 32 |
| `STSS(int s, D3DTEXTURESTAGESTATETYPE rs, DWORD v)` | `STS(DWORD stage, D3DTEXTURESTAGESTATETYPE type, DWORD val)` — `ltshell.h:190` |
| `SVSS(UINT reg, CONST void* data)` | `D3D_SetVertexShaderConstant(DWORD, CONST void*, DWORD)` — `ltshell.h:256`, three parameters not two |
| `CheckForGeforce3()` | `BOOL IsThisAGeForce3();` — `ltshell.h:331`, `ltshell.cpp:1742` |
| `GetWidth()` / `GetHeight()` | no such members; use `m_dwCreationWidth` / `m_dwCreationHeight` (`d3dapp.h:175-176`) |

**Unchanged:** `SRS` was and remains real (`ltshell.h:175`), as are
`m_pd3dDevice` / `m_pD3D` (`d3dapp.h:154-155`) and `m_dwCreationWidth` /
`m_dwCreationHeight` (`d3dapp.h:175-176`). Only the six rows above were wrong. Note
also that the "Inherits from `CD3DApplication`" line above is conditional in
source: `ltshell.h:52-56` selects `CD3DApplication` normally and
`CEditorD3DApp` under `EDITORBUILD2`.

### Window Title

The window title is set to "Battle Engine Aquila":
```cpp
m_strWindowTitle = _T("Battle Engine Aquila");
```

---

## ENGINE (CDXEngine)

**Header:** `DXEngine.h`

The rendering engine singleton. Handles the multi-pass rendering pipeline.

### Key Methods

**Rendering Pipeline:**
- `PreRender()` - Pre-render setup, imposter processing
- `Render(int pass)` - Main render (pass 0 = reflection, pass 1 = main)
- `PostRender()` - Post-render effects, EndScene

**Scene Elements:**
- `RenderLandscape()` - Terrain rendering
- `RenderLandscapeShadows()` - Terrain shadow pass
- `RenderStuff()` - Game objects
- `RenderObjectShadows()` - Object shadow pass
- `RenderParticles()` - Particle systems
- `RenderWater()` - Water surfaces

**Screen Effects:**
- `CaptureScreen()` - Capture for post-processing
- Motion blur in PostRender()

---

## SYSTEM (CSystem)

**Header:** `game.h`

The game system controller singleton. Manages the main game loop lifecycle.

### Key Methods

- `Init()` - Initialize game systems
- `Run()` - Main game loop
- `Shutdown()` - Clean up resources

### Main Loop Location

```cpp
void PCLTShell::MainLoop()
{
    SYSTEM.Init();
    SYSTEM.Run();      // Contains the actual game loop
    SYSTEM.Shutdown();
}
```

---

## MEM_MANAGER (CDXMemoryManager)

**Header:** `DXMemoryManager.h`

The memory management singleton. Provides typed heap allocation.

### Key Methods

**Allocation:**
- `Alloc(UINT size, EMemoryType type, char* file, UINT line)` - Allocate memory
- `ReAlloc(void* mem, UINT size)` - Reallocate
- `Free(void* mem)` - Deallocate
- `FreeAll(EMemoryType type)` - Free all of a type

**Heap Access:**
- `GetDefaultHeap()` - Main heap
- `GetThingHeap()` - Entity heap

**Thing Heap Status:**
- `IsThingHeapNearlyFull()` - Check < 200KB free
- `IsThingHeapFull()` - Check < 10KB free

**Statistics:**
- `GetDefaultHeapSize()` / `GetDefaultUsedSize()` / `GetDefaultPeakSize()`
- `OutputStats(char* filename)` - Write stats to file
- `PrintStats()` - Console output
- `LogDebugStats()` - Debug logging
- `CalcAndShowDeltas()` - Show allocation changes

**Validation:**
- `Validate()` - Check heap integrity
- `DoesExist(void* mem)` - Verify allocation

---

## Related Singletons (Referenced in Code)

These singletons appear in the rendering pipeline but their headers are not in the repository:

| Singleton | Purpose |
|-----------|---------|
| `IMPOSTER` | Imposter billboard system for distant objects |
| `SHADOWS` | Shadow texture rendering |
| `SKY` | Sky/cubemap rendering |
| `WATER_REFLECTION` | Water reflection render-to-texture |

---

## Usage Pattern

Singletons are accessed directly by name throughout the codebase:

```cpp
// Platform operations
PLATFORM.BeginScene();
PLATFORM.ClearScreen(0x00000000);

// Memory allocation
void* ptr = MEM_MANAGER.Alloc(1024, MT_THING, __FILE__, __LINE__);

// Rendering
ENGINE.PreRender();
ENGINE.Render(1);
ENGINE.PostRender();

// D3D state
LT.SRS(D3DRS_ZENABLE, TRUE);
```
