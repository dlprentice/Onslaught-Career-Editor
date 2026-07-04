# Ghidra CMenuItemRange / CMenuItemRangeVariant Wave442 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra signature/comment/tag correction

## Summary

Wave442 hardened the `CMenuItemRange` and `CMenuItemRangeVariant` cluster after fresh metadata/decompile/xref/instruction/vtable review. The pass preserved the existing names, corrected formerly `undefined` signatures, added proof-boundary comments, and tagged the confirmed range tables at `0x005dc650` and `0x005dc664`.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004a45c0` | `void * __thiscall CMenuItemRange__Init(void * this, short * title_text, float x, float y, int panel_flag, int panel_arg)` | Constructor-style range initializer for vtable `0x005dc650`; initializes the linked set and stores render/layout fields. |
| `0x004a4610` | `void * __thiscall CMenuItemRange__ScalarDestructor(void * this, byte flags)` | Scalar deleting destructor; calls range destructor and frees when flags bit 0 is set. |
| `0x004a4630` | `void __thiscall CMenuItemRange__ResetIterator(void * this)` | Clears selected index and walks children through vtable+`0x30`. |
| `0x004a4670` | `void __thiscall CMenuItemRange__AddItem(void * this, void * item)` | Appends an item through `CSPtrSet__AddToTail` at `this+0x08`. |
| `0x004a4680` | `void __thiscall CMenuItemRange__Destructor(void * this)` | Destroys child items, clears the linked set, and releases cached blank texture state. |
| `0x004a4730` | `void __thiscall CMenuItemRange__LoadTexture(void * this)` | Loads `FrontEnd_v2/FE_Blank.tga` and walks children through texture/load callback vtable+`0x34`. |
| `0x004a4790` | `void __thiscall CMenuItemRange__SelectNext(void * this)` | Advances selection, wraps only for lists with at least three entries, skips disabled children, and plays frontend sound on success. |
| `0x004a4810` | `int __thiscall CMenuItemRange__Render(void * this, void * binding_context)` | Main range renderer; handles row-height layout, optional title/panel rendering, lazy texture load, mouse selection, and deferred dropdown processing. |
| `0x004a4cd0` | `int __thiscall CMenuItemRange__ProcessInput(void * this, int from_controller, int button, int context)` | Vtable slot 2 input gate; forwards input to the selected child only when child vtable+`0x20` reports active. |
| `0x004a4d20` | `void __thiscall CMenuItemRange__HandleKeyPress(void * this, int from_controller, int button, int context)` | Vtable slot 1 button handler; handles up/down selection and forwards other buttons to selected child vtable+`0x04`. |
| `0x004a4dd0` | `void __thiscall CMenuItemRange__SetItemEnabled(void * this, int item_id, int enabled)` | Walks children and writes enabled state to child offset `+0x10` when child item id at `+0x08` matches. |
| `0x004a4e10` | `void * __thiscall CMenuItemRangeVariant__Init(void * this, short * title_text, float x, float y, int panel_flag, int panel_arg)` | Variant initializer for vtable `0x005dc664`; mirrors range setup while selecting the variant table. |
| `0x004a4e60` | `void * __thiscall CMenuItemRangeVariant__ScalarDestructor(void * this, byte flags)` | Variant scalar deleting destructor; calls variant destructor and frees when flags bit 0 is set. |
| `0x004a4e80` | `void __thiscall CMenuItemRangeVariant__Destructor(void * this)` | Variant destructor with the same linked-child teardown and cached texture release shape as range destructor. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| Headless `ApplyMenuItemRangeWave442.java` dry/apply/verify | PASS | Dry found `14` targets; apply reported `updated=14`, `missing=0`, `bad=0`; verify dry reported `updated=0`, `skipped=14`, `missing=0`, `bad=0`. |
| Post-apply metadata/tag/xref/vtable/decompile read-back | PASS | Verified `14` metadata rows, `14` tag rows, `71` xref rows, `64` vtable-slot rows, and `14` target decompile exports. |
| `py -3 -m py_compile tools\ghidra_menuitem_range_wave442_probe.py tools\ghidra_menuitem_range_wave442_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_menuitem_range_wave442_probe_test.py` | PASS | Focused tests passed `4/4`. |
| `cmd.exe /c npm run test:ghidra-menuitem-range-wave442` | PASS | Focused probe returned `PASS` for all `14` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6055` total functions, `1876` commented functions, `4179` commentless functions, `1753` undefined signatures, and `1740` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6055`
- Commented function objects: `1876`
- Commentless function objects: `4179`
- `undefined` signatures: `1753`
- Signatures still using `param_N`: `1740`

Telemetry-only proxies are comment-backed `1876/6055 = 30.98%` and strict clean-signature `1814/6055 = 29.96%`. These are not certification and are not completion gates.

## Backup

The actual saved Ghidra project was backed up after read-back at `[maintainer-local-ghidra-backup-root]\BEA_20260516-082948_post_wave442_menuitem_range_verified`. The backup comparison reported `19` files, `156175239` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Not Proven

This wave does not prove runtime frontend range/variant behavior; exact concrete layouts; exact field names/types; exact source method identity because the current local Stuart source snapshot has no `MenuItem.cpp` body; BEA launch behavior; game patching; or source-to-retail rebuild parity.
