# Ghidra GeneralVolume / Boat Signature Correction - 2026-05-10

## Summary

Wave 310 completed a saved Ghidra name/signature/comment correction tranche for `9` GeneralVolume, BattleLine, Boat, BoatAI, and UnitAI queue targets.

The tranche corrected stale intermediate labels at `0x00414b70`, `0x00414cb0`, `0x00414fa0`, `0x00414fc0`, `0x00415060`, and `0x00415080`, and hardened the entry-name and lifecycle signatures for adjacent already named targets.

## Corrected Targets

| Address | Saved signature |
| --- | --- |
| `0x00414970` | `void __thiscall CGeneralVolume__EnableEntriesByName(void * this, char * entryName)` |
| `0x00414a40` | `void __thiscall CGeneralVolume__DisableEntriesByNameAndReselect(void * this, char * entryName)` |
| `0x00414b70` | `int __fastcall CGeneralVolume__CountEnabledEntriesIncludingPrimary(void * this)` |
| `0x00414cb0` | `void __thiscall CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices(void * this)` |
| `0x00414e50` | `void __thiscall CBoat__Init(void * this, void * init)` |
| `0x00414fa0` | `void * __thiscall CBoatAI__scalar_deleting_dtor(void * this, int flags)` |
| `0x00414fc0` | `void __fastcall CBoatAI__dtor_body_00414fc0(void * this)` |
| `0x00415060` | `void * __thiscall CUnitAI__scalar_deleting_dtor(void * this, int flags)` |
| `0x00415080` | `void __fastcall CUnitAI__dtor_body_00415080(void * this)` |

## Validation

- Headless correction dry run: `updated=0 skipped=9 renamed=0 missing=0 bad=0`.
- Headless correction apply: `updated=9 skipped=0 renamed=6 missing=0 bad=0`.
- Metadata read-back: `9/9` targets found.
- Decompile read-back: `9/9` targets dumped.
- Xref read-back: `12` rows.
- Instruction read-back: `801` rows.
- Focused probe: `PASS targets=9 renamed=6 failures=0`.
- Whole-database queue snapshot: `5868` functions, `608` commented functions, `5260` commentless functions, `2065` undefined signatures, and `2358` `param_N` signatures.

## Boundary

This is saved static Ghidra refinement only. It does not prove runtime GeneralVolume entry selection, BattleLine overlay rendering, Boat/BoatAI/UnitAI lifecycle behavior, exact source identity, concrete structures, tags, local variables, runtime cloak activation, fire-while-cloaked behavior, exact retail `CBattleEngine::WeaponFired`, `weapon_fire_breaks_stealth`, BEA launch behavior, game patching, or rebuild parity.

Raw read-back exports and generated proof JSON remain under ignored `subagents/`.
