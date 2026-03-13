# MenuItem.cpp Functions

> Source File: MenuItem.cpp | Binary: BEA.exe
> Debug Path: 0x0062f7d8 (`C:\dev\ONSLAUGHT2\MenuItem.cpp`)

## Overview

Menu item UI component classes for the game's front-end menu system. This file implements a class hierarchy for interactive menu elements:

- **CMenuItem** - Base class for simple text/icon menu items
- **CMenuItemDropdown** - Dropdown/combo box menu items with expandable lists
- **CMenuItemSlider** - Slider controls for value selection
- **CMenuItemRange** - Menu containers that hold multiple items with navigation
- **CMenuItemRangeVariant** - Variant of CMenuItemRange with different vtable

## Class Hierarchy

```
CMenuItem (vtable: 0x005dc520)
  +-- CMenuItemDropdown (vtable: 0x005dc578, 0x005dc5c4)
  +-- CMenuItemSlider (vtable: 0x005dc610)
  +-- CMenuItemRange (vtable: 0x005dc650)
       +-- CMenuItemRangeVariant (vtable: 0x005dc664)
```

## Functions

### CMenuItem (Base Class)

| Address | Name | Purpose | Notes |
|---------|------|---------|-------|
| 0x004a3100 | CMenuItem__IsMouseInBounds | Check if mouse is within item bounds | Wrapper for `CFrontEnd__GetCursorStateInRect` |
| 0x004a3120 | CMenuItem__IsMouseClicked | Check if mouse clicked on item | Wrapper for `CFrontEnd__GetClickStateInRect` |
| 0x004a3140 | CMenuItem__Clone | Clone helper (compact object) | Allocates 0x1c bytes and copies core display fields |
| 0x004a3260 | CMenuItem__RenderCentered | Render item centered at position | Calls vtable+8 then Render |
| 0x004a3290 | CMenuItem__RenderWithColor | Render item with custom color | Calls vtable+8 then Render |
| 0x004a32c0 | CMenuItem__Render | Main render function | Handles icon+text, color states |
| 0x004a37c0 | CMenuItem__RenderValueBar | Render segmented value bar + mouse hotspots | Uses selected/current values and emits left/right button events |
| 0x004a3450 | CMenuItem__Clone | Clone/copy constructor (full object) | Allocates 0x38 bytes and initializes extra reader/resource fields |
| 0x004a3510 | CMenuItem__Init | Initialize menu item | Sets vtable, default color 0xffd6d6d6 |
| 0x004a3610 | CMenuItem__ScalarDestructor | Scalar deleting destructor | Calls Destructor, optionally frees |
| 0x004a3630 | CMenuItem__InitWithIcon | Initialize with icon parameter | Icon stored at offset 0x18 |
| 0x004a3730 | CMenuItem__Destructor | Base destructor | Cleans up resources at [7], [8], [0xd] |
| 0x004a43a0 | CMenuItem__ButtonPressed | Default value-item button handler | Handles confirm/left/right and optional owner notification |
| 0x004a4220 | Localization__GetYesNoString | Return localized Yes/No string | Wrapper for `Localization__GetStringById(5/6)` |
| 0x004a4450 | CMenuItem__GetWidth | Compute item width | Returns text extent + fixed padding |
| 0x004a44c0 | CMenuItem__SetUserData | Set user data pointer | Stores at offset 0x20 |

### CMenuItemDropdown

