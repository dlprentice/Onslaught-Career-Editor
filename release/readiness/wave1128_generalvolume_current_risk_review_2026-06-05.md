# Wave1128 GeneralVolume Current-Risk Review Readiness Note

Status: complete static comment/tag normalization evidence
Date: 2026-06-05
Scope: `wave1128-generalvolume-current-risk-review`

Wave1128 re-read and normalized comments/tags for `6 rows` from the Wave1108 current focused denominator as a score-22 `CGeneralVolume` current-risk cluster: `0x00402020 CGeneralVolume__ResetCooldownTimestamp`, `0x0040b100 CGeneralVolume__ctor_base`, `0x0040c720 CGeneralVolume__ResetAndSetActiveReader`, `0x00412830 CGeneralVolume__DisableLinkedEntriesByNameAndReselect`, `0x00413660 CGeneralVolume__ApplyYawInputByWeaponClass`, and `0x004136e0 CGeneralVolume__ApplyPitchInputByWeaponClass`.

Current focused accounting advances to `150/1179 = 12.72%` of the continuity denominator. The live regenerated current focused candidates: 1178; remaining active focused work: 1029. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

fresh Ghidra export evidence summary:

- Pre metadata/tag/xref/instruction/decompile exports: `6` / `6` / `54` / `170` / `6`.
- Dry/apply/final-dry summaries: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=3 tags_added=51 missing=0 bad=0`; `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=3 tags_added=51 missing=0 bad=0`; `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post metadata/tag/xref/instruction/decompile exports: `6` / `6` / `54` / `170` / `6`.
- Pre/post instruction exports match exactly.
- Queue quality refresh reported `total_functions=6410 commented_functions=6410`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-072044_post_wave1128_generalvolume_current_risk_review_verified`, `19` files, `175934343` bytes, `DiffCount=0`.
- Previous completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-071212_post_wave1127_mixed_score23_current_risk_review_verified`.

Mutation boundary:

- Comment/tag normalization.
- `51 tags` added.
- Three comments normalized to remove old “tags unproven” wording after the tags were saved.
- No rename, signature change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, or runtime-file mutation.

Claim boundary:

This proves saved static Ghidra read-back coherence for these six function rows and closes the older Wave966 tag gap for `0x00402020`, `0x0040b100`, and `0x0040c720`. Runtime behavior, exact source-body identity, concrete layout semantics, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
