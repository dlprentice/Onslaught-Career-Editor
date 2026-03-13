# FEPScreenPos.cpp - Function Analysis

## Overview

**Class:** `CFEPScreenPos` (RTTI string `.?AVCFEPScreenPos@@` at `0x00629db8`)

This FrontEnd page appears to handle screen-position calibration behavior.
Source file path/debug string has not yet been recovered from the current binary string set.

## Confirmed Mapping

| Address | Function | Role | Notes |
|---------|----------|------|-------|
| `0x0051f9f0` | `CFEPScreenPos__Init` | vtable slot 0 | Zeroes two calibration state fields (`this+0x04/+0x08`) and returns `1` |
| `0x0051fa00` | `CFEPScreenPos__ButtonPressed` | vtable slot 3 | Handles calibration input (`0x2a/0x2b/0x36/0x37` adjust ranges, `0x2c/0x2e` page flow + restore path) and writes top-byte metadata via `CCareer__SetKillCounterTopByte_*` helpers |
| `0x0051fb60` | `CFEPScreenPos__RenderPreCommon` | vtable slot 4 | Pre-common transition draw helper (calls `FUN_004679e0` with fixed color `0x3fffffff`) |
| `0x0051fb90` | `CFEPScreenPos__Render` | vtable slot 5 | Main calibration render path; draws "Adjust Screen Position" text/overlays and applies transition alpha |
| `0x0051fd50` | `CFEPScreenPos__TransitionNotification` | vtable slot 6 | Seeds a `now+2.0` timer, syncs two page fields (`+0x04/+0x08`) from backing values (`+0x10/+0x14`), and calls `CFEPOptions__GetKillCounterTopBytes_23F4_23F8` |

## Vtable Analysis (0x005db858)

RTTI CompleteObjectLocator:
- `0x005db854` -> `0x00613d10`
- `0x00613d10 + 0x0c` -> type descriptor `0x00629db0` (name string at `0x00629db8`)

Current slot map:

| Slot | Address | Status | Notes |
|------|---------|--------|-------|
| 0 | `0x0051f9f0` | mapped | `CFEPScreenPos__Init` |
| 1 | `0x0040c640` | mapped | `DebugTrace` placeholder in this class vtable |
| 2 | `0x00452b60` | mapped | inherited process no-op helper |
| 3 | `0x0051fa00` | mapped | `CFEPScreenPos__ButtonPressed` |
| 4 | `0x0051fb60` | mapped | `CFEPScreenPos__RenderPreCommon` |
| 5 | `0x0051fb90` | mapped | `CFEPScreenPos__Render` |
| 6 | `0x0051fd50` | mapped | `CFEPScreenPos__TransitionNotification` |
| 7 | `0x004014c0` | mapped | inherited active-notification no-op |
| 8 | `0x00459990` | mapped | inherited deactive no-op |
