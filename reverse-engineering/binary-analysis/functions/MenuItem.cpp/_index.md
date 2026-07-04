# MenuItem.cpp Functions

> Source File: MenuItem.cpp | Binary: BEA.exe
> Debug Path: 0x0062f7d8 (`[maintainer-local-source-export-root]\MenuItem.cpp`)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

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

## Wave756 MenuItem.cpp Unwind Continuation (2026-05-23)

Wave756 static read-back (`unwind-continuation-wave756`, `wave756-readback-verified`) hardened `0x005d35f0 Unwind@005d35f0` and `0x005d360c Unwind@005d360c` as MenuItem.cpp-adjacent compiler-generated SEH unwind cleanup callbacks. DATA scope-table xrefs `0x0061c344` and `0x0061c34c` point at the bodies; evidence includes MenuItem.cpp debug path `0x0062f7d8`, `OID__FreeObject_Callback(*(EBP-0x10))` with line token `0x80` and allocation/type value `0xad`, and `CMenuItem__RestoreCompactVTable(*(EBP-0x10))`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-112625_post_wave756_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Wave757 MenuItem.cpp Unwind Continuation (2026-05-23)

Wave757 static read-back (`unwind-continuation-wave757`, `wave757-readback-verified`) hardened `0x005d3630 Unwind@005d3630`, `0x005d3660 Unwind@005d3660`, and `0x005d3690 Unwind@005d3690` as MenuItem.cpp-adjacent compiler-generated SEH unwind cleanup callbacks. DATA scope-table xrefs `0x0061c37c`, `0x0061c3b4`, and `0x0061c3ec` point at the bodies; each row calls `CMenuItem__RestoreCompactVTable` on the local menu item pointer. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-120201_post_wave757_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Wave824 MenuItem/PauseMenu Raw Head (2026-05-24)

Wave824 static read-back (`menuitem-pausemenu-raw-head-wave824`, `wave824-readback-verified`) hardened two MenuItem-owned rows in the raw commentless head: `0x004cf050 CMenuItem__Destructor_Thunk` and `0x004d05c0 CMenuItemRange__IsBindingActive`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-190751_post_wave824_menuitem_pausemenu_raw_head_verified`.

| Address | Saved state | Static evidence |
| --- | --- | --- |
| `0x004cf050 CMenuItem__Destructor_Thunk` | `void __thiscall CMenuItem__Destructor_Thunk(void * this)` | Single-instruction jump thunk to `0x004a3730 CMenuItem__Destructor`; xref from `0x004cf030 CMouseSensitivityMenuItem__scalar_deleting_dtor`, which destroys the base menu item before optional free. |
| `0x004d05c0 CMenuItemRange__IsBindingActive` | `int __thiscall CMenuItemRange__IsBindingActive(void * this)` | `CMenuItemRange__Render` calls this predicate while gating mouse hover/click advancement into bound child items; the body returns 1 only when the binding/range context pointer at `this+0x08` exists and byte `context+0x08` is non-zero. |

This is saved static retail Ghidra metadata only. Exact concrete UI/control-binding layouts, exact source-body identity, runtime frontend input/render behavior, BEA patching, and rebuild parity remain deferred.

## Wave962 Game-Menu Options Bridge Review (2026-05-28)

Wave962 (`game-menu-options-bridge-review-wave962`) re-reviewed the MenuItem-owned binding-capacity renderer `0x004d0290 CControllerBackMenuItem__RenderBindingCapacityWarning` together with `0x004d0e40 CGameMenu__InitBase`, `0x004d3020 CEngine__SetOptionValueAndNotifyTarget`, and `0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput`. Fresh instruction evidence preserves the Wave465/Wave824 boundary: `0x004d02a5 PUSH 0xe8`, `0x004d02d7 PUSH 0xe9`, and the later call to `CMenuItem__RenderWithColor` select the warning text/color path, while `0x004d0e49 MOV [EAX], 0x5dc72c`, `0x004d302e MOV [EAX*0x4 + 0x662ab0], EDI`, `0x005dbc2c slot 3`, and `0x005dc72c` tie the reviewed row back to the temporary game-menu/options bridge. No mutation was needed. Wave911 focused re-audit progress after Wave962 is `309/1408 = 21.95%`; static export-contract closure remains `6152/6152 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-132411_post_wave962_game_menu_options_bridge_review_verified`. Runtime pause-menu/controller-binding/options persistence behavior, exact layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave962; game-menu-options-bridge-review-wave962; 0x004d0290 CControllerBackMenuItem__RenderBindingCapacityWarning; 0x004d0e40 CGameMenu__InitBase; 0x004d3020 CEngine__SetOptionValueAndNotifyTarget; 0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput; 0x004d02a5 PUSH 0xe8; 0x004d02d7 PUSH 0xe9; 0x004d0e49 MOV [EAX], 0x5dc72c; 0x004d302e MOV [EAX*0x4 + 0x662ab0], EDI; 0x005dbc2c slot 3; 0x005dc72c; 309/1408 = 21.95%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-132411_post_wave962_game_menu_options_bridge_review_verified; no mutation.

Wave1023 (`frontend-options-pause-menu-review-wave1023`) re-read the compact menu-item helpers `0x004d01c0 CMenuItem__RestoreCompactVTable` and `0x004d0490 CMenuItem__shared_compact_scalar_deleting_dtor` with no mutation. Fresh metadata confirmed the Wave465 bounded evidence: the restore helper writes `PTR_CMenuItem__scalar_deleting_dtor_005db440`, while the shared compact scalar-deleting destructor restores that compact vtable and conditionally frees `this`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-233831_post_wave1023_frontend_options_pause_menu_review_verified`. Runtime menu-item lifetime behavior, exact source-body identity, concrete compact menu-item layout, BEA patching, and rebuild parity remain separate proof.

