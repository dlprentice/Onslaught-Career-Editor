# Wave911 Reconstruction Preflight

Status: active static tracking note
Last updated: 2026-06-04
Scope: `wave911-reconstruction-preflight-wave1107`

Wave1107 checks whether the original Wave911 focused `1408`-row queue can be exactly regenerated from the current repo/workspace artifacts.

## Finding

The exact original Wave911 focused worklist is not reconstructable from the currently available tracked files plus the current on-disk Wave911 scratch folder.

This is not a static RE regression. It is an accounting/provenance boundary:

- Wave911 was generated from a Wave910 queue snapshot with `totalFunctions=6113`.
- The current live queue is `6411/6411 = 100.00%`.
- The current queue TSV schema is only `address`, `name`, `signature`, `comment`, and `status`.
- The current queue does not store Wave911 signal columns or the original Wave911 score.
- The Wave911 scratch folder contains only four output files, not a generator or full focused TSV.

## Evidence

| Surface | Evidence |
| --- | --- |
| Wave911 readiness note | `release/readiness/ghidra_wave911_static_reaudit_risk_rank_2026-05-27.md` documents the heuristic signals and records `focused candidates: 1408`. |
| Git history | `afa2c0f0 RE: verify Wave910 queue and seed Wave911 risk rank.` and merge `e56f8c89 Merge main: Wave910 queue verification and Wave911 risk rank.` added readiness/state documentation, not a tracked scoring generator. |
| Focused JSON | `wave911-focused-correction-candidates.v1`; `totalFunctions=6113`; `candidateFunctions=1408`; top sample count `200`. |
| Focused TSV | `300` data rows; partial scratch output, not the full `1408` focused queue. |
| Broad risk JSON | `wave911-risk-ranked-functions.v1`; `totalFunctions=6113`; `candidateFunctions=5803`; top sample count `250`. |
| Broad risk TSV | `500` data rows. |
| Current queue TSV | Header is `address`, `name`, `signature`, `comment`, `status`; current rows are `6411`. |
| Latest completed Ghidra backup | `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`. |

## Consequence

The remaining `596` Wave911-focused rows remain a valid historical residual counter, but the exact row identities cannot be proven from the currently available artifacts alone.

The safe static path is therefore:

1. Do not call the current `300`-row focused TSV the full `1408` Wave911 queue.
2. Do not generate an "exact Wave911 residual" from the current `6411`-row queue.
3. Either build a new current-risk-ranked queue from first principles and label it as a new Wave1108+ current-risk denominator, or close residual confidence by subsystem supersession ledgers that point to fresh Ghidra evidence and static contracts.

## Boundaries

This preflight does not change Ghidra, executable bytes, runtime files, saves, or installed game files. It does not prove runtime gameplay behavior, exact layouts, BEA patching behavior, visual QA, or clean-room rebuild parity.
