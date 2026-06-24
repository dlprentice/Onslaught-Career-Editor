# Ghidra Math / Half-Float Wave658 Readiness Note

Status: complete
Date: 2026-05-20

## Scope

Wave658 math/half-float hardening covered one owner-neutral math tolerance helper and two CFastVB half-float conversion rows:

| Address | Saved signature |
| --- | --- |
| `0x00575986` | `int __stdcall Math__IsFloatDiffOutsideTolerance(float lhs, float rhs)` |
| `0x005759c9` | `void __stdcall CFastVB__ConvertFloat32ArrayToFloat16(void * half_dest, void * float32_source, uint element_count)` |
| `0x00575a6b` | `void * __stdcall CFastVB__ConvertFloat16BufferToFloat32_00575a6b(void * float32_dest, void * half_source, uint element_count)` |

The pass added bounded comments/tags with the `math-half-float-wave658` tag. It made no renames, no function-boundary changes, no executable-byte changes, no installed-game changes, and no runtime claims.

## Evidence

- Pre-state exports: `subagents/ghidra-static-reaudit/wave658-math-half-float/pre-metadata.tsv`, `pre-tags.tsv`, `pre-xrefs.tsv`, `pre-instructions.tsv`, and `decompile-pre/`.
- Apply script: `tools/ApplyMathHalfFloatWave658.java`.
- Dry/apply/final dry:
  - Dry: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0`.
  - Apply: `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0`.
  - Final dry: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- Post-state exports verified `3` metadata rows, `3` tag rows, `17` xref rows, `723` instruction rows, and `3` clean decompile rows.
- Queue refresh passed with `6093` total functions, `3586` commented, `2507` commentless, `1217` exact-undefined signatures, and `722` `param_N` signatures.
- Comment-backed proxy: `3586/6093 = 58.85%`.
- Strict clean-signature proxy: `3536/6093 = 58.03%`.
- Verified backup: `G:\GhidraBackups\BEA_20260520-214232_post_wave658_math_half_float_verified` (`19` files, `163253127` bytes, `DiffCount=0`).
- Next high-signal queue head: `0x005771af CFastVB__DispatchIndirect_00656fb4`.

## Bounded Claim

This proves saved static retail Ghidra metadata for the three rows above: one float-difference tolerance helper, a float32-to-float16 array converter, and a float16-to-float32 array converter.

It does not prove exact tolerance semantics, NaN edge behavior, exact IEEE-754 edge-case parity, dispatch-table ownership, runtime math correctness, runtime vertex/texture conversion behavior, BEA patching, or rebuild parity.
