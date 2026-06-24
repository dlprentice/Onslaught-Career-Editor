# Original Binary Host-Authority Secure N-Slot Runtime Executor Readiness Note

Status: complete bounded copied-runtime proof
Date: 2026-06-19
Scope: `original-binary-host-authority-secure-n-slot-runtime-executor`

The secure N-slot runtime executor proof advances the previous provenance-only bridge into one fresh copied `BEA.exe` runtime observation. The executor consumed an accepted same-workstation N-slot session-security smoke proof, derived the P1/P2 relay input sequence from that proof, launched one copied level-850/config-1 host through the safe-copy live harness, attached CDB to the exact managed process, captured bounded split-screen frames, and stopped the managed copied process. The installed Steam game folder and original executable were not mutated.

Public-safe accepted summary:

| Field | Value |
| --- | --- |
| Schema | `winui-original-binary-host-authority-secure-n-slot-runtime-executor.v1` |
| Protocol | `host-authority-secure-n-slot-runtime-executor.v1` |
| Proof SHA-256 | `4a2b3814112931a60fb58ebfc424fe4382e19701c0f3a16200f3b4b4806b4df1` |
| Session-security proof SHA-256 | `3c0d0e15c23fa3644afcd937dc3c53df6d703301ec8ccffc9e665ea4f182711b` |
| Live runtime artifact SHA-256 | `cdfb399e3a058ad9b0f9080ff446c8887fdfe0b44c3ca52c32bd0497febaae3f` |
| Security proof scope | `same-workstation-session-security-smoke-not-online-gameplay-proof` |
| Session relay plan SHA-256 | `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002` |
| Runtime-compatible P1/P2 relay SHA-256 | `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376` |
| Derived input sequence | `wait:300`; `down:Q,wait:500,up:Q`; `wait:300`; `down:E,wait:500,up:E` |
| Accepted original-binary gameplay slots | `acceptedOriginalBinaryGameplaySlots=P1,P2` |
| Metadata-only slots | `metadataOnlySlots=P3,P4` |
| Rejected gameplay route slots | `rejectedGameplayRouteSlots=P3,P4` |
| Secure accepted command count | `secureSessionAcceptedCommandCount=2` |
| Secure metadata rejection count | `secureSessionMetadataRejectionCount=2` |
| Secure security rejection count | `secureSessionSecurityRejectionCount=25` |
| Delivered original-binary command count | `deliveredOriginalBinaryCommandCount=2` |
| Host helper input | `hostHelperInputSent=true` |
| Scheduler direct game input | `gameInputSentByNSlotScheduler=false` |
| New BEA launch count | `newBeaLaunchCount=1` |
| CDB attach count | `cdbAttachCount=1` |
| Visual captures | `visualCaptureCount=7` |
| Original-binary N-player runtime proof | `nPlayerOriginalBinaryRuntimeProof=0` |
| Active P3/P4 gameplay proof | `activeP3P4OriginalBinaryGameplayProof=false` |
| Visible movement claim | `visibleMovementDeltaClaim=false` |

Runtime movement-state evidence was positive at the CDB/state-observer layer for the P1/Q and P2/E windows. The public note intentionally redacts exact runtime pointers, local artifact paths, process ids, debugger-log locations, and copied-game locations.

This proof does not prove multi-host LAN play, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, more than two original-binary runtime players, co-op/versus online semantics, deterministic sync, rollback, anti-cheat, physical gamepad behavior, production server identity, rebuild parity, or no-noticeable-difference online parity.

Validation:

```powershell
py -3 tools\winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_check_test.py
py -3 tools\winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_check.py --self-test
py -3 tools\winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_check.py <private-proof-json>
npm run test:winui-original-binary-host-authority-secure-n-slot-runtime-executor
```

Release-boundary tokens: `rawPrivateProofPathPublished=false`; `rawPrivateArtifactContentPublished=false`; `absolutePrivatePathPublished=false`; `privateRuntimePointerRows=0`; `releaseIncludedPrivateArtifact=false`.
