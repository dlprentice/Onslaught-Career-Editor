# Wave1198 CDXMemBuffer Current-Risk Review

Wave1198 measured anchor: unique-address accounting now governs active current-risk progress. Wave1198 (`wave1198-cdxmembuffer-current-risk-review`) accounts for `6 CDXMemBuffer resource-buffer score15-16 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. The rows are `CDXMemBuffer__ctor`, `CDXMemBuffer__InitFromFile`, `CDXMemBuffer__Skip`, `CDXMemBuffer__Read`, `CDXMemBuffer__Close`, and `CDXMemBuffer__dtor_base_Thunk`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=92 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=92 missing=0 bad=0`, then final dry updated=0 skipped=6. It made no rename, no signature change, no function-boundary change, and no executable-byte change. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; corrected active current-risk progress is `860/1179 = 72.94%`; the legacy additive counter is deprecated (`891/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 319; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `709 xref rows`, `919 instruction rows`, and `6 decompile rows`. Verified backup: `G:\GhidraBackups\BEA_20260606-214911_post_wave1198_cdxmembuffer_current_risk_review_verified`. Active measurement files: `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, and `reverse-engineering/binary-analysis/mapped-systems.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Exact source-body identity, concrete CDXMemBuffer/file/CRC/path-munge layouts, runtime IO behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Status: complete static read-back evidence; historical artifact committed
Date: 2026-06-06
Tag: `wave1198-cdxmembuffer-current-risk-review`

Wave1198 saved comment/tag normalization for 6 CDXMemBuffer resource-buffer score15-16 current-risk rows from the `wave1108-current-risk-rank` current-risk denominator. It made no rename, no signature change, no function-boundary change, and no executable-byte change.

## Measured Result

| Track | Value | Authority |
| --- | ---: | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` | `subagents/ghidra-static-reaudit/queue/current/static-reaudit-queue.json` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` | `subagents/ghidra-static-reaudit/queue/current/static-reaudit-queue.json` |
| Corrected current-risk reviewed rows | `860/1179 = 72.94%` | `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json` |
| Remaining active focused work | `319` | `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json` |
| Live regenerated current focused candidates | `1141` | `subagents/ghidra-static-reaudit/wave1108-current-risk-rank/wave1108-current-focused-candidates.tsv` |

The active accounting mode is unique-address accounting. The legacy additive counter is deprecated: it would have reported `891/1179`, but that includes a 26 duplicate-address overcount plus a Wave1145 arithmetic overcount: 5. The central ledger records the correction so future waves do not carry stale additive math forward.

## Targets

| Address | Function | Static contract |
| --- | --- | --- |
| `0x00547d70` | `CDXMemBuffer__ctor` | Constructor/init path clears file/data/CRC pointer and buffered reader state fields. |
| `0x00547ec0` | `CDXMemBuffer__InitFromFile` | File-open/init helper with `filename`, `memType`, `mungePath`, and `startSkip` caller-popped contract. |
| `0x005482d0` | `CDXMemBuffer__Skip` | Advances the buffered read cursor, refilling blocks as needed, and returns observed skipped byte count. |
| `0x00548570` | `CDXMemBuffer__Read` | Copies bytes from the active buffer into caller storage, handles refills, short-read/EOF state, and CRC-side-data checks. |
| `0x00548c00` | `CDXMemBuffer__Close` | Closes read-mode handles or flushes write-mode buffered bytes and CRC side data, then clears owned state. |
| `0x004cdb90` | `CDXMemBuffer__dtor_base_Thunk` | ParticleSet.cpp unwind cleanup thunk; single-instruction jump to `0x00547d90 CDXMemBuffer__dtor_base`. |

## Evidence

- Fresh Ghidra export: `6` metadata rows, `6` tag rows, `709 xref rows`, `919 instruction rows`, and `6 decompile rows`.
- Ghidra dry/apply/final-dry:
  - `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=92 missing=0 bad=0`
  - `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=92 missing=0 bad=0`
  - final dry updated=0 skipped=6.
- Queue refresh remains `6411/6411 = 100.00%` with `0 / 0 / 0` static debt.
- Current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141.
- Verified backup: `G:\GhidraBackups\BEA_20260606-214911_post_wave1198_cdxmembuffer_current_risk_review_verified`.

## Boundary

This is static rebuild-grade static contracts evidence only. Exact source-body identity, concrete CDXMemBuffer/file/CRC/path-munge layouts, runtime IO behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
