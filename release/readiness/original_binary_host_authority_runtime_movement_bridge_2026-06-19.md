# Original Binary Host-Authority Runtime Movement Bridge Readiness Note

Status: complete bounded movement-state bridge proof
Date: 2026-06-19
Scope: `winui-original-binary-host-authority-runtime-movement-bridge`

This slice proves a narrower but stronger runtime-state bridge for the same-workstation host-authority P1/P2 lane. The accepted host-authority runtime executor proof was revalidated, then its live copied BEA level-850/config-1 runtime artifact was checked with the stricter movement-state delta checker. The result links the accepted scheduler relay plan to exact-PID CDB render-window movement-state deltas for the matching P0/P1 routes.

Accepted bridge evidence:

| Field | Evidence |
| --- | --- |
| Bridge protocol | `host-authority-runtime-movement-bridge.v1` |
| Derived input sequence | `wait:300`, `down:Q,wait:500,up:Q`, `wait:300`, `down:E,wait:500,up:E`. |
| Relay plan hash | `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`. |
| Runtime players | P1 `<runtime-p1-pointer-redacted>`; P2 `<runtime-p2-pointer-redacted>`. |
| Q/P0 route | `inputDevice0`; `button31ReceiveRows=11`; `forwardStateStoreRows=11`; `baselineRenderSamples=181`; `targetRenderSamples=213`; `targetPositionChanged=true`; `targetVelocityChanged=true`; `targetDiffersFromAdjacentBaseline=true`. |
| E/P1 route | `inputDevice1`; `button31ReceiveRows=11`; `forwardStateStoreRows=11`; `baselineRenderSamples=104`; `targetRenderSamples=183`; `targetPositionChanged=true`; `targetVelocityChanged=true`; `targetDiffersFromAdjacentBaseline=true`. |
| Delivery boundary | `deliveredOriginalBinaryCommandCount=2`; `gameInputSentByScheduler=false`; `hostHelperInputSent=true`; `nPlayerOriginalBinaryRuntimeProof=0`; `visibleMovementDeltaClaim=false`. |
| Safety boundary | Existing accepted executor proof kept `visualCaptureCount=7`, clean override hash identity, managed stop, and no remaining BEA/CDB process. No new BEA launch was needed for this bridge check. |

Validation:

```powershell
py -3 tools\winui_safe_copy_online_host_authority_runtime_movement_bridge_check.py --self-test
py -3 tools\winui_safe_copy_online_host_authority_runtime_movement_bridge_check.py <private-executor-proof>
npm run test:winui-original-binary-host-authority-runtime-movement-bridge
```

Diagnostic note: the strict visible movement-delta checker rejected this artifact because the Q/P0 target visual delta did not exceed the adjacent no-input baseline. This bridge therefore accepts exact-PID CDB movement-state deltas only; it does not claim visible movement causality.

No Ghidra mutation or Ghidra backup was required for this runtime proof slice.

Non-claims: this does not prove visible movement causality; does not prove improved control feel; does not prove physical gamepad behavior; does not prove more than two original-binary runtime players; does not prove active P3/P4 original-binary gameplay; does not prove co-op or versus online mode semantics; does not prove multi-host LAN play; does not prove public matchmaking; does not prove public relay/server behavior; does not prove native BEA netcode; does not prove NAT traversal; does not prove deterministic sync; does not prove rollback; does not prove anti-cheat; does not prove rebuild parity; and does not prove no-noticeable-difference online parity.