## Functions

### CMenuItem (Base Class)

| Address | Name | Purpose | Notes |
|---------|------|---------|-------|
| 0x004a3100 | CMenuItem__IsMouseInBounds | Check if mouse is within item bounds | Wrapper for `CFrontEnd__GetCursorStateInRect` |
| 0x004a3120 | CMenuItem__IsMouseClicked | Check if mouse clicked on item | Wrapper for `CFrontEnd__GetClickStateInRect` |
| 0x004a3140 | CMenuItem__Clone | Clone helper (compact object) | Allocates 0x1c bytes and copies core display fields |
| 0x004a3190 | CMenuItem__GetText | Resolve menu item display text | Vtable slot 2; returns `short *` text from CText/Localization/scratch paths |
| 0x004a3260 | CMenuItem__RenderCentered | Render item centered at position | Calls vtable+8 then Render |
| 0x004a3290 | CMenuItem__RenderWithColor | Render item with custom color | Calls vtable+8 then Render |
| 0x004a32c0 | CMenuItem__Render | Main render function | Handles icon+text, color states |
| 0x004a3420 | CMenuItem__GetTextWidth | Compute compact/base text width | Vtable slot 5 in recovered sibling/base table |
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
| 0x004d01c0 | CMenuItem__RestoreCompactVTable | Compact menu-item vtable reset | Writes `PTR_CMenuItem__scalar_deleting_dtor_005db440`; Wave465 corrected stale constructor-like label |
| 0x004d0290 | CControllerBackMenuItem__RenderBindingCapacityWarning | Controller-back render helper | Checks binding capacity and renders with warning color when localized ids `0xe8/0xe9` apply |
| 0x004d0490 | CMenuItem__shared_compact_scalar_deleting_dtor | Shared compact scalar-deleting destructor | Calls `CMenuItem__RestoreCompactVTable`, conditionally frees `this`, and is referenced by multiple menu-item family vtables |
| 0x004cf050 | CMenuItem__Destructor_Thunk | Base destructor thunk | Wave824 corrected the raw row to an explicit thunk label targeting `0x004a3730 CMenuItem__Destructor` |

### CMenuItemDropdown

| Address | Name | Purpose | Notes |
|---------|------|---------|-------|
| 0x004a3b10 | CMenuItemDropdown__Init | Initialize dropdown | vtable 0x005dc578 |
| 0x004a3b50 | CMenuItemDropdown__UpdateSelection | Update current selection | Vtable slot 12; syncs +0x1c/+0x20 via vtable+0x3c |
| 0x004a3b60 | CMenuItemDropdown__InitVariant | Alternate init | vtable 0x005dc5c4; extra slots include Yes/No text helper |
| 0x004a3ba0 | CMenuItemDropdown__ClearPending | Clear pending dropdown render | Sets DAT_0070486c = 0 before range traversal |
| 0x004a3be0 | CMenuItemDropdown__RenderOrQueueDeferred | Deferred popup render helper | Vtable slot 4; queues this/x/y when interactive, otherwise renders directly |
| 0x004a3bb0 | CMenuItemDropdown__ProcessPending | Process pending dropdown render | Consumes queued this/x/y globals after range traversal |
| 0x004a3c30 | CMenuItemDropdown__Render | Render dropdown | Handles collapsed/expanded states, hover/click helpers, selection animation |
| 0x004a40e0 | CMenuItemDropdown__IsExpanded | Return expanded/edit flag | Reads dropdown state byte at +0x24 |
| 0x004a4110 | CMenuItemDropdown__ButtonPressed | Button input handler | Handles up/down/select/cancel and deferred/immediate commit behavior |
| 0x004a42f0 | CMenuItemDropdown__HasPendingSelectionChange | Detect pending change | True when +0x25 is set and current selection differs from committed selection |
| 0x004a40f0 | CMenuItemDropdown__CommitSelection | Commit hover to selection | Calls vtable+0x38 callback then updates +0x1c |

