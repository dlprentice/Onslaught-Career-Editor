# FEPMain.cpp Functions

> Source File: FEPMain.cpp | Binary: BEA.exe
> Debug Path String: 0x00629414 (`C:\dev\ONSLAUGHT2\FEPMain.cpp`)
> RTTI Type Name: 0x00629d80 (`.?AVCFEPMain@@`)

## Overview

`CFEPMain` is the retail frontend main-menu page cluster. Static read-back ties it to New Game, Continue, Load Game, Options, Multiplayer, Goodies, Credits/About, and return-state action routing.

Source boundary: the retail binary contains the `C:\dev\ONSLAUGHT2\FEPMain.cpp` debug-path string, but `FEPMain.cpp` is absent from the current Stuart source snapshot. The names below are supported by retail vtable/debug-path/action-routing evidence, not by a direct source-file match.

Wave953 (`cfepmain-menu-review-wave953`) re-reviewed the CFEPMain main-menu cluster read-only after the Wave951/Wave952 GameInterface pause-menu work. Fresh exports verified 17 metadata rows, 17 tag rows, 257 xref rows, 2935 instruction rows, 17 decompile rows, 56 vtable rows, and the debug path string `C:\dev\ONSLAUGHT2\FEPMain.cpp`. Exact focused anchors: `0x004621d0 CFEPMain__GetMenuType`, `0x004621e0 CFEPMain__GetActionCount`, `0x00462b70 CFEPMain__RenderPreCommon`, and `0x00462c90 CFEPMain__Update`. The review preserved the Wave401 vtable correction: `0x005dbae4` is the full dispatch slice, `0x005dbaf0` starts with `CFEPMain__ButtonPressed`, and `0x005dbb00` starts with `CFEPMain__ActiveNotification`. No mutation was needed. Wave911 focused re-audit progress after Wave953 is `280/1408 = 19.89%`; static export-contract closure remains `6151/6151 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260528-093826_post_wave953_cfepmain_menu_review_verified`. Runtime main-menu behavior, exact source identity, concrete CFEPMain layout, BEA patching, and rebuild parity remain separate proof.

## CFEPMain Dispatch/Vtable Layout

Wave401 corrected the older vtable note. The full CFEPMain dispatch slice is best represented from `0x005dbae4`.

### Full CFEPMain Dispatch Slice (`0x005dbae4`)

| Offset | Address | Name | Purpose |
| --- | --- | --- | --- |
| `+0x00` | `0x004621b0` | `CFEPMain__Init` | Main-menu state/timer init slot. |
| `+0x04` | `0x0040c640` | `DebugTrace` | Retail trace stub/no-op inherited/shared slot. |
| `+0x08` | `0x00462640` | `CFEPMain__Process` | Per-frame process/update entry. |
| `+0x0c` | `0x00462250` | `CFEPMain__ButtonPressed` | Button input handler. |
| `+0x10` | `0x00462b70` | `CFEPMain__RenderPreCommon` | Pre-render transition/setup helper. |
| `+0x14` | `0x00462d40` | `CFEPMain__Render` | Main render path. |
| `+0x18` | `0x004644d0` | `CFEPMain__TransitionNotification` | Page transition notification hook. |
| `+0x1c` | `0x00464520` | `CFEPMain__ActiveNotification` | Active-page notification hook. |
| `+0x20` | `0x00459990` | inherited | Base/embedded frontend-page helper. |
| `+0x24` | `0x004621e0` | `CFEPMain__GetActionCount` | Menu-state action-count getter. |
| `+0x28` | `0x004621d0` | `CFEPMain__GetMenuType` | Constant menu-type getter. |
| `+0x2c` | `0x004623e0` | `CFEPMain__DoAction` | Main action router. |
| `+0x30` | `0x00462c90` | `CFEPMain__Update` | Menu-state text-token mapper. |

### Page-Notification Sub-Slice (`0x005dbaf0`)

| Offset | Address | Name | Purpose |
| --- | --- | --- | --- |
| `+0x00` | `0x00462250` | `CFEPMain__ButtonPressed` | Button input handler. |
| `+0x04` | `0x00462b70` | `CFEPMain__RenderPreCommon` | Pre-render transition/setup helper. |
| `+0x08` | `0x00462d40` | `CFEPMain__Render` | Main render path. |
| `+0x0c` | `0x004644d0` | `CFEPMain__TransitionNotification` | Page transition notification hook. |
| `+0x10` | `0x00464520` | `CFEPMain__ActiveNotification` | Active-page notification hook. |
| `+0x14` | `0x00459990` | inherited | Base/embedded frontend-page helper. |
| `+0x18` | `0x004621e0` | `CFEPMain__GetActionCount` | Menu-state action-count getter. |
| `+0x1c` | `0x004621d0` | `CFEPMain__GetMenuType` | Constant menu-type getter. |
| `+0x20` | `0x004623e0` | `CFEPMain__DoAction` | Main action router. |
| `+0x24` | `0x00462c90` | `CFEPMain__Update` | Menu-state text-token mapper. |

