# FEPMain.cpp Functions

> Source File: FEPMain.cpp | Binary: BEA.exe
> Debug Path String: 0x00629414 (`C:\dev\ONSLAUGHT2\FEPMain.cpp`)
> RTTI Type Name: 0x00629d80 (`.?AVCFEPMain@@`)

## Overview

CFEPMain is the **Frontend Page - Main Menu** class. It handles the main menu navigation, including options for New Game, Continue, Load Game, Options, Multiplayer, Goodies, and Exit.

The class inherits from a base FrontEndPage class and implements virtual methods for menu state management.

## CFEPMain Dispatch/Vtable Layout

The frontend page dispatch block for CFEPMain is anchored at `0x005dbaf0`.

### Page-notification dispatch (0x005dbaf0)

| Offset | Address | Name | Purpose |
|--------|---------|------|---------|
| +0x00 | 0x00462640 | CFEPMain__Process | Per-frame process/update entry |
| +0x04 | 0x00462250 | CFEPMain__ButtonPressed | Button input handler |
| +0x08 | 0x00462b70 | CFEPMain__RenderPreCommon | Pre-render transition/setup helper |
| +0x0C | 0x00462d40 | CFEPMain__Render | Main render path |
| +0x10 | 0x004644d0 | CFEPMain__TransitionNotification | Page transition notification hook |

### CFEPMain object-vtable slice (0x005dbb00)

| Offset | Address | Name | Purpose |
|--------|---------|------|---------|
| +0x00 | 0x00464520 | CFEPMain__Init | Initialize menu state (sets offsets +14, +18 to 0) |
| +0x04 | 0x00459990 | (inherited) | Base class method |
| +0x08 | 0x004621e0 | CFEPMain__GetActionCount | Returns action count (switch on input) |
| +0x0C | 0x004621d0 | CFEPMain__GetMenuType | Returns 7 (menu type identifier) |
| +0x10 | 0x004623e0 | **CFEPMain__DoAction** | Main action handler |
| +0x14 | 0x00462c90 | CFEPMain__Update | Update/render method (partially recovered region) |
| +0x18 | 0x00613d60 | (inherited) | Base class method |

`0x005dbb1c -> 0x00466140` is now tracked as `CGenericCamera__GetPos` from the adjacent camera vtable block, not CFEPMain cleanup.

## Functions

| Address | Name | Status | Size | Purpose |
|---------|------|--------|------|---------|
| 0x00462640 | CFEPMain__Process | DEFINED | Large | Main menu process loop; includes save/defaultoptions write chain under transition state |
| 0x00462250 | CFEPMain__ButtonPressed | DEFINED | ~350 bytes | Button dispatcher (`0x2a/0x2b/0x2c/0x36/0x37`) for menu selection + language cycling |
| 0x00462b70 | CFEPMain__RenderPreCommon | DEFINED | ~280 bytes | Transition alpha/scale prepass helper used before main render |
| 0x00462d40 | CFEPMain__Render | DEFINED | Large | Main menu render path (surfaces/text/layout, transition-weighted draw behavior) |
| 0x004644d0 | CFEPMain__TransitionNotification | DEFINED | ~70 bytes | Transition-state reset/sync helper (seeds timers + career-in-progress state mirror) |
| 0x004621d0 | CFEPMain__GetMenuType | DEFINED | ~6 bytes | Returns constant 7 (menu type) |
| 0x004621e0 | CFEPMain__GetActionCount | DEFINED | ~24 bytes | Returns action count based on state |
| 0x004623e0 | **CFEPMain__DoAction** | **DEFINED** | ~600 bytes | Menu action switch handler |
| 0x00462c90 | CFEPMain__Update | DEFINED | Unknown | Update/render method (vtable entry; contains jump tables and debug asserts in nearby partially recovered region) |
| 0x00464520 | CFEPMain__Init | DEFINED | ~12 bytes | Initialize member variables |

## Debug Path Reference

**Single xref found at 0x00462879** (inside the partially recovered region associated with the CFEPMain update/render path)

