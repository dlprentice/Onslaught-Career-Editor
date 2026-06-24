# Original Binary Host-Authority N-Slot Concurrent Process Smoke Readiness Note

Status: complete bounded same-workstation-client/private-interface concurrent process-layer proof
Date: 2026-06-19
Scope: `original-binary-host-authority-n-slot-concurrent-process-smoke`

This slice adds a sibling proof class for the original-binary online ladder: `winui-original-binary-host-authority-n-slot-concurrent-process-smoke.v1`. It does not replace the earlier sequential N-slot process smoke. It proves a same-workstation-client/private-interface host-authority process layer can hold four separate slot-scoped client processes and four socket connections behind an explicit barrier while still routing only P1/P2 into the original-binary relay plan. The listener is private-LAN reachable during the run and foreign peers are rejected after accept; this is not a same-workstation-only network proof.

Accepted private artifact:

| Field | Value |
| --- | --- |
| Artifact | `subagents/winui-safe-copy-live-runtime/online-host-authority-n-slot-concurrent-process-smoke-20260619-focus1/host-authority-n-slot-concurrent-process-smoke-proof.json` |
| Artifact SHA-256 | `7458bbafcca8fbb60f0b7750fac068b7a6dcdfe59b13980f54da081832f95896` |
| Schema | `winui-original-binary-host-authority-n-slot-concurrent-process-smoke.v1` |
| Protocol | `host-authority-n-slot-input.v1` |
| Transport | `host-authority-n-slot-tcp-jsonl-concurrent-process-smoke` |
| Client process model | `four-separate-python-client-processes` |
| Process concurrency | `processConcurrencyModel=barrier-concurrent-client-processes`; `simultaneousClientProcessesProven=4` |
| Barrier proof | `clientReadyBeforeBarrierReleaseCount=4`; `barrierReleaseAfterAllClientsReady=true` |
| Socket proof | `maxSimultaneousSocketConnectionsProven=4`; `privateLanReachableDuringRun=true`; `foreignPeersRejectedAfterAccept=true` |
| Network/process boundary | `sameWorkstationClientProcessesOnly=true`; `sameWorkstationNetworkOnly=false` |
| Process identity | `clientProcessCount=4`; `clientProcessIdsDistinctFromBuilder=true`; `clientProcessIdsDistinctFromEachOther=true` |
| Credential boundary | `credentialTransportToClientProcesses=stdin-ephemeral-not-serialized-to-artifact`; `clientEnvSensitiveKeyCount=0` |
| Security boundary | `securityProofScope=minimal-smoke-hmac-envelope-not-full-session-security-proof`; `sessionScopedMacCoverageProof=false`; `maxJsonLineBytesEnforced=false`; `unknownFieldRejectionProof=false`; `strictMessageSchemaProof=false` |
| Session slots | `slotCapacity=4`; `acceptedSessionParticipantCount=4`; `arrivalOrder=P4,P2,P3,P1`; `deterministicParticipantOrder=P1,P2,P3,P4` |
| Runtime relay boundary | `deterministicOriginalBinaryRelayOrder=P1,P2`; `acceptedOriginalBinaryGameplaySlots=P1,P2`; `metadataOnlySlots=P3,P4`; `rejectedGameplayRouteSlots=P3,P4` |
| Command counts | `acceptedOriginalBinaryGameplayCommandCount=2`; `rejectedOriginalBinaryGameplayCommandCount=2`; rejection policy `required-for-unproven-original-binary-slots` |
| Relay hashes | `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002`; `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376` |
| Runtime boundary | `gameInputSentByNSlotScheduler=false`; `hostHelperInputSent=false`; `newBeaLaunchCount=0`; `cdbAttachCount=0` |

What this proves:

- Four separate local client processes reached a parent-observed ready barrier before release.
- All four processes remained alive at release.
- Four private-interface socket connections overlapped in the host-authority layer; the listener was private-LAN reachable during the run and foreign peers were rejected after accept.
- P1 and P2 commands were accepted into the existing original-binary relay plan.
- P3 and P4 were accepted only as metadata participants, and their gameplay commands were rejected with `required-for-unproven-original-binary-slots`.
- The HMAC layer is a minimal smoke envelope, not a full session-security proof.

What this does not prove:

- `nPlayerOriginalBinaryRuntimeProof=0`.
- `activeP3P4OriginalBinaryGameplayProof=false`.
- `permanentImpossibilityClaim=false`.
- This does not prove active P3/P4 original-binary gameplay.
- This does not prove more than two original-binary runtime players.
- This does not prove co-op/versus runtime semantics.
- This does not prove multi-host LAN play.
- This does not prove public matchmaking.
- This does not prove native BEA netcode.
- This does not prove full session-scoped MAC coverage, max-message-size enforcement, strict schema allowlists, or unknown-field rejection.
- This does not prove deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

Validation:

- `py -3 -m py_compile tools\winui_safe_copy_online_host_authority_n_slot_concurrent_process_smoke_check.py tools\build_winui_original_binary_host_authority_n_slot_concurrent_process_smoke_bundle.py`
- `py -3 tools\winui_safe_copy_online_host_authority_n_slot_concurrent_process_smoke_check.py --self-test`
- `py -3 tools\build_winui_original_binary_host_authority_n_slot_concurrent_process_smoke_bundle.py --output subagents\winui-safe-copy-live-runtime\online-host-authority-n-slot-concurrent-process-smoke-20260619-focus1\host-authority-n-slot-concurrent-process-smoke-proof.json --bind-host <private-non-loopback-host>`
- `py -3 tools\winui_safe_copy_online_host_authority_n_slot_concurrent_process_smoke_check.py subagents\winui-safe-copy-live-runtime\online-host-authority-n-slot-concurrent-process-smoke-20260619-focus1\host-authority-n-slot-concurrent-process-smoke-proof.json`
- `npm run test:winui-original-binary-host-authority-n-slot-concurrent-process-smoke`

No Ghidra mutation, no Ghidra backup, no executable-byte mutation, no BEA launch, no CDB attach, no copied-game input, and no Steam install change occurred in this slice.
