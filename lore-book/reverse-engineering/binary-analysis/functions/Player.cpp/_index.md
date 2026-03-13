# Player.cpp Function Mappings

> Functions from `references/Onslaught/Player.cpp` mapped to `BEA.exe`.

## Overview
- **Functions Mapped:** 9
- **Status:** ACTIVE (camera/view control tranche corrected in wave24)
- **Class:** `CPlayer`

## Function List

| Address | Name | Status | Link |
|---------|------|--------|------|
| 0x004d28a0 | CPlayer__Init | NAMED | (doc pending) |
| 0x004d28c0 | CPlayer__GotoFPView | NAMED | (doc pending) |
| 0x004d29c0 | CPlayer__Goto3rdPersonView | NAMED | (doc pending) |
| 0x004d2a50 | CPlayer__GotoControlView | NAMED | (doc pending) |
| 0x004d2a70 | CPlayer__GetCurrentViewPoint | NAMED | (doc pending) |
| 0x004d2ae0 | CPlayer__GetCurrentViewOrientation | NAMED | (doc pending) |
| 0x004d2b40 | CPlayer__GetOldCurrentViewPoint | NAMED | (doc pending) |
| 0x004d2bb0 | CPlayer__GetOldCurrentViewOrientation | NAMED | (doc pending) |
| 0x004d2c10 | CPlayer__GotoPanView | NAMED | [View](CPlayer__GotoPanView.md) |

## Notes
- Wave24 corrected prior mislabels where `0x004d28c0`/`0x004d29c0` were incorrectly tracked as ctor/dtor.
- Camera-mode selectors and current/old view snapshot accessors are now explicitly separated in symbol names.

## Related
- Source: `references/Onslaught/Player.cpp`
- Header: `references/Onslaught/Player.h`
- Parent: [../_index.md](../_index.md)
