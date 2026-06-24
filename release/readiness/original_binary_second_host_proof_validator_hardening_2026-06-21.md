# Original Binary Second-Host Proof Validator Hardening

Status: validation hardening only; no accepted live second-host proof
Date: 2026-06-21
Scope: `second-host-proof-validator-hardening-not-netplay-proof`

This slice hardens the original-binary online proof gates after adversarial review. It does not run BEA, attach CDB, mutate Ghidra, patch an executable, enable Host/Join, publish a public endpoint, or claim player-ready online multiplayer.

Hardened gates:

- `tools/winui_safe_copy_online_second_host_command_source_check.py`
- `tools/winui_safe_copy_online_second_host_runtime_causality_check.py`
- `roadmap/original-binary-online-second-host-command-source.v1.json`
- `roadmap/original-binary-online-second-host-runtime-causality.v1.json`

Command-source hardening:

- Normal fixture/shape validation remains non-promotional.
- Future live command-source candidates must pass `py -3 tools\winui_safe_copy_online_second_host_command_source_check.py <private-bundle> --live`.
- `--live` requires `sessionSecurityHardening.evidenceMode=live-server-client-transcript`, signed request/response payload hashes from the observed transcript, per-event monotonic `serverObservedAtUnix` timestamps inside the invitation window, `sourceSafety.evidenceMode=local-preflight-computed`, local host/client source evidence, `machineFingerprintSource=local-hostname-platform-preflight`, `runtimeHostKindSource=auto-platform-preflight`, and file-counted copied-profile/source-install hashes.
- `--live` rejects fixture sentinel auth/identity/source hashes, fixture timestamps/addresses, and hidden Host/Join-style overclaims expressed as string or numeric truthy values.

Runtime-causality hardening:

- File-backed self-test candidates now require explicit fixture mode and return no live-delivery proof booleans.
- Future live candidates must carry concrete `rawEvidenceBody` fields for command-source transcript hardening, scheduler relay-plan evidence, bridge mapping, runtime input-window rows, exact-PID CDB log rows, copied-runtime artifact rows, copied-executable byte hash, and process identity.
- Future live candidates must file-back `mappedP2SequenceReceipt` to the runtime input-window artifact and `hostHelperDeliveryReceipt` to the exact-PID CDB artifact; those aliases must share the run id, accepted command payload hash, and invitation lifecycle hash.
- JSON-only forged live-looking artifacts, private-path-leaking artifacts, receipt-only/envelope-only artifacts, fixture/posthoc artifacts, and Host/Join overclaims are rejected.

Current truth remains:

- `acceptedLiveSecondHostCommandSourceProof=false`
- `acceptedLiveSecondHostRuntimeCausalityProof=false`
- `acceptedLiveSecondHostRuntimeDeliveryProof=false`
- `runtimeDrivenBySecondHostCommandSource=false`
- `hostJoinControlsMayBeEnabled=false`
- `baseOnlineMultiplayerReady=false`
- `multiHostLanPlayProof=false`
- `publicMatchmakingProof=false`
- `nativeBeaNetcodeProof=false`
- `activeP3P4OriginalBinaryGameplayProof=false`
- `nPlayerOriginalBinaryRuntimeProof=0`

Focused validation:

```powershell
npm run test:winui-original-binary-second-host-command-source
npm run test:winui-original-binary-second-host-runtime-causality
npm run test:winui-original-binary-host-join-enablement
```

Next proof boundary: run a real distinct private-LAN host or explicitly VM-labeled command-source candidate, validate it with `--live`, then bind that accepted command source through scheduler, bridge, copied-runtime input-window, and exact-PID CDB receipts accepted by the runtime-causality gate.
