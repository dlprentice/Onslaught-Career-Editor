# FrontEnd.cpp - Function Index

> Source File: FrontEnd.cpp | Category: Frontend/Menu System

## Overview

Main frontend menu system controller. CFrontEnd is the master class that owns and coordinates all 24 frontend page (FEP) objects. It handles initialization, page transitions, and the main menu loop.

**Debug Path**: `C:\dev\ONSLAUGHT2\FrontEnd.cpp` at 0x00629df0

## Functions

| Address | Function | Status | Description |
|---------|----------|--------|-------------|
| 0x004662a0 | [CFrontEnd__Init](./CFrontEnd__Init.md) | RENAMED | Initialize all 24 frontend pages and set initial state |
| 0x00466980 | [CFrontEnd__GetPlayer0ControllerPort](./CFrontEnd__GetPlayer0ControllerPort.md) | RENAMED | Returns player-0 controller port (normalizes unset sentinel) |
| 0x00466990 | [CFrontEnd__NumControllersPresent](./CFrontEnd__NumControllersPresent.md) | RENAMED | Returns number of controller ports available to frontend |
| 0x00466ab0 | [CFrontEnd__SetLanguage](./CFrontEnd__SetLanguage.md) | RENAMED | Switch frontend text/language resource set |
| 0x00466ae0 | [CFrontEnd__SetPage](./CFrontEnd__SetPage.md) | RENAMED | Page transition helper (immediate or timed transition) |
| 0x00466ba0 | [CFrontEnd__Process](./CFrontEnd__Process.md) | RENAMED | Per-frame frontend update body (event manager, controllers, pages, message box) |
| 0x00466de0 | [CFrontEnd__DrawLine](./CFrontEnd__DrawLine.md) | RENAMED | Draws line sprite between two points |
| 0x00466e70 | [CFrontEnd__DrawBox](./CFrontEnd__DrawBox.md) | RENAMED | Draws box via four edge lines |
| 0x00467010 | [CFrontEnd__DrawPanel](./CFrontEnd__DrawPanel.md) | RENAMED | Draws clamped blank-panel rectangle |
| 0x004670b0 | [CFrontEnd__DrawBarGraph](./CFrontEnd__DrawBarGraph.md) | RENAMED | Draws panel-backed proportional bar fill |
| 0x00467200 | [CFrontEnd__DrawSlidingTextBordersAndMask](./CFrontEnd__DrawSlidingTextBordersAndMask.md) | RENAMED | Transition bracket/mask animation renderer |
| 0x004679a0 | [CFrontEnd__HasStandardSlidingTextBordersAndMask](./CFrontEnd__HasStandardSlidingTextBordersAndMask.md) | RENAMED | Static page-style predicate used by border/mask renderer |
| 0x00467ae0 | [CFrontEnd__DrawBar](./CFrontEnd__DrawBar.md) | RENAMED | Draws segmented header/title bar |
| 0x00467bd0 | [CFrontEnd__DrawTitleBar](./CFrontEnd__DrawTitleBar.md) | RENAMED | Draws animated title-bar visuals and text |
| 0x004681c0 | [CFrontEnd__EnableAdditiveAlpha](./CFrontEnd__EnableAdditiveAlpha.md) | RENAMED | Sets additive blend mode (ONE/ONE) |
| 0x004681e0 | [CFrontEnd__EnableModulateAlpha](./CFrontEnd__EnableModulateAlpha.md) | RENAMED | Sets alpha-modulate blend mode (SRCALPHA/INVSRCALPHA) |
| 0x00468200 | [CFrontEnd__Render](./CFrontEnd__Render.md) | RENAMED | Frontend render pass used by Run's `while (!Render())` loop |
| 0x004684d0 | [CFrontEnd__Run](./CFrontEnd__Run.md) | RENAMED | Main frontend loop - runs Init then calls `CFrontEnd__Process` |
| 0x00468730 | [CFrontEnd__GetShadowOffsetX](./CFrontEnd__GetShadowOffsetX.md) | RENAMED | Computes animated X shadow offset |
| 0x00468750 | [CFrontEnd__GetShadowOffsetY](./CFrontEnd__GetShadowOffsetY.md) | RENAMED | Computes animated Y shadow offset |
| 0x00468770 | [CFrontEnd__PlaySound](./CFrontEnd__PlaySound.md) | RENAMED | UI sound helper (move/select/back) |

