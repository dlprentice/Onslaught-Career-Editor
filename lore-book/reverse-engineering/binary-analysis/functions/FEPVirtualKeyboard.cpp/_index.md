# FEPVirtualKeyboard.cpp - Function Analysis

## Overview

**Class:** `CFEPVirtualKeyboard` (RTTI type descriptor string `.?AVCFEPVirtualKeyboard@@` at `0x00629d18`)

This FrontEnd page handles virtual-keyboard save-name entry behavior used by save/load flows.
The source file is not present in `references/Onslaught/`, so mapping here is retail-binary-first.

## Identified Functions

| Address | Name | Role | Notes |
|---------|------|------|-------|
| `0x0051ff90` | `CFEPVirtualKeyboard__Init` | vtable | Initializes keyboard page state fields and returns `1` |
| `0x0051ffd0` | `CFEPVirtualKeyboard__Shutdown` | vtable | Page shutdown helper; hides keyboard context when active |
| `0x005202d0` | `CFEPVirtualKeyboard__Process` | vtable | Per-frame process; refreshes save list by state and handles context setup |
| `0x00520370` | `CFEPVirtualKeyboard__ButtonPressed` | vtable | Input handler for nav/select/back and character cycling |
| `0x00521100` | `CFEPVirtualKeyboard__Render` | vtable | Keyboard UI render path using transition alpha |
| `0x00520130` | `CFEPVirtualKeyboard__TransitionNotification` | vtable | Transition hook; resets cursor/selection and save-name defaults from prior page |

## Vtable Analysis (0x005db830)

RTTI CompleteObjectLocator:
- `0x005db82c` -> `0x00613bb8`
- `0x00613bb8 + 0x0c` -> type descriptor `0x00629d10` (name string at `0x00629d18`)

Primary vtable at `0x005db830`:

| Slot | Address | Function | Notes |
|------|---------|----------|-------|
| 0 | `0x0051ff90` | `CFEPVirtualKeyboard__Init` | Returns `1` |
| 1 | `0x0051ffd0` | `CFEPVirtualKeyboard__Shutdown` | Shutdown helper |
| 2 | `0x005202d0` | `CFEPVirtualKeyboard__Process` | Process/state update |
| 3 | `0x00520370` | `CFEPVirtualKeyboard__ButtonPressed` | Button handler |
| 4 | `0x0051ae50` | (shared) `CFEPLanguageTest__RenderPreCommon` | Shared pre-common frontend render helper |
| 5 | `0x00521100` | `CFEPVirtualKeyboard__Render` | Main render |
| 6 | `0x00520130` | `CFEPVirtualKeyboard__TransitionNotification` | Transition hook |
| 7 | `0x004014c0` | (inherited) `CFrontEndPage__ActiveNotification_NoOp` | Active no-op |
| 8 | `0x00459990` | (inherited) `CFrontEndPage__DeActiveNotification` | DeActive no-op |

## Additional Helpers (Wave23)

| Address | Name | Role | Notes |
|---------|------|------|-------|
| `0x00520530` | `CFEPVirtualKeyboard__InitKeyboardLayout` | layout init | Initializes virtual-keyboard key tables (tokens, glyph widths, row descriptors, defaults). |
| `0x00520cc0` | `CFEPVirtualKeyboard__HandleKeyToken` | token handler | Applies control-token and glyph-token input to edit buffer (cursor move, insert/delete, mode toggles, confirm). |
| `0x00520f70` | `CFEPVirtualKeyboard__MoveSelectionToRow` | row-selection helper | Moves to target row while preserving weighted column and skipping empty entries. |

## Notes

- `CFEPVirtualKeyboard__Process` (`0x005202d0`) calls `CFEPDirectory__RefreshSaveFileList` for non-state-3 paths.
- `CFEPVirtualKeyboard__Render` (`0x00521100`) calls shared helper `CFEPDirectory__RenderSaveFileList` (`0x0051ae70`) to draw/poll the save list strip.
- `CFEPVirtualKeyboard__TransitionNotification` (`0x00520130`) triggers save-name reseed/length clamp logic for selected page transitions (`from_page` checks include `0`, `9`, `14`).
- This class was recovered via manual function-object creation (`F`) followed by serialized direct-HTTP rename/signature writes with immediate read-back verification.
