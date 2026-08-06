# Engine System

> Analysis from engine.cpp/h, DXEngine.cpp/h, PCEngine.cpp/h, Camera.cpp/h, and EditorD3DApp.cpp/h - December 2025

## Overview

The Engine system is the core 3D rendering and world management framework. It has **NO direct connection to save files** - all rendering state is runtime-only.

---

## Purpose

`CEngine` provides the rendering pipeline, camera management, and platform
abstraction layer. The `_DIRECTX` arm selects `CDXEngine`. The PS2 arm declares
an external `CPS2Engine`, but the absent `PS2Engine.h` means its implementation
and base class are not established by this source drop.

---

## Class Hierarchy

```
CEngine (base - abstract interface)
    ├── CDXEngine (DirectX 8 implementation - PC/Xbox)   -- DXEngine.h:22
    └── CPCEngine (parallel PC implementation)           -- PCEngine.h:19
```

**CORRECTED 2026-07-28.** This tree previously nested `CPCEngine (PC-specific
extensions)` one level under `CDXEngine`. That derivation does not exist:
`references/Onslaught/PCEngine.h:19` is `class CPCEngine : public CEngine`, the
same abstract base `CDXEngine` derives from at
`references/Onslaught/DXEngine.h:22`. The two are parallel implementations, not a
base and an extension. `CPS2Engine` is INFERRED — it occurs only as
`extern class CPS2Engine ENGINE;` at `engine.h:237`, and `PS2Engine.h` is not in
the pinned drop.

Platform selection is compile-time via preprocessor:

```cpp
#ifdef _DIRECTX
    extern class CDXEngine ENGINE;
#elif TARGET == PS2
    extern class CPS2Engine ENGINE;
#endif
```

---

## Key Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `VIEWPOINTS` | 2 | Split-screen support (explains mIsGod array has 2 elements, one per player) |
| `DEFAULT_Z_FAR` | 256.0f | Default far clipping plane |
| `DEFAULT_Z_NEAR` | 0.1f | Default near clipping plane |
| `MAX_GLOBAL_MESHES` | 256 | Mesh pool size |

---

## Memory/Buffer Size Differences

| Buffer | PC | Xbox/Console |
|--------|-----|--------------|
| Write buffer | 2 MB | 10 KB |
| Sound heap | ~30.7 MB | 6.6 MB |
| Thing heap (debug) | 10 MB | 10 MB |
| Thing heap (release) | 3.5 MB | 3.5 MB |

The PC version has significantly more memory available for buffered I/O and audio, while the console versions are constrained by hardware limits.

---

## Split-Screen Support

The engine supports 2-player split-screen via the `VIEWPOINTS` constant:

```cpp
mCamera[VIEWPOINTS]   // Camera per player
mViewport[VIEWPOINTS] // Viewport per player
mPlayer[VIEWPOINTS]   // Player per viewpoint
```

### Save File Implication

This explains why the **internal build** CCareer contains per-player arrays (e.g., `mIsGod[2]`) to support split-screen multiplayer.

**Steam build correction (Feb 2026):** Do not assume the internal build’s `mIsGod[]` fields exist on disk in the Steam PC port. In the retail binary, the persisted CCareer region at `+0x249C/+0x24A4` is used by the Controls UI for per-player invert-Y toggles (flight/jet + walker), and `+0x2498` is observed as reserved/unused padding.

```cpp
// From CCareer in Career.h
CSArray<BOOL, 2> mIsGod;  // One flag per player
```

---

## Render Pipeline (CDXEngine)

Fixed rendering order from `engine.cpp`:

1. **Gamut/frustum creation** - Determine visible region
2. **LOD calculation** - Level of detail for distant objects
3. **Shadow maps** - (Stencil shadows disabled - see Known Hacks)
4. **Sky** - Skybox rendering (KempyCube)
5. **Landscape** - Terrain with LOD
6. **World objects** - Units, structures, props
7. **Imposters, Trees** - Billboard vegetation
8. **Water** - Water surface plane
9. **Particles** - Effects, explosions
10. **Cockpit** - HUD interior overlays
11. **Screen FX** - Post-processing effects

All rendering state is runtime-only and not persisted to save files.

---

## PC Rendering Engine (CPCEngine)

> Parallel PC implementation of `CEngine`, sibling to `CDXEngine` — `PCEngine.h:19`

