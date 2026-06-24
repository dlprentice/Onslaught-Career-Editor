# Original Binary Host-Authority Runtime Executor Readiness Note

Status: complete bounded executor-chain proof
Date: 2026-06-19
Scope: `winui-original-binary-host-authority-runtime-executor`

This slice proves executor provenance for the same-workstation host-authority P1/P2 runtime-delivery lane. The hardened executor read the accepted host-authority two-client scheduler proof, derived the live input plan from `hostAuthorityScheduler.relayPlan`, launched a copied level-850/config-1 BEA host through the safe-copy live harness, built the runtime-delivery proof bundle, and then validated the executor receipt.

Accepted executor evidence:

| Field | Evidence |
| --- | --- |
| Executor mode | `live-executor-subprocess` |
| Environment boundary | `childEnvSensitiveKeyCount=0`; child environment was allowlisted before launching the live smoke harness. |
| Freshness boundary | `executorRecordsFreshSameRootArtifacts=true`; the live runtime artifact and runtime-delivery proof were created under the same ignored proof root. |
| Clean specimen boundary | `overrideHashBefore=74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, matching the scheduler/session clean specimen. |
| Derived input sequence | `wait:300`, `down:Q,wait:500,up:Q`, `wait:300`, `down:E,wait:500,up:E`. |
| Relay plan hash | `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`. |
| Runtime-delivery bundle hash | `a79618c7ccdd8312c2da2af125f939451e62a8d3f1377b94c94cee84080400c3`. |
| Runtime players | P1 `<runtime-p1-pointer-redacted>`; P2 `<runtime-p2-pointer-redacted>`. |
| Runtime rows | P1 `button31ReceiveRows=11`, `forwardStateStoreRows=11`; P2 `button31ReceiveRows=11`, `forwardStateStoreRows=11`. |
| Delivery boundary | `deliveredOriginalBinaryCommandCount=2`; `gameInputSentByScheduler=false`; `hostHelperInputSent=true`; `nPlayerOriginalBinaryRuntimeProof=0`. |
| Visual/source safety | `visualCaptureCount=7`; installed executable, clean override executable, and source save/options hashes were unchanged; managed stop completed with no BEA/CDB process left running. |

Validation:

```powershell
py -3 tools\winui_safe_copy_online_host_authority_runtime_executor_check.py --self-test
py -3 tools\winui_safe_copy_online_host_authority_runtime_executor_check.py <private-executor-proof>
npm run test:winui-original-binary-host-authority-runtime-executor
```

No Ghidra mutation or Ghidra backup was required for this runtime proof slice.

Non-claims: this does not prove more than two original-binary runtime players, does not prove active P3/P4 original-binary gameplay, does not prove co-op or versus online mode semantics, does not prove multi-host LAN play, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic sync, rollback, anti-cheat, physical gamepad behavior, improved control feel, rebuild parity, or no-noticeable-difference online parity.
