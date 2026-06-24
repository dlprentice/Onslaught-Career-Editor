# Original Binary Host Authority State-Authority Replayability Readiness Note

Status: complete bounded state-authority replayability proof
Date: 2026-06-19
Scope: `winui-original-binary-host-authority-state-authority-replayability`

This slice validates replayability of the same-workstation, single-copied-host exact-PID P1/P2 state-authority graph. It compares two distinct host-authority state-authority observer proofs built from the same accepted four-client N-slot concurrent process proof and runtime-compatible P1/P2 relay plan.

## Evidence

| Field | Value |
| --- | --- |
| Replayability schema | `winui-original-binary-host-authority-state-authority-replayability.v1` |
| Replayability protocol | `host-authority-state-authority-replayability.v1` |
| Replayability summary hash | `a66e66dee6ff06bfab3a1cae234b86958bc8537712206d4db6605c898543ef7a` |
| Observer proof hashes | `ac1cd32281e354b5ae37a0aa8c17b1ab883bc9dd863c2ae5e2ffe7bde62c0416`, `e57516d1b306d0a8a37aa1be2103235f066d1d4e06d4b648a9b0c140dfafc017` |
| Source bridge proof hashes | `ee9aee859c40db44978664cfa11d1a668ec4fb9bade08a18ddfadcaa7847221f`, `6e6a8d68d1c4dea875b93e9dc74b63a6aeabc05b350a4e683bc17f0881176ba8` |
| Live runtime artifact hashes | `7b6118b783e82d13f20ed9e09fc593b920793e90f09a48ffc698750e56c940ae`, `f87e0e6b622e504733082a9b8aafb4ba8d4e254e7a93471b0eacb87d263f32a8` |
| N-slot concurrent proof hash | `7458bbafcca8fbb60f0b7750fac068b7a6dcdfe59b13980f54da081832f95896` |
| N-slot relay plan hash | `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002` |
| Runtime-compatible P1/P2 relay hash | `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376` |
| Proof count | `2` |
| Slot capacity | `4` |
| Accepted original-binary gameplay slots | `P1`, `P2` |
| Metadata-only slots | `P3`, `P4` |
| Rejected gameplay route slots | `P3`, `P4` |
| Role invariant | `P1 -> Q -> inputDevice0/top split half; P2 -> E -> inputDevice1/bottom split half` |
| P1/Q rows per proof | `button31ReceiveRows=12`, `forwardStateStoreRows=12` |
| P2/E rows per proof | `button31ReceiveRows=11`, `forwardStateStoreRows=11` |
| Visual capture count per proof | `7` |

Required replayability booleans:

- `hostAuthorityScope=single-copied-host-exact-pid-state-graph`
- `stateAuthorityGraphProven=true`
- `stateAuthorityReplayabilityProven=true`
- `distinctLiveRuntimeArtifactHashes=true`
- `distinctSourceBridgeProofHashes=true`
- `distinctProcessIds=true`
- `distinctCdbLogs=true`
- `distinctRuntimePointerTuples=true`
- `distinctPlayers=true`
- `distinctBattleEngines=true`
- `distinctWalkers=true`
- `distinctControllers=true`
- `waitWindowsClean=true`
- `hostHelperInputSent=true`
- `gameInputSentByNSlotScheduler=false`
- `nPlayerOriginalBinaryRuntimeProof=0`
- `activeP3P4OriginalBinaryGameplayProof=false`
- `beyondTwoPlayersRequiresNewProofClass=true`
- `absenceOfCurrentProofIsNotProofOfPermanentAbsence=true`
- `permanentImpossibilityClaim=false`
- `privateProofReleaseExcludedByPolicy=true`
- `rawPrivateProofPathPublished=false`
- `rawPrivateArtifactContentPublished=false`
- `absolutePrivatePathPublished=false`
- `releaseIncludedPrivateArtifact=false`

## Non-Claims

This is not active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, multi-host LAN play, public matchmaking, native BEA netcode, full session security, deterministic sync, rollback, anti-cheat, physical gamepad behavior, visible movement causality, rebuild parity, or no-noticeable-difference online parity.

No Ghidra mutation or executable-byte mutation occurred in this slice.
