# Cutscene.cpp Functions

> Source File: Cutscene.cpp | Binary: BEA.exe
> Debug Path: 0x0062811c

## Overview

Cutscene playback system. CCutscene handles loading, playing, and managing in-game cutscenes with animation slots and audio synchronization.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0043ed80 | CCutscene__Load (TODO) | Load cutscene from .cut file | ~600 bytes |
| 0x0043f210 | CCutscene__AddAnimation (TODO) | Add animation to cutscene | ~200 bytes |
| 0x0043f690 | CCutscene__Update (TODO) | Frame-by-frame playback | ~800 bytes |
| 0x0043f510 | CCutscene__InitAnimations | Initialize animation slots | ~300 bytes |

## Additional Functions (No debug path ref)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0043f340 | CCutscene__Start | Start cutscene playback |
| 0x0043f420 | CCutscene__Stop | Stop and cleanup cutscene |
| 0x0043fa70 | CCutscene__PrepareAnimations | Calculate durations |
| 0x0043fcd0 | CCutscene__ForceEnd | Force-end via global pointer |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d1ff0 | Unwind@005d1ff0 | 203 | Cleanup for Load 16-byte allocation |
| 0x005d2020 | Unwind@005d2020 | 549 | Cleanup for Update 156-byte allocation |

## Key Observations

- **File format** - Loads from `data\cutscenes\%s.cut`
- **Animation slots** - 32 animation slot pointers at offset 0x7c
- **Frame-based** - Playback uses frame counter with audio sync
- **Global pointer** - Current cutscene stored at DAT_0066ea20
- **VTable at 0x005dae00** - CCutscene virtual function table

## CCutscene Class Structure (Partial)

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x000 | 4 | vtable | CCutscene vtable |
| 0x01c | 16 | cameraData | Camera position/rotation |
| 0x07c | 128 | animSlots[32] | Animation slot pointers |
| 0x5a8 | 256 | cutsceneName | Cutscene name string |
| 0x6b8 | 1 | isPlaying | Playing flag |
| 0x6bc | 128 | animCounts[32] | Animation count per slot |
| 0x840 | 1 | cameraRestoreFlag | Restore camera on end |
| 0x841 | 1 | dirtyFlag | Needs re-initialization |
| 0x844 | 4 | frameStart | Start frame |
| 0x848 | 4 | totalFrames | Total frame count |

## CCutsceneAnim Structure

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x008 | 256 | animName | Animation name |
| 0x108 | 32 | meshName | Mesh name |
| 0x12d | 256 | audioName | Audio file name |
| 0x234 | 4 | duration | Duration in frames |
| 0x23c | 4 | startFrame | Start frame in cutscene |
| 0x248 | 4 | next | Next in linked list |

## Related Files

- RTCutscene.cpp - Real-time cutscene variant
- Music.cpp - Audio playback

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
