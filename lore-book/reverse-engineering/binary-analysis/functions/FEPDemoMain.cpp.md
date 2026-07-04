# FEPDemoMain.cpp Functions

> Source File: FEPDemoMain.cpp | Binary: BEA.exe
> Source boundary: FEPDemoMain source file was not found in the current Stuart source snapshot.

## Overview

`CFEPDemoMain` is a compact retail frontend demo-menu page cluster. Static read-back ties it to a small vtable slice, one action dispatcher, and frontend text-token selection.

Source-style names below are supported by retail vtable/action/text-token evidence, not by a direct source-file match. This page documents saved static Ghidra metadata only.

Wave956 (`cfepdemo-main-review-wave956`) re-reviewed the four-target `CFEPDemoMain` dispatch slice read-only after static export-contract closure. Fresh exports verified 11 metadata rows, 11 tag rows, 220 xref rows, 404 instruction rows, 11 decompile rows, and 20 vtable/data-table rows. No mutation was needed; anchor phrase: no mutation. The Wave402 signatures still hold, vtable `0x005db7c0` still maps slots 3 through 6 to `0x00457ed0 CFEPDemoMain__GetActionCount`, `0x00457ec0 CFEPDemoMain__GetMenuType`, `0x00457ee0 CFEPDemoMain__DoAction`, and `0x00457f20 CFEPDemoMain__Update`, and data-table pointer `0x005e4a78` remains mixed context rather than a second dispatch slice. Wave911 focused re-audit progress after Wave956 is `290/1408 = 20.60%`; static closure remains `6151/6151 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-105733_post_wave956_cfepdemo_main_review_verified`. Runtime demo-menu behavior, runtime frontend navigation/rendering behavior, concrete `CFEPDemoMain` layout names, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

## CFEPDemoMain Dispatch Context

Fresh Wave956 vtable read-back preserves the compact `CFEPDemoMain` slice from `0x005db7c0`.

| Offset | Address | Name | Purpose |
| --- | --- | --- | --- |
| `+0x00` | `0x004644d0` | `CFEPMain__TransitionNotification` | Inherited/shared transition notification context. |
| `+0x04` | `0x00464520` | `CFEPMain__ActiveNotification` | Inherited/shared active notification context. |
| `+0x08` | `0x00459990` | `CFrontEndPage__DeActiveNotification` | Base/embedded frontend-page helper. |
| `+0x0c` | `0x00457ed0` | `CFEPDemoMain__GetActionCount` | Constant demo-menu action-count getter. |
| `+0x10` | `0x00457ec0` | `CFEPDemoMain__GetMenuType` | Constant demo-menu type getter. |
| `+0x14` | `0x00457ee0` | `CFEPDemoMain__DoAction` | Demo action dispatcher. |
| `+0x18` | `0x00457f20` | `CFEPDemoMain__Update` | Demo text-token update helper. |

The extra xref at `0x005e4a78` points to `CFEPDemoMain__GetMenuType`, but the surrounding Wave956 export still mixes function pointers and non-function data values. Treat it as additional data-table context, not as a full `CFEPDemoMain` dispatch slice.

## Functions

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x00457ec0` | `int __cdecl CFEPDemoMain__GetMenuType(void)` | No-argument getter returning constant menu type `3`. |
| `0x00457ed0` | `int __stdcall CFEPDemoMain__GetActionCount(int menu_state)` | One-stack-argument helper returning constant action count `1`. |
| `0x00457ee0` | `void __fastcall CFEPDemoMain__DoAction(void * this)` | Reads `this+0x8` action state, writes `DAT_008a956c` for states `0` and `2`, calls `CFrontEnd__SetPage` for state `1`, and falls back to `CFEPMain__DoAction` otherwise. |
| `0x00457f20` | `void __stdcall CFEPDemoMain__Update(int menu_state)` | Stack-only menu-state mapping to `FrontEndText` token lookups `0`, `6`, and fallback `8`. |

## Wave956 Re-Audit Validation

Wave956 rechecked the four rows above without Ghidra mutation:

- Fresh exports: `11` metadata rows, `11` tag rows, `220` xref rows, `404` instruction rows, `11` decompile rows, and `20` vtable/data-table rows.
- `0x00457ec0 CFEPDemoMain__GetMenuType` still decompiles to `return 3`.
- `0x00457ed0 CFEPDemoMain__GetActionCount` still decompiles to `return 1`.
- `0x00457ee0 CFEPDemoMain__DoAction` still writes `DAT_008a956c`, calls `CFrontEnd__SetPage(&DAT_0089d758, 0x11, 0x46)`, and falls back to `CFEPMain__DoAction`.
- `0x00457f20 CFEPDemoMain__Update` still reaches `FrontEndText__GetLocalizedOrFallbackTextByToken` for tokens `0`, `8`, and `6`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-105733_post_wave956_cfepdemo_main_review_verified`, `19` files, `173542279` bytes, `DiffCount=0`.

## Wave402 Validation

Wave402 saved and read back Ghidra metadata for the four targets above:

- `ApplyFEPDemoWave402.java` dry run: `updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- `ApplyFEPDemoWave402.java` apply run: `updated=4 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back verified `4` metadata rows, `4` decompile exports, `5` xref rows, `4` tag rows, `420` instruction rows, and `80` vtable/data-context rows.
- Focused probe: `tools/ghidra_fepdemo_wave402_probe.py --check` passed.

This is saved static Ghidra name/signature/comment/tag refinement only. It does not prove runtime frontend behavior, exact source identity, concrete `CFEPDemoMain` layout, local variable names, structure types, BEA launch behavior, game patching, or rebuild parity.
