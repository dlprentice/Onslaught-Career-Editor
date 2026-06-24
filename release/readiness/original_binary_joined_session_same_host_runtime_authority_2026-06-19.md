# Original Binary Joined-Session Same-Host Runtime-Authority Readiness Note

Status: complete bounded wrapper proof
Date: 2026-06-19
Scope: `original-binary-joined-session-same-host-runtime-authority`

This slice links the accepted local session-directory P2 join-ticket and the same-physical-machine WSL2 command-source predecessor to the already accepted secure N-slot executor replayability and exact-PID state-authority replayability evidence. It is a public-safe wrapper over prior accepted artifacts; it does not launch BEA, attach CDB, mutate the installed game, mutate the clean backup executable, or mutate Ghidra.

Accepted summary:

| Field | Value |
| --- | --- |
| Schema | `winui-original-binary-joined-session-same-host-runtime-authority.v1` |
| Protocol | `joined-session-same-host-runtime-authority.v1` |
| Scope | `joined-session-same-host-runtime-authority-not-online-play` |
| Chain flag | `joinedSessionSameHostRuntimeAuthorityChainProven=true` |
| Accepted join ticket | `acceptedJoinTicketSlot=P2`; `joinTicketRuntimeRelayHashMatched=true` |
| Same-host source boundary | `samePhysicalMachineWslPredecessor=true`; `sameHostOnly=true`; `secondPhysicalHostProof=false` |
| Host authority | `hostAuthorityModel=single-host-authoritative-copied-session`; `hostAuthorityScope=single-copied-host-exact-pid-state-graph` |
| Runtime profile | `runtimeProfile=original-binary-copied-local-splitscreen` |
| Accepted gameplay slots | `acceptedOriginalBinaryGameplaySlots=P1,P2` |
| Metadata-only slots | `metadataOnlySlots=P3,P4` |
| Rejected gameplay routes | `rejectedGameplayRouteSlots=P3,P4` |
| Secure executor replayability | `secureNSlotRuntimeExecutorReplayabilityProven=true`; proof count `2` |
| State authority replayability | `stateAuthorityGraphProven=true`; `stateAuthorityReplayabilityProven=true`; proof count `2` |
| Host helper input | `hostHelperInputSentByAcceptedRuntimeAuthority=true` |
| Wrapper side effects | `wrapperNewBeaLaunchCount=0`; `wrapperCdbAttachCount=0` |
| Direct input non-claims | `gameInputSentByDirectory=false`; `gameInputSentByWslClient=false`; `gameInputSentByNSlotScheduler=false` |
| Visible movement boundary | `visibleMovementReferenceAccepted=true`; `joinedSessionVisibleMovementCausalityProof=false` |
| Online non-claims | `publicMatchmakingProof=false`; `multiHostLanProof=false`; `nativeBeaNetcodeProof=false` |
| Slot non-claims | `nPlayerOriginalBinaryRuntimeProof=0`; `activeP3P4OriginalBinaryGameplayProof=false` |

Source evidence:

- Local session-directory smoke: `same-workstation-local-directory-smoke-not-public-matchmaking`; `registeredSessionCount=1`; `compatibleListingCount=1`; `acceptedJoinTicketCount=1`; `rejectedDirectoryCaseCount=14`.
- WSL2 command-source predecessor: `wsl2-remote-client-tcp-jsonl-auth-smoke`; `acceptedCommandId=wsl-remote-client-p2-forward-0001`; same physical machine only.
- Secure executor replayability: session-security proof hash `3c0d0e15c23fa3644afcd937dc3c53df6d703301ec8ccffc9e665ea4f182711b`; relay plan hash `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002`; runtime-compatible P1/P2 relay hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`; executor proof hashes `4a2b3814112931a60fb58ebfc424fe4382e19701c0f3a16200f3b4b4806b4df1` and `8ef72707fd57a6c4ad9e65d3f03e1c21dd945e72bfbb3c3c87f5ddfd3c5d1e0d`.
- State-authority replayability: replayability summary hash `a66e66dee6ff06bfab3a1cae234b86958bc8537712206d4db6605c898543ef7a`; observer proof hashes `ac1cd32281e354b5ae37a0aa8c17b1ab883bc9dd863c2ae5e2ffe7bde62c0416` and `e57516d1b306d0a8a37aa1be2103235f066d1d4e06d4b648a9b0c140dfafc017`.

Boundary:

This proves a same-host joined-session runtime-authority chain for the currently proven P1/P2 original-binary route. The accepted local directory P2 join-ticket selects the bounded P1/P2 relay path, and the same-physical-machine WSL command-source predecessor is linked to that accepted P2 route; the WSL smoke is not itself a relay-hash carrier. It does not prove a second physical host, multi-host LAN play, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, deterministic sync, rollback, anti-cheat, physical gamepad behavior, joined-session visible movement causality, rebuild parity, or no-noticeable-difference online parity.

Validation:

```powershell
npm run test:winui-original-binary-online-session-directory-smoke
npm run test:winui-original-binary-wsl-remote-client-smoke
py -3 tools\build_winui_original_binary_joined_session_same_host_runtime_authority_bundle.py
py -3 tools\winui_safe_copy_online_joined_session_same_host_runtime_authority_check_test.py
py -3 tools\winui_safe_copy_online_joined_session_same_host_runtime_authority_check.py --self-test
py -3 tools\winui_safe_copy_online_joined_session_same_host_runtime_authority_check.py --check
npm run test:winui-original-binary-joined-session-same-host-runtime-authority
```

Release-boundary tokens: `privateProofReleaseExcludedByPolicy=true`; `rawPrivateProofPathPublished=false`; `rawPrivateArtifactContentPublished=false`; `absolutePrivatePathPublished=false`; `releaseIncludedPrivateArtifact=false`.
