# Ghidra Linked / Monitor Signature Tranche - 2026-05-09

## Summary

This wave reparsed six linked-list, monitor, sound, unit-transform, and line-constructor-adjacent functions from the current static re-audit queue. Fresh metadata, decompile, xref, instruction, and vtable/RTTI exports showed useful behavior evidence plus stale signature debt. A serial headless dry/apply pass saved corrected signatures, proof-boundary comments, and one owner correction, followed by fresh read-back and a focused probe.

## Corrected Targets

| Address | Saved signature after correction | Evidence boundary |
| --- | --- | --- |
| `0x00409760` | `void * __fastcall LinkedPtrCursor__MoveFirstAndGet(void * cursor)` | Decompile read-back moves an iterator/cursor to the first linked node through the list pointer at `+0x4` and returns the node item pointer or null. Exact list layout, source identity, and runtime behavior remain unproven. |
| `0x00409780` | `void * __fastcall LinkedPtrCursor__MoveNextAndGet(void * cursor)` | Decompile read-back advances the current linked node through `+0x4` and returns the node item pointer or null. Exact list layout, source identity, and runtime behavior remain unproven. |
| `0x004097a0` | `void __thiscall CUnit__PushTransformHistoryAndSetCurrent(void * this, void * transform)` | Instruction evidence shows `ret 0x4`; decompile read-back copies transform-history rows and refreshes a timestamp-like `+0xac` field from `DAT_00672fd0` when enabled. Concrete `CUnit` layout and runtime transform behavior remain unproven. |
| `0x00409880` | `int __fastcall CMonitor__GetLastValidRangeStep100(void * monitor)` | Decompile read-back scans five 100-step slots from monitor `+0xa4` and returns the last slot whose entry is not `-1`. Concrete monitor/range layout remains unproven. |
| `0x004098e0` | `void __thiscall CLine__ctor_copy(void * this, void * sourceLine)` | Owner correction from stale `CGeneralVolume__ctor_like_004098e0`: decompile/vtable read-back shows a `CGeneralVolume` base vtable write followed by a `CLine` vtable write while copying three 16-byte rows from `sourceLine`; vtable/RTTI export confirms both `CGeneralVolume` and `CLine`. Exact constructor identity and concrete layouts remain unproven. |
| `0x00409950` | `void __fastcall CMonitor__UpdateSoundEventPlaybackForReader(void * monitor)` | Decompile read-back updates engine/health/energy/lock/walk sound chains, active-reader state at `+0x5e8`, and walk-sound counters. Runtime audio behavior and exact source identity remain unproven. |

## Validation

- Headless dry/apply: `updated=0 skipped=6 missing=0 bad=0`, then `updated=6 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `6/6` targets.
- Fresh xref read-back: `60` rows.
- Fresh instruction read-back: `4278` rows, including `6` checked return-evidence hits.
- Vtable/RTTI read-back: `2` rows covering `CGeneralVolume` and `CLine`.
- Focused probe: `cmd.exe /c npm run test:ghidra-linked-monitor-signature-tranche` passed with `0` `param_N` signature hits and `0` overclaim hits.
- Refreshed queue probe: `5866` functions, `465` commented functions, `5401` commentless functions, `2076` undefined signatures, and `2486` `param_N` signatures.

## Non-Claims

This is saved Ghidra signature/comment refinement plus one owner-label correction only. It does not prove exact Stuart-source method identities, concrete `CMonitor` / `CUnit` / `CLine` / `CGeneralVolume` layouts, local variable names, structure types, tags, runtime sound behavior, runtime transform behavior, BEA launch behavior, game patching, or rebuild parity.
