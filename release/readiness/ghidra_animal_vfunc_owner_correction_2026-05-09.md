# Ghidra Animal Vfunc Owner Correction - 2026-05-09

## Summary

This wave reparsed a focused saved-Ghidra tranche after RTTI/vtable and decompile evidence showed one old lifecycle label was stale. A clean headless dry/apply pass updated three saved names/signatures/comments, then fresh metadata, decompile, xref, instruction, and vtable type read-back verified the result.

## Corrected Targets

| Address | Saved name after correction | Evidence boundary |
| --- | --- | --- |
| `0x00403d30` | `CAnimal__Init` | `CAnimal` vtable slot `9` points here; the body copies init transform/vector state, reads a type value at init offset `+0x3bc`, references `bird_msh`, creates a model/resource object, delegates to `CComplexThing__Init`, links the animal list, and schedules event `3000` when active. |
| `0x00404010` | `CAnimal__dtor_base` | The body resets the vtable to `0x005d8698`, clears linked animal-list references through `DAT_00660130` / `DAT_00660134`, then delegates to `CComplexThing__dtor_base`; this supersedes the old `CAtmospheric__Destructor` owner label. |
| `0x004041f0` | `CAnimal__scalar_deleting_dtor` | The wrapper calls `CAnimal__dtor_base`, checks `flags&1`, optionally frees `this`, returns `this`, and returns with one stack argument. |

## Validation

- Headless dry/apply: `updated=0 skipped=3 missing=0 bad=0`, then `updated=3 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `3/3` targets.
- Fresh xref read-back: `3` rows.
- Fresh instruction read-back: `783` rows.
- Vtable type read-back: `1` row resolving `0x005d8698` to `CAnimal`.
- Focused probe: `cmd.exe /c npm run test:ghidra-animal-vfunc-owner-correction` passed with `0` stale name/signature token hits.
- Refreshed queue probe: `5866` functions, `441` commented functions, `5425` commentless functions, `2076` undefined signatures, and `2510` `param_N` signatures.

## Non-Claims

This is saved Ghidra name/signature/comment refinement only. It does not prove exact Stuart-source virtual method names, concrete `CAnimal` / init-object / resource descriptor layouts, tags, local variable names, structure types, runtime animal spawning, scheduling, model loading, destructor side effects, BEA launch behavior, game patching, or rebuild parity.
