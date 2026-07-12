# Ghidra Monitor / Gameplay Signature Tranche - 2026-05-09

> **Owner/name supersession (2026-07-12):** this file remains the historical
> saved-signature/read-back record. Current read-only RTTI, vtable, caller,
> object-layout, and source-order evidence identifies `0x004081c0` as
> `CBattleEngine__Move`, not `CMonitor__Process`. See the
> [current movement crosswalk](../../reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md).

## Summary

This wave reparsed six monitor/gameplay-adjacent functions from the current static re-audit queue after fresh metadata, decompile, xref, and instruction exports showed commentless `param_N` signature debt. A serial headless dry/apply pass saved corrected signatures and proof-boundary comments, followed by fresh read-back and a focused probe.

## Corrected Targets

| Address | Saved signature after correction | Evidence boundary |
| --- | --- | --- |
| `0x00407940` | `void __thiscall CGeneralVolume__RandomizeOffsets4B8_4C0(void * this, float offsetRange)` | Instruction evidence shows `ret 0x4`; decompile read-back randomizes the `+0x4b8`, `+0x4bc`, and `+0x4c0` offset fields, resets `+0x4c4`, and conditionally reaches linked/front-end context. This corrects a stale two-stack-argument view but does not prove concrete `CGeneralVolume` layout. |
| `0x00407a50` | `void __fastcall CMonitor__UpdateCameraVectorsAndInput(void * monitor)` | Decompile read-back copies orientation angles from `+0x114`, applies grounded/height checks, calls mouse-look and orientation helpers, and decays camera-offset noise. |
| `0x004080f0` | `bool __fastcall CGame__IsWalkerGroundedOrCollision(void * battleEngine)` | Decompile read-back returns a boolean gate for mode `+0x260` plus collision/height-delta checks. The current owner/source-method identity remains provisional. |
| `0x00408120` | `bool __fastcall CUnitAI__IsState2AndBelowHeightDeltaThreshold_00408120(void * unitAi)` | Decompile read-back returns a boolean state/timestamp predicate using mode `+0x260`, timestamp `+0xcc`, and a global threshold. |
| `0x00408150` | `void __fastcall CUnit__ProcessStateSwapAndDeathChecks(void * unit)` | Decompile read-back swaps part readers, checks death flag `+0x2c & 4`, dispatches pickup/death paths, and resets the `+0xd0` timestamp-like field. |
| `0x004081c0` | `void __fastcall CMonitor__Process(void * monitor)` | Decompile read-back covers active-reader expiry, tracked-list updates, `0x5d8`/`0x5dc` interpolation, vibration, cloak/fade timer decay, actor movement, camera update, and target/effect updates. This is cloak/fade context, not runtime cloak activation or fire-while-cloaked proof. |

## Validation

- Headless dry/apply: `updated=0 skipped=6 missing=0 bad=0`, then `updated=6 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `6/6` targets.
- Fresh xref read-back: `10` rows.
- Fresh instruction read-back: `2562` rows, including `4` checked return-evidence hits.
- Focused probe: `cmd.exe /c npm run test:ghidra-monitor-gameplay-signature-tranche` passed with `0` `param_N` signature hits and `0` overclaim hits.
- Refreshed queue probe: `5866` functions, `459` commented functions, `5407` commentless functions, `2076` undefined signatures, and `2492` `param_N` signatures.

## Non-Claims

This is saved Ghidra signature/comment refinement only. It does not prove exact Stuart-source method identities, concrete `CGeneralVolume` / `CMonitor` / `CUnit` / `CUnitAI` layouts, local variable names, structure types, tags, runtime movement/camera/cloak behavior, cloak activation, fire-while-cloaked behavior, BEA launch behavior, game patching, or rebuild parity.
