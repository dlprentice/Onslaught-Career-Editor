# Original Binary Online Session Scalability Contract Readiness Note

Status: complete public-safe design contract plus process-layer concurrency and session-security smoke proof
Date: 2026-06-18
Updated: 2026-06-19
Scope: `original-binary-online-session-scalability-contract`

This slice records the online multiplayer scalability and mode contract requested for the long-term online lane. It does not launch BEA, does not send game input, does not mutate any executable, does not mutate Ghidra, and does not touch the installed Steam folder.

## Accepted Contract

The public-safe contract is:

```text
roadmap\original-binary-online-session-scalability-contract.v1.json
```

The contract records:

- schema `winui-original-binary-online-session-scalability-contract.v1`
- runtime profile `original-binary-copied-local-splitscreen`
- `originalBinaryPlayerSlotsProven=2`
- `maxRetailPlayersProven=2`
- `retailSlotsProven=P1,P2`
- `retailViewpointsProven=2`
- proven runtime slots `P1`, `P2`
- source player-count anchor `references/Onslaught/game.cpp:705 WORLD.IsMultiplayer() sets mPlayers=2`
- source viewpoint anchor `references/Onslaught/engine.h:16 defines VIEWPOINTS 2`
- `moreThanTwoOriginalBinaryRuntimeProofSlices=0`
- `nPlayerOriginalBinaryRuntimeProof=0`
- `beyondTwoPlayersRequiresNewProofClass=true`
- `coOpVersusModeRuntimeProofSlices=0`
- `nativeBeaNetcodeProofSlices=0`
- `modeScalableContractStatus=design-only-unproven`
- `modeClassifierPolicy`
- `winui-original-binary-online-mode-classifier.v1`
- `static-source-session-taxonomy-not-runtime-mode-proof`
- `original-binary-online-mode-classifier-not-runtime-mode-proof`
- `currentRuntimeModeClassification=unclassified-local-multiplayer`
- `runtime-observed-local-splitscreen-not-co-op-or-versus-proof`
- `modeRuntimeProofSlices=0`
- `coOpModeRuntimeProof=false`
- `versusModeRuntimeProof=false`
- `teamVersusRuntimeProof=false`
- `spectatorAdminRuntimeProof=false`
- `teamAssignmentAuthority=schema-only-not-runtime-proof`
- `modeScalableArchitecturePlanned=true`
- planned `sessionType` model with `participants[]`, `maxOriginalBinaryActiveSlots=2`, and unsupported-slot rejection
- slot model `profile-declared-indexed-player-slots`
- `minimumArchitectureAcceptanceSlots=4`
- design example slots `P1`, `P2`, `P3`, `P4`
- `schedulerCardinalityProven=4`
- `maxClientProcessesProven=4`
- `sequentialProcessConcurrencyModel=sequential-distinct-client-processes`
- `sequentialSimultaneousClientProcessesProven=1`
- `processConcurrencyModel=barrier-concurrent-client-processes`
- `simultaneousClientProcessesProven=4`
- `maxSimultaneousSocketConnectionsProven=4`
- `clientReadyBeforeBarrierReleaseCount=4`
- `barrierReleaseAfterAllClientsReady=true`
- `privateInterfaceListenerScope=private-lan-reachable-during-smoke-foreign-peers-rejected-after-accept`
- `concurrentProcessSmokeSecurityScope=minimal-smoke-hmac-envelope-not-full-session-security-proof`
- `securityProofScope=same-workstation-session-security-smoke-not-online-gameplay-proof`
- `sessionScopedMacCoverageProof=true`
- `maxJsonLineBytesEnforced=true`
- `unknownFieldRejectionProof=true`
- `strictMessageSchemaProof=true`
- `rejectedSecurityCaseCount=25`
- `activeP3P4OriginalBinaryGameplayProof=false`
- scheduler/process cardinality was raised by the 2026-06-19 same-workstation sequential four-client N-slot process smoke; process-layer overlap was then raised by the 2026-06-19 same-workstation-client/private-interface concurrent/barrier four-client N-slot process smoke; original-binary runtime slots remain capped at `P1`, `P2`
- schedule policy `stable-slot-order`
- `rejectedExtraSlot` handling is required for unproven original-binary slots
- planned mode families `cooperative`, `versus-free-for-all`, `team-versus`, and `spectator-admin`

