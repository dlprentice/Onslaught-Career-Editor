# Wave1131 HeightField Current-Risk Review Readiness

Status: complete static tag-normalization evidence
Date: 2026-06-05
Scope: `wave1131-heightfield-current-risk-review`

Wave1131 saved current-risk/read-back tags for seven HeightField MAP rows: `0x0047e870 CHeightField__ResetCoreBuffersAndFlags`, `0x0047e8a0 CHeightField__FreeOwnedBuffers_24_1028`, `0x0047ef20 CHeightField__RecomputeGridExtentsAndHeightRange`, `0x00490e20 CHeightField__FreeOwnedBuffers_Thunk`, `0x00490f10 CHeightField__InitAndClearMapLoadFlags`, `0x00490f40 CHeightField__ShutdownAndDestroyMixerMap`, and `0x00490f50 CHeightField__TraceMapLoadRequestAndCheckLoadedFlags`.

Probe anchor: Wave1131; `wave1131-heightfield-current-risk-review`; `7 rows`; `168/1179 = 14.25%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1011; HeightField MAP current-risk cluster; fresh Ghidra export; tag-only normalization; `40 tags`; static debt `0 / 0 / 0`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260605-090018_post_wave1131_heightfield_current_risk_review_verified`; previous completed backup `[maintainer-local-ghidra-backup-root]\BEA_20260605-082438_post_wave1130_dive_dropship_current_risk_review_verified`.

Read-back evidence:

- Pre/post exports: `7` metadata rows, `7` tag rows, `9` xref rows, `220` instruction rows, and `7` decompile rows.
- Context exports: `7` metadata rows, `7` tag rows, `30` xref rows, `703` instruction rows, and `7` decompile rows.
- Dry/apply/final-dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=40 missing=0 bad=0`; `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=40 missing=0 bad=0`; `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Pre/post metadata, instruction, and xref exports match exactly.
- Queue quality refresh: `total_functions=6410 commented_functions=6410`.
- Current focused accounting: `168/1179 = 14.25%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1011.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-090018_post_wave1131_heightfield_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The seven target rows exist in the saved Ghidra project.
- Names and signatures match the expected saved static evidence.
- Current-risk tags were saved and read back.
- The evidence remains static Ghidra evidence only.

What remains separate:

- Runtime terrain and map-load behavior.
- Runtime battle-line and mixer-map behavior.
- Exact source-body identity and concrete layouts.
- BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity.
