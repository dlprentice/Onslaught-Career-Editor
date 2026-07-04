# Ghidra Wave900+ Through Wave1089 Recheck Note

Status: validation passed
Date: 2026-06-04
Scope: `wave900-plus-through-wave1089-recheck`

This note extends the post-Wave900 recheck chain through Wave1089 and records the passed local validation gate:

```powershell
npm run test:ghidra-wave900-plus-through-wave1089-recheck
```

Wave1089 (`unit-family-residual-vtable-final-review-wave1089`) recovered thirty-five unit-family residual vtable function boundaries from the final ten-vtable sample. The focused readiness note is [`ghidra_unit_family_residual_vtable_final_review_wave1089_2026-06-04.md`](ghidra_unit_family_residual_vtable_final_review_wave1089_2026-06-04.md).

Coverage anchors:

- Static function-quality closure is `6410/6410 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1527/1560 = 97.88%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- The final ten-vtable unit-family residual sample is `1580` OK / `20` `NO_FUNCTION_AT_POINTER`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-130410_post_wave1089_unit_family_residual_vtable_final_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Exact source virtual names, concrete unit-family layouts, runtime behavior, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Validation result:

- Readiness notes: `192`.
- Covered waves: `190`.
- Package probe scripts: `188`.
- Evidence bases: `188`.
- Backup references: `190`.
- Apply scripts: `69`.
- Wave982-Wave1089 direct probes: `108` results, `1` direct pass, `107` expected stale-state/rolled-doc/historical-live-queue failures, `0` disallowed evidence/unclassified failures.
- Current queue: `6410` functions, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status `PASS`.

Probe token anchor: Wave1089; unit-family-residual-vtable-final-review-wave1089; 0x00489ed0 CInfantryUnitVFunc__ReturnFlag24Float005d856cOr005d8568_00489ed0; 0x004d35d0 CPodVFunc__FlagArg70AndSeedMotion250_004d35d0; 0x004deec0 CSentinelVFunc__BuildField164ContextAndDispatch_004deec0; 0x004eee80 CSubmarineVFunc__UpdateMotionVectorsAndNormalize_004eee80; 0x0050e9d0 CInfantryUnitVFunc__GetClassNameString_0050e9d0; 0x0050fd10 CGillMHeadVFunc__ForwardArgWithFlags40082000_0050fd10; 1527/1560 = 97.88%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-130410_post_wave1089_unit_family_residual_vtable_final_review_verified; boundary recovery.