### CMenuItemSlider

| Address | Name | Purpose | Notes |
|---------|------|---------|-------|
| 0x004a4250 | CMenuItemSlider__Init | Initialize slider | vtable 0x005dc610, default ID=3, linked range/list at +0x1c |
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
| 0x004a4810 | CMenuItemRange__Render | Main render function | Returns range title text pointer; Wave481 corrected return type to `short *` |
| 0x004d05c0 | CMenuItemRange__IsBindingActive | Binding-context active predicate | Wave824 hardened the `this+0x08` / `context+0x08` predicate used by `CMenuItemRange__Render` |
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
   - `0x00453a50` (`ButtonPressed_NoOp`) is a zero-body button-handler slot (`RET 0x0c`) observed in menu-item-family vtable data.
   - `0x00453a60` (`IsEnabled`) returns field `this+0x10`; `CMenuItemRange__SetItemEnabled` writes this field.
   - `0x00453a70` (`GetRowHeight`) returns `0x14` or `0x28` based on secondary text-id presence at `this+0x0c`.
   - `0x00453a80` (`DefaultFalseFlag`) is a shared default-false bool stub used by base slots `0x20/0x24/0x28`.
   - `0x00453a90` (`scalar_deleting_dtor`) installs vtable `0x005db440`, conditionally frees through `OID__FreeObject` when flags bit 0 is set, and returns `this`.

9. **Wave371 Ghidra read-back boundary**:
   - Fresh read-back on 2026-05-13 confirmed the saved names/signatures/comments/tags for `0x00453a50`, `0x00453a60`, `0x00453a70`, `0x00453a80`, and `0x00453a90`.
   - Primary vtable evidence for this recovered base-vfunc cluster is `0x005db440`: slot 0 `CMenuItem__scalar_deleting_dtor`, slot 1 `CMenuItem__ButtonPressed_NoOp`, slot 3 `CMenuItem__IsEnabled`, slot 6 `CMenuItem__GetRowHeight`, and slots 8-10 `CMenuItem__DefaultFalseFlag`.
   - Sibling vtable evidence at `0x005dc520` still reuses `IsEnabled`, `GetRowHeight`, and `DefaultFalseFlag`, but it does not carry the same slot-0 destructor or slot-1 no-op handler. Treat the two vtables as related menu-item-family evidence, not one interchangeable table.
   - Static retail evidence only; exact source method identity, concrete class layout, runtime frontend behavior, and rebuild parity remain unproven for this tranche.

10. **Wave440 CMenuItem base read-back boundary**:
   - Fresh read-back on 2026-05-16 hardened signatures/comments/tags for the base `CMenuItem` cluster at `0x004a3100`, `0x004a3120`, `0x004a3140`, `0x004a3190`, `0x004a3260`, `0x004a3290`, `0x004a32c0`, `0x004a3420`, `0x004a3450`, `0x004a3510`, `0x004a3610`, `0x004a3630`, `0x004a3730`, `0x004a37c0`, `0x004a43a0`, `0x004a4450`, and `0x004a44c0`.
   - Primary vtable evidence remains split across `0x005dc520` for the full 0x38-byte item and `0x005db440` for the compact/recovered sibling table. The two clone bodies are intentionally same-named in Ghidra but address-distinguished: `0x004a3140` allocates `0x1c`, while `0x004a3450` allocates `0x38`.
   - Mouse helpers at `0x004a3100` and `0x004a3120` are cdecl four-float wrappers for `CFrontEnd__GetCursorStateInRect` and `CFrontEnd__GetClickStateInRect`; callers consume the helper status.
   - Static retail decompile/xref/vtable evidence only. The local Stuart source snapshot does not contain a `MenuItem.cpp` body, so exact source identity, concrete field names, runtime frontend rendering/input behavior, and rebuild parity remain unproven.

