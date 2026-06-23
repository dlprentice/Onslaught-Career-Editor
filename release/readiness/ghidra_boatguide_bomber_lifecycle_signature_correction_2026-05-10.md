# Ghidra BoatGuide/Bomber Lifecycle Signature Correction - 2026-05-10

## Summary

Wave 312 completed a saved Ghidra name/signature/comment correction tranche for `5` BoatGuide/Bomber lifecycle queue targets.

The tranche corrected older constructor-like and vfunc-style labels to bounded constructor/destructor names:

- `0x00415d70` is now `CBoatGuide__ctor`.
- `0x004161a0` is now `CBomberAI__scalar_deleting_dtor`.
- `0x004161c0` is now `CBomberAI__dtor_body_004161c0`.
- `0x00416260` is now `CBomberGuide__scalar_deleting_dtor`.
- `0x00416280` is now `CBomberGuide__dtor_body_00416280`.

## Corrected Targets

| Address | Saved signature |
| --- | --- |
| `0x00415d70` | `void * __thiscall CBoatGuide__ctor(void * this, void * init)` |
| `0x004161a0` | `void * __thiscall CBomberAI__scalar_deleting_dtor(void * this, int flags)` |
| `0x004161c0` | `void __fastcall CBomberAI__dtor_body_004161c0(void * this)` |
| `0x00416260` | `void * __thiscall CBomberGuide__scalar_deleting_dtor(void * this, int flags)` |
| `0x00416280` | `void __fastcall CBomberGuide__dtor_body_00416280(void * this)` |

## Validation

- Headless correction dry run: `updated=0 skipped=5 renamed=0 missing=0 bad=0`.
- Headless correction apply: `updated=5 skipped=0 renamed=5 missing=0 bad=0`.
- Metadata read-back: `5/5` targets found.
- Decompile read-back: `5/5` targets dumped.
- Xref read-back: `5` rows.
- Instruction read-back: `445` rows.
- Focused probe: `PASS targets=5 renamed=5 failures=0`.
- Whole-database queue snapshot: `5868` functions, `618` commented functions, `5250` commentless functions, `2065` undefined signatures, and `2348` `param_N` signatures.

## Boundary

This is saved static Ghidra refinement only. It does not prove exact source identity, concrete BoatGuide/BomberAI/BomberGuide layouts, tag/local/type recovery, runtime pathfinding or AI cleanup behavior, BEA launch behavior, game patching, or rebuild parity.

`Bomber.cpp` remains missing from Stuart's source snapshot, so the CBomber names are retail-binary evidence, not source-confirmed methods.

Raw read-back exports and generated proof JSON remain under ignored `subagents/`.
