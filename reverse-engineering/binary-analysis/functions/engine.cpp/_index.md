# engine.cpp Functions

> Source File: engine.cpp | Binary: BEA.exe
> Debug Path: 0x00628b40

## Overview

Core engine implementation. CEngine handles rendering subsystems, camera setup, console variables (cvars), and hit effect configuration.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004499d0 | CEngine__Init (TODO) | Initialize engine and subsystems | ~880 bytes |
| 0x0044a020 | CEngine__SetViewpoint | Set camera/viewport/player for a viewpoint slot | ~112 bytes |
| 0x0044a1c0 | [CEngine__UpdatePos](./CEngine__UpdatePos.md) | Per-viewpoint landscape-position update from camera | ~32 bytes |
| 0x0052ff30 | ScriptCommandRegistry__InitBuiltins | Initialize built-in mission script command metadata/dispatch table | Large |
| 0x00528b50 | CEngine__SetNumViewpoints | Set active viewpoint count (`mViewpoints`) | ~16 bytes |
| 0x0053e220 | CDXEngine__PreRender | Per-frame engine pre-render setup (`CViewport*`) | ~180 bytes |
| 0x0053e2e0 | CDXEngine__Render | Per-view world render pass (`viewpoint`) | Large |
| 0x0053ecc0 | CDXEngine__PostRender | HUD/UI/overlay post-render pass (`CViewport*`) | ~1.5 KB |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d23a0 | Unwind@005d23a0 | 135 | Cleanup for 56-byte allocation |
| 0x005d23b9 | Unwind@005d23b9 | 139 | Cleanup for 536-byte allocation |
| 0x005d23d2 | Unwind@005d23d2 | 143 | Cleanup for 15KB allocation |
| 0x005d23eb | Unwind@005d23eb | 147 | Cleanup for 64-byte allocation |
| 0x005d2404 | Unwind@005d2404 | 165 | Cleanup for 2580-byte allocation |
| 0x005d241d | Unwind@005d241d | 171 | Cleanup for 1148-byte allocation |
| 0x005d2440 | Unwind@005d2440 | 310 | Cleanup for SetViewpoint allocation |

## Key Observations

- **CVar System** - Uses FUN_0042b040 to register console variables (Quake-style)
- **Hit Effect Colors** - Configurable RGB factors at offsets 0x48c, 0x490, 0x494
- **Large subsystems** - Allocates 15KB+ for rendering subsystem at offset 0x14
- **CEngine size** - At least 1212 bytes (0x4bc) based on member offsets
- **Render pipeline linkage** - `CGame__Render` now source-aligns to `CDXEngine__PreRender -> CDXEngine__Render -> CDXEngine__PostRender`
- **Viewpoint API parity** - `CEngine__SetNumViewpoints` and `CEngine__SetViewpoint` now match source naming/behavior (`engine.cpp`).
- **Landscape update bridge** - `CGame__MainLoop` viewpoint loop now resolves to `CEngine__UpdatePos(GetCamera(i))`.

## Console Variables

| CVar | Description | Offset |
|------|-------------|--------|
| cg_hiteffectfactorr | Red factor for hit effect | 0x48c |
| cg_hiteffectfactorg | Green factor for hit effect | 0x490 |
| cg_hiteffectfactorb | Blue factor for hit effect | 0x494 |
| cg_renderlandscape | Should landscape be rendered | - |
| cg_drawpolybuckets | Should polybucket volumes be rendered | - |

## Init Allocations

| Line | Size | Offset | Purpose |
|------|------|--------|---------|
| 135 | 56 bytes | +0x470 | First subsystem |
| 139 | 536 bytes | +0x49c | Array of 7 items (76 bytes each) |
| 143 | 15036 bytes | +0x14 | Large rendering subsystem |
| 147 | 64 bytes | +0x10 | Subsystem |
| 165 | 2580 bytes | +0x498 | Subsystem |
| 171 | 1148 bytes | +0x18 | Subsystem |

## Related Files

- Camera.cpp - CCamera used by CEngine
- BattleEngine.cpp - Game logic engine

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