**CORRECTED 2026-07-28.** This blockquote previously read "Extends CDXEngine with
PC-specific features". It does not: `references/Onslaught/PCEngine.h:19` is
`class CPCEngine : public CEngine`, exactly as `CDXEngine` is at `DXEngine.h:22`.

This is not cosmetic. The table below is written as though these were features
CPCEngine *adds on top of* CDXEngine. They are not inherited from CDXEngine —
they are `CPCEngine`'s own members over the abstract base, so a reader porting
water reflections or the PatchManager LOD ladder must not go looking for
CDXEngine behaviour underneath them. (Under `_DIRECTX` the pinned drop selects
`CDXEngine`, not `CPCEngine` — `engine.h:229-233`.)

### PC-Specific Features (CPCEngine's own, not inherited from CDXEngine)

| Feature | Implementation |
|---------|----------------|
| **Water Reflections** | Camera mirroring, render-to-texture |
| **Screen Capture** | 1024x512 texture for blur effects (pause menu, transitions) |
| **Split-Screen** | 2 viewpoints supported for multiplayer |
| **Terrain LOD** | PatchManager with 4 detail levels: 33x33, 17x17, 9x9, 5x5 vertices |

### Debug Flags (Bitmask)

Debug visualization flags stored as a bitmask:

| Flag | Value | Purpose |
|------|-------|---------|
| `DRAW_MAP_WHO` | 1 | Unknown map debug display |
| `DRAW_PROFILE` | 2 | Performance profiler overlay |
| `DRAW_OBJECTS_AS_CUBOIDS` | 4 | Replace objects with bounding boxes |
| `DRAW_COCKPIT` | 8 | Draw cockpit interior |
| `DRAW_SKELETAL_ACCURATELY` | 16 | Precise skeletal rendering |
| `DRAW_OUTER_RADIUS` | 32 | Show object collision radii |
| `DRAW_MEM_MANAGER` | 64 | Memory manager visualization |

### Console Variables

Runtime configuration via console commands:

| CVar | Purpose |
|------|---------|
| `cg_renderreflections` | Enable/disable water reflections |
| `cg_texturereflections` | Use render-to-texture reflections (vs. simpler method) |
| `cg_battleenginevisible` | Toggle Battle Engine visibility |

### Rendering Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `DEFAULT_Z_FAR` | 256.0f | Default far clipping plane |
| `DEFAULT_Z_NEAR` | 0.1f | Default near clipping plane |
| Landscape far plane | 700 | Extended draw distance for terrain |
| Blur fade rate | 15/frame | Screen blur dissipation speed |

---

## Known Hacks and Issues

| Issue | Location | Notes |
|-------|----------|-------|
| **Hardcoded sun directions** | Per-skybox | Cubes 2-4, 7-9 have specific sun vectors; all others use default |
| **Stencil shadows disabled** | Commented out | Stencil shadow rendering code is present but disabled |
| **Index buffer bug** | `RenderArrow()` | Bug in arrow debug rendering function |
| **"Horible hack"** | DXEngine.cpp | Developer comment (typo preserved) |

### Hardcoded Sun Directions

The lighting system couldn't automatically determine sun position from skybox textures, requiring manual per-skybox configuration:

```cpp
// Conceptual sun direction lookup
switch (skybox_cube) {
    case 2: case 3: case 4:
        sun_dir = specific_vector_A;
        break;
    case 7: case 8: case 9:
        sun_dir = specific_vector_B;
        break;
    default:
        sun_dir = default_sun_vector;
}
```

### Special Pan Camera Levels

8 levels have the player starting "on something" requiring a different intro camera:

```
221, 222, 231, 232, 331, 332, 523, 524
```

These correspond to carrier-based missions where the Battle Engine starts on a moving platform.

---

## What IS Saved (in CCareer, NOT Engine)

In the Steam build analyzed for this repo, these settings map to CCareer-region offsets below (entries marked pending still require full retail-path verification):

| Setting | Offset | Type | Default |
|---------|--------|------|---------|
| `mSoundVolume` | 0x248C | float (raw IEEE-754) | 1.0 |
| `mMusicVolume` | 0x2490 | float (raw IEEE-754) | 1.0 |
| `g_bGodModeEnabled` | 0x2494 | int/bool (raw 0/1 observed) | 0 |
| (reserved/unused) | 0x2498 | uint32 (observed 0) | 0 |
| Invert Y (Flight/Jet) | 0x249C | int/bool array[2] (Steam: `0=Off`, non-zero=On; verified in `FUN_00407540`) | (varies) |
| Invert Y (Walker) | 0x24A4 | int/bool array[2] (Steam: `0=Off`, non-zero=On; verification pending on walker path) | (varies) |

