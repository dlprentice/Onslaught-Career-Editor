# Ghidra Cockpit / Compass Signature Correction - 2026-05-09

## Summary

This wave reparsed a focused saved-Ghidra cockpit/compass tranche after vtable, decompile, xref, and instruction evidence showed several labels and signatures needed hardening. A clean headless dry/apply pass updated six saved names/signatures/comments, then fresh metadata, decompile, xref, instruction, and vtable type read-back verified the result.

## Corrected Targets

| Address | Saved name after correction | Evidence boundary |
| --- | --- | --- |
| `0x00405970` | `CDXCockpit__scalar_deleting_dtor` | CDXCockpit vtable evidence and wrapper shape show a scalar-deleting destructor that calls `CDXCockpit__dtor_base_thunk`, checks the delete flag, optionally calls `OID__FreeObject`, and returns `this`. |
| `0x00405990` | `CDXCockpit__dtor_base_thunk` | Instruction/xref evidence shows a jump thunk into `CCockpit__dtor_base`, reached from the CDXCockpit scalar-deleting destructor. |
| `0x00406040` | `CDXCompass__GetTrackedPositionX` | Decompile evidence reads a tracked pointer from `context +0x4b0` and returns the `+0x1c` value through the FPU; xrefs include compass render and dynamic overlay update paths. |
| `0x0040c630` | `CDXCompass__GetTrackedPositionY` | Decompile evidence reads a tracked pointer from `context +0x4b0` and returns the `+0x20` value through the FPU; xrefs include compass render and dynamic overlay update paths. |
| `0x00424710` | `CCockpit__scalar_deleting_dtor` | CCockpit vtable evidence and wrapper shape show a scalar-deleting destructor that calls `CCockpit__dtor_base`, checks the delete flag, optionally calls `OID__FreeObject`, and returns `this`. |
| `0x00424730` | `CCockpit__dtor_base` | Decompile/instruction evidence resets CCockpit vtable slots `0x005d9524` and `0x005d94ac`, releases an owned `+0x8c` object through a vcall when present, and calls `CMonitor__Shutdown`. |

## Validation

- Headless dry/apply: `updated=0 skipped=6 missing=0 bad=0`, then `updated=6 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `6/6` targets.
- Fresh xref read-back: `12` rows.
- Fresh instruction read-back: `510` rows.
- Vtable type read-back: rows resolving `0x005d88b0` to `CDXCockpit`, and `0x005d9524` / `0x005d94ac` to `CCockpit`.
- Focused probe: `cmd.exe /c npm run test:ghidra-cockpit-compass-signature-correction` passed with `0` stale name hits and `0` `param_N` signature hits.
- Refreshed queue probe: `5866` functions, `447` commented functions, `5419` commentless functions, `2076` undefined signatures, and `2504` `param_N` signatures.

## Non-Claims

This is saved Ghidra name/signature/comment refinement only. It does not prove exact Stuart-source method identities, concrete `CDXCockpit` / `CCockpit` / `CDXCompass` layouts, tags, local variable names, structure types, runtime cockpit or compass behavior, BEA launch behavior, game patching, or rebuild parity.