## Headless Semantic Wave118 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x00452ce0 | CFrontEnd__RenderVideoQuadScaledToWindow | Pre-common render helper that resolves default window-scaled center coordinates and renders the frontend video quad (`CDXFrontEndVideo__Render`). |
| 0x00469390 | CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture | Input gate wrapper: returns mouse-ready mask when active, otherwise dispatches `CVBufTexture` interaction path. |
| 0x00469550 | CFrontEnd__ResolveLevelNameTextByCode | Maps level/world numeric codes to localized text IDs with fallback to `\"Unnamed Level\"`. |

## Headless Semantic Wave119 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x004691c0 | CFrontEnd__ReleaseParticleHudWaypointResources | Cleanup helper that destroys particle-manager state, clears HUD-owned handles, frees waypoint/mesh transient resources, and nulls retained pointers. |

## Headless Semantic Wave121 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x00469c20 | CFrontEnd__ResolveEpisodeNameTextByIndex | Resolves episode indices (`1..8`) to localized episode-name strings with fallback to `\"Unnamed Episode\"`. |
| 0x00469cf0 | CFrontEnd__ResolveLevelNameTextIdByCode | Resolves level/world numeric code to localized text-id; returns `-1` when unmapped. |
| 0x0046a210 | CFrontEnd__GetFallbackUnnamedLevelTextId | Returns fallback sentinel text-id used when level-name code resolution fails. |

## Headless Semantic Wave122 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x00472ad0 | UISelectionList__AdvanceToNextEnabledWithWrap | Advances selection to the next enabled UI entry with wrap-around and plays move SFX when selection changes. |

## CFrontEnd Class Layout

Based on analysis of `CFrontEnd__Init`, the class contains pointers to 24 frontend page objects at offset 0x214:

| Offset | Index | Page Class | Notes |
|--------|-------|------------|-------|
| 0x214 | 0 | CFEPage (base) | Points to 0x278 |
| 0x218 | 1 | CFEPage | Points to 0x29c |
| 0x21c | 2 | CFEPage | Points to 0x2b0 |
| 0x220 | 3 | CFEPage | Points to 0x2bc (700 decimal) |
| 0x224 | 4 | CFEPage | Points to 0x2ec |
| 0x228 | 5 | CFEPage | Points to 0x324 |
| 0x22c | 6 | CFEPage | Points to 0x338 - Main menu? |
| 0x230 | 7 | CFEPage | Points to 0x360 |
| 0x234 | 8 | CFEPage | Points to 0x37dc |
| 0x238 | 9 | CFEPage | Points to 0x39b8 |
| 0x23c | 10 | CFEPage | Points to 0x39d0 |
| 0x240 | 11 | CFEPage | Points to 0x3c1c |
| 0x244 | 12 | CFEPage | Points to 0x4034 |
| 0x248 | 19 | CFEPage | Points to 0x413c |
| 0x24c | 20 | CFEPage | Points to 0x4834 |
| 0x250 | 15 | CFEPage | Points to 0x40b8 |
| 0x254 | 13 | CFEPage | Points to 0x4050 |
| 0x258 | 14 | CFEPage | Points to 0x40ec |
| 0x25c | 16 | CFEPage | Points to 0x4118 |
| 0x260 | 17 | CFEPage | Points to 0x4124 |
| 0x264 | 21 | CFEPage | Points to 0x8848 |
| 0x268 | 22 | CFEPage | Points to 0xbcc8 |
| 0x26c | 23 | CFEPage | Points to 0xbde0 |
| 0x270 | 24 | CFEPage (null) | Points to 0xbe04 (default null page) |

