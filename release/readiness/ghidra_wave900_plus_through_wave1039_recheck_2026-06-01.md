# Ghidra Wave900+ Through Wave1039 Recheck

Status: ready for local validation
Date: 2026-06-01
Scope: Wave900 through Wave1039 static re-audit evidence

This note extends the Wave900+ structural recheck through Wave1039. It keeps the earlier Wave900-Wave1038 records historical and adds the Wave1039 focused probe/readiness/evidence/backup extension.

Current extension:

- Focused package script: `test:ghidra-component-scalar-flag-apply-review-wave1039`
- Aggregate package script: `test:ghidra-wave900-plus-through-wave1039-recheck`
- Focused readiness note: `release/readiness/ghidra_component_scalar_flag_apply_review_wave1039_2026-06-01.md`
- Focused probe: `tools/ghidra_component_scalar_flag_apply_review_wave1039_probe.py`
- Apply script: `tools/ApplyComponentScalarFlagApplyReviewWave1039.java`
- Evidence base: `subagents/ghidra-static-reaudit/wave1039-component-value-scalar-flag-apply-review`
- Verified backup: `G:\GhidraBackups\BEA_20260601-075609_post_wave1039_component_value_scalar_flag_apply_review_verified`

Wave1039 summary:

Wave1039 (`component-scalar-flag-apply-review-wave1039`) re-read fifteen component scalar/flag apply helpers and saved a comment/tag correction. Representative anchors are `0x0043ca70 CComponentScalarD8__ApplyToComponentByName`, `0x0043d460 CComponentScalar160__ApplyToComponentByName`, `0x0043ce60 CComponentFlag124__ApplyToComponentByName`, and `0x0043d3a0 CComponentFlag108__ApplyToComponentByName`. The correction replaces stale positive-only wording on the flag helpers with zero-comparison/nonzero-path evidence tied to `0x005d856c`. Fresh post exports verified `15` metadata rows, `15` tag rows, `15` DATA xref rows, `1070` body-instruction rows, and `15` decompile rows. Queue closure remains `6238/6238 = 100.00%`; Wave911 focused progress is `711/1408 = 50.50%`; expanded static surface progress is `940/1493 = 62.96%`; top-500 coverage remains `500/500 = 100.00%`.

Expected validation:

- `npm run test:ghidra-component-scalar-flag-apply-review-wave1039`
- `npm run test:ghidra-wave900-plus-through-wave1039-recheck`
- `npm run test:ghidra-static-reaudit-queue`

Boundary note:

This is structural static evidence validation. It checks focused probe coverage, readiness/evidence/backup structure, apply-log coverage, and live static queue closure. It does not prove runtime PhysicsScript application behavior, runtime component behavior, mission-script outcomes, exact source-body identity, concrete layouts, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1039; component-scalar-flag-apply-review-wave1039; 0x0043ca70 CComponentScalarD8__ApplyToComponentByName; 0x0043d460 CComponentScalar160__ApplyToComponentByName; 0x0043ce60 CComponentFlag124__ApplyToComponentByName; 0x0043d3a0 CComponentFlag108__ApplyToComponentByName; DAT_00855400; 0x005d856c; positive-only wording; 711/1408 = 50.50%; 940/1493 = 62.96%; 500/500 = 100.00%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-075609_post_wave1039_component_value_scalar_flag_apply_review_verified; comment/tag correction.
