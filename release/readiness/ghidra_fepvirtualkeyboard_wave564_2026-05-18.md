# Ghidra FEP Virtual Keyboard Wave564 Readiness Note

Date: 2026-05-18
Status: PASS

## Scope

Wave564 hardened four FEP virtual keyboard `CFEPVirtualKeyboard` helpers:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00520530` | `void __thiscall CFEPVirtualKeyboard__InitKeyboardLayout(void * this)` | `CFEPVirtualKeyboard__Init` passes only `this` in `ECX`; the helper returns with plain `RET` and fills the virtual-keyboard key tables. |
| `0x00520cc0` | `void __thiscall CFEPVirtualKeyboard__HandleKeyToken(void * this, int key_token)` | `RET 0x4` and the select callsite prove one explicit `key_token`; the body handles control tokens, edit-buffer mutation, accented fallback, and confirm-page flow. |
| `0x00520f70` | `void __thiscall CFEPVirtualKeyboard__MoveSelectionToRow(void * this, int target_row)` | `RET 0x4` and four row-navigation callsites prove one explicit `target_row`; the body preserves weighted column state and skips blocked special keys. |
| `0x00521260` | `void __thiscall CFEPVirtualKeyboard__DrawPanel(void * this, float panel_y, float transition, int alpha)` | `RET 0x0c` and `CFEPVirtualKeyboard__Render` prove three explicit args: `DAT_0063fd30`, `transition`, and clamped alpha. |

No rename or boundary recovery was performed. This class is retail-binary-first because `FEPVirtualKeyboard.cpp` is not present in `references/Onslaught`; no `source-parity` tag was applied.

## Verification

- Dry pass: `updated=0 skipped=4 missing=0 bad=0`, `REPORT: Save succeeded`
- Apply pass: `updated=4 skipped=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Final dry: `updated=0 skipped=4 missing=0 bad=0`, `REPORT: Save succeeded`
- Post exports: `4` metadata rows, `4` tag rows, `7` xref rows, `964` focused instruction rows, `4` target decompiles, `3` caller decompiles, and `195` DrawPanel disassembly rows
- Queue refresh: `6089` total functions, `2800` commented, `3289` commentless, `1498` exact-undefined signatures, `1181` `param_N` signatures
- Strict proxy: `2800 / 6089 = 45.99%`
- Backup: `G:\GhidraBackups\BEA_20260518-203938_post_wave564_fepvirtualkeyboard_verified`
- Backup verification: `19` files, `159878023` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`

## Limits

This is saved static Ghidra evidence only. Runtime virtual-keyboard behavior, save-name side effects, concrete `CFEPVirtualKeyboard` layout, live frontend timing, BEA launch, game patching, and rebuild parity remain unproven.
