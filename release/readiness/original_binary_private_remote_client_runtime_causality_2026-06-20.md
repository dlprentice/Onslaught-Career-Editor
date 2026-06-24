# Original Binary Private Remote-Client Runtime Causality Proof

Status: accepted private proof wrapper over existing copied-runtime evidence
Date: 2026-06-20
Scope: `private-remote-client-to-runtime-executor-same-workstation-not-online-play`

This proof links the existing same-workstation process-separated private remote-client command-source smoke to the accepted host-authority scheduler and the accepted relay-plan-driven copied-runtime executor proof. It does not launch a new BEA process; it revalidates the private source artifacts and records the causality path from the accepted private remote-client P2 command into the already accepted level-850/config-1 copied runtime executor chain.

No Ghidra mutation occurred.

Path-safety follow-up: source artifact references are `privateProofRootRelative=true`; `absoluteSourceArtifactPathRejected=true`; `sourceArtifactEscapesPrivateProofRootRejected=true`.

Accepted evidence:

| Field | Value |
| --- | --- |
| Schema | `winui-original-binary-private-remote-client-runtime-causality.v1` |
| Private remote-client proof hash | `7ff37d8886044dbbd3c5a749b5af1a4643ae82b5a3dc4aa5ab5ca48c964f4d04` |
| Host-authority two-client proof hash | `1c6b3c593caceb2f472dd0de9f0d302bd43c7dc13419ffc0d55234535835310c` |
| Runtime executor proof hash | `cecc4d9868c02014d709b34b8170b91b5f6fd085c346cf50b9bb55352d7345fa` |
| Runtime delivery proof hash | `a79618c7ccdd8312c2da2af125f939451e62a8d3f1377b94c94cee84080400c3` |
| Live runtime artifact hash | `bad167001bd970e8c3d610f8fdebf0ef93a36e2b2ad26e2748b2cf064d1a1a89` |
| Host relay plan hash | `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376` |

Machine-checked tokens:

- `privateRemoteClientRuntimeCausalityProven=true`
- `remoteClientAcceptedCommandId=private-remote-client-p2-forward-0001`
- `remoteClientProcessSeparated=true`
- `sameWorkstationOnly=true`
- `remoteClientWouldForwardToPrivateLanCommandId=private-lan-p2-forward-0001`
- `remoteClientToHostRelayPathMatchCount=1`
- `hostRelayToRuntimeExecutorPathMatchCount=1`
- `newBeaLaunchCount=1`
- `cdbAttachCount=1`
- `visualCaptureCount=7`
- `deliveredOriginalBinaryCommandCount=2`
- `hostHelperInputSent=true`
- `gameInputSentByRemoteClient=false`
- `gameInputSentByHostAuthorityScheduler=false`
- `bridgeSendsNewNetworkInput=false`
- `acceptedOriginalBinaryGameplaySlots=P1,P2`
- `metadataOnlySlots=P3,P4`
- `rejectedGameplayRouteSlots=P3,P4`
- `baseOnlineMultiplayerReady=false`
- `publicMatchmakingProof=false`
- `multiHostLanProof=false`
- `nativeBeaNetcodeProof=false`
- `nPlayerOriginalBinaryRuntimeProof=0`
- `activeP3P4OriginalBinaryGameplayProof=false`
- `privateProofReleaseExcludedByPolicy=true`
- `privateProofRootRelative=true`
- `absoluteSourceArtifactPathRejected=true`
- `sourceArtifactEscapesPrivateProofRootRejected=true`

Boundary:

This proves a same-workstation process-separated private remote-client command source is on the validated provenance path into one copied original-BEA level-850/config-1 host-authority runtime executor proof. It does not prove base player-tryable online multiplayer readiness, a second physical host, multi-host LAN play, public matchmaking, native BEA netcode, a new network input bridge inside BEA, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.
