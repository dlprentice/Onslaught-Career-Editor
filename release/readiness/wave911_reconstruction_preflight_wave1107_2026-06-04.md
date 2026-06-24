# Wave911 Reconstruction Preflight Wave1107 Readiness Note

Status: complete static reconstruction preflight
Date: 2026-06-04
Scope: `wave911-reconstruction-preflight-wave1107`

Wave1107 checks whether the original Wave911 focused `1408`-row queue can be exactly regenerated from currently available repo/workspace artifacts. This is a documentation/probe wave only: no Ghidra export, no Ghidra mutation, no executable-byte change, no BEA launch, no save mutation, and no installed-game/runtime-file mutation occurred.

Findings:

The original Wave911 full focused worklist is not reconstructable from present artifacts. The current queue TSV header is `address`, `name`, `signature`, `comment`, and `status`, and the Wave911 scratch folder contains four output files.

| Surface | Evidence |
| --- | --- |
| Wave911 readiness | `release/readiness/ghidra_wave911_static_reaudit_risk_rank_2026-05-27.md`; records `focused candidates: 1408`. |
| Git history | `afa2c0f0 RE: verify Wave910 queue and seed Wave911 risk rank.` and `e56f8c89 Merge main: Wave910 queue verification and Wave911 risk rank.` added readiness/state docs, not a tracked scoring generator. |
| Focused JSON | `wave911-focused-correction-candidates.v1`; `totalFunctions=6113`; `candidateFunctions=1408`; top sample count `200`. |
| Focused TSV | `300` data rows; partial scratch output, not the full `1408` focused queue. |
| Broad risk JSON | `wave911-risk-ranked-functions.v1`; `totalFunctions=6113`; `candidateFunctions=5803`; top sample count `250`. |
| Broad risk TSV | `500` data rows. |
| Current queue | `6411/6411 = 100.00%`; queue TSV header is `address`, `name`, `signature`, `comment`, `status`. |
| Current counters | `0 / 0 / 0` commentless / exact-undefined / `param_N`; expanded surface `1560/1560 = 100.00%`; Wave911 focused `812/1408 = 57.67%`; top-500 `500/500 = 100.00%`; residual `596`. |

Canonical note: `reverse-engineering/binary-analysis/wave911-reconstruction-preflight.md`.

Latest completed Ghidra review backup remains Wave1100: `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

What this proves:

- The original Wave911 full focused row identities cannot be proven from the present artifacts alone.
- The current `300`-row focused TSV is partial scratch evidence and must not be treated as the full `1408` focused queue.
- Any future regenerated queue from the current `6411`-row surface must be labeled as a new current-risk denominator, not the exact original Wave911 list.

What remains separate:

- Building a new current-risk-ranked queue from first principles.
- Reviewing or superseding the remaining historical `596` Wave911-focused rows.
- Runtime gameplay behavior, exact layouts, BEA patching behavior, gameplay outcomes, visual QA, and clean-room rebuild parity.
