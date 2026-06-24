# Original Binary Multiplayer Outcome Semantics Matrix Readiness Note

Status: complete public-safe static candidate matrix, not runtime proof
Date: 2026-06-19
Scope: `original-binary-p1p2-multiplayer-outcome-semantics-matrix-not-runtime-proof`

This slice adds `roadmap/original-binary-online-multiplayer-outcome-semantics-matrix.v1.json` and checker `tools/winui_safe_copy_online_multiplayer_outcome_semantics_matrix_check.py`.

Matrix result:

- Schema: `winui-original-binary-multiplayer-outcome-semantics-matrix.v1`
- Proof class: `static-candidate-matrix-not-runtime-outcome-proof`
- Candidate levels: `851`, `854`, `855`, `860`
- Selected runtime candidate: `854`
- Required hook target count: `10`
- Runtime proof created by this matrix: `false`
- `modeRuntimeProofSlicesAdded=0`
- `coOpVersusModeRuntimeProofSlicesAdded=0`
- `newBeaLaunchCount=0`
- `cdbAttachCount=0`
- `nPlayerOriginalBinaryRuntimeProof=0`

Representative hook anchors:

| Name | Address |
| --- | --- |
| `CGame__MPDeclarePlayerWon` | `0x0046f360` |
| `CGame__MPDeclareGameDrawn` | `0x0046f3e0` |
| `CGame__DeclarePlayerDead` | `0x0046f550` |
| `CGame__RespawnPlayer` | `0x00470120` |
| `CGame__GetPlayerLives` | `0x004725f0` |
| `CGame__DeclareLevelWon` | `0x0046f2f0` |
| `CGame__DeclareLevelLost` | `0x0046f430` |

Boundary:

This is a public-safe static matrix selecting level `854` as the first P1/P2 copied-runtime multiplayer outcome-semantics candidate. It does not launch BEA, attach CDB, prove outcome transitions, prove co-op, prove versus, prove online play, prove matchmaking, prove native BEA netcode, prove active P3/P4 gameplay, prove deterministic sync, prove rollback, prove anti-cheat, or prove rebuild/no-noticeable-difference parity.

Validation:

- `py -3 tools\winui_safe_copy_online_multiplayer_outcome_semantics_matrix_check_test.py`: PASS
- `py -3 tools\winui_safe_copy_online_multiplayer_outcome_semantics_matrix_check.py --self-test`: PASS
- `py -3 tools\winui_safe_copy_online_multiplayer_outcome_semantics_matrix_check.py --check`: PASS
- `npm run test:winui-original-binary-multiplayer-outcome-semantics-matrix`: PASS
