# Original Binary Second-Host Runtime Executor Readiness

Status: builder ready, live promotion blocked by source-bound distinct command-source runtime proof
Date: 2026-06-20
Schema: `winui-original-binary-second-host-runtime-executor.v1`
Scope: `second-host-command-source-to-fresh-copied-runtime-executor-not-player-ready-online`

This slice adds a public-safe runtime executor contract/readiness note plus private release-denied builder/checker tooling. The tooling can bind a checker-accepted second-host P2 command-source proof to a host-authority P1/P2 proof, run the existing copied-BEA runtime executor in live mode, and emit a private proof. Live promotion is intentionally blocked unless the second-host command-source proof carries `evidenceMode=live-server-client-transcript`, the full command-source checker hardening contract, signed request/response payload hashes tied to the observed transcript, and source-binding evidence across the second-host proof, host-authority proof, bridge proof, and runtime executor proof.

Evidence:

| Item | Value |
| --- | --- |
| Contract | `roadmap/original-binary-online-second-host-runtime-executor.v1.json` |
| Builder | `tools/build_winui_original_binary_second_host_runtime_executor_bundle.py` |
| Checker | `tools/winui_safe_copy_online_second_host_runtime_executor_check.py` |
| Helper tool release class | `R4_DENY` private runtime tooling |
| Focused script | `test:winui-original-binary-second-host-runtime-executor` |
| Builder readiness | `runtimeExecutorBuilderReady=true` |
| Live second-host runtime delivery | `acceptedLiveSecondHostRuntimeDeliveryProof=false` |
| Runtime driven by second-host command source | `runtimeDrivenBySecondHostCommandSource=false` |
| Upstream private-LAN proof binding | `sourceBinding.upstreamPrivateLanProofHashMatch=true` |
| Invitation lifecycle binding | `sourceBinding.secondHostInvitationLifecycleSha256` |
| Same-bundle bridge ownership | `bridgeProofSameBundleOwnership=true` |
| Base online readiness | `baseOnlineMultiplayerReady=false` |
| Private proof release boundary | `privateProofReleaseExcludedByPolicy=true` |
| Secure N-slot runtime executor warmup handling | Retries only the exact first-baseline `wait window 1 had no render movement samples` CDB warmup miss when later wait/input windows already contain render samples; final accepted proof still requires the unchanged movement-state validator |

Required before live promotion:

- `badHmacLiveRejected=true`
- `replayNonceLiveRejected=true`
- `timestampWindowLiveEnforced=true` for stale and future timestamps relative to server-observed time and the configured nonce window
- `sequenceOrderLiveEnforced=true`
- `pinnedIdentityLiveEnforced=true` for wrong server pin and wrong client pin
- `compatibilityKeyLiveEnforced=true`
- `metadataSlotGameplayLiveRejected=true`
- `preSessionCommandLiveRejected=true`
- `directInputBypassLiveRejected=true`
- `sourceBinding.requiredBeforeAcceptedLiveRuntimeDelivery=true`
- `sourceBinding.sessionCompatibilityKeyMatch=true` before live promotion
- `sourceBinding.cleanSpecimenHashMatch=true`
- `sourceBinding.upstreamPrivateLanProofHashMatch=true`
- `bridgeProofSameBundleOwnership=true`; the bridge proof's second-host, host-authority, private remote-client, runtime-executor, runtime-delivery, and live-runtime artifact references must resolve back to the same enclosing executor bundle
- `sourceBinding.acceptedSecondHostCommandPayloadSha256` matches the accepted second-host command envelope
- `sourceBinding.acceptedSecondHostCommandRequestEvent=client_command_p2_forward`
- `sourceBinding.acceptedSecondHostCommandRequestPayloadSha256` matches the accepted command-source transcript request hash
- `sourceBinding.acceptedSecondHostCommandResponseEvent=server_command_accepted`
- `sourceBinding.acceptedSecondHostCommandResponsePayloadSha256` matches the accepted command-source transcript response hash
- `sourceBinding.secondHostNetworkIdentityEvidenceSha256`, `sourceBinding.secondHostSourceSafetySha256`, and `sourceBinding.secondHostAuthorizationSha256` match the second-host proof
- `sourceBinding.secondHostInvitationLifecycleSha256`, `sourceBinding.secondHostInvitationLifecycleDeleted=true`, and `sourceBinding.secondHostInvitationLifecyclePostDeleteAbsent=true` match the second-host proof
- `mappedP2SequenceReceipt` is file-backed by the runtime input-window artifact and `hostHelperDeliveryReceipt` is file-backed by the exact-PID CDB artifact
- runtime/CDB raw bodies carry mapped sequence `down:E,wait:500,up:E`, route `P2/inputDevice1/bottom-split-half`, input device `1`, host-helper source binding, and positive P2 button/state rows
- live mode requires second-host `sourceSafety.evidenceMode=local-preflight-computed` with host/client non-operator copied-profile and source-install hashes

Boundaries:

- Self-test mode uses fixtures only and does not launch BEA.
- Live mode must use copied BEA only and exact-PID CDB evidence.
- Live compatibility proof must keep `runtimeInputDerivedFromSecondHostCommandSource=false`, `runtimeDrivenBySecondHostCommandSource=false`, and `acceptedLiveSecondHostRuntimeDeliveryProof=false` until a direct second-host payload/session receipt is carried through scheduler, bridge, runtime, and CDB input windows.
- Host/Join remains disabled.
- No public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, active P3/P4 gameplay, or player-ready online play is claimed.