The assertion/debug code pushes:
- Line number: 0x61 (97)
- File path: 0x00629414 ("C:\dev\ONSLAUGHT2\FEPMain.cpp")

This is within the large process loop now recovered as `CFEPMain__Process` at `0x00462640`.

## CFEPMain__Process Analysis (0x00462640)

Recovered via manual function-object creation (`F`) + serialized rename/signature read-back.

Behavior highlights:
- Signature: `void CFEPMain__Process(void * this, int state)` (`__thiscall`)
- Handles per-frame main-menu process flow and state-gated updates (`state == 0` path does active work).
- Contains the previously-orphan save/defaultoptions call pair:
  - `CCareer__Save(&CAREER, buf)` at callsite `0x00462893`
  - `CFEPOptions__WriteDefaultOptionsFile(buf, size)` at callsite `0x004628df`
- In the same branch, conditionally writes selected slot via `PCPlatform__WriteSaveFile(...)`.

## CFEPMain__DoAction Analysis (0x004623e0)

This is a thiscall method that switches on `this->state` (offset +8) to handle menu actions:

```cpp
switch (this->state) {
    case 0: // New Game
        if (!DAT_00662aa8) {  // No memory card dialog pending
            CCareer__Blank(&g_Career);
            CFEPOptions__EnumerateSaveFiles();
            // Set up new game state...
        }
        break;
    case 1: // Continue (goto page 7)
        CFrontEnd__SetPage(&DAT_0089d758, 7, 0x46);
        break;
    case 2: // Load Game
        // ...
        break;
    case 3: // Options (goto page 0x10)
        CFrontEnd__SetPage(&DAT_0089d758, 0x10, 0x46);
        break;
    case 4: // Multiplayer (goto page 8)
        CFrontEnd__SetPage(&DAT_0089d758, 8, 0x46);
        break;
    case 5: // Goodies (goto page 0x11)
        CFrontEnd__SetPage(&DAT_0089d758, 0x11, 0x46);
        break;
    case 6: // Credits/About
        // Show fireworks effect...
        break;
    case 8: // Return from sub-menu
        // Restore state...
        break;
}
```

### Menu Page Constants (from analysis)
- 0x07 = Save/Load selection
- 0x08 = Multiplayer menu
- 0x0B = Continue game
- 0x10 = Options menu
- 0x11 = Goodies gallery
- 0x46 = Page transition time constant used by Main menu actions (70)

## Global Variables

| Address | Type | Purpose |
|---------|------|---------|
| 0x00660620 | CCareer | Global career data structure |
| 0x00662aa8 | DWORD | Memory card dialog pending flag |
| 0x008a9580 | DWORD | Career in progress flag |
| 0x008a9584 | DWORD | Sub-menu return state |
| 0x008a968c | DWORD | Current page ID |
| 0x008a9690 | DWORD | Previous/return page ID |
| 0x0089d94c | DWORD | Some counter (set to 100 on new game) |

## Key Observations

1. **Large CFEPMain Region Is Recovering:** `CFEPMain__Process` (0x00462640) is now a recovered function object, and key save/defaultoptions call chains inside this region are now owned by a named function.

2. **Single Debug Reference:** Only one function in FEPMain.cpp contains an assertion with the debug path, at address 0x00462879 (line 97).

3. **Menu Navigation:** The frontend uses page numbers and per-page notifications. `CFrontEnd__SetPage(&DAT_0089d758, page, time)` is the page transition helper (immediate when `time==0`, otherwise timed).

4. **Memory Card Handling:** The code checks `DAT_00662aa8` before certain operations, suggesting console memory card dialog handling that was kept in the PC port.

5. **Vtable Structure:** CFEPMain inherits from a base FrontEndPage class, with virtual methods for initialization, action handling, update, and cleanup.

## Related Source Files

Based on call patterns, CFEPMain.cpp interacts with:
- Career.cpp (CCareer__Blank)
- FEPOptions.cpp (CFEPOptions__EnumerateSaveFiles)
- FrontEnd.cpp (navigation functions)

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*Function CFEPMain__DoAction renamed in Ghidra*
