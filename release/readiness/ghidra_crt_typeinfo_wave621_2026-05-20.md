# Ghidra CRT/type_info Wave621 Readiness Note

Status: complete
Date: 2026-05-20

## Scope

Wave621 hardened ten CRT/type_info/runtime helper rows after the Wave620 CRT/SEH head in the saved Ghidra project:

- `0x0055dac5 type_info__dtor`
- `0x0055daee type_info__scalar_deleting_dtor`
- `0x0055db0a CRT__EhVectorDestructorIterator_WithUnwind`
- `0x0055dccd CRT__Acos`
- `0x0055dda8 CRT__CExit`
- `0x0055ddca CRT__DoExit`
- `0x0055de81 CRT__InvokeFunctionPointerRange`
- `0x0055df28 CRT__OnexitTablePush`
- `0x0055dfa6 CRT__RegisterOnexitFunction`
- `0x0055dfe7 CRT__RoundDoubleWithFpuChecks`

The pass saved bounded signatures, comments, and tags. It corrected three stale names: `type_info__ctor_like_0055dac5`, `type_info__VFunc_00_0055daee`, and `CDXLandscape__DestroyArrayWithCallback`. It made no function-boundary changes and no executable byte changes.

## Evidence

- Dry/apply/final-dry logs reported `updated=0 skipped=10 renamed=0 would_rename=3 missing=0 bad=0`, then `updated=10 skipped=0 renamed=3 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post-state exports verified `10` metadata rows, `10` tag rows, `246` xref rows, `490` instruction rows, and `10` decompile rows.
- Type-info evidence covers the destructor body that restores `type_info::vftable` and frees the cached name buffer, plus the scalar-deleting destructor wrapper that tests `deleteFlags & 1`.
- Vector-destructor evidence at `0x0055db0a` computes `array + elemSize * count`, walks elements in reverse, calls the element destructor callback through ECX, and uses `CRT__EhVectorDestructorIterator_IfNoException` on the cleanup path. Broad xrefs show generic runtime-helper use, not CDXLandscape ownership.
- Exit/onexit evidence covers `CRT__CExit`, `CRT__DoExit`, the function-pointer range walker, and the onexit registration table.
- Math evidence covers the acos-style FPU helper and rounded-double helper with control-word/status handling.
- Backup verified: `G:\GhidraBackups\BEA_20260520-042315_post_wave621_crt_typeinfo_verified` with `19` files, `161844103` bytes, and `DiffCount=0`.

## Queue Telemetry

Post-Wave621 queue telemetry:

- Total functions: `6093`
- Commented functions: `3234`
- Commentless functions: `2859`
- Exact `undefined` signatures: `1218`
- `param_N` signatures: `1046`
- Comment-backed proxy: `3234/6093 = 53.08%`
- Strict clean-signature proxy: `3182/6093 = 52.22%`

Delta from Wave620: `+10` commented, `-10` commentless, `0` exact-undefined signatures, `-10` `param_N`, and `+13` strict clean-signature rows.

The next high-signal queue head is `0x0055e14f CLIParams__ScanFormatFromString`.

## Boundaries

This is static saved-Ghidra CRT/type_info/runtime helper evidence only. Exact MSVC CRT version, full `type_info`/RTTI layouts, exact EH vector helper identity, runtime unwind/math/exit behavior, BEA patching, and rebuild parity remain deferred.
