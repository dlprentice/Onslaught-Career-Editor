# Wave911 Residual Accounting Wave1106 Readiness Note

Status: complete static accounting consolidation
Date: 2026-06-04
Scope: `wave911-residual-accounting-wave1106`

Wave1106 reconciles the Wave911 focused-candidate accounting against current static closure counters. This is a documentation/probe wave only: no Ghidra export, no Ghidra mutation, no executable-byte change, no BEA launch, no save mutation, and no installed-game/runtime-file mutation occurred.

Read-back/accounting anchors:

| Surface | Evidence |
| --- | --- |
| Function-quality closure | `6411/6411 = 100.00%`; commentless / exact-undefined / `param_N` debt is `0 / 0 / 0`. |
| Expanded post-100 surface | `1560/1560 = 100.00%`. |
| Wave911 focused queue | `812/1408 = 57.67%`; historical-retired/non-reconstructable provenance with `596` residual identities unproven and `300` materialized focused rows. |
| Wave911 top-500 | `500/500 = 100.00%`. |
| Active current-risk lane | `373/1179 = 31.64%`; active target `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. |
| Focused JSON | `wave911-focused-correction-candidates.v1`; `totalFunctions=6113`; `candidateFunctions=1408`; top sample count `200`. |
| Focused TSV | `300` data rows; partial scratch output, not the full `1408` focused queue. |
| Broad risk JSON | `wave911-risk-ranked-functions.v1`; `candidateFunctions=5803`; top sample count `250`. |
| Broad risk TSV | `500` data rows; matches the top-500 risk-ranked subset. |

Canonical note: `reverse-engineering/binary-analysis/wave911-residual-accounting.md`.

Latest completed Ghidra review backup remains Wave1100: `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

What this proves:

- The current repo now has a bounded, machine-checked statement of how the Wave911 focused queue relates to the newer `6411/6411`, `1560/1560`, and top-500 counters.
- The Wave911 `596` residual is historical provenance, not a present exact-address worklist; active static reconciliation is Wave1108 current-risk.
- The focused TSV is explicitly partial and must not be treated as the full `1408` focused queue.

What remains separate:

- Preserving Wave911 as historical-retired/non-reconstructable unless a future exact reconstruction produces a real row-level ledger.
- Reviewing or superseding the active Wave1108 current-risk focused denominator to `1179/1179`.
- Runtime gameplay behavior, exact layouts, BEA patching behavior, gameplay outcomes, visual QA, and clean-room rebuild parity.