### Key CFrontEnd Members

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x1f8 | int | mCurrentPage | Page index to display (-1 = use mPreviousPage) |
| 0x200 | int | mPreviousPage | Previous page index |
| 0x1f4 | int | mLastWorld | World ID (500+ range for campaign) |
| 0x214-0x270 | ptr[] | mPages[24] | Frontend page object pointers |
| 0xbe0c | ptr[2] | mUnknown | Two objects allocated at line 0xb3 (179) |
| 0xbe14 | int | mState | State (-2 = running, -1 = exit, etc.) |
| 0xbe18 | int | mUnknown2 | Unknown state |
| 0xbe1c | int | mFromOutro | Non-zero after outro/victory |
| 0xbe20 | float | mUnknown3 | Initialized to -100.0f |
| 0xbe2c | int | mPlayType | 2 = something special |
| 0xbf34 | int | mNextPage | Used with timed transitions |
| 0xbf38 | int | mTransitionTimer | Timer for page transitions |

## Page Index Constants

Based on code flow analysis in `CFrontEnd__Init`:

| Index | Probable Page | Evidence |
|-------|---------------|----------|
| 0x00 (0) | Legal/Splash | First page after load |
| 0x06 (6) | Main Menu | Default fallback, set at offset 0x22c |
| 0x08 (8) | ? | Special case for worlds 0x385-0x389 |
| 0x0b (11) | ? | Used with timed transition |
| 0x0c (12) | ? | Intro/demo mode start |
| 0x10 (16) | ? | Special case for worlds 0x352-0x36f |
| 0x17 (23) | ? | Transition page, set before `CFrontEnd__SetPage` calls |

## Global Variables Referenced

| Address | Name | Purpose |
|---------|------|---------|
| 0x00662f40 | DAT_00662f40 | If non-zero, calls `CSoundManager__ReloadLanguageSampleBank` during init |
| 0x0066304c | DAT_0066304c | Level override (-1 = none, else jump to level) |
| 0x00662dd0 | DAT_00662dd0 | Demo/intro flag |
| 0x00662dcc | DAT_00662dcc | If non-zero, calls FUN_004bb8c0 at end |
| 0x006630cc | DAT_006630cc | Special mode flag |
| 0x0083d448 | DAT_0083d448 | Demo state |
| 0x0083d454 | DAT_0083d454 | Playable demo timeout control |
| 0x008a9ab4 | DAT_008a9ab4 | Init complete flag |
| 0x008a9580 | DAT_008a9580 | Unknown flag set during transitions |
| 0x008a9584 | DAT_008a9584 | Unknown flag set during transitions |
| 0x008a9aac | DAT_008a9aac | Cleared to 0 after page init |
| 0x00679b40 | DAT_00679b40 | Frontend active flag (1 during Run loop) |

## Cross-References

### Calls To
- `CCareer__Update` - Update career progress
- `CConsole__SetLoading` - Loading-screen enable/disable toggle used around frontend init/load phases
- `CConsole__SetLoadingRange` / `CConsole__SetLoadingFraction` - Progress bar range/value updates
- `CFrontEnd__LoadSharedResources` - Resource loading (returns 0 on failure)
- `CFrontEndPage__Init_ReturnTrue` - Resource loading gate helper (returns non-zero success)
- `CDXFrontEndVideo__SetDefaultSize` - Frontend video default-size setup (returns non-zero success)
- `CFrontEnd__SetPage` - Page transition function
- `OID__AllocObject` - Memory allocation (size 0x178, align 0x27)
- `CPCController__ctor` - Controller object construction

### Called By
- `FUN_00XXXXXX` (main game loop - not yet identified)

## Discovery Method

Found via xrefs to debug path string `C:\dev\ONSLAUGHT2\FrontEnd.cpp` at 0x00629df0:
- 0x00466578 in CFrontEnd__Init (line 179 / 0xb3)
- 0x005d2735 in Unwind@005d2730 (exception handler)

## Notes

1. **24 Frontend Pages**: The system initializes 24 page pointers (0x18 in hex), iterating with format string "FEP %d..." during loading
2. **Page Virtualization**: Each page object has a vtable with methods at offsets 0x00 (init), 0x18 (activate?), 0x1c (show?)
3. **Dev Mode Checks**: Several paths check `g_bDevModeEnabled` and `g_bAllCheatsEnabled` for special behavior
4. **World ID Ranges**: Certain world IDs (0x352-0x36f, 0x385-0x389) trigger specific page selections

## Migration Notes

- Created Dec 2025 during systematic FrontEnd.cpp analysis
- Debug path xref discovery method
