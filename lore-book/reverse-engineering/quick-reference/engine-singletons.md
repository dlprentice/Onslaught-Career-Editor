Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
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
DWORD mRenderStateCache[256];
DWORD mTextureStageStateCache[8][32];
```

### Key Methods

**Cached State Setters:**
- `SRS(D3DRENDERSTATETYPE rs, DWORD v)` - Cached SetRenderState
- `STSS(int s, D3DTEXTURESTAGESTATETYPE rs, DWORD v)` - Cached SetTextureStageState
- `SVSS(UINT reg, CONST void* data)` - Cached SetVertexShaderConstant

**Display:**
- `GetWidth()` / `GetHeight()` - Render target dimensions
- `m_dwCreationWidth` / `m_dwCreationHeight` - Window dimensions

**GPU:**
- `CheckForGeforce3()` - Detect GeForce 3 hardware

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
