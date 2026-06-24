# Original Binary Host-Authority Secure N-Slot Runtime Executor Replayability Readiness Note

Status: complete bounded copied-runtime replayability proof
Date: 2026-06-19
Scope: `original-binary-host-authority-secure-n-slot-runtime-executor-replayability`

The secure N-slot runtime executor replayability proof revalidates the previous secure N-slot session-derived executor path across two distinct copied `BEA.exe` level-850/config-1 host-helper runs. Both proofs consumed the same accepted same-workstation session-security smoke proof, derived the same P1/P2 relay input sequence, launched exactly one copied runtime per proof, attached CDB to the managed process, captured bounded split-screen frames, and stopped the managed copied process. The installed Steam game folder and original executable were not mutated.

Public-safe accepted summary:

| Field | Value |
| --- | --- |
| Schema | `winui-original-binary-host-authority-secure-n-slot-runtime-executor-replayability.v1` |
| Protocol | `host-authority-secure-n-slot-runtime-executor-replayability.v1` |
| Proof count | `2` |
| Replayability proven | `secureNSlotRuntimeExecutorReplayabilityProven=true` |
| Proof SHA-256 values | `4a2b3814112931a60fb58ebfc424fe4382e19701c0f3a16200f3b4b4806b4df1`; `8ef72707fd57a6c4ad9e65d3f03e1c21dd945e72bfbb3c3c87f5ddfd3c5d1e0d` |
| Session-security proof SHA-256 | `3c0d0e15c23fa3644afcd937dc3c53df6d703301ec8ccffc9e665ea4f182711b` |
| Live runtime artifact SHA-256 values | `cdfb399e3a058ad9b0f9080ff446c8887fdfe0b44c3ca52c32bd0497febaae3f`; `8db116a2b68c0100dc7a6bc49e29df9c9167aee2e6d41aa8a356e438bf9cb877` |
| Security proof scope | `same-workstation-session-security-smoke-not-online-gameplay-proof` |
| Session relay plan SHA-256 | `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002` |
| Runtime-compatible P1/P2 relay SHA-256 | `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376` |
| Derived input sequence | `wait:300`; `down:Q,wait:500,up:Q`; `wait:300`; `down:E,wait:500,up:E` |
| Accepted original-binary gameplay slots | `acceptedOriginalBinaryGameplaySlots=P1,P2` |
| Metadata-only slots | `metadataOnlySlots=P3,P4` |
| Rejected gameplay-route slots | `rejectedGameplayRouteSlots=P3,P4` |
| Secure session accepted command count | `secureSessionAcceptedCommandCount=2` |
| Secure session metadata rejection count | `secureSessionMetadataRejectionCount=2` |
| Secure session security rejection count | `secureSessionSecurityRejectionCount=25` |
| Delivered original-binary command count per proof | `deliveredOriginalBinaryCommandCountPerProof=2` |
| Host helper input | `hostHelperInputSent=true` |
| Scheduler direct game input | `gameInputSentByNSlotScheduler=false` |
| New BEA launch count per proof | `newBeaLaunchCountPerProof=1` |
| CDB attach count per proof | `cdbAttachCountPerProof=1` |
| Distinct runtime evidence | `distinctLiveRuntimeArtifactHashes=true`; `distinctRuntimeArtifactPaths=true`; `distinctProcessIds=true`; `distinctCdbLogs=true`; `distinctCdbLogHashes=true`; `distinctRuntimePointerTuples=true` |
| N-player original-binary runtime proof | `nPlayerOriginalBinaryRuntimeProof=0` |
| Active P3/P4 original-binary gameplay proof | `activeP3P4OriginalBinaryGameplayProof=false` |
| Visible movement claim | `visibleMovementDeltaClaim=false` |

This proof proves repeated same-workstation secure-session-derived P1/P2 copied-runtime executor artifacts with distinct live runtime hashes, process IDs, CDB logs, runtime paths, and runtime player tuples. This proof does not prove visible movement causality, multi-host LAN play, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, more than two original-binary runtime players, co-op/versus online semantics, deterministic sync, rollback, anti-cheat, physical gamepad behavior, production server identity, rebuild parity, or no-noticeable-difference online parity.

Validation:

```powershell
py -3 tools\winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_replayability_check_test.py
py -3 tools\winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_replayability_check.py --self-test
py -3 tools\winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_replayability_check.py <private-proof-json-1> <private-proof-json-2>
npm run test:winui-original-binary-host-authority-secure-n-slot-runtime-executor-replayability
```

Release-boundary tokens: `rawPrivateProofPathPublished=false`; `rawPrivateArtifactContentPublished=false`; `absolutePrivatePathPublished=false`; `privateRuntimePointerRows=0`; `releaseIncludedPrivateArtifact=false`.