| Address | Name | Purpose | Notes |
|---------|------|---------|-------|
| 0x004a3b10 | CMenuItemDropdown__Init | Initialize dropdown | vtable 0x005dc578 |
| 0x004a3b50 | CMenuItemDropdown__UpdateSelection | Update current selection | Syncs [7] and [8] via vtable+0x3c |
| 0x004a3b60 | CMenuItemDropdown__InitVariant | Alternate init | vtable 0x005dc5c4 |
| 0x004a3ba0 | CMenuItemDropdown__ClearPending | Clear pending selection | Sets DAT_0070486c = 0 |
| 0x004a3be0 | CMenuItemDropdown__RenderOrQueueDeferred | Deferred popup render helper | Queues coordinates/state when interactive, otherwise performs render |
| 0x004a3bb0 | CMenuItemDropdown__ProcessPending | Process pending selection | Calls Render if pending flag set |
| 0x004a3c30 | CMenuItemDropdown__Render | Render dropdown | Complex: handles expanded/collapsed states, mouse hover, selection animation |
| 0x004a40e0 | CMenuItemDropdown__IsExpanded | Return expanded/edit flag | Reads dropdown state byte at +0x24 |
| 0x004a4110 | CMenuItemDropdown__ButtonPressed | Button input handler | Handles up/down/select/cancel and commit behavior |
| 0x004a42f0 | CMenuItemDropdown__HasPendingSelectionChange | Detect pending change | True when expanded + current selection differs from committed selection |
| 0x004a40f0 | CMenuItemDropdown__CommitSelection | Commit hover to selection | Calls vtable+0x38 callback |

### CMenuItemSlider

| Address | Name | Purpose | Notes |
|---------|------|---------|-------|
| 0x004a4250 | CMenuItemSlider__Init | Initialize slider | vtable 0x005dc610, default ID=3 |
| 0x004a4290 | CMenuItemSlider__ButtonPressed | Slider button handler | On select, iterates bound item set and fires per-item callback |
| 0x004a4310 | CMenuItemSlider__Render | Slider render override | Pulsed highlight + text render path |

### CMenuItemRange (Container)

| Address | Name | Purpose | Notes |
|---------|------|---------|-------|
| 0x004a45c0 | CMenuItemRange__Init | Initialize range container | vtable 0x005dc650 |
| 0x004a4610 | CMenuItemRange__ScalarDestructor | Scalar deleting destructor | |
| 0x004a4630 | CMenuItemRange__ResetIterator | Reset item iterator | Iterates calling vtable+0x30 |
| 0x004a4670 | CMenuItemRange__AddItem | Add item to container | Wrapper for CSPtrSet__AddToTail |
| 0x004a4680 | CMenuItemRange__Destructor | Destructor | Destroys all child items |
| 0x004a4730 | CMenuItemRange__LoadTexture | Load blank texture | Loads "FrontEnd_v2/FE_Blank.tga" |
| 0x004a4790 | CMenuItemRange__SelectNext | Select next item | Wraps around, skips disabled |
| 0x004a4810 | CMenuItemRange__Render | Main render function | ~1216 bytes, complex layout logic |
| 0x004a4cd0 | CMenuItemRange__ProcessInput | Process input on selected | Checks vtable+0x20, calls vtable+4 |
| 0x004a4d20 | CMenuItemRange__HandleKeyPress | Handle up/down keys | 0x2a=up, 0x2b=down |
| 0x004a4dd0 | CMenuItemRange__SetItemEnabled | Enable/disable item by ID | Iterates items, sets offset 0x10 |

### CMenuItemRangeVariant

| Address | Name | Purpose | Notes |
|---------|------|---------|-------|
| 0x004a4e10 | CMenuItemRangeVariant__Init | Initialize variant | vtable 0x005dc664 |
| 0x004a4e60 | CMenuItemRangeVariant__ScalarDestructor | Scalar deleting destructor | |
| 0x004a4e80 | CMenuItemRangeVariant__Destructor | Destructor | Same logic as Range |

## CMenuItem Structure (0x38 bytes)

Based on decompilation analysis:

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x00 | 4 | vtable | Pointer to virtual function table |
| 0x04 | 4 | mTextID | Text/string identifier |
| 0x08 | 4 | mParam1 | Constructor param 1 |
| 0x0C | 4 | mIcon | Icon resource handle |
| 0x10 | 4 | mParam3 | Constructor param 3 |
| 0x14 | 4 | mParam4 | Constructor param 4 / color |
| 0x18 | 4 | mIconAlt | Alternative icon |
| 0x1C | 4 | mField7 | Resource handle (cleaned in dtor) |
| 0x20 | 4 | mField8 | Resource handle (cleaned in dtor) |
| 0x24 | 4 | mValue | Current value |
| 0x28 | 4 | mValueAlt | Alternative value |
| 0x2C | 4 | mMaxValue | Maximum value |
| 0x30 | 1 | mFlags | Control flags |
| 0x34 | 4 | mOwner | Owner pointer (with monitor) |

