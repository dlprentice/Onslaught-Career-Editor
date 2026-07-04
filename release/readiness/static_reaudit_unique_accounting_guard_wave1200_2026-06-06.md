# Static Re-Audit Unique Accounting Guard Wave1200

Status: complete accounting refresh
Date: 2026-06-06
Scope: `static-reaudit-unique-accounting-guard-wave1200`

Wave1200 (`wave1200-residual-unwind-current-risk-supersession`) uses the `wave1108-current-risk-rank` current-risk denominator, focused threshold `15`, and unique-address accounting from `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json`.

Measured status:

| Track | Value |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Corrected current-risk reviewed rows | `1017/1179 = 86.26%` |
| Remaining active focused work | `162` |
| Current risk candidates | `6166` |
| Current focused candidates | `1141` |
| Live regenerated current focused candidates | `1141` |

Wave1200 accounts for `147 residual compiler-unwind current-risk rows` with fresh Ghidra export evidence and read-only supersession. Fresh exports verified `147 xref rows`, `348 instruction rows`, and `147 decompile rows`. The wave made no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Probe token anchor: current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 162; current risk candidates: 6166; fresh Ghidra export; read-only supersession; 0x005d1115 Unwind@005d1115; 0x005d3440 Unwind@005d3440; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`.

Accounting boundary: the legacy additive counter is deprecated. After Wave1200 it would read `1048/1179`, but that includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; this is not Wave911 reconstruction.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-231915_post_wave1200_residual_unwind_current_risk_verified`.

Active measurement files:

- `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json`
- `reverse-engineering/binary-analysis/static-reaudit-progress.json`
- `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`
- `reverse-engineering/binary-analysis/mapped-systems.md`

Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`.

Boundary: static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime cleanup behavior, exact source-body identity, exact layouts, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
