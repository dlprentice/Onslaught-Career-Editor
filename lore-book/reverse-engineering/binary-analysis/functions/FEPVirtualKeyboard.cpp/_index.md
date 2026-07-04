# FEPVirtualKeyboard.cpp - Function Analysis

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

**Class:** `CFEPVirtualKeyboard` (RTTI type descriptor string `.?AVCFEPVirtualKeyboard@@` at `0x00629d18`)

This FrontEnd page handles virtual-keyboard save-name entry behavior used by save/load flows.
The source file is not present in `references/Onslaught/`, so mapping here is retail-binary-first.

## Wave860 CFEPVirtualKeyboard Core

Wave860 CFEPVirtualKeyboard core static read-back (`fepvirtualkeyboard-core-wave860`, `wave860-readback-verified`) saved bounded comments/tags/signatures for eight important frontend/virtual-keyboard connective infrastructure rows from `0x0051ff90 CFEPVirtualKeyboard__Init` through `0x005214d0 CFEPVirtualKeyboard__IsSpecialKeyBlocked`. The pass corrected stale `0x0051fff0 CFEPOptions__EnumerateSaveFiles` to `0x0051fff0 CFEPVirtualKeyboard__SeedUniqueDefaultSaveName`, corrected `0x0051ffd0 CFEPVirtualKeyboard__Shutdown` to `void __fastcall CFEPVirtualKeyboard__Shutdown(void * this)`, and made no function-boundary or executable-byte changes.

Evidence ties the core to CFEPVirtualKeyboard vtable `0x005db830`, RTTI string `.?AVCFEPVirtualKeyboard@@`, default save-name strings `BEA` and ` %d`, existing-save duplicate checks through `EnumerateSaveFiles_1/2`, shared save-list refresh/render helpers, key-sink setup through `PlatformInput__SetKeySinkCore`, key-token dispatch through `CFEPVirtualKeyboard__HandleKeyToken`, and special-key filtering through `CFEPVirtualKeyboard__IsSpecialKeyBlocked`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-134150_post_wave860_fepvirtualkeyboard_core_verified`.

Post-Wave860 queue telemetry is `6105` functions, `5792` commented, `313` commentless, 0 exact-undefined signatures, and 0 `param_N` signatures. Comment-backed proxy is `5792/6105 = 94.87%`; strict clean-signature proxy is `5792/6105 = 94.87%`. The next raw commentless row is `0x00523a70 CDXEngine__RenderMouseCursorSprite`; commentless high-signal, signature, and name-confidence queues remain empty. Exact `CFEPVirtualKeyboard` layout, exact key-token enum identity, runtime virtual-keyboard input/render behavior, runtime save-name/filesystem behavior, BEA patching, and rebuild parity remain deferred.

## Wave801 Frontend/Render Helper Read-Back

Wave801 static read-back (`frontend-render-helpers-wave801`, `wave801-readback-verified`) saved a current comment/tag on `0x00465dd0 CFEPVirtualKeyboard__IsInputAccepted`. Static evidence shows the predicate returns accepted when `this+0x15c` is nonzero; otherwise it dispatches the first virtual function with `input_ctx` and compares the low byte result against `DAT_00679af4`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-073450_post_wave801_frontend_render_helpers_verified`.

This remains static retail Ghidra evidence only. Exact source-body identity, runtime virtual-keyboard behavior, save-name side effects, BEA patching, and rebuild parity remain deferred.

## Identified Functions

| Address | Name | Role | Notes |
|---------|------|------|-------|
| `0x0051ff90` | `CFEPVirtualKeyboard__Init` | vtable | Initializes keyboard page state fields and returns `1` |
| `0x0051ffd0` | `CFEPVirtualKeyboard__Shutdown` | vtable | Page shutdown helper; hides keyboard context when active |
| `0x0051fff0` | `CFEPVirtualKeyboard__SeedUniqueDefaultSaveName` | helper | Seeds a non-duplicate default save name with `BEA` plus numeric suffix; Wave860 supersedes stale `CFEPOptions__EnumerateSaveFiles` |
| `0x005202d0` | `CFEPVirtualKeyboard__Process` | vtable | Per-frame process; refreshes save list by state and handles context setup |
| `0x00520370` | `CFEPVirtualKeyboard__ButtonPressed` | vtable | Input handler for nav/select/back and character cycling |
| `0x00521100` | `CFEPVirtualKeyboard__Render` | vtable | Keyboard UI render path using transition alpha |
| `0x00520130` | `CFEPVirtualKeyboard__TransitionNotification` | vtable | Transition hook; resets cursor/selection and save-name defaults from prior page |
| `0x005214d0` | `CFEPVirtualKeyboard__IsSpecialKeyBlocked` | helper | Blocks page-specific special keys and empty/space-only confirm-like token |

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
| `0x00521260` | `CFEPVirtualKeyboard__DrawPanel` | render helper | Draws the virtual-keyboard panel, edit buffer, selected-name highlight, and blinking cursor. |

## Static Re-Audit Wave564

Wave564 hardened four helper signatures/comments/tags from static retail evidence:

