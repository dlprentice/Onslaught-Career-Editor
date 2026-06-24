# Original Binary Second-Host Runtime Promotion Guard

Status: public-safe no-BEA shape preflight accepted
Date: 2026-06-21
Scope: `source-bound-second-host-command-to-copied-runtime-causality-not-host-join-enable`

This slice adds a shape preflight for the next Host/Join-grade proof rung. It prevents the current second-host runtime executor compatibility artifact from being promoted into `host-runtime-delivery-from-source-bound-distinct-command-source`. The promotion guard does not accept live runtime proof by itself; file-backed runtime-causality validation owns that decision.

Tracked artifacts:

| Artifact | Purpose |
| --- | --- |
| `tools/winui_safe_copy_online_second_host_runtime_promotion_guard.py` | Defines the stricter source-bound second-host-to-runtime causality shape preflight. |
| `tools/winui_safe_copy_online_second_host_runtime_promotion_guard_test.py` | Regression tests proving the current compatibility executor is rejected and a future fully source-bound fixture shape passes preflight without becoming live proof. |
| `roadmap/original-binary-online-host-join-enablement.v1.json` | Now requires the promotion guard and same-run payload-hash receipts before Host/Join enablement. |

Required before this guard can preflight a future runtime causality candidate:

- `runtimeInputDerivedFromSecondHostCommandSource=true`
- `runtimeDrivenBySecondHostCommandSource=true`
- candidate-declared live runtime-delivery proof field is affirmative (preflight input only; current accepted proof remains false until the file-backed runtime-causality gate accepts source-bound raw evidence)
- accepted second-host request payload hash bound in scheduler receipt
- accepted second-host request payload hash bound in bridge receipt
- accepted second-host request payload hash bound in runtime input-window receipt
- accepted second-host request payload hash bound in exact-PID CDB receipt
- mapped P2 sequence receipt bound to the runtime input-window artifact
- host-helper delivery receipt bound to the exact-PID CDB artifact
- one same-run artifact chain
- no fixture, self-test, or posthoc compatibility binding

Required before a future candidate can become live runtime causality proof:

- the stricter runtime-causality gate must recompute file-backed raw-artifact receipts from disk
- `mappedP2SequenceReceipt` must hash-match the runtime input-window artifact and share the same run id, accepted command payload hash, and invitation lifecycle hash
- `hostHelperDeliveryReceipt` must hash-match the exact-PID CDB artifact and share the same run id, accepted command payload hash, and invitation lifecycle hash
- runtime input-window and exact-PID CDB raw bodies must carry mapped sequence `down:E,wait:500,up:E`, route `P2/inputDevice1/bottom-split-half`, input device `1`, host-helper source binding, and positive P2 button/state rows

Current truth remains:

- the existing second-host runtime executor is compatibility/source-binding evidence only
- `hostJoinControlsMayBeEnabled=false`
- `baseOnlineMultiplayerReady=false`
- `acceptedLiveSecondHostRuntimeDeliveryProof=false`
- `runtimeDrivenBySecondHostCommandSource=false`
- `publicMatchmakingProof=false`
- `nativeBeaNetcodeProof=false`
- `activeP3P4OriginalBinaryGameplayProof=false`

Validation:

```powershell
npm run test:winui-original-binary-second-host-runtime-promotion-guard
npm run test:winui-original-binary-host-join-enablement
```

This is not a BEA launch, CDB attach, new runtime artifact, live second-host LAN proof, Host/Join implementation, player-ready online multiplayer, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference proof.
