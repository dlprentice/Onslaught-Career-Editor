# Ghidra GeneralVolume Active-Reader Signature Tranche - 2026-05-09

## Summary

This wave reparsed the already named `CGeneralVolume__ResetAndSetActiveReader` path after the static re-audit queue selected `0x0040c720` as the next nearby target. Fresh metadata, decompile, xref, and instruction exports showed the behavior label was still useful, but the saved signature shape was not solid: `0x0040c720` returned with `ret 0x4` while the decompiler still exposed stale `param_N` debt, and its callee `0x00402020` also returned with `ret 0x4` despite being saved as a no-stack-argument `__fastcall`.

A serial headless dry/apply pass corrected both saved signatures and proof-boundary comments, followed by fresh metadata, decompile, xref, and instruction read-back plus a focused probe.

## Corrected Targets

| Address | Saved signature after correction | Evidence boundary |
| --- | --- | --- |
| `0x00402020` | `void __thiscall CGeneralVolume__ResetCooldownTimestamp(void * this, void * activeReaderTarget)` | Instruction read-back shows `ret 0x4`; body stores `DAT_00672fd0` into `this+0xd4` and ignores the stack argument. Exact source identity, layout, tags, locals, and runtime behavior remain unproven. |
| `0x0040c720` | `void __thiscall CGeneralVolume__ResetAndSetActiveReader(void * this, void * activeReaderTarget)` | Body calls `CBattleEngine__SwapPrimarySecondaryPartReadersForState`, binds `this+0x264` through `CGenericActiveReader__SetReader`, then calls `CGeneralVolume__ResetCooldownTimestamp` with the same target. Exact source identity, layout, tags, locals, and runtime behavior remain unproven. |

## Validation

- Focused TDD start: `py -3 tools\ghidra_general_volume_active_reader_signature_tranche_probe_test.py` failed before implementation with missing probe module.
- Focused tests: `py -3 tools\ghidra_general_volume_active_reader_signature_tranche_probe_test.py` passed `2/2`.
- Headless dry/apply: `updated=0 skipped=2 missing=0 bad=0`, then `updated=2 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `2/2` targets with corrected signatures and comments.
- Fresh xref read-back: `43` rows.
- Fresh instruction read-back: `178` rows, including `2` checked `ret 0x4` evidence rows.
- Focused probe: `cmd.exe /c npm run test:ghidra-general-volume-active-reader-signature-tranche` passed with `0` `param_N` signature hits and `0` overclaim hits.
- Refreshed queue probe: `5866` functions, `5365` commentless functions, `2076` undefined signatures, and `2450` `param_N` signatures.

## Non-Claims

This is saved Ghidra signature/comment refinement only. It does not prove exact Stuart-source identity for either GeneralVolume helper, concrete `CGeneralVolume` layout, local variable names, structure types, Ghidra tags, runtime active-reader behavior, BEA launch behavior, game patching, or rebuild parity.