## Key Observations

1. **Color Constants**:
   - Default color: `0xffd6d6d6` (light gray)
   - Disabled color: `0xff505050` (dark gray)
   - Selected color: `0xffffcc00` (yellow)
   - Hover color: `0xffffffff` (white)
   - Dropdown item: `0xff404040` (dark)

2. **Animation**: Dropdown uses cosine-based pulsing animation for selection highlight (fcos with 2*PI multiplier)

3. **Mouse Handling**: Uses `CFrontEnd__GetCursorStateInRect` (bounds check) and `CFrontEnd__GetClickStateInRect` (click detection)

4. **Yes/No Strings**: `Localization__GetYesNoString(value)` returns `Localization__GetStringById(5/6)`

5. **Texture Loading**: Uses "FrontEnd_v2/FE_Blank.tga" as background texture

6. **Screen Bounds**: Hard-coded 480.0 height limit in CMenuItemRange__Render

7. **Global State**:
   - `DAT_0070486c` - Pending dropdown selection flag
   - `DAT_00704870` - Pending Y coordinate
   - `DAT_00704874` - Pending X coordinate
   - `DAT_00704a88` - Input processed flag
   - `DAT_0082b4e8` - UI mode flag
   - `DAT_0082b490` - Cached texture handle

8. **Base vfunc semantics (promoted 2026-02-25)**:
   - `0x00453a60` (`IsEnabled`) returns field `this+0x10`; `CMenuItemRange__SetItemEnabled` writes this field.
   - `0x00453a70` (`GetRowHeight`) returns `0x14` or `0x28` based on secondary text-id presence at `this+0x0c`.
   - `0x00453a80` (`DefaultFalseFlag`) is a shared default-false bool stub used by base slots `0x20/0x24/0x28`.

## VTable Layout (CMenuItem at 0x005dc520)

| Offset | Address | Method |
|--------|---------|--------|
| 0x00 | 0x004a3610 | ScalarDestructor |
| 0x04 | 0x004a43a0 | ButtonPressed |
| 0x08 | 0x004a3190 | GetText |
| 0x0C | 0x00453a60 | IsEnabled |
| 0x10 | 0x004a37c0 | RenderValueBar |
| 0x14 | 0x004a4450 | GetWidth |
| 0x18 | 0x00453a70 | GetRowHeight |
| 0x1C | 0x004a3450 | Clone |
| 0x20 | 0x00453a80 | DefaultFalseFlag (also reused at 0x24/0x28 in base) |
| ... | ... | ... |

### Recovered Sibling VTable Slots (2026-02-25)

Headless recovery pass created previously-missing function objects and resolved these slots:

| Address | Symbol | Signature |
|---------|--------|-----------|
| 0x00453a50 | CMenuItem__ButtonPressed_NoOp | `void __thiscall CMenuItem__ButtonPressed_NoOp(void * this, int from_controller, int button)` |
| 0x00453a60 | CMenuItem__IsEnabled | `int __thiscall CMenuItem__IsEnabled(void * this)` |
| 0x00453a70 | CMenuItem__GetRowHeight | `int __thiscall CMenuItem__GetRowHeight(void * this)` |
| 0x00453a80 | CMenuItem__DefaultFalseFlag | `byte __thiscall CMenuItem__DefaultFalseFlag(void * this)` |
| 0x00453a90 | CMenuItem__scalar_deleting_dtor | `void * __thiscall CMenuItem__scalar_deleting_dtor(void * this, byte flags)` |

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*Total: 34 functions identified across 5 classes*
