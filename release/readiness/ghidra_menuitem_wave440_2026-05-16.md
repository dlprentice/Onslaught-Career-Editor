# Ghidra CMenuItem Base Wave440 Correction

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x004a43a0` comment correction; `0x004cf050` → `CMenuItem__Destructor_Thunk` (was `CMenuItem__Destructor`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra signature/comment/tag correction

## Summary

Wave440 hardened the base `CMenuItem` cluster after a fresh metadata/decompile/xref/instruction/vtable review. The pass preserved the existing names, corrected or confirmed signatures, added proof-boundary comments, and tagged both the full `CMenuItem` vtable at `0x005dc520` and the recovered compact/base sibling table at `0x005db440`.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004a3100` | `int __cdecl CMenuItem__IsMouseInBounds(float x0, float y0, float x1, float y1)` | Four-float wrapper for `CFrontEnd__GetCursorStateInRect`; reached by `CMenuItemRange__Render`. |
| `0x004a3120` | `int __cdecl CMenuItem__IsMouseClicked(float x0, float y0, float x1, float y1)` | Four-float wrapper for `CFrontEnd__GetClickStateInRect`; reached by `CMenuItemRange__Render`. |
| `0x004a3140` | `void * __thiscall CMenuItem__Clone(void * this)` | Compact clone body from recovered table `0x005db440`; allocates `0x1c` bytes. |
| `0x004a3190` | `short * __thiscall CMenuItem__GetText(void * this)` | Vtable slot 2 text resolver shared by both tables. |
| `0x004a3260` | `void __thiscall CMenuItem__RenderCentered(void * this, float x, float y, int alpha)` | Recovered compact/base render slot; forwards text and default `0xffffffff` color to `CMenuItem__Render`. |
| `0x004a3290` | `void __thiscall CMenuItem__RenderWithColor(void * this, float x, float y, int alpha, int argb_color)` | Custom-color render wrapper. |
| `0x004a32c0` | `void __thiscall CMenuItem__Render(void * this, float x, float y, int alpha, int argb_color, short * text)` | Shared text render body with optional secondary text/id path and `CDXEngine__DrawTextScaledWithShadow`. |
| `0x004a3420` | `int __thiscall CMenuItem__GetTextWidth(void * this)` | Recovered compact/base width slot; returns measured text x extent. |
| `0x004a3450` | `void * __thiscall CMenuItem__Clone(void * this)` | Full `0x38`-byte clone body from table `0x005dc520`; transfers active-reader linkage via `CGenericActiveReader__SetReader`. |
| `0x004a3510` | `void * __thiscall CMenuItem__Init(void * this, int text_id, int item_id, float value_scale, void * owner, int max_value, byte notify_on_change)` | Initializes default color `0xffd6d6d6`, owner monitor linkage, notify flag, max value, and current/committed value fields. |
| `0x004a3610` | `void * __thiscall CMenuItem__ScalarDestructor(void * this, byte flags)` | Scalar deleting destructor wrapper; calls `CMenuItem__Destructor` and optionally frees. |
| `0x004a3630` | `void * __thiscall CMenuItem__InitWithIcon(void * this, int icon_or_text_id, int item_id, float value_scale, void * owner, int max_value, byte notify_on_change)` | Alternate initializer storing the first id at `+0x18` while sharing the same owner/value setup. |
| `0x004a3730` | `void __thiscall CMenuItem__Destructor(void * this)` | Releases resource counters and removes owner monitor linkage via `CSPtrSet__Remove`. |
| `0x004a37c0` | `void __thiscall CMenuItem__RenderValueBar(void * this, float x, float y, int interactive)` | Full-table value-bar renderer and mouse hotspot mapper for buttons `0x36`/`0x37`. |
| `0x004a43a0` | `void __thiscall CMenuItem__ButtonPressed(void * this, int from_controller, int button)` | Handles confirm `0x2c`, decrement `0x36`, increment `0x37`, clamping, callbacks, and optional owner notification. |
| `0x004a4450` | `int __thiscall CMenuItem__GetWidth(void * this)` | Full-table width slot; returns text width plus `0x6a` padding. |
| `0x004a44c0` | `void __thiscall CMenuItem__SetUserData(void * this, void * user_data)` | One-store setter for the `+0x20` value/resource field. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| Headless `ApplyMenuItemWave440.java` dry/apply/verify | PASS | Dry found `17` targets; apply reported `updated=17`, `missing=0`, `bad=0`; verify dry reported `updated=0`, `skipped=17`, `missing=0`, `bad=0`. |
| Post-apply metadata/tag/xref/instruction/vtable/decompile read-back | PASS | Verified `17` metadata rows, `17` tag rows, `123` xref rows, `1513` instruction rows, `64` vtable-slot rows, and `17` target decompile exports. |
| `py -3 -m py_compile tools\ghidra_menuitem_wave440_probe.py tools\ghidra_menuitem_wave440_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_menuitem_wave440_probe_test.py` | PASS | Focused tests passed `4/4`. |
| `cmd.exe /c npm run test:ghidra-menuitem-wave440` | PASS | Focused probe returned `PASS` for all `17` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6055` total functions, `1848` commented functions, `4207` commentless functions, `1775` undefined signatures, and `1740` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6055`
- Commented function objects: `1848`
- Commentless function objects: `4207`
- `undefined` signatures: `1775`
- Signatures still using `param_N`: `1740`

Telemetry-only proxies are comment-backed `1848/6055 = 30.52%` and strict clean-signature `1786/6055 = 29.50%`. These are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime frontend rendering/input behavior; exact concrete `CMenuItem`/compact sibling layouts; exact field names/types; exact source method identity because the current local Stuart source snapshot has no `MenuItem.cpp` body; BEA launch behavior; game patching; or source-to-retail rebuild parity.
