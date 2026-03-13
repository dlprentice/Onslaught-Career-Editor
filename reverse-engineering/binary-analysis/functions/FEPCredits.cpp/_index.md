# FEPCredits.cpp - Function Analysis

## Overview

**Class:** `CFEPCredits` (RTTI type string `.?AVCFEPCredits@@` at `0x00629c78`)

This page owns credits-screen flow in the frontend vtable cluster rooted at `0x005db880`.
Source file content is not present in `references/Onslaught/`, so this mapping is retail-binary-first.

## Confirmed Mapping

| Address | Function | Role | Notes |
|---------|----------|------|-------|
| `0x0051a7f0` | `CFEPCredits__ButtonPressed` | vtable slot 3 | Handles button `0x2e` (back/exit): plays FE sound, returns to page `0x11` (time `0x1e`), resumes FE music |
| `0x0051a820` | `CFEPCredits__Process` | vtable slot 2 | Per-frame page process: watches completion flag at `this+0x08`, performs page/music return when set, and draws prompt code `0x2e` |
| `0x0051a880` | `CFEPCredits__RenderPreCommon` | vtable slot 4 | At `transition == 1.0`, issues FE pre-common pass (`FUN_004679e0(1.0, 0x3fffffff, dest)`) |
| `0x0051a8b0` | `CFEPCredits__Render` | vtable slot 5 | Computes fade alpha from `transition`, calls `CCredits__RenderCredits`, sets completion flag at `this+0x08` when done |
| `0x0051a970` | `CFEPCredits__TransitionNotification` | vtable slot 6 | Sets transition timer (`now + 2.0`), starts credits music (`CMusic__PlayTrackByType(1,1)`), clears local state flag at `this+0x08` |

## Vtable Analysis (0x005db880)

RTTI CompleteObjectLocator:
- `0x005db87c` -> `0x00613ac8`
- `0x00613ac8 + 0x0c` -> type descriptor `0x00629c70` (name string at `0x00629c78`)

Current slot map:

| Slot | Address | Status | Notes |
|------|---------|--------|-------|
| 0 | `0x004fdc10` | mapped | inherited/common FE init-style helper |
| 1 | `0x0040c640` | mapped | `DebugTrace` placeholder |
| 2 | `0x0051a820` | mapped | `CFEPCredits__Process` |
| 3 | `0x0051a7f0` | mapped | `CFEPCredits__ButtonPressed` |
| 4 | `0x0051a880` | mapped | `CFEPCredits__RenderPreCommon` |
| 5 | `0x0051a8b0` | mapped | `CFEPCredits__Render` |
| 6 | `0x0051a970` | mapped | `CFEPCredits__TransitionNotification` |
| 7 | `0x004014c0` | mapped | inherited active-notification no-op |
| 8 | `0x00459990` | mapped | inherited deactive-notification no-op |

## Notes

- `0x0051a030` (`CCredits__RenderCredits`) is called from this vtable region (`0x0051a92b`) and from `CGame__RollCredits` (`0x004726b0`), tying page render behavior to the shared credits renderer.
- Calling-convention nuance in this runtime: slot-3/slot-4 read back as `__stdcall` signatures (`ButtonPressed(int button,float val)`, `RenderPreCommon(float transition,int dest)`) even though they are vtable targets; `this` is effectively hidden/unused in those bodies.
- Direct-HTTP mutation quirk observed in this wave: PATCH comment calls for `0x0051a7f0/0x0051a880/0x0051a8b0` returned `COMMENT_FAILED`, but immediate decompile read-back showed comments present. For this runtime, address-level read-back remains source of truth.
