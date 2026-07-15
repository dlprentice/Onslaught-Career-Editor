# Runtime proof lab retention (tracked summary)

Status: active  
Last updated: 2026-07-14

## Rule

**Safe-copy while running. Compact evidence after closeout.**

| Phase | Action |
|-------|--------|
| Live run | Operate only on copied targets / app-owned profile roots. Never patch Steam or original `BEA.exe`. |
| After closeout | Delete full `profile-app-config` game trees and private runner `bin`/`obj` junk. |
| Durable science | Keep metrics, raw sample JSON (if small), receipts, digests, and **tracked** public contracts under `reverse-engineering/`. |

Ignored lab roots (`local-proofs/`, `game/`, `local-lab/`) may hold temporary copies. They are not the long-term archive of multi-GB duplicates per attempt.

## Scalar measurement precedent

Accepted walker measurement:
[walker-forward-scalar-response-v2.json](walker-forward-scalar-response-v2.json).

Accepted jet measurement:
[jet-forward-scalar-response-v1.json](jet-forward-scalar-response-v1.json)
(private label `jet-p06`).

Private full-profile pair directories are pruned after compact closeout retention;
do not re-hoard multi-GB trees.

## Implementation

Shipped helpers (unit-tested, no live BEA):

- `tools/runtime_proof_lab_hygiene.py`
  - `strip_bulky_attempt_tree` — deletes `profile-app-config` under an attempt
  - `strip_runner_build_junk` — deletes `runner/bin` and `runner/obj`
  - `strip_pair_private_root` — both of the above for a pair root
  - `materialize_from_durable_lab_base` — copy a durable lab profile base into an
    attempt dest (both must sit strictly under the authorized private root)

The walker two-attempt runner (`run_battleengine_walker_trajectory_measurement.py`)
calls strip after each validated attempt closeout and strips runner junk at pair
end. Compact evidence under `evidence/` is retained.

### Keep

- `walker-trajectory-raw.json`, `walker-trajectory-metrics.json`,
  `observer-status.json`, `runtime-process-receipt.json`, attempt/pair closeouts,
  focus/harness receipts, tracked public contracts under `reverse-engineering/`

### Delete after closeout

- `profile-app-config/**` (full game trees)
- `runner/bin/**`, `runner/obj/**`

### Never

- Steam install / original `BEA.exe`
- Paths outside the authorized private root