**Note**: These are `CCareer` members, not `CEngine` members. In the retail `.bes` file, CCareer bytes begin at `file + 2` (true dword view), so file offsets are `file_off = 0x0002 + career_off`. The historical 4-byte-aligned view can make small ints *appear* shifted (`0x00010000`), but that is a misaligned view.

---

## What is NOT Saved (Runtime-Only)

These engine settings exist only at runtime and reset to defaults on game restart:

- Gamma settings
- Reflection toggles
- Debug draw flags
- All rendering state
- Camera positions/orientations
- Viewport configurations
- Terrain LOD settings
- Water reflection quality
- Screen blur state

---

## Relevance to Save Editing

**Indirectly useful.** The engine/system view confirms:

1. **Visual/render option globals are serialized** in options entries + tail (`0x24BE..end`), but `.bes` load (`CCareer::Load(..., flag=1)`) does not apply that block immediately.
2. **VIEWPOINTS=2 explains per-player array shapes** in internal/source classes.
3. **Audio settings ARE saved** as `CCareer` members, not `CEngine` state.

### Architecture Insight

Understanding the engine helps explain:
- Why there's no "graphics settings" section in save files
- Why audio volume IS saved (it's career progression metadata)
- Why god mode is per-player (split-screen multiplayer support)

The engine is important for understanding the game's architecture but has **no impact on .bes save file structure**.

---

## DirectX 8 Framework (internal source lineage)

The pinned internal source targets DirectX 8 (2000-era API). The **shipped retail
Steam `BEA.exe` does not** — it imports `d3d9.dll`. See
[`../../binary-analysis/d3d-default-render-state-block-2026-07-27.md`](../../binary-analysis/d3d-default-render-state-block-2026-07-27.md)
section 2.

**CORRECTED 2026-07-28.** This section previously opened with the unqualified
sentence "The game uses DirectX 8 (2000-era API):". That sentence is true of
Stuart's source drop and false of the game people play, and this document gives a
reader no way to tell which it meant — it interleaves a "Steam build correction
(Feb 2026)" and a Steam-build `CCareer` offset table above.

- **MEASURED (retail):** `BEA.exe.original.backup`, SHA-256
  `74154bfa…7750`, 2,506,752 bytes
  (`local-lab/safe-copy-bea-pristine/`, read-only) contains `d3d9.dll` ×2 and
  `d3d9d.dll` ×1 and **zero** occurrences of `d3d8.dll`. Re-read for this
  correction on 2026-07-28; the live installed `BEA.exe` was not read, because it
  is deliberately patched. The vtable displacement evidence
  (`SetRenderState` at +0x0E4, and a `SetSamplerState` at +0x114 that D3D8 does
  not have at all) is in the binary-analysis note cited above and indexed from
  `RE-INDEX.md`.
- **SOURCE (pinned drop):** genuinely D3D8 — `ltshell.h:168-169`
  (`LPDIRECT3DDEVICE8`), `d3dapp.h:154-155` (`LPDIRECT3D8` /
  `LPDIRECT3DDEVICE8`).

**Unchanged by this correction:** the feature bullets below are accurate
descriptions of the pinned source's D3D8 usage and are not withdrawn. The
equivalent D3D8 statement in
[`../../quick-reference/engine-singletons.md`](../../quick-reference/engine-singletons.md)
is also correct as written, because it is explicitly scoped to `ltshell.h`.

### Rendering Features (as written in the pinned D3D8 source)

- Fixed-function pipeline (pre-shader model 2.0)
- Optional vertex shader support (GeForce 3+)
- Stencil buffer for effects (shadows disabled)
- Render-to-texture for water reflections
- Screen capture for blur effects

### Hardware Requirements

**Target GPU**: GeForce 3 (first GPU with programmable vertex shaders)

From `PCPlatform.cpp`:
```cpp
if (!mGeforce3) {
    LT.ForceToWindow();  // Fallback to windowed mode
    if (!PLATFORM.Ask("This game only runs on GeForce 3 cards.\n"
                      "Press OK if you have a GeForce 3 card installed."))
        exit(1);
}
```

Non-GeForce 3 systems trigger a warning and may run in degraded mode.

---

## Camera System

8 camera types for different gameplay situations (from `Camera.cpp/h`):

| Camera Type | Purpose |
|-------------|---------|
| `CThingCamera` | Base thing-following camera |
| `CThing3rdPersonCamera` | Standard gameplay camera |
| `CViewPointCamera` | Fixed viewpoint |
| `CPanCamera` | Panning shots (carrier intros) |
| `CMovieCamera` | Cutscene camera |
| `CControllableCamera` | Player-controlled free camera (debug) |
| `CGenericCamera` | Generic purpose |
| `CInterpolatedCamera` | Smooth transitions |

### Split-Screen Aspect Ratios

- **Multiplayer**: 0.5 (half screen per player)
- **Single-player**: 0.75 (full screen with HUD)

### Spline Paths

Cameras can follow spline-based paths for cinematic sequences (mission intros, cutscenes).

---

## Developer Notes

**Developer Initials Found** (in Camera.cpp, DXEngine.cpp):
- **JCL** - Unknown developer (memory manager, floating-point concerns)
- **led** - Unknown developer (camera code)
- **kempy** - Unknown team member (skybox named "kempy cube")

**Typos Preserved**:
- "Horible hack" (should be "Horrible") - DXEngine.cpp
- `BUTTON_CAMERA_MOVE_FORAWRD` (should be FORWARD) - Controller.h

---

## Internal Editor Infrastructure (EditorD3DApp)

D3D8 application framework for internal editor tools. Based on Microsoft D3D8 SDK framework (copyright 1998-2000).

### Purpose

This class provides the application shell for Lost Toys internal development tools:
- Model Viewer
- Cutscene Editor
- Particle Editor

These tools were used during development but stripped from the retail build.

### Key Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `N_RENDERSTATES` | 172 | Number of D3D render states tracked |
| `N_TEXTURESTAGESTATES` | 30 | Texture stage state count |
| `MAX_JOYPADS` | 4 | Maximum gamepad support |
| Default resolution | 640x480 | Initial window size |

### Internal Development Tools

**Guarded by `DEV_VERSION` define:**

| Tool | CLI Flag | Purpose |
|------|----------|---------|
| Model Viewer | `-modelviewer` | View and inspect 3D models |
| Cutscene Editor | `-cutsceneeditor` | Edit cinematic sequences |
| Particle Editor | (PARTICLE_ED define) | Particle effect authoring |

### Build Configuration Defines

| Define | Purpose |
|--------|---------|
| `EDITORBUILD` | MFC-based level editor build |
| `EDITORBUILD2` | D3D-based editor tools build |
| `DEV_VERSION` | Enable developer features |
| `LT_DEBUG` | Lost Toys debug mode |

### Video Capture System

Built-in screen recording via `CCAPTURE` class:

| Menu Command | Purpose |
|--------------|---------|
| `IDM_CAPTURESTART` | Begin video capture |
| `IDM_STOPCAPTURE` | End video capture |

### Debug Features

| Feature | Description |
|---------|-------------|
| Exception handler | Source builds contain symbolic stack-reporting code; the measured retail handler only opens/truncates `OnslaughtException.txt` and returns, with no stack walk or symbols |
| Console command | `cg_whatami` - identity/debug info |
| Screen capture | Saves to `grabs\scrNNNN.tga` (sequential numbering) |

---

## Files Analyzed

| File | Purpose |
|------|---------|
| `engine.cpp` | Base engine implementation |
| `engine.h` | CEngine class definition, VIEWPOINTS constant |
| `DXEngine.cpp` | DirectX-specific rendering (PC/Xbox) |
| `DXEngine.h` | CDXEngine class definition |
| `PCEngine.cpp` | PC-specific rendering extensions |
| `PCEngine.h` | CPCEngine class definition, debug flags |
| `Camera.cpp` | Camera system implementation |
| `Camera.h` | Camera types, spline paths |
| `EditorD3DApp.cpp` | Editor application implementation |
| `EditorD3DApp.h` | Class definition, constants |

---

## See Also

- [platform-system.md](platform-system.md) - Platform abstraction layer
- [../gameplay/game-system.md](../gameplay/game-system.md) - Game loop integration
- [../../save-file/save-format.md](../../save-file/save-format.md) - Audio settings in save files

---

*Last updated: December 2025*
