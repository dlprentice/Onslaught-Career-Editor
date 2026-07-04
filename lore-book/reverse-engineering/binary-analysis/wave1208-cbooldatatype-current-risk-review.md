# Wave1208 CBoolDataType Current-Risk Review

Status: complete static read-only review; local validation passed; artifact committed
Date: 2026-06-07
Tag: `wave1208-cbooldatatype-current-risk-review`

Wave1208 measured anchor: unique-address accounting governs active current-risk progress. Wave1208 (`wave1208-cbooldatatype-current-risk-review`) accounts for `3 CBoolDataType current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This read-only review made no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; active current-risk progress is `1092/1179 = 92.62%`; remaining active focused work: 87; legacy additive counter is deprecated (`1123/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `3 xref rows`, `99 instruction rows`, and `3 decompile rows`. Anchors: `CBoolDataType__Equals`, `CBoolDataType__NotEquals`, and `CBoolDataType__Assign`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-040938_post_wave1208_cbooldatatype_current_risk_review_verified`. Active measurement files: `static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, and `reverse-engineering/binary-analysis/wave1108-current-risk-rank.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime MissionScript behavior, runtime bool datatype behavior, exact bool ABI, exact datatype layout, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Reviewed Rows

| Address | Function | Static evidence |
| --- | --- | --- |
| `0x0052e420` | `CBoolDataType__Equals` | DATA vtable-slot xref `0x005e4d68`; calls rhs datatype vtable slot `+0x3c`, reads `this+0x04`, compares equality, and returns via `RET 0x4`. |
| `0x0052e440` | `CBoolDataType__NotEquals` | DATA vtable-slot xref `0x005e4d6c`; calls rhs datatype vtable slot `+0x3c`, reads `this+0x04`, compares inequality, and returns via `RET 0x4`. |
| `0x0052e460` | `CBoolDataType__Assign` | DATA vtable-slot xref `0x005e4d64`; calls rhs datatype vtable slot `+0x3c`, stores the returned byte at `this+0x04`, and returns via `RET 0x4`. |

## Evidence Counts

- `pre-metadata.tsv`: 3 rows.
- `pre-tags.tsv`: 3 rows.
- `pre-xrefs.tsv`: 3 xref rows.
- `pre-instructions.tsv`: 99 instruction rows.
- `pre-decompile/index.tsv`: 3 decompile rows.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-040938_post_wave1208_cbooldatatype_current_risk_review_verified`, 18 files, 176425863 bytes, `DiffCount=0`, `HashDiffCount=0`.

## Accounting

- Static function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Active current-risk progress: `1092/1179 = 92.62%`.
- Remaining active focused work: 87.
- Current risk candidates: 6166.
- Current focused candidates: 1141.
- Live regenerated current focused candidates: 1141.
- Legacy additive counter is deprecated at `1123/1179`.
- Corrected duplicate-address overcount: 26 duplicate-address overcount.
- Wave1145 arithmetic overcount: 5.

## Boundary

This wave is static retail Ghidra metadata/tag/xref/instruction/decompile evidence only. It refreshes the MissionScript bool datatype vtable-slot map for rebuild-grade static contracts, but runtime MissionScript behavior, runtime bool datatype behavior, exact bool ABI, exact datatype layout, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
