# Ghidra FEPDemoMain Correction Tranche - 2026-05-14

Status: public-safe static evidence note

This note records a serialized static Ghidra correction wave for four `CFEPDemoMain` demo-menu targets. It documents saved Ghidra metadata only. It does not include private decompile excerpts, private screenshots, copied executables, copied saves, raw runtime evidence, or private asset payloads.

## What Changed

| Address | Saved state | Public-safe evidence summary |
| --- | --- | --- |
| `0x00457ec0` | `int __cdecl CFEPDemoMain__GetMenuType(void)` | Corrected the stale hidden-`this` parameter. Static read-back shows a no-argument getter returning constant menu type `3`. |
| `0x00457ed0` | `int __stdcall CFEPDemoMain__GetActionCount(int menu_state)` | Corrected the stale extra receiver parameter. Static read-back shows a one-stack-argument helper returning constant action count `1`. |
| `0x00457ee0` | `void __fastcall CFEPDemoMain__DoAction(void * this)` | Hardened the action-dispatch comment. Static read-back shows a `this+0x8` action-state switch, `DAT_008a956c` writes for states `0` and `2`, a `CFrontEnd__SetPage` path for state `1`, and fallback into `CFEPMain__DoAction` for other states. |
| `0x00457f20` | `void __stdcall CFEPDemoMain__Update(int menu_state)` | Corrected the stale extra receiver parameter. Static read-back shows a stack-only `menu_state` helper selecting `FrontEndText` tokens `0`, `6`, and fallback token `8`. |

## Vtable / Data Context

Fresh vtable read-back shows the compact `CFEPDemoMain` slice from `0x005db7c0`: slot `3` points to `CFEPDemoMain__GetActionCount`, slot `4` points to `CFEPDemoMain__GetMenuType`, slot `5` points to `CFEPDemoMain__DoAction`, and slot `6` points to `CFEPDemoMain__Update`.

`0x005e4a78 is an extra data-table xref to CFEPDemoMain__GetMenuType`. The checked surrounding export mixes function pointers with non-function data values, so this tranche records it as additional data-table context rather than a second `CFEPDemoMain` dispatch slice.

## Source Boundary

FEPDemoMain source file was not found in the current Stuart source snapshot. Source-style names in this tranche are supported by retail vtable/action/text-token evidence, not by a direct source-file match.

## Validation

- `ApplyFEPDemoWave402.java` dry run: `updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- `ApplyFEPDemoWave402.java` apply run: `updated=4 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Metadata/decompile/xref/tag/instruction/vtable read-back is stored under ignored `subagents/`.
- Focused probe: `tools/ghidra_fepdemo_wave402_probe.py --check`.
- Self-test: `tools/ghidra_fepdemo_wave402_probe_test.py`.
- Read-back verified `4` metadata rows, `4` decompile exports, `5` xref rows, `4` tag rows, `420` instruction rows, and `80` vtable/data-context rows.
- Refreshed queue reports `6028` functions, `1555` commented functions, `4473` commentless functions, `1910` undefined signatures, and `1860` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1555/6028 = 25.80%`, strict clean-signature `1490/6028 = 24.72%`.
- The live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260514_045727_post_wave402_fepdemo_verified` with `19` files, `154798983` bytes, and `HashDiffCount=0`.

## Claim Boundary

This tranche improves saved static Ghidra comments, tags, and signatures for the `CFEPDemoMain` demo-menu cluster. It does not prove runtime frontend behavior, does not prove exact source identity, does not recover concrete structure types/locals, does not launch or patch `BEA.exe`, and does not prove rebuild parity.
