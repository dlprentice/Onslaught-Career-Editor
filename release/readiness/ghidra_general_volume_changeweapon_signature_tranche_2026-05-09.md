# Ghidra GeneralVolume / ChangeWeapon Signature Tranche - 2026-05-09

## Summary

This wave reparsed six top-of-queue `CGeneralVolume` / `CBattleEngine__ChangeWeapon` functions from the saved Ghidra static re-audit queue. Fresh metadata, decompile, xref, and instruction exports showed stale `param_N` signature debt on already named functions. A serial headless dry/apply pass saved corrected pointer parameter names and proof-boundary comments, followed by fresh read-back and a focused probe.

## Corrected Targets

| Address | Saved signature after correction | Evidence boundary |
| --- | --- | --- |
| `0x00409e80` | `void __fastcall CGeneralVolume__SetParam2CC_ToOne(void * generalVolume)` | Decompile read-back writes float `1.0` to `generalVolume +0x2cc`; current callers include `CCockpit__CycleToNextUsableWeapon` and `CGeneralVolume__SelectNextEnabledEntry`. Exact layout and runtime behavior remain unproven. |
| `0x00409e90` | `void __fastcall CGeneralVolume__SetParam2CC_ToOne_IfCurrentState1(void * generalVolume)` | Decompile read-back resolves a related state through the `+0x1d4` vcall and writes float `1.0` to `+0x2cc` only when nested state `+0x34` equals `1`. Exact source identity remains unproven. |
| `0x00409ec0` | `void __fastcall CGeneralVolume__SetParam2CC_ToPoint4_IfCurrentState1(void * generalVolume)` | Decompile read-back matches the same state gate and writes float `0.4` to `+0x2cc`. Exact source identity remains unproven. |
| `0x00409ef0` | `void __fastcall CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0(void * generalVolume)` | Decompile read-back dispatches by mode `+0x260` to a mode-2 current-entry progress refresh at `+0x578` or mode-3 burst-progress/spawn path at `+0x57c`. |
| `0x00409f20` | `void __fastcall CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90(void * generalVolume)` | Decompile read-back clears `+0x588`, seeds `+0x2b4` from `+0x2a0` or `+0x2b0`, then dispatches mode-specific refresh or selected-burst preset helpers. |
| `0x00409f70` | `void __fastcall CBattleEngine__ChangeWeapon(void * battleEngine)` | Decompile read-back counts active weapons by mode `+0x260`, clears `+0x588`, cycles selected walker/jet weapon helpers, timestamps `+0x584`, and matches Stuart `CBattleEngine::ChangeWeapon` HUD weapon sample string flow. Runtime weapon cycling and HUD audio playback remain unproven. |

## Validation

- Headless dry/apply: `updated=0 skipped=6 missing=0 bad=0`, then `updated=6 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `6/6` targets.
- Fresh xref read-back: `7` rows.
- Fresh instruction read-back: `2526` rows, including `6` checked return-evidence hits.
- Focused probe: `cmd.exe /c npm run test:ghidra-general-volume-changeweapon-signature-tranche` passed with `0` `param_N` signature hits and `0` overclaim hits.
- Refreshed queue probe: `5866` functions, `471` commented functions, `5395` commentless functions, `2076` undefined signatures, and `2480` `param_N` signatures.

## Non-Claims

This is saved Ghidra signature/comment refinement only. It does not prove concrete `CGeneralVolume` or `CBattleEngine` layouts, local variable names, structure types, Ghidra tags, exact source identity for the GeneralVolume helpers, runtime weapon cycling, HUD audio playback, BEA launch behavior, game patching, or rebuild parity.
