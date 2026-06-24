# Ghidra BattleEngine ResetConfiguration Signature Tranche - 2026-05-10

## Scope

This note records a saved Ghidra signature/comment hardening tranche for two already named BattleEngine reset-configuration helpers. It is public-safe static RE evidence only: no BEA launch, no debugger attach, no executable patching, no installed-game mutation, and no private decompile excerpt is included here.

## Saved Targets

| Address | Saved name | Previous signature boundary | Current saved signature boundary |
| --- | --- | --- | --- |
| `0x00412650` | `CBattleEngineJetPart__ResetConfiguration` | `void __fastcall ...(void * param_1)` | `void __thiscall ...(void * this)` |
| `0x004146b0` | `CBattleEngineWalkerPart__ResetConfiguration` | `void __fastcall ...(void * param_1)` | `void __thiscall ...(void * this)` |

## Evidence Summary

- Headless dry/apply saved two signature/comment updates with dry `updated=0 skipped=2 missing=0 bad=0` and apply `updated=2 skipped=0 missing=0 bad=0`.
- Final metadata and decompile read-back found `2/2` targets.
- Final xref export produced `4` xref rows across the targets.
- Final instruction export produced `842` instruction rows after extending the WalkerPart window far enough to include its final `RET`.
- The focused probe reports `2` targets, `0` stale signature hits, `0` comment overclaims, `4` xref hits, and return evidence for both bodies.
- The refreshed queue remains at `5868` total functions, `548` commented functions, `5320` commentless functions, `2068` undefined signatures, and now `2413` `param_N` signatures.

## Boundary

This tranche improves saved Ghidra signatures/comments only. It does not prove concrete `CBattleEngineJetPart`, `CBattleEngineWalkerPart`, or `CBattleEngine` layouts, local variable names, structure types, tags, runtime weapon/reset behavior, BEA launch behavior, game patching, or rebuild parity.
