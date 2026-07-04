# Wave911 Residual Static Accounting

Status: active static tracking note
Last updated: 2026-06-04
Scope: `wave911-residual-accounting-wave1106`

This note reconciles the Wave911 focused queue with the newer static closure counters so the remaining static re-audit path is measurable without overclaiming from partial scratch files.

## Current Counters

| Track | Current | Meaning |
| --- | ---: | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` | Every loaded Ghidra function object currently has a bounded name/signature/comment-quality treatment. |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` | No remaining export-contract signature/comment debt in the live queue. |
| Expanded post-100 static surface | `1560/1560 = 100.00%` | The broader post-100 review denominator is closed. |
| Wave911 top-500 risk-ranked subset | `500/500 = 100.00%` | The top-500 high-risk subset is complete. |
| Wave911 focused risk queue | `812/1408 = 57.67%` | Historical-retired/non-reconstructable provenance with `596` residual identities unproven and `300` materialized focused rows. |
| Active current-risk lane | `373/1179 = 31.64%` | Wave1108 current focused denominator; active target is `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. |

## Wave911 Artifact Reconciliation

Wave911 produced useful risk-ranked artifacts, but the current checked-in scratch files are not a full live worklist. Treat the canonical `1408` denominator as historical focused-queue accounting, not as proof that `1408` rows are presently materialized in a TSV.

| Artifact | Current evidence |
| --- | --- |
| `subagents/ghidra-static-reaudit/wave911-risk-rank/wave911-focused-correction-candidates.json` | Schema `wave911-focused-correction-candidates.v1`; source `functions_quality.tsv`; `totalFunctions=6113`; `candidateFunctions=1408`; top sample count `200`. |
| `subagents/ghidra-static-reaudit/wave911-risk-rank/wave911-focused-correction-candidates.tsv` | `300` data rows; partial scratch output, not the full `1408` focused queue. |
| `subagents/ghidra-static-reaudit/wave911-risk-rank/wave911-risk-ranked-functions.json` | Schema `wave911-risk-ranked-functions.v1`; source `functions_quality.tsv`; `totalFunctions=6113`; `candidateFunctions=5803`; top sample count `250`. |
| `subagents/ghidra-static-reaudit/wave911-risk-rank/wave911-risk-ranked-functions.tsv` | `500` data rows; matches the top-500 risk-ranked subset that is already complete. |

The focused JSON records the canonical Wave911 focused denominator (`1408`) and the current progress dashboard preserves `812/1408 = 57.67%`. The focused TSV only records `300` data rows. Therefore, the safe historical residual is:

```text
1408 focused candidates - 812 completed = 596 residual Wave911-focused identities not proven by present artifacts
```

Latest completed Ghidra review backup remains Wave1100: `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Wave1107 reconstruction preflight (`wave911-reconstruction-preflight-wave1107`) checked whether the original Wave911 full focused worklist is not reconstructable from present artifacts. The Wave911 readiness note records `focused candidates: 1408`, and git history anchors `afa2c0f0 RE: verify Wave910 queue and seed Wave911 risk rank.` plus `e56f8c89 Merge main: Wave910 queue verification and Wave911 risk rank.`. The available artifacts still show `totalFunctions=6113`, `candidateFunctions=1408`, top sample count `200`, `300` data rows, `candidateFunctions=5803`, top sample count `250`, and `500` data rows, while the current queue is `6411/6411 = 100.00%` with header `address`, `name`, `signature`, `comment`, and `status`; only four output files are present in the Wave911 scratch folder. This preserves the `596` residual counter while blocking any claim that the exact original `1408` row identities were recovered from the current `6411`-row queue.

## Active Static Completion Target

The loaded-function export contract and expanded post-100 audit are already closed. Wave911 `812/1408 = 57.67%` is preserved as historical-retired/non-reconstructable provenance, not as an active exact-address worklist. The active static reconciliation lane is Wave1108 current-risk: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`, currently `373/1179 = 31.64%`.

1. Review or supersede Wave1108 current-risk focused rows in small coherent static clusters until the active denominator reaches `1179/1179`.
2. Use fresh Ghidra metadata/tags/instructions/xrefs/decompile evidence before any mutation.
3. Mutate only when source, decompile, xrefs, instructions, and ownership evidence justify it; otherwise record read-only PASS.
4. Keep subsystem contracts current so the evidence becomes usable static maps rather than scattered readiness notes.
5. Preserve the Wave911 residual number as provenance unless a future exact reconstruction produces a real row-level ledger.

## Boundaries

This accounting note does not change Ghidra, executable bytes, runtime files, saves, or installed game files. It does not prove runtime gameplay behavior, exact layouts, patch behavior, or clean-room rebuild parity.

Use this note to avoid two mistakes:

- Do not treat `6411/6411 = 100.00%` as runtime or rebuild completion.
- Do not treat the `300`-row focused TSV as the full Wave911 `1408`-row focused queue.
