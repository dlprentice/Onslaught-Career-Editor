# Wave1132 Component/UnitAI Current-Risk Review Readiness

Status: complete static tag-normalization evidence
Date: 2026-06-05
Scope: `wave1132-component-ai-current-risk-review`

Wave1132 saved current-risk/read-back tags for ten component/active-reader UnitAI residual rows: `0x00427b80 CComponent__VFunc_09_00427b80`, `0x00427f90 CComponentBomberAI__scalar_deleting_dtor`, `0x00427fb0 CComponentBomberAI__dtor_base`, `0x00428050 CFenrirMainGunAI__scalar_deleting_dtor`, `0x00428070 CFenrirMainGunAI__dtor_base`, `0x00428710 CUnitAI__GetRenderPosFromActorOrCache`, `0x00428770 CUnitAI__GetRenderOrientationFromActorOrCache`, `0x00428c70 CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action`, `0x00428d50 CUnitAI__PlayActivateAnimationOrFinalizeActivated`, and `0x00428e80 CComponentAI__ClearReaderIfTargetDestroyedThenForward`.

Probe anchor: Wave1132; `wave1132-component-ai-current-risk-review`; `10 rows`; `178/1179 = 15.10%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1001; component/active-reader UnitAI residual cluster; fresh Ghidra export; tag-only normalization; `91 tags`; static debt `0 / 0 / 0`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260605-093432_post_wave1132_component_ai_current_risk_review_verified`; previous completed backup `[maintainer-local-ghidra-backup-root]\BEA_20260605-090018_post_wave1131_heightfield_current_risk_review_verified`.

Read-back evidence:

- Pre/post exports: `10` metadata rows, `10` tag rows, `21` xref rows, `326` instruction rows, and `10` decompile rows.
- Context exports: `10` metadata rows, `10` tag rows, `16` xref rows, `1173` instruction rows, and `10` decompile rows.
- Dry/apply/final-dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=91 missing=0 bad=0`; `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=91 missing=0 bad=0`; `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Pre/post metadata, instruction, and xref exports match exactly.
- Queue quality refresh: `total_functions=6410 commented_functions=6410`.
- Current focused accounting: `178/1179 = 15.10%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1001.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-093432_post_wave1132_component_ai_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The ten target rows exist in the saved Ghidra project.
- Names and signatures match the expected saved static evidence.
- Current-risk tags were saved and read back.
- The evidence remains static Ghidra evidence only.

What remains separate:

- Runtime Component, UnitAI, active-reader, render-cache, and activation behavior.
- Exact source-body identity and concrete layouts.
- BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity.
