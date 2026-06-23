# Ghidra Monitor / Ground / Tracked-List Signature Tranche - 2026-05-10

## Summary

This wave continued the saved-Ghidra static re-audit by hardening eight monitor, unit, ground-probe, and tracked-list-adjacent functions from the signature queue. A serial headless dry/apply pass saved signatures and proof-boundary comments, followed by fresh metadata, decompile, xref, instruction, and focused-probe read-back.

## Corrected Targets

| Address | Saved signature after correction | Evidence boundary |
| --- | --- | --- |
| `0x0040e1b0` | `void __thiscall VFuncSlot_00_0040e1b0(void * this, void * sourceObject)` | Body copies/clones source-object fields into `this`, including transform/matrix-style blocks and state through `+0x3b0`; xrefs include spawner and squad contexts. Exact owner/source identity remains unresolved. |
| `0x0040e840` | `void __fastcall CMonitor__ToggleAttachedObjectFlag300(void * monitor)` | Reads the attached object pointer at `+0x528` and toggles the attached object's `+0x12c` integer flag. |
| `0x0040e860` | `void __thiscall CGeneralVolume__OffsetPointByForwardScaled(void * this, void * point, void * unusedContext)` | Instruction evidence preserves `ret 0x8`; decompile read-back offsets `point` by a forward vector from vcall `+0x6c` scaled by `_DAT_005d85ec`, with optional attached-object `+0x528` context. |
| `0x0040e8e0` | `float __fastcall CUnit__IsNearGroundByTerrainProbe(void * unit)` | Calls `CStaticShadows__SampleShadowHeightBilinear` using unit position context and compares the sampled height against unit `+0x24`. |
| `0x0040e910` | `float __fastcall CUnit__GetGroundedControlFactor(void * unit)` | Checks vtable `+0x10c` and `HeightDelta__Below015_D4`, then returns one of two global control factors. |
| `0x0040e940` | `void __fastcall CMonitor__UpdateTrackedList_59C(void * monitor)` | Walks tracked list `+0x1d4`, uses `+0x59c` / `+0x614` sample/effect context, dispatches selector `0x1a`, and marks `+0x1e4` active. |
| `0x0040eb50` | `void __fastcall CMonitor__FlushTrackedList_1D4(void * monitor)` | Flushes tracked list `+0x1d4` when `+0x1e4` is set, finalizes linked-unit state, touches `+0x59c`, and clears `+0x1e4`. |
| `0x0040ebf0` | `void __fastcall CMonitor__UpdateTrackedList_620(void * monitor)` | Walks secondary tracked list `+0x620`, gates on `+0x630` / `+0x634`, uses `+0x618` / `+0x61c`, and dispatches selector `0x17`. |

## Validation

- Headless `ApplyMonitorGroundTrackedListSignatureTranche.java` dry/apply: `updated=0 skipped=8 missing=0 bad=0`, then `updated=8 skipped=0 missing=0 bad=0`; save succeeded.
- Fresh metadata read-back: `8/8` targets with expected saved signatures and proof-boundary comments.
- Fresh decompile read-back: `8/8` target decompile files with expected behavior tokens.
- Fresh xref read-back: `16` checked xref/data rows, with focused xref evidence for all eight targets.
- Fresh instruction read-back: `904` instruction rows, with return evidence for all eight targets in the focused probe.
- Focused probe: `cmd.exe /c npm run test:ghidra-monitor-ground-tracked-list-signature-tranche` passed with `8` targets, `0` `param_N` signature hits, `0` comment overclaims, `8` return-evidence hits, and `8` xref-evidence hits.
- Refreshed queue probe: `5868` functions, `521` commented functions, `5347` commentless functions, `2069` undefined signatures, and `2429` `param_N` signatures.

## Non-Claims

This is saved Ghidra signature/comment refinement only. It does not prove exact Stuart-source method identities, concrete `CMonitor` / `CUnit` / `CGeneralVolume` layouts, tracked-list node structures, tags, local variable names, runtime ground/monitor/effect behavior, runtime cloak/fire behavior, BEA launch behavior, game patching, or rebuild parity.

## Privacy / Release Safety

This report stores repo-relative filenames, public addresses already present in repo evidence, current function names, saved signatures, command summaries, row counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, or raw Ghidra mutation logs.
