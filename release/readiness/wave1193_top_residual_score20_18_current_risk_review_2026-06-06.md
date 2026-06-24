# Wave1193 Top Residual Score20-18 Current-Risk Review

Status: complete static read-back evidence committed
Date: 2026-06-06
Tag: `wave1193-top-residual-score20-18-current-risk-review`

Wave1193 accounts for `24 top residual score20-18 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. Score-band split: score20 residual rows: 5; score19 residual rows: 10; score18 residual rows: 9.

Evidence:

| Item | Result |
| --- | --- |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=24 tags_added=319 missing=0 bad=0` |
| Apply | `updated=24 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=24 tags_added=319 missing=0 bad=0`; `REPORT: Save succeeded` |
| Final dry | `updated=0 skipped=24 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Post exports | `24` metadata rows, `24` tag rows, `1554 xref rows`, `1386 instruction rows`, and `24 decompile rows` |
| Backup | `G:\GhidraBackups\BEA_20260606-185314_post_wave1193_top_residual_score20_18_current_risk_review_verified` |

Representative anchors include `CCockpit__dtor_base`, `CRT__RunStaticInitRangesWithOptionalCallback`, `SharedVFunc__ReturnZero_00405930`, `CHazard__VFunc02_CleanupWorldSoundAndLinkedState`, `CDestructableSegmentsController__Init`, `CFEPMain__Process`, `CUnitAI__QueueFiringOrPostfireAnimation`, and `CTexture__BuildTransformMatrixWithOptionalOffsets`.

No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt. Wave1108 current focused accounting is now `856/1179 = 72.60%`; current risk candidates: 6166; current focused candidates: 1154; live regenerated current focused candidates: 1154; remaining active focused work: 323; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Exact layouts, exact source-body identity, runtime behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1193; wave1193-top-residual-score20-18-current-risk-review; 856/1179 = 72.60%; 24 top residual score20-18 current-risk rows; score20 residual rows: 5; score19 residual rows: 10; score18 residual rows: 9; current focused candidates: 1154; live regenerated current focused candidates: 1154; remaining active focused work: 323; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=24 skipped=0; comment_only_updated=24; tags_added=319; final dry updated=0 skipped=24; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CCockpit__dtor_base; CRT__RunStaticInitRangesWithOptionalCallback; SharedVFunc__ReturnZero_00405930; CHazard__VFunc02_CleanupWorldSoundAndLinkedState; CDestructableSegmentsController__Init; CFEPMain__Process; CUnitAI__QueueFiringOrPostfireAnimation; CTexture__BuildTransformMatrixWithOptionalOffsets; 0 / 0 / 0; 6411/6411 = 100.00%; 1554 xref rows; 1386 instruction rows; 24 decompile rows; G:\GhidraBackups\BEA_20260606-185314_post_wave1193_top_residual_score20_18_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