| Address | Saved signature | Notes |
|---------|-----------------|-------|
| `0x00520530` | `void __thiscall CFEPVirtualKeyboard__InitKeyboardLayout(void * this)` | `CFEPVirtualKeyboard__Init` passes only `this` in `ECX`; the helper returns with plain `RET` and fills numeric, letter, punctuation, accented, and control-token key pages. |
| `0x00520cc0` | `void __thiscall CFEPVirtualKeyboard__HandleKeyToken(void * this, int key_token)` | `RET 0x4` and the select callsite prove one explicit `key_token`; handles control tokens `1..9`, edit-buffer mutation at `this+0x04`, `DAT_008a1388` commit, and `_DAT_0089bcb8` width gating. |
| `0x00520f70` | `void __thiscall CFEPVirtualKeyboard__MoveSelectionToRow(void * this, int target_row)` | `RET 0x4` and four row-navigation callsites prove one explicit `target_row`; preserves weighted column field `this+0x6f4`, updates `this+0x6e8/0x6ec`, and skips blocked special keys. |
| `0x00521260` | `void __thiscall CFEPVirtualKeyboard__DrawPanel(void * this, float panel_y, float transition, int alpha)` | `RET 0x0c` and `CFEPVirtualKeyboard__Render` prove three explicit args: `DAT_0063fd30`, `transition`, and clamped alpha. |

Read-back evidence: dry/apply/final dry reported clean Ghidra saves; post exports verified `4` metadata rows, `4` tag rows, `7` xref rows, `964` target instruction rows, `4` target decompiles, `3` caller decompiles, and `195` focused `DrawPanel` disassembly rows. Backup `[maintainer-local-ghidra-backup-root]\BEA_20260518-203938_post_wave564_fepvirtualkeyboard_verified` verified `19` files, `159878023` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

Limits: this class remains retail-binary-first; `FEPVirtualKeyboard.cpp` is not present in `references/Onslaught`, no `source-parity` tag was applied, and runtime virtual-keyboard behavior/save-name side effects/rebuild parity remain unproven.

## Wave860 Core Read-Back Details (0x0051ff90-0x005214d0)

| Address | Static read-back evidence |
| --- | --- |
| `0x0051ff90 CFEPVirtualKeyboard__Init` | Vtable slot 0; seeds `this+0x6f4` to `0.5`, clears edit/cursor/page state at `this+0x44`, `this+0x4c`, `this+0x50`, and `this+0x6e4..0x6f0`, calls `CFEPVirtualKeyboard__InitKeyboardLayout`, and returns `1`. |
| `0x0051ffd0 CFEPVirtualKeyboard__Shutdown` | Vtable slot 1; clears key sink `DAT_0051feb0` through `PlatformInput__SetKeySinkCore(&DAT_00855bb0, null)` when active; Wave860 corrected stale cdecl storage to `__fastcall`. |
| `0x0051fff0 CFEPVirtualKeyboard__SeedUniqueDefaultSaveName` | Owner/name correction for stale `CFEPOptions__EnumerateSaveFiles`; writes `BEA` plus ` %d` into the edit buffer, avoids existing save-name duplicates through `EnumerateSaveFiles_1/2`, caps search at `0x1001`, clamps cursor length at `this+0x44`, and sets active flag `this+0x48`. |
| `0x00520130 CFEPVirtualKeyboard__TransitionNotification` | Vtable slot 6; from pages `0`, `9`, or `0xe` may reseed the same default save name, then reset keyboard page/row/column fields `this+0x6e4..0x6ec`, restore `this+0x6f4` to `0.5`, and clamp cursor position. |
| `0x005202d0 CFEPVirtualKeyboard__Process` | Vtable slot 2; refreshes the shared save list through `CFEPDirectory__RefreshSaveFileList`, installs/clears virtual-keyboard key sink `DAT_0051feb0`, polls storage with `PCPlatform__GetStorageDeviceInfo`, and shows `CFEPSaveGame__RemovedMUWhinge(0x3c)` when no storage device is present. |
| `0x00520370 CFEPVirtualKeyboard__ButtonPressed` | Vtable slot 3; handles row movement for buttons `0x2a/0x2b`, selected-key dispatch through `CFEPVirtualKeyboard__HandleKeyToken` on button `0x2c`, cancel/page return on `0x2e`, and column cycling on `0x36/0x37` while skipping blocked keys. |
| `0x00521100 CFEPVirtualKeyboard__Render` | Vtable slot 5; renders and polls `CFEPDirectory__RenderSaveFileList`, copies selected save-name rows with `CRT__WcsNcpyZeroPad`, updates cursor/active flags, renders prompt/title/overlay paths, and calls `CFEPVirtualKeyboard__DrawPanel`. |
| `0x005214d0 CFEPVirtualKeyboard__IsSpecialKeyBlocked` | Helper called by `ButtonPressed` and `MoveSelectionToRow`; blocks key tokens `4` and `5` on keyboard page `1`, and blocks token `9` when the edit buffer is empty or only spaces. |

Read-back evidence: dry/apply/final dry reported `updated=8 skipped=0 renamed=0 would_rename=1 signature_updated=2 comment_only_updated=6 missing=0 bad=0`, then `updated=8 skipped=0 renamed=1 would_rename=1 signature_updated=2 comment_only_updated=6 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. Post exports verified `8` metadata rows, `8` tag rows, `11` xref rows, `648` instruction rows, `8` decompile rows, `13` context metadata rows, `13` context decompile rows, `18` vtable slots, `74` callsite instruction rows, and string dumps for `.?AVCFEPVirtualKeyboard@@`, `BEA`, and ` %d`.

## Notes

- `CFEPVirtualKeyboard__Process` (`0x005202d0`) calls `CFEPDirectory__RefreshSaveFileList` for non-state-3 paths.
- `CFEPVirtualKeyboard__Render` (`0x00521100`) calls shared helper `CFEPDirectory__RenderSaveFileList` (`0x0051ae70`) to draw/poll the save list strip.
- `CFEPVirtualKeyboard__TransitionNotification` (`0x00520130`) triggers save-name reseed/length clamp logic for selected page transitions (`from_page` checks include `0`, `9`, `14`).
- This class was originally recovered via manual function-object creation (`F`) followed by serialized direct-HTTP rename/signature writes with immediate read-back verification; Wave564 refreshed the helper signatures/comments/tags through serialized headless dry/apply/read-back.
