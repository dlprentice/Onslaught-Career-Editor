# Ghidra Component Scalar/Flag Apply Review Wave1039 Readiness Note

Status: complete static read-back evidence with comment/tag correction
Date: 2026-06-01
Scope: `component-scalar-flag-apply-review-wave1039`

Wave1039 re-read fifteen `CComponent*__ApplyToComponentByName` helpers originally hardened by Wave343 and saved a bounded Ghidra comment/tag correction. The pass preserved all names and signatures, made no function-boundary changes, made no executable-byte changes, did not launch BEA, and did not mutate game files.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0043ca70 CComponentScalarD8__ApplyToComponentByName` | DATA vtable ref `0x005daac4`; walks `DAT_00855400` by `componentName`; writes scalar `this+0x8` to component record `+0xd8`. |
| `0x0043d460 CComponentScalar160__ApplyToComponentByName` | DATA vtable ref `0x005da998`; walks `DAT_00855400` by `componentName`; writes scalar `this+0x8` to component record `+0x160`. |
| `0x0043ce60 CComponentFlag124__ApplyToComponentByName` | DATA vtable ref `0x005da9e8`; compares scalar `this+0x8` with zero constant `0x005d856c`; writes component record `+0x124` as `0` on the zero-comparison path and `1` otherwise. |
| `0x0043d3a0 CComponentFlag108__ApplyToComponentByName` | DATA vtable ref `0x005da9ac`; same zero-comparison flag shape for component record `+0x108`. |

Correction:

- The eight component flag rows previously carried positive-only wording.
- Fresh instruction/decompile evidence shows `FCOMP` against zero constant `0x005d856c`, `TEST AH,0x40`, and stores `0` on the zero-comparison path and `1` otherwise.
- Wave1039 replaces the stale positive-only wording with zero-comparison/nonzero-path wording and adds `component-scalar-flag-apply-review-wave1039` plus `wave1039-readback-verified` tags.

Read-back evidence:

- `ApplyComponentScalarFlagApplyReviewWave1039.java dry`: `updated=0 skipped=15 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=15 tags_added=60 missing=0 bad=0`
- `ApplyComponentScalarFlagApplyReviewWave1039.java apply`: `updated=15 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=15 tags_added=60 missing=0 bad=0`
- `ApplyComponentScalarFlagApplyReviewWave1039.java final dry`: `updated=0 skipped=15 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Post exports verified `15` metadata rows, `15` tag rows, `15` DATA xref rows, `1070` body-instruction rows, and `15` decompile rows.
- Queue closure remains `6238/6238 = 100.00%`.
- Wave911 focused progress advances to `711/1408 = 50.50%`.
- Expanded static surface progress advances to `940/1493 = 62.96%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-075609_post_wave1039_component_value_scalar_flag_apply_review_verified`, `19` files, `174001031` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The fifteen reviewed component scalar/flag apply rows exist in the saved Ghidra project with the expected names and `void __thiscall ...(void * this, char * componentName)` signatures.
- The saved comments and tags include Wave1039 read-back evidence.
- The scalar helpers walk `DAT_00855400` by component name and write `this+0x8` to the documented component-record offsets.
- The flag helpers walk `DAT_00855400` by component name and use the zero-comparison/nonzero-path store shape instead of positive-only semantics.

What remains separate proof:

- Runtime PhysicsScript application behavior.
- Runtime component behavior.
- Mission-script outcomes.
- Concrete component record field meanings beyond observed offsets.
- Exact source-body identity.
- BEA patching, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1039; component-scalar-flag-apply-review-wave1039; 0x0043ca70 CComponentScalarD8__ApplyToComponentByName; 0x0043d460 CComponentScalar160__ApplyToComponentByName; 0x0043ce60 CComponentFlag124__ApplyToComponentByName; 0x0043d3a0 CComponentFlag108__ApplyToComponentByName; DAT_00855400; 0x005d856c; positive-only wording; 711/1408 = 50.50%; 940/1493 = 62.96%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-075609_post_wave1039_component_value_scalar_flag_apply_review_verified; comment/tag correction.
