# FEPLevelSelect.cpp - Function Analysis

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

**Class:** `CFEPLevelSelect` (RTTI string `.?AVCFEPLevelSelect@@` at `0x006293a0`)
**Primary Vtable:** `0x005db584` (COL pointer at `0x005db580` -> `0x006135f8`)

This front-end page drives the world/mission level-select wheel. It owns the current selected row/column, handles unlock-gated navigation, and renders world nodes/grade overlays.

## Wave801 Frontend/Render Helper Read-Back

Wave801 static read-back (`frontend-render-helpers-wave801`, `wave801-readback-verified`) saved a current comment/tag on `0x0045d730 CFEPLevelSelect__UpdateMouseEdgeSlide`. The body is called by level-select processing, gates on `CFrontEnd__IsMouseInputReady`, reads cursor globals `DAT_0089bda8/DAT_0089bda4`, applies a cubic delta scale, and clamps the target value. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-073450_post_wave801_frontend_render_helpers_verified`.

This remains static retail Ghidra evidence only. Exact source-body identity, runtime mouse-edge slide behavior, BEA patching, and rebuild parity remain deferred.

## Identified Functions

| Address | Name | Role | Notes |
|---------|------|------|-------|
| `0x00460140` | `CFEPLevelSelect__ctor` | ctor | Initializes page state and vtable wiring |
| `0x00460310` | `CFEPLevelSelect__SyncSelectionFromCurrentWorldAndResetTimers` | helper | Syncs row/column from current world id and resets timers |
| `0x004603d0` | `CFEPLevelSelect__Init` | vtable | Rebuilds selection from current world id and seeds wheel/timing state |
| `0x00460490` | `CFEPLevelSelect__SyncSelectionFromCurrentWorld` | vtable/helper | Sync helper for current world id |
| `0x004604f0` | `CFEPLevelSelect__MarkSelectionPulseByState` | vtable/helper | Pulse-state helper used by transition flow |
| `0x00460520` | `CFEPLevelSelect__BeginSelectionPulseByState` | vtable/helper | Starts selection pulse for a given state |
| `0x00460590` | `CFEPLevelSelect__Process` | vtable | Per-frame update for selection/pulse/wheel animation |
| `0x004606b0` | `CFEPLevelSelect__ButtonPressed` | vtable | Input handler (up/down/confirm/back + row shifts), unlock-gated |
| `0x00460a40` | `CFEPLevelSelect__SelectLatestUnlockedWorld` | helper | Finds most recent unlocked world, updates selection/timers |
| `0x00460b40` | `CFEPLevelSelect__Render` | vtable | Draws world nodes/rings/grade overlays and hover selection |
| `0x0045d730` | `CFEPLevelSelect__UpdateMouseEdgeSlide` | helper | Mouse-edge cubic slide/clamp helper used by `Process` |
| `0x00459990` | `CFEPLevelSelect__NoOp` | inherited vtable slot | Shared no-op page helper |

## Vtable Analysis (0x005db584)

Primary vtable entries:

| Slot | Address | Function | Notes |
|------|---------|----------|-------|
| 0 | `0x004603d0` | `CFEPLevelSelect__Init` | Returns `bool` success |
| 1 | `0x00460490` | `CFEPLevelSelect__SyncSelectionFromCurrentWorld` | Selection sync helper |
| 2 | `0x00460590` | `CFEPLevelSelect__Process` | Per-frame page update |
| 3 | `0x004606b0` | `CFEPLevelSelect__ButtonPressed` | Input dispatch |
| 4 | `0x0051ae50` | (inherited pre-common render) | Shared FEP pre-common render helper |
| 5 | `0x00460b40` | `CFEPLevelSelect__Render` | Main render path |
| 6 | `0x00460520` | `CFEPLevelSelect__BeginSelectionPulseByState` | Transition helper |
| 7 | `0x004604f0` | `CFEPLevelSelect__MarkSelectionPulseByState` | Transition helper |
| 8 | `0x00459990` | `CFEPLevelSelect__NoOp` | No-op helper |

## Career Integration Notes

- `CFEPLevelSelect__SelectLatestUnlockedWorld` (`0x00460a40`) is called during load flow and uses `Career_IsWorldUnlocked` to clamp selection to accessible content.
- Both `ButtonPressed` and `Render` consult unlock state, so cursor movement and visual emphasis are consistent with career progression.
- `CFEPLevelSelect__Process` calls `CFEPLevelSelect__UpdateMouseEdgeSlide(state, &this->field_3460, 1100.0f)` to apply mouse-edge cubic slide/clamp behavior in the level-select wheel.

## Recovery Notes

- 2026-02-23: Function objects for the LevelSelect wave were confirmed present after manual CodeBrowser `F` creation, then renamed/signed/commented via serialized MCP with read-back verification.
