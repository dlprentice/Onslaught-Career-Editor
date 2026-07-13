# Ghidra Early Helper Signature Tranche - 2026-05-09

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00407060` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

## Summary

This wave reparsed six already named early helper functions after fresh metadata, decompile, xref, and instruction exports showed several signatures still carried stale `param_N` or wrong arity evidence. A serial headless dry/apply pass saved corrected signatures and proof-boundary comments, followed by fresh read-back and a focused probe.

## Corrected Targets

| Address | Saved signature after correction | Evidence boundary |
| --- | --- | --- |
| `0x004062d0` | `void __thiscall CSquadNormal__BuildOrientationMatrixFromEuler(void * this, float angle0, float angle1, float angle2)` | Instruction evidence shows `ret 0xc`; decompile read-back shows FPU trig and matrix-row writes through the object/output matrix through `+0x28`. Wide xrefs keep exact owner/source identity provisional. |
| `0x00406d50` | `void __fastcall Vec3__NormalizeInPlace(void * vec)` | Decompile read-back shows SQRT length, zero-length guard, reciprocal scale, and in-place writes to vector lanes `+0x0`, `+0x4`, and `+0x8`. |
| `0x00407060` | `void __thiscall CEngine__MoveBurstReaderToCooldownSet(void * this, int readerId)` | Instruction evidence shows `ret 0x4`; decompile read-back moves a matching active-set `+0x294` entry into cooldown set `+0x2a4` or frees a duplicate reader. |
| `0x00407140` | `void __thiscall CMonitor__RemoveActiveReaderById(void * this, int readerId)` | Instruction evidence shows `ret 0x4`; decompile read-back scans cooldown set `+0x2a4`, removes a matching entry, and calls `CGenericActiveReader__dtor` / `OID__FreeObject`. |
| `0x00407310` | `bool __thiscall CBattleEngine__IsCurrentResolvedEntry(void * this, void * expectedEntry)` | Instruction evidence shows `ret 0x4`; decompile read-back resolves the current entry through `+0x57c` or `+0x578` and compares it with the expected pointer. |
| `0x00407540` | `void __fastcall CGame__UpdateMouseLookAngles(void * battleEngine)` | Decompile/xref read-back keeps the historical mouse-look behavior label: sensitivity/window dimensions, invert-Y state, orientation matrix setup, vector helpers, heightfield normal sampling, pitch clamp, and cursor recentering. |

## Validation

- Headless dry/apply: `updated=0 skipped=6 missing=0 bad=0`, then `updated=6 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `6/6` targets.
- Fresh xref read-back: `171` rows.
- Fresh instruction read-back: `1038` rows, including `4` checked return-arity rows.
- Focused probe: `cmd.exe /c npm run test:ghidra-early-helper-signature-tranche` passed with `0` `param_N` signature hits.
- Refreshed queue probe: `5866` functions, `453` commented functions, `5413` commentless functions, `2076` undefined signatures, and `2498` `param_N` signatures.

## Non-Claims

This is saved Ghidra signature/comment refinement only. It does not prove exact Stuart-source method identities, concrete object/entry/reader/matrix layouts, tags, local variable names, structure types, runtime mouse-look/projectile-reader/entry-resolution behavior, BEA launch behavior, game patching, or rebuild parity.
