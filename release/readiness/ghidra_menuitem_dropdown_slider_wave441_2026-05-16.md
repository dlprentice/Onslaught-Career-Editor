# Ghidra CMenuItemDropdown / CMenuItemSlider Wave441 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra signature/comment/tag correction

## Summary

Wave441 hardened the `CMenuItemDropdown` and `CMenuItemSlider` cluster after fresh metadata/decompile/xref/instruction/vtable review. The pass preserved the existing names, corrected formerly `undefined` signatures, added proof-boundary comments, and tagged dropdown vtables `0x005dc578` / `0x005dc5c4` plus slider vtable `0x005dc610`.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004a3b10` | `void * __thiscall CMenuItemDropdown__Init(void * this, int text_id, int item_id, byte defer_commit)` | Constructor-style dropdown initializer for vtable `0x005dc578`; clears compact base fields, default color, expanded state, and deferred-commit flag. |
| `0x004a3b50` | `void __thiscall CMenuItemDropdown__UpdateSelection(void * this)` | Vtable slot 12 selection sync helper; copies vtable+`0x3c` result into committed/current fields at `+0x1c`/`+0x20`. |
| `0x004a3b60` | `void * __thiscall CMenuItemDropdown__InitVariant(void * this, int text_id, int item_id, byte defer_commit)` | Variant initializer for vtable `0x005dc5c4`; table includes `Localization__GetYesNoString`. |
| `0x004a3ba0` | `void __cdecl CMenuItemDropdown__ClearPending(void)` | Clears deferred dropdown render global `DAT_0070486c`; called by `CMenuItemRange__Render` before traversal. |
| `0x004a3bb0` | `void __cdecl CMenuItemDropdown__ProcessPending(void)` | Consumes queued dropdown `this/x/y` globals after traversal and calls render with queued-pass flag `1`. |
| `0x004a3be0` | `void __thiscall CMenuItemDropdown__RenderOrQueueDeferred(void * this, float x, float y, int interactive)` | Vtable slot 4 render entry; queues interactive popup render when no dropdown is pending, otherwise renders directly. |
| `0x004a3c30` | `void __thiscall CMenuItemDropdown__Render(void * this, float x, float y, int queued_pass)` | Dropdown body renderer with collapsed/expanded paths, text measurement, hover/click rect helpers, and optional immediate commit. |
| `0x004a40e0` | `byte __thiscall CMenuItemDropdown__IsExpanded(void * this)` | Vtable slots 8/9 state query; returns byte field `+0x24`. |
| `0x004a40f0` | `void __thiscall CMenuItemDropdown__CommitSelection(void * this)` | Vtable slot 11 commit helper; calls vtable+`0x38` when current selection differs from committed selection. |
| `0x004a4110` | `void __thiscall CMenuItemDropdown__ButtonPressed(void * this, int from_controller, int button)` | Vtable slot 1 input handler for up/down/select/cancel and deferred/immediate commit behavior. |
| `0x004a42f0` | `bool __thiscall CMenuItemDropdown__HasPendingSelectionChange(void * this)` | Vtable slot 10 deferred-commit query; true when `+0x25` is set and `+0x1c` differs from `+0x20`. |
| `0x004a4250` | `void * __thiscall CMenuItemSlider__Init(void * this, void * linked_range)` | Slider initializer for vtable `0x005dc610`; stores linked range/list pointer at `+0x1c`. |
| `0x004a4290` | `void __thiscall CMenuItemSlider__ButtonPressed(void * this, int from_controller, int button)` | Vtable slot 1 select-button handler; walks linked range/list and calls child callback slot `0x2c`. |
| `0x004a4310` | `void __thiscall CMenuItemSlider__Render(void * this, float x, float y, int alpha)` | Vtable slot 4 render override; computes optional pulsed color and forwards to `CMenuItem__Render`. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| Headless `ApplyMenuItemDropdownSliderWave441.java` dry/apply/verify | PASS | Dry found `14` targets; apply reported `updated=14`, `missing=0`, `bad=0`; verify dry reported `updated=0`, `skipped=14`, `missing=0`, `bad=0`. |
| Post-apply metadata/tag/xref/instruction/vtable/decompile read-back | PASS | Verified `14` metadata rows, `14` tag rows, `174` xref rows, `1526` instruction rows, `96` vtable-slot rows, and `14` target decompile exports. |
| `py -3 -m py_compile tools\ghidra_menuitem_dropdown_slider_wave441_probe.py tools\ghidra_menuitem_dropdown_slider_wave441_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_menuitem_dropdown_slider_wave441_probe_test.py` | PASS | Focused tests passed `4/4`. |
| `cmd.exe /c npm run test:ghidra-menuitem-dropdown-slider-wave441` | PASS | Focused probe returned `PASS` for all `14` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6055` total functions, `1862` commented functions, `4193` commentless functions, `1767` undefined signatures, and `1740` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6055`
- Commented function objects: `1862`
- Commentless function objects: `4193`
- `undefined` signatures: `1767`
- Signatures still using `param_N`: `1740`

Telemetry-only proxies are comment-backed `1862/6055 = 30.75%` and strict clean-signature `1800/6055 = 29.73%`. These are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime frontend dropdown/slider behavior; exact concrete layouts; exact field names/types; exact source method identity because the current local Stuart source snapshot has no `MenuItem.cpp` body; BEA launch behavior; game patching; or source-to-retail rebuild parity.
