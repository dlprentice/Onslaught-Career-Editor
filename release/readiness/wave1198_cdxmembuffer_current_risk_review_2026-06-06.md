# Wave1198 CDXMemBuffer Current-Risk Review Readiness Note

Wave1198 measured anchor: unique-address accounting now governs active current-risk progress. Wave1198 (`wave1198-cdxmembuffer-current-risk-review`) accounts for `6 CDXMemBuffer resource-buffer score15-16 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. The rows are `CDXMemBuffer__ctor`, `CDXMemBuffer__InitFromFile`, `CDXMemBuffer__Skip`, `CDXMemBuffer__Read`, `CDXMemBuffer__Close`, and `CDXMemBuffer__dtor_base_Thunk`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=92 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=92 missing=0 bad=0`, then final dry updated=0 skipped=6. It made no rename, no signature change, no function-boundary change, and no executable-byte change. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; corrected active current-risk progress is `860/1179 = 72.94%`; the legacy additive counter is deprecated (`891/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 319; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `709 xref rows`, `919 instruction rows`, and `6 decompile rows`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-214911_post_wave1198_cdxmembuffer_current_risk_review_verified`. Active measurement files: `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, and `reverse-engineering/binary-analysis/mapped-systems.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Exact source-body identity, concrete CDXMemBuffer/file/CRC/path-munge layouts, runtime IO behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Status: complete static read-back evidence; historical artifact committed
Date: 2026-06-06
Scope: `wave1198-cdxmembuffer-current-risk-review`

Wave1198 saved comment/tag normalization for 6 CDXMemBuffer resource-buffer score15-16 current-risk rows: `CDXMemBuffer__ctor`, `CDXMemBuffer__InitFromFile`, `CDXMemBuffer__Skip`, `CDXMemBuffer__Read`, `CDXMemBuffer__Close`, and `CDXMemBuffer__dtor_base_Thunk`. The pass made no rename, no signature change, no function-boundary change, and no executable-byte change.

Measured status:

| Track | Value |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Corrected current-risk reviewed rows | `860/1179 = 72.94%` |
| Remaining active focused work | `319` |
| Current risk candidates | `6166` |
| Current focused candidates | `1141` |
| Live regenerated current focused candidates | `1141` |

Accounting boundary: the active current-risk percentage now uses unique-address accounting from `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json`. The legacy additive counter is deprecated; after Wave1198 it would read `891/1179`, but that includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.

Read-back evidence:

- Dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=92 missing=0 bad=0`.
- Apply: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=92 missing=0 bad=0`.
- Final dry: final dry updated=0 skipped=6.
- Post exports: `6` metadata rows, `6` tag rows, `709 xref rows`, `919 instruction rows`, and `6 decompile rows`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-214911_post_wave1198_cdxmembuffer_current_risk_review_verified`.

Boundary: this proves static Ghidra comments/tags and resource-buffer contracts only. Exact source-body identity, concrete layouts, runtime IO behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