`0x005dbaf0` starts with `CFEPMain__ButtonPressed`, not `CFEPMain__Process`. `0x005dbb00` points to `CFEPMain__ActiveNotification`, not an init slot. `0x005dbb1c -> 0x00466140` remains tracked as adjacent `CGenericCamera__GetPos` context, not CFEPMain cleanup.

## Functions

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x004621b0` | `int __fastcall CFEPMain__Init(void * this)` | Seeds CFEPMain selection/timer state at observed offsets and returns success. |
| `0x004621d0` | `int __cdecl CFEPMain__GetMenuType(void)` | No-argument getter returning constant menu type `7`. |
| `0x004621e0` | `int __stdcall CFEPMain__GetActionCount(int menu_state)` | Stack-only `menu_state` switch with career-in-progress, controller-count, and dialog/memory-card flag gating. |
| `0x00462250` | `void __thiscall CFEPMain__ButtonPressed(void * this, int button, float val)` | Handles menu up/down/select and language-cycling inputs `0x2a`, `0x2b`, `0x2c`, `0x36`, and `0x37`. |
| `0x004623e0` | `void __fastcall CFEPMain__DoAction(void * this)` | Routes main-menu actions for New Game, Continue, Load, Options, Multiplayer, Goodies, Credits/About, and Return. |
| `0x00462640` | `void __thiscall CFEPMain__Process(void * this, int state)` | State-gated process loop including career-node checks, debug-path allocation context, `CCareer__Save`, and `CFEPOptions__WriteDefaultOptionsFile`. |
| `0x00462b70` | `void __stdcall CFEPMain__RenderPreCommon(float transition, int dest)` | Stack-only transition/dest helper for shared pre-render layer and destination `0x0c` context. |
| `0x00462c90` | `void __stdcall CFEPMain__Update(int menu_state)` | Stack-only menu-state mapping to `FrontEndText` token lookups and fallback text token `8`. |
| `0x00462d40` | `void __thiscall CFEPMain__Render(void * this, float transition, int dest)` | Main render path using selection state, transition/destination arguments, language arrows, pulse state, and state-specific menu rows. |
| `0x004644d0` | `void __fastcall CFEPMain__TransitionNotification(void * this, int from)` | Resets transition state, refreshes platform time, promotes career-in-progress state, mirrors selection, and stores float-selection state. |
| `0x00464520` | `void __fastcall CFEPMain__ActiveNotification(void * this, int from_page)` | Clears active-selection/timer fields; the page argument is ignored by the observed body. |

## Debug Path Reference

The checked debug-path xref sits inside the recovered `CFEPMain__Process` body. The assertion/debug path pushes line `0x61` (`97`) and file path `0x00629414` (`C:\dev\ONSLAUGHT2\FEPMain.cpp`) before the save/defaultoptions call chain.

## Menu Page Constants

| Constant | Static context |
| --- | --- |
| `0x07` | Save/load selection page. |
| `0x08` | Multiplayer menu page. |
| `0x0b` | Continue-game page context. |
| `0x0c` | Destination/page context observed in process and pre-render logic. |
| `0x10` | Options menu page. |
| `0x11` | Goodies gallery page. |
| `0x46` | Timed page-transition constant used by main-menu actions. |

## Global Context

| Address | Purpose |
| --- | --- |
| `0x00660620` | Global career data structure context. |
| `0x00662aa8` | Dialog/memory-card style gating flag used by action-count/action routing. |
| `0x008a9580` | Career-in-progress state mirror. |
| `0x008a9584` | Sub-menu return state. |
| `0x008a968c` | Current page id global. |
| `0x008a9690` | Previous/return page id global. |
| `0x0089d94c` | Counter/state global set during selected new-game paths. |

## Validation

Wave953 read-only re-audit evidence:

- `cfepmain-menu-review-wave953` re-exported the eleven CFEPMain rows plus six frontend context anchors with no missing rows and no mutation.
- Fresh read-back verified 17 metadata rows, 17 tag rows, 257 xref rows, 2935 instruction rows, 17 decompile rows, and 56 vtable rows.
- The existing Wave401 continuity probe still passed: `py -3 tools\ghidra_fepmain_wave401_probe.py --check`.
- Read-only backup verified at `G:\GhidraBackups\BEA_20260528-093826_post_wave953_cfepmain_menu_review_verified` with 19 files, 173542279 bytes, and `DiffCount=0`.

Wave401 saved and read back Ghidra metadata for the eleven targets above:

- `ApplyFEPMainWave401.java` dry run: `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- `ApplyFEPMainWave401.java` apply run: `updated=11 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back verified `11` metadata rows, `11` decompile exports, `19` xref rows, `11` tag rows, `1155` instruction rows, and `72` combined vtable-slot rows.
- Focused probe: `tools/ghidra_fepmain_wave401_probe.py --check` passed.

This is saved static Ghidra name/signature/comment/tag refinement only. It does not prove runtime frontend behavior, exact source identity, concrete CFEPMain layout, local variable names, structure types, BEA launch behavior, game patching, or rebuild parity.