The checker requires the architecture to reject hardcoded two-player design while keeping the current original-binary runtime proof capped at two players.

The security/protocol requirements include per-slot identity, canonical-message HMAC coverage excluding only `mac`, replay cache namespacing by session/client/slot/nonce, raw JSON line max message size, schema allowlists, unknown-field rejection, per-slot and global queue limits, tick budget/backpressure/drop policy, and `publicBind=false` until a real public server design exists. The current concurrent process smoke uses a minimal smoke HMAC envelope only and is not full session-security proof by itself. The separate same-workstation N-slot session-security smoke proves the protocol-message layer with `sessionScopedMacCoverageMode=canonical-json-message-excluding-mac`, `sessionScopedMacFieldSensitivityProof=true`, `rawJsonLineByteLimitRejected=true`, and `rejectedSecurityCaseCount=25`, while still proving no BEA launch, CDB attach, game input, multi-host LAN play, public matchmaking, native BEA netcode, or active P3/P4 original-binary gameplay.

2026-06-19 joined-session control update: the contract also records a joined-session control-lifecycle proof with `sessionControlLifecycleProven=true`, `joined-session-control-lifecycle-same-host-not-online-play`, `joined-session-same-host-session-control-not-online-play`, `acceptedControlActionCount=11`, `rejectedControlCaseCount=22`, `metadata-reconnect-only-not-runtime-reconnect`, `newBeaLaunchCount=0`, `cdbAttachCount=0`, `gameInputSentBySessionControl=false`, `baseOnlineMultiplayerReady=false`, and `activeP3P4OriginalBinaryGameplayProof=false`. This is public-safe same-host session-control lifecycle evidence only; it is not BEA launch/runtime proof, direct game input, second-host LAN, public matchmaking, native BEA netcode, P3/P4 gameplay, or co-op/versus mode proof.

2026-06-19 online mode classifier update: the contract also records `modeClassifierPolicy` from `roadmap\original-binary-online-mode-classifier.v1.json`. It classifies the current copied level-850/runtime profile as `currentRuntimeModeClassification=unclassified-local-multiplayer` with status `runtime-observed-local-splitscreen-not-co-op-or-versus-proof`. Planned mode families remain `cooperative`, `versus-free-for-all`, `team-versus`, and `spectator-admin`, but `modeRuntimeProofSlices=0`, `coOpVersusModeRuntimeProofSlices=0`, `coOpModeRuntimeProof=false`, `versusModeRuntimeProof=false`, `teamVersusRuntimeProof=false`, `spectatorAdminRuntimeProof=false`, and `teamAssignmentAuthority=schema-only-not-runtime-proof`.

## Commands

```powershell
py -3 tools\winui_safe_copy_online_session_scalability_contract_check.py --check
py -3 tools\winui_safe_copy_online_session_scalability_contract_check.py --self-test
npm run test:winui-original-binary-online-session-scalability-contract
```

## Boundary

This is not a BEA launch/capture/stop run, not runtime proof for more than two original-binary players, not co-op mode proof, not versus mode proof, not team-versus proof, not multi-host LAN play, not public matchmaking, not native BEA netcode, not deterministic sync, not rollback, not anti-cheat, not physical gamepad behavior, not rebuild parity, and not no-noticeable-difference online parity.

No Ghidra backup was created because no Ghidra mutation occurred. The latest verified Ghidra review backup remains Wave1219 backup id `BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`; exact local backup roots stay in private state/evidence.
