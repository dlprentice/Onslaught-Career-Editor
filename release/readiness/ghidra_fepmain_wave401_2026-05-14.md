# Ghidra FEPMain Correction Tranche - 2026-05-14

Status: public-safe static evidence note

This note records a serialized static Ghidra correction wave for eleven `CFEPMain` main-menu targets. It documents saved Ghidra metadata only. It does not include private decompile excerpts, private screenshots, copied executables, copied saves, raw runtime evidence, or private asset payloads.

## What Changed

| Address | Saved state | Public-safe evidence summary |
| --- | --- | --- |
| `0x004621b0` | `int __fastcall CFEPMain__Init(void * this)` | Hardened the comment for the CFEPMain init slot. Static read-back shows selection/timer state seeds at `+0x14`, `+0x1c`, and `+0x20`, with the function returning `1` from the CFEPMain vtable slice. |
| `0x004621d0` | `int __cdecl CFEPMain__GetMenuType(void)` | Corrected the stale hidden-`this` parameter. Static read-back shows a no-argument getter returning constant menu type `7`. |
| `0x004621e0` | `int __stdcall CFEPMain__GetActionCount(int menu_state)` | Corrected the stale extra receiver parameter. Static read-back shows a stack-only `menu_state` switch with career-in-progress gating, controller-count gating, memory-card/dialog flag use, and default-zero behavior. |
| `0x00462250` | `void __thiscall CFEPMain__ButtonPressed(void * this, int button, float val)` | Hardened the button-handler comment. Static read-back shows menu up/down/select and language-cycling inputs `0x2a`, `0x2b`, `0x2c`, `0x36`, and `0x37`, with selection fields and frontend sounds updated. |
| `0x004623e0` | `void __fastcall CFEPMain__DoAction(void * this)` | Refreshed the stale source-style comment into a bounded static claim. Static read-back shows action routing for New Game, Continue, Load, Options, Multiplayer, Goodies, Credits, and Return, including Career/list refresh helpers, page globals, and `DAT_0089d94c`. |
| `0x00462640` | `void __thiscall CFEPMain__Process(void * this, int state)` | Hardened the process-loop comment. Static read-back shows state-gated menu updates, career-node checks for `800` and `0x2e5`, the `FEPMain.cpp` debug-path allocation call before `CCareer__Save` and `CFEPOptions__WriteDefaultOptionsFile`, and page `0x0c`/new-game refresh paths. |
| `0x00462b70` | `void __stdcall CFEPMain__RenderPreCommon(float transition, int dest)` | Corrected the stale extra receiver parameter. Static read-back shows a stack-only transition/dest helper that handles destination `0x0c`, computes front-end video fade values, and draws the shared pre-render layer. |
| `0x00462c90` | `void __stdcall CFEPMain__Update(int menu_state)` | Corrected the stale extra receiver parameter. Static read-back shows stack-only menu-state mapping to `FrontEndText` token lookups `0`, `1`, `2`, `4`, `5`, `6`, `3`, and fallback `8`. |
| `0x00462d40` | `void __thiscall CFEPMain__Render(void * this, float transition, int dest)` | Hardened the main-render comment. Static read-back shows use of the selection state at `+0x8`, transition/dest arguments, language arrows/pulse state, and state-specific menu rows. |
| `0x004644d0` | `void __fastcall CFEPMain__TransitionNotification(void * this, int from)` | Hardened the transition hook comment. Static read-back shows `+0x14` reset to `-1.0`, platform-time refresh, career-in-progress promotion from state `0` to `1`, selection mirroring, and float-selection storage. |
| `0x00464520` | `void __fastcall CFEPMain__ActiveNotification(void * this, int from_page)` | Hardened the active-notification hook comment. Static read-back shows `+0x14` and `+0x18` cleared from the CFEPMain vtable slice with the page argument ignored. |

## Vtable Correction

Fresh vtable read-back corrects an older note in `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md`.

- The full CFEPMain dispatch slice is best represented from `0x005dbae4`: slot `0` is `CFEPMain__Init`, slot `2` is `CFEPMain__Process`, slot `3` is `CFEPMain__ButtonPressed`, slot `7` is `CFEPMain__ActiveNotification`, and slot `11` is `CFEPMain__DoAction`.
- `0x005dbaf0` starts with `CFEPMain__ButtonPressed`; it is not a `CFEPMain__Process`-first table.
- `0x005dbb00` points to `CFEPMain__ActiveNotification`; it is not an init slot.

Plain-text probe anchors: 0x005dbaf0 starts with CFEPMain__ButtonPressed; 0x005dbb00 points to CFEPMain__ActiveNotification.

## Source Boundary

The retail binary contains the debug-path string `[maintainer-local-source-export-root]\FEPMain.cpp`, but `FEPMain.cpp` is absent from the current Stuart source snapshot. Source-style names in this tranche are supported by retail vtable/debug-path/action-routing evidence, not by a direct source file match.

Plain-text source-boundary anchor: FEPMain.cpp is absent from the current Stuart source snapshot.

## Validation

- `ApplyFEPMainWave401.java` dry run: `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- `ApplyFEPMainWave401.java` apply run: `updated=11 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Metadata/decompile/xref/tag/instruction/vtable read-back is stored under ignored `subagents/`.
- Focused probe: `tools/ghidra_fepmain_wave401_probe.py --check`.
- Self-test: `tools/ghidra_fepmain_wave401_probe_test.py`.
- Read-back verified `11` metadata rows, `11` decompile exports, `19` xref rows, `11` tag rows, `1155` instruction rows, and `72` combined vtable rows.

## Claim Boundary

This tranche improves saved static Ghidra comments, tags, and signatures for the CFEPMain main-menu cluster. It does not prove runtime frontend behavior, does not prove exact source identity, does not recover concrete structure types/locals, does not launch or patch `BEA.exe`, and does not prove rebuild parity.