11. **Wave441 CMenuItemDropdown / CMenuItemSlider read-back boundary**:
   - Fresh read-back on 2026-05-16 hardened signatures/comments/tags for `CMenuItemDropdown` and `CMenuItemSlider` targets at `0x004a3b10`, `0x004a3b50`, `0x004a3b60`, `0x004a3ba0`, `0x004a3bb0`, `0x004a3be0`, `0x004a3c30`, `0x004a40e0`, `0x004a40f0`, `0x004a4110`, `0x004a42f0`, `0x004a4250`, `0x004a4290`, and `0x004a4310`.
   - Dropdown vtable evidence is split across `0x005dc578` and variant table `0x005dc5c4`; both share button/render/text/state/commit/update slots, while the variant table adds `SharedVFunc__Return2_004059c0` and `Localization__GetYesNoString`.
   - Dropdown deferred popup rendering uses globals `DAT_0070486c` for queued `this`, `DAT_00704874` for queued x, and `DAT_00704870` for queued y. `CMenuItemRange__Render` clears the pending pointer before traversal and processes it after traversal.
   - `CMenuItemDropdown__Render` has a `RET 0x0c` signature with an observed queued-pass stack argument. Static decompile shows callers push `0` or `1`, but the body does not otherwise use the flag.
   - `CMenuItemSlider__Init` stores the linked range/list pointer at `+0x1c`; `CMenuItemSlider__ButtonPressed` walks that linked set on select button `0x2c` and calls each child item callback at vtable+`0x2c`.
   - Static retail decompile/xref/vtable evidence only. Runtime frontend dropdown/slider behavior, exact concrete layouts, exact field names/types, source-body identity, BEA launch, game patching, and rebuild parity remain unproven.

12. **Wave442 CMenuItemRange / CMenuItemRangeVariant read-back boundary**:
   - Fresh read-back on 2026-05-16 hardened signatures/comments/tags for `CMenuItemRange` and `CMenuItemRangeVariant` targets at `0x004a45c0`, `0x004a4610`, `0x004a4630`, `0x004a4670`, `0x004a4680`, `0x004a4730`, `0x004a4790`, `0x004a4810`, `0x004a4cd0`, `0x004a4d20`, `0x004a4dd0`, `0x004a4e10`, `0x004a4e60`, and `0x004a4e80`.
   - `CMenuItemRange` uses a compact four-slot vtable at `0x005dc650`: scalar destructor, `HandleKeyPress`, `ProcessInput`, and shared `CMenuItem__DefaultFalseFlag`. The adjacent dword after those four slots is not range vtable evidence.
   - `CMenuItemRangeVariant` starts at `0x005dc664` and reuses the range button and input-forwarding slots after its own scalar destructor. The slot walk is intentionally bounded because unrelated data/functions follow the confirmed table.
   - Range construction stores title text at `+0x04`, initializes the linked item set at `+0x08`, clears selected index `+0x18` and cached blank texture `+0x24`, stores render origin floats at `+0x1c/+0x20`, and keeps unresolved panel/layout fields at `+0x28/+0x2c`.
   - `CMenuItemRange__Render` clears pending dropdown rendering before traversal, measures row heights via child vtable+`0x18`, lazy-loads `FrontEnd_v2/FE_Blank.tga`, updates selection from mouse hover/click when bindings allow it, processes the deferred dropdown after traversal, and returns the range title text pointer from `this+0x04`. Wave481 corrected its saved return type to `short *`.
   - Static retail decompile/xref/vtable evidence only. Runtime frontend range/variant behavior, exact concrete layouts, exact field names/types, source-body identity, BEA launch, game patching, and rebuild parity remain unproven.

13. **Wave465 compact menu-item tail read-back boundary**:
   - Fresh read-back on 2026-05-16 corrected compact menu-item tail metadata for `0x004d01c0`, `0x004d0290`, and `0x004d0490`.
   - `CMenuItem__RestoreCompactVTable` is deliberately behavior-named: the body only installs `PTR_CMenuItem__scalar_deleting_dtor_005db440`, and the evidence does not prove a full constructor or destructor body by itself.
   - `CMenuItem__shared_compact_scalar_deleting_dtor` is DATA-referenced by multiple menu-item family vtables and calls the compact vtable-reset helper before optional `CDXMemoryManager__Free`.
   - `CControllerBackMenuItem__RenderBindingCapacityWarning` checks free binding slots, tests multiplayer/controller state, resolves localized warning text ids `0xe8/0xe9`, and forwards to `CMenuItem__RenderWithColor`.
   - Static retail decompile/xref/vtable evidence only. Runtime frontend render/input behavior, exact concrete layouts, exact field names/types, source-body identity, BEA launch, game patching, and rebuild parity remain unproven.

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

## Wave1151 Current-Risk Tag Normalization

Wave1151 tag-only normalization also covers `0x004cf050 CMenuItem__Destructor_Thunk` as a score21 current-risk row. It preserves the menu-item destructor-thunk evidence and adds Wave1151/current-risk tags only. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
