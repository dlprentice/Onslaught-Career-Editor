# Original Binary Joined-Session Runtime Causality Proof

Status: accepted copied-runtime proof
Date: 2026-06-19
Scope: `joined-session-fresh-runtime-causality-same-host-not-online-play`

This proof adds one fresh same-host copied-runtime rung after the joined-session same-host runtime-authority wrapper. It validates the accepted joined-session P2 ticket/relay chain, builds a fresh N-slot session-security proof, then runs the existing secure N-slot runtime executor against a copied level-850/config-1 `BEA.exe` host.

Accepted evidence:

| Field | Value |
| --- | --- |
| Schema | `winui-original-binary-joined-session-runtime-causality.v1` |
| Joined proof hash | `d7cf48a6f60d6537416f46af1bf6b8667dc08a4f7c7bd25313a708cd187c312f` |
| Secure executor proof hash | `98e5e68f4d4a8afca436ff4b5e4aeef8f477db6cb8b4fc5441b69662b300bf98` |
| Fresh session-security proof hash | `a5592a4febe7b6f35aa862af8c12b6100c6bff8984d01688637eb2a05ae35687` |
| Fresh live runtime artifact hash | `ee5acab52c81c452dcd16cd7d678e0612cb3b12f2ce720c98337d2c699c07295` |
| Fresh CDB log hash | `ecc1c3bd52575446e39e154ab22f29f199a8a118015d09a605bb857f4c1e4e5f` |
| Runtime state summary hash | `04ba82a9948bd62a3941d873a9e35212c23eba672219835832ae21bd1144efb1` |
| Runtime-compatible relay hash | `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376` |

Machine-checked tokens:

- `joinedSessionRuntimeCausalityProven=true`
- `joinTicketRuntimeRelayPathMatchCount=1`
- `acceptedJoinTicketSlot=P2`
- `joinTicketRuntimeRelayHashMatched=true`
- `samePhysicalMachineWslPredecessor=true`
- `sameHostOnly=true`
- `newBeaLaunchCount=1`
- `cdbAttachCount=1`
- `visualCaptureCount=7`
- `deliveredOriginalBinaryCommandCount=2`
- `hostHelperInputSent=true`
- `gameInputSentByJoinedSessionClient=false`
- `gameInputSentByDirectory=false`
- `gameInputSentByWslClient=false`
- `gameInputSentByNSlotScheduler=false`
- `exactPidCdbStateRowsProven=true`
- `visibleMovementDeltaClaim=false`
- `acceptedOriginalBinaryGameplaySlots=P1,P2`
- `metadataOnlySlots=P3,P4`
- `rejectedGameplayRouteSlots=P3,P4`
- `baseOnlineMultiplayerReady=false`
- `publicMatchmakingProof=false`
- `multiHostLanProof=false`
- `nativeBeaNetcodeProof=false`
- `nPlayerOriginalBinaryRuntimeProof=0`
- `activeP3P4OriginalBinaryGameplayProof=false`
- `joinedSessionVisibleMovementCausalityProof=false`
- `privateProofReleaseExcludedByPolicy=true`

Boundary:

This proves same-host joined-session runtime causality for the currently accepted P1/P2 host-authority path. It does not prove base player-tryable online multiplayer readiness, a second physical host, multi-host LAN play, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, deterministic sync, rollback, anti-cheat, physical gamepad behavior, joined-session visible movement causality, rebuild parity, or no-noticeable-difference online parity.
