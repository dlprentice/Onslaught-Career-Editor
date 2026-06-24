# Wave1130 Dive/Dropship Current-Risk Review Readiness

Status: complete static tag-normalization evidence
Date: 2026-06-05
Scope: `wave1130-dive-dropship-current-risk-review`

Wave1130 saved current-risk/read-back tags for six DiveBomber/Dropship aircraft rows: `0x00445380 CDiveBomberAI__scalar_deleting_dtor`, `0x00445440 CDiveBomberGuide__scalar_deleting_dtor`, `0x00446d70 CDropship__Init`, `0x00447040 CDropshipAI__scalar_deleting_dtor`, `0x00447120 CDropship__ProcessDoorThrustersAndChildUnits`, and `0x00448170 CDropship__TraceGroundAndSpawnThrusterDust`.

Probe anchor: Wave1130; `wave1130-dive-dropship-current-risk-review`; `6 rows`; `161/1179 = 13.66%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1018; score-22 DiveBomber/Dropship aircraft current-risk cluster; fresh Ghidra export; tag-only normalization; `42 tags`; static debt `0 / 0 / 0`; verified backup `G:\GhidraBackups\BEA_20260605-082438_post_wave1130_dive_dropship_current_risk_review_verified`; previous completed backup `G:\GhidraBackups\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified`.

Read-back evidence:

- Pre/post exports: `6` metadata rows, `6` tag rows, `7` xref rows, `1049` instruction rows, `6` decompile rows, and `512` vtable-slot rows.
- Dry/apply/final-dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=42 missing=0 bad=0`; `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=42 missing=0 bad=0`; `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Pre/post metadata, instruction, xref, and vtable-slot exports match exactly.
- Queue quality refresh: `total_functions=6410 commented_functions=6410`.
- Current focused accounting: `161/1179 = 13.66%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1018.
- Verified backup: `G:\GhidraBackups\BEA_20260605-082438_post_wave1130_dive_dropship_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`.

What this proves:

- The six target rows exist in the saved Ghidra project.
- Names and signatures match the expected saved static evidence.
- Current-risk tags were saved and read back.
- The evidence remains static Ghidra evidence only.

What remains separate:

- Runtime dive-bomber AI behavior.
- Runtime dropship door/thruster/child-unit behavior.
- Exact source-body identity and concrete layouts.
- BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity.
